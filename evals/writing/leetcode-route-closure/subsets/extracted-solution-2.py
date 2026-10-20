def subsets_iterative(nums: list[int]) -> list[list[int]]:
    result = [[]]
    for x in nums:
        old_count = len(result)
        for j in range(old_count):
            result.append(result[j] + [x])
    return result
