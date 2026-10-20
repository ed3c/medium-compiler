#!/usr/bin/env python3
"""Read a full-site deployment against a local, clean build; never deploy."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import urllib.error
import urllib.request


def verify(url: str, site: Path, revision: str) -> dict:
    origin=url.rstrip('/')
    checks=[]
    def request(path, status=200, method='GET'):
        req=urllib.request.Request(origin+path, method=method,
                                   headers={'User-Agent':'medium-compiler-site-verifier/1.0'})
        try:
            response=urllib.request.urlopen(req, timeout=30)
        except urllib.error.HTTPError as error:
            response=error
        with response:
            body=response.read()
            assert response.status==status, f'{method} {path}: {response.status}, expected {status}'
            assert response.url.startswith(origin+'/'), f'{path}: redirected to another origin'
            checks.append({'path':path,'method':method,'status':response.status})
            return body,response.headers
    expected=(site/'deployment.json').read_bytes()
    manifest=json.loads(expected)
    assert manifest['revision']==revision and manifest['dirty'] is False, 'Expected clean matching-revision build'
    actual,_=request('/deployment.json')
    assert actual==expected, 'Remote deployment manifest differs from local build'
    for path,digest in manifest['files'].items():
        if path.startswith('_'): continue  # Provider routing configuration is not a public asset.
        body,headers=request('/'+path)
        assert hashlib.sha256(body).hexdigest()==digest, f'Asset bytes differ: {path}'
        if path.endswith('.svg'): assert 'image/svg+xml' in headers['Content-Type'], path
        if path.endswith('.wasm'): assert 'application/wasm' in headers['Content-Type'], path
        if path.endswith('.css'): assert 'text/css' in headers['Content-Type'], path
        if path.endswith(('.js','.mjs')): assert 'javascript' in headers['Content-Type'], path
    for path in ('/','/alg-four/','/learning/','/cefr-alg-c2/','/articles/','/transcripts/','/more-route/'):
        _,headers=request(path)
        assert 'text/html' in headers['Content-Type'], path
    _,headers=request('/alg-four')
    assert 'text/html' in headers['Content-Type']
    _,headers=request('/reliability/')
    assert headers['Cross-Origin-Opener-Policy']=='same-origin'
    assert headers['Cross-Origin-Embedder-Policy']=='require-corp'
    request('/not-a-real-site-route',404)
    for path,status,method in (('/api/missing',404,'GET'),('/api/create',404,'GET'),
                               ('/api/transcripts?q=x',400,'GET'),
                               ('/api/transcripts?action=inspect&url=http://localhost',400,'GET'),
                               ('/api/transcripts',405,'POST')):
        body,headers=request(path,status,method)
        assert 'application/json' in headers['Content-Type']
        assert isinstance(json.loads(body).get('error'),str)
        assert headers['Cache-Control']=='no-store'
    return {'status':'PASS','origin':origin,'revision':revision,'asset_count':len(manifest['files'])-1,
            'checks':checks,'provider_transcript_search_inspect':'separate live-provider readback',
            'sandbox_behavior':'NOT_EXERCISED'}


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--url',required=True)
    parser.add_argument('--site',type=Path,required=True)
    parser.add_argument('--revision',required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    result={'status':'INCONCLUSIVE'}
    try:
        result=verify(args.url,args.site,args.revision)
    except Exception as error:
        result['error']=str(error)
        raise
    finally:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='checks'},indent=2))
