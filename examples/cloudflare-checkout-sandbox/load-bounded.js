// Operator-only smoke: admission and settlement are measured separately.
import http from "k6/http";
import {check,sleep} from "k6";
import {Counter,Rate,Trend} from "k6/metrics";
const url=(__ENV.TEST_URL||"http://127.0.0.1:8787").replace(/\/$/,"");
const local=/^http:\/\/(127\.0\.0\.1|localhost):8787$/.test(url);
const runId=__ENV.RUN_ID,rate=Number(__ENV.ARRIVALS_PER_SECOND||2),seconds=Number(__ENV.DURATION_SECONDS||8);
if(!runId||!/^[a-zA-Z0-9-]{1,40}$/.test(runId))throw Error("Supply a unique RUN_ID (1–40 letters, digits or hyphens)");
if(![1,2].includes(rate)||![4,8].includes(seconds))throw Error("Bounded fixture: rate 1 or 2, duration 4 or 8 seconds");
if(!local&&(!/^https:\/\/[a-z0-9-]+\.[a-z0-9-]+\.workers\.dev$/.test(url)||!__ENV.CF_ACCESS_TOKEN))
  throw Error("Remote targets require an application-scoped Access JWT from cloudflared access login");
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
function state(){
  const r=http.post(url+"/api/state","{}",{headers,tags:{phase:"readback"},timeout:"5s"});
  if(r.status!==200)throw Error("Owner readback failed: HTTP "+r.status);
  return r.json();
}
export function setup(){
  const before=state();
  if(before.orders.some(o=>o.key.startsWith(runId+"-")))throw Error("RUN_ID already exists; do not mix runs");
  if(before.orders.length+maxIntents>30)throw Error("Identity lacks quota for this bounded run");
  if(!before.usage||before.usage.orders+maxIntents>before.usage.limits.orders||
     before.usage.dispatches+3*maxIntents>before.usage.limits.dispatches)
    throw Error("Account lacks reserved order/dispatch capacity for this bounded run");
  return {start:Date.now()};
}
export default function(run){
  const key=runId+"-"+__VU+"-"+__ITER,start=Date.now();
  const r=http.post(url+"/api/create",JSON.stringify({key,amount:1250,fault:"none"}),
    {headers,tags:{phase:"admission"},timeout:"5s"});
  admissionLatency.add(Date.now()-start);admission.add(r.status===202);
  if(r.status===202)accepted.add(1);
  // Unknown admission outcome requires readback, never a new key or blind retry.
  let settled=false,lastError=null;
  while(Date.now()-start<30000){
    try{
      const s=state(),order=s.orders.find(o=>o.key===key),charges=s.charges.filter(c=>c.key===key);
      const outbox=s.outbox.find(o=>o.key===key);
      if(order?.status==="PAID"){
        settled=charges.length===1&&charges[0].amount===1250&&charges[0].currency==="USD"&&outbox?.delivered===1;
        break;
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
  const final=state();
  console.log(JSON.stringify({runId,finalOrders:final.orders.filter(o=>o.key.startsWith(runId+"-")),
    finalCharges:final.charges.filter(c=>c.key.startsWith(runId+"-")),finalOutbox:final.outbox.filter(o=>o.key.startsWith(runId+"-")),
    integrity:final.integrity}));
}
export function handleSummary(data){
  const count=name=>data.metrics[name]?.values.count||0;
  const elapsedSeconds=(data.metrics.run_elapsed_ms?.values.max||0)/1000;
  const result={runId,scope:"bounded smoke; settlement observations include polling delay",arrivalsPerSecond:rate,
    arrivalWindowSeconds:seconds,maxIntentBudget:maxIntents,accepted:count("accepted_intents"),paid:count("paid_orders"),
    acceptedPerArrivalSecond:count("accepted_intents")/seconds,
    paidPerObservedSecond:elapsedSeconds?count("paid_orders")/elapsedSeconds:null,metrics:data.metrics};
  return {[__ENV.EVIDENCE_FILE||"stdout"]:JSON.stringify(result,null,2)+"\n"};
}
