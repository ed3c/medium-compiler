// Independent SQLite-backed Durable Object: mock external payment provider.
// No real payment API, credentials, or cross-DO ACID transaction.
import {scopeQuery,readRows} from "./readback.mjs";
export class ProviderState{
  constructor(ctx){
    this.ctx=ctx;this.sql=ctx.storage.sql;
    this.sql.exec("CREATE TABLE IF NOT EXISTS charges(key TEXT PRIMARY KEY,amount INTEGER NOT NULL,currency TEXT NOT NULL,charge_id TEXT NOT NULL UNIQUE)");
    if(!this.rows("PRAGMA table_info(charges)").some(row=>row.name==="run_id"))
      this.sql.exec("ALTER TABLE charges ADD COLUMN run_id TEXT");
    this.sql.exec("CREATE INDEX IF NOT EXISTS charges_run_id ON charges(run_id)");
  }
  rows(s,...p){return this.sql.exec(s,...p).toArray();}
  async fetch(request){
    try{
      const q=await request.json();let value;
      if(q.action==="charge"){
        value=this.ctx.storage.transactionSync(()=>{
          const old=this.rows("SELECT * FROM charges WHERE key=?",q.key)[0];
          if(old){if(old.amount!==q.amount||(q.runId!=null&&old.run_id!==q.runId))throw new Error("Provider key conflict");return old;}
          const id=crypto.randomUUID();
          this.sql.exec("INSERT INTO charges(key,amount,currency,charge_id,run_id) VALUES(?,?,'USD',?,?)",q.key,q.amount,id,q.runId??null);
          return {key:q.key,amount:q.amount,currency:"USD",charge_id:id,run_id:q.runId??null};
        });
      }else if(q.action==="lookup"){
        value=this.rows("SELECT * FROM charges WHERE key=?",q.key)[0]||null;
      }else if(q.action==="state"){
        if(q.scope){
          const {where,bindings}=scopeQuery(q.scope);
          const read=readRows(this.sql,"SELECT * FROM charges"+where+" ORDER BY key",bindings);
          value={charges:read.rows,rowsRead:read.rowsRead};
        }else value=this.rows("SELECT * FROM charges ORDER BY key");
      }else if(q.action==="bookmark"){
        value=await this.ctx.storage.getCurrentBookmark().catch(()=>null);
      }else throw new Error("Invalid internal provider action");
      return Response.json({ok:true,value});
    }catch(e){return Response.json({ok:false,error:e.message},{status:400});}
  }
}
