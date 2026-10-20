import hashlib
import importlib.util
import json
import re
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("alg_four_site",ROOT/"scripts/build_site.py")
site=importlib.util.module_from_spec(spec)
spec.loader.exec_module(site)
MANIFEST=ROOT/"references/learning/alg-four-group-anagrams.json"
SKILL=ROOT/".agents/skills/alg-four/SKILL.md"
LEGACY_LOCK=ROOT/"references/upstream/cefr-alg-skills-lock.json"


class AnnotationParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.indices=[]
        self.roles=[]
        self.words=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if "data-outline-index" in a:
            self.indices.append(int(a["data-outline-index"]))
        if "data-alg-four-role" in a:
            self.roles.append(a["data-alg-four-role"])


class AlgFourSourceAndDeliveryTests(unittest.TestCase):
    def test_owner_split_and_frozen_skill_source_unchanged(self):
        self.assertIn("name: alg-four",SKILL.read_text())
        self.assertIn("2000",SKILL.read_text())
        self.assertIn("NOT_OBSERVED",SKILL.read_text()+
                      (ROOT/".agents/skills/alg-four/references/lesson-contract.md").read_text())
        lock=json.loads(LEGACY_LOCK.read_text())
        self.assertEqual(lock["revision"],"b4b37fd95e9e654aa11c70ce76333aaeea683cd1")
        self.assertEqual(len(lock["files"]),12)
        self.assertFalse((ROOT/".agents/skills/alg-leetcode-mental-simulator/SKILL.md").exists())
        self.assertIn("name: leetcode-mental",
                      (ROOT/".agents/skills/leetcode-mental/SKILL.md").read_text())
        self.assertTrue((ROOT/".agents/skills/alg-leetcode-mental-simulator/references/medium-reference.md").is_file())
        composition=(ROOT/".agents/skills/verify-learning-article/features/four-pass-composition.md").read_text()
        self.assertIn("alg-four/SKILL.md",composition)
        self.assertIn("alg-vocab-encounter",composition)
        self.assertIn("原文",composition)

    def test_cumulative_2000_admission_without_fabricated_complete_corpus(self):
        data=json.loads(MANIFEST.read_text())
        self.assertEqual(data["schema_version"],"alg-four-paragraph-annotations@2")
        self.assertEqual(data["format"],"source_preserved_with_inline_zh_tw_annotations")
        self.assertEqual(data["source"]["technical_authority"],"leetcode-mental")
        self.assertEqual(data["source"]["writing_authority"],"medium-writing")
        self.assertEqual(data["learning_policy"]["goal_active_lexical_items"],2000)
        self.assertEqual(data["learning_policy"]["goal_linked_english_sentences"],2000)
        self.assertEqual(data["learning_policy"]["learner_evidence"],"NOT_OBSERVED")
        self.assertNotIn("pass1",data)
        self.assertNotIn("pass2",data)
        self.assertNotIn("pass3",data)
        notes=data["paragraph_annotations"]
        self.assertEqual([n["paragraph_index"] for n in notes],list(range(75)))
        self.assertEqual({n["kind"] for n in notes},{"PASSIVE","PASSIVE_AND_ACTIVE"})
        self.assertEqual({d["id"] for d in data["decisions"]},{"D1","D2","D3","D4","D5"})
        ids=[x["id"] for x in data["active_items"]]
        self.assertEqual(len(ids),len(set(ids)))
        self.assertLess(len(ids),2000)
        for item in data["active_items"]:
            self.assertGreater(len(item["english_sentence"].split()),5)
            self.assertIn(item["decision_id"],{d["id"] for d in data["decisions"]})
            self.assertGreaterEqual(item["paragraph_index"],0)
            self.assertLess(item["paragraph_index"],len(notes))

    def test_original_paragraph_order_and_html_are_preserved(self):
        data=json.loads(MANIFEST.read_text())
        source=(ROOT/data["source"]["path"]).read_bytes()
        source_blob=hashlib.sha1(f"blob {len(source)}\0".encode()+source).hexdigest()
        self.assertEqual(source_blob,data["source"]["git_blob"])
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/"dist"
            result=site.build(out)["alg_four"]
            full=(out/"alg-four/index.html").read_text()
            self.assertIn('lang="zh-Hant"',full)
            self.assertIn("<pre><code>",full)
            parser=AnnotationParser()
            parser.feed(full)
            self.assertEqual(parser.indices,list(range(75)))
            self.assertEqual(parser.roles.count("PASSIVE_AND_ACTIVE"),
                             sum(n["kind"]=="PASSIVE_AND_ACTIVE" for n in data["paragraph_annotations"]))
            self.assertEqual(result["annotated_paragraphs"],75)
            self.assertEqual(result["active_items_collected"],len(data["active_items"]))
            self.assertEqual(result["active_vocabulary_goal"],2000)
            self.assertTrue(result["source_article_unchanged"])
            self.assertEqual(result["learning_evidence"],"NOT_OBSERVED")
            self.assertEqual((out/"alg-four/source.json").read_bytes(),MANIFEST.read_bytes())
            article=re.search(r'<article class="article alg-four-source">(.*?)</article>',full,re.S)
            self.assertIsNotNone(article)
            self.assertNotIn('class="alg-four-annotation"',article.group(1))
            # Only anchor attributes are added to the original rendered blocks.
            projection=re.sub(r' id="alg-(?:p|heading)-\d+" data-alg-(?:four-index|heading)="\d+"','',article.group(1))
            self.assertEqual(projection,site.markdown(source.decode("utf-8")))
            self.assertIn('class="alg-four-sidebar"',full)
            self.assertIn('id="alg-p-0"',article.group(1))
            self.assertIn('href="#alg-p-74"',full)
            self.assertIn('/assets/alg-four.js',full)
            self.assertIn('/assets/alg-four.css',full)
            self.assertIn('alg-active-term',full)
            self.assertEqual(result["annotation_projection"],"right_outline")
            self.assertGreater(result["heading_count"],0)
            self.assertIn('/alg-four/',(out/"learning/index.html").read_text())
            self.assertTrue((out/"cefr-alg-c2/technical.html").is_file())

    def test_refuse_source_drift_omitted_annotation_or_wrong_lexicon(self):
        data=json.loads(MANIFEST.read_text())
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            source=root/data["source"]["path"]
            source.parent.mkdir(parents=True)
            source.write_text("tampered source")
            meta=root/"references/learning/alg-four-group-anagrams.json"
            meta.parent.mkdir(parents=True)
            meta.write_text(json.dumps(data))
            with patch.object(site,"ROOT",root):
                with self.assertRaisesRegex(ValueError,"source blob changed"):
                    site.render_alg_four(root/"out")
            source.write_bytes((ROOT/data["source"]["path"]).read_bytes())
            data["paragraph_annotations"].pop()
            meta.write_text(json.dumps(data))
            with patch.object(site,"ROOT",root):
                with self.assertRaisesRegex(ValueError,"every original prose paragraph"):
                    site.render_alg_four(root/"out")
            data=json.loads(MANIFEST.read_text())
            data["active_items"][0]["english_sentence"]=""
            meta.write_text(json.dumps(data))
            with patch.object(site,"ROOT",root):
                with self.assertRaisesRegex(ValueError,"source paragraph, decision or sentence"):
                    site.render_alg_four(root/"out")


if __name__=="__main__":
    unittest.main()
