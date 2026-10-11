// Operator-only smoke: admission and settlement are measured separately.
import http from "k6/http";
import {check,sleep} from "k6";
import {Counter,Rate,Trend} from "k6/metrics";
const url=(__ENV.TEST_URL||"http://127.0.0.1:8787").replace(/\/$/,"");
const local=/^http:\/\/(127\.0\.0\.1|localhost):8787$/.test(url);
const runId=__ENV.RUN_ID,rate=Number(__ENV.ARRIVALS_PER_SECOND||2),seconds=Number(__ENV.DURATION_SECONDS||8);
if(!runId||!/^[a-zA-Z0-9-]{1,40}$/.test(runId))throw Error("Supply a unique RUN_ID (1–40 letters, digits or hyphens)");
if(![1,2].includes(rate)||![4,8,30,60].includes(seconds)||rate*seconds>60)
  throw Error("Bounded fixture: rate 1 or 2, duration 4, 8, 30 or 60 seconds, at most 60 scheduled intents");
if(!local&&(!/^https:\/\/[a-z0-9-]+\.[a-z0-9-]+\.workers\.dev$/.test(url)||!__ENV.CF_ACCESS_TOKEN))
  throw Error("Remote targets require an application-scoped Access JWT from cloudflared access login");
if(!local&&__ENV.CONFIRM_FREE_PLAN!=="Workers Free")
  throw Error("Read back Cloudflare Billing, then set CONFIRM_FREE_PLAN='Workers Free'; never upgrade for a load run");
const headers={"Content-Type":"application/json"};
if(__ENV.CF_ACCESS_TOKEN)headers["Cf-Access-Token"]=__ENV.CF_ACCESS_TOKEN;
// Cover a boundary tick conservatively without increasing the arrival rate/window.
// Settlement waiting occupies a VU; reserve one slot per possible finite arrival.
const maxIntents=rate*seconds+1;
const accepted=new Counter("accepted_intents"),paid=new Counter("paid_orders");
const complete=new Rate("settlement_success"),admission=new Rate("admission_success");
const admissionLatency=new Trend("admission_ms",true),settlementLatency=new Trend("settlement_ms",true);
const pendingAge=new Trend("observed_pending_age_ms",true),elapsed=new Trend("run_elapsed_ms",true);
export const options={
  scenarios:{bounded:{executor:"constant-arrival-rate",rate,timeUnit:"1s",duration:seconds+"s",
    preAllocatedVUs:maxIntents,maxVUs:maxIntents,gracefulStop:"35s"}},
  summaryTrendStats:["min","med","p(95)","p(99)","max"],
  thresholds:{admission_success:["rate==1"],settlement_success:["rate==1"],dropped_iterations:["count==0"]}
};
const readRequests=new Counter("readback_requests"),readRows=new Counter("readback_rows_read"),readBytes=new Counter("readback_response_bytes");
function state(selection){
  const r=http.post(url+"/api/state",JSON.stringify(selection),{headers,tags:{phase:"readback"},timeout:"5s"});
  if(r.status!==200)throw Error("Owner readback failed: HTTP "+r.status);
  const value=r.json();
  if(value.schema!=="checkout-remote-evidence@3"||typeof value.readbackUsage?.totalRowsRead!=="number")throw Error("Native scoped readback measurement unavailable");
  readRequests.add(1);readRows.add(value.readbackUsage.totalRowsRead);readBytes.add(r.body.length);
  return value;
}
export function setup(){
  const before=state({runId});
  if(before.orders.length||before.charges.length||before.outbox.length)throw Error("RUN_ID already exists; do not mix runs");
  if(before.schema!=="checkout-remote-evidence@3")throw Error("Read back the deployed quota policy before this bounded run");
  return {start:Date.now()};
}
export default function(run){
  const key=runId+"-"+__VU+"-"+__ITER,start=Date.now();
  const r=http.post(url+"/api/create",JSON.stringify({key,runId,amount:1250,fault:"none"}),
    {headers,tags:{phase:"admission"},timeout:"5s"});
  admissionLatency.add(Date.now()-start);admission.add(r.status===202);
  if(r.status===202)accepted.add(1);
  // Unknown admission outcome requires readback, never a new key or blind retry.
  let settled=false,lastError=null;
  while(Date.now()-start<30000){
    try{
      const s=state({key}),order=s.orders.find(o=>o.key===key),charges=s.charges.filter(c=>c.key===key);
      const outbox=s.outbox.find(o=>o.key===key);
      if(order?.status==="PAID"){
        settled=charges.length===1&&charges[0].amount===1250&&charges[0].currency==="USD"&&outbox?.delivered===1;
        if(settled)break;
        lastError="PAID evidence incomplete or conflicting; repeat same-key readback";
      }
      if(order?.status==="PENDING")pendingAge.add(Date.now()-start);
    }catch(error){lastError=String(error);}
    sleep(2);
  }
  const duration=Date.now()-start;
  if(settled){paid.add(1);settlementLatency.add(duration);}
  complete.add(settled);elapsed.add(Date.now()-run.start);
  check(settled,{"PAID with one matching charge and consumed outbox":v=>v});
  console.log(JSON.stringify({key,admitted:r.status===202,admissionStatus:r.status,settled,observedSettlementMs:duration,lastError}));
}
export function teardown(){
  const final=state({runId});
  console.log(JSON.stringify({runId,finalOrders:final.orders.filter(o=>o.key.startsWith(runId+"-")),
    finalCharges:final.charges.filter(c=>c.key.startsWith(runId+"-")),finalOutbox:final.outbox.filter(o=>o.key.startsWith(runId+"-")),
    integrity:final.integrity,readbackUsage:final.readbackUsage}));
}
export function handleSummary(data){
  const count=name=>data.metrics[name]?.values.count||0;
  const elapsedSeconds=(data.metrics.run_elapsed_ms?.values.max||0)/1000;
  const result={runId,scope:"bounded smoke; settlement observations include polling delay",arrivalsPerSecond:rate,
    arrivalWindowSeconds:seconds,maxIntentBudget:maxIntents,accepted:count("accepted_intents"),paid:count("paid_orders"),
    acceptedPerArrivalSecond:count("accepted_intents")/seconds,
    paidPerObservedSecond:elapsedSeconds?count("paid_orders")/elapsedSeconds:null,
    readback:{requests:count("readback_requests"),sqlRowsRead:count("readback_rows_read"),responseBytes:count("readback_response_bytes"),scope:"Readback SQL cursors only; not whole account usage"},metrics:data.metrics};
  return {[__ENV.EVIDENCE_FILE||"stdout"]:JSON.stringify(result,null,2)+"\n"};
}
