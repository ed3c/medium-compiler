def subsets_of_size(nums: list[int], k: int) -> list[list[int]]:
    n = len(nums)
    result = []
    path = []

    def visit(i: int) -> None:
        if len(path) == k:
            result.append(path.copy())
            return
        if len(path) + (n - i) < k:
            return

        visit(i + 1)
        path.append(nums[i])
        visit(i + 1)
        path.pop()

    visit(0)
    return result
