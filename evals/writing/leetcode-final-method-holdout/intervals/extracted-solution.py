class Solution:
    def merge(self, intervals: list[list[int]]) -> list[list[int]]:
        ordered = sorted(intervals, key=lambda pair: pair[0])
        merged = []

        for start, end in ordered:
            if not merged or start > merged[-1][1]:
                merged.append([start, end])
            else:
                merged[-1][1] = max(merged[-1][1], end)

        return merged
