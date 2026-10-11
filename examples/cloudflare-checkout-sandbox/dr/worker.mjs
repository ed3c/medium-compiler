// Operator drill only: distinct namespaces, one payment, no public hostname.
import {CheckoutState} from '../src/checkout.mjs';
import {ProviderState} from '../src/provider.mjs';
const key='dr-one-payment',amount=1250;
export class DrillCheckout extends CheckoutState{
  async fetch(request){
    const q=await request.clone().json();
    if(q.action==='dr-create'){
      if(this.snapshot().orders.length)throw Error('Drill already contains an intent; read back, do not rerun');
      return Response.json({ok:true,value:this.create({key,amount,account:'isolated-dr',fault:'none'})});
    }
    if(q.action==='dr-corrupt'){
      if(this.snapshot().orders.length!==1)throw Error('Drill requires its one saved intent');
      this.ctx.storage.transactionSync(()=>{
        this.sql.exec("UPDATE orders SET amount=999,status='PENDING' WHERE key=?",key);
        this.sql.exec('UPDATE outbox SET delivered=0 WHERE key=?',key);
      });
      return Response.json({ok:true,value:this.snapshot()});
    }
    if(q.action==='dr-prepare'){
      if(typeof q.bookmark!=='string'||!/^[0-9a-f-]{20,100}$/.test(q.bookmark))throw Error('Invalid native bookmark');
      const undo=await this.ctx.storage.onNextSessionRestoreBookmark(q.bookmark);
      return Response.json({ok:true,value:{undo}});
    }
    if(q.action==='dr-restart'){this.ctx.abort('Operator-authorized isolated PITR restart');}
    return super.fetch(request);
  }
}
export class DrillProvider extends ProviderState{}
async function invoke(stub,body){
  const response=await stub.fetch('https://internal/dr',{method:'POST',body:JSON.stringify(body)});
  const data=await response.json();if(!data.ok)throw Error(data.error||'Drill DO refused');return data.value;
}
export default{
  async fetch(request,env){
    try{
      if(request.method!=='POST')return new Response('Operator POST only',{status:405});
      const raw=await request.text();if(raw.length>2048)throw Error('Bounded drill payload only');
      const q=JSON.parse(raw);
      if(!/^dr-[a-zA-Z0-9-]{1,36}$/.test(env.DR_RUN_ID))throw Error('Missing fixed isolated run ID');
      const checkout=env.CHECKOUT.get(env.CHECKOUT.idFromName(env.DR_RUN_ID));
      const provider=env.PROVIDER.get(env.PROVIDER.idFromName(env.DR_RUN_ID));
      let value;
      switch(q.action){
        case 'create':value=await invoke(checkout,{action:'dr-create'});break;
        case 'state':{
          const [local,charges,checkoutBookmark,providerBookmark]=await Promise.all([
            invoke(checkout,{action:'state'}),invoke(provider,{action:'state'}),
            invoke(checkout,{action:'bookmark'}),invoke(provider,{action:'bookmark'})]);
          value={runId:env.DR_RUN_ID,version:env.DR_VERSION?.id||null,...local,charges,bookmarks:{checkout:checkoutBookmark,provider:providerBookmark}};break;
        }
        case 'provider-commit':value=await invoke(provider,{action:'charge',key,amount});break;
        case 'reconcile':{
          const evidence=await invoke(provider,{action:'lookup',key});
          if(!evidence||evidence.amount!==amount||evidence.currency!=='USD')throw Error('No matching provider effect');
          value=await invoke(checkout,{action:'paid',key,amount});break;
        }
        case 'corrupt':value=await invoke(checkout,{action:'dr-corrupt'});break;
        case 'prepare-restore':value=await invoke(checkout,{action:'dr-prepare',bookmark:q.bookmark});break;
        case 'restart':value=await invoke(checkout,{action:'dr-restart'});break;
        default:return Response.json({error:'Unknown drill action'},{status:400});
      }
      return Response.json({ok:true,value});
    }catch(error){return Response.json({ok:false,error:error.message},{status:503});}
  }
};
