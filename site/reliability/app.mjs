const worker=new Worker("/assets/reliability/browser-worker.mjs",{type:"module"});
const $=id=>document.getElementById(id);
const pending=new Map();let sequence=0,snapshot=null;
worker.onmessage=({data})=>{
  const request=pending.get(data.id);if(!request)return;
  pending.delete(data.id);
  if(data.ok)request.resolve(data.result);else request.reject(new Error(data.error||"Worker refused"));
};
worker.onerror=event=>{
  for(const item of pending.values())item.reject(new Error("SQLite Worker unavailable; check COOP/COEP, OPFS, and Wasm."));
  pending.clear();$("reliability-error").textContent="Browser engine failed to load. "+(event.message||"Check browser console");
};
function call(action,key="",amount=0){
  const id=++sequence;
  return new Promise((resolve,reject)=>{pending.set(id,{resolve,reject});worker.postMessage({id,action,key,amount});});
}
function show(result){
  snapshot=result;
  const {orders,charges,outbox,events,integrity}=result;
  $("reliability-summary").textContent="Orders: "+orders.length+" · PAID: "+orders.filter(x=>x.status==="PAID").length+" · Mock charges: "+charges.length+" · Outbox pending: "+outbox.filter(x=>!x.delivered).length;
  $("reliability-integrity").textContent=(integrity.pass?"PASS (scoped): ":"FAIL: ")+integrity.reason;
  $("reliability-records").textContent=JSON.stringify({orders,charges,outbox},null,2);
  $("reliability-events").textContent=events.map(e=>new Date(e.at_ms).toISOString()+" | "+e.type+" | "+e.key+" | "+e.detail).join("\n")||"No events";
}
async function run(action){
  const status=$("reliability-ready"),error=$("reliability-error");
  error.textContent="";status.textContent="執行中："+action;
  try{
    if(action==="export"){
      if(!snapshot)throw Error("No evidence recorded");
      const evidence={schema:"checkout-browser-evidence@1",at:new Date().toISOString(),scope:"single-browser SQLite-Wasm OPFS; virtual provider",...snapshot};
      const blob=new Blob([JSON.stringify(evidence,null,2)],{type:"application/json"});
      const url=URL.createObjectURL(blob);const a=document.createElement("a");
      a.href=url;a.download="checkout-browser-evidence.json";a.click();
      setTimeout(()=>URL.revokeObjectURL(url),1000);status.textContent="已匯出此瀏覽器的實際資料";return;
    }
    const key=$("payment-key").value.trim(),amount=Number($("payment-amount").value);
    const result=await call(action==="refresh"?"counts":action,key,action==="duplicate"?36:amount);
    show(result);status.textContent="SQLite "+result.sqlite+" · OPFS · "+action+" 已回讀";
  }catch(err){error.textContent=err.message;status.textContent="此操作未完成；保留原本狀態及拒絕原因";}
}
document.querySelectorAll(".reliability-lab button[data-action]").forEach(b=>b.addEventListener("click",()=>run(b.dataset.action)));
run("init");
