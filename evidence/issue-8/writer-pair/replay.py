#!/usr/bin/env python3
"""Real same-article explanation update; not a fresh writer/model/learner episode."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
ROOT=Path(__file__).resolve().parents[3];EV=Path(__file__).resolve().parent

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();out=a.out.resolve()
    if out.exists() or out.is_relative_to(ROOT):p.error('--out must be new and outside the checkout')
    out.mkdir(parents=True);logs=[]
    def call(*args,expected=0):
        argv=[sys.executable,str(ROOT/'scripts/lossless_batch.py'),*map(str,args)]
        start=time.monotonic();r=subprocess.run(argv,capture_output=True,text=True,timeout=40)
        logs.append({'argv':argv,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'elapsed_seconds':time.monotonic()-start})
        (out/'commands.json').write_text(json.dumps(logs,ensure_ascii=False,indent=2)+'\n')
        if r.returncode!=expected:raise ValueError('unexpected exit; see commands.json')
        return json.loads(r.stdout or r.stderr)
    with tempfile.TemporaryDirectory(prefix='writer-observation-article-') as tmp:
        run=Path(tmp)/'run'
        ready=call('preflight','--article',EV/'before.md','--plan',EV/'plan.json');assert ready['status']=='READY'
        boot=call('boot','--article',EV/'before.md','--plan',EV/'plan.json','--run-dir',run)
        delta=(EV/'drill-down.md').read_bytes()
        patch={'unit_id':'observe-writer-not-guard','base_sha256':boot['article_sha256'],'text':delta.decode()}
        path=Path(tmp)/'patch.json';path.write_text(json.dumps(patch,ensure_ascii=False)+'\n')
        call('drill-down','--run-dir',run,'--patch',path)
        assert call('drill-down','--run-dir',run,'--patch',path)['operation']=='NOOP'
        call('render','--run-dir',run,'--output',out/'article.md')
        result=call('finish','--run-dir',run,'--review',EV/'review.json');assert result['status']=='DONE'
        before=(EV/'before.md').read_bytes();after=(out/'article.md').read_bytes()
        assert after.count(delta)==1 and after.replace(delta,b'',1)==before
        assert after==(ROOT/'articles/ai-engineer-learning-path.md').read_bytes()
        shutil.copytree(run,out/'retained-run')
    assert call('next','--run-dir',out/'retained-run')['status']=='DONE'
    receipt={'status':'REAL_ARTICLE_ADDITION_REPLAYED','before_sha256':'sha256:'+hashlib.sha256(before).hexdigest(),
             'after_sha256':'sha256:'+hashlib.sha256(after).hexdigest(),'inserted_bytes':len(delta),
             'unchanged_outside_insertion':True,'review':'AUTHOR_REVIEW_ONLY','fresh_writer_ab':'NOT_RUN',
             'accepted_episode':'NOT_SUPPLIED','human_learning_progress':'NOT_UPDATED','evidence_survived_cleanup':True}
    (out/'result.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(receipt,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
