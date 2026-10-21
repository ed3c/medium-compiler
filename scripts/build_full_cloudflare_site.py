#!/usr/bin/env python3
"""Build the entire site for an independent Cloudflare Static Assets Worker."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
from build_site import ROOT, MAIN_ORIGIN, build as build_site


def build(out: Path) -> dict:
    provenance = build_site(out)
    # Map presentation URLs only. Admitted Markdown and source manifests stay exact.
    pattern = re.compile(r'((?:href|src)=")' + re.escape(MAIN_ORIGIN) + r'(/[^"\s]*)"')
    for path in out.rglob('*.html'):
        text = path.read_text(encoding='utf-8')
        path.write_text(pattern.sub(r'\1\2"', text), encoding='utf-8')
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    dirty = bool(subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=normal'], cwd=ROOT, text=True).strip())
    provenance['deployment'] = {'target': 'cloudflare-full-site', 'revision': revision, 'dirty': dirty,
                              'lab_origin_preserved': True}
    (out/'provenance.json').write_text(json.dumps(provenance, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    files = {path.relative_to(out).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
             for path in sorted(out.rglob('*')) if path.is_file()}
    if len(files)+1 > 20000 or any(path.stat().st_size > 25*1024*1024 for path in out.rglob('*') if path.is_file()):
        raise ValueError('Full site exceeds Workers Free Static Assets deployment limits')
    manifest = {'revision': revision, 'dirty': dirty, 'files': files}
    (out/'deployment.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
    return {'revision': revision, 'dirty': dirty, 'files': len(files)+1,
            'bytes': sum(path.stat().st_size for path in out.rglob('*') if path.is_file()),
            'alg_four': provenance['alg_four']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, default=ROOT/'dist')
    args = parser.parse_args()
    print(json.dumps(build(args.out.resolve()), ensure_ascii=False, indent=2))
