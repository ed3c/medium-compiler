#!/usr/bin/env python3
"""Build only the Cloudflare experiment subsite; Vercel owns the total site."""
import argparse
import shutil
from pathlib import Path
from build_site import ROOT, MAIN_ORIGIN, build_reliability

def build(out:Path)->None:
    out=out.resolve()
    if out.exists():shutil.rmtree(out)
    (out/'assets').mkdir(parents=True)
    shutil.copyfile(ROOT/'site/styles.css',out/'assets/styles.css')
    shutil.copyfile(ROOT/'site/_headers',out/'_headers')
    build_reliability(out,MAIN_ORIGIN)
    routes=['/', '/articles/*', '/learning/*', '/cefr-alg-c2/*', '/experiments/*', '/ai-evals/*', '/transcripts/*']
    (out/'_redirects').write_text('\n'.join(f'{route} {MAIN_ORIGIN}{route.replace("*",":splat")} 302' for route in routes)+'\n')

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',type=Path,default=ROOT/'dist-cloudflare')
    build(parser.parse_args().out)
