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
            for filename,route in [('index.html','/cefr-alg-c2'),('compare.html','/cefr-alg-c2/compare'),('technical.html','/cefr-alg-c2/technical?lesson=software-factory-sole-acceptance')]:
                parser=Assets(); parser.feed((alg/filename).read_text())
                base=urljoin('https://example.test'+route,parser.base)
                self.assertEqual(base,'https://example.test/cefr-alg-c2/')
                for ref in parser.refs+['./studio-narrator.js','./kokoro-worker.js','./audio/manifest.json','./narration/manifest.json']:
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
            narration=json.loads((alg/'narration/manifest.json').read_text())
            expected={f'{lesson}-{scene}-{variant}' for lesson in ['release','handoff','design','everyday'] for scene in range(3) for variant in ['plain','detailed']}
            self.assertEqual({r['case_id'] for r in narration['results']},expected)
            self.assertEqual(len(narration['results']),24)
            for result in narration['results']:
                self.assertEqual(hashlib.sha256((alg/'narration'/result['audio_file']).read_bytes()).hexdigest(),result['audio_sha256'])
            self.assertNotIn('speechSynthesis',(alg/'app.js').read_text())
            self.assertIn('id="narration-model"',(alg/'index.html').read_text())
            self.assertIn('id="cefr-alg"',(out/'index.html').read_text())
            self.assertIn('/cefr-alg-c2/',(out/'learning/index.html').read_text())

    def test_frozen_technical_lesson_media_and_projection_survive_import(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/'dist'; site.build(out)
            source=ROOT/'site/cefr-alg-c2'
            target=out/'cefr-alg-c2'
            lesson=target/'technical-lessons/software-factory-sole-acceptance'
            manifest=json.loads((lesson/'manifest.json').read_text())
            data=json.loads((lesson/'lesson.json').read_text())
            self.assertEqual(data['lesson_id'],'software-factory-sole-acceptance')
            self.assertEqual(data['revision'],'1.0.0')
            for path in lesson.iterdir():
                self.assertEqual(path.read_bytes(),(source/path.relative_to(target)).read_bytes())
            self.assertEqual(hashlib.sha256((lesson/'final.mp4').read_bytes()).hexdigest(),
                             'f171144553782a2af03a0fb33f6375abdd963563a1b2522a35d32842da0bd050')
            self.assertEqual(hashlib.sha256((lesson/'narration.txt').read_bytes()).hexdigest(),
                             '9ee68b89c9fce494e50f14d24a847620cb40bedfe6bb0d19cdcb128a1ebb6e31')
            self.assertEqual(hashlib.sha256((lesson/'lesson.json').read_bytes()).hexdigest(),manifest['projection_sha256'])
            self.assertTrue((lesson/'captions.vtt').read_text().startswith('WEBVTT\n'))
            for name in ('technical.js','technical-notes.js'):
                self.assertEqual((source/name).read_bytes(),(target/name).read_bytes())
            html=(target/'technical.html').read_text()
            self.assertNotIn('Downstream import remains pending',html)
            self.assertIn('Pinned snapshot imported here',html)
            self.assertIn('/cefr-alg-c2/technical?lesson=software-factory-sole-acceptance',(out/'index.html').read_text())

    def test_local_video_controls_are_consumer_owned_and_provenance_scoped(self):
        class Controls(HTMLParser):
            def __init__(self):
                super().__init__(); self.divs=[]; self.elements={}; self.scripts=[]
            def handle_starttag(self,tag,attrs):
                a=dict(attrs)
                if a.get('id'): self.elements[a['id']]=(tag,a,tuple(self.divs))
                if tag=='div': self.divs.append(a.get('id'))
                if tag=='script' and a.get('src'): self.scripts.append(a['src'])
            def handle_endtag(self,tag):
                if tag=='div': self.divs.pop()
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/'dist'; site.build(out)
            target=out/'cefr-alg-c2'
            parser=Controls(); parser.feed((target/'technical.html').read_text())
            tag,attrs,parents=parser.elements['local-video-file']
            self.assertEqual((tag,attrs['type'],attrs['accept']),('input','file','video/*'))
            self.assertIn('fixed-media',parents)
            self.assertIn('disabled',parser.elements['reset-lesson-video'][1])
            self.assertIn('hidden',parser.elements['local-video-warning'][1])
            self.assertNotIn('fixed-media',parser.elements['local-video-warning'][2])
            self.assertIn('./local-lesson-video.js',parser.scripts)
            self.assertEqual((target/'local-lesson-video.js').read_bytes(),
                             (ROOT/'site/local-lesson-video.js').read_bytes())
            lock=json.loads((target/'provenance.json').read_text())
            self.assertNotIn('local-lesson-video.js',lock['files'])
            self.assertEqual(lock['output_sha256']['local-lesson-video.js'],
                             hashlib.sha256((target/'local-lesson-video.js').read_bytes()).hexdigest())
            for name,digest in lock['files'].items():
                self.assertEqual(hashlib.sha256((ROOT/'site/cefr-alg-c2'/name).read_bytes()).hexdigest(),digest)
                if name not in ('index.html','compare.html','technical.html'):
                    self.assertEqual(hashlib.sha256((target/name).read_bytes()).hexdigest(),digest)

    def test_local_video_import_refuses_missing_or_duplicate_player_anchor(self):
        html=(ROOT/'site/cefr-alg-c2/technical.html').read_text()
        anchor='<div id="fixed-media" hidden>'
        for changed in (html.replace(anchor,''),html.replace(anchor,anchor+anchor)):
            with self.subTest(anchor_count=changed.count(anchor)):
                with self.assertRaisesRegex(ValueError,'requires one anchor'):
                    site.add_local_video_controls(changed)

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
