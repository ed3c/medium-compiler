"""All transport/reviewer records here are SYNTHETIC TESTS, never writer A/B evidence."""
import copy
from datetime import datetime,timezone,timedelta
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import run_writer_pair as runner
import evaluate_writer_run as observer

FAKE=ROOT/'tests/fixtures/fake_codex_exec.py'

def put(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')

def read(path):return json.loads(path.read_text())

class WriterObserverTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name).resolve()
        self.ws=self.root/'workspace';self.ws.mkdir();(self.ws/'inputs').mkdir()
        (self.ws/'inputs/article.md').write_text('SYNTHETIC ARTICLE\n')
        (self.ws/'work').mkdir()
        self.cap=self.root/'capture'
        self.meta={'requested_model':'synthetic-fixture','execution_kind':'synthetic_control','packet_sha256':'sha256:fixture',
            'job_id':'run-01','arm':'baseline','phase':'comparison','codex_sha256':observer.sha(FAKE.read_bytes()),
            'codex_version':'synthetic','host_approval_sha256':'sha256:fixture'}
    def capture(self,mode='good',timeout=3):
        if mode!='good':(self.ws/'fixture-mode.txt').write_text(mode)
        return runner.capture(FAKE,self.ws,self.cap,b'SYNTHETIC INPUT',self.meta,timeout)
    def review(self,result,flag=None):
        _,rows=observer.inspect_capture(self.cap,result['run_sha256'])
        labels=[]
        for i,r in enumerate(rows):
            labels.append({'line':r['line'],'quote':'SYNTHETIC','reason':'Synthetic test label, not a human evaluation.',
                'barriers':{k:bool(i==0 and k==flag) for k in observer.BARRIERS}})
        path=self.root/'external-review.json'
        put(path,{'schema_version':'writer-route-review@1','run_sha256':result['run_sha256'],
            'events_sha256':result['files']['events.jsonl'],'reviewer':'SYNTHETIC reviewer','independent':True,
            'instruction_read_observed':True,'source_fidelity':'PASS','task_outcome':'PASS','events':labels})
        return path
    def test_subprocess_captures_fixture_not_natural_writer(self):
        result=self.capture()
        observed=observer.evaluate(self.cap,result['run_sha256'])
        self.assertEqual(observed['evidence_validity'],'VALID_CAPTURE')
        self.assertEqual(observed['execution_kind'],'synthetic_control')
        self.assertIsNone(observed['behavior']);self.assertEqual(observed['review_status'],'PENDING')
    def test_failed_command_can_be_valid_capture_without_being_zero_barrier(self):
        result=self.capture();p=self.review(result,'premature_article_writing')
        report=observer.evaluate(self.cap,result['run_sha256'],p)
        self.assertEqual(report['behavior']['by_kind']['premature_article_writing'],1)
        self.assertEqual(report['snapshot_changes'],[])
    def test_pending_article_mutation_detected_independently_of_self_report(self):
        result=self.capture('mutate');report=observer.evaluate(self.cap,result['run_sha256'])
        self.assertIn('inputs/article.md',report['pending_article_effects'])
    def test_returned_output_is_not_used_as_self_reported_score(self):
        result=self.capture();report=observer.evaluate(self.cap,result['run_sha256'])
        self.assertIsNone(report['behavior']);self.assertFalse(report['authorizes_landing'])
    def test_no_secret_environment_forwarding(self):
        with patch.dict(os.environ,{'GH_TOKEN':'DO_NOT_FORWARD'}):result=self.capture()
        self.assertIn('GH_TOKEN=False',(self.cap/'events.jsonl').read_text())
        self.assertNotIn('DO_NOT_FORWARD',json.dumps(result))
    def test_argv_has_fresh_and_sandbox_flags_never_resume_or_bypass(self):
        result=self.capture();argv=result['argv']
        self.assertIn('--ephemeral',argv);self.assertIn('--json',argv);self.assertIn('workspace-write',argv)
        self.assertNotIn('resume',argv);self.assertNotIn('--ignore-rules',argv);self.assertNotIn('danger-full-access',argv)
    def test_corrupt_or_truncated_events_are_invalid_not_zero(self):
        for mode in ('truncated','missing-exit','unknown','empty-final'):
            with self.subTest(mode=mode):
                self.cap=self.root/('capture-'+mode)
                result=self.capture(mode);report=observer.evaluate(self.cap,result['run_sha256'])
                if mode=='empty-final':self.assertEqual(report['evidence_validity'],'INVALID')
                else:self.assertEqual(report['evidence_validity'],'INVALID')
                self.assertIsNone(report['behavior'])
    def test_timeout_preserves_partial_raw_output(self):
        result=self.capture('timeout',1.5)
        self.assertEqual(result['stop_reason'],'timeout');self.assertTrue((self.cap/'events.jsonl').read_bytes())
        self.assertIsNone(observer.evaluate(self.cap,result['run_sha256'])['behavior'])
    def test_capture_cannot_overwrite_prior_attempt(self):
        self.capture()
        with self.assertRaises(observer.Invalid):self.capture()
    def test_capture_digest_drift_refuses(self):
        result=self.capture();(self.cap/'events.jsonl').write_text('{}\n')
        self.assertEqual(observer.evaluate(self.cap,result['run_sha256'])['evidence_validity'],'INVALID')
    def test_receipt_drift_refuses(self):
        result=self.capture();(self.cap/'run.json').write_text('{}\n')
        self.assertEqual(observer.evaluate(self.cap,result['run_sha256'])['evidence_validity'],'INVALID')
    def test_missing_or_nonindependent_reviews_cannot_score(self):
        result=self.capture();p=self.review(result);x=read(p);x['independent']=False;put(p,x)
        self.assertIsNone(observer.evaluate(self.cap,result['run_sha256'],p)['behavior'])
    def test_review_missing_event_or_quote_refuses(self):
        result=self.capture();p=self.review(result);good=read(p)
        for defect in ('missing','quote','bool'):
            x=copy.deepcopy(good)
            if defect=='missing':x['events'].pop()
            elif defect=='quote':x['events'][0]['quote']='not in source'
            else:x['events'][0]['barriers']['wrong_owner']=0
            put(p,x);self.assertIsNone(observer.evaluate(self.cap,result['run_sha256'],p)['behavior'])
    def test_duplicate_thread_and_unfinished_item_refuse(self):
        result=self.capture();raw=(self.cap/'events.jsonl').read_bytes()
        rows=[json.loads(x) for x in raw.splitlines()]
        rows.insert(1,{'type':'thread.started','thread_id':'another'})
        with self.assertRaises(observer.Invalid):observer.parse_events(('\n'.join(map(json.dumps,rows))+'\n').encode())
        rows=[json.loads(x) for x in raw.splitlines()];rows.pop(3)
        with self.assertRaises(observer.Invalid):observer.parse_events(('\n'.join(map(json.dumps,rows))+'\n').encode())
    def test_missing_binary_reports_blocked_without_inference(self):
        report=runner.doctor('nonexistent-codex-unit-test')
        self.assertEqual(report['status'],'BLOCKED');self.assertEqual(report['model_calls'],0)
    def test_symlink_and_path_escape_refuse(self):
        with self.assertRaises(observer.Invalid):observer.safe_path(self.root,'../outside')
        p=self.root/'linked';p.symlink_to(self.ws)
        with self.assertRaises(observer.Invalid):observer.safe_path(p,'inputs/article.md')

class WriterPreparationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name).resolve()
        self.source=self.root/'source';self.source.mkdir();self.out=self.root/'packet'
        for name,text in [('task.md','SYNTHETIC task'),('AGENTS.md','SYNTHETIC instructions'),('article.md','SYNTHETIC article')]:
            (self.source/name).write_text(text)
        def entry(path,target):return {'root':'common','path':path,'target':target,'sha256':observer.sha((self.source/path).read_bytes())}
        self.spec={'schema_version':'writer-pair-experiment@1','experiment_id':'synthetic-control','scenario':'pending',
           'execution_kind':'synthetic_control','timeout_seconds':10,'task':{'path':'task.md','sha256':observer.sha((self.source/'task.md').read_bytes())},
           'order':['baseline','treatment','treatment','baseline','baseline','treatment'],
           'common_files':[entry('AGENTS.md','AGENTS.md'),entry('article.md','inputs/article.md')],
           'arms':{a:{'revision':'0'*40,'files':[]} for a in ('baseline','treatment')}}
        self.path=self.source/'spec.json';put(self.path,self.spec)
    def prepare(self):return runner.prepare(self.path,{a:self.source for a in ('common','baseline','treatment')},self.out)
    def test_prepare_is_offline_and_equal_inputs(self):
        result=self.prepare();p=read(self.out/'packet.json')
        self.assertEqual(result['writer_runs'],0);self.assertEqual(p['inputs']['baseline'],p['inputs']['treatment'])
        self.assertFalse((self.out/'runs').exists());self.assertFalse((self.out/'capsules/baseline/experiment.json').exists())
        self.assertEqual(len(p['jobs']),6);runner.validate_packet(self.out,result['packet_sha256'])
    def test_wrong_source_digest_refuses_before_output(self):
        (self.source/'article.md').write_text('changed')
        with self.assertRaises(observer.Invalid):self.prepare()
        self.assertFalse(self.out.exists())
    def test_overlapping_output_and_duplicate_destination_refuse(self):
        with self.assertRaises(observer.Invalid):runner.prepare(self.path,{a:self.source for a in ('common','baseline','treatment')},self.source/'packet')
        self.spec['common_files'].append(self.spec['common_files'][0]);put(self.path,self.spec)
        with self.assertRaises(observer.Invalid):self.prepare()
    def test_credentials_and_history_never_copied(self):
        for target in ('.git/config','.codex/config.toml','auth.json'):
            self.spec['common_files'][0]['target']=target;put(self.path,self.spec)
            with self.assertRaises(observer.Invalid):self.prepare()
            self.assertFalse(self.out.exists())
    def test_fixed_count_and_unsupported_accepted_packet_refuse(self):
        self.spec['order']=['baseline'];put(self.path,self.spec)
        with self.assertRaises(observer.Invalid):self.prepare()
        self.spec['scenario']='accepted';put(self.path,self.spec)
        with self.assertRaises(observer.Invalid):self.prepare()
    def test_post_preparation_input_mutation_refuses(self):
        result=self.prepare();(self.out/'capsules/baseline/inputs/article.md').write_text('drift')
        with self.assertRaises(observer.Invalid):runner.validate_packet(self.out,result['packet_sha256'])
    def test_external_host_is_required_and_pinned(self):
        result=self.prepare();h=self.root/'approval.json';put(h,{})
        with self.assertRaises(observer.Invalid):runner.validate_host(h,observer.sha(h.read_bytes()),result['packet_sha256'],{})
    def test_no_model_launch_without_qualified_pilot(self):
        # Synthetic packets are never launchable by the normal CLI path.
        result=self.prepare();host={'schema_version':'writer-host-approval@1','packet_sha256':result['packet_sha256'],
           'owner':'SYNTHETIC','isolation_evidence_ref':'SYNTHETIC','effective_config_ref':'SYNTHETIC','authentication_ref':'SYNTHETIC',
           'effects':['model-invocation','workspace-only-writes'],'model':'synthetic','isolation_verified':True,
           'expires_at':(datetime.now(timezone.utc)+timedelta(hours=1)).isoformat()}
        report=runner.doctor(str(FAKE));host.update(codex_sha256=report['codex_sha256'],codex_version=report['version'])
        p=self.root/'approval.json';put(p,host)
        with self.assertRaisesRegex(observer.Invalid,'synthetic'):
            runner.execute(self.out,result['packet_sha256'],str(FAKE),p,observer.sha(p.read_bytes()),'comparison')
        self.assertFalse((self.out/'runs').exists())
    def test_missing_selected_run_cannot_be_zero(self):
        self.spec['execution_kind']='host_codex_exec';put(self.path,self.spec)
        result=self.prepare();p=self.root/'selection.json';put(p,{})
        with self.assertRaisesRegex(observer.Invalid,'missing'):
            observer.compare(self.out,result['packet_sha256'],p)


