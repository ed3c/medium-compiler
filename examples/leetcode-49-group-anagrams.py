"""LeetCode 49 reference: 26-count tuple is a canonical anagram key.

Observed tests are owned by tests/test_alg_leetcode_v4.py; importing this
module alone does not prove execution, correctness or learner mastery.
"""
from typing import List


class Solution:
    def groupAnagrams(self, strs: List[str]) -> List[List[str]]:
        groups: dict[tuple[int, ...], list[str]] = {}

        for word in strs:
            counts = [0] * 26
            for char in word:
                counts[ord(char) - ord("a")] += 1

            key = tuple(counts)
            if key not in groups:
                groups[key] = []
            groups[key].append(word)

        return list(groups.values())
