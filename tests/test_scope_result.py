import copy
import hashlib
import html
from html.parser import HTMLParser
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / 'scripts/import_scope_result.py'
spec = importlib.util.spec_from_file_location('scope_site', ROOT / 'scripts/scope_site.py')
site = importlib.util.module_from_spec(spec)
spec.loader.exec_module(site)
NATIVE_INPUTS = ('SCOPE_FACTORYWEAVER_ROOT', 'SCOPE_NEOWEAVER_ROOT', 'SCOPE_BUNDLE', 'SCOPE_RESULT')


class Tags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.pre = []
        self.in_pre = False

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        if tag == 'pre':
            self.in_pre = True
            self.pre.append('')

    def handle_endtag(self, tag):
        if tag == 'pre':
            self.in_pre = False

    def handle_data(self, data):
        if self.in_pre:
            self.pre[-1] += data


def source_values(value):
    if isinstance(value, dict):
        return [text for item in value.values() for text in source_values(item)]
    if isinstance(value, list):
        return [text for item in value for text in source_values(item)]
    return [value if isinstance(value, str) else json.dumps(value)]


class ScopeBuildTests(unittest.TestCase):
    def test_existing_builder_connects_scope_routes_css_and_loop_provenance(self):
        builder_spec = importlib.util.spec_from_file_location('scope_builder', ROOT / 'scripts/build_site.py')
        builder = importlib.util.module_from_spec(builder_spec)
        builder_spec.loader.exec_module(builder)
        with tempfile.TemporaryDirectory() as name:
            out = Path(name) / 'site'
            result = builder.build(out)
            self.assertEqual(result['scopes'][0]['route'], '/scopes/parser-scope/')
            self.assertEqual(result['scopes'][0]['result_sha256'], hashlib.sha256(
                (ROOT / 'reports/scopes/parser-scope.json').read_bytes()).hexdigest())
            self.assertIn('href="/scopes/"', (out / 'index.html').read_text())
            detail = (out / 'scopes/parser-scope/index.html').read_text()
            self.assertIn('class="active" href="/scopes/"', detail)
            self.assertIn('href="/assets/styles.css"', detail)
            self.assertEqual((out / 'assets/styles.css').read_bytes(), (ROOT / 'site/styles.css').read_bytes())
            self.assertEqual(json.loads((out / 'provenance.json').read_bytes())['scopes'], result['scopes'])
            for entry in result['loops']:
                self.assertTrue((out / entry['route'].strip('/') / 'index.html').is_file())
            self.assertIn('href="/loops/"', (out / 'index.html').read_text())


