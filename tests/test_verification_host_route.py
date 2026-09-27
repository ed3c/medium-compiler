"""Mechanism controls, not fresh native writer/reader evidence."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
ENTRY = ROOT / '.agents/skills/verify-medium/scripts/verify.py'


class VerificationHostRouteTests(unittest.TestCase):
    def run_entry(self, feature, with_codex):
        with tempfile.TemporaryDirectory(prefix='verify-host-route-') as tmp:
            temp = Path(tmp)
            binary_dir = temp / 'bin'
            binary_dir.mkdir()
            marker = temp / 'codex-was-invoked'
            if with_codex:
                trap = binary_dir / 'codex'
                trap.write_text('#!' + sys.executable + '\n'
                                'from pathlib import Path\n'
                                'Path(' + repr(str(marker)) + ').write_text("unexpected probe")\n'
                                'raise SystemExit(9)\n')
                trap.chmod(0o755)
            env = dict(os.environ, PATH=str(binary_dir), PYTHONDONTWRITEBYTECODE='1')
            result = subprocess.run([sys.executable, str(ENTRY), '--feature', feature,
                                     '--out', str(temp / 'evidence')],
                                    env=env, capture_output=True, text=True, timeout=30)
            self.assertFalse(marker.exists(), 'verification selected a Local Codex probe')
            self.assertEqual(result.returncode, 3 if feature == 'behavior-evals' else 0,
                             result.stderr + result.stdout)
            report = json.loads(result.stdout)
            commands = json.loads((temp / 'evidence/commands.json').read_text())['commands']
            self.assertTrue(commands, 'real compiler doctor did not execute')
            self.assertTrue(all(Path(c['argv'][1]).name == 'medium_compiler.py'
                                for c in commands))
            return report

    def test_behavior_with_codex_on_path_does_not_probe_it(self):
        report = self.run_entry('behavior-evals', True)
        self.assertEqual(report['outcome'], 'blocked')
        self.assertIsNone(report['features']['behavior-evals']['behavior'])

    def test_behavior_without_codex_preserves_unknown_evidence(self):
        report = self.run_entry('behavior-evals', False)
        row = report['features']['behavior-evals']
        self.assertEqual(row['fresh_writer_ab'], 'NOT_RUN')
        self.assertEqual(row['independent_reader'], 'NOT_RUN')
        self.assertEqual(row['model_calls'], 0)
        self.assertNotIn('runner_probe', row)

    def test_repository_doctor_is_not_an_agent_carrier_check(self):
        report = self.run_entry('doctor', True)
        self.assertEqual(report['features']['doctor']['status'], 'PASS')
        self.assertNotIn('codex_executable', report['features']['doctor'])

    def test_behavior_report_cannot_launch_any_subprocess_or_detect_native_tools(self):
        spec = importlib.util.spec_from_file_location('native_route_verify', ENTRY)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(
                module.subprocess, 'run', side_effect=AssertionError('unexpected launch')):
            row = module.Driver(Path(tmp)).behavior()
        self.assertEqual(row['status'], 'BLOCKED')
        self.assertIsNone(row['behavior'])
        self.assertEqual(row['capability_observation'],
                         'HOST_SESSION_OWNED; not probed by this verifier')
