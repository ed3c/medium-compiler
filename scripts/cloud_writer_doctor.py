#!/usr/bin/env python3
"""No-model cloud preflight. Evidence of prerequisites, never a host approval.

Uses the existing writer doctor plus harmless, generated sandbox canaries. Receives
only the boolean that a named GitHub secret is configured; never receives its value.
No package installation, authentication, production writes or model calls here.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

from run_writer_pair import doctor

ROOT = Path(__file__).resolve().parents[1]
PROBE = r'''
import json, pathlib, sys
outside = pathlib.Path(sys.argv[1])
def attempt(fn):
    try:
        fn()
        return {"allowed": True}
    except OSError as exc:
        return {"allowed": False, "errno": exc.errno}
result = {
    "read_other_arm": attempt(lambda: (outside / "other-arm.txt").read_bytes()),
    "overwrite_recorder": attempt(lambda: (outside / "recorder.txt").write_text("changed")),
    "write_workspace": attempt(lambda: pathlib.Path("allowed.txt").write_text("allowed")),
}
print(json.dumps(result))
'''


def write(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def classification(cli: dict, sandbox: dict, configured: str) -> dict:
    if configured not in {'true', 'false'}:
        raise ValueError('credential presence must be exactly true or false; never pass a key')
    missing = []
    if cli.get('status') != 'EXECUTABLE_FOUND_NOT_QUALIFIED':
        missing.extend(cli.get('missing') or ['codex_executable_compatibility'])
    if configured == 'false':
        missing.append('configured_model_authentication')
    # These canaries test only this default native sandbox, NOT full-host qualification.
    observed = sandbox.get('observed')
    if not isinstance(observed, dict):
        missing.append('native_sandbox_probe')
    elif observed.get('read_other_arm', {}).get('allowed') is not False:
        missing.append('cross_arm_read_isolation')
    if not isinstance(observed, dict) or observed.get('overwrite_recorder', {}).get('allowed') is not False:
        missing.append('recorder_write_isolation')
    if not isinstance(observed, dict) or observed.get('write_workspace', {}).get('allowed') is not True:
        missing.append('workspace_write_capability')
    # Passing a few canaries cannot auto-sign an isolation/identity/authentication claim.
    missing.append('qualified_host_and_external_pilot_review')
    return {
        'status': 'BLOCKED',
        'scope': 'cloud executable and bounded canary observation only',
        'missing': missing,
        'configured_secret': {'name': 'OPENAI_API_KEY', 'present': configured == 'true',
                              'value_received': False, 'authentication_tested': False},
        'host_approval_created': False,
        'model_calls': 0, 'pilot': 'NOT_RUN', 'fresh_writer_ab': 'NOT_RUN',
        'independent_reader': 'NOT_RUN', 'behavior': None,
        'authorizes_landing': False, 'authorizes_product_write': False,
    }


def run(codex: str, out: Path, configured: str) -> dict:
    if configured not in {'true', 'false'}:
        raise ValueError('only a credential-presence boolean is accepted')
    out = out.absolute()
    if out.exists() or out.resolve().is_relative_to(ROOT):
        raise ValueError('output must be new and outside the checkout')
    if any(p.is_symlink() for p in [out, *out.parents]):
        raise ValueError('symlinked output is not allowed')
    out.mkdir(parents=True)
    commands = []
    with tempfile.TemporaryDirectory(prefix='medium-cloud-canary-') as td:
        root = Path(td); capsule = root / 'capsule'; outside = root / 'outside'; home = root / 'home'
        for path in [capsule, outside, home, home / '.codex']:
            path.mkdir()
        (capsule / 'probe.py').write_text(PROBE)
        (outside / 'other-arm.txt').write_text('SYNTHETIC OUTSIDE-ARM SENTINEL; not user data\n')
        (outside / 'recorder.txt').write_text('SYNTHETIC PROTECTED RECORDER\n')
        original = (outside / 'recorder.txt').read_bytes()
        env = {'PATH': os.environ.get('PATH', '/usr/bin:/bin'), 'HOME': str(home),
               'CODEX_HOME': str(home / '.codex'), 'LANG': 'C.UTF-8',
               'PYTHONDONTWRITEBYTECODE': '1'}
        def call(argv: list[str], cwd: Path = capsule) -> dict:
            try:
                proc = subprocess.run(argv, cwd=cwd, env=env, capture_output=True,
                                      text=True, timeout=25)
                result = {'argv': argv, 'exit': proc.returncode,
                          'stdout': proc.stdout, 'stderr': proc.stderr}
            except subprocess.TimeoutExpired as exc:
                result = {'argv': argv, 'exit': None, 'error': 'timeout',
                          'stdout': (exc.stdout or b'').decode(errors='replace') if isinstance(exc.stdout, bytes) else (exc.stdout or ''),
                          'stderr': (exc.stderr or b'').decode(errors='replace') if isinstance(exc.stderr, bytes) else (exc.stderr or '')}
            commands.append(result); write(out / 'commands.json', {'commands': commands})
            return result
        control = call([sys.executable, 'probe.py', str(outside)])
        (outside / 'recorder.txt').write_bytes(original)
        (capsule / 'allowed.txt').unlink(missing_ok=True)
        # existing doctor only runs --version/exec --help; it does not inspect auth files
        cli = doctor(codex); write(out / 'doctor.json', cli)
        sandbox = {'status': 'NOT_RUN', 'observed': None}
        binary = cli.get('codex')
        if binary:
            call([binary, 'sandbox', 'linux', '--help'])
            result = call([binary, 'sandbox', 'linux', '-c', 'sandbox_mode="workspace-write"',
                           '-c', 'sandbox_workspace_write.network_access=false', '--',
                           sys.executable, 'probe.py', str(outside)])
            if result['exit'] == 0:
                try:
                    value = json.loads(result['stdout'])
                    if isinstance(value, dict) and set(value) == {'read_other_arm', 'overwrite_recorder', 'write_workspace'}:
                        sandbox = {'status': 'OBSERVED', 'observed': value}
                except json.JSONDecodeError:
                    pass
            sandbox['recorder_unchanged'] = (outside / 'recorder.txt').read_bytes() == original
            sandbox['workspace_file_created'] = (capsule / 'allowed.txt').is_file()
        report = classification(cli, sandbox, configured)
        report.update({'schema_version': 'writer-cloud-preflight@1',
                       'checked_at': datetime.now(timezone.utc).isoformat(),
                       'git_commit': subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip(),
                       'runner': {k: os.environ.get(k) for k in ('GITHUB_RUN_ID', 'GITHUB_RUN_ATTEMPT', 'RUNNER_OS', 'RUNNER_ARCH')},
                       'doctor_status': cli.get('status'), 'codex_version': cli.get('version'),
                       'codex_sha256': cli.get('codex_sha256'),
                       'unsandboxed_control': control, 'native_workspace_sandbox': sandbox,
                       'controller_sha256': 'sha256:' + hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
    report['canary_scratch_cleaned'] = not root.exists()
    write(out / 'report.json', report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return report


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--codex', required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--credential-configured', choices=['true', 'false'], required=True)
    args = p.parse_args()
    run(args.codex, args.out, args.credential_configured)
    return 3  # qualification / model invocation is a separate, still-required operation


if __name__ == '__main__':
    raise SystemExit(main())