class ScopeResultTests(unittest.TestCase):
    native = False

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.result = self.root / 'result.json'
        self.bundle = self.root / 'bundle.json'
        self.destination = self.root / 'reports/scopes/parser-scope.json'
        if self.native:
            self.factory = Path(os.environ['SCOPE_FACTORYWEAVER_ROOT']).resolve()
            self.neo = Path(os.environ['SCOPE_NEOWEAVER_ROOT']).resolve()
            self.bundle.write_bytes(Path(os.environ['SCOPE_BUNDLE']).read_bytes())
            self.raw = Path(os.environ['SCOPE_RESULT']).read_bytes()
        else:
            self.factory = self.root / 'factory'
            self.neo = self.root / 'neo'
            for folder in (self.factory, self.neo):
                (folder / 'scripts').mkdir(parents=True)
            for name in ('factoryweaver', 'soodles_handoff'):
                (self.factory / 'scripts' / (name + '.py')).write_text('')
            # This stand-in checks transport only. Native tests exercise the real validators.
            (self.neo / 'scripts/import_factory_scope.py').write_text('''
import argparse, hashlib, json
from pathlib import Path
p = argparse.ArgumentParser()
p.add_argument('bundle', type=Path)
p.add_argument('--factoryweaver-root', required=True)
p.add_argument('--output', required=True, type=Path)
a = p.parse_args()
raw = a.bundle.read_bytes()
value = json.loads(raw)['fixture_result']
value['bundle_sha256'] = hashlib.sha256(raw).hexdigest()
a.output.write_text(json.dumps(value))
''')
            value = json.loads((ROOT / 'reports/scopes/parser-scope.json').read_bytes())
            self.bundle.write_text(json.dumps({'fixture_result': value}))
            value['bundle_sha256'] = hashlib.sha256(self.bundle.read_bytes()).hexdigest()
            self.raw = (json.dumps(value, ensure_ascii=False, indent=3) + '\n\n').encode()
        self.value = json.loads(self.raw)
        self.result.write_bytes(self.raw)

    def cli(self):
        return subprocess.run(
            [sys.executable, '-B', str(CLI), '--result', str(self.result),
             '--bundle', str(self.bundle), '--factoryweaver-root', str(self.factory),
             '--neoweaver-root', str(self.neo), '--root', str(self.root)],
            capture_output=True, text=True, check=False, timeout=45)

    def write_result(self, value):
        self.result.write_text(json.dumps(value, ensure_ascii=False))

    def refused(self, error=None):
        before = self.destination.read_bytes() if self.destination.exists() else None
        result = self.cli()
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertEqual(result.stdout, '')
        report = json.loads(result.stderr)
        self.assertEqual(report['status'], 'REFUSED')
        if error:
            self.assertIn(error, report['error'])
        after = self.destination.read_bytes() if self.destination.exists() else None
        self.assertEqual(after, before)

    def imported(self):
        result = self.cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, '')
        self.assertEqual(json.loads(result.stdout)['status'], 'IMPORTED')
        self.assertEqual(self.destination.read_bytes(), self.raw)

    def test_exact_bytes_then_noop_without_rewrite(self):
        self.imported()
        before = self.destination.stat()
        result = self.cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['status'], 'NOOP')
        self.assertEqual(self.destination.read_bytes(), self.raw)
        after = self.destination.stat()
        self.assertEqual((before.st_ino, before.st_mtime_ns), (after.st_ino, after.st_mtime_ns))
        self.assertEqual(after.st_mode & 0o222, 0)

    def test_conflicting_serialization_refuses_even_when_values_match(self):
        self.imported()
        self.write_result(self.value)
        self.refused('scope_output_conflict')

    def test_forged_fields_and_reordering_refuse_without_public_mutation(self):
        self.imported()
        for key in self.value:
            with self.subTest(field=key):
                value = copy.deepcopy(self.value)
                if isinstance(value[key], list):
                    value[key].append('forged consumer PASS')
                elif key == 'authorizes_landing':
                    value[key] = True
                elif key == 'schema':
                    value[key] = True
                else:
                    value[key] += 'forged'
                self.write_result(value)
                self.refused()
        for key in ('requirements', 'cards', 'selected_card_ids', 'prompt_delta'):
            with self.subTest(order=key):
                value = copy.deepcopy(self.value)
                value[key].reverse()
                self.write_result(value)
                self.refused('source_result_value_mismatch')
        for key, field in (('cards', 'payload'), ('requirements', 'statement')):
            value = copy.deepcopy(self.value)
            value[key][0][field] += ' forged PASS'
            self.write_result(value)
            self.refused('source_result_value_mismatch')

    def test_source_digest_binds_raw_bundle_bytes(self):
        self.imported()
        self.bundle.write_bytes(self.bundle.read_bytes() + b'\n')
        self.refused('source_bundle_digest_mismatch')

    def test_unknown_fields_duplicate_keys_constants_and_wrong_types_refuse(self):
        self.imported()
        for raw in (b'{"schema":1,"schema":1}', b'{"x":NaN}', b'[]', b'\xff', b'{'):
            with self.subTest(raw=raw):
                self.result.write_bytes(raw)
                self.refused()
        for value in ({**self.value, 'consumer_pass': True}, {**self.value, 'goal': 1},
                      {**self.value, 'cards': {}}, {**self.value, 'authorizes_landing': 0}):
            self.write_result(value)
            self.refused()
        value = copy.deepcopy(self.value)
        value['cards'][0]['revision'] = float(value['cards'][0]['revision'])
        self.write_result(value)
        self.refused('source_result_type_mismatch')

    def test_private_paths_and_credentials_refuse(self):
        self.imported()
        for private in ('/Users/alice/source', '/home/alice/key', '/private/tmp/data',
                        'C:\\Users\\alice', 'file:///secret', '~/private',
                        'sk-' + 'a' * 24, 'ghp_' + 'b' * 24,
                        'Authorization: Bearer hidden', 'api_key=hidden',
                        'AKIA' + 'A' * 16, 'github_pat_' + 'b' * 24,
                        'xoxb-' + 'c' * 20, 'https://alice:password@example.com',
                        '/workspace/private/data', 'AWS_SECRET_ACCESS_KEY=hidden',
                        '-----BEGIN PRIVATE KEY-----'):
            with self.subTest(private=private):
                value = copy.deepcopy(self.value)
                value['cards'][0]['payload'] += '\n' + private
                self.write_result(value)
                self.refused('scope_contains_private_text')

    def test_symlinks_and_wrong_upstream_roots_refuse(self):
        self.result.unlink()
        target = self.root / 'actual.json'
        target.write_bytes(self.raw)
        self.result.symlink_to(target)
        self.refused('regular_file')
        self.result.unlink()
        self.result.write_bytes(self.raw)
        self.neo = self.factory
        self.refused()

    def test_destination_symlink_and_escaping_parent_refuse(self):
        self.destination.parent.mkdir(parents=True)
        other = self.root / 'unchanged'
        other.write_bytes(b'unchanged')
        self.destination.symlink_to(other)
        self.refused('scope_public_path')
        self.assertEqual(other.read_bytes(), b'unchanged')
        self.destination.unlink()
        self.destination.parent.rmdir()
        with tempfile.TemporaryDirectory() as outside:
            self.destination.parent.symlink_to(outside, target_is_directory=True)
            self.refused('scope_public_path')
            self.assertEqual(list(Path(outside).iterdir()), [])

    def test_render_preserves_all_source_text_order_routes_and_provenance(self):
        self.imported()
        out = self.root / 'site'
        result = site.render_scopes(self.root, out, lambda title, body, active: body)
        self.assertEqual(result, [{'route': '/scopes/parser-scope/',
                                  'result_sha256': hashlib.sha256(self.raw).hexdigest(),
                                  'bundle_sha256': self.value['bundle_sha256'],
                                  'proof_ceiling': 'SOURCE_BOUND_SELECTION_ONLY'}])
        rendered = (out / 'scopes/parser-scope/index.html').read_text()
        self.assertIn(html.escape(self.value['goal']), rendered)
        self.assertEqual(len(self.value['requirements']), 10)
        self.assertEqual(len(self.value['cards']), 6)
        tags = Tags()
        tags.feed(rendered)
        expected = []
        for key in ('goal', 'requirements', 'selected_requirement_ids', 'selected_card_ids',
                    'cards', 'prompt_delta', 'bundle_sha256'):
            expected.extend(source_values(self.value[key]))
        self.assertEqual(tags.pre, expected)
        self.assertIn('SOURCE_BOUND_SELECTION_ONLY', rendered)
        self.assertIn('href="/scopes/parser-scope/"', (out / 'scopes/index.html').read_text())

    def test_empty_site_does_not_invent_selection(self):
        out = self.root / 'site'
        self.assertEqual(site.render_scopes(self.root, out, lambda title, body, active: body), [])
        self.assertIn('目前沒有已匯入的 Scope', (out / 'scopes/index.html').read_text())
        self.assertFalse((out / 'scopes/parser-scope').exists())

    def test_renderer_escapes_nested_strings_and_keys_without_active_markup(self):
        self.imported()
        value = copy.deepcopy(self.value)
        payload = '<script>execute()</script><img src=x onerror="execute()"> & \' "'
        value['goal'] = payload
        value['cards'][0]['payload'] = payload
        value['cards'][0][payload] = payload
        self.destination.chmod(0o644)
        self.destination.write_text(json.dumps(value))
        out = self.root / 'site'
        site.render_scopes(self.root, out, lambda title, body, active: body)
        for name in ('scopes/index.html', 'scopes/parser-scope/index.html'):
            rendered = (out / name).read_text()
            self.assertIn(html.escape(payload), rendered)
            tags = Tags()
            tags.feed(rendered)
            for tag in ('script', 'img', 'form', 'button', 'input', 'iframe'):
                self.assertNotIn(tag, tags.tags)


