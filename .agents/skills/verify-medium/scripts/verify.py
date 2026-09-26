#!/usr/bin/env python3
"""Drive the actual writing CLI, preserving proof outside disposable runs."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
import medium_compiler as mc

FEATURES=("staged-authoring","bounded-revision","lossless-drilldown","delivery","behavior-evals")


def blob(data):return hashlib.sha1(f"blob {len(data)}\0".encode()+data).hexdigest()
def sha(data):return "sha256:"+hashlib.sha256(data).hexdigest()
def put(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n")


class Driver:
    def __init__(self,out):self.out=out;self.logs=[];self.feature="doctor"
    def call(self,args,expected=0):
        r=subprocess.run(args,cwd=ROOT,capture_output=True,text=True,timeout=40)
        self.logs.append({"feature":self.feature,"argv":args,"exit":r.returncode,"stdout":r.stdout,"stderr":r.stderr})
        if r.returncode!=expected:raise ValueError(f"unexpected exit {r.returncode}: {args}")
        try:return json.loads(r.stdout)
        except json.JSONDecodeError:return {"text":r.stdout}
    def cli(self,*args,expected=0):return self.call([sys.executable,str(ROOT/'medium_compiler.py'),*map(str,args)],expected)
    def batch(self,*args,expected=0):return self.call([sys.executable,str(ROOT/'scripts/lossless_batch.py'),*map(str,args)],expected)
    def doctor(self):
        self.feature='doctor'
        self.cli('--help')
        names=[]
        if not (ROOT/'articles/ai-engineer-learning-path.md').is_file():
            raise ValueError('current article missing')
        for p in sorted((ROOT/'.agents/skills').glob('*/SKILL.md')):
            text=p.read_text();m=re.search(r'(?m)^name:\s*(.+)$',text)
            if not text.startswith('---\n') or not m or 'description:' not in text:
                raise ValueError(f'skill metadata invalid: {p}')
            names.append(m.group(1).strip('"\''))
        if len(names)!=len(set(names)):raise ValueError('duplicate skill names')
        lock=json.loads((ROOT/'references/upstream/skills-lock.json').read_text())
        for entry in lock['files']:
            if hashlib.sha256((ROOT/entry['path']).read_bytes()).hexdigest()!=entry['sha256']:
                raise ValueError('vendored bytes drift: '+entry['path'])
        return {'status':'PASS','python':sys.version.split()[0],'registered_skills':names,
                'codex_executable':shutil.which('codex'),'registration':'FILES_VERIFIED; live Codex selection not measured',
                'compiler_sha256':sha((ROOT/'medium_compiler.py').read_bytes())}
    def staged(self):
        self.feature='staged-authoring'
        with tempfile.TemporaryDirectory(prefix='medium-staged-') as tmp:
            p=Path(tmp);put(p/'spec.json',{'topic':'CLI stage-order control, not fresh Agent authorship','claims':[],'terms':[]})
            self.cli('init','--spec',p/'spec.json','--run-dir',p/'run')
            action=self.cli('next','--run-dir',p/'run');assert action['next_stage']==0
            (p/'part.md').write_text('# Fixture\n')
            put(p/'coverage.json',{'elements':list(mc.STAGE_ELEMENTS[1]),'claims':[],'terms':[]})
            self.cli('submit','--run-dir',p/'run','--stage',1,'--input',p/'part.md','--coverage',p/'coverage.json',expected=2)
            for i in range(7):
                text=f'## CLI fixture {i}\n\nStage order control.\n'
                if i==6:text=(p/'run/semantic-draft.md').read_text()
                (p/'part.md').write_text(text)
                put(p/'coverage.json',{'elements':list(mc.STAGE_ELEMENTS[i]),'claims':[],'terms':[]})
                self.cli('submit','--run-dir',p/'run','--stage',i,'--input',p/'part.md','--coverage',p/'coverage.json')
            self.cli('assemble','--run-dir',p/'run');self.cli('verify','--run-dir',p/'run')
            r=self.cli('next','--run-dir',p/'run');assert r['status']=='VALIDATED' and r['next'] is None
            shutil.copytree(p/'run',self.out/'staged-run')
        assert (self.out/'staged-run/validation-receipt.json').is_file()
        return {'status':'PASS','fixture_kind':'scripted CLI control; not a writer run'}
    def revision(self):
        self.feature='bounded-revision'
        with tempfile.TemporaryDirectory(prefix='medium-revision-') as tmp:
            p=Path(tmp);before=(ROOT/'evidence/issue-8/before.md').read_text()
            old='這篇文章的主例是公開的';new='這裡使用的主例是公開的'
            assert before.count(old)==1
            (p/'before.md').write_text(before);(p/'after.md').write_text(before.replace(old,new,1))
            put(p/'spec.json',{'topic':'Bounded real-article prose route control','claims':[],'terms':[]})
            put(p/'coverage.json',{'elements':['copyedit'],'claims':[],'terms':[]})
            self.cli('init','--draft',p/'before.md','--spec',p/'spec.json','--run-dir',p/'run')
            assert self.cli('next','--run-dir',p/'run')['next_stage']==6
            bad=before.replace('100.00','100.01',1)
            (p/'bad.md').write_text(bad)
            self.cli('submit','--run-dir',p/'run','--stage',6,'--input',p/'bad.md','--coverage',p/'coverage.json',expected=2)
            self.cli('submit','--run-dir',p/'run','--stage',6,'--input',p/'after.md','--coverage',p/'coverage.json')
            self.cli('assemble','--run-dir',p/'run');self.cli('verify','--run-dir',p/'run')
            self.cli('prove-update','--run-dir',p/'run','--issue',8,'--before',p/'before.md','--after',p/'after.md','--output',p/'proof.json')
            shutil.copytree(p/'run',self.out/'revision-run');shutil.copy2(p/'proof.json',self.out/'revision-proof.json')
            final=p/'run/medium-canonical.md';final.write_bytes(final.read_bytes()+b'changed')
            self.cli('check-receipt','--run-dir',p/'run',expected=2)
        self.cli('check-receipt','--run-dir',self.out/'revision-run')
        return {'status':'PASS','fixture_kind':'controlled one-phrase article edit, not the shipped expansion'}
    def lossless(self):
        self.feature='lossless-drilldown';ev=ROOT/'evidence/issue-8'
        with tempfile.TemporaryDirectory(prefix='medium-lossless-') as tmp:
            p=Path(tmp);run=p/'run'
            r=self.batch('boot','--article',ev/'before.md','--plan',ev/'plan.json','--run-dir',run)
            assert r['status']=='CONTINUE' and len(r['remaining_work'])==2
            assert r['case']['id']=='ops-reconciliation-copilot' and r['human_checkpoint']['status']=='DEFERRED'
            assert r['learning_step'].startswith('A03') and {x['role'] for x in r['evidence_refs']}=={'code','test','test_result'}
            self.batch('finish','--run-dir',run,'--review',ev/'review.json',expected=2)
            self.batch('drill-down','--run-dir',run,'--patch',ev/'patch-02.json',expected=2)
            self.batch('drill-down','--run-dir',run,'--patch',ev/'patch-01.json')
            assert self.batch('next','--run-dir',run)['source_cursor']=='finding-precedence'
            assert self.batch('drill-down','--run-dir',run,'--patch',ev/'patch-01.json')['operation']=='NOOP'
            self.batch('drill-down','--run-dir',run,'--patch',ev/'patch-02.json')
            ready=self.batch('next','--run-dir',run)
            assert ready['next']=='review-and-finish' and ready['human_checkpoint']['status']=='PENDING'
            self.batch('render','--run-dir',run,'--output',p/'expanded.md')
            r=self.batch('finish','--run-dir',run,'--review',ev/'review.json')
            assert r['status']=='DONE' and r['semantic_review']=='AUTHOR_REVIEW_ONLY'
            assert r['human_checkpoint']['status']=='PENDING' and r['human_learning_outcome']=='NOT_MEASURED'
            data=(run/'final/compiled/medium-canonical.md').read_bytes()
            assert data==(ev/'expected-after.md').read_bytes()
            shutil.copytree(run,self.out/'lossless-run')
            shutil.copy2(p/'expanded.md',self.out/'article.md')
        # Re-read after relocation AND cleanup, rather than assuming proof survived.
        assert self.batch('next','--run-dir',self.out/'lossless-run')['status']=='DONE'
        handoff=self.call([sys.executable,str(ROOT/'evidence/issue-8/handoff/replay.py'),
                           '--out',str(self.out/'handoff-proof')])
        data=(self.out/'handoff-proof/article.md').read_bytes()
        assert data==(ROOT/'articles/ai-engineer-learning-path.md').read_bytes()
        (self.out/'article.md').write_bytes(data)
        return {'status':'PASS','article_sha256':sha(data),'real_article':True,
                'author_review':'performed, not independent','learning_handoff':handoff['missing_handoff'],
                'human_progress':'NOT_UPDATED','fresh_writer_ab':'NOT_RUN'}
    def delivery(self):
        self.feature='delivery';parts=ROOT/'articles/ai-engineer-learning-path.parts'
        m=json.loads((parts/'manifest.json').read_text())
        order=m['part_order'];pieces=[]
        if len(order)!=len(set(order)):raise ValueError('duplicate delivery parts')
        for item in m['parts']:
            data=(parts/item['path']).read_bytes()
            if blob(data)!=item['git_blob']:raise ValueError('part identity drift')
        for name in order:pieces.append((parts/name).read_bytes())
        data=b''.join(pieces);article=(ROOT/m['article']).read_bytes()
        if data!=article or blob(data)!=m['article_git_blob']:raise ValueError('delivery differs from canonical article')
        sys.path.insert(0,str(ROOT/'scripts'))
        import lossless_batch
        lossless_batch.plain_article(data)
        controls={
            'missing_part': b''.join(pieces[:-1]) != article,
            'reordered_parts': b''.join(list(reversed(pieces))) != article,
            'changed_part': b''.join([pieces[0]+b'x',*pieces[1:]]) != article}
        if not all(controls.values()):raise ValueError('delivery controls insensitive')
        (self.out/'assembled-from-parts.md').write_bytes(data)
        return {'status':'PASS','parts':len(order),'refusal_controls':controls,'article_sha256':sha(data),'medium_browser_rendering':'NOT_RUN'}
    def behavior(self):
        self.feature='behavior-evals'
        return {'status':'BLOCKED','attempted':'doctor searched PATH; this deterministic driver has no authorized fresh-session execution interface',
                'codex_executable':shutil.which('codex'),'fresh_writer_ab':'NOT_RUN','independent_reader':'NOT_RUN',
                'missing':['approved isolated writer/reader carrier','fixed model/task/observer and raw per-session traces','trusted semantic labels'],
                'reason':'The local driver is deterministic; it cannot manufacture natural Agent or human-reader evidence.'}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--feature',choices=['doctor','all','mechanical',*FEATURES],required=True)
    p.add_argument('--out',type=Path,required=True);args=p.parse_args()
    out=args.out.resolve()
    if out.exists() or out.is_relative_to(ROOT):p.error('--out must be new and outside the checkout')
    out.mkdir(parents=True);driver=Driver(out);results={};failed=False
    try:
        results['doctor']=driver.doctor()
        choices=FEATURES if args.feature=='all' else FEATURES[:-1] if args.feature=='mechanical' else [] if args.feature=='doctor' else [args.feature]
        functions=dict(zip(FEATURES,[driver.staged,driver.revision,driver.lossless,driver.delivery,driver.behavior]))
        for feature in choices:
            driver.doctor() # each feature starts from a freshly checked CLI context
            try:results[feature]=functions[feature]()
            except Exception as exc:
                failed=True;results[feature]={'status':'FAIL','error':str(exc)}
                driver.doctor()
    except Exception as exc:
        failed=True;results['driver']={'status':'FAIL','error':str(exc)}
    finally:
        put(out/'commands.json',{'commands':driver.logs})
        blocked=any(v.get('status')=='BLOCKED' for v in results.values())
        report={'features':results,'outcome':'failed' if failed else 'blocked' if blocked else 'mechanical_pass',
                'source_review':'coordinator source review is separate; no subagent wave fabricated',
                'strict_pstack_maintenance':'NOT_CLAIMED','evidence_retained':True}
        put(out/'feature-results.json',report);print(json.dumps(report,ensure_ascii=False,indent=2))
    return 2 if failed else 3 if blocked else 0


if __name__=='__main__':raise SystemExit(main())
