import json
from pathlib import Path
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from scripts import transcript_discovery as d
from api.transcripts import respond

EPISODE = 'https://podscripts.co/podcasts/test-show/test-episode'
RESULTS = b'''<h3><a href="/podcasts/test-show/test-episode?search_type=basic">Agent &amp; memory</a></h3>
<h3><a href="https://evil.test/podcasts/test-show/test-episode">Wrong host</a></h3>
<a href="/podcasts/test-show/another-episode">Unrelated navigation</a>
<h3><a href="/podcasts/test-show/test-episode">Duplicate</a></h3>'''
TRANSCRIPT = b'''<title>Fixture episode - Transcript</title>
<span class="pod_timestamp_indicator">Starting point is 00:00:00</span>
<span class="transcript-text">This is a synthetic transcript with enough words to exercise the public excerpt budget and ensure that later words never leave the server response.</span>
<span class="pod_timestamp_indicator">Starting point is 00:01:00</span>
<span class="transcript-text">PRIVATE FULL TEXT MARKER</span>'''


class DiscoveryTests(unittest.TestCase):
    def test_search_filters_links_and_exposes_real_query_scope(self):
        urls = []
        def reader(url):
            urls.append(url)
            return RESULTS
        result = d.search('Agent 記憶', 'latent-space', reader=reader)
        self.assertEqual(result['search_terms'], 'Agent memory')
        self.assertEqual(len(urls), 1)
        params = parse_qs(urlsplit(urls[0]).query)
        self.assertEqual(params['podSelectedId'], ['1772'])
        self.assertEqual(params['slv'], ['single'])
        self.assertEqual(result['results'], [{'title': 'Agent & memory', 'source_url': EPISODE,
                                             'status': 'candidate_not_audio_verified'}])

    def test_video_is_metadata_search_not_verified_identity(self):
        urls = []
        def reader(url, *args):
            urls.append(url)
            return json.dumps({'title': 'A Test Episode'}).encode() if '/oembed?' in url else RESULTS
        result = d.search('https://youtu.be/abcdefghijk', reader=reader)
        self.assertEqual(result['video_association'], 'video_title_search_only_not_verified')
        self.assertEqual(result['mode'], 'episode')
        self.assertEqual(len(urls), 2)
        known = d.search('https://youtu.be/ekK8urKHPMQ', reader=reader)
        self.assertEqual(known['video_association'], 'existing_caller_supplied_association_not_audio_verified')
        self.assertEqual(len(urls), 3)

    def test_empty_results_are_distinct_from_block_or_markup_change(self):
        result = d.search('unlikely', reader=lambda _: b'Found <span class="found-count-text">0</span> episodes')
        self.assertEqual(result['results'], [])
        for raw in (b'<title>Login required</title>', b'<title>Changed layout</title>'):
            with self.assertRaises(d.ProviderError):
                d.search('unlikely', reader=lambda _: raw)

    def test_untrusted_network_targets_and_redirects_refused(self):
        for url in ('http://podscripts.co/podcasts/a/b', 'https://127.0.0.1/a',
                    'https://podscripts.co@evil.test/podcasts/a/b',
                    'https://podscripts.co:443/podcasts/a/b',
                    'https://podscripts.co/podcasts/a/b?x=1'):
            with self.subTest(url=url), self.assertRaises(ValueError):
                d.inspect_episode(url, reader=lambda _: self.fail('Must not fetch invalid target'))
        with self.assertRaises(d.ProviderError):
            d.NoRedirect().redirect_request(None, None, 302, '', {}, 'https://evil.test')
        with self.assertRaises(ValueError):
            d.read_public('https://example.com')

    def test_fixed_preview_is_bounded_and_never_contains_full_transcript(self):
        data = d.inspect_episode(EPISODE, reader=lambda _: TRANSCRIPT)
        self.assertEqual(data['segment_count'], 2)
        self.assertEqual(data['last_timestamp'], '00:01:00')
        self.assertLessEqual(len(data['title'].split()) + len(data['excerpt'].split()), 25)
        self.assertNotIn('PRIVATE FULL TEXT MARKER', json.dumps(data))
        self.assertNotIn('segments', data)
        self.assertFalse(data['audio_verified'])
        with self.assertRaises(d.ProviderError):
            d.inspect_episode(EPISODE, reader=lambda _: b'blocked')

    def test_invalid_requests_never_reach_network(self):
        with patch.object(d, 'build_opener', side_effect=AssertionError('no network')):
            for path in ('/api/transcripts?q=x', '/api/transcripts?q=xx&podcast=evil',
                         '/api/transcripts?q=xx&q=yy', '/api/transcripts?action=other',
                         '/api/transcripts?action=inspect&url=http://localhost',
                         '/api/transcripts?q=https://example.com', '/api/transcripts?q='+'x'*241):
                self.assertEqual(respond(path)[0], 400, path)
        with patch('api.transcripts.search', side_effect=d.ProviderError('down')):
            self.assertEqual(respond('/api/transcripts?q=agent')[0], 502)

    def test_network_reader_enforces_response_budget_type_and_timeout(self):
        with patch.object(d, 'build_opener') as opener:
            response = opener.return_value.open.return_value.__enter__.return_value
            response.headers.get_content_type.return_value = 'text/html'
            response.read.return_value = b'12345'
            with self.assertRaises(d.ProviderError):
                d.read_public(EPISODE, limit=4)
            self.assertEqual(opener.return_value.open.call_args.kwargs['timeout'], 15)
            response.read.assert_called_with(5)
            response.headers.get_content_type.return_value = 'application/octet-stream'
            with self.assertRaises(d.ProviderError):
                d.read_public(EPISODE)

    def test_site_includes_form_script_and_does_not_embed_provider_content(self):
        root = Path(__file__).resolve().parents[1]
        html = (root/'site/transcripts.html').read_text()
        self.assertIn('id="transcript-form"', html)
        self.assertIn('aria-live="polite"', html)
        self.assertIn('/assets/transcripts.js', html)
        script = (root/'site/transcripts.js').read_text()
        self.assertNotIn('innerHTML', script)
        self.assertIn('id !== request', script)
