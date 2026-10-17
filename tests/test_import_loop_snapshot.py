import copy
import fcntl
import hashlib
import html
import json
import os
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

    def cli(self, snapshot_id='reviewed', supersede=None):
        return subprocess.run(
            [sys.executable, str(CLI), '--snapshot', str(self.source),
             '--id', snapshot_id, '--root', str(self.root)]
            + (['--supersede', supersede] if supersede is not None else []),
            cwd=self.root, capture_output=True, text=True, check=False,
        )

    def stored_bytes(self):
        return {str(path.relative_to(self.root)): path.read_bytes()
                for path in self.folder.rglob('*') if path.is_file()}

    def refuse(self, snapshot_id='reviewed', error=None, supersede=None):
        before = self.stored_bytes()
        result = self.cli(snapshot_id, supersede)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertEqual(result.stdout, '')
        report = json.loads(result.stderr)
        self.assertEqual(report['status'], 'REFUSED')
        self.assertTrue(report['error'])
        if error:
            self.assertIn(error, report['error'])
        self.assertEqual(self.stored_bytes(), before)
        return report

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

    def concurrent_imports(self, requests):
        descriptor = os.open(self.folder, os.O_RDONLY | os.O_DIRECTORY)
        processes = []
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX)
            for source, name in requests:
                processes.append(subprocess.Popen(
                    [sys.executable, str(CLI), '--snapshot', str(source),
                     '--id', name, '--root', str(self.root)], cwd=self.root,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                ))
            # Hold the transaction boundary externally: neither importer may
            # publish or return success while another catalog writer owns it.
            for process in processes:
                with self.assertRaises(subprocess.TimeoutExpired):
                    process.communicate(timeout=0.25)
            self.assertEqual(json.loads(self.catalog.read_bytes())['snapshots'], [])
            fcntl.flock(descriptor, fcntl.LOCK_UN)
            results = []
            for process in processes:
                stdout, stderr = process.communicate(timeout=10)
                results.append((process.returncode, json.loads(stdout or stderr)))
            return results
        finally:
            os.close(descriptor)
            for process in processes:
                if process.poll() is None:
                    process.kill()
                process.communicate(timeout=10)

    def test_concurrent_distinct_imports_preserve_both_catalog_entries(self):
        other = self.root / 'other.json'
        value = fixture(); value['runs'][0]['id'] = 'other-run'
        other.write_text(json.dumps(value))
        results = self.concurrent_imports([(self.source, 'first'), (other, 'second')])
        self.assertEqual([status for status, _ in results], [0, 0])
        self.assertEqual([result['status'] for _, result in results], ['IMPORTED', 'IMPORTED'])
        entries = json.loads(self.catalog.read_bytes())['snapshots']
        self.assertEqual({entry['path'] for entry in entries},
                         {'reports/loops/first.json', 'reports/loops/second.json'})
        self.assertEqual((self.folder / 'first.json').read_bytes(), self.raw)
        self.assertEqual((self.folder / 'second.json').read_bytes(), other.read_bytes())

    def test_concurrent_identical_imports_return_one_import_and_one_noop(self):
        results = self.concurrent_imports([(self.source, 'same'), (self.source, 'same')])
        self.assertEqual([status for status, _ in results], [0, 0])
        self.assertEqual(sorted(result['status'] for _, result in results), ['IMPORTED', 'NOOP'])
        self.assertEqual(len(json.loads(self.catalog.read_bytes())['snapshots']), 1)
        self.assertEqual((self.folder / 'same.json').read_bytes(), self.raw)

    def test_concurrent_conflicting_import_refuses_without_overwriting_winner(self):
        other = self.root / 'other.json'
        value = fixture(); value['runs'][0]['status'] = 'completed'
        other.write_text(json.dumps(value))
        results = self.concurrent_imports([(self.source, 'same'), (other, 'same')])
        self.assertEqual(sorted(status for status, _ in results), [0, 2])
        self.assertEqual(sorted(result['status'] for _, result in results), ['IMPORTED', 'REFUSED'])
        entries = json.loads(self.catalog.read_bytes())['snapshots']
        self.assertEqual(len(entries), 1)
        saved = (self.folder / 'same.json').read_bytes()
        self.assertIn(saved, [self.raw, other.read_bytes()])
        self.assertEqual(hashlib.sha256(saved).hexdigest(), entries[0]['sha256'])

    def test_same_id_with_different_bytes_refuses(self):
        self.assertEqual(self.cli().returncode, 0)
        self.source.write_bytes(self.raw + b' ')
        self.refuse(error='Conflicting')

    def test_invalid_and_private_snapshots_refuse(self):
        existing = fixture()
        existing['runs'][0]['id'] = 'existing-run'
        self.add_existing('existing', existing)
        values = [({}, 'Invalid public Loop fields'),
                  ({'schema_version': 2, 'runs': []}, 'Unsupported public Loop schema')]
        for private in ('/Users/person/private', 'API_KEY=not-public'):
            value = fixture()
            value['runs'][0]['stages'][0]['prompt'] = private
            values.append((value, 'Public Loop text contains private data or is not text'))
        value = fixture()
        value['runs'][0]['environment'] = {'TOKEN': 'not-public'}
        values.append((value, 'Invalid public Loop fields'))
        for value, error in values:
            with self.subTest(value=value):
                self.write_source(value)
                self.assertEqual(self.refuse()['error'], error)
        value = fixture()
        value['runs'][0]['breakpoints'][0]['stage_id'] = []
        self.write_source(value)
        self.refuse(error="unhashable type: 'list'")
        self.source.write_bytes(b'{invalid json')
        self.refuse(error='Expecting property name enclosed in double quotes')
        self.write_source(fixture())
        result = self.cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['status'], 'IMPORTED')

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

    def test_supersede_retains_old_bytes_and_reentry_is_noop(self):
        old = self.add_existing('old', fixture())
        original = (self.folder / 'old.json').read_bytes()
        value = fixture(); value['runs'][0]['status'] = 'completed'
        self.write_source(value)
        result = self.cli(supersede='old')
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report['status'], 'SUPERSEDED')
        self.assertEqual(report['supersedes'], old)
        entries = json.loads(self.catalog.read_bytes())['snapshots']
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]['supersedes'], old)
        self.assertEqual((self.folder / 'old.json').read_bytes(), original)
        before = self.stored_bytes()
        stats = {path: path.stat().st_mtime_ns for path in self.folder.iterdir()}
        self.assertEqual(json.loads(self.cli(supersede='old').stdout)['status'], 'NOOP')
        self.assertEqual(json.loads(self.cli().stdout)['status'], 'NOOP')
        self.assertEqual(self.stored_bytes(), before)
        self.assertEqual({path: path.stat().st_mtime_ns for path in self.folder.iterdir()}, stats)
        out = self.root / 'rendered'; out.mkdir()
        self.assertEqual(len(site.render_loops(self.root, out, lambda title, body, active: body)), 1)

    def test_supersede_rejects_missing_old_run_changed_identity_and_other_duplicates(self):
        self.add_existing('old', fixture())
        other = fixture(); other['runs'][0]['id'] = 'other-run'
        self.add_existing('other', other)
        for field, new in [('id', 'replaced-run'), ('repository', 'different/repo'), ('mode', 'different')]:
            with self.subTest(field=field):
                value = fixture(); value['runs'][0][field] = new; self.write_source(value)
                self.refuse(supersede='old', error='preserve every old run')
        value = fixture(); value['runs'].append(other['runs'][0]); self.write_source(value)
        self.refuse(supersede='old', error='Duplicate public Loop run')
        self.write_source(fixture())
        self.refuse(supersede='absent', error='not selected')
        self.refuse('old', supersede='old', error='distinct')
        self.refuse(supersede='../old', error='Invalid public Loop ID')

    def test_supersede_snapshot_only_interruption_recovers_and_preserves_history(self):
        old = self.add_existing('old', fixture())
        destination = self.folder / 'reviewed.json'; destination.write_bytes(self.raw)
        before = destination.stat().st_mtime_ns
        result = self.cli(supersede='old')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['status'], 'RECOVERED')
        self.assertEqual(destination.stat().st_mtime_ns, before)
        self.assertEqual(json.loads(self.catalog.read_bytes())['snapshots'][0]['supersedes'], old)
        self.assertEqual(json.loads(self.cli(supersede='old').stdout)['status'], 'NOOP')

    def test_supersede_reentry_refuses_wrong_lineage_and_retained_source_drift(self):
        self.add_existing('old', fixture())
        self.assertEqual(self.cli(supersede='old').returncode, 0)
        self.refuse(supersede='unrelated', error='not this recorded supersession')
        self.source.write_bytes(self.raw + b' ')
        self.refuse(supersede='old', error='Conflicting')
        self.source.write_bytes(self.raw)
        (self.folder / 'old.json').write_bytes(b'{}')
        self.refuse(supersede='old', error='hash mismatch')
        self.refuse(error='hash mismatch')

    def test_supersede_chain_validates_every_retained_snapshot(self):
        self.add_existing('old', fixture())
        self.assertEqual(self.cli(supersede='old').returncode, 0)
        value = fixture(); value['runs'][0]['status'] = 'completed'; self.write_source(value)
        self.assertEqual(self.cli('newer', supersede='reviewed').returncode, 0)
        self.assertEqual(json.loads(self.cli('newer', supersede='reviewed').stdout)['status'], 'NOOP')
        self.refuse('fresh', supersede='old', error='not selected')
        (self.folder / 'old.json').write_bytes(b'{}')
        self.refuse('newer', supersede='reviewed', error='hash mismatch')


if __name__ == '__main__':
    unittest.main()
