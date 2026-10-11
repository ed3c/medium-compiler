// One SQLite-backed Durable Object per authenticated Access user.
// Queue dispatch and provider effects are separate from this SQLite transaction.
export class CheckoutState{
  constructor(ctx,env){
    this.ctx=ctx;this.env=env;this.sql=ctx.storage.sql;
    this.sql.exec("CREATE TABLE IF NOT EXISTS orders(key TEXT PRIMARY KEY,amount INTEGER NOT NULL,status TEXT NOT NULL CHECK(status IN ('PENDING','PAID')),fault TEXT NOT NULL,account TEXT NOT NULL)");
    this.sql.exec("CREATE TABLE IF NOT EXISTS outbox(key TEXT PRIMARY KEY,delivered INTEGER NOT NULL DEFAULT 0,sends INTEGER NOT NULL DEFAULT 0)");
    this.sql.exec("CREATE TABLE IF NOT EXISTS faults(key TEXT PRIMARY KEY,injected INTEGER NOT NULL DEFAULT 0)");
    if(!this.rows("PRAGMA table_info(outbox)").some(row=>row.name==="replays"))
      this.sql.exec("ALTER TABLE outbox ADD COLUMN replays INTEGER NOT NULL DEFAULT 0");
    this.sql.exec("CREATE TABLE IF NOT EXISTS usage(day TEXT PRIMARY KEY,orders INTEGER NOT NULL DEFAULT 0,dispatches INTEGER NOT NULL DEFAULT 0)");
    this.sql.exec("CREATE TABLE IF NOT EXISTS reservations(identity TEXT PRIMARY KEY,amount INTEGER NOT NULL)");
  }
  rows(query,...params){return this.sql.exec(query,...params).toArray();}
  async useBudget(payload){
    try{
      const budget=this.env.CHECKOUT.get(this.env.CHECKOUT.idFromName("sandbox-account-budget"));
      const response=await budget.fetch("https://internal/budget",{method:"POST",body:JSON.stringify(payload)});
      const result=await response.json();
      if(!result.ok)throw Error(result.error||"503: Account usage guard unavailable");
      return result.value;
    }catch(error){
      if(/^(409|429|503):/.test(error.message))throw error;
      throw Error("503: Account usage guard unavailable: "+error.message);
    }
  }
  usage(){
    const day=new Date().toISOString().slice(0,10);
    return {day,...(this.rows("SELECT orders,dispatches FROM usage WHERE day=?",day)[0]||{orders:0,dispatches:0}),
      limits:{orders:20,dispatches:50},scope:"Sandbox-wide across Access users; conservative reservations, not Cloudflare billing usage"};
  }
  reserve({kind,identity,amount}){
    return this.ctx.storage.transactionSync(()=>{
      if(kind==="order"){
        const previous=this.rows("SELECT amount FROM reservations WHERE identity=?",identity)[0];
        if(previous){if(previous.amount!==amount)throw Error("409: reservation amount conflict");return {reserved:true,replay:true};}
      }else if(kind!=="dispatch")throw Error("Invalid usage reservation");
      const day=new Date().toISOString().slice(0,10),column=kind==="order"?"orders":"dispatches",limit=kind==="order"?20:50;
      this.sql.exec("INSERT OR IGNORE INTO usage(day) VALUES(?)",day);
      if(this.rows("SELECT "+column+" AS n FROM usage WHERE day=?",day)[0].n>=limit)
        throw Error("429: Daily account "+kind+" budget exhausted");
      this.sql.exec("UPDATE usage SET "+column+"="+column+"+1 WHERE day=?",day);
      if(kind==="order")this.sql.exec("INSERT INTO reservations(identity,amount) VALUES(?,?)",identity,amount);
      return {reserved:true};
    });
  }
  async admit(q){
    if(!this.rows("SELECT key FROM orders WHERE key=?",q.key)[0])
      await this.useBudget({action:"reserve",kind:"order",identity:JSON.stringify([q.account,q.key]),amount:q.amount});
    return this.create(q);
  }
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
      outbox:this.rows("SELECT key,delivered,sends,replays FROM outbox ORDER BY key")};
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
  async enqueue(keys=null){
    const pending=this.rows("SELECT o.key,o.amount,o.fault,o.account,x.sends FROM orders o JOIN outbox x ON o.key=x.key WHERE x.delivered=0 AND x.sends<3 ORDER BY o.key LIMIT 15");
    let dispatched=0;
    for(const row of pending){
      if(keys&&!keys.includes(row.key))continue;
      try{await this.useBudget({action:"reserve",kind:"dispatch"});}
      catch(err){console.warn(JSON.stringify({phase:"dispatch-budget",error:err.message}));break;}
      // Mark intent before sending: a lost publish result leaves readback/retry work.
      if(!this.rows("UPDATE outbox SET sends=sends+1 WHERE key=? AND delivered=0 AND sends<3 RETURNING sends",row.key).length)continue;
      try{await this.env.PAYMENTS_QUEUE.send({account:row.account,key:row.key,amount:row.amount,fault:row.fault});dispatched++;}
      catch(err){console.warn(JSON.stringify({phase:"queue-publish",error:err.message}));}
    }
    const budget=await this.useBudget({action:"usage"});
    if(budget.dispatches<budget.limits.dispatches&&this.rows("SELECT COUNT(*) AS n FROM outbox WHERE delivered=0 AND sends<3")[0].n>0)
      await this.ctx.storage.setAlarm(Date.now()+30000);
    return {dispatched,pending:this.rows("SELECT COUNT(*) AS n FROM outbox WHERE delivered=0")[0].n};
  }
  async fetch(request){
    try{
      const q=await request.json();let value;
      switch(q.action){
        case "create": value=await this.admit(q);await this.ctx.storage.setAlarm(Date.now()+15000);break;
        case "reserve": value=this.reserve(q);break;
        case "usage": value=this.usage();break;
        case "state": value=this.snapshot();break;
        case "bookmark": value=await this.ctx.storage.getCurrentBookmark().catch(()=>null);break;
        case "paid": value=this.paid(q);break;
        case "claimFault": value=this.claimFault(q);break;
        case "enqueue": value=await this.enqueue();break;
        case "replay":
          {
            const keys=this.rows("SELECT key FROM outbox WHERE delivered=0 AND replays<2 ORDER BY key LIMIT 15").map(row=>row.key);
            this.ctx.storage.transactionSync(()=>{
              for(const key of keys)this.sql.exec("UPDATE outbox SET sends=0,replays=replays+1 WHERE key=?",key);
            });
            value=await this.enqueue(keys);break;
          }
        default: throw new Error("Invalid internal action");
      }
      return Response.json({ok:true,value});
    }catch(err){return Response.json({ok:false,error:err.message},{status:400});}
  }
  async alarm(){await this.enqueue();}
}
