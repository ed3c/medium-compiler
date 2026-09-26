#!/usr/bin/env python3
"""Replay the experiment-vs-promotion authority correction on the real article."""
import argparse, hashlib, json, shutil, subprocess, sys, tempfile, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; EV=Path(__file__).resolve().parent
def dig(data): return 'sha256:'+hashlib.sha256(data).hexdigest()
def write(path,value): path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def main():
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args(); out=a.out.resolve()
    if out.exists() or out.is_relative_to(ROOT): ap.error('--out must be new and outside checkout')
    out.mkdir(parents=True); logs=[]
    def call(*args,expected=0):
        argv=[sys.executable,str(ROOT/'scripts/lossless_batch.py'),*map(str,args)]
        t=time.monotonic(); r=subprocess.run(argv,capture_output=True,text=True,timeout=40)
        logs.append({'argv':argv,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'elapsed_seconds':time.monotonic()-t})
        write(out/'commands.json',{'commands':logs})
        if r.returncode!=expected: raise ValueError(f'unexpected exit {r.returncode}; see commands.json')
        raw=r.stdout or r.stderr
        return json.loads(raw) if raw.strip().startswith('{') else {'text':raw}
    result={'fresh_writer_ab':'NOT_RUN','independent_reader':'NOT_RUN','human_learning_progress':'NOT_UPDATED'}
    with tempfile.TemporaryDirectory(prefix='medium-authority-') as td:
        temp=Path(td); run=temp/'article-run'
        ready=call('preflight','--article',EV/'before.md','--plan',EV/'plan.json'); assert ready['status']=='READY'
        boot=call('boot','--article',EV/'before.md','--plan',EV/'plan.json','--run-dir',run)
        patch={'unit_id':'experiment-before-promotion','base_sha256':boot['article_sha256'],'text':(EV/'drill-down.md').read_text()}
        write(temp/'patch.json',patch); bad=dict(patch,base_sha256='sha256:'+'0'*64); write(temp/'bad.json',bad)
        call('drill-down','--run-dir',run,'--patch',temp/'bad.json',expected=2)
        call('drill-down','--run-dir',run,'--patch',temp/'patch.json')
        assert call('drill-down','--run-dir',run,'--patch',temp/'patch.json')['operation']=='NOOP'
        call('render','--run-dir',run,'--output',out/'article.md')
        done=call('finish','--run-dir',run,'--review',EV/'review.json')
        before=(EV/'before.md').read_bytes(); after=(out/'article.md').read_bytes(); d=(EV/'drill-down.md').read_bytes()
        assert after.count(d)==1 and after.replace(d,b'',1)==before
        assert after==(ROOT/'articles/ai-engineer-learning-path.md').read_bytes() and done['status']=='DONE'
        shutil.copytree(ROOT/'evidence/issue-8/inputs',temp/'inputs')
        plan=json.loads((ROOT/'evidence/issue-8/plan.json').read_text()); plan['purpose']='learning-episode'
        plan['learning']={'episode_id':'synthetic-authority','lesson_ref':'synthetic-course@fixed:authority','handoff_source':'owner-handoff'}
        def add_source(sid,data,provenance):
            rel=f'inputs/{sid}.txt'; (temp/rel).write_bytes(data)
            plan['sources']=[x for x in plan['sources'] if x['id']!=sid]
            plan['sources'].append({'id':sid,'path':rel,'sha256':dig(data),'provenance':provenance})
        add_source('human-answer',b'SYNTHETIC HUMAN ANSWER\n','synthetic learner; test only')
        add_source('learning-record',b'SYNTHETIC LEARNING OWNER ACCEPTANCE\n','synthetic learning owner; test only')
        record={'schema_version':'medium-learning-handoff@2','episode_id':'synthetic-authority','lesson_ref':'synthetic-course@fixed:authority','case':plan['case'],'status':'ACCEPTED','experiment_decision':'EXPERIMENT','promotion_decision':'NOT_EVALUATED','product_need':'UNKNOWN','evidence_refs':[{'source_id':'ops-runtime-result','anchor':'cross_currency_not_subtracted'}],'human_checkpoint':{'source_id':'human-answer','anchor':'SYNTHETIC HUMAN ANSWER'},'learning_record':{'source_id':'learning-record','anchor':'SYNTHETIC LEARNING OWNER ACCEPTANCE'}}
        def sync(name):
            data=(json.dumps(record,ensure_ascii=False,indent=2,sort_keys=True)+'\n').encode()
            add_source('owner-handoff',data,'synthetic external owner declaration; test only')
            p=temp/name; write(p,plan); return p
        p=sync('learning-plan.json'); experiment=call('preflight','--article',EV/'before.md','--plan',p)
        assert experiment['status']=='READY' and not experiment['authorizes_product_write']
        record['promotion_decision']='PROMOTE'; record['product_need']='ABSENT'
        call('preflight','--article',EV/'before.md','--plan',sync('bad-promote.json'),expected=2)
        record['product_need']='PRESENT'; promote=call('preflight','--article',EV/'before.md','--plan',sync('promote.json'))
        assert promote['promotion_prerequisites_declared'] and not promote['authorizes_product_write']
        record['experiment_decision']='PENDING'; record['promotion_decision']='NOT_EVALUATED'; record['product_need']='UNKNOWN'
        pending=call('preflight','--article',EV/'before.md','--plan',sync('pending.json'),expected=3)
        assert pending['next']['owner']=='experiment-owner'
        result['authority_controls']={'experiment_without_promotion':'READY_NON_AUTHORIZING','promote_without_product_need':'REFUSED','promote_with_declared_prerequisites':'READY_NON_AUTHORIZING','pending_experiment_owner':'experiment-owner','synthetic_acceptance':'UNIT_TEST_CONTROL_ONLY'}
        result['article']={'before_sha256':dig(before),'after_sha256':dig(after),'inserted_bytes':len(d),'unchanged_outside_insertion':True,'canonical_matches':True,'review':'AUTHOR_REVIEW_ONLY'}
    result['status']='SCOPED_AUTHORITY_CORRECTION'; write(out/'result.json',result); print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
