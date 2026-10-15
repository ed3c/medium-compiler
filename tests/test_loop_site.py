import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
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
                      '{"api_key":"DUMMY_NOT_A_REAL_SECRET"}',
                      "{'password': 'DUMMY_NOT_A_REAL_SECRET'}", 'TOKEN=DUMMY_NOT_A_REAL_SECRET',
                      '{"access_token": "DUMMY_NOT_A_REAL_SECRET"}',
                      '{"credentials": "DUMMY_NOT_A_REAL_SECRET"}',
                      '{"Authorization": "Bearer DUMMY_NOT_A_REAL_SECRET"}',
                      '.noodle/sessions/example/raw.ndjson', './.worktrees/example/prompt.txt',
                      r'.noodle\sessions\example\input.txt', 'nested/.worktrees/example',
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

    def test_public_text_remains_valid_and_nested_private_refs_refuse(self):
        for value in ('Tokens: UNKNOWN', 'Token count: 200', 'No credentials provided.',
                      'https://github.com/example/repository/blob/main/source.md',
                      'source:review-stage', '本階段保留原始要求。'):
            self.assertEqual(site.text(value), value)
        for collection in ('cards', 'notes'):
            data = fixture()
            data['runs'][0][collection][0]['source_refs'] = ['.noodle/sessions/example/raw.ndjson']
            with self.subTest(collection=collection), self.assertRaises(ValueError):
                site.validate_snapshot(data)
        data = fixture()
        data['runs'][0]['resources'][0]['value'] = '{"token": "DUMMY_NOT_A_REAL_SECRET"}'
        with self.assertRaises(ValueError):
            site.validate_snapshot(data)

    def test_prompt_comparison_preserves_text_and_unknown(self):
        run = fixture()['runs'][0]
        first = run['stages'][0]
        first['prompt'] = '原文😀'
        first['consumer_status'] = 'UNKNOWN'
        for stage_id, prompt in (('same', '原文😀'), ('changed', '<b>😀'), ('shorter', '短')):
            stage = copy.deepcopy(first)
            stage.update(id=stage_id, prompt=prompt)
            run['stages'].append(stage)
        rendered = site.render_run(run)
        first_rendered = rendered.split('</article>', 1)[0]
        self.assertIn('第一階段 · 3 字元 · 無前一階段可比較。', first_rendered)
        self.assertNotIn('並列比較', first_rendered)
        self.assertIn('完全相同 · 3 → 3 字元（0）', rendered)
        self.assertIn('文字不同 · 3 → 4 字元（+1）', rendered)
        self.assertIn('文字不同 · 4 → 1 字元（-3）', rendered)
        self.assertEqual(rendered.count('前一階段 → 本階段：並列比較'), 3)
        self.assertIn('前一階段 · same · source-review', rendered)
        self.assertIn('本階段 · changed · source-review', rendered)
        self.assertIn('&lt;b&gt;😀', rendered)
        self.assertNotIn('<b>', rendered)
        self.assertIn('僅比較文字；不代表語義改變或 consumer 已遵循。', rendered)
        self.assertIn('Consumer：UNKNOWN', rendered)
        self.assertIn('evidence · UNKNOWN', rendered)
        self.assertIn('Read original source', rendered)

    def test_publication_excludes_native_state_and_environment_files(self):
        private_paths = ['.noodle/sessions/fixture/raw.ndjson', 'nested/.noodle/input.txt',
                         '.worktrees/fixture/source.py', 'nested/.worktrees/fixture/prompt.txt',
                         '.env', '.env.local', 'nested/.env.production']
        ignored = subprocess.run(['git', 'check-ignore', '--no-index', '--stdin'],
                                 cwd=ROOT, input='\n'.join(private_paths) + '\n',
                                 text=True, capture_output=True, check=True)
        self.assertEqual(ignored.stdout.splitlines(), private_paths)
        upload_rules = set((ROOT / '.vercelignore').read_text().splitlines())
        settings = json.loads((ROOT / 'vercel.json').read_text())
        function_rules = set(settings['functions']['api/transcripts.py']['excludeFiles'][1:-1].split(','))
        required_rules = {'**/.noodle/**', '**/.worktrees/**', '**/.transcripts/**', '**/.env*',
                          '**/raw.ndjson', '**/events.ndjson', '**/prompt.txt', '**/input.txt', '**/spawn.json'}
        self.assertTrue(required_rules <= upload_rules)
        self.assertTrue(required_rules <= function_rules)
        self.assertEqual(settings['buildCommand'], 'python3 scripts/build_site.py')
        self.assertEqual(settings['outputDirectory'], 'dist')

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
