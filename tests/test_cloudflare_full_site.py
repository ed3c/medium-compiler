"""Complete-site transport preserves source bytes and the existing Lab boundary."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from build_full_cloudflare_site import build


class FullCloudflareSiteTests(unittest.TestCase):
    def test_full_assets_and_immutable_sources(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/'site'
            result=build(out)
            self.assertEqual(result['alg_four']['annotated_paragraphs'],36)
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
            manifest=json.loads((out/'deployment.json').read_text())
            for path,digest in manifest['files'].items():
                self.assertEqual(hashlib.sha256((out/path).read_bytes()).hexdigest(),digest,path)

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
