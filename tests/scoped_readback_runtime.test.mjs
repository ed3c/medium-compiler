// Real local workerd SQLite cursors; not Cloudflare account billing evidence.
import {test} from "node:test";
import assert from "node:assert/strict";
import {execFileSync} from "node:child_process";
import {mkdtempSync,readFileSync,rmSync} from "node:fs";
import {join} from "node:path";
import {tmpdir} from "node:os";
import {Miniflare,convertV4MiniflareOptions} from "miniflare";
test("workerd scoped cursors read only indexed payment/run rows as ledger grows",async()=>{
  const dir=mkdtempSync(join(tmpdir(),"scoped-readback-"));let runtime;
  try{
    execFileSync(process.execPath,["node_modules/wrangler/bin/wrangler.js","deploy","--config","examples/cloudflare-checkout-sandbox/wrangler.jsonc","--dry-run","--outdir",dir],{stdio:"pipe"});
    runtime=new Miniflare(convertV4MiniflareOptions({workers:[{name:"readback-test",modules:true,script:readFileSync(join(dir,"index.js"),"utf8"),compatibilityDate:"2026-10-11",
      durableObjects:{CHECKOUT:{className:"CheckoutState",useSQLite:true},PROVIDER:{className:"ProviderState",useSQLite:true}},
      queueProducers:{PAYMENTS_QUEUE:"fixture"}}]}));
    const checkout=await runtime.getDurableObjectNamespace("CHECKOUT"),provider=await runtime.getDurableObjectNamespace("PROVIDER");
    const c=checkout.get(checkout.idFromName("owner")),p=provider.get(provider.idFromName("owner"));
    async function invoke(stub,payload){const r=await stub.fetch("https://internal/",{method:"POST",body:JSON.stringify(payload)});const data=await r.json();assert.equal(data.ok,true,data.error);return data.value;}
    for(let i=0;i<100;i++){
      const key="fixture-"+i,runId=i<5?"r":"r-child";
      await invoke(c,{action:"create",key,runId,amount:1250,fault:"none",account:"owner"});
      await invoke(p,{action:"charge",key,runId,amount:1250});
    }
    const read=async scope=>{const local=await invoke(c,{action:"state",scope}),remote=await invoke(p,{action:"state",scope});return {local,remote,rows:local.rowsRead+remote.rowsRead};};
    const full=await read({type:"full"}),run=await read({type:"run",runId:"r"}),key=await read({type:"key",key:"fixture-0"});
    assert.equal(full.local.orders.length,100);assert.equal(run.local.orders.length,5);assert.equal(run.remote.charges.length,5);
    assert.equal(key.local.outbox.length,1);assert.equal(key.remote.charges.length,1);
    assert.ok(key.rows>0&&key.rows<15);assert.ok(run.rows<full.rows/5);
    await invoke(c,{action:"create",key:"extra",runId:"other",amount:1250,fault:"none",account:"owner"});
    await invoke(p,{action:"charge",key:"extra",runId:"other",amount:1250});
    assert.equal((await read({type:"key",key:"fixture-0"})).rows,key.rows);
    assert.equal((await read({type:"run",runId:"r"})).rows,run.rows);
    assert.equal((await read({type:"key",key:"absent"})).local.orders.length,0);
  }finally{if(runtime)await runtime.dispose();rmSync(dir,{recursive:true});}
});
