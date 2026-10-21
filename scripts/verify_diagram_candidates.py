#!/usr/bin/env python3
"""Verify reviewed versioned derived architecture/editorial candidates.

A review receipt in a JSON file is a source assertion, not proof of
independent native method use, browser interaction, or semantic correctness.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath

SCHEMA='derived-visual-knowledge@1'
MAX_BYTES=2*1024*1024
def rel(name):
    if not isinstance(name,str) or not name or '\\' in name or name.startswith('/'):
        raise ValueError('UNSAFE_SOURCE_PATH')
    path=PurePosixPath(name)
    if any(part in ('.','..') for part in path.parts):
        raise ValueError('UNSAFE_SOURCE_PATH')
    return path

def source_bytes(root,relative):
    p=rel(relative)
    full=root.joinpath(*p.parts)
    if not full.is_file() or not full.resolve().is_relative_to(root.resolve()):
        raise ValueError('UNAVAILABLE_SOURCE')
    for candidate in (full,*full.parents):
        if candidate==root:break
        if candidate.is_symlink():raise ValueError('SYMLINK_REFUSED')
    if full.stat().st_size>MAX_BYTES:raise ValueError('SOURCE_TOO_LARGE')
    return full.read_bytes()

def check(root,data):
    if data.get('schema_version')!=SCHEMA or not isinstance(data.get('items'),list):
        raise ValueError('INVALID_MANIFEST')
    seen=set()
    for item in data['items']:
        required={'kind','source','source_sha256','candidate','candidate_sha256',
                  'status','loss_report','review_receipt'}
        if not isinstance(item,dict) or set(item)!=required:
            raise ValueError('INVALID_ENTRY')
        if item['kind'] not in ('omm-architecture','seecode-editorial'):
            raise ValueError('UNSUPPORTED_KIND')
        pair=(item['kind'],item['candidate'])
        if pair in seen:raise ValueError('DUPLICATE_CANDIDATE')
        seen.add(pair)
        for ref,digest in ((item['source'],item['source_sha256']),
                           (item['candidate'],item['candidate_sha256'])):
            if not isinstance(digest,str) or len(digest)!=64 or any(ch not in '0123456789abcdef' for ch in digest):
                raise ValueError('MALFORMED_DIGEST')
            if hashlib.sha256(source_bytes(root,ref)).hexdigest()!=digest:
                raise ValueError('SOURCE_DIGEST_DRIFT')
        if not isinstance(item['loss_report'],list) or any(not isinstance(x,str) for x in item['loss_report']):
            raise ValueError('MISSING_LOSS_REPORT')
        if item['kind']=='omm-architecture':
            if not item['candidate'].startswith('docs/derived-architecture/') or not item['candidate'].endswith('.mmd'):
                raise ValueError('OUTSIDE_REVIEWED_ARCHITECTURE_DIR')
            if not item['source'].startswith(('site/','scripts/','apps/','contracts/','docs/')):
                raise ValueError('UNBOUND_CODE_SOURCE')
            diagram=source_bytes(root,item['candidate'])
            if not diagram.lstrip().startswith((b'graph ',b'flowchart ')):
                raise ValueError('NOT_ARCHITECTURE_MERMAID')
        else:
            if not item['candidate'].startswith('design/diagram-candidates/') or not item['candidate'].endswith('.json'):
                raise ValueError('OUTSIDE_EDITORIAL_CANDIDATE_DIR')
            spec=json.loads(source_bytes(root,item['candidate']))
            if spec.get('fonts')!='system' or spec.get('motion') not in ('none','trace','step','reveal'):
                raise ValueError('EXTERNAL_RESOURCE_OR_MOTION')
            refs=spec.get('evidence')
            if not isinstance(refs,list) or not refs or any(row.get('file')!=item['source'] for row in refs):
                raise ValueError('UNBOUND_EDITORIAL_EVIDENCE')
        if item['status']=='reviewed':
            receipt=item['review_receipt']
            if not isinstance(receipt,dict) or set(receipt)!={'reviewer','source_sha256','candidate_sha256'} or not receipt['reviewer']:
                raise ValueError('MISSING_REVIEW_METADATA')
            if receipt['source_sha256']!=item['source_sha256'] or receipt['candidate_sha256']!=item['candidate_sha256']:
                raise ValueError('REVIEW_VERSION_DRIFT')
        elif item['status']=='candidate':
            if item['review_receipt'] is not None:
                raise ValueError('PREMATURE_REVIEW')
        else:raise ValueError('BAD_REVIEW_STATUS')
    return {'status':'SOURCE_CONTRACT_PASS','count':len(data['items']),
            'reviewed_claims':sum(x['status']=='reviewed' for x in data['items'])}

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    p.add_argument('--manifest',default='design/diagram-candidates/manifest.json')
    args=p.parse_args()
    root=args.root.resolve()
    print(json.dumps(check(root,json.loads(source_bytes(root,args.manifest)))))
if __name__=='__main__':main()
