"""Focused contract routing checks for the source-agnostic LeetCode article profile.

These checks catch missing links and ownership regression; they do NOT
claim that a model wrote an accurate article or that Medium was published.
"""
import unittest
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEET = ROOT / ".agents/skills/leetcode-mental"
WRITER = ROOT / ".agents/skills/medium-writing/SKILL.md"
PROFILE = LEET / "references/article-content-profile.md"
CONSTRUCTION = LEET / "references/article-construction.md"
PROMPT = ROOT / "prompts/leetcode-medium-system.md"


class CompleteArticleRoutingTests(unittest.TestCase):
    def test_canonical_profile_and_invocation_are_reachable(self):
        self.assertTrue(PROFILE.is_file())
        self.assertTrue(CONSTRUCTION.is_file())
        self.assertTrue(PROMPT.is_file())
        # The selected profile must reach its method through a real relative link.
        targets = re.findall(r"\]\(([^)#]+)(?:#[^)]*)?\)", PROFILE.read_text())
        self.assertIn(CONSTRUCTION.resolve(), [(PROFILE.parent / p).resolve() for p in targets])
        for target in re.findall(r"\]\(([^)#]+)(?:#[^)]*)?\)", CONSTRUCTION.read_text()):
            self.assertTrue((CONSTRUCTION.parent / target).is_file(), target)
        for path in (
            LEET / "SKILL.md",
            LEET / "references/v4-contract.md",
            WRITER,
            ROOT / "AGENTS.md",
            ROOT / "README.md",
            ROOT / "writing-contract.md",
            ROOT / "prompts/medium-article.md",
            PROMPT,
        ):
            self.assertIn("article-content-profile.md", path.read_text(), str(path))

    def test_semantic_owner_is_distinct_from_formatting_owner(self):
        profile = PROFILE.read_text()
        writer = WRITER.read_text()
        self.assertIn("sole semantic Content Owner", profile)
        self.assertIn("entire source-grounded English technical narrative", profile)
        self.assertIn("full Traditional Chinese final draft", profile)
        self.assertIn("medium-writing is the Medium formatter and assembler", profile)
        self.assertIn("Formatter/Assembler", writer)
        self.assertIn("leetcode-mental", writer)
        self.assertIn("Stage 0–7", profile)
        self.assertIn("Stage 7 copies admitted bytes", profile)

    def test_generalized_profile_has_no_leetcode49_defaults(self):
        profile = PROFILE.read_text()
        prompt = PROMPT.read_text()
        for forbidden in ("Group Anagrams", "LeetCode 49", "count[26]", "exactly six figures", "six figures by default"):
            self.assertNotIn(forbidden, profile)
            self.assertNotIn(forbidden, prompt)
            self.assertNotIn(forbidden, CONSTRUCTION.read_text())
        self.assertIn("number of sections", profile)
        self.assertIn("Figures are derived", profile)
        self.assertIn("another problem with different constraints", profile)

    def test_language_and_publication_claims_remain_scoped(self):
        profile = PROFILE.read_text()
        self.assertIn("before translating", profile)
        self.assertIn("Traditional Chinese with exact English technical terms", profile)
        self.assertIn("NOT_RUN", profile)
        self.assertIn("PUBLISHED/NOT_RUN", profile)
        self.assertIn("alg-four", profile)

    def test_legacy_four_pass_route_is_preserved(self):
        v4 = (LEET / "references/v4-contract.md").read_text()
        self.assertIn("Mandatory 14-block LeetCode output order", v4)
        self.assertIn("FOUR_PASS_LOOP", v4)
        self.assertIn("Same-turn", v4)
        self.assertIn("ordinary v4 teaching profile", v4)
        self.assertIn("article-content-profile.md", v4)


if __name__ == "__main__":
    unittest.main()
