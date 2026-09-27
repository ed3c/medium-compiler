from __future__ import annotations

import hashlib
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "articles/ai-engineer-learning-path.md"
CONTEXT = ROOT / "articles/ai-engineer-learning-path.context.json"
PARTS = ROOT / "articles/ai-engineer-learning-path.parts"
RESOURCES = ROOT / "references/open-access-resources.json"

LINK_RE = re.compile(r"\]\((https?://[^)]+)\)")
FENCE_RE = re.compile(r"(?ms)^```.*?^```\s*$")
TABLE_LINE_RE = re.compile(r"(?m)^\s*\|.*\|\s*$")


def git_blob_sha(payload: bytes) -> str:
    header = f"blob {len(payload)}\0".encode()
    return hashlib.sha1(header + payload).hexdigest()


class ReaderNavigationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.article = ARTICLE.read_text(encoding="utf-8")
        cls.context = json.loads(CONTEXT.read_text(encoding="utf-8"))
        cls.resources = json.loads(RESOURCES.read_text(encoding="utf-8"))

    def test_final_article_has_no_markdown_table(self):
        prose = FENCE_RE.sub("", self.article)
        self.assertIsNone(TABLE_LINE_RE.search(prose))

    def test_primary_case_is_ops_reconciliation(self):
        self.assertIn("Ops Reconciliation Copilot", self.article)
        self.assertIn("mapping_proposal", self.article)
        self.assertNotIn("doc_assistant.py", self.article)
        self.assertNotIn("billing-v1-01", self.article)

    def test_no_paid_or_owner_only_links(self):
        for value in ("gotop.com.tw", "oreilly.com", "amazon.", "/workspace"):
            self.assertNotIn(value, self.article)

    def test_every_reader_link_is_allowlisted(self):
        allowed = {item["url"] for item in self.resources["resources"]}
        actual = set(LINK_RE.findall(self.article))
        self.assertTrue(actual)
        self.assertEqual(actual - allowed, set())

    def test_resource_manifest_is_open_access(self):
        for item in self.resources["resources"]:
            self.assertEqual(item["reader_access"], "open")

    def test_companion_only_resource_is_absent(self):
        self.assertNotIn("https://github.com/chiphuyen/aie-book", self.article)

    def test_core_learning_links_are_substantive(self):
        resources = {item["url"]: item for item in self.resources["resources"]}
        required = [
            "https://web.stanford.edu/~jurafsky/slp3/7.pdf",
            "https://web.stanford.edu/~jurafsky/slp3/8.pdf",
            "https://web.stanford.edu/~jurafsky/slp3/11.pdf",
            "https://huggingface.co/learn/llm-course/chapter11/1",
            "https://huggingface.co/learn/llm-course/chapter11/5",
        ]
        for url in required:
            self.assertIn(url, resources)
            self.assertEqual(resources[url]["learning_depth"], "substantive")
        self.assertIn("happy-llm/blob/main/docs/chapter5", self.article)
        self.assertIn("happy-llm/blob/main/docs/chapter6", self.article)
        self.assertIn("happy-llm/blob/main/docs/chapter7", self.article)

    def test_context_has_ten_reader_decisions(self):
        self.assertEqual(self.context["decision_count"], 10)
        self.assertEqual(len(self.context["decisions"]), 10)
        self.assertEqual(self.context["source_case"]["repo"], "ed3c/ops-reconciliation-copilot")

    def test_parts_reassemble_exact_article(self):
        manifest = json.loads((PARTS / "manifest.json").read_text(encoding="utf-8"))
        combined = "".join((PARTS / name).read_text(encoding="utf-8") for name in manifest["part_order"])
        self.assertEqual(combined, self.article)

    def test_part_git_blobs_match_manifest(self):
        manifest = json.loads((PARTS / "manifest.json").read_text(encoding="utf-8"))
        for item in manifest["parts"]:
            payload = (PARTS / item["path"]).read_bytes()
            self.assertEqual(git_blob_sha(payload), item["git_blob"])
        self.assertEqual(git_blob_sha(ARTICLE.read_bytes()), manifest["article_git_blob"])

    def test_stage_zero_is_tableless(self):
        plan = (ROOT / "articles/ai-engineer-learning-path.stage-00.md").read_text(encoding="utf-8")
        prose = FENCE_RE.sub("", plan)
        self.assertIsNone(TABLE_LINE_RE.search(prose))
        self.assertIn("A10", plan)

    def test_prompt_and_skill_encode_medium_policy(self):
        prompt = (ROOT / "prompts/medium-article.md").read_text(encoding="utf-8")
        entry = (ROOT / ".agents/skills/medium-writing/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("writing-contract.md", entry)
        contract = (ROOT / "writing-contract.md").read_text(encoding="utf-8")
        self.assertIn("native-no-tables", prompt)
        self.assertIn("open-access-only", prompt)
        self.assertIn("Medium-native final body", contract)
        self.assertIn("Reader-link access gate", contract)

    def test_card_adapter_does_not_copy_v71_prompt(self):
        s = (ROOT / "references/card-context-v7.1.md").read_text(encoding="utf-8")
        self.assertIn("7f3019f4b41a90728cd48a523d742c7c59721bf6", s)
        self.assertFalse((ROOT / "governance/CARD_PROTOCOL_V7_1.md").exists())


if __name__ == "__main__":
    unittest.main()
