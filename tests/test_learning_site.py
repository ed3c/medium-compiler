import importlib.util, json, tempfile
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("build_site",ROOT/"scripts/build_site.py")
site=importlib.util.module_from_spec(spec);spec.loader.exec_module(site)

class LearningSiteTests(unittest.TestCase):
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
