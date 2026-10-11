// Access-protected remote reliability lab; separate DOs + at-least-once Queue.
// Never invokes a real payment processor or accepts visitor API tokens.
import {requireAccess} from "./auth.mjs";
import {CheckoutState} from "./checkout.mjs";
import {ProviderState} from "./provider.mjs";
import {remotePage} from "./ui.mjs";
import {validPayment,invariant} from "../../../site/reliability/logic.mjs";
export {CheckoutState,ProviderState};
const faultModes=new Set(["none","lost_reply","worker_crash"]);
function json(value,status=200){return Response.json(value,{status,headers:{"Cache-Control":"no-store","X-Content-Type-Options":"nosniff"}});}
async function invoke(stub,payload){
  const r=await stub.fetch("https://internal/"+payload.action,{method:"POST",body:JSON.stringify(payload)});
  const response=await r.json();
  if(!response.ok)throw new Error(response.error||"Durable Object refused");
  return response.value;
}
function stores(env,account){
  const key="access-user:"+account;
  return {checkout:env.CHECKOUT.get(env.CHECKOUT.idFromName(key)),
          provider:env.PROVIDER.get(env.PROVIDER.idFromName(key))};
}
export default {
  async fetch(request,env,ctx){
    try{
      const url=new URL(request.url),origin=request.headers.get("Origin");
      if(origin&&origin!==url.origin)return json({error:"Cross-origin mutation refused"},403);
      const user=await requireAccess(ctx);
      if(!env.REQUEST_LIMITER?.limit)throw Error("503: Request usage guard is unavailable");
      const limited=await env.REQUEST_LIMITER.limit({key:user.userId+":"+(url.pathname==="/api/state"?"read":"write")});
      if(!limited.success)return json({error:"Rate limit reached; preserve the payment key and wait"},429);
      if(request.method==="GET"&&url.pathname==="/")
        return new Response(remotePage,{headers:{"Content-Type":"text/html; charset=utf-8","Cache-Control":"no-store",
          "Content-Security-Policy":"default-src 'none'; base-uri 'none'; frame-ancestors 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self'"}});
      if(request.method!=="POST"||!["/api/create","/api/state","/api/replay"].includes(url.pathname))
        return json({error:"Unknown or unapproved route"},404);
      if(Number(request.headers.get("Content-Length")||0)>2048)return json({error:"Payload too large"},413);
      const raw=await request.text();
      if(raw.length>2048)return json({error:"Payload too large"},413);
      const input=JSON.parse(raw);
      const {checkout,provider}=stores(env,user.userId);
      if(url.pathname==="/api/create"){
        const {key,amount}=validPayment(input.key,input.amount);
        const fault=faultModes.has(input.fault)?input.fault:"none";
        const created=await invoke(checkout,{action:"create",key,amount,fault,account:user.userId});
        const dispatch=await invoke(checkout,{action:"enqueue"});
        return json({created,dispatch,message:"202 means pending intent, not settled payment"},202);
      }
      if(url.pathname==="/api/replay"){
        const dispatch=await invoke(checkout,{action:"replay"});
        return json({dispatch,message:"Replayed only pending work with the original payment key"});
      }
      const [local,charges,checkoutBookmark,providerBookmark]=await Promise.all([
        invoke(checkout,{action:"state"}),invoke(provider,{action:"state"}),
        invoke(checkout,{action:"bookmark"}),invoke(provider,{action:"bookmark"})]);
      const budget=env.CHECKOUT.get(env.CHECKOUT.idFromName("sandbox-account-budget"));
      const usage=await invoke(budget,{action:"usage"});
      return json({schema:"checkout-remote-evidence@1",usage,
        scope:"two independent Cloudflare SQLite Durable Objects with Queue",
        at:new Date().toISOString(),...local,charges,
        bookmarks:{checkout:checkoutBookmark,provider:providerBookmark},
        integrity:invariant({orders:local.orders,charges}),
        note:"Separate-service behavioral and disaster recovery proof requires external observation"});
    }catch(err){
      const reason=String(err?.message||err);
      const accessFailure=/Cloudflare Access/.test(reason);
      return json({error:reason},accessFailure?403:reason.startsWith("409:")?409:reason.startsWith("429:")?429:reason.startsWith("503:")?503:400);
    }
  },
  async queue(batch,env){
    for(const message of batch.messages){
      const {account,key,amount,fault}=message.body||{};
      try{
        if(typeof account!=="string"||account.length>300)throw Error("Invalid queued Access identity");
        validPayment(key,amount);
        const {checkout,provider}=stores(env,account);
        // Only trusted mock-provider readback establishes its committed effect.
        let charge=await invoke(provider,{action:"lookup",key});
        if(!charge)charge=await invoke(provider,{action:"charge",key,amount});
        if(charge.amount!==amount||charge.currency!=="USD")throw Error("Provider evidence mismatch");
        if(fault==="lost_reply"||fault==="worker_crash"){
          if(await invoke(checkout,{action:"claimFault",key})){
            // Deliberately preserve PENDING after Provider COMMIT. Redelivery
            // must read back the same payment identity, not charge twice.
            message.retry({delaySeconds:3});continue;
          }
        }
        await invoke(checkout,{action:"paid",key,amount});
        message.ack();
      }catch(error){console.warn(JSON.stringify({phase:"queue-consumer",error:error.message}));message.retry({delaySeconds:5});}
    }
  }
};
