#!/usr/bin/env python3
"""Replay this article's actual staged inputs through the unchanged writing CLI."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def main():
    p = argparse.ArgumentParser(); p.add_argument('--out', type=Path, required=True)
    args = p.parse_args(); args.out.mkdir(parents=True, exist_ok=False)
    sys.path.insert(0, str(ROOT))
    from medium_compiler import STAGE_ELEMENTS
    claims = [
        ('C1', 1, 'Source analogy and the author\'s acceptance-based interpretation remain distinct.', ['2005', '驗收條件']),
        ('C2', 2, 'The hypothetical A-to-B change invalidates mismatched evidence.', ['候選 B', '假設案例']),
        ('C3', 3, 'Compare alternatives with all failed-attempt costs included.', ['C / A', 'A 為零']),
        ('C4', 4, 'Version checks do not establish check adequacy or publishing authority.', ['不會自行擴張']),
        ('C5', 5, 'No audio verification or whole-episode translation is claimed.', ['沒有逐句核對原始音訊']),
    ]
    spec = {'topic': 'Agent primitives and product differentiation', 'claims': [
        {'id': key, 'stage': stage, 'description': desc, 'protected_literals': literals}
        for key, stage, desc, literals in claims], 'terms': []}
    spec_path = args.out/'spec.json'; spec_path.write_text(json.dumps(spec, ensure_ascii=False, indent=2)+'\n')
    run = args.out/'run'; commands = []

    def invoke(*argv):
        command = [sys.executable, str(ROOT/'medium_compiler.py'), *map(str, argv)]
        r = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        commands.append({'argv': command, 'exit': r.returncode, 'stdout': r.stdout, 'stderr': r.stderr})
        (args.out/'commands.json').write_text(json.dumps(commands, ensure_ascii=False, indent=2)+'\n')
        if r.returncode:
            raise RuntimeError(r.stderr)

    invoke('init', '--spec', spec_path, '--run-dir', run)
    for stage in range(7):
        invoke('next', '--run-dir', run)
        coverage = {'elements': list(STAGE_ELEMENTS[stage]),
                    'claims': [c[0] for c in claims if c[1] == stage], 'terms': []}
        cov = args.out/f'stage-{stage:02d}.coverage.json'
        cov.write_text(json.dumps(coverage)+'\n')
        if stage == 6:
            source = run/'semantic-draft.md'  # Reviewed unchanged; no fabricated rewrite.
        else:
            source = HERE/f'stage-{stage:02d}.md'
        invoke('submit', '--run-dir', run, '--stage', stage, '--input', source, '--coverage', cov)
    invoke('assemble', '--run-dir', run)
    invoke('verify', '--run-dir', run)
    invoke('check-receipt', '--run-dir', run)
    invoke('next', '--run-dir', run)
    final = (run/'medium-canonical.md').read_bytes()
    print(json.dumps({'article_sha256': hashlib.sha256(final).hexdigest(), 'canonical': str(run/'medium-canonical.md')}))


if __name__ == '__main__':
    main()
