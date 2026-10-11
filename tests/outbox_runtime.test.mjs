// Actual local workerd SQL costs; no Cloudflare account usage or remote effects.
import {test} from "node:test";
import assert from "node:assert/strict";
import {build} from "esbuild";
import {Miniflare,convertV4MiniflareOptions} from "miniflare";

test("outbox reads depend on active work, not 100/1000/10000 delivered history rows",async()=>{
  const bundle=await build({stdin:{contents:`
    import {CheckoutState} from "./examples/cloudflare-checkout-sandbox/src/checkout.mjs";
    export class MeasuredCheckout extends CheckoutState{
      rows(query,...bindings){
        const cursor=this.sql.exec(query,...bindings),rows=cursor.toArray();
        this.measured?.push({query,bindings,rowsRead:cursor.rowsRead,rowsWritten:cursor.rowsWritten});
        return rows;
      }
      async fetch(request){
        const q=await request.json();
        if(q.action==="fixture"){
          this.sql.exec("WITH RECURSIVE n(i) AS (SELECT 1 UNION ALL SELECT i+1 FROM n WHERE i<?) INSERT INTO orders(key,amount,status,fault,account) SELECT 'history-'||i,1250,'PAID','none','owner' FROM n",q.history);
          this.sql.exec("INSERT INTO outbox(key,delivered,sends,published) SELECT key,1,1,1 FROM orders");
          if(q.active){
            for(const [key,published,sends,at] of [["due",0,0,0],["future",0,0,Date.now()+3600000],["published",1,1,0],["exhausted",0,3,0]]){
              this.create({key,amount:1250,fault:"none",account:"owner"});
              this.sql.exec("UPDATE outbox SET published=?,sends=?,next_attempt_at=? WHERE key=?",published,sends,at,key);
            }
          }
          return Response.json({fixtureRows:this.rows("SELECT COUNT(*) AS n FROM outbox")[0].n});
        }
        if(q.action==="pending-fixture"){
          for(let i=0;i<q.pending;i++){
            const key="pending-"+i;
            this.create({key,amount:1250,fault:"none",account:"owner"});
            this.sql.exec("UPDATE outbox SET published=1 WHERE key=?",key);
          }
          return Response.json({pending:this.pendingCount()});
        }
        this.measured=[];
        const value=await this.enqueue(q.keys??null);
        const queries=this.measured;
        const plans=queries.filter(row=>row.query.startsWith("SELECT")).map(row=>({query:row.query,plan:this.sql.exec("EXPLAIN QUERY PLAN "+row.query,...row.bindings).toArray()}));
        return Response.json({value,queries,plans});
      }
    }
    export default {fetch(){return new Response("Local fixture only");}};
  `,resolveDir:process.cwd(),sourcefile:"outbox-cost-fixture.mjs"},bundle:true,write:false,format:"esm",platform:"neutral"});
  const runtime=new Miniflare(convertV4MiniflareOptions({workers:[{name:"outbox-cost-test",modules:true,script:bundle.outputFiles[0].text,compatibilityDate:"2026-10-11",
    durableObjects:{CHECKOUT:{className:"MeasuredCheckout",useSQLite:true}},queueProducers:{PAYMENTS_QUEUE:"local-fixture"}}]}));
  try{
    const ns=await runtime.getDurableObjectNamespace("CHECKOUT");
    async function call(stub,input){const r=await stub.fetch("https://fixture/",{method:"POST",body:JSON.stringify(input)});assert.equal(r.status,200);return r.json();}
    let first,firstIdle;
    for(const history of [100,1000,10000]){
      const empty=ns.get(ns.idFromName("empty-"+history));
      assert.equal((await call(empty,{action:"fixture",history})).fixtureRows,history);
      const idle=await call(empty,{action:"measure"});
      assert.deepEqual(idle.value,{dispatched:0,pending:0});
      const idleReads=idle.queries.reduce((n,q)=>n+q.rowsRead,0);
      assert.ok(idleReads<=3,JSON.stringify(idle));
      if(firstIdle!==undefined)assert.equal(idleReads,firstIdle);else firstIdle=idleReads;
      const active=ns.get(ns.idFromName("active-"+history));
      assert.equal((await call(active,{action:"fixture",history,active:true})).fixtureRows,history+4);
      const result=await call(active,{action:"measure"});
      assert.deepEqual(result.value,{dispatched:1,pending:4});
      const select=result.queries.filter(q=>q.query.startsWith("SELECT"));
      assert.ok(select.every(q=>q.rowsRead<20),JSON.stringify(result));
      assert.ok(result.plans.some(q=>JSON.stringify(q.plan).includes("outbox_retry_due")),JSON.stringify(result.plans));
      assert.equal(select.find(q=>q.query.includes("FROM outbox_totals")).rowsRead,1);
      const costs=result.queries.map(({query,rowsRead,rowsWritten})=>({query,rowsRead,rowsWritten}));
      if(first)assert.deepEqual(costs,first);else first=costs;
      const again=await call(active,{action:"measure"});
      assert.deepEqual(again.value,{dispatched:0,pending:4});
      console.log(JSON.stringify({history,emptyRowsRead:idleReads,activeQueries:costs,plans:result.plans}));
    }
    for(const pending of [1,100,10000]){
      const stub=ns.get(ns.idFromName("pending-"+pending));
      assert.deepEqual(await call(stub,{action:"pending-fixture",pending}),{pending});
      const result=await call(stub,{action:"measure",keys:[]});
      assert.deepEqual(result.value,{dispatched:0,pending});
      assert.equal(result.queries.length,1);
      assert.equal(result.queries[0].rowsRead,1);
      console.log(JSON.stringify({pending,queries:result.queries}));
    }
  }finally{await runtime.dispose();}
});
