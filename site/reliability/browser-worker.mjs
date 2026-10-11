// Browser-only SQLite-Wasm / OPFS payment fault lab. No external payment calls.
import sqlite3InitModule from "https://cdn.jsdelivr.net/npm/@sqlite.org/sqlite-wasm@3.53.4-build2/dist/index.mjs";
import {validPayment,invariant} from "./logic.mjs";
let db,sqlite;
function sql(statement,bind=[]){
  const resultRows=[];
  db.exec({sql:statement,bind,resultRows,rowMode:"object"});
  return resultRows;
}
function transaction(fn){
  sql("BEGIN IMMEDIATE");
  try { const value=fn();sql("COMMIT");return value; }
  catch(err){sql("ROLLBACK");throw err;}
}
function event(type,key,detail){
  sql("INSERT INTO events(type,payment_key,detail,at_ms) VALUES(?,?,?,?)",[type,key,detail,Date.now()]);
}
function current(){
  const orders=sql("SELECT payment_key AS key,amount_cents AS amount,status FROM orders ORDER BY payment_key");
  const charges=sql("SELECT payment_key AS key,amount_cents AS amount,currency FROM charges ORDER BY payment_key");
  const outbox=sql("SELECT payment_key AS key,delivered FROM outbox ORDER BY payment_key");
  const events=sql("SELECT seq,type,payment_key AS key,detail,at_ms FROM events ORDER BY seq DESC LIMIT 70").reverse();
  return {orders,charges,outbox,events,integrity:invariant({orders,charges}),storage:"SQLite-Wasm / OPFS",sqlite:sqlite.version.libVersion};
}
async function initialize(){
  sqlite=await sqlite3InitModule();
  if(!("opfs" in sqlite)||!self.crossOriginIsolated)throw new Error("SQLite OPFS needs a secure, cross-origin-isolated browser. Check COOP/COEP and browser support.");
  db=new sqlite.oo1.OpfsDb("/medium-checkout-reliability-v1.sqlite3");
  sql("CREATE TABLE IF NOT EXISTS orders(payment_key TEXT PRIMARY KEY,amount_cents INTEGER NOT NULL CHECK(amount_cents>0),status TEXT NOT NULL CHECK(status IN ('PENDING','PAID')))");
  sql("CREATE TABLE IF NOT EXISTS outbox(payment_key TEXT PRIMARY KEY,delivered INTEGER NOT NULL DEFAULT 0 CHECK(delivered IN (0,1)))");
  sql("CREATE TABLE IF NOT EXISTS charges(payment_key TEXT PRIMARY KEY,amount_cents INTEGER NOT NULL,currency TEXT NOT NULL,charge_id TEXT UNIQUE NOT NULL)");
  sql("CREATE TABLE IF NOT EXISTS events(seq INTEGER PRIMARY KEY AUTOINCREMENT,type TEXT NOT NULL,payment_key TEXT NOT NULL,detail TEXT NOT NULL,at_ms INTEGER NOT NULL)");
}
function create(key,amount){
  validPayment(key,amount);
  return transaction(()=>{
    const existing=sql("SELECT amount_cents AS amount,status FROM orders WHERE payment_key=?",[key])[0];
    if(existing){if(existing.amount!==amount)throw new Error("409: same Idempotency-Key with different amount");event("REPLAY",key,"Same purchase identity; no second order");return;}
    if(sql("SELECT COUNT(*) AS n FROM orders")[0].n>=200)throw new Error("Sandbox cap: 200 orders. Export evidence and reset.");
    sql("INSERT INTO orders VALUES(?,?,'PENDING')",[key,amount]);
    sql("INSERT INTO outbox VALUES(?,0)",[key]);
    event("CREATE",key,"Atomic Order + Outbox commit");
  });
}
function provider(key){
  const o=sql("SELECT amount_cents AS amount FROM orders WHERE payment_key=?",[key])[0];if(!o)throw new Error("Missing order");
  return transaction(()=>{
    const existing=sql("SELECT amount_cents AS amount FROM charges WHERE payment_key=?",[key])[0];
    if(existing){if(existing.amount!==o.amount)throw new Error("Provider charge conflict");return;}
    sql("INSERT INTO charges VALUES(?,?,'USD',?)",[key,o.amount,crypto.randomUUID()]);
    event("PROVIDER_COMMIT",key,"Provider ledger committed independently of order status");
  });
}
function reconcile(key){
  const o=sql("SELECT amount_cents AS amount,status FROM orders WHERE payment_key=?",[key])[0];if(!o)throw new Error("Missing order");
  const c=sql("SELECT amount_cents AS amount,currency FROM charges WHERE payment_key=?",[key])[0];
  if(!c){event("UNKNOWN",key,"No matching provider record; do not declare failure or PAID");return;}
  if(c.amount!==o.amount||c.currency!=="USD")throw new Error("Provider evidence conflict");
  transaction(()=>{
    sql("UPDATE orders SET status='PAID' WHERE payment_key=? AND status='PENDING'",[key]);
    sql("UPDATE outbox SET delivered=1 WHERE payment_key=?",[key]);
    event("READBACK_PAID",key,"Provider evidence reconciled; pending intent completed");
  });
}
function scenario(action,key,amount){
  if(action==="reset"){transaction(()=>{for(const t of ["events","outbox","orders","charges"])sql("DELETE FROM "+t);});return;}
  if(action==="duplicate"){
    for(let i=0;i<Math.min(36,Number(amount)||1);i++)create(key,1250);
    event("DUPLICATE_EXERCISE",key,"Sequential replay only; not a multi-thread stress test");return;
  }
  if(action==="create")return create(key,amount);
  if(action==="lost_reply"||action==="worker_crash"){
    provider(key);
    event(action==="lost_reply"?"RESPONSE_LOST":"WORKER_CRASH",key,"After provider COMMIT; checkout stays PENDING");
    return;
  }
  if(action==="reconcile")return reconcile(key);
  if(action==="counts")return;
  throw new Error("Unsupported action");
}
self.onmessage=async ({data})=>{
  const id=data?.id;
  try{
    if(!db)await initialize();
    if(data.action&&data.action!=="init")scenario(data.action,data.key,data.amount);
    self.postMessage({id,ok:true,result:current()});
  }catch(err){self.postMessage({id,ok:false,error:err instanceof Error?err.message:String(err)});}
};
