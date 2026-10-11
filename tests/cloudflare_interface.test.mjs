// Contract-level fake endpoints; NOT an actual Cloudflare Durable Object / Queue drive.
import test from "node:test";
import assert from "node:assert/strict";
import worker from "../examples/cloudflare-checkout-sandbox/src/index.mjs";
import {DatabaseSync} from "node:sqlite";
import {CheckoutState} from "../examples/cloudflare-checkout-sandbox/src/checkout.mjs";

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
         case "usage":value={orders:0,dispatches:0,limits:{orders:20,dispatches:50}};break;
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
 return {CHECKOUT,PROVIDER,REQUEST_LIMITER:{async limit(){return {success:true};}},PAYMENTS_QUEUE:{async send(x){pending.push(x);}},pending};
}
const ctx={access:{async getIdentity(){return {email:"owner@example.test"};}}};
// Real source SQL against SQLite; only platform transport and alarm are adapters.
// This verifies quota semantics, not Cloudflare-native execution.
function sqliteEnvironment(){
  const objects=new Map(),databases=[],sent=[];
  const env={PAYMENTS_QUEUE:{async send(value){sent.push(value);}}};
  env.CHECKOUT={idFromName:name=>name,get(name){
    if(!objects.has(name)){
      const db=new DatabaseSync(":memory:");databases.push(db);
      const storage={sql:{exec(sql,...params){const rows=db.prepare(sql).all(...params);return {toArray:()=>rows};}},
        transactionSync(fn){db.exec("BEGIN");try{const value=fn();db.exec("COMMIT");return value;}catch(error){db.exec("ROLLBACK");throw error;}},
        async setAlarm(){}};
      const object=new CheckoutState({storage},env),fetch=object.fetch.bind(object);
      object.fetch=(request,options)=>fetch(request instanceof Request?request:new Request(request,options));
      objects.set(name,object);
    }
    return objects.get(name);
  }};
  return {env,sent,close(){for(const db of databases)db.close();}};
}
test("account reservations share the 20-order budget and preserve idempotency",async()=>{
  const fixture=sqliteEnvironment();
  try{
    const result=await Promise.allSettled(Array.from({length:21},(_,i)=>
      fixture.env.CHECKOUT.get("user-"+i).admit({key:"order",amount:1250,fault:"none",account:"user-"+i})));
    assert.equal(result.filter(r=>r.status==="fulfilled").length,20);
    assert.match(result.find(r=>r.status==="rejected").reason.message,/429/);
    const object=fixture.env.CHECKOUT.get("user-0");
    assert.equal((await object.admit({key:"order",amount:1250,fault:"none",account:"user-0"})).replay,true);
    await assert.rejects(object.admit({key:"order",amount:1300,fault:"none",account:"user-0"}),/409/);
    assert.equal(fixture.env.CHECKOUT.get("sandbox-account-budget").usage().orders,20);
  }finally{fixture.close();}
});
test("unavailable account budget preserves no new order or outbox effect",async()=>{
  const fixture=sqliteEnvironment();
  try{
    const object=fixture.env.CHECKOUT.get("user"),get=fixture.env.CHECKOUT.get;
    fixture.env.CHECKOUT.get=name=>name==="sandbox-account-budget"?{async fetch(){throw Error("transport unavailable");}}:get(name);
    await assert.rejects(object.admit({key:"unknown",amount:1250,fault:"none",account:"user"}),/503:.*transport unavailable/);
    assert.deepEqual(object.snapshot(),{orders:[],outbox:[]});
    assert.equal(fixture.sent.length,0);
  }finally{fixture.close();}
});
test("dispatch budget, concurrent relay and manual replay stay bounded",async()=>{
  const fixture=sqliteEnvironment();
  try{
    const object=fixture.env.CHECKOUT.get("user");
    await object.admit({key:"pending",amount:1250,fault:"none",account:"user"});
    await Promise.all(Array.from({length:8},()=>object.enqueue()));
    assert.equal(fixture.sent.length,3);
    for(let i=0;i<3;i++)await object.fetch(post("replay",{action:"replay"}));
    assert.equal(object.snapshot().outbox[0].replays,2);
    assert.equal(fixture.sent.length,5);
    const budget=fixture.env.CHECKOUT.get("sandbox-account-budget");
    while(budget.usage().dispatches<50)budget.reserve({kind:"dispatch"});
    const before=fixture.sent.length;
    await object.enqueue();
    assert.equal(fixture.sent.length,before);
    assert.equal(budget.usage().dispatches,50);
    assert.equal(object.snapshot().orders[0].status,"PENDING");
  }finally{fixture.close();}
});
function post(path,body={}){return new Request("https://sandbox.example/"+path,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});}
test("Access-gated: no authenticated ctx rejects every route",async()=>{
  const env=fakeEnvironment();
  assert.equal((await worker.fetch(post("api/state"),env,{})).status,403);
  assert.equal((await worker.fetch(new Request("https://sandbox.example/"),env,{})).status,403);
});
test("missing or refusing rate guard blocks effects before DO access",async()=>{
  const env=fakeEnvironment();delete env.REQUEST_LIMITER;
  assert.equal((await worker.fetch(post("api/create",{key:"guarded",amount:1250}),env,ctx)).status,503);
  env.REQUEST_LIMITER={async limit(){return {success:false};}};
  assert.equal((await worker.fetch(post("api/create",{key:"guarded",amount:1250}),env,ctx)).status,429);
  assert.equal(env.CHECKOUT.objects.size,0);assert.equal(env.pending.length,0);
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