@unittest.skipUnless(all(os.environ.get(key) for key in NATIVE_INPUTS),
                     'Native upstream checkouts require explicit SCOPE_* inputs')
class NativeScopeResultTests(ScopeResultTests):
    native = True

    def native_result(self):
        output = self.root / 'native-result.json'
        output.unlink(missing_ok=True)
        result = subprocess.run(
            [sys.executable, '-B', str(self.neo / 'scripts/import_factory_scope.py'),
             str(self.bundle), '--factoryweaver-root', str(self.factory), '--output', str(output)],
            capture_output=True, text=True, check=False, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.result.write_bytes(output.read_bytes())
        return output.read_bytes()

    def test_invalid_source_cannot_be_blessed_by_matching_digest(self):
        self.imported()
        bundle = json.loads(self.bundle.read_bytes())
        for invalid in ('unknown_protocol', 'invalid_record', 'duplicate_key'):
            with self.subTest(control=invalid):
                changed = copy.deepcopy(bundle)
                if invalid == 'unknown_protocol':
                    changed['protocol'] = 'factoryweaver/unknown/v99'
                elif invalid == 'invalid_record':
                    del changed['knowledge_record']['requirements'][0]['statement']
                raw = json.dumps(changed).encode()
                if invalid == 'duplicate_key':
                    raw = b'{"protocol":"factoryweaver/soodles-scope/v1",' + raw[1:]
                self.bundle.write_bytes(raw)
                self.write_result({**self.value, 'bundle_sha256': hashlib.sha256(raw).hexdigest()})
                self.refused('neoweaver_recompute_refused')

    def test_source_bound_private_text_still_refuses(self):
        self.imported()
        original = json.loads(self.bundle.read_bytes())
        for private in ('/Users/alice/private', 'api_key=secret-value'):
            with self.subTest(private=private):
                changed = copy.deepcopy(original)
                changed['selection']['goal'] = private
                self.bundle.write_text(json.dumps(changed))
                self.native_result()
                self.refused('scope_contains_private_text')

    def test_html_in_native_source_imports_as_inert_text(self):
        bundle = json.loads(self.bundle.read_bytes())
        payload = '<script>execute()</script><img src=x onerror="execute()"> & \' "'
        bundle['selection']['goal'] = payload
        self.bundle.write_text(json.dumps(bundle))
        self.raw = self.native_result()
        self.imported()
        out = self.root / 'site'
        site.render_scopes(self.root, out, lambda title, body, active: body)
        for name in ('scopes/index.html', 'scopes/parser-scope/index.html'):
            rendered = (out / name).read_text()
            self.assertIn(html.escape(payload), rendered)
            tags = Tags()
            tags.feed(rendered)
            self.assertNotIn('script', tags.tags)
            self.assertNotIn('img', tags.tags)


if __name__ == '__main__':
    unittest.main()
