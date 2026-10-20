"""Execute the published solution, without treating runtime checks as prose review."""
from collections import defaultdict
from pathlib import Path
import random
import re
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def article_codes(language):
    path = ROOT / ("articles/leetcode-49-group-anagrams" + language + ".md")
    blocks = re.findall(r"(?ms)^(?:```|~~~)python\s*\n(.*?)^(?:```|~~~)\s*$",
                        path.read_text())
    solutions = [block for block in blocks if "def groupAnagrams(" in block]
    if not solutions:
        raise AssertionError(f"Expected complete solutions in {path}")
    return solutions


def normalized(groups):
    return sorted(tuple(sorted(group)) for group in groups)


def solution(code):
    namespace = {}
    exec(compile(code, "<article solution>", "exec"), namespace)
    return namespace["Solution"]().groupAnagrams


class ArticleSolutionTests(unittest.TestCase):
    def test_bilingual_code_and_literal_grouping_contract(self):
        codes = article_codes(".en")
        self.assertEqual(codes, article_codes(""))
        cases = [
            (["eat", "tea", "tan", "ate", "nat", "bat"],
             [["eat", "tea", "ate"], ["tan", "nat"], ["bat"]]),
            (["", "", "a", "a", "aa", "b"], [["", ""], ["a", "a"], ["aa"], ["b"]]),
            (["ab", "aab", "ba", "aba"], [["ab", "ba"], ["aab", "aba"]]),
            (["z" * 100, "a" * 100, "z" * 100], [["z" * 100, "z" * 100], ["a" * 100]]),
            ([], []),
        ]
        for code in codes:
            group = solution(code)
            for words, expected in cases:
                with self.subTest(words=words):
                    before = words.copy()
                    self.assertEqual(normalized(group(words)), normalized(expected))
                    self.assertEqual(words, before)

    def test_variable_lengths_against_sorting_oracle(self):
        group = solution(article_codes(".en")[0])
        rng = random.Random(49)
        for _ in range(80):
            words = ["".join(rng.choices("abcxyz", k=rng.randrange(21)))
                     for _ in range(rng.randrange(1, 35))]
            words += [words[0], words[0][::-1]]
            expected = {}
            for word in words:
                expected.setdefault("".join(sorted(word)), []).append(word)
            self.assertEqual(normalized(group(words)), normalized(expected.values()))

    def test_main_solution_uses_factory_only_for_new_keys(self):
        misses = []
        factories = []

        class ObservedDefaultDict(defaultdict):
            def __init__(self, factory):
                factories.append(factory)
                super().__init__(factory)

            def __missing__(self, key):
                value = super().__missing__(key)
                misses.append((key, value, self[key] is value))
                return value

        with patch("collections.defaultdict", ObservedDefaultDict):
            group = solution(article_codes(".en")[0])
        result = group(["eat", "tea", "bat", "", ""])
        self.assertEqual(factories, [list])
        self.assertEqual(len(misses), 3)
        self.assertTrue(all(stored for _, _, stored in misses))
        self.assertEqual(len({id(value) for _, value, _ in misses}), 3)
        self.assertEqual(normalized(result), normalized([["eat", "tea"], ["bat"], ["", ""]]))


if __name__ == "__main__":
    unittest.main()
