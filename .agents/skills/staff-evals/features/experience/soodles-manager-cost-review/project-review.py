from pathlib import Path
import json,hashlib,time,datetime,copy,sys
sys.path.insert(0,'/workspace/scratch/7ed56a5a2a33/soodles-work')
import cost_telemetry as cost
import test_manager as tm
import schema_manager as sm
p=Path('/tmp/staff-evals-manager-review-20261004');h=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
def save(name,x):(p/name).write_text(json.dumps(x,indent=2)+'\n')
pred=json.loads((p/'prediction.json').read_text())
for ref in pred['input_refs']:assert h(Path(ref['path']))==ref['sha256']
subject={'repository':'ed3c/soodles','head':'75c453fe1e104f530a9800784eddb3f169951480','run_id':37185131471,'attempt':1,'scope':'standalone CI review; no atom authorization or current owner supplied'}
ref={'path':str(p/'verification-timing.log'),'sha256':h(p/'verification-timing.log')};started=datetime.datetime.now(datetime.timezone.utc).isoformat();ts=time.perf_counter()
observations=cost.timing_log((p/'verification-timing.log').read_bytes(),ref,subject,head=subject['head'],attempt=1);parse_ms=(time.perf_counter()-ts)*1000
# Existing project calls Test Manager.review_cost, then Schema Manager.project_cost.
ts=time.perf_counter();projection=cost.project(subject,observations);project_ms=(time.perf_counter()-ts)*1000
feedback=sm.project_owner_feedback({'cost':projection})
save('observations.json',observations);save('schema-cost-feedback.json',projection);save('owner-feedback.json',feedback)
facts={k:projection[k] for k in ('subject','coverage','summary','sources')}
# Synthetic data-only controls, not additional test executions or real cost claims.
large=copy.deepcopy(facts)
for phase in large['summary']['phase_costs']:
 if phase['inclusive_seconds'] is not None:phase['inclusive_seconds']*=100
large_review=tm.review_cost(large)
repeat=copy.deepcopy(facts);phase=next(x for x in repeat['summary']['phase_costs'] if x['phase']=='test.module');phase['observations']=phase['measured_spans']=2;phase['statuses']={'passed':2}
repeat_review=tm.review_cost(repeat)
save('synthetic-controls.json',{'scope':'Synthetic boundary data, not measured cost','duration_only':large_review,'repeat':repeat_review})
actual={'normal_review':projection['schema_projection']['review']['status'],'normal_test_demand':projection['schema_projection']['test_demand'],'normal_effects':projection['schema_projection']['effects'],'unmeasured_end_to_end_wall':projection['summary']['observed_wall_seconds'] is None,'missing_owner_transition':feedback['dag']['owner_transition']['status'],'synthetic_duration_only_review':large_review['status'],'synthetic_repeat_review':repeat_review['status'],'synthetic_repeat_test_demand':repeat_review['test_demand']}
save('outcome.json',{'prediction_sha256':h(p/'prediction.json'),'started_at':started,'actual':actual,'resolution':'confirmed' if actual==pred['predicted_observable'] else 'contradicted','timing_ms':{'parse_and_normalize':parse_ms,'aggregate_and_test_manager_schema_cost':project_ms,'owner_feedback_projection':feedback['elapsed_ms']},'effects':[],'tests_executed':0,'limits':'Single in-process observation. Excludes model, provider, cold Python startup and file retrieval. Known historical input; no calibrated future-agent prediction.'})
save('owner-consumption.json',{'consumer':'/root review coordinator','feedback_file_sha256':h(p/'schema-cost-feedback.json'),'observed_review_status':actual['normal_review'],'action':'Retain measured costs, unknowns and investigation targets. Do not invoke repair or repeat CI from duration alone. Actual atom owner must supply current readback for lifecycle continuation.','live_owner_feedback_complete':False,'missing':'Original atom authorization/checkpoint/current typed owner result not supplied. No substitute authority created.'})
print(json.dumps({'actual':actual,'matches_forecast':actual==pred['predicted_observable'],'timing_ms':json.loads((p/'outcome.json').read_text())['timing_ms'],'modules':len(projection['summary']['verification_modules']),'worker_seconds':projection['summary']['parallel_worker_seconds'],'unknowns':len(projection['schema_projection']['review']['unknowns'])},indent=2))
