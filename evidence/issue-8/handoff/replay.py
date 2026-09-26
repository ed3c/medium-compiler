#!/usr/bin/env python3
"""One actual article insertion plus read-only learning-admission controls.

No accepted learner record is created. The ready learning path is covered only by
explicit synthetic unit-test fixtures. This replay exercises the actual absent handoff.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[3]
EV = Path(__file__).resolve().parent
BEFORE = ROOT / 'evidence/issue-8/expected-after.md'

def digest(data): return 'sha256:' + hashlib.sha256(data).hexdigest()
def write(path, value): path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--baseline-cli', type=Path)
    a = p.parse_args(); out = a.out.resolve()
    if out.exists() or out.is_relative_to(ROOT): p.error('--out must be new and outside checkout')
    out.mkdir(parents=True); logs = []
    def call(*args, expected=0, entry=None):
        argv = [sys.executable, str(entry or ROOT/'scripts/lossless_batch.py'), *map(str,args)]
        start = time.monotonic(); r = subprocess.run(argv, capture_output=True, text=True, timeout=40)
        logs.append({'argv':argv,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr,
                     'elapsed_seconds':time.monotonic()-start})
        write(out/'commands.json', {'commands':logs})
        if r.returncode != expected: raise ValueError('unexpected exit; see commands.json')
        return json.loads(r.stdout or r.stderr)
    result = {'baseline_commit':'71fce847f6b521d812ba8179dcf4f53e06a69ef6',
              'fresh_writer_ab':'NOT_RUN','independent_reader':'NOT_RUN',
              'human_learning_progress':'NOT_UPDATED', 'synthetic_learning_acceptance':'UNIT_TESTS_ONLY',
              'candidate_helper_sha256':digest((ROOT/'scripts/lossless_batch.py').read_bytes())}
    with tempfile.TemporaryDirectory(prefix='medium-handoff-') as td:
        temp=Path(td)
        # This is the actual existing source/plan. The requested learning purpose has
        # no admitted episode: no placement or learner record is invented to fill it.
        shutil.copytree(ROOT/'evidence/issue-8/inputs',temp/'inputs')
        plan=json.loads((ROOT/'evidence/issue-8/plan.json').read_text())
        plan['purpose']='learning-episode'
        write(temp/'pending-plan.json',plan)
        result['same_pending_plan_sha256']=digest((temp/'pending-plan.json').read_bytes())
        denied=call('preflight','--article',BEFORE,'--plan',temp/'pending-plan.json',expected=3)
        blocked=call('boot','--article',BEFORE,'--plan',temp/'pending-plan.json','--run-dir',temp/'blocked-run',expected=3)
        assert blocked['next']['owner']=='learning-owner'
        assert blocked['next']['missing_input']=='learning_handoff'
        assert not (temp/'blocked-run').exists()
        result['missing_handoff']={'preflight':denied,'boot':blocked,'created_run':False}
        if a.baseline_cli:
            result['baseline_helper_sha256']=digest(a.baseline_cli.read_bytes())
            old=call('boot','--article',BEFORE,'--plan',temp/'pending-plan.json','--run-dir',temp/'old-run',entry=a.baseline_cli)
            assert old['status']=='CONTINUE' and old['next']=='drill-down'
            result['baseline_missing_handoff']={'output':old,'created_run':(temp/'old-run').exists(),
                         'classification':'deterministic old-code reproduction, not a natural writer run'}
        # Different explicit task: source-explanation of the learning/writing boundary.
        # This never imports or grades the pending Ops PR24 learning episode.
        ready=call('preflight','--article',BEFORE,'--plan',EV/'article-plan.json')
        assert ready['purpose']=='source-explanation'
        run=temp/'article-run'
        call('boot','--article',BEFORE,'--plan',EV/'article-plan.json','--run-dir',run)
        action=call('next','--run-dir',run)
        patch={'unit_id':'learning-before-writing','base_sha256':action['article_sha256'],
               'text':(EV/'drill-down.md').read_text()}
        bad=dict(patch,base_sha256='sha256:'+'0'*64); write(temp/'bad.json',bad)
        call('drill-down','--run-dir',run,'--patch',temp/'bad.json',expected=2)
        write(temp/'patch.json',patch)
        call('drill-down','--run-dir',run,'--patch',temp/'patch.json')
        assert call('drill-down','--run-dir',run,'--patch',temp/'patch.json')['operation']=='NOOP'
        assert call('next','--run-dir',run)['next']=='review-and-finish'
        call('render','--run-dir',run,'--output',out/'article.md')
        call('finish','--run-dir',run,'--review',EV/'review.json')
        before=BEFORE.read_bytes(); after=(out/'article.md').read_bytes(); delta=(EV/'drill-down.md').read_bytes()
        assert after.count(delta)==1 and after.replace(delta,b'',1)==before
        assert after==(ROOT/'articles/ai-engineer-learning-path.md').read_bytes()
        assert after==(run/'final/compiled/medium-canonical.md').read_bytes()
        shutil.copytree(run,out/'retained-run')
        result['article']={'before_sha256':digest(before),'after_sha256':digest(after),
                          'inserted_bytes':len(delta),'unchanged_outside_insertion':True,
                          'canonical_matches':True,'review':'AUTHOR_REVIEW_ONLY',
                          'purpose':'source-explanation, NOT a completed learning episode'}
    # Fresh process reads back after scratch cleanup and relocation.
    assert call('next','--run-dir',out/'retained-run')['status']=='DONE'
    result['evidence_survived_cleanup']=True
    result['status']='SCOPED_DETERMINISTIC_CORRECTION'
    write(out/'result.json',result)
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
