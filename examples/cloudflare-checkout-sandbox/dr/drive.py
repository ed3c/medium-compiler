"""One-shot operator drive through loopback -> remote service -> native DOs."""
import json,time,urllib.request,urllib.error,sys
from pathlib import Path
if len(sys.argv)!=2: raise SystemExit('Supply an evidence JSON path outside the repository')
output=Path(sys.argv[1])
if output.exists(): raise SystemExit('Evidence path exists; preserve prior run and read back instead')
trace=[]
def call(action,**payload):
    start=time.monotonic()
    request=urllib.request.Request('http://127.0.0.1:8877/',data=json.dumps({'action':action,**payload}).encode(),headers={'Content-Type':'application/json'},method='POST')
    try:
        with urllib.request.urlopen(request,timeout=30) as response: status=response.status;data=json.load(response)
    except urllib.error.HTTPError as error: status=error.code;data=json.load(error)
    trace.append({'action':action,'input':payload,'status':status,'at':time.time(),'ms':round((time.monotonic()-start)*1000,2),'response':data})
    output.write_text(json.dumps({'scope':'isolated native PITR; one checkout restored, provider retained','trace':trace},indent=2))
    if status!=200 or not data.get('ok'): raise RuntimeError(action+': '+str(data.get('error')))
    return data['value']
def assert_state(state,status,charges):
    assert len(state['orders'])==1 and state['orders'][0]['key']=='dr-one-payment'
    assert state['orders'][0]['amount']==1250 and state['orders'][0]['status']==status
    assert len(state['charges'])==charges
    if charges: assert state['charges'][0]['amount']==1250 and state['charges'][0]['currency']=='USD'
    assert state['outbox'][0]['delivered']==int(status=='PAID')
empty=call('state')
assert empty['orders']==[] and empty['charges']==[], 'Run ID already used; no blind replay'
call('create');before=call('state');assert_state(before,'PENDING',0)
cutoff=time.monotonic();bookmark=before['bookmarks']['checkout'];assert bookmark
call('provider-commit');unknown=call('state');assert_state(unknown,'PENDING',1)
call('reconcile');paid=call('state');assert_state(paid,'PAID',1)
charge_id=paid['charges'][0]['charge_id']
fault_at=time.monotonic();call('corrupt');corrupted=call('state');assert corrupted['orders'][0]['amount']==999
assert corrupted['charges'][0]['charge_id']==charge_id
cutoff_age_ms=(time.monotonic()-cutoff)*1000
call('prepare-restore',bookmark=bookmark)
try: call('restart')
except (RuntimeError,urllib.error.URLError) as error:
    trace.append({'action':'restart-observed-abort','error':str(error),'at':time.time()})
# Restart is issued once; uncertain outcome is resolved by readback, never retrying restore.
restored=call('state');assert_state(restored,'PENDING',1)
assert restored['charges'][0]['charge_id']==charge_id
call('reconcile');recovered=call('state');assert_state(recovered,'PAID',1)
assert recovered['charges'][0]['charge_id']==charge_id
rto_ms=(time.monotonic()-fault_at)*1000
result={'scope':'isolated native PITR; one checkout restored, provider retained','runId':recovered['runId'],'nativeVersion':recovered['version'],
        'rtoMs':round(rto_ms,2),'bookmarkCutoffAgeAtFaultReadbackMs':round(cutoff_age_ms,2),
        'lostCheckoutIntents':0,'providerEffectsReconciled':1,'trace':trace,
        'limits':'Single data-corruption drill, not regional outage or a joint cross-DO restore/RPO guarantee'}
output.write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k not in ['trace']}))
