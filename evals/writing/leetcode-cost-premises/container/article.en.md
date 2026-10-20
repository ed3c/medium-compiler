# Container With Most Water: why the shorter wall can be discarded

Two tall walls can make a poor container if they stand too close together. In LeetCode 11, the decision is about a pair's height and distance together.

## Turn the picture into a number

The input `height` lists vertical wall heights at positions `0, 1, ..., n - 1`. Choose two distinct positions `i < j`; the ground and those two walls form an upright container. Return the largest capacity, as an integer, rather than the wall positions. The statement allows `2 <= n <= 100000` and `0 <= height[i] <= 10000`. It does not ask us to change the input, and the solutions below leave it unchanged. Empty and one-wall inputs are outside this contract. [LeetCode problem statement](https://leetcode.com/problems/container-with-most-water/).

The water cannot rise above the shorter wall: it would spill over that side. The horizontal distance is `j - i`, counting gaps rather than walls. Thus a pair's capacity is its rectangular cross-sectional area:

`area(i, j) = (j - i) * min(height[i], height[j])`.

For the constructed input `[2, 5, 1, 4]`, walls at positions `1` and `3` give width `2`, water height `4`, and area `8`. Positions `0` and `3` are farther apart, but give only `3 * 2 = 6`. The tallest wall alone does not determine the answer. Intermediate walls do not subtract their height from this rectangle; this problem chooses two boundaries, rather than adding pockets of trapped rainwater.

If both chosen heights are zero, their area is zero. When all heights are zero, zero is the correct maximum. This makes `best = 0` a valid initial value for every legal input.

## First keep every possible pair

A direct solution fixes the left position and tries every position to its right. `best` retains the largest area evaluated so far; keeping the areas of old pairs would add storage without helping the next comparison.

```python
def max_area_all_pairs(height: list[int]) -> int:
    n = len(height)
    best = 0
    for i in range(n - 1):
        for j in range(i + 1, n):
            area = (j - i) * min(height[i], height[j])
            best = max(best, area)
    return best
```

`range(i + 1, n)` produces positions from `i + 1` through `n - 1`. It excludes `n`, so every lookup is valid, every pair has distinct walls, and a pair is not repeated in reverse. `min(a, b)` returns the smaller argument; `max(best, area)` returns the larger. Neither call changes the list. These are the two-argument forms of the documented [Python built-in functions](https://docs.python.org/3.14/library/functions.html).

For `[2, 5, 1, 4]`, the six pairs in execution order have areas `2, 2, 6, 1, 8, 1`. The corresponding `best` values are `2, 2, 6, 6, 8, 8`; returning `8` therefore follows from examining every candidate.

The number of candidates matters at the upper input limit. To count them, position `0` has `n - 1` partners, position `1` has `n - 2`, and the last useful left position has `1`. Add these counts forward and backward: each matched sum is `n`, and there are `n - 1` such sums. That double-counts the candidates, giving `n * (n - 1) / 2` pairs. At `n = 100000`, that is `4,999,950,000` area evaluations. We need a reason to skip candidates without losing the maximum.

## Evaluate the widest remaining pair, then remove a wall

Keep two indices, `left` and `right`, initially at opposite ends. These indices are called two pointers here; they are ordinary integer positions, not copied sublists or Python memory addresses. The inclusive interval from `left` to `right` contains the positions still available for unresolved pairs. Evaluate its endpoint pair before discarding anything.

Suppose `height[left] <= height[right]`. The pair just measured has area `(right - left) * height[left]`. Consider any pair that keeps `left` and replaces `right` with an inner position `k`. Its width `k - left` is smaller, and its water height cannot exceed `height[left]`, even if the new wall is much taller. Because heights are nonnegative,

`area(left, k) <= (k - left) * height[left] <= (right - left) * height[left]`.

So no such pair can beat the endpoint area we already recorded. Every remaining candidate involving `left` can be discarded together by increasing `left` by one. This is a bound on all its possible partners, not a prediction that the next wall is taller or that the next area will improve.

When the right wall is shorter, the same argument applies with the sides reversed: keeping `right` while moving the left endpoint inward cannot improve the area just measured, so decrease `right`. If the heights are equal, either endpoint may be discarded by the same inequality. The code chooses to discard the left one. Zero-height ties remain safe because every pair keeping either zero-height wall has area zero.

This rule deliberately gives up width. It removes a wall only after proving that the lost pairs are already covered by a recorded value. Always moving the taller wall lacks that proof. On `[1, 3, 3]`, the outer pair gives area `2`. Moving the taller right wall inward then gives area `1`, and the process returns `2`; it misses positions `1` and `2`, whose area is `3`. This is a smallest counterexample by number of walls: with two walls, the only candidate is evaluated before any move.

## Follow the state all the way to the return

On `[2, 5, 1, 4]`, begin with `(left, right, best) = (0, 3, 0)`.

Read `height[0] = 2` and `height[3] = 4`. Width is `3`, water height is `2`, and area is `6`. Replace `best` with `6` before moving. Since `2 <= 4`, increase `left`: the new state is `(1, 3, 6)`. The skipped pairs keeping position `0` cannot exceed the measured `6`.

Now read heights `5` and `4`. Width is `2`, so area is `8`. `best` becomes `8`. The left wall is taller, so decrease `right`, giving `(1, 2, 8)`. In particular, pair `(2, 3)` is safely discarded: its width is `1`, and its height cannot exceed the discarded right wall's height `4`.

Read heights `5` and `1`. Width is `1`, giving area `1`. The comparison leaves `best` at `8`. Decrease `right` again, reaching `(1, 1, 8)`. The condition `left < right` is now false: one position cannot supply two distinct walls. Return `8`.

A separate tie witness, `[3, 3, 3]`, starts with area `6`, moves left, measures area `3`, moves left again and returns `6`. A move can reduce the current area; the saved maximum prevents losing the earlier answer.

```python
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
```

The `while` statement tests its condition before each execution of the body; `if` selects exactly one branch. Thus exactly one index changes per iteration. [Python compound statements](https://docs.python.org/3.14/reference/compound_stmts.html).

Reading `height[left]` retrieves an element without removing it. Assigning that value to `left_height` binds a local name; it does not copy the list. Python integers are immutable: `left += 1` computes an integer value and rebinds `left`, rather than changing an integer stored inside `height`. An assignment targeting an item such as `height[left]` would write that item; no such assignment occurs here. The input remains available to the caller. [Python assignments](https://docs.python.org/3.14/reference/simple_stmts.html#assignment-statements), [numeric types](https://docs.python.org/3.14/library/stdtypes.html#numeric-types-int-float-complex).

## What stays true at every checkpoint

The area formula describes one pair. Correctness of the whole search needs a separate loop invariant, a statement that remains true at a chosen checkpoint. At the start of every `while` condition check: `best` is the maximum area among pairs already evaluated, or zero if none were evaluated; every pair with an endpoint outside the current interval has area at most `best`.

Initially there are no positions outside `[0, n - 1]`, so the second claim has no excluded pairs to check. The first claim holds because `best` is zero and all legal areas are nonnegative.

During an iteration, measuring the endpoints and updating `best` preserves the first claim. The discard inequality proves that every newly excluded pair has area at most the area just measured, which is at most the updated `best`. Previously excluded pairs remain covered because `best` never decreases. These facts reestablish the invariant for either branch, including equal heights.

The distance `right - left` starts at `n - 1` and decreases by exactly one each time. It reaches zero after `n - 1` iterations. At that point no pair has both endpoints in the remaining interval, so every legal pair has been evaluated or covered by the invariant. Since `best` also comes from actual candidates, except for the harmless initial zero, it equals the required maximum.

## Account for operations and stored values

Let `n` be the number of walls. We compare growth using a bounded-integer, unit-cost model: one integer comparison, addition, subtraction, multiplication, local binding, or indexed list access costs a bounded amount; storing one such scalar or reference uses one unit. For this statement, indices are below `100000`, heights are at most `10000`, and an area is at most `99999 * 10000 = 999,990,000`. These values fit within a fixed number of machine-sized integer pieces. This model counts work, not equal physical time for all Python expressions. Python can represent larger integers, but an unbounded increase in their digit count would require a different arithmetic cost model.

The list-access assumption has a concrete implementation basis. In CPython v3.14.0, a list stores element references in indexed slots; fetching slot `i` accesses that slot rather than walking through the preceding `i` elements. Its length is stored, so `len(height)` does not count the walls one by one. These properties support bounded work for this access pattern, with an ordinary list and no concurrent mutation. [CPython list implementation](https://github.com/python/cpython/blob/v3.14.0/Objects/listobject.c), [list structure and access macros](https://github.com/python/cpython/blob/v3.14.0/Include/cpython/listobject.h).

Each two-pointer iteration makes two list reads, a fixed number of bounded arithmetic and comparison operations, and one index update. `min` and `max` each receive two scalar values, so their comparison work does not grow with `n`. There are exactly `n - 1` iterations and `n` loop-condition checks; setup and return add fixed work. Thus total work is bounded by a constant times `n` plus a constant. We write this as `O(n)` time. Big O expresses an upper growth bound, ignoring fixed multipliers; here the exact iteration count also gives linear growth, not just an upper limit.

Only a fixed number of local names and temporary integer results are live at once. Later iterations replace earlier values rather than retaining a history. There is no recursion, growing collection or copied input. Auxiliary space, meaning storage added beyond the supplied input and returned result, is `O(1)`. Transient arithmetic values also occupy only a fixed number of bounded units at once. The returned single integer is `O(1)` output space; the caller's original list already occupies `O(n)` units and is excluded from auxiliary space.

The all-pairs solution uses the same bounded reads, arithmetic and two-argument comparisons for each candidate. Its `n * (n - 1) / 2` evaluations therefore give `O(n²)` time: for growing `n`, the squared term dominates. Its space is still `O(1)` auxiliary and `O(1)` output. A Python `range` retains its start, stop and step rather than materializing all indices. The outer loop keeps one range and its current position; each inner range replaces the previous one, and no pair list or area history survives. Even though many inner ranges are created over time, only a fixed number are live simultaneously. The `n - 1` inner-range setups store only these fixed fields, and each step advances a bounded integer index. Under the stated elementary model, those setups add linear work and each step adds fixed work per candidate; neither exceeds the quadratic total. [Python range objects](https://docs.python.org/3.14/library/stdtypes.html#ranges).

For tiny inputs, all-pairs is useful as a checking oracle: it is easy to inspect because it directly enumerates the contract's candidates. It also remains a starting point if a new scoring rule destroys the shorter-wall bound; that changed rule would need its own costs and proof. Under the present contract and large input limit, the two-pointer solution avoids billions of evaluations with no extra growing storage.

## Change the spacing, preserve the reason

Suppose the input supplies strictly increasing integer coordinates `x`, in the same order as `height`, with `0 <= x[i] <= 1000000000`. Keep the original height and length limits. Walls no longer stand one unit apart. Reusing `right - left` would calculate the number of gaps, rather than their total width.

Replace the width by `x[right] - x[left]`. On `x = [0, 1, 100]` and `height = [1, 3, 2]`, the outer pair has area `100`; moving the shorter left wall reveals area `99 * 2 = 198`. The answer is `198`. The original index-width calculation would instead return `2`.

```python
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
```

Strictly increasing coordinates ensure that moving either endpoint inward decreases physical width. The shorter-wall height bound is unchanged, so the discard inequality and invariant still hold with coordinate differences replacing index differences. The pointers still move by one position per iteration: the numerical size of a coordinate gap does not add iterations.

The adaptation adds two coordinate-slot reads per iteration; subtracting their values replaces the old index subtraction. It adds no growing loop or collection. Coordinates and areas remain bounded, with area at most `1000000000 * 10000 = 10¹³`, fitting a fixed number of scalar units under the same model. Consequently the `n - 1` iterations still give `O(n)` time and fixed live state gives `O(1)` auxiliary and output space. The additional coordinate list is supplied input, using another `O(n)` units, rather than a list allocated by the function. This argument assumes coordinates arrive ordered and matched to heights; the function neither sorts nor verifies that different contract.

## Interview English and the master map

Why move the shorter wall? Keeping it caps the water height while moving the other endpoint inward reduces width. All such pairs are bounded by the endpoint area already measured.

Does the next pair have to improve? No. `best` remembers earlier candidates, so the current area may decrease.

What happens on equal heights? Either endpoint can be removed safely. This implementation removes the left one.

Why is the time linear? The index distance decreases from `n - 1` to zero, once per constant-work iteration.

What does constant space exclude? It excludes the caller's input list. The function adds a fixed set of scalar locals and returns one integer.

The master map is a chain of reasons: two wall positions determine width; the shorter wall determines water height; their product evaluates a candidate. An evaluated candidate bounds every inward pair retaining its shorter wall. Removing that wall shrinks the unresolved interval while `best` covers excluded pairs. When the interval cannot contain two walls, `best` covers every legal choice.
