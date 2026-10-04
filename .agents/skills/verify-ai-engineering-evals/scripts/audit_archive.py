#!/usr/bin/env python3
"""Read and bind an archived Soodles comparison. Never execute archived commands."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ARCHIVE = 'docs/experiments/claim-refusal-closure/behavior'


def audit(root, revision):
    head = subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()
    if head != revision:
        raise ValueError('Selected revision differs from checkout HEAD')
    sources = []
    def read(relative):
        path = ARCHIVE + '/' + relative
        raw = (root / path).read_bytes()
        pinned = subprocess.check_output(['git', '-C', str(root), 'show', revision + ':' + path])
        if raw != pinned:
            raise ValueError('Selected source differs from pinned Git bytes: ' + path)
        sources.append({'path': path, 'sha256': hashlib.sha256(raw).hexdigest(),
                        'url': f'https://github.com/ed3c/soodles/blob/{revision}/{path}'})
        return json.loads(raw)
    provenance = read('native/provenance.json')
    rows = []
    for case in ('c1', 'c2', 'c3'):
        for arm in ('n4', 'z8'):
            base = f'native/packets/{arm}/{case}'
            current = read(base + '/current.json')
            identity = read(base + '/identity.json')
            report = read(base + '/output/report.json')
            capture = read(f'native/raw/{arm}/{case}-launch.json')
            rows.append({'case': case, 'arm': arm,
                         'owner_status': current.get('status'),
                         'action': report.get('action'),
                         'waiting_on': report.get('waiting_on'),
                         'required': report.get('required'),
                         'resolved': report.get('resolved'),
                         'proposed_argv': report.get('proposed_argv'),
                         'reported_lifecycle_invocations': len(report.get('executed_lifecycle_argv', [])),
                         'observation_scope': report.get('observation_scope'),
                         'identity_fields': sorted(identity), 'launch_fields': sorted(capture)})
    return {'schema_version': 'ai-engineering-archive-audit@1',
            'repository': 'ed3c/soodles', 'revision': revision,
            'mode': 'retrospective_archive_review', 'sources': sources, 'observations': rows,
            'complete_platform_transcript': provenance['complete_platform_transcript'],
            'fresh_coding_model_runs': 0, 'quality_verdict': None,
            'authorizes_landing': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--soodles', type=Path, required=True)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.soodles.resolve(), args.revision)
    args.out.mkdir(parents=True, exist_ok=False)
    (args.out / 'archive-audit.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': 'SOURCE_BYTES_VERIFIED', 'reports': len(result['observations']),
                      'out': str(args.out), 'quality_verdict': None}))


if __name__ == '__main__':
    main()
