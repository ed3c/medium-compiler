#!/usr/bin/env python3
"""Black-box CLI control. These subprocesses are NOT fresh model/Agent sessions."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ELEMENTS = {
    0: ['toc', 'decision_map', 'runtime_map'],
    1: ['problem', 'governing_property', 'representation'],
    2: ['runtime_witness', 'internals'],
    3: ['alternative', 'decision_boundary', 'complexity'],
    4: ['implementation', 'correctness', 'edge_cases'],
    5: ['interview', 'master_map'], 6: ['copyedit'],
}


def digest(data):
    return 'sha256:' + hashlib.sha256(data).hexdigest()


def snapshot(root):
    return {str(p.relative_to(root)): digest(p.read_bytes())
            for p in root.rglob('*') if p.is_file()}


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def scenario(cli, out, target, arm):
    out.mkdir()
    run = out/'run'
    trace = []
    def call(*args, expected=0):
        result = subprocess.run([sys.executable, str(cli), *map(str, args)],
                                capture_output=True, text=True, encoding='utf-8', timeout=20)
        try:
            output = json.loads(result.stdout)
        except json.JSONDecodeError:
            output = None
        trace.append({'argv': [str(a).replace(str(out), '<case>') for a in args],
                      'exit_code': result.returncode,
                      'stdout_sha256': digest(result.stdout.encode()),
                      'stderr': result.stderr.replace(str(out), '<case>'),
                      'observed_next': output.get('next') if isinstance(output, dict) else None})
        if result.returncode != expected:
            raise AssertionError(f'{args}: expected {expected}, got {result.returncode}: {result.stderr}')
        return output

    spec = out/'spec.json'
    write_json(spec, {'topic': 'Synthetic CLI control, not a published article',
                     'claims': [{'id': f'C{i}', 'stage': i, 'description': f'fixture {i}',
                                 'protected_literals': [f'exact-{i}']} for i in range(1, 6)],
                     'terms': []})
    inputs = {}
    for i in range(7):
        text = '# Plan\n\nSynthetic map.\n' if i == 0 else f'## Fixture {i}\n\nexact-{i}\n'
        if i == 4:
            text += '\n```python\nvalue = 1\n```\n'
        inputs[i] = out/f'input-{i}.md'
        inputs[i].write_text(text, encoding='utf-8')
        write_json(out/f'coverage-{i}.json', {'elements': ELEMENTS[i],
                                            'claims': [f'C{i}'] if i in range(1, 6) else [], 'terms': []})
    call('init', '--spec', spec, '--run-dir', run)
    for i in range(6):
        call('submit', '--run-dir', run, '--stage', i, '--input', inputs[i], '--coverage', out/f'coverage-{i}.json')
    before = snapshot(run)
    frozen_before = (run/'semantic-draft.md').read_bytes()
    call('next', '--run-dir', run)
    observed = {'arm': arm, 'target_stage': target, 'fixture': 'synthetic', 'trace': trace}
    if target is not None:
        operation = call('reopen', '--run-dir', run, '--stage', target,
                         expected=2 if arm == 'baseline' else 0)
        if arm == 'baseline':
            assert before == snapshot(run), 'missing operation must not change the run'
            observed.update(result='MISSING_OPERATION', run_unchanged=True)
            return observed
        observed['reopen_output'] = operation
        assert operation['target_stage'] == target
        current = snapshot(run)
        retained = {name: sha for name, sha in before.items()
                    if name == 'spec.json' or any(name.startswith(f'parts/stage-{i:02d}.') for i in range(target))}
        assert all(current.get(name) == sha for name, sha in retained.items())
        assert 'semantic-draft.md' not in current
        next_step = call('next', '--run-dir', run)
        assert next_step['next'] == 'submit' and next_step['next_stage'] == target
        text = inputs[target].read_text(encoding='utf-8')
        inputs[target].write_text(text.replace('value = 1', 'value = 2') if target == 4
                                  else text + '\nSynthetic governing-property clarification.\n', encoding='utf-8')
        for i in range(target, 6):
            call('submit', '--run-dir', run, '--stage', i, '--input', inputs[i], '--coverage', out/f'coverage-{i}.json')
        observed['prefix_unchanged'] = True
    copyedit = (run/'semantic-draft.md').read_text(encoding='utf-8')
    if target is None:
        copyedit = copyedit.replace('## Fixture 1', '## Introduction')
    inputs[6].write_text(copyedit, encoding='utf-8')
    call('submit', '--run-dir', run, '--stage', 6, '--input', inputs[6], '--coverage', out/'coverage-6.json')
    call('assemble', '--run-dir', run)
    call('verify', '--run-dir', run)
    assert call('check-receipt', '--run-dir', run)['status'] == 'VALID'
    terminal = call('next', '--run-dir', run)
    assert terminal['next'] is None and terminal['semantic_correctness'] == 'NOT_ASSESSED'
    final = (run/'medium-canonical.md').read_bytes()
    assert final == (run/'parts/stage-06.md').read_bytes()
    assert final != frozen_before
    observed.update(result='VALIDATED', canonical_equals_admitted_stage6=True,
                    terminal_next=None, semantic_correctness='NOT_ASSESSED')
    return observed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline-cli', required=True, type=Path)
    parser.add_argument('--candidate-cli', type=Path, default=Path(__file__).resolve().parents[2]/'medium_compiler.py')
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    # mkdir(exist_ok=False): never overwrite previous evidence or repository files.
    args.out.mkdir(parents=True, exist_ok=False)
    result = {'experiment_type': 'DETERMINISTIC_CLI_CONTROL',
              'baseline_commit': '6b9b24f35c8f3271ff04673efad337db2e60371f',
              'baseline_cli_sha256': digest(args.baseline_cli.read_bytes()),
              'candidate_cli_sha256': digest(args.candidate_cli.read_bytes()),
              'natural_agent_behavior': 'NOT_RUN', 'real_article_update': 'NOT_PERFORMED',
              'cases': []}
    for arm, cli in [('baseline', args.baseline_cli.resolve()), ('candidate', args.candidate_cli.resolve())]:
        for label, target in [('semantic-1', 1), ('semantic-4', 4), ('prose-only', None)]:
            result['cases'].append(scenario(cli, args.out/f'{arm}-{label}', target, arm))
    result['status'] = 'PASS'
    write_json(args.out/'result.json', result)
    print(json.dumps({k: v for k, v in result.items() if k != 'cases'}, indent=2))


if __name__ == '__main__':
    main()
