#!/usr/bin/env python3
"""Replay this issue's real article update and a separate planted CLI control.

No model, network, repository mutation, or Medium publication. --out must be new.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
BASE = '3876cbbf1cff627647e2c3c6c13ffda80fa8c1c0'
BEFORE_BLOB = 'aed314c86ef9bf6af33af95a9f193b86be9b9f79'
LOG = []


def sha(path):
    return 'sha256:' + hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def call(cli, *args, expected=0):
    argv = [sys.executable, str(cli), *map(str, args)]
    p = subprocess.run(argv, text=True, capture_output=True, timeout=20)
    LOG.append({'argv': argv, 'exit': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr})
    if p.returncode != expected:
        raise RuntimeError(f'expected exit {expected}, got {p.returncode}: {p.stderr}')
    return json.loads(p.stdout) if p.stdout else None


def planted(cli, root, expected):
    """Same fixture and mutation for old/new CLI. This is not a fresh writer run."""
    root.mkdir(parents=True)
    write(root/'spec.json', {'topic': 'guard-control', 'claims': [], 'terms': []})
    run = root/'run'
    call(cli, 'init', '--spec', root/'spec.json', '--run-dir', run)
    elements = [
        ['toc', 'decision_map', 'runtime_map'],
        ['problem', 'governing_property', 'representation'],
        ['runtime_witness', 'internals'],
        ['alternative', 'decision_boundary', 'complexity'],
        ['implementation', 'correctness', 'edge_cases'],
        ['interview', 'master_map'], ['copyedit'],
    ]
    for stage in range(7):
        text = f'Stage {stage} control\n'
        if stage == 4:
            text += '\n```python\nprint("protected")\n```\n'
        if stage == 6:
            text = (run/'semantic-draft.md').read_text()
        (root/'part.md').write_text(text)
        write(root/'coverage.json', {'elements': elements[stage], 'claims': [], 'terms': []})
        call(cli, 'submit', '--run-dir', run, '--stage', stage,
             '--input', root/'part.md', '--coverage', root/'coverage.json')
    call(cli, 'assemble', '--run-dir', run)
    call(cli, 'verify', '--run-dir', run)
    for name in ('parts/stage-06.md', 'medium-canonical.md'):
        p = run/name
        p.write_text(p.read_text().replace('print("protected")', 'print("changed")'))
    call(cli, 'verify', '--run-dir', run, expected=expected)
    return {'fixture': 'same post-admission code mutation', 'verify_exit': expected}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--baseline-cli', type=Path)
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    cli = ROOT/'medium_compiler.py'
    before = Path(__file__).with_name('before.md')
    after = ROOT/'articles/ai-engineer-learning-path.md'
    raw = before.read_bytes()
    blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    assert blob == BEFORE_BLOB, 'wrong retained article baseline'
    review = json.loads(Path(__file__).with_name('edit-review.json').read_text())
    rebuilt = raw.decode()
    for edit in review['edits']:
        assert rebuilt.count(edit['before']) == 1
        rebuilt = rebuilt.replace(edit['before'], edit['after'], 1)
    assert rebuilt.encode() == after.read_bytes(), 'change outside the four reviewed spans'
    spec = {
        'topic': 'AI Engineer learning path: bounded prose edit',
        'claims': [{'id': 'C1', 'stage': 1, 'description': 'preserve factual boundaries',
                    'protected_literals': ['引用存在，不足以證明回答忠於引用。',
                                           '2 GiB', '不代表已測試真實 LLM 的回答品質',
                                           'O(M + K + V + R + C)']}],
        'terms': [{'id': 'T1', 'first_stage': 1, 'canonical': 'behavior hill climb'},
                  {'id': 'T2', 'first_stage': 1, 'canonical': 'KV cache'}],
    }
    write(out/'spec.json', spec)
    write(out/'coverage.json', {'elements': ['copyedit'], 'claims': [], 'terms': []})
    run = out/'run'
    call(cli, 'init', '--spec', out/'spec.json', '--draft', before, '--run-dir', run)
    assert call(cli, 'next', '--run-dir', run)['next_stage'] == 6
    call(cli, 'submit', '--run-dir', run, '--stage', 6,
         '--input', after, '--coverage', out/'coverage.json')
    call(cli, 'assemble', '--run-dir', run)
    call(cli, 'verify', '--run-dir', run)
    call(cli, 'check-receipt', '--run-dir', run)
    proof = call(cli, 'prove-update', '--run-dir', run, '--issue', 1,
                 '--before', before, '--after', after, '--output', out/'article-update.json')
    assert call(cli, 'next', '--run-dir', run)['next'] is None
    # Actual canonical article, not a toy string, must match the submitted update.
    assert (run/'medium-canonical.md').read_bytes() == after.read_bytes()
    negative = out/'negative'
    shutil.copytree(run, negative)
    for name in ('parts/stage-06.md', 'medium-canonical.md'):
        p = negative/name
        p.write_text(p.read_text().replace('return {"status": "candidate"',
                                           'return {"status": "verified"'))
    call(cli, 'verify', '--run-dir', negative, expected=2)
    candidate_control = planted(cli, out/'candidate-control', 2)
    baseline_control = None
    if args.baseline_cli:
        baseline_control = planted(args.baseline_cli.resolve(), out/'baseline-control', 0)
    tests = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v'],
                           cwd=ROOT, text=True, capture_output=True, timeout=30)
    (out/'tests.txt').write_text(tests.stdout + tests.stderr)
    assert tests.returncode == 0
    # Match edit scope and unchanged formal material using separate simple comparisons.
    import re
    fences = lambda text: re.findall(r'(?ms)^```[^\n]*\n.*?^```[ \t]*$', text)
    digits = lambda text: re.findall(r'\d+(?:[.,]\d+)*', text)
    assert fences(before.read_text()) == fences(after.read_text())
    assert digits(before.read_text()) == digits(after.read_text())
    result = {
        'issue': 1, 'source_commit': BASE, 'before_git_blob': BEFORE_BLOB,
        'before_sha256': sha(before), 'after_sha256': sha(after), 'compiler_sha256': sha(cli),
        'skill_sha256': sha(ROOT/'SKILL.md'), 'real_article_changed': True,
        'changed_prose_spans': len(review['edits']),
        'unchanged_fenced_blocks': len(fences(before.read_text())),
        'digit_tokens_unchanged': True, 'all_other_text_exact': True,
        'article_update_proof': proof,
        'baseline_planted_control': baseline_control, 'candidate_planted_control': candidate_control,
        'unit_test_exit': tests.returncode,
        'semantic_review': 'AUTHOR_REVIEW_OF_FOUR_SPANS; NOT_INDEPENDENT',
        'fresh_writer_ab': 'NOT_RUN', 'independent_reader': 'NOT_RUN',
        'medium_publication': 'NOT_REQUESTED_OR_PERFORMED',
        'conclusion': 'SCOPED_DETERMINISTIC_CORRECTION_AND_REAL_ARTICLE_UPDATE',
    }
    write(out/'execution.json', result)
    write(out/'command-log.json', {'commands': LOG})
    print(json.dumps({k: result[k] for k in ['changed_prose_spans', 'unchanged_fenced_blocks',
                                            'unit_test_exit', 'conclusion']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
