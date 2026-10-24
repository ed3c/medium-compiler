# Merge Intervals: when a gap becomes permanent

Suppose the input is `[[8,10],[1,7],[3,4],[7,8],[12,12],[12,14]]`. The required answer is `[[1,10],[12,14]]`. Several short intervals combine into the first stretch. The second stretch begins after a gap. To produce that answer reliably, the program needs a way to tell a permanent gap from one that a later interval could still fill.

## What counts as the same coverage?

An interval `[start, end]` includes both endpoints and every point between them. Thus `[1,2]` and `[2,3]` share the point `2` and must become `[1,3]`. `[1,2]` and `[3,4]` have a gap and remain separate. Integer endpoints do not turn the intervals into sets of integers; the gap between `2` and `3` still matters. A single-point interval such as `[12,12]` is valid.

LeetCode 56 accepts between `1` and `10^4` intervals. Each has exactly two integer endpoints satisfying `0 <= start <= end <= 10^4`. Input order is not promised. The result must have no overlapping intervals while covering exactly what the input covers. Adding points in a gap would be incorrect. The shared-endpoint rule appears explicitly in the [problem statement](https://leetcode.com/problems/merge-intervals/).

Think of coverage as the collection of all points included by at least one interval; mathematicians call this the union. Two input lists are equivalent for this task when their unions are equal. Their original order and repeated copies do not affect the union. This is a property of the required answer, before any algorithm has been chosen.

The statement does not promise that callers want their input rearranged or edited. The implementation below therefore preserves both the input list's order and its inner pairs. It returns new pairs. It also returns `[]` for an empty input, though empty input lies outside the stated constraints.

## Sort before deciding that a stretch has ended

An initial idea is to compare each arriving interval with the last interval already saved. In the order `[[5,6],[1,2],[2,5]]`, the first two appear separate, but the third joins them into `[1,6]`. A gap observed in arbitrary input order is insufficient evidence to finish a component. Here a component means one uninterrupted stretch formed by merging intervals that connect, possibly through other intervals.

Sort by increasing start instead. The same input becomes `[[1,2],[2,5],[5,6]]`. Once starts move only to the right, a new interval beginning after the current stretch ends proves that all later intervals also begin too far right to reach that stretch.

Let the current stretch be `[left, right]`, and the next sorted interval be `[start, end]`. Sorting gives `left <= start`. If `start <= right`, the intervals meet or overlap. Their union has no hole, begins at `left`, and ends at `max(right, end)`. If `start > right`, points between `right` and `start` are uncovered. Preserve the current stretch and start a new one.

The right endpoint must mean the furthest reach of the entire current component. It cannot mean merely the previous input interval's end. For `[[1,5],[2,3]]`, replacing `right` with `3` loses coverage from `3` to `5`. This counterexample is minimal in number of intervals for that error: a single interval cannot trigger a merge update. Taking the maximum keeps a contained interval from shrinking its container.

Overlapping pairs are not themselves an equivalence relation: `[1,2]` overlaps `[2,3]`, and `[2,3]` overlaps `[3,4]`, but `[1,2]` does not overlap `[3,4]`. Connections through a chain are what justify the single merged interval `[1,4]`. Keeping the component's furthest endpoint retains the information needed for the next connection, even after the original members have been forgotten.

## Put the frontier in the last output pair

Use a list named `merged` for the components found so far. Its pairs are ordered by start and separated by strict gaps. The last pair is the frontier: it may grow when the next interval arrives. Earlier pairs are complete.

Why compare only with the last pair? Suppose an earlier component ends at `a`, and the last component begins at `b`, with `a < b`. Every new start is at least `b`. It therefore cannot reach backward across that gap into the earlier component. If it reaches any saved component, only the last one is a candidate. This removes the need to rescan the whole output after each interval.

In Python, `sorted(intervals, key=lambda pair: pair[0])` returns a new outer list. The small function `lambda pair: pair[0]` takes one pair and returns its start; starts are the values used to order the pairs. The key function runs once per input pair. For example, `[8,10]` contributes key `8` and `[1,7]` contributes key `1`, so `[1,7]` comes first. Equal starts need no secondary endpoint order for this algorithm: either order will be combined by the maximum. Python's stable sort preserves their original relative order. [Python sorting documentation](https://docs.python.org/3.14/howto/sorting.html#key-functions)

A new outer list does not mean new inner pairs. Its entries still refer to the input pair objects. If the program saved one of those pairs directly and changed its end, the caller would see the change. Instead, `merged.append([start, end])` creates a fresh two-item list for each new component. The integers can be shared safely because the program never changes an integer object; it replaces an entry in an output pair. The input pairs are only read. Python distinguishes a [shallow list copy](https://docs.python.org/3.14/tutorial/datastructures.html#more-on-lists) from independent nested objects.

Here is the complete Python 3 solution:

```python
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
```

`for start, end in ordered` reads a pair and binds its two values to the local names `start` and `end`. `merged[-1]` selects the last output pair; the following `[1]` selects that pair's end. Assigning to `merged[-1][1]` replaces that slot in the existing pair. It neither appends another component nor replaces the entire output list.

For the first interval, `not merged` is true because `merged` is empty. Python's `or` stops after a true left operand, so the expression never tries to index the nonexistent last pair. On later iterations it tests the gap. These are [documented truth-value and short-circuit rules](https://docs.python.org/3.14/library/stdtypes.html#boolean-operations-and-or-not).

`append` changes the output list and returns `None`; the code uses its effect, not its return value. Writing `merged = merged.append(...)` would replace the variable with `None` and break the next iteration. Likewise, `intervals.sort(...)` would sort the caller's list in place and return `None`; it is not interchangeable with the `sorted(...)` expression used here. [Python list methods](https://docs.python.org/3.14/tutorial/datastructures.html#more-on-lists)

## Follow one input through the whole program

This is a worked state trace, not a measurement of interpreter instructions. Start with:

```text
intervals = [[8,10],[1,7],[3,4],[7,8],[12,12],[12,14]]
```

The sorting call finishes before the loop begins. It returns:

```text
ordered = [[1,7],[3,4],[7,8],[8,10],[12,12],[12,14]]
merged = []
```

The input remains in its original order. Equal-start pairs `[12,12]` and `[12,14]` retain their relative order. During the scan, no assignment targets `ordered` or an input pair.

The first pair supplies `start = 1`, `end = 7`. Since `merged` is empty, the first branch appends a newly allocated `[1,7]`:

```text
merged: [] -> [[1,7]]
```

The next pair is `[3,4]`. The last output end is `7`. The gap test `3 > 7` is false, so the `else` branch computes `max(7,4)`, which returns `7`. Assigning that value leaves the visible result unchanged:

```text
merged: [[1,7]] -> [[1,7]]
```

This unchanged state is necessary: `[3,4]` contributes no points beyond those already covered.

For `[7,8]`, `7 > 7` is false. Sharing an endpoint takes the merge branch. `max(7,8)` returns `8`, and the existing output pair changes:

```text
merged: [[1,7]] -> [[1,8]]
```

For `[8,10]`, `8 > 8` is also false. The next maximum is `10`:

```text
merged: [[1,8]] -> [[1,10]]
```

For `[12,12]`, `12 > 10` is true. There is a real gap, so the program appends a new pair instead of extending the first one:

```text
merged: [[1,10]] -> [[1,10],[12,12]]
```

No later start can be less than `12`. The first component `[1,10]` is now beyond the reach of all remaining intervals.

Finally `[12,14]` meets the last component because `12 > 12` is false. Only that last pair changes:

```text
merged: [[1,10],[12,12]] -> [[1,10],[12,14]]
```

The loop has consumed every pair. `return merged` returns `[[1,10],[12,14]]`; no final flush is required because the frontier has already lived in the output throughout the scan. The return value shares neither its outer list nor its inner pairs with the input. Changing an output endpoint later would therefore leave the input unchanged.

A nearby boundary test distinguishes this code from a tempting mistake. On `[[1,2],[2,3]]`, treating `start >= last_end` as a gap would return two touching intervals. The required answer is `[[1,3]]`. The strict `>` in the code is the exact point where the closed-endpoint contract affects the branch.

## Why the scan cannot lose or invent coverage

A loop invariant is a statement that remains true at the same checkpoint on every iteration. Here the checkpoint is immediately before processing the next sorted pair. At that point, `merged` is an exact, fully merged description of the processed prefix: it has the same union, starts increase, and every neighboring output pair has a strict gap. All pairs except possibly the last are final even with respect to unread input.

This differs from the earlier task-equivalence property. Equal unions describe which answers are acceptable. The invariant additionally describes the intermediate state and what future work can change.

Initially the processed prefix and `merged` are both empty. They cover no points, and there are no pairs whose ordering or gaps could violate the invariant.

For maintenance, suppose a next pair `[start,end]` arrives. If the output is empty, a fresh copy represents exactly that first pair. Otherwise, sorting guarantees that `start` is no earlier than the start of the last component. If `start` is no greater than its end, the intervals intersect. Replacing that end by their maximum represents their exact union: it adds precisely the new covered points and leaves no hole. Its left endpoint stays fixed, so it cannot disturb the gap to an earlier component.

If `start` is greater than the last end, appending preserves both exact coverage and a strict gap. Every unread interval has a start at least as large as `start`; none can fill this newly established gap from the left. The old last component can now join the earlier final components. These cases preserve the invariant.

At termination the processed prefix is the entire input. The invariant supplies exact coverage and strict gaps between output components. Thus no pair of output intervals overlaps, and no covered point has been lost or invented. The loop terminates because it visits each element of a finite sorted list once.

## Account for the hidden work in sorting and appending

Let `n` be the number of input intervals and `k` the number of output components, so `k <= n`. Big O gives a growth bound while ignoring fixed multipliers and small fixed overhead. `O(n)` means work bounded by a constant times the input size; `O(n log n)` includes an additional factor that grows as a logarithm. These are operation-count statements, not elapsed seconds.

Treat endpoint comparison, indexing and replacing a list entry as constant work here. The statement bounds endpoints by `10^4`, so these integers have bounded size. The sorting key reads one endpoint per pair, contributing `O(n)` work. The scan visits `n` pairs; each visit makes a fixed number of tests, reads and maximum comparisons, plus at most one append.

An append can occasionally require a larger storage area and copying existing references. It is not correct to claim that every individual append costs constant time. In CPython v3.14.0, list storage grows with spare capacity proportional to its current size. Across repeated growth, copied capacities form a geometric progression: viewed backward, earlier capacities decrease by a fixed fraction. Their sum is bounded by a fixed multiple of the final capacity. Thus all `k` appends together cost `O(k)`, called amortized constant cost per append. This is a bound over the sequence, not an assumption that an occasional expensive append never happens. [CPython list growth implementation](https://github.com/python/cpython/blob/v3.14.0/Objects/listobject.c#L111-L121)

Sorting dominates the worst-case time. CPython v3.14.0 uses an adaptive merge sort: it finds ordered stretches, called runs, and combines them. To see where the logarithm comes from, consider the conceptual case of combining equal-sized runs. A round doubles run size: `1, 2, 4, 8, ...`. Reaching `n` needs about `log2(n)` rounds; `log2(8) = 3` because three doublings turn `1` into `8`. Combining runs examines at most a linear number of items across each round, giving `O(n log n)` work. CPython uses a more elaborate merge schedule rather than those exact rounds, while retaining the worst-case `O(n log n)` bound. Existing ordered runs can reduce its work. This is a cost explanation, not a claim that the implementation literally splits every input into single items. [CPython sorting design](https://github.com/python/cpython/blob/v3.14.0/Objects/listsort.txt)

Adding sorting and the scan gives worst-case `O(n log n)` time for growing `n` (with constant work at `n = 1`). The visible single loop does not make the entire function linear: `sorted` performs its own work before that loop.

The returned result occupies `O(k)` space: one outer list and `k` fresh pairs, each of fixed size two. Excluding the input and returned result, auxiliary space is still `O(n)`. `ordered` contains `n` references, and sorting can keep keys and temporary merge storage proportional to `n`. Those temporary structures disappear after sorting, while `ordered` survives through the scan. The scan itself needs only a constant number of local references in addition to output. Peak extra space including the returned result is `O(n + k) = O(n)`. Using in-place `list.sort` would remove the copied outer list but would not justify a general `O(1)` auxiliary-space claim for CPython's sorting. [CPython key allocation](https://github.com/python/cpython/blob/v3.14.0/Objects/listobject.c#L2770-L2793) and [merge storage](https://github.com/python/cpython/blob/v3.14.0/Objects/listsort.txt#L14-L18)

## When the input arrives already ordered

If a changed contract guarantees nondecreasing starts, remove the sorting call and scan that order directly. The same proof applies because its required ordering premise is now supplied by the caller. Time becomes `O(n)` under the same primitive-cost assumptions.

This also permits streaming: keep just one pending `[left,right]` pair, extend it when intervals meet, and emit it when a strict gap appears. Emit the last pending pair when input ends. Emission means passing a completed pair to a consumer instead of keeping all completed pairs in a list. That version needs `O(1)` working state beyond its input stream and whatever the consumer stores. If the API still demands a returned list, storing the `k` results still needs `O(k)` space.

The guarantee is essential. An unsorted stream might deliver a bridging interval after a component has been emitted; `[[5,6],[1,2],[2,5]]` already demonstrates the failure. For arbitrary input under the original contract, sorting is the chosen alternative to repeatedly revisiting previously saved components. The cost of arranging intervals buys the ability to finish each component once.

## English interview rehearsal

**Why sort by start?** Sorting makes future starts nondecreasing. Once a new start exceeds the current end, no later interval can bridge the gap.

**Why keep the maximum end?** The last output pair represents a whole connected component. A contained interval must not shorten its furthest reach.

**Why does equality merge?** The intervals are closed. Two intervals with a shared endpoint intersect at that point.

**What is your invariant?** Before each iteration, the output is the fully merged union of the processed prefix, ordered with strict gaps. Earlier components are final; only the last may grow.

**What are the costs and mutation effects?** Worst-case time is `O(n log n)`, auxiliary space is `O(n)`, and returned output uses `O(k)` space. The implementation preserves the input and creates new output pairs.

## Master Map

Closed endpoints make equality an overlap. Arbitrary input order makes an observed gap provisional. Sorting by start makes future starts move only right, which makes a strict gap permanent. The last output pair then holds the only component that can still grow; taking the maximum end preserves its full coverage. Fresh output pairs keep those updates away from the caller's input. The prefix invariant connects each local update to the required final union. Sorting pays for this one-pass decision rule; an already ordered input supplies that rule without the sorting cost.
