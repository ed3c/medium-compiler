import importlib.util
import itertools
import re
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".agents/skills/leetcode-mental/SKILL.md"
CONTRACT = ROOT / ".agents/skills/leetcode-mental/references/v4-contract.md"
EXAMPLE = ROOT / "examples/leetcode-49-group-anagrams-zero-context.md"
REFERENCE = ROOT / "examples/leetcode-49-group-anagrams.py"


def load_solution():
    spec = importlib.util.spec_from_file_location("leetcode49", REFERENCE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.Solution()


def groups_as_multiset(groups):
    return Counter(tuple(sorted(group)) for group in groups)


def independent_oracle(words):
    buckets = {}
    for word in words:
        key = "".join(sorted(word))
        buckets.setdefault(key, []).append(word)
    return groups_as_multiset(buckets.values())


class LeetcodeMentalSimulatorTests(unittest.TestCase):
    def test_skill_registration_is_separate_from_frozen_cefr(self):
        content = SKILL.read_text()
        self.assertIn("name: leetcode-mental", content)
        self.assertIn("cefr-alg-four-pass", content)
        self.assertIn("FULL_SINGLE_TURN", content)
        self.assertIn("v4-contract.md", content)
        self.assertIn("medium-reference.md", content)
        source = CONTRACT.read_text()
        for token in ("EXACTLY_5", "MENTAL_TRACE", "MASTERY_NOT_YET_OBSERVED", "/interactive", "English Interview Pack", "FIRST", "Same-turn"):
            self.assertIn(token.lower(), source.lower())

    def test_four_passes_and_five_anchors_precede_reference(self):
        content = EXAMPLE.read_text()
        anchors = re.search(r"## Five-Anchor Memory Card\n(.*?)\n## Invariant Memory", content, re.S).group(1)
        lines = [x for x in anchors.splitlines() if re.match(r"^\d+\. \*\*", x)]
        self.assertEqual(len(lines), 5)
        for title, line in zip(("Signal", "State", "Invariant", "Transition", "Bug Alarm"), lines):
            self.assertIn("**" + title + "**", line)
        sections = [
            "## Five-Anchor Memory Card", "## Invariant Memory", "## Program Movie",
            "## Reference Answer", "## Pass 1 — Whole Encounter",
            "## Pass 2 — Structural Compression", "## Pass 3 — Top-Down Back-Compilation",
            "## Pass 4 — Active Reconstruction + Oracle Diff", "## Correctness Proof",
            "## Complexity and Assumptions", "## Bug Alarm and Minimal Counterexample",
            "## What-if Pivot", "## English Interview Pack", "## Spaced Recall Card"
        ]
        starts = [content.index(s) for s in sections]
        self.assertEqual(starts, sorted(starts))
        self.assertIn("## Correctness Proof", content)
        self.assertIn("[" + '"a", "aa"' + "]", content)
        self.assertIn("MENTAL_TRACE", content)
        self.assertIn("MASTERY_NOT_YET_OBSERVED", content)
        self.assertIn("STOP HERE", content)
        self.assertIn("English", content)

    def test_group_anagrams_official_examples_and_boundaries(self):
        solve = load_solution().groupAnagrams
        for words in (
            ["eat","tea","tan","ate","nat","bat"],
            [""], ["a"], ["a", "aa"], ["", ""],
            ["abb", "bab", "bba", "ab", "ba"],
            ["zzz", "zz", "z", "zzz"]
        ):
            with self.subTest(words=words):
                self.assertEqual(groups_as_multiset(solve(words)), independent_oracle(words))
        self.assertEqual([len(g) for g in solve(["", "", ""])], [3])

    def test_count_key_matches_independent_sorted_oracle(self):
        solve = load_solution().groupAnagrams
        alphabet = "abc"
        items = [""]
        for width in range(1, 4):
            items.extend("".join(p) for p in itertools.product(alphabet, repeat=width))
        for k in range(1, 5):
            words = [items[(i * 11 + k) % len(items)] for i in range(k * 3)]
            self.assertEqual(groups_as_multiset(solve(words)), independent_oracle(words))

    def test_first_divergence_and_mutability(self):
        solve = load_solution().groupAnagrams
        self.assertEqual(len(solve(["a", "aa"])), 2)
        with self.assertRaises(TypeError):
            {[]: ["eat"]}
        source = REFERENCE.read_text()
        self.assertIn("tuple(counts)", source)
        self.assertIn('ord(char) - ord("a")', source)
        self.assertIn("return list(groups.values())", source)


if __name__ == "__main__":
    unittest.main()
