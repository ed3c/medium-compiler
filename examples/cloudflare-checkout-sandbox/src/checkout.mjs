// One SQLite-backed Durable Object per authenticated Access user.
// Queue dispatch and provider effects are separate from this SQLite transaction.
import {scopeQuery,readRows} from "./readback.mjs";
export class CheckoutState{
  constructor(ctx,env){
    this.ctx=ctx;this.env=env;this.sql=ctx.storage.sql;
    this.sql.exec("CREATE TABLE IF NOT EXISTS orders(key TEXT PRIMARY KEY,amount INTEGER NOT NULL,status TEXT NOT NULL CHECK(status IN ('PENDING','PAID')),fault TEXT NOT NULL,account TEXT NOT NULL)");
    this.sql.exec("CREATE TABLE IF NOT EXISTS outbox(key TEXT PRIMARY KEY,delivered INTEGER NOT NULL DEFAULT 0,sends INTEGER NOT NULL DEFAULT 0)");
    this.sql.exec("CREATE TABLE IF NOT EXISTS faults(key TEXT PRIMARY KEY,injected INTEGER NOT NULL DEFAULT 0)");
    if(!this.rows("PRAGMA table_info(orders)").some(row=>row.name==="run_id"))
      this.sql.exec("ALTER TABLE orders ADD COLUMN run_id TEXT");
    this.sql.exec("CREATE INDEX IF NOT EXISTS orders_run_id ON orders(run_id)");
    if(!this.rows("PRAGMA table_info(outbox)").some(row=>row.name==="replays"))
      this.sql.exec("ALTER TABLE outbox ADD COLUMN replays INTEGER NOT NULL DEFAULT 0");
    if(!this.rows("PRAGMA table_info(outbox)").some(row=>row.name==="published"))
      this.sql.exec("ALTER TABLE outbox ADD COLUMN published INTEGER NOT NULL DEFAULT 0");
    if(!this.rows("PRAGMA table_info(outbox)").some(row=>row.name==="next_attempt_at"))
      this.sql.exec("ALTER TABLE outbox ADD COLUMN next_attempt_at INTEGER NOT NULL DEFAULT 0");
    this.sql.exec("CREATE INDEX IF NOT EXISTS outbox_pending ON outbox(key) WHERE delivered=0");
    this.sql.exec("CREATE INDEX IF NOT EXISTS outbox_retry_due ON outbox(next_attempt_at,key) WHERE delivered=0 AND published=0 AND sends<3");
    this.sql.exec("CREATE TABLE IF NOT EXISTS outbox_totals(id INTEGER PRIMARY KEY CHECK(id=1),pending INTEGER NOT NULL CHECK(pending>=0))");
    // Bootstrap an existing ledger once. Synchronous SQL cannot yield to a
    // request; later creates and deliveries update this row in their transaction.
    this.ctx.storage.transactionSync(()=>{
      if(!this.rows("SELECT pending FROM outbox_totals WHERE id=1").length)
        this.sql.exec("INSERT INTO outbox_totals(id,pending) SELECT 1,COUNT(*) FROM outbox WHERE delivered=0");
    });
  }
  rows(query,...params){return this.sql.exec(query,...params).toArray();}
  pendingCount(){
    const row=this.rows("SELECT pending FROM outbox_totals WHERE id=1")[0];
    if(!row)throw new Error("Outbox pending total unavailable");
    return row.pending;
  }
  changePending(delta){
    if(!this.rows("UPDATE outbox_totals SET pending=pending+? WHERE id=1 RETURNING pending",delta).length)
      throw new Error("Outbox pending total unavailable");
  }
  create({key,amount,fault,account,runId=null}){
    const previous=this.rows("SELECT * FROM orders WHERE key=?",key)[0];
    if(previous){
      if(previous.amount!==amount)throw new Error("409: identical key, different amount");
      if(runId!==null&&previous.run_id!==runId)throw new Error("409: identical key, different Run ID");
      return {replay:true,...previous};
    }
    return this.ctx.storage.transactionSync(()=>{
      this.sql.exec("INSERT INTO orders(key,amount,status,fault,account,run_id) VALUES(?,?,'PENDING',?,?,?)",key,amount,fault,account,runId);
      this.sql.exec("INSERT INTO outbox(key,delivered,sends) VALUES(?,0,0)",key);
      this.changePending(1);
      this.sql.exec("INSERT INTO faults(key,injected) VALUES(?,0)",key);
      return {key,amount,status:"PENDING",fault,run_id:runId,replay:false};
    });
  }
  snapshot(){
    return {orders:this.rows("SELECT key,amount,status,fault FROM orders ORDER BY key"),
      outbox:this.rows("SELECT key,delivered,sends,replays,published,next_attempt_at FROM outbox ORDER BY key")};
  }
  readState(scope){
    const {where,bindings}=scopeQuery(scope);
    const orders=readRows(this.sql,"SELECT key,amount,status,fault,run_id FROM orders"+where+" ORDER BY key",bindings);
    const outboxScope=scopeQuery(scope,true);
    const outbox=readRows(this.sql,"SELECT key,delivered,sends,replays,published,next_attempt_at FROM outbox"+outboxScope.where+" ORDER BY key",outboxScope.bindings);
    return {orders:orders.rows,outbox:outbox.rows,
      rowsRead:orders.rowsRead===null||outbox.rowsRead===null?null:orders.rowsRead+outbox.rowsRead};
  }
  paid({key,amount}){
    return this.ctx.storage.transactionSync(()=>{
      const order=this.rows("SELECT * FROM orders WHERE key=?",key)[0];
      if(!order||order.amount!==amount)throw new Error("Payment identity mismatch");
      this.sql.exec("UPDATE orders SET status='PAID' WHERE key=?",key);
      if(this.rows("UPDATE outbox SET delivered=1 WHERE key=? AND delivered=0 RETURNING key",key).length)
        this.changePending(-1);
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
  async readback(row){
    const provider=this.env.PROVIDER.get(this.env.PROVIDER.idFromName("access-user:"+row.account));
    const response=await provider.fetch("https://internal/lookup",{method:"POST",body:JSON.stringify({action:"lookup",key:row.key})});
    const evidence=await response.json();
    if(!response.ok||!evidence.ok)throw new Error(evidence.error||"Provider readback unavailable");
    if(!evidence.value)return false;
    if(evidence.value.key!==row.key||evidence.value.amount!==row.amount||evidence.value.currency!=="USD")
      throw new Error("Provider evidence mismatch");
    this.paid(row);return true;
  }
  async enqueue(keys=null){
    if(keys&&!keys.length)return {dispatched:0,pending:this.pendingCount()};
    const scope=keys?" AND o.key IN ("+keys.map(()=>"?").join(",")+")":"";
    const pending=this.rows("SELECT o.key,o.amount,o.fault,o.account,o.run_id,x.sends,x.replays FROM outbox x JOIN orders o ON o.key=x.key WHERE x.delivered=0 AND x.published=0 AND x.sends<3 AND x.next_attempt_at<=?"+scope+" ORDER BY x.next_attempt_at,x.key LIMIT 15",Date.now(),...(keys||[]));
    let dispatched=0;
    for(const row of pending){
      // Durable claim excludes concurrent relays while send awaits. Replays is
      // the recovery epoch, so a late completion cannot overwrite a new claim.
      const claim=this.rows("UPDATE outbox SET sends=sends+1,next_attempt_at=? WHERE key=? AND delivered=0 AND published=0 AND sends=? AND replays=? AND sends<3 AND next_attempt_at<=? RETURNING sends,replays",Date.now()+30000,row.key,row.sends,row.replays,Date.now())[0];
      if(!claim)continue;
      // A recovery wake-up is required even on the last bounded attempt.
      // Propagate storage failure so the platform retries the alarm turn.
      await this.ctx.storage.setAlarm(Date.now()+30000);
      try{
        // An earlier publish may have committed despite its missing reply.
        if(row.sends>0&&await this.readback(row))continue;
        if(!this.rows("SELECT key FROM outbox WHERE key=? AND delivered=0 AND published=0 AND sends=? AND replays=? AND next_attempt_at>?",row.key,claim.sends,claim.replays,Date.now()).length)continue;
        await this.env.PAYMENTS_QUEUE.send({account:row.account,key:row.key,amount:row.amount,fault:row.fault,runId:row.run_id});
        this.sql.exec("UPDATE outbox SET published=1,next_attempt_at=0 WHERE key=? AND sends=? AND replays=?",row.key,claim.sends,claim.replays);
        dispatched++;
      }
      catch(err){console.warn(JSON.stringify({phase:"queue-publish",error:err.message}));}
    }
    const next=this.rows("SELECT next_attempt_at AS at FROM outbox WHERE delivered=0 AND published=0 AND sends<3 ORDER BY next_attempt_at,key LIMIT 1")[0]?.at;
    if(next!==undefined)await this.ctx.storage.setAlarm(Math.max(Date.now()+1000,next));
    return {dispatched,pending:this.pendingCount()};
  }
  async fetch(request){
    try{
      const q=await request.json();let value;
      switch(q.action){
        case "create":
          // Persist the wake-up before the atomic intent; a crash between
          // commit and the API's relay still leaves an alarm to resume it.
          if(!this.rows("SELECT key FROM orders WHERE key=?",q.key).length)await this.ctx.storage.setAlarm(Date.now()+15000);
          value=this.create(q);break;
        case "state": value=q.scope?this.readState(q.scope):this.snapshot();break;
        case "bookmark": value=await this.ctx.storage.getCurrentBookmark().catch(()=>null);break;
        case "paid": value=this.paid(q);break;
        case "claimFault": value=this.claimFault(q);break;
        case "enqueue": value=await this.enqueue(q.keys||null);break;
        case "replay":
          {
            const pending=this.rows("SELECT o.key,o.amount,o.account,x.sends,x.replays,x.published FROM outbox x JOIN orders o ON o.key=x.key WHERE x.delivered=0 AND x.next_attempt_at<=? ORDER BY x.key LIMIT 15",Date.now());
            const recoverable=[];
            for(const row of pending){
              if(await this.readback(row))continue;
              // Provider absence while delivery is paused does not undo a
              // trusted Queue acknowledgement. Resume delivery, do not republish.
              if(row.published)continue;
              recoverable.push(row);
            }
            // Validate the batch before resetting any published marker. A
            // failed later readback must not leave an earlier intent unarmed.
            if(recoverable.length)await this.ctx.storage.setAlarm(Date.now()+15000);
            const keys=[];
            for(const row of recoverable){
              if(this.rows("UPDATE outbox SET sends=0,published=0,next_attempt_at=0,replays=replays+1 WHERE key=? AND delivered=0 AND sends=? AND replays=? AND next_attempt_at<=? RETURNING key",row.key,row.sends,row.replays,Date.now()).length)keys.push(row.key);
            }
            value=await this.enqueue(keys);break;
          }
        default: throw new Error("Invalid internal action");
      }
      return Response.json({ok:true,value});
    }catch(err){return Response.json({ok:false,error:err.message},{status:400});}
  }
  async alarm(){await this.enqueue();}
}
