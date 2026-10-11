// Contract-level fake endpoints; NOT an actual Cloudflare Durable Object / Queue drive.
import test from "node:test";
import assert from "node:assert/strict";
import worker from "../examples/cloudflare-checkout-sandbox/src/index.mjs";
import {DatabaseSync} from "node:sqlite";
import {readScope} from "../examples/cloudflare-checkout-sandbox/src/readback.mjs";
import {CheckoutState} from "../examples/cloudflare-checkout-sandbox/src/checkout.mjs";
import {ProviderState} from "../examples/cloudflare-checkout-sandbox/src/provider.mjs";
import drill,{DrillCheckout,DrillProvider} from "../examples/cloudflare-checkout-sandbox/dr/worker.mjs";
import proxy from "../examples/cloudflare-checkout-sandbox/dr/proxy.mjs";

function matches(row,scope){return scope?.type==="key"?row.key===scope.key:scope?.type==="run"?row.run_id===scope.runId:true;}
function fakeEnvironment(){
 const pending=[],actions=[];
 class Checkout{
   constructor(){this.orders=new Map();this.outbox=new Map();this.faults=new Set();}
   async fetch(_url,options){
     const x=JSON.parse(options.body);actions.push(x.action);let value;
     try{
       switch(x.action){
         case "create":{
           const previous=this.orders.get(x.key);
           if(previous&&(previous.amount!==x.amount||(x.runId!=null&&previous.run_id!==x.runId)))throw Error("409: identical key, different amount");
           if(!previous){
             this.orders.set(x.key,{key:x.key,amount:x.amount,status:"PENDING",fault:x.fault,account:x.account,run_id:x.runId??null});
             this.outbox.set(x.key,{key:x.key,delivered:0,sends:0,published:0});
           }
           value={...this.orders.get(x.key),replay:!!previous};break;
         }
         case "state":{const orders=[...this.orders.values()].filter(o=>matches(o,x.scope));const keys=new Set(orders.map(o=>o.key));value={orders,outbox:[...this.outbox.values()].filter(o=>keys.has(o.key)),rowsRead:null};break;}
         case "bookmark":value="FAKE_BOOKMARK";break;
         case "enqueue":{
           let count=0;
           for(const o of this.orders.values()){
             const e=this.outbox.get(o.key);
             if((!x.keys||x.keys.includes(o.key))&&!e.delivered&&!e.published&&e.sends<3){e.sends++;e.published=1;pending.push({account:o.account,key:o.key,amount:o.amount,fault:o.fault,runId:o.run_id});count++;}
           }
           value={dispatched:count,pending:[...this.outbox.values()].filter(e=>!e.delivered).length};break;
         }
         case "replay":{
           for(const e of this.outbox.values())if(!e.delivered){e.sends=0;e.published=0;}
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
     const x=JSON.parse(options.body);actions.push(x.action);let value;
     if(x.action==="lookup")value=this.charges.get(x.key)||null;
     else if(x.action==="charge"){
       value=this.charges.get(x.key);
       const replay=!!value;
       if(value&&(value.amount!==x.amount||(x.runId!=null&&value.run_id!==x.runId)))
         return Response.json({ok:false,error:"Provider key conflict"},{status:400});
       if(!value){value={key:x.key,amount:x.amount,currency:"USD",charge_id:"mock",run_id:x.runId??null};this.charges.set(x.key,value);}
       value={...value,replay};
     }else if(x.action==="state")value={charges:[...this.charges.values()].filter(o=>matches(o,x.scope)),rowsRead:null};
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
 return {CHECKOUT,PROVIDER,PAYMENTS_QUEUE:{async send(x){pending.push(x);}},pending,actions};
}
const ctx={access:{async getIdentity(){return {email:"owner@example.test"};}}};
// Real source SQL against SQLite; only platform transport and alarm are adapters.
// This verifies quota semantics, not Cloudflare-native execution.
function sqliteEnvironment(Class=CheckoutState){
  const objects=new Map(),databases=[],sent=[],evidence=new Map(),readbacks=[],alarms=[];
  const env={PAYMENTS_QUEUE:{async send(value){sent.push(value);}},PROVIDER:{idFromName:name=>name,get(){return {async fetch(_url,options){const input=JSON.parse(options.body);readbacks.push(input.key);return Response.json({ok:true,value:evidence.get(input.key)||null});}};}}};
  env.CHECKOUT={idFromName:name=>name,get(name){
    if(!objects.has(name)){
      const db=new DatabaseSync(":memory:");databases.push(db);
      const storage={sql:{exec(sql,...params){const rows=db.prepare(sql).all(...params);return {toArray:()=>rows};}},
        transactionSync(fn){db.exec("BEGIN");try{const value=fn();db.exec("COMMIT");return value;}catch(error){db.exec("ROLLBACK");throw error;}},
        async setAlarm(at){alarms.push(at);},async getCurrentBookmark(){throw Error("PITR is unavailable in this local SQL adapter");}};
      const object=new Class({storage},env),fetch=object.fetch.bind(object);
      object.fetch=(request,options)=>fetch(request instanceof Request?request:new Request(request,options));
      objects.set(name,object);
    }
    return objects.get(name);
  }};
  return {env,sent,evidence,readbacks,alarms,close(){for(const db of databases)db.close();}};
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
test("pending total survives recreation, duplicate callbacks and transaction rollback",()=>{
  const fixture=sqliteEnvironment();
  try{
    let object=fixture.env.CHECKOUT.get("counter");
    for(const key of ["a","b"])object.create({key,amount:1250,fault:"none",account:"counter"});
    assert.equal(object.pendingCount(),2);
    object.create({key:"a",amount:1250,fault:"none",account:"counter"});
    assert.equal(object.pendingCount(),2);
    object.paid({key:"a",amount:1250});object.paid({key:"a",amount:1250});
    assert.equal(object.pendingCount(),1);
    assert.throws(()=>object.paid({key:"b",amount:99}),/mismatch/);
    assert.equal(object.pendingCount(),1);
    // Failure after the increment rolls back the Order, Outbox and total.
    object.sql.exec("INSERT INTO faults(key,injected) VALUES('rollback',0)");
    assert.throws(()=>object.create({key:"rollback",amount:1250,fault:"none",account:"counter"}));
    assert.equal(object.pendingCount(),1);
    assert.equal(object.rows("SELECT key FROM orders WHERE key='rollback'").length,0);
    assert.equal(object.rows("SELECT key FROM outbox WHERE key='rollback'").length,0);
    // Emulate an old ledger with no materialized total, then reopen it.
    object.sql.exec("DROP TABLE outbox_totals");
    object=new CheckoutState(object.ctx,object.env);
    assert.equal(object.pendingCount(),1);
    const exec=object.sql.exec;
    object.sql.exec=(query,...args)=>{assert.doesNotMatch(query,/COUNT\(/);return exec(query,...args);};
    object=new CheckoutState(object.ctx,object.env);
    assert.equal(object.pendingCount(),1);
    object.sql.exec=exec;
    // An underflow refuses and rolls back the preceding PAID update.
    object.sql.exec("UPDATE outbox_totals SET pending=0 WHERE id=1");
    assert.throws(()=>object.paid({key:"b",amount:1250}),/CHECK/);
    assert.equal(object.rows("SELECT status FROM orders WHERE key='b'")[0].status,"PENDING");
    assert.equal(object.rows("SELECT delivered FROM outbox WHERE key='b'")[0].delivered,0);
    object.sql.exec("UPDATE outbox_totals SET pending=1 WHERE id=1");
    object.paid({key:"b",amount:1250});
    assert.equal(object.pendingCount(),0);
  }finally{fixture.close();}
});
test("Queue quota refusal preserves pending work and stops automatic publish retries",async t=>{
  let now=Date.now();t.mock.method(Date,"now",()=>now);
  const fixture=sqliteEnvironment();
  try{
    const object=fixture.env.CHECKOUT.get("user");
    object.create({key:"unknown",amount:1250,fault:"none",account:"user"});
    let attempts=0;
    fixture.env.PAYMENTS_QUEUE.send=async()=>{attempts++;throw Error("Platform quota exceeded");};
    for(let i=0;i<5;i++){await object.alarm();now+=30001;}
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
test("successful publication is excluded from concurrent and later relays",async()=>{
  const fixture=sqliteEnvironment();
  try{
    const object=fixture.env.CHECKOUT.get("user");
    object.create({key:"pending",amount:1250,fault:"none",account:"user"});
    await Promise.all(Array.from({length:8},()=>object.enqueue()));
    assert.equal(fixture.sent.length,1);
    assert.equal(object.snapshot().outbox[0].published,1);
    await object.alarm();
    assert.equal(fixture.sent.length,1);
    for(let i=0;i<4;i++)await object.fetch(post("replay",{action:"replay"}));
    assert.equal(object.snapshot().outbox[0].replays,0);
    assert.equal(fixture.sent.length,1);
    assert.equal(fixture.readbacks.length,4);
    object.paid({key:"pending",amount:1250});
    const before=fixture.sent.length;
    await object.fetch(post("replay",{action:"replay"}));
    assert.equal(fixture.sent.length,before);
    for(let i=0;i<18;i++)object.create({key:"next-"+i,amount:1250,fault:"none",account:"user"});
    for(let i=0;i<6;i++)await object.enqueue();
    assert.equal(fixture.sent.length,19);
    assert.ok(object.snapshot().outbox.filter(row=>row.key.startsWith("next-")).every(row=>row.sends===1&&row.published===1));
    assert.ok(fixture.sent.every(message=>message.amount===1250));
  }finally{fixture.close();}
});
test("Create relays only its key even beyond the first fifteen pending orders",async()=>{
  const fixture=sqliteEnvironment();
  try{
    const object=fixture.env.CHECKOUT.get("access-user:owner@example.test");
    for(let i=0;i<18;i++)object.create({key:"a-"+i,amount:1250,fault:"none",account:"owner@example.test"});
    const response=await worker.fetch(post("api/create",{key:"z-current",amount:1250}),fixture.env,ctx);
    assert.equal(response.status,202);
    assert.deepEqual(fixture.sent.map(row=>row.key),["z-current"]);
    await worker.fetch(post("api/create",{key:"z-current",amount:1250}),fixture.env,ctx);
    assert.equal(fixture.sent.length,1);
  }finally{fixture.close();}
});
test("unknown publish reply reads provider evidence before deciding to resend",async t=>{
  let now=Date.now();t.mock.method(Date,"now",()=>now);
  const fixture=sqliteEnvironment();
  try{
    const object=fixture.env.CHECKOUT.get("user");
    object.create({key:"lost-publish",amount:1250,fault:"none",account:"user"});
    fixture.env.PAYMENTS_QUEUE.send=async message=>{fixture.sent.push(message);throw Error("Lost publish reply after Queue accepted");};
    await object.enqueue();
    await object.enqueue();
    assert.equal(fixture.sent.length,1);
    fixture.evidence.set("lost-publish",{key:"lost-publish",amount:1250,currency:"USD",charge_id:"readback"});
    now+=30001;await object.alarm();
    assert.equal(fixture.sent.length,1);
    assert.equal(object.snapshot().orders[0].status,"PAID");
    assert.equal(object.snapshot().outbox[0].delivered,1);
    assert.deepEqual(fixture.readbacks,["lost-publish"]);
  }finally{fixture.close();}
});
test("late publish completion cannot overwrite a manual recovery epoch",async t=>{
  let now=Date.now();t.mock.method(Date,"now",()=>now);
  const fixture=sqliteEnvironment();
  try{
    const object=fixture.env.CHECKOUT.get("user");
    object.create({key:"slow",amount:1250,fault:"none",account:"user"});
    let finish;
    fixture.env.PAYMENTS_QUEUE.send=()=>new Promise(resolve=>{finish=resolve;});
    const first=object.enqueue();
    await object.fetch(post("replay",{action:"replay"}));
    assert.equal(object.snapshot().outbox[0].replays,0);
    now+=30001;
    fixture.env.PAYMENTS_QUEUE.send=async()=>{throw Error("New publish unavailable");};
    await object.fetch(post("replay",{action:"replay"}));
    finish();await first;
    const row=object.snapshot().outbox[0];
    assert.equal(row.replays,1);assert.equal(row.sends,1);
    assert.equal(row.published,0);assert.equal(row.next_attempt_at,now+30000);
  }finally{fixture.close();}
});
test("manual recovery reconciles known effects and refuses mismatched evidence",async()=>{
  const fixture=sqliteEnvironment();
  try{
    const object=fixture.env.CHECKOUT.get("user");
    object.create({key:"known",amount:1250,fault:"none",account:"user"});
    await object.enqueue();
    fixture.evidence.set("known",{key:"known",amount:1250,currency:"USD",charge_id:"known"});
    await object.fetch(post("replay",{action:"replay"}));
    assert.equal(fixture.sent.length,1);assert.equal(object.snapshot().orders[0].status,"PAID");
    object.create({key:"mismatch",amount:1250,fault:"none",account:"user"});
    fixture.evidence.set("mismatch",{key:"mismatch",amount:999,currency:"USD"});
    const response=await object.fetch(post("replay",{action:"replay"}));
    assert.equal(response.status,400);
    assert.equal(object.snapshot().orders.find(row=>row.key==="mismatch").status,"PENDING");
    assert.equal(fixture.sent.length,1);
  }finally{fixture.close();}
});
test("recovery wake-up is persisted before committing intent or awaiting Queue",async()=>{
  const fixture=sqliteEnvironment();
  try{
    const object=fixture.env.CHECKOUT.get("user");
    object.ctx.storage.setAlarm=async()=>{throw Error("Alarm persistence unavailable");};
    assert.equal((await object.fetch(post("create",{action:"create",key:"new",amount:1250,fault:"none",account:"user"}))).status,400);
    assert.equal(object.snapshot().orders.length,0);
    object.create({key:"relay",amount:1250,fault:"none",account:"user"});
    await assert.rejects(object.alarm(),/Alarm persistence unavailable/);
    assert.equal(fixture.sent.length,0);
    object.sql.exec("UPDATE outbox SET sends=2,next_attempt_at=0 WHERE key='relay'");
    await assert.rejects(object.alarm(),/Alarm persistence unavailable/);
    assert.equal(fixture.sent.length,0);
    object.ctx.storage.setAlarm=async at=>fixture.alarms.push(at);
    object.sql.exec("UPDATE outbox SET sends=0,next_attempt_at=0 WHERE key='relay'");
    fixture.env.PAYMENTS_QUEUE.send=async message=>{
      assert.ok(fixture.alarms.length>0);fixture.sent.push(message);
    };
    await object.alarm();assert.equal(fixture.sent.length,1);
  }finally{fixture.close();}
});
test("an expired readback cannot publish after another recovery epoch succeeds",async t=>{
  let now=Date.now();t.mock.method(Date,"now",()=>now);
  const fixture=sqliteEnvironment();
  try{
    const object=fixture.env.CHECKOUT.get("user");
    object.create({key:"delayed-read",amount:1250,fault:"none",account:"user"});
    fixture.env.PAYMENTS_QUEUE.send=async()=>{throw Error("Unknown publish result");};
    await object.enqueue();now+=30001;
    let finish;
    fixture.env.PROVIDER.get=()=>({fetch:()=>new Promise(resolve=>{finish=()=>resolve(Response.json({ok:true,value:null}));})});
    const old=object.enqueue();
    // Wait for the fake storage await to finish, then the deferred provider read.
    await new Promise(resolve=>setImmediate(resolve));
    now+=30001;
    fixture.env.PROVIDER.get=()=>({async fetch(){return Response.json({ok:true,value:null});}});
    fixture.env.PAYMENTS_QUEUE.send=async message=>fixture.sent.push(message);
    await object.fetch(post("replay",{action:"replay"}));
    finish();await old;
    assert.equal(fixture.sent.length,1);assert.equal(object.snapshot().outbox[0].published,1);
  }finally{fixture.close();}
});
test("mixed replay readback failure does not reset an earlier published intent",async()=>{
  const fixture=sqliteEnvironment();
  try{
    const object=fixture.env.CHECKOUT.get("user");
    for(const key of ["a","b"])object.create({key,amount:1250,fault:"none",account:"user"});
    await object.enqueue();
    fixture.evidence.set("b",{key:"b",amount:999,currency:"USD"});
    const response=await object.fetch(post("replay",{action:"replay"}));
    assert.equal(response.status,400);
    assert.ok(object.snapshot().outbox.every(row=>row.published===1&&row.replays===0));
    await object.alarm();assert.equal(fixture.sent.length,2);
  }finally{fixture.close();}
});
function post(path,body={}){return new Request("https://sandbox.example/"+path,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});}
test("scoped API refuses missing/ambiguous scopes, isolates Run IDs and skips bookmarks",async()=>{
  const env=fakeEnvironment();
  for(const input of [{},{key:"x",runId:"run"},{runId:"%"},{key:"bad'"},{full:true,key:"x"}])
    assert.equal((await worker.fetch(post("api/state",input),env,ctx)).status,400);
  assert.equal(env.actions.length,0);
  for(const [key,runId] of [["run-a-1-0","run-a"],["run-a-b-1-0","run-a-b"]]){
    assert.equal((await worker.fetch(post("api/create",{key,runId,amount:1250}),env,ctx)).status,202);
    await worker.queue({messages:[{body:env.pending.at(-1),ack(){},retry(){}}]},env);
  }
  const read=async body=>(await worker.fetch(post("api/state",body),env,ctx)).json();
  const run=await read({runId:"run-a"});
  assert.deepEqual(run.orders.map(o=>o.key),["run-a-1-0"]);
  assert.deepEqual(run.charges.map(o=>o.key),["run-a-1-0"]);
  assert.deepEqual(run.outbox.map(o=>o.key),["run-a-1-0"]);
  assert.equal(run.integrity.scope.type,"run");assert.equal(run.readbackUsage.totalRowsRead,null);
  assert.equal("bookmarks" in run,false);assert.equal(env.actions.includes("bookmark"),false);
  const empty=await read({key:"missing"});assert.deepEqual(empty.orders,[]);assert.deepEqual(empty.charges,[]);
  const other={access:{async getIdentity(){return {email:"other@example.test"};}}};
  assert.deepEqual((await (await worker.fetch(post("api/state",{runId:"run-a"}),env,other)).json()).orders,[]);
  assert.equal((await worker.fetch(post("api/create",{key:"run-a-1-0",runId:"run-a-b",amount:1250}),env,ctx)).status,409);
  assert.ok((await read({full:true,includeBookmarks:true})).bookmarks);
});
test("real source SQL uses indexed exact Run ID and keeps legacy Key readback",async()=>{
  const fixture=sqliteEnvironment();
  try{
    const object=fixture.env.CHECKOUT.get("user");
    for(const [key,runId] of [["r-1","r"],["r-child-1","r-child"],["legacy",null]])object.create({key,runId,amount:1250,account:"user",fault:"none"});
    assert.deepEqual(object.readState(readScope({runId:"r"})).orders.map(o=>o.key),["r-1"]);
    assert.deepEqual(object.readState(readScope({key:"legacy"})).outbox.map(o=>o.key),["legacy"]);
    assert.throws(()=>object.create({key:"r-1",runId:"changed",amount:1250}),/different Run ID/);
    assert.throws(()=>object.readState({type:"unknown"}),/Select exactly one/);
    assert.match(JSON.stringify(object.rows("EXPLAIN QUERY PLAN SELECT key FROM orders WHERE run_id=?","r")),/orders_run_id/);
  }finally{fixture.close();}
});
test("Access-gated: no authenticated ctx rejects every route",async()=>{
  const env=fakeEnvironment();
  assert.equal((await worker.fetch(post("api/state",{full:true}),env,{})).status,403);
  assert.equal((await worker.fetch(new Request("https://sandbox.example/"),env,{})).status,403);
});
test("API reports platform quota uncertainty without inventing remaining order capacity",async()=>{
  const env=fakeEnvironment();
  const read=await (await worker.fetch(post("api/state",{full:true}),env,ctx)).json();
  assert.equal(read.schema,"checkout-remote-evidence@3");
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
  let read=await (await worker.fetch(post("api/state",{full:true}),env,ctx)).json();
  assert.equal(read.orders[0].status,"PENDING");assert.equal(read.charges.length,1);
  await worker.queue({messages:[message]},env);
  read=await (await worker.fetch(post("api/state",{full:true}),env,ctx)).json();
  assert.equal(read.orders[0].status,"PAID");assert.equal(read.charges.length,1);assert.equal(acks,1);
  assert.equal(read.integrity.pass,true);
  assert.equal((await worker.fetch(post("api/create",{...input,amount:1300}),env,ctx)).status,409);
});
test("mixed batch retains per-message recovery and emits secret-free live timings",async t=>{
  const records=[];t.mock.method(console,"log",line=>records.push(JSON.parse(line)));
  const env=fakeEnvironment(),runId="timing-control";
  for(const key of ["first","lost","last"])
    await worker.fetch(post("api/create",{key,runId,amount:1250,fault:key==="lost"?"lost_reply":"none"}),env,ctx);
  const acks=[],retries=[];
  const messages=env.pending.map(body=>({body,timestamp:new Date(Date.now()-1000),attempts:1,
    ack(){acks.push(body.key);},retry(){retries.push(body.key);}}));
  await worker.queue({messages},env);
  assert.deepEqual(acks,["first","last"]);assert.deepEqual(retries,["lost"]);
  assert.equal(records.length,3);
  assert.ok(records.every(r=>r.batchSize===3&&r.queueLagMs>=1000&&r.processingMs>=0));
  assert.ok(records.every(r=>!("account" in r)&&!("headers" in r)));
  const lost=records.find(r=>r.key==="lost");assert.equal(lost.result,"retry-injected");
  assert.equal("paidConfirmedAt" in lost,false);
  assert.ok(records.filter(r=>r.result==="ack").every(r=>r.paidConfirmedAt>=r.startedAt));
  await worker.queue({messages:[{...messages[1],attempts:2}]},env);
  assert.equal(records.at(-1).providerFound,true);assert.equal(records.at(-1).result,"ack");
  assert.ok(records.at(-1).chargeMs>=0);
  assert.equal(env.actions.filter(action=>action==="lookup").length,0);
  const state=await (await worker.fetch(post("api/state",{runId}),env,ctx)).json();
  assert.equal(state.charges.length,3);assert.ok(state.orders.every(o=>o.status==="PAID"));
});
test("provider transaction reads an unknown committed effect before any new charge",async()=>{
  const fixture=sqliteEnvironment(ProviderState);
  try{
    const provider=fixture.env.CHECKOUT.get("provider"),input={action:"charge",key:"unknown-effect",amount:1250,runId:"provider-control"};
    const call=async payload=>{const response=await provider.fetch(post("charge",payload));return {status:response.status,...await response.json()};};
    const first=await call(input),retry=await call(input);
    assert.equal(first.value.replay,false);assert.equal(retry.value.replay,true);
    assert.equal(first.value.charge_id,retry.value.charge_id);
    assert.equal((await call({...input,amount:1251})).status,400);
    assert.equal((await call({...input,runId:"another-run"})).status,400);
    const state=await call({action:"state",scope:{type:"key",key:input.key}});
    assert.equal(state.value.charges.length,1);assert.equal(state.value.charges[0].amount,1250);
  }finally{fixture.close();}
});
test("mismatched provider evidence leaves checkout pending and retries the message",async t=>{
  t.mock.method(console,"log",()=>{});t.mock.method(console,"warn",()=>{});
  const env=fakeEnvironment();
  await worker.fetch(post("api/create",{key:"evidence-control",amount:1250}),env,ctx);
  env.PROVIDER.get=()=>({async fetch(){return Response.json({ok:true,value:{key:"another-payment",amount:1250,currency:"USD",replay:true}});}});
  let acks=0,retries=0;
  await worker.queue({messages:[{body:env.pending[0],ack(){acks++;},retry(){retries++;}}]},env);
  assert.equal(acks,0);assert.equal(retries,1);
  assert.equal([...env.CHECKOUT.objects.values()][0].orders.get("evidence-control").status,"PENDING");
});
test("replay preserves same identity and anonymous cross-site writes refuse",async()=>{
  const env=fakeEnvironment();
  await worker.fetch(post("api/create",{key:"same",amount:100,fault:"none"}),env,ctx);
  await worker.fetch(post("api/create",{key:"same",amount:100,fault:"none"}),env,ctx);
  const data=await (await worker.fetch(post("api/state",{full:true}),env,ctx)).json();
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
