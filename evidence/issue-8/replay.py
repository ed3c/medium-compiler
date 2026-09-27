#!/usr/bin/env python3
"""Replay the two reviewed article increments; updating checked-in delivery is explicit.

Default writes only a new external --out. --update-article additionally installs the
already-reviewed exact article and its dependent evidence/delivery files; unknown
current article bytes are refused. No Git, network, model, or publication operation.
"""
import argparse
import difflib
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
EV=Path(__file__).resolve().parent
AFTER='2fe1433a2e4f7ed4dfc83936617c22b915532ceeb29397773332c8564a55ad0f'
BEFORE='c5e7b5ca7a02f5b8bc9b5b19d4ad58fe2e386be55b5051815d017c6c21d3fb82'

def digest(b):return hashlib.sha256(b).hexdigest()
def blob(b):return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--update-article',action='store_true')
    a=p.parse_args();out=a.out.resolve()
    if out.exists() or out.is_relative_to(ROOT):p.error('--out must be new and outside checkout')
    before=(EV/'before.md').read_bytes()
    if digest(before)!=BEFORE:raise ValueError('baseline drift')
    current=ROOT/'articles/ai-engineer-learning-path.md'
    if a.update_article and digest(current.read_bytes()) not in {BEFORE,AFTER}:
        raise ValueError('refuse to overwrite an unknown article edition')
    out.mkdir(parents=True);logs=[];plan=json.loads((EV/'plan.json').read_text());run=out/'run'
    def call(*args):
        argv=[sys.executable,str(ROOT/'scripts/lossless_batch.py'),*map(str,args)]
        r=subprocess.run(argv,cwd=ROOT,capture_output=True,text=True,timeout=40)
        logs.append({'argv':argv,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
        dump(out/'commands.json',{'commands':logs})
        if r.returncode:raise ValueError('batch refused; see commands.json')
        return json.loads(r.stdout)
    call('boot','--article',EV/'before.md','--plan',EV/'plan.json','--run-dir',run)
    patches=[]
    for i,unit in enumerate(plan['units'],1):
        state=call('next','--run-dir',run)
        if state['source_cursor']!=unit['id']:raise ValueError('unexpected cursor')
        text=(EV/f'drill-down-0{i}.md').read_text(encoding='utf-8')
        patch={'unit_id':unit['id'],'base_sha256':state['article_sha256'],'text':text}
        path=out/f'patch-0{i}.json';dump(path,patch);patches.append(path)
        call('drill-down','--run-dir',run,'--patch',path)
    call('render','--run-dir',run,'--output',out/'article.md')
    after=(out/'article.md').read_bytes()
    if digest(after)!=AFTER:raise ValueError('output differs from reviewed article')
    call('finish','--run-dir',run,'--review',EV/'review.json')
    call('next','--run-dir',run)
    if a.update_article:
        current.write_bytes(after);(EV/'expected-after.md').write_bytes(after)
        for i,path in enumerate(patches,1):(EV/f'patch-0{i}.json').write_bytes(path.read_bytes())
        (EV/'batch-proof.json').write_bytes((run/'final/batch-proof.json').read_bytes())
        (EV/'article.diff').write_text(''.join(difflib.unified_diff(before.decode().splitlines(True),after.decode().splitlines(True),fromfile='before.md',tofile='articles/ai-engineer-learning-path.md')),encoding='utf-8')
        pieces=[];text=after.decode();positions=[0]+[text.index(h) for h in ('## 5.','## 8.','## 11.','## 14.')]+[len(text)]
        directory=ROOT/'articles/ai-engineer-learning-path.parts'
        for i in range(5):
            data=text[positions[i]:positions[i+1]].encode();name=f'part-{i+1:02d}.md'
            (directory/name).write_bytes(data);pieces.append({'path':name,'git_blob':blob(data)})
        dump(directory/'manifest.json',{'schema_version':'medium-delivery-parts@2','article':'articles/ai-engineer-learning-path.md','article_git_blob':blob(after),'part_order':[v['path'] for v in pieces],'parts':pieces,'assembly':'concatenate part_order with no separator; result bytes must equal article'})
        context_path=ROOT/'articles/ai-engineer-learning-path.context.json'
        context=json.loads(context_path.read_text());context['incremental_expansion']={'issue':8,'work_plan':'evidence/issue-8/plan.json','applied_units':[u['id'] for u in plan['units']],'retention':'Two insertions only; prior article bytes retained.','semantic_review':'AUTHOR_REVIEW_ONLY','independent_reader':'NOT_RUN'};dump(context_path,context)
    print(json.dumps({'status':'REPLAYED','before_sha256':BEFORE,'after_sha256':AFTER,'article_updated':a.update_article,'independent_reader':'NOT_RUN'}))

if __name__=='__main__':main()
