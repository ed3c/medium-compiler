import hashlib
import importlib.util
import json
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("alg_four_site",ROOT/"scripts/build_site.py")
site=importlib.util.module_from_spec(spec)
spec.loader.exec_module(site)
MANIFEST=ROOT/"references/learning/alg-four-group-anagrams.json"
NEW_SKILL=ROOT/".agents/skills/alg-four/SKILL.md"
LEGACY_LOCK=ROOT/"references/upstream/cefr-alg-skills-lock.json"


class DecisionTags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids=[]
        self.details=0
        self.scripts=[]
    def handle_starttag(self,tag,attrs):
        data=dict(attrs)
        if "data-alg-four-decision" in data:
            self.ids.append(data["data-alg-four-decision"])
        if tag=="details":
            self.details+=1
        if tag=="script":
            self.scripts.append(data.get("src"))


class AlgFourSourceAndDeliveryTests(unittest.TestCase):
    def test_skill_boundary_and_pinned_legacy_closure(self):
        self.assertIn("name: alg-four",NEW_SKILL.read_text())
        self.assertIn("Q52 B",NEW_SKILL.read_text())
        self.assertIn("NOT_OBSERVED",NEW_SKILL.read_text())
        self.assertIn("legacy",NEW_SKILL.read_text().lower())
        self.assertEqual(json.loads(LEGACY_LOCK.read_text())["revision"],
                         "b4b37fd95e9e654aa11c70ce76333aaeea683cd1")
        composition=(ROOT/".agents/skills/verify-learning-article/features/four-pass-composition.md").read_text()
        self.assertIn("alg-four/SKILL.md",composition)
        self.assertIn("alg-vocab-encounter",composition)
        self.assertIn("歷史 Frozen",composition)

    def test_all_decisions_are_receptive_and_productive(self):
        manifest=json.loads(MANIFEST.read_text())
        self.assertEqual(manifest["owner"],"alg-four")
        self.assertEqual(manifest["scope"],"FULL_ARTICLE_ALL_DECISIONS")
        self.assertEqual(manifest["learner_attempt"],"NOT_OBSERVED")
        ids=[d["id"] for d in manifest["decisions"]]
        self.assertEqual(ids,["D1","D2","D3","D4","D5"])
        for d in manifest["decisions"]:
            for key in ("source_concept","passive","context","active_cue","oracle","counterexample"):
                self.assertTrue(d[key])
        self.assertLess(len(manifest["priority_active_phrases"]),len(manifest["passive_vocabulary"]))

    def test_static_page_is_separate_source_pinned_and_honest(self):
        class RootLinks(HTMLParser):
            def __init__(self):
                super().__init__();self.hrefs=[]
            def handle_starttag(self,tag,attrs):
                if tag=="a":self.hrefs.append(dict(attrs).get("href"))
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/"dist"
            provenance=site.build(out)
            lesson=out/"alg-four/index.html"
            self.assertTrue(lesson.is_file())
            html=lesson.read_text()
            parser=DecisionTags();parser.feed(html)
            self.assertEqual(parser.ids,["D1","D2","D3","D4","D5"])
            self.assertEqual(parser.details,6)  # One oracle per decision and a final full-article oral reconstruction
            self.assertEqual(parser.scripts,[])
            self.assertIn("NOT_OBSERVED",json.dumps(provenance["alg_four"]))
            self.assertEqual((out/"alg-four/source.json").read_bytes(),MANIFEST.read_bytes())
            self.assertEqual(provenance["alg_four"]["manifest_sha256"],hashlib.sha256(MANIFEST.read_bytes()).hexdigest())
            source=(ROOT/json.loads(MANIFEST.read_text())["source"]["path"]).read_bytes()
            expected=hashlib.sha1(f"blob {len(source)}\0".encode()+source).hexdigest()
            self.assertEqual(provenance["alg_four"]["source_blob"],expected)
            self.assertEqual(provenance["alg_four"]["decision_ids"],parser.ids)
            self.assertIn('lang="en"',html)
            self.assertIn("does not record attempts",html)
            self.assertNotIn("localStorage",html)
            nav=RootLinks();nav.feed((out/"learning/index.html").read_text())
            self.assertIn("/alg-four/",nav.hrefs)
            self.assertTrue((out/"cefr-alg-c2/technical.html").is_file())

    def test_changed_source_and_missing_decision_refused(self):
        manifest=json.loads(MANIFEST.read_text())
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            path=root/manifest["source"]["path"];path.parent.mkdir(parents=True)
            path.write_text("tampered source",encoding="utf-8")
            target=root/"references/learning/alg-four-group-anagrams.json";target.parent.mkdir(parents=True)
            target.write_text(json.dumps(manifest),encoding="utf-8")
            with patch.object(site,"ROOT",root):
                with self.assertRaisesRegex(ValueError,"source blob changed"):
                    site.render_alg_four(root/"out")
            path.write_bytes((ROOT/manifest["source"]["path"]).read_bytes())
            manifest["decisions"][0]["oracle"]=""
            target.write_text(json.dumps(manifest),encoding="utf-8")
            with patch.object(site,"ROOT",root):
                with self.assertRaisesRegex(ValueError,"omitted a decision"):
                    site.render_alg_four(root/"out")


if __name__=="__main__":
    unittest.main()