class ComparisonSelectionTests(unittest.TestCase):
    setUp=WriterObserverTests.setUp
    capture=WriterObserverTests.capture
    review=WriterObserverTests.review
    """Schema controls built from synthetic transport, never reported as natural runs."""
    def make_comparison(self):
        sample=self.capture();packet=self.root/'packet';packet.mkdir()
        before=read(self.cap/'before.json')
        p={'schema_version':'writer-packet@1','execution_kind':'host_codex_exec','task_sha256':sample['files']['prompt.txt'],
           'controller_sha256':runner.tool_hashes(),
           'inputs':{a:{k:v['sha256'] for k,v in before.items()} for a in ('baseline','treatment')},
           'jobs':[{'id':f'run-{i:02d}','arm':'baseline' if i%2 else 'treatment'} for i in range(1,7)]}
        put(packet/'packet.json',p);psha=observer.sha((packet/'packet.json').read_bytes())
        def clone(dest,identity,arm,phase,host_sha):
            shutil.copytree(self.cap,dest)
            events=[json.loads(x) for x in (dest/'events.jsonl').read_text().splitlines()]
            events[0]['thread_id']=identity
            (dest/'events.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in events))
            r=read(dest/'run.json');r.update(packet_sha256=psha,job_id=identity,arm=arm,phase=phase,
                thread_id=identity,execution_kind='host_codex_exec',host_approval_sha256=host_sha)
            r['files']['events.jsonl']=observer.sha((dest/'events.jsonl').read_bytes());put(dest/'run.json',r)
            return r,observer.sha((dest/'run.json').read_bytes())
        pilot,pilot_sha=clone(packet/'pilot/capture','pilot','pilot','pilot','SYNTHETIC')
        host={'packet_sha256':psha,'isolation_verified':True,'capture_review_ref':'SYNTHETIC QUALIFICATION',
              'pilot_run_sha256':pilot_sha,'model':sample['requested_model'],'codex_sha256':sample['codex_sha256'],
              'codex_version':sample['codex_version'],'expires_at':(datetime.now(timezone.utc)+timedelta(hours=1)).isoformat()}
        put(packet/'runs/host-approval.json',host);hostsha=observer.sha((packet/'runs/host-approval.json').read_bytes())
        selection={}
        for job in p['jobs']:
            dest=packet/f"runs/{job['id']}/capture";r,rsha=clone(dest,job['id'],job['arm'],'comparison',hostsha)
            old=self.cap;self.cap=dest
            review=self.review({**r,'run_sha256':rsha},'wrong_owner' if job['arm']=='baseline' else None)
            new=packet/f"reviews/{job['id']}.json";new.parent.mkdir(exist_ok=True);shutil.copyfile(review,new);self.cap=old
            selection[job['id']]={'run_sha256':rsha,'review':str(new),'review_sha256':observer.sha(new.read_bytes())}
        selected=packet/'selection.json';put(selected,selection)
        return packet,psha,selected
    def test_controlled_label_comparison_is_scoped_not_closure(self):
        folder,sha,selection=self.make_comparison();r=observer.compare(folder,sha,selection)
        self.assertEqual(r['counts'],{'baseline':3,'treatment':0})
        self.assertEqual(r['verdict'],'SCOPED_OBSERVED_ROUTE_IMPROVEMENT')
        self.assertFalse(r['authorizes_landing']);self.assertEqual(r['accepted_episode_writing'],'NOT_TESTED')
    def test_duplicate_session_refuses_even_when_rehashed(self):
        folder,psha,selection=self.make_comparison();selected=read(selection)
        dest=folder/'runs/run-02/capture';events=[json.loads(x) for x in (dest/'events.jsonl').read_text().splitlines()]
        events[0]['thread_id']='run-01';(dest/'events.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in events))
        r=read(dest/'run.json');r['thread_id']='run-01';r['files']['events.jsonl']=observer.sha((dest/'events.jsonl').read_bytes());put(dest/'run.json',r)
        rsha=observer.sha((dest/'run.json').read_bytes());rev=Path(selected['run-02']['review']);v=read(rev)
        v['run_sha256']=rsha;v['events_sha256']=r['files']['events.jsonl'];put(rev,v)
        selected['run-02'].update(run_sha256=rsha,review_sha256=observer.sha(rev.read_bytes()));put(selection,selected)
        with self.assertRaisesRegex(observer.Invalid,'duplicate'):observer.compare(folder,psha,selection)
    def test_missing_pilot_or_model_mismatch_cannot_compare(self):
        folder,psha,selection=self.make_comparison();selected=read(selection);dest=folder/'runs/run-02/capture'
        r=read(dest/'run.json');r['requested_model']='another-model';put(dest/'run.json',r)
        selected['run-02']['run_sha256']=observer.sha((dest/'run.json').read_bytes());put(selection,selected)
        with self.assertRaisesRegex(observer.Invalid,'carrier'):observer.compare(folder,psha,selection)
    def test_relabelled_pilot_cannot_count_as_formal_run(self):
        folder,psha,selection=self.make_comparison();selected=read(selection);dest=folder/'runs/run-02/capture'
        r=read(dest/'run.json');r['phase']='pilot';put(dest/'run.json',r)
        rsha=observer.sha((dest/'run.json').read_bytes());v=Path(selected['run-02']['review']);x=read(v);x['run_sha256']=rsha;put(v,x)
        selected['run-02'].update(run_sha256=rsha,review_sha256=observer.sha(v.read_bytes()));put(selection,selected)
        with self.assertRaises(observer.Invalid):observer.compare(folder,psha,selection)

if __name__=='__main__':unittest.main()
