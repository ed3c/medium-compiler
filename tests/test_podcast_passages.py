import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from scripts import transcript as t
from scripts import build_site

ROOT = Path(__file__).resolve().parents[1]
URL = 'https://podscripts.co/podcasts/example/synthetic-episode'
HTML = b'''<title>Synthetic episode</title>
<span class="pod_timestamp_indicator">Starting point is 00:00:00</span>
<span class="transcript-text">Only under the stated condition.</span>
<span class="pod_timestamp_indicator">Starting point is 00:01:02</span>
<span class="transcript-text">An AGENT may use memory. It may fail. It may fail.</span>
<span class="pod_timestamp_indicator">Starting point is 00:02:04</span>
<span class="transcript-text">This does not establish safety.</span>'''


class PodcastPassageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        source = self.root/'source.html'; source.write_bytes(HTML)
        self.snapshot = self.root/'snapshot'
        t.acquire(URL, None, self.snapshot, source)

    def test_source_without_video_is_honest_and_preserved(self):
        manifest = t.verify(self.snapshot)
        self.assertIsNone(manifest['video_url'])
        self.assertEqual(manifest['video_association'], 'not_supplied')
        public = t.receipt(self.snapshot, self.root/'public.json')
        self.assertNotIn('segments', public)
        self.assertEqual((self.snapshot/'source.html').read_bytes(), HTML)

    def test_location_is_lexical_only_and_exposes_no_raw_text(self):
        result = t.locate(self.snapshot, ['AGENT', 'memory', 'agent'])
        self.assertEqual(result['matching_segments'], 1)
        self.assertEqual(result['matches'][0]['timestamp'], '00:01:02')
        self.assertEqual(result['matches'][0]['score'], 2)
        self.assertNotIn('It may fail', json.dumps(result))
        self.assertEqual(t.locate(self.snapshot, ['unmatched'])['matches'], [])
        (self.snapshot/'transcript.json').write_text('{}')
        with self.assertRaisesRegex(ValueError, 'bytes changed'):
            t.locate(self.snapshot, ['agent'])

    def test_passage_preserves_text_and_context_and_rejects_changed_packet(self):
        data = t.passage(self.snapshot, '00:01:02', '00:01:02')
        self.assertEqual(data['segments'][0]['text'], 'An AGENT may use memory. It may fail. It may fail.')
        self.assertEqual(data['context_before'][0]['text'], 'Only under the stated condition.')
        self.assertEqual(data['context_after'][0]['text'], 'This does not establish safety.')
        packet = self.root/'packet.json'; packet.write_bytes(t.json_bytes(data))
        t.verify_passage(self.snapshot, packet)
        data['segments'][0]['text'] = 'It will work.'
        packet.write_bytes(t.json_bytes(data))
        with self.assertRaisesRegex(ValueError, 'no longer matches'):
            t.verify_passage(self.snapshot, packet)
        for first,last,context in [('00:01:00','00:01:02',1),('00:02:04','00:00:00',1),('00:00:00','00:02:04',4)]:
            with self.assertRaises(ValueError):
                t.passage(self.snapshot, first, last, context)

    def test_actual_cli_refuses_overwrite_and_prints_metadata_only(self):
        packet = self.root/'packet.json'
        command = [sys.executable, str(ROOT/'scripts/transcript.py'), 'passage',
                   '--snapshot', str(self.snapshot), '--start', '00:01:02',
                   '--through', '00:01:02', '--out', str(packet)]
        result = subprocess.run(command, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn('It may fail', result.stdout)
        before = packet.read_bytes()
        repeated = subprocess.run(command, text=True, capture_output=True)
        self.assertEqual(repeated.returncode, 2)
        self.assertEqual(before, packet.read_bytes())

    def test_new_article_uses_own_source_scope_and_optional_video(self):
        article = b'# Another article\n\nIndependent analysis.\n'
        public = self.root/'receipt.json'
        meta = t.receipt(self.snapshot, public)
        context = {'article_sha256': t.digest(article), 'source_manifest': 'receipt.json',
                   'source_manifest_sha256': t.digest(public.read_bytes()),
                   'source_scope': {'timestamps': ['00:01:02'],
                                    'public_note': 'A different source scope. ',
                                    'analysis_note': 'An independent example. '}}
        context_path = self.root/'context.json'
        context_path.write_bytes(t.json_bytes(context))
        item = {'slug': 'different-podcast', 'source_manifest': 'receipt.json', 'context': 'context.json'}
        out = self.root/'out'; out.mkdir()
        with patch.object(build_site, 'ROOT', self.root):
            panel,_ = build_site.transcript_source(item, article, out)
            self.assertNotIn('14:05', panel)
            self.assertNotIn('回看原影片', panel)
            self.assertNotIn('商品頁', panel)
            self.assertIn('A different source scope.', panel)
            self.assertEqual((out/'article.md').read_bytes(), article)
            meta['video_url'] = 'https://www.youtube.com/watch?v=abcdefghijk'
            public.write_bytes(t.json_bytes(meta))
            context['source_manifest_sha256'] = t.digest(public.read_bytes())
            context_path.write_bytes(t.json_bytes(context))
            panel,_ = build_site.transcript_source(item, article, out)
            self.assertIn('&amp;t=62', panel)
            self.assertIn('01:02', panel)
            del context['source_scope']['analysis_note']
            context_path.write_bytes(t.json_bytes(context))
            with self.assertRaisesRegex(ValueError, 'own scope'):
                build_site.transcript_source(item, article, out)
