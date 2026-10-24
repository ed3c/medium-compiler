# Merge Intervals: why sorting leaves only one unfinished interval

Sort the intervals by their left endpoints. Walk through that order, keeping the merged result in a list. A new interval either extends the result's last interval or starts a new one. The reason this works is stronger than “nearby intervals are easier to compare”: once a gap appears, no later start can reach backward across it.

## What must the result preserve?

In [LeetCode 56, Merge Intervals](https://leetcode.com/problems/merge-intervals/), each input pair `[start, end]` describes a closed interval: every position from `start` through `end`, including both endpoints. There are between 1 and 10,000 pairs, and their integer endpoints satisfy `0 <= start <= end <= 10000`. Return non-overlapping intervals after merging overlaps. The returned intervals must cover exactly the positions covered by the input. Keeping everything inside one large interval would incorrectly fill gaps.

For example, `[1,4]` and `[4,6]` share position `4`, so their replacement is `[1,6]`. But `[1,4]` and `[5,6]` have a gap between them and remain separate. Integer endpoints do not mean that the interval contains only integer points. A zero-length interval such as `[12,12]` still covers its endpoint. The problem's examples explicitly count touching endpoints as overlap. [Original problem and boundary example](https://leetcode.com/problems/merge-intervals/).

Input order carries no useful guarantee. An interval that connects two others may arrive after both. We will return intervals in increasing start order and preserve the caller's input, although preserving it is an implementation choice rather than a requirement stated by the problem.

## Which order makes a decision permanent?

Suppose the current merged interval is `[left, right]`, and the next interval is `[start, end]`. If starts arrive in increasing order, then `left <= start`. Because each input also satisfies `start <= end`, two cases remain.

If `start <= right`, the new interval meets the existing coverage. Their union is `[left, max(right, end)]`: keep the earlier left endpoint and whichever right endpoint reaches farther. An interval contained inside the current one contributes no new positions. Assigning `right = end` unconditionally would incorrectly shorten coverage.

If `start > right`, there is a gap. Every later interval starts at least as far right as `start`, so none can overlap `[left, right]` or bridge that gap. The current interval is finished. Start a new interval at `[start, end]`.

This ordering also explains why only the last result interval needs inspection. Earlier result intervals already ended before a gap that the scan crossed. The current start and every future start are beyond those gaps. A growing last interval may reach farther right, but its left endpoint never moves backward to join an earlier result interval.

```text
Unordered input
    -> order by start
    -> inspect the last merged interval
         start <= last end -> keep left, extend right if needed
         start >  last end -> finish last, append a new interval
    -> return the merged list
```

Sorting by start is one way to obtain the needed order; it is not a claim that every correct algorithm must sort. The important permission is that future starts cannot be smaller than the start currently being processed.

## What does the Python state represent?

Use `ordered` for a start-sorted list and `merged` for the partial answer. A pair in `merged` represents all coverage in one connected group of processed intervals, not necessarily one original input pair. `merged[-1]` selects its last pair, and `merged[-1][1]` selects that pair's right endpoint. The earlier pairs are finished; the last pair can still grow.

The ordering expression is `sorted(intervals, key=lambda interval: interval[0])`. The `lambda` is a small function: give it a pair and it returns that pair's first number. The sort uses those numbers as its comparison keys. Thus `[8,10]` receives key `8`, while `[1,4]` receives key `1`. Python evaluates the key once per input pair and returns a new outer list in ascending key order. Equal starts can appear in either order for this algorithm: retaining the larger end produces the same union. [Python sorting documentation](https://docs.python.org/3/howto/sorting.html#key-functions).

A new outer list does not imply new inner pairs. Its elements still refer to the original pair objects. When adding an answer interval, `merged.append([start, end])` creates a fresh two-item list and places a reference to it at the end of `merged`. Later endpoint updates therefore modify an answer pair, not an input pair. Appending an original pair and then modifying it would share that mutation with the caller. Python assignment binds references rather than copying objects; list elements can be changed in place. [Python lists and assignment](https://docs.python.org/3.14/tutorial/introduction.html#lists).

## Program Movie: containment, extension, touching, and a gap

Consider this constructed input:

```text
intervals = [[8,10], [1,4], [2,3], [3,6], [6,8], [12,12]]
ordered   = [[1,4], [2,3], [3,6], [6,8], [8,10], [12,12]]
merged    = []
```

The call to `sorted` produces `ordered`; it does not rearrange `intervals`. The scan visits each pair in `ordered`, binding its two numbers to `start` and `end`.

For `[1,4]`, there is no last answer pair. Create `[1,4]` and append it. The answer is now `[[1,4]]`. No endpoint lookup is needed while the answer is empty.

For `[2,3]`, compare `2` with the last right endpoint `4`. They overlap, but `max(4,3)` is `4`. Writing that value back leaves `merged` equal to `[[1,4]]`. This is the containment case; moving the endpoint to `3` would lose coverage between `3` and `4`.

For `[3,6]`, `3 <= 4`, so write `max(4,6)`, which is `6`, into the last pair's end slot. `merged` becomes `[[1,6]]`. The stored left endpoint stays `1` because sorting already established that no new left endpoint is smaller.

For `[6,8]`, the start equals the stored end. The closed intervals share `6`; write `max(6,8) = 8`. The answer becomes `[[1,8]]`. For `[8,10]`, the same touching rule extends it to `[[1,10]]`.

For `[12,12]`, `12 > 10`. There is a gap, so append a fresh `[12,12]` without changing `[1,10]`. `merged` becomes `[[1,10], [12,12]]`. The loop then runs out of input and returns that list. The last interval is already stored, so there is no final “flush” operation.

```text
[]
  -- [1,4]: first pair --> [[1,4]]
  -- [2,3]: contained --> [[1,4]]
  -- [3,6]: extends   --> [[1,6]]
  -- [6,8]: touches   --> [[1,8]]
  -- [8,10]: touches  --> [[1,10]]
  -- [12,12]: gap     --> [[1,10], [12,12]]
```

## The complete Python implementation

```python
from typing import List


class Solution:
    def merge(self, intervals: List[List[int]]) -> List[List[int]]:
        ordered = sorted(intervals, key=lambda interval: interval[0])
        merged: List[List[int]] = []

        for start, end in ordered:
            if not merged or start > merged[-1][1]:
                merged.append([start, end])
            else:
                merged[-1][1] = max(merged[-1][1], end)

        return merged
```

`not merged` is true for an empty list. Python's `or` stops once its left side is true, so the first iteration never evaluates `merged[-1][1]` on an empty list. After that first append, the second condition tests for a strict gap. The `else` therefore includes equality, and `max` returns the larger of the existing end and the incoming end. [Python truth testing and short-circuit evaluation](https://docs.python.org/3.14/library/stdtypes.html#boolean-operations-and-or-not).

The type hints say that the method accepts and returns a list of integer pairs; they do not validate input at runtime. The method relies on the problem's valid-pair contract. It also returns `[]` for an empty input, although that input lies outside LeetCode's stated constraints.

## Why is the partial answer correct?

Use this English loop invariant at the checkpoint immediately after each iteration: “`merged` contains the exact union of the processed intervals as start-ordered, non-overlapping intervals; all but its last interval are final against every unprocessed interval.” Here, *union* means all positions covered by at least one interval. The union property describes the required coverage; the invariant additionally states when the partial answer is valid and which pieces can no longer change.

Before processing anything, the empty result covers exactly the empty set of processed intervals. There are no finalized pairs to contradict the invariant. The first iteration creates the initial interval, which is its own exact union.

For an overlap, replacing `[left,right]` with `[left,max(right,end)]` adds exactly the new interval's positions. There is no gap inside that replacement because `start <= right`. Its left boundary is unchanged, so it remains separated from all earlier answer pairs. No earlier pair becomes reachable by a later start. The invariant survives.

For a strict gap, appending `[start,end]` preserves all previous coverage and adds exactly the new interval. It is separate from the last pair, hence also from the pairs farther left. Future starts are at least `start`, so the old last pair is now final. The newly appended pair becomes the only unfinished pair.

Each iteration consumes one of the finite `n` input pairs. At termination every pair has been processed. Exact coverage and pairwise non-overlap now apply to the whole input, so `merged` is the required result. “Unfinished” describes possible future extension, not missing output data.

A tempting mistake is comparing each new start with the previous original interval's end. With `[[1,10], [2,3], [4,5]]`, that compares `4` with `3` and invents a gap. The current group actually reaches `10`, so all three belong to `[1,10]`. The answer must retain the largest reached endpoint of the whole group, which the `max` update maintains.

Dropping the sort also breaks the reasoning. For `[[5,6], [1,2]]`, the same code sees `1 <= 6` and keeps `[5,6]`, losing `[1,2]`. Its merge formula assumed that the stored left endpoint came first. Neither the formula nor the invariant authorizes using it in arbitrary input order.

## Where do the time and memory costs come from?

Let `n` be the input interval count and `k` the returned interval count, with `k <= n`. Count a bounded endpoint comparison, a reference read/write, and a fixed two-slot pair creation as constant work. Endpoints are bounded integers here, so arbitrary-length integer arithmetic is not part of this model. Big O gives an upper growth bound up to a constant factor; `O(n)` means that doubling the input increases that bound by a factor of two.

The scan visits `n` pairs. Each iteration performs a bounded number of endpoint reads, comparisons and writes. It never searches through `merged`; selecting its last slot uses the stored position directly. At most `n` new pairs are created, and exactly `k` remain in the result.

List append needs an aggregate argument. A Python list stores references in an array with some spare slots. Most appends fill one spare slot. When full, growth may allocate a larger array and copy its references. CPython reserves extra capacity proportional to the size, rather than copying on every append. Looking backward from a final capacity `C`, earlier large capacities shrink by a fixed ratio below one. For a doubling illustration they are `C/2, C/4, C/8, ...`; their sum is less than `C`. A smaller fixed growth fraction changes the constant multiplier, not the linear total. Thus at most `k` appends from an initially empty list cost `O(k)` altogether, including copies, though one particular append can cost more than constant time. This is the meaning of *amortized* cost. CPython's actual growth is milder than doubling. [CPython 3.14 list growth implementation](https://github.com/python/cpython/blob/v3.14.0/Objects/listobject.c#L98-L126).

Ordering dominates the worst-case time. Python's sort uses an adaptive merge-based algorithm; it recognizes already ordered stretches, called runs, and combines neighboring runs. To understand the `n log n` scale, consider a conceptual balanced merge plan. Combining sorted stretches of lengths `a` and `b` takes `O(a+b)` work: compare their front items, move the smaller, and advance its position until both are exhausted. Neither position moves backward. Across one level, each input item belongs to one merge, giving `O(n)` work. Stretch sizes grow as `1,2,4,8,...`; after `h` doublings they reach `2^h`. The number needed to reach `n` is about `log2(n)`, so `O(n)` work across `O(log n)` levels gives `O(n log n)`.

That balanced picture explains the cost mechanism, not the exact execution of `sorted`. CPython 3.14 uses natural runs and the Powersort merge strategy to keep its merge work within the same worst-case `O(n log n)` bound; existing order can reduce work. The library's scheduling rule and its bound are implementation facts used here, rather than claims that our six-pair trace exposes its internal merges. Key extraction adds `n` constant-cost reads. Together, ordering plus the `O(n)` scan gives worst-case `O(n log n)` time. [CPython sorting design, including its merge strategy](https://github.com/python/cpython/blob/v3.14.0/Objects/listsort.txt#L281-L378).

The returned output occupies `O(k)` space: one outer list and `k` fresh two-slot pairs, including proportional spare capacity. Excluding that output, the selected implementation still uses `O(n)` auxiliary space. `ordered` holds `n` references, and sorting can retain keys and temporary reference storage proportional to `n`. Loop variables occupy constant space. The objects shared with the input do not become `n` new pair allocations merely because `ordered` is new. Peak extra storage including output is `O(n+k)`, hence `O(n)` because `k <= n`.

Calling `intervals.sort(...)` instead would remove the separate sorted outer list but rearrange the caller's list. It would not establish constant auxiliary space: Python's sorting workspace can still grow with `n`. Changing mutation permission alone does not remove that cost. [Python sorting behavior](https://docs.python.org/3/howto/sorting.html#sorting-basics), [CPython sorting memory](https://github.com/python/cpython/blob/v3.14.0/Objects/listsort.txt#L12-L25).

## An alternative, and a constraint that changes the choice

A simpler way to construct the required order is repeated selection. Keep the input and a Boolean “used” marker for each pair. Scan all unused pairs to find a smallest remaining start, mark that pair used, then feed its endpoints into the same merge rule. Retain only the selected index and best start during each search. Choosing equal starts in any order remains valid because the end update keeps the maximum.

This also produces nondecreasing starts, so the earlier correctness proof applies to the merge step. But finding the next pair repeatedly costs more. With `n` markers checked on each of `n` selections, there are `n*n` marker checks. Even a version that scans only the remaining candidates must inspect `n + (n-1) + ... + 1` candidates. Pair the first and last counts: each pair totals `n+1`, yielding `n(n+1)/2`, which grows quadratically. This alternative takes `O(n^2)` time, `O(n)` auxiliary marker space, and `O(k)` output space with the same fresh-pair and append argument. It avoids relying on a sorting library, but does not improve this problem's worst-case resource bounds.

If a different input contract guarantees that intervals already arrive in nondecreasing start order, the useful adaptation is to skip ordering entirely. Feed each arriving pair directly into the same merge rule. The ordering premise now comes from the input producer; the gap proof and largest-end update remain unchanged. There are still `n` visits and at most `n` appends, so the scan takes `O(n)` time. With no `ordered` list and no sort workspace, it needs `O(1)` auxiliary state beyond the retained `O(k)` result. Preserving the caller's pairs still requires fresh answer pairs. This is preferable when the sorted-input guarantee is reliable; merely observing a few sorted examples is insufficient.

## English interview practice

**Why sort by the start?** “It makes future starts nondecreasing. After a strict gap, no future interval can connect to the interval we just finished.”

**Why keep the maximum end?** “The last answer pair represents an entire overlapping group. A contained interval must not shorten that group's coverage.”

**Why is equality overlap?** “The intervals are closed. If a start equals the current end, both intervals contain that endpoint.”

**What are the costs?** “For this Python implementation, sorting costs worst-case O(n log n), and the scan costs O(n) including amortized appends. Auxiliary space is O(n), plus O(k) output space.”

**What would change for sorted input?** “I would remove the ordering step, keep the same merge rule, and obtain O(n) time with O(1) auxiliary state excluding the output.”

## Master Map

```text
Closed intervals -> equality shares coverage -> merge at start <= last end
Unordered starts -> sort by start -> future starts never move backward
Processed coverage -> merged pairs -> only the last pair can still extend
Overlap -> preserve left and max end -> exact union without shrinking
Strict gap -> append fresh pair -> previous pair becomes final
Fresh answer pairs -> mutate output endpoints -> preserve input pairs
Sort + one scan -> O(n log n) worst-case time
Ordered references + sort workspace -> O(n) auxiliary space
k answer pairs -> O(k) output space
Guaranteed sorted input -> omit ordering -> O(n) time, O(1) auxiliary state
```
