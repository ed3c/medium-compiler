// One SQLite-backed Durable Object per authenticated Access user.
// Queue dispatch and provider effects are separate from this SQLite transaction.
export class CheckoutState{
  constructor(ctx,env){
    this.ctx=ctx;this.env=env;this.sql=ctx.storage.sql;
    this.sql.exec("CREATE TABLE IF NOT EXISTS orders(key TEXT PRIMARY KEY,amount INTEGER NOT NULL,status TEXT NOT NULL CHECK(status IN ('PENDING','PAID')),fault TEXT NOT NULL,account TEXT NOT NULL)");
    this.sql.exec("CREATE TABLE IF NOT EXISTS outbox(key TEXT PRIMARY KEY,delivered INTEGER NOT NULL DEFAULT 0,sends INTEGER NOT NULL DEFAULT 0)");
    this.sql.exec("CREATE TABLE IF NOT EXISTS faults(key TEXT PRIMARY KEY,injected INTEGER NOT NULL DEFAULT 0)");
  }
  rows(query,...params){return this.sql.exec(query,...params).toArray();}
  create({key,amount,fault,account}){
    const previous=this.rows("SELECT * FROM orders WHERE key=?",key)[0];
    if(previous){
      if(previous.amount!==amount)throw new Error("409: identical key, different amount");
      return {replay:true,...previous};
    }
    if(this.rows("SELECT COUNT(*) AS n FROM orders")[0].n>=30)throw new Error("Sandbox quota: 30 orders per Access user");
    return this.ctx.storage.transactionSync(()=>{
      this.sql.exec("INSERT INTO orders(key,amount,status,fault,account) VALUES(?,?,'PENDING',?,?)",key,amount,fault,account);
      this.sql.exec("INSERT INTO outbox(key,delivered,sends) VALUES(?,0,0)",key);
      this.sql.exec("INSERT INTO faults(key,injected) VALUES(?,0)",key);
      return {key,amount,status:"PENDING",fault,replay:false};
    });
  }
  snapshot(){
    return {orders:this.rows("SELECT key,amount,status,fault FROM orders ORDER BY key"),
      outbox:this.rows("SELECT key,delivered,sends FROM outbox ORDER BY key")};
  }
  paid({key,amount}){
    return this.ctx.storage.transactionSync(()=>{
      const order=this.rows("SELECT * FROM orders WHERE key=?",key)[0];
      if(!order||order.amount!==amount)throw new Error("Payment identity mismatch");
      this.sql.exec("UPDATE orders SET status='PAID' WHERE key=?",key);
      this.sql.exec("UPDATE outbox SET delivered=1 WHERE key=?",key);
      return {key,status:"PAID"};
    });
  }
  claimFault({key}){
    return this.ctx.storage.transactionSync(()=>{
      const row=this.rows("SELECT injected FROM faults WHERE key=?",key)[0];
      if(!row)throw new Error("Unknown fault marker");
      if(row.injected)return false;
      this.sql.exec("UPDATE faults SET injected=1 WHERE key=?",key);
      return true;
    });
  }
  async enqueue(){
    const pending=this.rows("SELECT o.key,o.amount,o.fault,o.account,x.sends FROM orders o JOIN outbox x ON o.key=x.key WHERE x.delivered=0 AND x.sends<3 ORDER BY o.key LIMIT 15");
    let dispatched=0;
    for(const row of pending){
      // Mark intent before sending: a lost publish result leaves readback/retry work.
      this.sql.exec("UPDATE outbox SET sends=sends+1 WHERE key=? AND delivered=0 AND sends<3",row.key);
      try{await this.env.PAYMENTS_QUEUE.send({account:row.account,key:row.key,amount:row.amount,fault:row.fault});dispatched++;}
      catch(_err){/* Alarm / authorized recovery will retry with the same payment key. */}
    }
    if(this.rows("SELECT COUNT(*) AS n FROM outbox WHERE delivered=0 AND sends<3")[0].n>0)
      await this.ctx.storage.setAlarm(Date.now()+30000);
    return {dispatched,pending:this.rows("SELECT COUNT(*) AS n FROM outbox WHERE delivered=0")[0].n};
  }
  async fetch(request){
    try{
      const q=await request.json();let value;
      switch(q.action){
        case "create": value=this.create(q);await this.ctx.storage.setAlarm(Date.now()+15000);break;
        case "state": value=this.snapshot();break;
        case "paid": value=this.paid(q);break;
        case "claimFault": value=this.claimFault(q);break;
        case "enqueue": value=await this.enqueue();break;
        case "replay":
          this.sql.exec("UPDATE outbox SET sends=0 WHERE delivered=0 AND sends>=3");
          value=await this.enqueue();break;
        default: throw new Error("Invalid internal action");
      }
      return Response.json({ok:true,value});
    }catch(err){return Response.json({ok:false,error:err.message},{status:400});}
  }
  async alarm(){await this.enqueue();}
}
