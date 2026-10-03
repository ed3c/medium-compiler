import importlib.util, json, tempfile, hashlib, wave
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("build_site",ROOT/"scripts/build_site.py")
site=importlib.util.module_from_spec(spec);spec.loader.exec_module(site)

class LearningSiteTests(unittest.TestCase):
    def test_alg_clean_urls_resolve_assets_and_preserve_audio(self):
        class Assets(HTMLParser):
            def __init__(self):
                super().__init__(); self.base=None; self.refs=[]
            def handle_starttag(self,tag,attrs):
                a=dict(attrs)
                if tag=='base': self.base=a['href']
                if tag=='script' and a.get('src'): self.refs.append(a['src'])
                if tag=='link' and a.get('rel')=='stylesheet': self.refs.append(a['href'])
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/'dist'; provenance=site.build(out)
            alg=out/'cefr-alg-c2'
            for filename,route in [('index.html','/cefr-alg-c2'),('compare.html','/cefr-alg-c2/compare')]:
                parser=Assets(); parser.feed((alg/filename).read_text())
                base=urljoin('https://example.test'+route,parser.base)
                self.assertEqual(base,'https://example.test/cefr-alg-c2/')
                for ref in parser.refs+['./kokoro-worker.js','./audio/manifest.json']:
                    self.assertTrue((out/urlparse(urljoin(base,ref)).path.lstrip('/')).is_file())
            lock=json.loads((alg/'provenance.json').read_text())
            self.assertIn('href="./compare#lab"',(alg/'compare.html').read_text())
            self.assertEqual(provenance['cefr_alg']['revision'],lock['revision'])
            for name,digest in lock['output_sha256'].items():
                self.assertEqual(hashlib.sha256((alg/name).read_bytes()).hexdigest(),digest)
            manifest=json.loads((alg/'audio/manifest.json').read_text())
            self.assertEqual({r['engine'] for r in manifest['results']},{'kokoro','parler','qwen','pocket','kokoro-web'})
            for result in manifest['results']:
                audio=alg/'audio'/result['audio_file']
                self.assertEqual(hashlib.sha256(audio.read_bytes()).hexdigest(),result['audio_sha256'])
                with wave.open(str(audio)) as wav:
                    self.assertAlmostEqual(wav.getnframes()/wav.getframerate(),result['audio_seconds'],places=3)
            self.assertIn('id="cefr-alg"',(out/'index.html').read_text())
            self.assertIn('/cefr-alg-c2/',(out/'learning/index.html').read_text())

    def test_build_uses_article_ops_snapshot_and_honest_learning_state(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/"dist";p=site.build(out)
            self.assertTrue((out/"index.html").is_file())
            self.assertTrue((out/"experiments/index.html").is_file())
            self.assertTrue((out/"articles/ai-engineer-learning-path/index.html").is_file())
            self.assertTrue((out/"learning/index.html").is_file())
            home=(out/"index.html").read_text()
            self.assertIn("AI Engineer",home)
            self.assertIn("Experiment templates",home)
            experiments=(out/"experiments/index.html").read_text()
            self.assertIn("Prompt Change Experiment",experiments)
            self.assertIn("Agent Workflow Decision",experiments)
            article=(out/"articles/ai-engineer-learning-path/index.html").read_text()
            self.assertIn("Ops Reconciliation Copilot",article)
            if not (ROOT/"LEARNING.md").exists():
                self.assertEqual(p["learning"]["status"],"NOT_INITIALIZED")
    def test_upstream_learning_skill_bytes_match_pinned_git_blobs(self):
        lock=json.loads((ROOT/"references/upstream/ai-engineering-skills-lock.json").read_text())
        import hashlib
        for item in lock["files"]:
            data=(ROOT/item["target_path"]).read_bytes()
            blob=hashlib.sha1(f"blob {len(data)}\0".encode()+data).hexdigest()
            self.assertEqual(blob,item["git_blob"])
    def test_ops_snapshot_is_pinned_and_templates_do_not_auto_promote(self):
        data=json.loads((ROOT/"references/ops-experiment-catalog.json").read_text())
        self.assertEqual(len(data["templates"]),5)
        self.assertEqual(len(data["provider_revision"]),40)
        for item in data["templates"]:
            self.assertNotIn("AUTO_PROMOTE",json.dumps(item))
            self.assertTrue(item["promotion_gate"])

if __name__=="__main__":unittest.main()
