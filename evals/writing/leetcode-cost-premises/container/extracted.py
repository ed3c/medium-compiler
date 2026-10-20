def max_area_all_pairs(height: list[int]) -> int:
    n = len(height)
    best = 0
    for i in range(n - 1):
        for j in range(i + 1, n):
            area = (j - i) * min(height[i], height[j])
            best = max(best, area)
    return best


class Solution:
    def maxArea(self, height: list[int]) -> int:
        left = 0
        right = len(height) - 1
        best = 0

        while left < right:
            left_height = height[left]
            right_height = height[right]
            area = (right - left) * min(left_height, right_height)
            best = max(best, area)

            if left_height <= right_height:
                left += 1
            else:
                right -= 1

        return best


def max_area_at_positions(x: list[int], height: list[int]) -> int:
    left = 0
    right = len(height) - 1
    best = 0
    while left < right:
        left_height = height[left]
        right_height = height[right]
        area = (x[right] - x[left]) * min(left_height, right_height)
        best = max(best, area)
        if left_height <= right_height:
            left += 1
        else:
            right -= 1
    return best
