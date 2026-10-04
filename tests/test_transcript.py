import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("transcript", ROOT / "scripts/transcript.py")
t = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t)
URL = "https://podscripts.co/podcasts/test-show/test-episode"
VIDEO = "https://youtu.be/ekK8urKHPMQ"
# Synthetic markup: no copied transcript text.
HTML = b'''<title>Fixture &amp; episode</title><nav>Not transcript</nav>
<span class="pod_timestamp_indicator">Starting point is 00:00:00</span>
<span class="transcript-text">Keep <b>the</b> condition &amp; uncertainty.</span>
<span class="transcript-text">Repeated.</span><span class="transcript-text">Repeated.</span>
<script>Not transcript either</script>
<span class="pod_timestamp_indicator">Starting point is 00:01:02</span>
<span class="transcript-text">It may work.</span>'''


class TranscriptTests(unittest.TestCase):
    def test_parser_preserves_conditions_duplicates_and_timestamp(self):
        result = t.parse(HTML)
        self.assertEqual(result['title'], 'Fixture & episode')
        self.assertEqual(result['segments'][0]['text'], 'Keep the condition & uncertainty. Repeated. Repeated.')
        self.assertEqual(result['segments'][1], {'timestamp': '00:01:02', 'start_seconds': 62, 'text': 'It may work.'})

    def test_bad_provider_pages_refuse(self):
        for raw in (b'<title>Access denied</title>', HTML.replace(b'00:01:02', b'00:00:00'),
                    HTML.replace(b'00:01:02', b'00:99:00'), HTML.split(b'<span class="transcript-text">It')[0]):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                t.parse(raw)

    def test_network_target_and_redirect_stay_on_provider(self):
        for url in ('http://podscripts.co/podcasts/a/b', 'https://localhost/podcasts/a/b',
                    'https://podscripts.co@evil.test/podcasts/a/b', URL+'?redirect=http://localhost',
                    'https://podscripts.co:443/podcasts/a/b', 'https://podscripts.co/podcasts/a/../b'):
            with self.subTest(url=url), self.assertRaises(ValueError):
                t.source_url(url)
        with self.assertRaises(ValueError):
            t.SafeRedirect().redirect_request(None, None, 302, '', {}, 'https://evil.test/a')

    def test_import_verify_receipt_and_refuse_overwrite(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); source = root/'input.html'; source.write_bytes(HTML)
            snapshot = root/'snapshot'
            manifest = t.acquire(URL, VIDEO, snapshot, source)
            self.assertEqual((snapshot/'source.html').read_bytes(), HTML)
            self.assertEqual(manifest['acquisition'], 'imported_html')
            self.assertIsNone(manifest['retrieved_at'])
            self.assertFalse(t.verify(snapshot)['audio_verified'])
            before = {f.name: f.read_bytes() for f in snapshot.iterdir()}
            with self.assertRaises(ValueError):
                t.acquire(URL, VIDEO, snapshot, source)
            self.assertEqual(before, {f.name: f.read_bytes() for f in snapshot.iterdir()})
            public = root/'public.json'; receipt = t.receipt(snapshot, public)
            self.assertNotIn('segments', receipt)
            self.assertNotIn('Keep the condition', public.read_text())
            with self.assertRaises(FileExistsError):
                t.receipt(snapshot, public)
            (snapshot/'transcript.md').write_text('edited')
            with self.assertRaisesRegex(ValueError, 'bytes changed'):
                t.verify(snapshot)

    def test_rehashed_extraction_still_must_match_raw(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); source = root/'input.html'; source.write_bytes(HTML)
            snapshot = root/'snapshot'; manifest = t.acquire(URL, VIDEO, snapshot, source)
            fake = b'rewritten source'; (snapshot/'transcript.md').write_bytes(fake)
            manifest['files']['transcript.md'] = t.digest(fake)
            (snapshot/'manifest.json').write_bytes(t.json_bytes(manifest))
            with self.assertRaisesRegex(ValueError, 'no longer matches'):
                t.verify(snapshot)

    def test_failed_fetch_and_bad_import_leave_no_snapshot(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); target = root/'snapshot'
            with patch.object(t, 'build_opener') as opener:
                opener.return_value.open.side_effect = TimeoutError('fixture timeout')
                with self.assertRaises(TimeoutError):
                    t.acquire(URL, VIDEO, target)
            self.assertFalse(target.exists())
            bad = root/'bad.html'; bad.write_text('<title>No transcript</title>')
            result = subprocess.run([sys.executable, str(ROOT/'scripts/transcript.py'),
                                     'import-html', '--url', URL, '--video-url', VIDEO,
                                     '--html', str(bad), '--out', str(target)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(json.loads(result.stderr)['status'], 'REFUSED')
            self.assertFalse(target.exists())


class TranscriptSiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        site_spec = importlib.util.spec_from_file_location('transcript_site', ROOT/'scripts/build_site.py')
        cls.site = importlib.util.module_from_spec(site_spec)
        site_spec.loader.exec_module(cls.site)

    def test_staged_replay_matches_published_article_and_receipt(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)/'replay'
            result = subprocess.run([sys.executable, str(ROOT/'evidence/transcript-cli/replay.py'),
                                     '--out', str(run)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((run/'run/medium-canonical.md').read_bytes(),
                             (ROOT/'articles/agent-primitives-product-differentiation.md').read_bytes())
            self.assertEqual(json.loads((run/'run/validation-receipt.json').read_bytes()),
                             json.loads((ROOT/'evidence/transcript-cli/validation-receipt.json').read_bytes()))

    def test_article_download_provenance_navigation_and_no_raw_publication(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)/'site'
            provenance = self.site.build(out)
            slug = 'agent-primitives-product-differentiation'
            route = '/articles/'+slug+'/'
            target = out/'articles'/slug
            original = (ROOT/'articles'/f'{slug}.md').read_bytes()
            self.assertEqual((target/'article.md').read_bytes(), original)
            self.assertIn('尚未逐句核對音訊', (target/'index.html').read_text())
            self.assertIn(route, (out/'articles/index.html').read_text())
            self.assertIn(route, (out/'index.html').read_text())
            self.assertIn(route, (out/'transcripts/index.html').read_text())
            self.assertIn('scripts/transcript.py fetch', (out/'transcripts/index.html').read_text())
            record = next(p for p in provenance['articles'] if p['route'] == route)
            self.assertEqual(record['sha256'], t.digest(original))
            self.assertEqual(record['source_manifest_sha256'], t.digest((target/'source.json').read_bytes()))
            self.assertFalse(list(out.rglob('source.html')))
            self.assertFalse(list(out.rglob('transcript.md')))

    def test_changed_article_or_source_refuses_publication(self):
        item = next(a for a in self.site.ARTICLES if a.get('source_manifest'))
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for name in (item['context'], item['source_manifest']):
                dest = root/name; dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes((ROOT/name).read_bytes())
            original = (ROOT/item['source']).read_bytes()
            with patch.object(self.site, 'ROOT', root):
                with self.assertRaisesRegex(ValueError, 'changed since'):
                    self.site.transcript_source(item, original+b'changed', root)
                manifest = root/item['source_manifest']
                manifest.write_bytes(manifest.read_bytes()+b' ')
                with self.assertRaisesRegex(ValueError, 'changed since'):
                    self.site.transcript_source(item, original, root)


if __name__ == '__main__':
    unittest.main()
