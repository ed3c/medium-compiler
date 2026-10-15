import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('loop_site', ROOT / 'scripts/loop_site.py')
site = importlib.util.module_from_spec(spec)
spec.loader.exec_module(site)


def fixture():
    return {'schema_version': 1, 'runs': [{
        'id': 'test-only-run', 'repository': 'example/repository', 'mode': 'single',
        'status': 'NOT_RUN', 'stages': [{
            'id': 'review', 'kind': 'source-review', 'status': 'NOT_RUN',
            'prompt': '<script>alert(1)</script>\n[link](javascript:alert(1))',
            'input_refs': ['source:example', 'https://github.com/example/repository/blob/main/source.md'], 'output_refs': [], 'consumer_status': 'NOT_RUN'}],
        'cards': [{'id': 'spec-1', 'type': 'SPEC', 'title': '<img src=x onerror=alert(1)>',
                   'body': 'Specification text', 'source_refs': ['source:example']}],
        'notes': [{'id': 'note-1', 'title': 'Note', 'body': 'Observation', 'source_refs': []}],
        'breakpoints': [{'kind': 'evidence', 'status': 'UNKNOWN', 'stage_id': 'review', 'message': 'No native capture'}],
        'resources': [{'label': 'Tokens', 'value': 'UNKNOWN'}], 'next': 'Read original source'}]}


class LoopSiteTests(unittest.TestCase):
    def prepare(self, root, value):
        folder = root / 'reports/loops'
        folder.mkdir(parents=True, exist_ok=True)
        raw = json.dumps(value).encode()
        (folder / 'public.json').write_bytes(raw)
        entry = {'path': 'reports/loops/public.json', 'sha256': hashlib.sha256(raw).hexdigest()}
        (folder / 'catalog.json').write_text(json.dumps({'schema_version': 1, 'snapshots': [entry]}))
        return entry

    def test_public_snapshot_renders_inert_text_and_preserves_unknown(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            entry = self.prepare(root, fixture())
            out = root / 'out'
            out.mkdir()
            provenance = site.render_loops(root, out, lambda title, body, active: body)
            rendered = (out / 'loops/test-only-run/index.html').read_text()
            self.assertIn('&lt;script&gt;alert(1)&lt;/script&gt;', rendered)
            self.assertIn('&lt;img', rendered)
            self.assertNotIn('<script', rendered)
            self.assertNotIn('<img', rendered)
            self.assertNotIn('href="javascript:', rendered)
            self.assertNotIn('<form', rendered)
            self.assertIn('UNKNOWN', rendered)
            self.assertIn('Consumer：NOT_RUN', rendered)
            self.assertIn('規格卡片', rendered)
            self.assertIn('卡盒筆記', rendered)
            self.assertIn('/loops/test-only-run/', (out / 'loops/index.html').read_text())
            self.assertEqual(provenance[0]['snapshot_sha256'], entry['sha256'])
            self.assertEqual(provenance[0]['status'], 'NOT_RUN')
            self.assertEqual(list((out / 'loops/test-only-run').iterdir()), [out / 'loops/test-only-run/index.html'])

    def test_private_fields_and_known_private_text_refuse(self):
        for value in ('/Users/person/private', '/home/person/secret', 'C:\\Users\\person',
                      'file:///private/data', 'API_KEY=not-public', 'Authorization: Bearer private',
                      'sk-' + 'a' * 30):
            with self.subTest(value=value):
                data = fixture()
                data['runs'][0]['stages'][0]['prompt'] = value
                with self.assertRaises(ValueError):
                    site.validate_snapshot(data)
        data = fixture()
        data['runs'][0]['environment'] = {'TOKEN': 'not-public'}
        with self.assertRaises(ValueError):
            site.validate_snapshot(data)

    def test_hash_drift_and_path_escape_refuse(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            entry = self.prepare(root, fixture())
            (root / entry['path']).write_text('{}')
            with self.assertRaisesRegex(ValueError, 'hash mismatch'):
                site.checked_snapshot(root, entry)
            for path in ('../private.json', '/tmp/private.json', 'reports/other.json'):
                with self.subTest(path=path), self.assertRaises(ValueError):
                    site.checked_snapshot(root, {'path': path, 'sha256': '0' * 64})

    def test_duplicate_ids_unknown_stage_and_extra_fields_refuse(self):
        data = fixture()
        data['runs'].append(copy.deepcopy(data['runs'][0]))
        with self.assertRaises(ValueError):
            site.validate_snapshot(data)
        data = fixture()
        data['runs'][0]['breakpoints'][0]['stage_id'] = 'absent'
        with self.assertRaises(ValueError):
            site.validate_snapshot(data)
        data = fixture()
        data['runs'][0]['next'] = {'argv': ['execute']}
        with self.assertRaises(ValueError):
            site.validate_snapshot(data)

    def test_empty_catalog_does_not_invent_execution(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / 'reports/loops').mkdir(parents=True)
            (root / 'reports/loops/catalog.json').write_text('{"schema_version": 1, "snapshots": []}')
            out = root / 'out'
            out.mkdir()
            self.assertEqual(site.render_loops(root, out, lambda title, body, active: body), [])
            self.assertIn('目前沒有已公開的 Loop 紀錄', (out / 'loops/index.html').read_text())

    def test_existing_builder_exposes_loop_navigation_and_provenance(self):
        builder_spec = importlib.util.spec_from_file_location('loop_site_builder', ROOT / 'scripts/build_site.py')
        builder = importlib.util.module_from_spec(builder_spec)
        builder_spec.loader.exec_module(builder)
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / 'site'
            result = builder.build(out)
            catalog = json.loads((ROOT / 'reports/loops/catalog.json').read_text())
            count = sum(len(site.checked_snapshot(ROOT, entry)['runs']) for entry in catalog['snapshots'])
            self.assertEqual(len(result['loops']), count)
            self.assertEqual(json.loads((out / 'provenance.json').read_text())['loops'], result['loops'])
            self.assertIn('href="/loops/"', (out / 'index.html').read_text())
            self.assertIn('class="active" href="/loops/"', (out / 'loops/index.html').read_text())
