// Access-protected remote reliability lab; separate DOs + at-least-once Queue.
// Never invokes a real payment processor or accepts visitor API tokens.
import {requireAccess} from "./auth.mjs";
import {CheckoutState} from "./checkout.mjs";
import {ProviderState} from "./provider.mjs";
import {remotePage} from "./ui.mjs";
import {readScope,validRunId} from "./readback.mjs";
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
        const runId=input.runId===undefined?null:validRunId(input.runId);
        const created=await invoke(checkout,{action:"create",key,amount,fault,runId,account:user.userId});
        const dispatch=await invoke(checkout,{action:"enqueue",keys:[key]});
        return json({created,dispatch,message:"202 means pending intent, not settled payment"},202);
      }
      if(url.pathname==="/api/replay"){
        const dispatch=await invoke(checkout,{action:"replay"});
        return json({dispatch,message:"Replayed only pending work with the original payment key"});
      }
      const selection=readScope(input);
      if(input.includeBookmarks!==undefined&&typeof input.includeBookmarks!=="boolean")throw Error("includeBookmarks must be boolean");
      const [local,remote]=await Promise.all([
        invoke(checkout,{action:"state",scope:selection}),invoke(provider,{action:"state",scope:selection})]);
      let bookmarks;
      if(input.includeBookmarks===true){
        const [checkoutBookmark,providerBookmark]=await Promise.all([
          invoke(checkout,{action:"bookmark"}),invoke(provider,{action:"bookmark"})]);
        bookmarks={checkout:checkoutBookmark,provider:providerBookmark};
      }
      const {rowsRead:checkoutReads,...state}=local,charges=remote.charges;
      return json({schema:"checkout-remote-evidence@3",selection,
        quotaPolicy:{enforcement:"Cloudflare platform quotas",requiredPlan:"Workers Free",planVerification:"OPERATOR_REQUIRED",remaining:"UNKNOWN",
          usage:"Platform usage must be read from Cloudflare; the app does not meter account quotas"},
        scope:"two independent Cloudflare SQLite Durable Objects with Queue",
        at:new Date().toISOString(),...state,charges,
        ...(bookmarks?{bookmarks}:{}),
        readbackUsage:{checkoutRowsRead:checkoutReads,providerRowsRead:remote.rowsRead,
          totalRowsRead:checkoutReads==null||remote.rowsRead==null?null:checkoutReads+remote.rowsRead,
          scope:"Only these fully consumed SQL readback cursors; excludes initialization, mutations, alarms and other account usage"},
        integrity:{...invariant({orders:state.orders,charges}),scope:selection},
        note:"Separate-service behavioral and disaster recovery proof requires external observation"});
    }catch(err){
      const reason=String(err?.message||err);
      const accessFailure=/Cloudflare Access/.test(reason);
      return json({error:reason},accessFailure?403:reason.startsWith("409:")?409:reason.startsWith("429:")?429:reason.startsWith("503:")?503:400);
    }
  },
  async queue(batch,env){
    const batchStartedAt=Date.now();
    for(const message of batch.messages){
      const {account,key,amount,fault,runId}=message.body||{};
      const startedAt=Date.now(),queuedAt=message.timestamp?.getTime?.();
      const timing={phase:"queue-consumer-result",key:null,runId:null,
        batchSize:batch.messages.length,batchStartedAt,startedAt,
        queuedAt:Number.isFinite(queuedAt)?queuedAt:null,
        queueLagMs:Number.isFinite(queuedAt)?batchStartedAt-queuedAt:null,
        batchWaitMs:startedAt-batchStartedAt,attempt:message.attempts??null};
      try{
        if(typeof account!=="string"||account.length>300)throw Error("Invalid queued Access identity");
        validPayment(key,amount);
        if(runId!=null)validRunId(runId);
        timing.key=key;timing.runId=runId??null;
        const {checkout,provider}=stores(env,account);
        // Only trusted mock-provider readback establishes its committed effect.
        let stepAt=Date.now();
        let charge=await invoke(provider,{action:"lookup",key});
        timing.lookupMs=Date.now()-stepAt;timing.providerFound=!!charge;
        if(!charge){
          stepAt=Date.now();charge=await invoke(provider,{action:"charge",key,amount,runId});
          timing.chargeMs=Date.now()-stepAt;
        }
        if(charge.amount!==amount||charge.currency!=="USD")throw Error("Provider evidence mismatch");
        if(fault==="lost_reply"||fault==="worker_crash"){
          stepAt=Date.now();const injected=await invoke(checkout,{action:"claimFault",key});
          timing.claimFaultMs=Date.now()-stepAt;
          if(injected){
            // Deliberately preserve PENDING after Provider COMMIT. Redelivery
            // must read back the same payment identity, not charge twice.
            message.retry({delaySeconds:3});timing.result="retry-injected";continue;
          }
        }
        stepAt=Date.now();await invoke(checkout,{action:"paid",key,amount});
        timing.paidMs=Date.now()-stepAt;timing.paidConfirmedAt=Date.now();
        message.ack();timing.result="ack";
      }catch(error){console.warn(JSON.stringify({phase:"queue-consumer",error:error.message}));message.retry({delaySeconds:5});timing.result="retry-error";}
      finally{
        timing.completedAt=Date.now();timing.processingMs=timing.completedAt-startedAt;
        // Live tail only: no SQL writes, persistent Logs, account IDs or headers.
        console.log(JSON.stringify(timing));
      }
    }
  }
};
