import importlib.util
from pathlib import Path
import tempfile
import unittest

P=Path(__file__).resolve().parents[1]/'scripts/learning_duckdb_agent.py'
spec=importlib.util.spec_from_file_location('learning_cli',P)
cli=importlib.util.module_from_spec(spec)
spec.loader.exec_module(cli)
class LearningCliTests(unittest.TestCase):
    def test_bounded_readonly_agent_command(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'test.duckdb'
            path.write_bytes(b'fixture')
            argv=cli.build_command(str(path))
            self.assertEqual(argv[1:3],['-agent','-readonly'])
            self.assertIn('enable_external_access = false',argv[-1])
            self.assertIn('LIMIT 100',argv[-1])
            self.assertNotIn('ATTACH ',argv[-1])
    def test_path_and_binary_adversarial_inputs(self):
        with tempfile.TemporaryDirectory() as folder:
            d=Path(folder)
            file=d/'valid.duckdb';file.write_bytes(b'fixture')
            symlink=d/'alias.duckdb';symlink.symlink_to(file)
            with self.assertRaises(ValueError):cli.build_command(symlink)
            with self.assertRaises(ValueError):cli.build_command(file, 'duckdb;rm')
            with self.assertRaises(ValueError):cli.build_command(d/'wrong.json')
if __name__=='__main__':unittest.main()
