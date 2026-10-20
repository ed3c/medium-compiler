"""Complete-site transport preserves source bytes and the existing Lab boundary."""
import importlib.util
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from build_full_cloudflare_site import build


class FullCloudflareSiteTests(unittest.TestCase):
    def test_ci_build_skips_asset_hashing_but_deploy_build_emits_manifest(self):
        def source(out):
            out.mkdir()
            (out/'asset.txt').write_bytes(b'abc')
            return {'alg_four': {}}

        with tempfile.TemporaryDirectory() as td:
            with patch('build_full_cloudflare_site.build_site', side_effect=source):
                ci=Path(td)/'ci'
                with patch('build_full_cloudflare_site.hashlib.sha256',
                           side_effect=AssertionError('Content CI must not hash deployment assets')):
                    result=build(ci, deployment_manifest=False)
                self.assertEqual((ci/'asset.txt').read_bytes(),b'abc')
                self.assertFalse((ci/'deployment.json').exists())
                self.assertFalse(result['deployment_manifest'])
                deploy=Path(td)/'deploy'
                build(deploy)
                manifest=json.loads((deploy/'deployment.json').read_text())
                self.assertEqual(set(manifest['files']),{'asset.txt','provenance.json'})
                self.assertEqual(manifest['files']['asset.txt'],
                                 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad')

    def test_full_assets_and_immutable_sources(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/'site'
            result=build(out, deployment_manifest=False)
            source=json.loads((ROOT/'references/learning/alg-four-group-anagrams.json').read_text())
            self.assertEqual(result['alg_four']['annotated_paragraphs'],source['alignment']['paragraph_count'])
            self.assertEqual(result['alg_four']['active_items_collected'],14)
            for route in ('alg-four','learning','articles','cefr-alg-c2','transcripts','experiments','reliability','ai-evals','loops','scopes','more-route'):
                self.assertTrue((out/route/'index.html').is_file(),route)
            self.assertFalse((out/'_redirects').exists())
            self.assertEqual((out/'_headers').read_bytes(),(ROOT/'site/_headers').read_bytes())
            self.assertEqual((out/'alg-four/source.json').read_bytes(),(ROOT/'references/learning/alg-four-group-anagrams.json').read_bytes())
            page=(out/'alg-four/index.html').read_text()
            figures=re.findall(r'<img[^>]+src="([^"]+)"',page)
            self.assertEqual(len(figures),7)
            for src in figures:
                self.assertTrue(src.startswith('/assets/alg-four/'))
                self.assertEqual((out/src.lstrip('/')).read_bytes(),(ROOT/'site/alg-four-figures'/Path(src).name).read_bytes())
            for page in out.rglob('*.html'):
                self.assertNotRegex(page.read_text(),r'(?:src|href)="https://medium-compiler\.vercel\.app/')
            self.assertIn('href="https://medium-compiler.ga874199.workers.dev/reliability/"',(out/'index.html').read_text())
            for path in out.rglob('article.md'):
                slug=path.parent.name
                self.assertEqual(path.read_bytes(),(ROOT/'articles'/f'{slug}.md').read_bytes())
            self.assertFalse((out/'deployment.json').exists())
            self.assertFalse(result['deployment_manifest'])

    def test_separate_worker_has_no_payment_bindings(self):
        config=json.loads((ROOT/'wrangler.full-site.jsonc').read_text())
        self.assertEqual(config['name'],'medium-compiler-full-site')
        self.assertEqual(config['assets']['directory'],'./dist')
        self.assertEqual(config['assets']['not_found_handling'],'none')
        self.assertEqual(config['assets']['run_worker_first'],['/api/*'])
        for key in ('queues','durable_objects','services','routes','migrations'):
            self.assertNotIn(key,config)
        original=json.loads((ROOT/'wrangler.jsonc').read_text())
        self.assertEqual(original['assets']['directory'],'./dist-cloudflare')
