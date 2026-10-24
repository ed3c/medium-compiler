class Solution:
    def subsets(self, nums: list[int]) -> list[list[int]]:
        n = len(nums)
        result = []
        path = []

        def visit(i: int) -> None:
            if i == n:
                result.append(path.copy())
                return

            visit(i + 1)
            path.append(nums[i])
            visit(i + 1)
            path.pop()

        visit(0)
        return result
