// Contract-level fake endpoints; NOT an actual Cloudflare Durable Object / Queue drive.
import test from "node:test";
import assert from "node:assert/strict";
import worker from "../examples/cloudflare-checkout-sandbox/src/index.mjs";
import {DatabaseSync} from "node:sqlite";
import {CheckoutState} from "../examples/cloudflare-checkout-sandbox/src/checkout.mjs";
import drill,{DrillCheckout,DrillProvider} from "../examples/cloudflare-checkout-sandbox/dr/worker.mjs";
import proxy from "../examples/cloudflare-checkout-sandbox/dr/proxy.mjs";

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
// Real source SQL against SQLite; only platform transport and alarm are adapters.
// This verifies quota semantics, not Cloudflare-native execution.
function sqliteEnvironment(Class=CheckoutState){
  const objects=new Map(),databases=[],sent=[];
  const env={PAYMENTS_QUEUE:{async send(value){sent.push(value);}}};
  env.CHECKOUT={idFromName:name=>name,get(name){
    if(!objects.has(name)){
      const db=new DatabaseSync(":memory:");databases.push(db);
      const storage={sql:{exec(sql,...params){const rows=db.prepare(sql).all(...params);return {toArray:()=>rows};}},
        transactionSync(fn){db.exec("BEGIN");try{const value=fn();db.exec("COMMIT");return value;}catch(error){db.exec("ROLLBACK");throw error;}},
        async setAlarm(){},async getCurrentBookmark(){throw Error("PITR is unavailable in this local SQL adapter");}};
      const object=new Class({storage},env),fetch=object.fetch.bind(object);
      object.fetch=(request,options)=>fetch(request instanceof Request?request:new Request(request,options));
      objects.set(name,object);
    }
    return objects.get(name);
  }};
  return {env,sent,close(){for(const db of databases)db.close();}};
}
test("orders exceed former application caps and preserve idempotency",async()=>{
  const fixture=sqliteEnvironment();
  try{
    const object=fixture.env.CHECKOUT.get("user");
    for(let i=0;i<31;i++)object.create({key:"order-"+i,amount:1250,fault:"none",account:"user"});
    assert.equal(object.snapshot().orders.length,31);
    assert.equal(object.create({key:"order-0",amount:1250,fault:"none",account:"user"}).replay,true);
    assert.throws(()=>object.create({key:"order-0",amount:1300,fault:"none",account:"user"}),/409/);
    assert.equal(object.snapshot().outbox.length,31);
  }finally{fixture.close();}
});
test("Queue quota refusal preserves pending work and stops automatic publish retries",async()=>{
  const fixture=sqliteEnvironment();
  try{
    const object=fixture.env.CHECKOUT.get("user");
    object.create({key:"unknown",amount:1250,fault:"none",account:"user"});
    let attempts=0;
    fixture.env.PAYMENTS_QUEUE.send=async()=>{attempts++;throw Error("Platform quota exceeded");};
    for(let i=0;i<5;i++)await object.alarm();
    assert.equal(attempts,3);
    assert.equal(object.snapshot().orders[0].status,"PENDING");
    assert.equal(object.snapshot().outbox[0].delivered,0);
    assert.equal(fixture.sent.length,0);
    fixture.env.PAYMENTS_QUEUE.send=async message=>fixture.sent.push(message);
    await object.fetch(post("replay",{action:"replay"}));
    assert.equal(fixture.sent[0].key,"unknown");
    assert.equal(object.snapshot().orders[0].status,"PENDING");
  }finally{fixture.close();}
});
test("concurrent relay stays finite; manual recovery exceeds former replay and dispatch caps",async()=>{
  const fixture=sqliteEnvironment();
  try{
    const object=fixture.env.CHECKOUT.get("user");
    object.create({key:"pending",amount:1250,fault:"none",account:"user"});
    await Promise.all(Array.from({length:8},()=>object.enqueue()));
    assert.equal(fixture.sent.length,3);
    for(let i=0;i<4;i++)await object.fetch(post("replay",{action:"replay"}));
    assert.equal(object.snapshot().outbox[0].replays,4);
    assert.equal(fixture.sent.length,7);
    object.paid({key:"pending",amount:1250});
    const before=fixture.sent.length;
    await object.fetch(post("replay",{action:"replay"}));
    assert.equal(fixture.sent.length,before);
    for(let i=0;i<18;i++)object.create({key:"next-"+i,amount:1250,fault:"none",account:"user"});
    for(let i=0;i<6;i++)await object.enqueue();
    assert.equal(fixture.sent.length,61);
    assert.ok(fixture.sent.every(message=>message.amount===1250));
  }finally{fixture.close();}
});
function post(path,body={}){return new Request("https://sandbox.example/"+path,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});}
test("Access-gated: no authenticated ctx rejects every route",async()=>{
  const env=fakeEnvironment();
  assert.equal((await worker.fetch(post("api/state"),env,{})).status,403);
  assert.equal((await worker.fetch(new Request("https://sandbox.example/"),env,{})).status,403);
});
test("API reports platform quota uncertainty without inventing remaining order capacity",async()=>{
  const env=fakeEnvironment();
  const read=await (await worker.fetch(post("api/state"),env,ctx)).json();
  assert.equal(read.schema,"checkout-remote-evidence@2");
  assert.equal(read.quotaPolicy.remaining,"UNKNOWN");
  assert.equal(read.quotaPolicy.planVerification,"OPERATOR_REQUIRED");
  assert.equal("usage" in read,false);
  assert.equal(env.CHECKOUT.objects.size,1);
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

test("isolated DR commands preserve provider evidence and reject reuse",async()=>{
  const checkout=sqliteEnvironment(DrillCheckout),provider=sqliteEnvironment(DrillProvider);
  const env={CHECKOUT:checkout.env.CHECKOUT,PROVIDER:provider.env.CHECKOUT,DR_RUN_ID:"dr-control"};
  const invoke=async(action)=>{const r=await drill.fetch(post("dr",{action}),env);return {status:r.status,...await r.json()};};
  try{
    assert.equal((await invoke("create")).status,200);
    assert.equal((await invoke("create")).status,503);
    assert.equal((await invoke("reconcile")).status,503);
    await invoke("provider-commit");await invoke("reconcile");
    const paid=(await invoke("state")).value;
    assert.equal(paid.orders[0].status,"PAID");assert.equal(paid.charges.length,1);
    await invoke("corrupt");
    assert.equal((await invoke("reconcile")).status,503);
    const damaged=(await invoke("state")).value;
    assert.equal(damaged.orders[0].amount,999);
    assert.equal(damaged.charges[0].charge_id,paid.charges[0].charge_id);
    assert.equal((await drill.fetch(post("dr",{action:"prepare-restore",bookmark:"invalid"}),env)).status,503);
  }finally{checkout.close();provider.close();}
});
test("DR bridge rejects non-loopback and cross-origin requests before remote effects",async()=>{
  let calls=0;const env={DR:{async fetch(){calls++;return new Response("local operator accepted");}}};
  assert.equal((await proxy.fetch(new Request("http://remote.example/",{method:"POST"}),env)).status,403);
  assert.equal((await proxy.fetch(new Request("http://127.0.0.1:8877/",{method:"POST",headers:{Origin:"https://evil.invalid"}}),env)).status,403);
  assert.equal(calls,0);
  assert.equal((await proxy.fetch(new Request("http://127.0.0.1:8877/",{method:"POST"}),env)).status,200);
  assert.equal(calls,1);
});
