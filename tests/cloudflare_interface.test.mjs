// Contract-level fake endpoints; NOT an actual Cloudflare Durable Object / Queue drive.
import test from "node:test";
import assert from "node:assert/strict";
import worker from "../examples/cloudflare-checkout-sandbox/src/index.mjs";

function fakeEnvironment(){
 const pending=[];
 class Checkout{
   constructor(){this.orders=new Map();this.outbox=new Map();this.faults=new Set();}
   async fetch(_url,options){
     const x=JSON.parse(options.body);let value;
     try{
       switch(x.action){
         case "create":{
           const previous=this.orders.get(x.key);
           if(previous&&previous.amount!==x.amount)throw Error("409: identical key, different amount");
           if(!previous){
             if(this.orders.size>=30)throw Error("Sandbox quota");
             this.orders.set(x.key,{key:x.key,amount:x.amount,status:"PENDING",fault:x.fault,account:x.account});
             this.outbox.set(x.key,{key:x.key,delivered:0,sends:0});
           }
           value={...this.orders.get(x.key),replay:!!previous};break;
         }
         case "state":value={orders:[...this.orders.values()],outbox:[...this.outbox.values()]};break;
         case "bookmark":value="FAKE_BOOKMARK";break;
         case "enqueue":{
           let count=0;
           for(const o of this.orders.values()){
             const e=this.outbox.get(o.key);
             if(!e.delivered&&e.sends<3){e.sends++;pending.push({account:o.account,key:o.key,amount:o.amount,fault:o.fault});count++;}
           }
           value={dispatched:count,pending:[...this.outbox.values()].filter(e=>!e.delivered).length};break;
         }
         case "replay":{
           for(const e of this.outbox.values())if(!e.delivered)e.sends=0;
           return this.fetch(_url,{body:JSON.stringify({action:"enqueue"})});
         }
         case "claimFault":value=!this.faults.has(x.key);this.faults.add(x.key);break;
         case "paid":{
           const o=this.orders.get(x.key);
           if(!o||o.amount!==x.amount)throw Error("Payment identity mismatch");
           o.status="PAID";this.outbox.get(x.key).delivered=1;
           value={key:x.key,status:"PAID"};break;
         }
         default:throw Error("Unknown request");
       }
       return Response.json({ok:true,value});
     }catch(err){return Response.json({ok:false,error:err.message},{status:400});}
   }
 }
 class Provider{
   constructor(){this.charges=new Map();}
   async fetch(_url,options){
     const x=JSON.parse(options.body);let value;
     if(x.action==="lookup")value=this.charges.get(x.key)||null;
     else if(x.action==="charge"){
       value=this.charges.get(x.key);
       if(!value){value={key:x.key,amount:x.amount,currency:"USD",charge_id:"mock"};this.charges.set(x.key,value);}
     }else if(x.action==="state")value=[...this.charges.values()];
     else if(x.action==="bookmark")value="FAKE_BOOKMARK";
     else throw Error("Unknown action");
     return Response.json({ok:true,value});
   }
 }
 class Namespace{
   constructor(Class){this.Class=Class;this.objects=new Map();}
   idFromName(name){return name;}
   get(name){if(!this.objects.has(name))this.objects.set(name,new this.Class());return this.objects.get(name);}
 }
 const CHECKOUT=new Namespace(Checkout),PROVIDER=new Namespace(Provider);
 return {CHECKOUT,PROVIDER,PAYMENTS_QUEUE:{async send(x){pending.push(x);}},pending};
}
const ctx={access:{async getIdentity(){return {email:"owner@example.test"};}}};
function post(path,body={}){return new Request("https://sandbox.example/"+path,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});}
test("Access-gated: no authenticated ctx rejects every route",async()=>{
  const env=fakeEnvironment();
  assert.equal((await worker.fetch(post("api/state"),env,{})).status,403);
  assert.equal((await worker.fetch(new Request("https://sandbox.example/"),env,{})).status,403);
});
test("one lost reply retries under same key and reconciles once",async()=>{
  const env=fakeEnvironment(),input={key:"cart-42",amount:1250,fault:"lost_reply"};
  assert.equal((await worker.fetch(post("api/create",input),env,ctx)).status,202);
  assert.equal(env.pending.length,1);
  let retries=0,acks=0;
  const message={body:env.pending[0],retry(){retries++},ack(){acks++}};
  await worker.queue({messages:[message]},env);
  assert.equal(retries,1);assert.equal(acks,0);
  let read=await (await worker.fetch(post("api/state"),env,ctx)).json();
  assert.equal(read.orders[0].status,"PENDING");assert.equal(read.charges.length,1);
  await worker.queue({messages:[message]},env);
  read=await (await worker.fetch(post("api/state"),env,ctx)).json();
  assert.equal(read.orders[0].status,"PAID");assert.equal(read.charges.length,1);assert.equal(acks,1);
  assert.equal(read.integrity.pass,true);
  assert.equal((await worker.fetch(post("api/create",{...input,amount:1300}),env,ctx)).status,409);
});
test("replay preserves same identity and anonymous cross-site writes refuse",async()=>{
  const env=fakeEnvironment();
  await worker.fetch(post("api/create",{key:"same",amount:100,fault:"none"}),env,ctx);
  await worker.fetch(post("api/create",{key:"same",amount:100,fault:"none"}),env,ctx);
  const data=await (await worker.fetch(post("api/state"),env,ctx)).json();
  assert.equal(data.orders.length,1);
  const req=new Request("https://sandbox.example/api/state",{method:"POST",headers:{Origin:"https://evil.invalid"},body:"{}"});
  assert.equal((await worker.fetch(req,env,ctx)).status,403);
});
