// Independent SQLite-backed Durable Object: mock external payment provider.
// No real payment API, credentials, or cross-DO ACID transaction.
export class ProviderState{
  constructor(ctx){
    this.ctx=ctx;this.sql=ctx.storage.sql;
    this.sql.exec("CREATE TABLE IF NOT EXISTS charges(key TEXT PRIMARY KEY,amount INTEGER NOT NULL,currency TEXT NOT NULL,charge_id TEXT NOT NULL UNIQUE)");
  }
  rows(s,...p){return this.sql.exec(s,...p).toArray();}
  async fetch(request){
    try{
      const q=await request.json();let value;
      if(q.action==="charge"){
        value=this.ctx.storage.transactionSync(()=>{
          const old=this.rows("SELECT * FROM charges WHERE key=?",q.key)[0];
          if(old){if(old.amount!==q.amount)throw new Error("Provider key conflict");return old;}
          const id=crypto.randomUUID();
          this.sql.exec("INSERT INTO charges VALUES(?,?,'USD',?)",q.key,q.amount,id);
          return {key:q.key,amount:q.amount,currency:"USD",charge_id:id};
        });
      }else if(q.action==="lookup"){
        value=this.rows("SELECT * FROM charges WHERE key=?",q.key)[0]||null;
      }else if(q.action==="state"){
        value=this.rows("SELECT * FROM charges ORDER BY key");
      }else if(q.action==="bookmark"){
        value=await this.ctx.storage.getCurrentBookmark().catch(()=>null);
      }else throw new Error("Invalid internal provider action");
      return Response.json({ok:true,value});
    }catch(e){return Response.json({ok:false,error:e.message},{status:400});}
  }
}
