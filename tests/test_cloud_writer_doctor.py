"""Controls for evidence classification. No model/cloud claims from these fixtures."""
import sys
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from cloud_writer_doctor import classification

class CloudDoctorTests(unittest.TestCase):
    def setUp(self):
        self.cli = {'status': 'EXECUTABLE_FOUND_NOT_QUALIFIED', 'missing': []}
        self.probe = {'observed': {'read_other_arm': {'allowed': False},
                                  'overwrite_recorder': {'allowed': False},
                                  'write_workspace': {'allowed': True}}}

    def test_perfect_canaries_do_not_create_host_approval(self):
        result = classification(self.cli, self.probe, 'true')
        self.assertEqual(result['status'], 'BLOCKED')
        self.assertEqual(result['model_calls'], 0)
        self.assertFalse(result['host_approval_created'])
        self.assertFalse(result['configured_secret']['authentication_tested'])
        self.assertIsNone(result['behavior'])

    def test_absent_named_secret_is_explicit(self):
        self.assertIn('configured_model_authentication', classification(self.cli, self.probe, 'false')['missing'])

    def test_read_access_cannot_be_misreported_as_isolation(self):
        self.probe['observed']['read_other_arm']['allowed'] = True
        self.assertIn('cross_arm_read_isolation', classification(self.cli, self.probe, 'true')['missing'])

    def test_crashed_probe_is_not_successful_denial(self):
        result = classification(self.cli, {'observed': None}, 'false')
        self.assertIn('native_sandbox_probe', result['missing'])
        self.assertIn('workspace_write_capability', result['missing'])

    def test_actual_key_is_never_a_supported_argument(self):
        with self.assertRaises(ValueError):
            classification(self.cli, self.probe, 'not-a-boolean')

    def test_unsupported_cli_is_not_a_fresh_run(self):
        self.cli = {'status': 'BLOCKED', 'missing': ['cli_flag:--ephemeral']}
        result = classification(self.cli, self.probe, 'true')
        self.assertIn('cli_flag:--ephemeral', result['missing'])
        self.assertEqual(result['fresh_writer_ab'], 'NOT_RUN')

if __name__ == '__main__':
    unittest.main()
