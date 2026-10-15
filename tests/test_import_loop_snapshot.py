import copy
import hashlib
import html
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from test_loop_site import fixture, site


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / 'scripts/import_loop_snapshot.py'


class ImportLoopSnapshotTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.folder = self.root / 'reports/loops'
        self.folder.mkdir(parents=True)
        self.catalog = self.folder / 'catalog.json'
        self.catalog.write_bytes(b'{"schema_version": 1, "snapshots": []}\n')
        self.source = self.root / 'owner reviewed snapshot.json'
        self.raw = self.write_source(fixture())

    def write_source(self, value):
        raw = ('\n' + json.dumps(value, ensure_ascii=False, indent=3) + '\n\n').encode('utf-8')
        self.source.write_bytes(raw)
        return raw

    def cli(self, snapshot_id='reviewed'):
        return subprocess.run(
            [sys.executable, str(CLI), '--snapshot', str(self.source),
             '--id', snapshot_id, '--root', str(self.root)],
            cwd=self.root, capture_output=True, text=True, check=False,
        )

    def stored_bytes(self):
        return {str(path.relative_to(self.root)): path.read_bytes()
                for path in self.folder.rglob('*') if path.is_file()}

    def refuse(self, snapshot_id='reviewed', error=None):
        before = self.stored_bytes()
        result = self.cli(snapshot_id)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertEqual(result.stdout, '')
        report = json.loads(result.stderr)
        self.assertEqual(report['status'], 'REFUSED')
        self.assertTrue(report['error'])
        if error:
            self.assertIn(error, report['error'])
        self.assertEqual(self.stored_bytes(), before)

    def add_existing(self, name, value):
        raw = json.dumps(value).encode('utf-8')
        (self.folder / (name + '.json')).write_bytes(raw)
        entry = {'path': 'reports/loops/' + name + '.json',
                 'sha256': hashlib.sha256(raw).hexdigest()}
        catalog = json.loads(self.catalog.read_bytes())
        catalog['snapshots'].append(entry)
        self.catalog.write_text(json.dumps(catalog))
        return entry

    def test_first_import_preserves_original_bytes_and_renderer_content(self):
        result = self.cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        digest = hashlib.sha256(self.raw).hexdigest()
        self.assertEqual(json.loads(result.stdout), {
            'status': 'IMPORTED', 'id': 'reviewed', 'path': 'reports/loops/reviewed.json',
            'sha256': digest, 'run_ids': ['test-only-run'],
        })
        self.assertEqual(result.stderr, '')
        self.assertEqual((self.folder / 'reviewed.json').read_bytes(), self.raw)
        self.assertEqual(self.source.read_bytes(), self.raw)
        self.assertEqual(json.loads(self.catalog.read_bytes()), {
            'schema_version': 1, 'snapshots': [
                {'path': 'reports/loops/reviewed.json', 'sha256': digest}],
        })
        out = self.root / 'rendered'
        out.mkdir()
        provenance = site.render_loops(self.root, out, lambda title, body, active: body)
        self.assertEqual(provenance, [{
            'route': '/loops/test-only-run/', 'snapshot_sha256': digest,
            'repository': 'example/repository', 'mode': 'single', 'status': 'NOT_RUN',
        }])
        rendered = (out / 'loops/test-only-run/index.html').read_text()
        run = fixture()['runs'][0]
        for text in (run['stages'][0]['prompt'], run['cards'][0]['title'],
                     run['cards'][0]['body'], run['notes'][0]['body'],
                     run['breakpoints'][0]['message'], 'UNKNOWN', 'Consumer：NOT_RUN'):
            self.assertIn(html.escape(text), rendered)

    def test_same_bytes_are_noop_without_rewriting_files(self):
        self.assertEqual(self.cli().returncode, 0)
        before = self.stored_bytes()
        stats = {path: path.stat().st_mtime_ns for path in self.folder.iterdir()}
        result = self.cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['status'], 'NOOP')
        self.assertEqual(self.stored_bytes(), before)
        self.assertEqual({path: path.stat().st_mtime_ns for path in self.folder.iterdir()}, stats)

    def test_same_id_with_different_bytes_refuses(self):
        self.assertEqual(self.cli().returncode, 0)
        self.source.write_bytes(self.raw + b' ')
        self.refuse(error='Conflicting')

    def test_invalid_and_private_snapshots_refuse(self):
        self.add_existing('existing', fixture())
        values = [{}, {'schema_version': 2, 'runs': []}]
        for private in ('/Users/person/private', 'API_KEY=not-public'):
            value = fixture()
            value['runs'][0]['stages'][0]['prompt'] = private
            values.append(value)
        value = fixture()
        value['runs'][0]['environment'] = {'TOKEN': 'not-public'}
        values.append(value)
        value = fixture()
        value['runs'][0]['breakpoints'][0]['stage_id'] = []
        values.append(value)
        for value in values:
            with self.subTest(value=value):
                self.write_source(value)
                self.refuse()
        self.source.write_bytes(b'{invalid json')
        self.refuse()

    def test_unsafe_and_reserved_ids_refuse(self):
        for snapshot_id in ('../escape', '/absolute', 'a/b', 'a\\b', '.', '..', '',
                            'space name', 'catalog', 'CATALOG'):
            with self.subTest(snapshot_id=snapshot_id):
                self.refuse(snapshot_id)
        self.assertFalse((self.root / 'escape.json').exists())

    def test_duplicate_run_ids_within_input_and_across_catalog_refuse(self):
        value = fixture()
        value['runs'].append(copy.deepcopy(value['runs'][0]))
        self.write_source(value)
        self.refuse(error='Duplicate public Loop run ID')
        self.write_source(fixture())
        self.add_existing('existing', fixture())
        self.refuse(error='Duplicate public Loop run across snapshots')

    def test_existing_duplicate_run_ids_refuse_even_on_noop(self):
        self.assertEqual(self.cli().returncode, 0)
        self.add_existing('duplicate', fixture())
        self.refuse(error='Duplicate public Loop run across snapshots')

    def test_existing_catalog_digest_drift_refuses_new_import_and_noop(self):
        self.assertEqual(self.cli().returncode, 0)
        value = fixture()
        value['runs'][0]['id'] = 'another-run'
        self.add_existing('existing', value)
        (self.folder / 'existing.json').write_bytes(b'{}')
        self.refuse(error='hash mismatch')
        self.write_source(value)
        self.refuse('new-snapshot', error='hash mismatch')

    def test_snapshot_only_interruption_recovers_existing_catalog(self):
        value = fixture()
        value['runs'][0]['id'] = 'another-run'
        entry = self.add_existing('existing', value)
        destination = self.folder / 'reviewed.json'
        destination.write_bytes(self.raw)
        before = destination.stat().st_mtime_ns
        result = self.cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['status'], 'RECOVERED')
        self.assertEqual(destination.read_bytes(), self.raw)
        self.assertEqual(destination.stat().st_mtime_ns, before)
        self.assertEqual(json.loads(self.catalog.read_bytes())['snapshots'], [entry, {
            'path': 'reports/loops/reviewed.json', 'sha256': hashlib.sha256(self.raw).hexdigest(),
        }])
        self.assertEqual(json.loads(self.cli().stdout)['status'], 'NOOP')

    def test_snapshot_only_with_different_bytes_refuses(self):
        (self.folder / 'reviewed.json').write_bytes(self.raw + b' ')
        self.refuse(error='different bytes')

    def test_catalog_only_missing_snapshot_is_not_recovered(self):
        self.assertEqual(self.cli().returncode, 0)
        (self.folder / 'reviewed.json').unlink()
        self.refuse(error='No such file')

    def test_invalid_catalog_and_escaping_source_paths_refuse(self):
        catalogs = [
            {'schema_version': True, 'snapshots': []},
            {'schema_version': 1, 'snapshots': [], 'extra': True},
            {'schema_version': 1, 'snapshots': 'invalid'},
        ]
        for path in ('../owner reviewed snapshot.json', str(self.source), 'source.json'):
            catalogs.append({'schema_version': 1, 'snapshots': [
                {'path': path, 'sha256': hashlib.sha256(self.raw).hexdigest()}]})
        for catalog in catalogs:
            with self.subTest(catalog=catalog):
                self.catalog.write_text(json.dumps(catalog))
                self.refuse()

    def test_duplicate_catalog_paths_refuse_even_with_no_runs(self):
        entry = self.add_existing('empty', {'schema_version': 1, 'runs': []})
        self.catalog.write_text(json.dumps({'schema_version': 1, 'snapshots': [entry, entry]}))
        self.refuse(error='Duplicate public Loop snapshot path')

    def test_symlink_destination_and_catalog_refuse_without_touching_targets(self):
        destination = self.folder / 'reviewed.json'
        destination.symlink_to(self.source)
        self.refuse(error='symlink')
        self.assertEqual(self.source.read_bytes(), self.raw)
        destination.unlink()
        original = self.catalog.read_bytes()
        target = self.root / 'catalog-target.json'
        target.write_bytes(original)
        self.catalog.unlink()
        self.catalog.symlink_to(target)
        self.refuse(error='symlink')
        self.assertEqual(target.read_bytes(), original)


if __name__ == '__main__':
    unittest.main()
