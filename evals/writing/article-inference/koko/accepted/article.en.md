# Koko Eating Bananas: find the first speed that works

For Koko, finding the slowest acceptable eating speed starts with an easier question: how many hours would a particular speed require? Once that calculation is exact, a failed speed rules out every slower speed. A successful speed lets us keep searching below it. This is binary search over possible answers, and it does not require sorting the banana piles.

## One hour belongs to one pile

In [LeetCode 875](https://leetcode.com/problems/koko-eating-bananas/description/), `piles` is a nonempty list of positive pile sizes. Koko chooses one positive integer speed `k`, measured in bananas per hour. During each hour she eats from one pile. Finishing that pile early does not let her start another pile during the same hour. Return the smallest speed that finishes all piles in at most `h` hours.

The constraints are `1 <= n <= 10^4`, `n <= h <= 10^9`, and `1 <= piles[i] <= 10^9`, where `n` is the number of piles. Every pile needs at least one hour, so `h >= n` matters: the problem guarantees that a sufficiently large speed can work. The solution below only reads the input list; it neither sorts nor changes its elements. Empty lists and `h < n` are outside this contract. [Problem statement and constraints](https://leetcode.com/problems/koko-eating-bananas/description/).

For a small example, take `piles = [4, 4]` and `h = 3`. Speed `3` takes two hours per pile, four hours total. Speed `4` takes one hour per pile, two hours total. The answer is `4`, even though dividing eight bananas by three hours and rounding up suggests `3`. That shortcut spends spare capacity from one pile on another, which the hourly rule forbids.

## Count a proposed speed without simulating every hour

For a pile of size `p` at speed `k`, count complete groups of `k` bananas. If some bananas remain, they need another whole hour. This count is the ceiling of `p / k`: the smallest integer at least as large as that quotient. For `p = 11` and `k = 4`, the groups are `4, 4, 3`, so the pile takes three hours.

Python's integer `//` operator rounds a quotient downward. For positive integers, `(p + k - 1) // k` instead gives the required upward rounding. To see why, write `p = q * k + r`, where `q` is the number of full groups and the remainder `r` satisfies `0 <= r < k`. When `r = 0`, adding `k - 1` still leaves the quotient at `q`. When `r > 0`, `r + k - 1` lies between `k` and `2 * k - 2`, so the quotient becomes `q + 1`. Both cases count exactly the hours needed. [Python arithmetic semantics](https://docs.python.org/3/reference/expressions.html#binary-arithmetic-operations).

Add that count separately for every pile. Call the total `T(k)`. Each pile requires its own hours, so any valid schedule needs at least `T(k)` hours. Eating one pile to completion and then the next achieves exactly that total. Thus `T(k) <= h` is both necessary and sufficient for speed `k` to work. Pile order cannot change this sum.

At `k = 4` on `[3, 6, 7, 11]`, an accumulator named `hours` starts at zero. The first pile contributes `(3 + 3) // 4 = 1`, changing `hours` to `1`. The next contributes `2`, changing it to `3`; the next contributes `2`, changing it to `5`; the last contributes `3`, changing it to `8`. The calculation stores a running total, without allocating a list of all four contributions or changing the piles.

## A faster speed cannot need more hours

Increasing `k` cannot increase the hours for any individual pile: a speed that clears it in a given number of hours can still clear it within those hours when increased. Adding the pile counts preserves that direction. Therefore `T(k)` never increases as `k` increases. The test `T(k) <= h` has a monotone shape: an initial run of failing speeds, possibly empty, followed by successful speeds.

This property permits discarding whole ranges. If speed `6` fails, every speed from `1` through `6` fails. If speed `6` works, the minimum successful speed is at most `6`, but might be smaller. Returning the first successful probe would ignore that distinction.

Let `M` be the largest pile. Speed `M` clears every pile in one hour, using exactly `n` hours, which fits the guaranteed `h >= n`. No positive answer lies below `1`, and an answer exists by `M`, so start with the inclusive interval `[low, high] = [1, M]`. These numbers are speeds, not indices into `piles`; no sorted pile list or stored list of candidates is needed.

At the start of every search iteration, maintain this invariant: **The minimum feasible speed lies in the inclusive interval [low, high], and high is feasible.** Here feasible means that the speed passes the hours test. The monotone property describes the problem's answers across all speeds; the invariant describes what the current search state still guarantees.

Choose `mid = (low + high) // 2`, the lower middle integer. When `T(mid) > h`, set `low = mid + 1`: `mid` and every smaller speed have failed. Otherwise set `high = mid`: larger speeds are unnecessary, but the successful `mid` must remain a candidate. Stop when `low == high` and return that value. This repeated halving of an ordered candidate range is binary search.

## Follow the interval from input to answer

Use `piles = [3, 6, 7, 11]` and `h = 8`. Initialize `low = 1` and `high = 1`. The largest-pile scan reads `3, 6, 7, 11`; each exceeds the stored upper bound, so `high` becomes `3`, then `6`, then `7`, then `11`. Each `hours` calculation starts again at zero.

```text
[low, high] = [1, 11]
mid = 6
pile hours: 1 + 1 + 2 + 2 = 6
6 <= 8 -> high = 6 -> [1, 6]

[low, high] = [1, 6]
mid = 3
pile hours: 1 + 2 + 3 + 4 = 10
10 > 8 -> low = 4 -> [4, 6]

[low, high] = [4, 6]
mid = 5
pile hours: 1 + 2 + 2 + 3 = 8
8 <= 8 -> high = 5 -> [4, 5]

[low, high] = [4, 5]
mid = 4
pile hours: 1 + 2 + 2 + 3 = 8
8 <= 8 -> high = 4 -> [4, 4]

low == high -> return 4
```

The first probe succeeds at `6`, yet the final answer is `4`. The failed probe at `3` removes speeds `1, 2, 3` together. Speeds `4` and `5` both take eight hours, so an exact match to the deadline does not justify returning immediately either. The search needs the first successful speed, including when several speeds give the same total.

At speed `4`, the pile of `11` uses hours for `4`, `4`, and `3` bananas. That last partially used hour still belongs to this pile. The scalar calculation and the physical eating rule agree at the place where pooling would give the wrong model.

## Complete Python solution

The first loop finds the largest pile explicitly: after each item, `high` holds the largest value seen so far, with initial value `1` valid because every pile is positive. Each search iteration then traverses the same list to calculate its proposed speed's total. The `Solution` class is the submission wrapper; `self` refers to its instance, and the algorithm stores no state on that instance.

```python
class Solution:
    def minEatingSpeed(self, piles, h):
        low = 1
        high = 1
        for pile in piles:
            if pile > high:
                high = pile

        while low < high:
            mid = (low + high) // 2
            hours = 0
            for pile in piles:
                hours += (pile + mid - 1) // mid

            if hours > h:
                low = mid + 1
            else:
                high = mid

        return low
```

`hours = 0` belongs inside the `while` loop because a new speed needs a new total. `hours += ...` adds to this scalar, not to the input list. The two assignments after the scan are the same two interval changes in the trace. All candidate speeds stay positive, so the division never has a zero divisor. There is no recursion, sorting, copied input, or saved history of probes.

## Why the returned speed is the minimum

Initially, the answer lies between `1` and `M`, and `M` is feasible. Suppose the invariant holds before an iteration. If `mid` fails, monotonicity excludes all speeds at most `mid`, so the answer remains in `[mid + 1, high]`; the unchanged `high` remains feasible. If `mid` succeeds, some feasible speed is now known at `mid`. The minimum therefore lies in `[low, mid]`, and assigning `high = mid` keeps the upper endpoint feasible. Each branch preserves both parts of the invariant.

When `low < high`, the lower middle satisfies `low <= mid < high`. In the failure branch the lower endpoint strictly increases; in the success branch the upper endpoint strictly decreases. The interval stays nonempty and has fewer integer candidates, so it must eventually contain one candidate. The invariant then says that this sole candidate is the minimum feasible speed. Returning `low` is justified even if that exact speed was not separately tested after the final update.

Updating `low = mid` on failure would break progress. For `piles = [2]`, `h = 1`, the interval is `[1, 2]` and `mid = 1` fails. That incorrect assignment leaves `[1, 2]` unchanged forever. The `+ 1` removes a candidate that the hours test has already disproved.

Boundary inputs also follow the same reasoning. With all piles of size `1`, `M = 1` and the search loop never runs; speed `1` is already the answer. If `h = n`, each pile must fit into its one hour, so the largest pile forces the answer to be `M`. If `h` is at least the total number of bananas, speed `1` works and the search converges to `1`. The guarantee `h >= n` is essential: outside it, even unlimited speed cannot fit all the positive piles into the deadline.

## Count the scans and the stored values

Use a bounded-integer cost model: reading a list element, comparing these integers, and doing arithmetic on values within this problem's limits each count as constant work. This compares growth in operation counts, not equal wall-clock time for every Python instruction. Pile sizes and speeds are at most `10^9`, and an hours total is at most `n * M <= 10^13`, so their required numeric range is bounded. Python integers remain exact at these values; they do not wrap at a fixed machine limit. [Python numeric types](https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex).

The largest-pile loop visits `n` elements. A proposed speed also visits all `n` piles, performing a fixed number of arithmetic and update operations for each, so one test costs proportional to `n`. The code deliberately computes the complete total even when it already exceeds `h`.

The lower middle splits an interval into a lower group including `mid` and an upper group excluding it. With an even number `L` of candidates, each group has `L / 2` members; with an odd `L`, the lower group has one more member than the upper. Success keeps the lower group and failure keeps the upper, so either update leaves at most `ceil(L / 2)` candidates. For example, an initial `M = 11` gives worst-case size bounds `11 -> 6 -> 3 -> 2 -> 1`. After `t` halvings, at most `ceil(M / 2^t)` candidates remain. It suffices for `2^t` to reach `M`; `ceil(log2 M)` is the smallest such whole number of halvings. Thus the total work is at most a constant times `n + n * ceil(log2 M)`, written `O(n * (1 + log M))`. For `M >= 2`, the common shorthand is `O(n log M)`. Keeping the initial `n` term explains the `M = 1` case too. Since `2^30 > 10^9`, the stated limits need at most thirty proposed-speed scans.

Only a fixed number of scalars and a loop's traversal state remain live. Reassigning `hours` or an endpoint replaces its previous value; it does not retain one entry per pile or per iteration. Auxiliary space is therefore `O(1)` in the same bounded-integer model, excluding the supplied input list. Temporary arithmetic results add only a fixed number of bounded values. The returned output is one integer, also `O(1)` space under this model. If arbitrary-length integer inputs replaced the stated limits, arithmetic and integer storage would need a separate bit-size analysis; the scalar model here does not claim otherwise.

## When simpler alternatives fit

An ascending search can try `k = 1, 2, 3, ...` and return the first speed whose complete pile-hours scan passes. It keeps only the current speed and running total, plus the largest-pile bound if used. All earlier speeds have been explicitly rejected, so its first success is minimal. If the answer is `a`, it performs `a` scans of `n` elements, or `n * a` pile visits; since `a <= M`, its worst-case time is `O(nM)`. A single pile of size `M` with `h = 1` forces it to test every speed through `M`. Reusing the accumulator on each scan keeps auxiliary and output space `O(1)` under the same numeric model. If a changed task guaranteed that `M` was a tiny fixed value, ascending search would be a reasonable choice for its simpler control flow; it has no speed advantage promised here. At `M` up to a billion, skipping ranges is the useful difference.

A different hourly rule changes the calculation more substantially. Suppose Koko could switch piles within an hour and use the entire capacity `k` across them. Let `S` be the total banana count. In that changed task, `h` hours can consume at most `h * k` bananas, and continuously taking bananas across pile boundaries can achieve that capacity until the supply ends. Therefore `h * k >= S` is sufficient as well as necessary, and the minimum integer speed is `(S + h - 1) // h`. A single pass adds each pile to `S`, followed by a fixed amount of arithmetic: `O(n)` time, `O(1)` auxiliary space, and one integer output under the same bounded model. No per-pile hours or candidate searches remain. This formula fails for the original `[4, 4], h = 3` precisely because that original task does not allow switching piles mid-hour.

## Reconstruct the decision and explain it aloud

For `piles = [2, 5]` and `h = 4`, start from `[1, 5]`. Before checking the result, reconstruct the proposed speeds, each hours total, and both endpoint updates. Ask what makes removing the untested smaller speeds valid, rather than only remembering an assignment pattern.

The reconstruction is `[1, 5] -> mid 3 -> 1 + 2 = 3 -> [1, 3]`; then `mid 2 -> 1 + 3 = 4 -> [1, 2]`; then `mid 1 -> 2 + 5 = 7 -> [2, 2]`, returning `2`. The last failure removes `1`, and the maintained interval leaves only `2`.

Why can we use binary search without sorting the piles? "We search integer speeds, not pile positions. Increasing the speed cannot increase the required hours, so feasibility changes only from false to true."

Why do we round each pile upward? "An unfinished remainder takes a whole hour, and unused capacity cannot move to another pile in that hour. The required time is the sum of the per-pile ceilings."

What does the search invariant guarantee? "The minimum feasible speed remains in the inclusive interval, and the upper endpoint is feasible. A failed midpoint removes itself and all smaller speeds; a feasible midpoint stays in the interval."

What is the cost? "Finding the maximum takes one scan. Each midpoint takes another scan, and halving the candidate range needs at most ceiling log base two of the largest pile. The total is O(n times (1 plus log M)), with constant auxiliary space under the bounded-integer model."

The problem rules come from the linked LeetCode statement; the rounding and integer guarantees come from the linked Python documentation. The interval reasoning, worked traces, alternatives, and proof above derive from those rules.

```text
Master Map
one pile per hour -> round each pile upward -> add hours
higher speed -> no more hours -> monotone feasibility
h >= n -> largest pile M is feasible -> start [1, M]
mid fails -> discard all speeds <= mid -> low = mid + 1
mid works -> keep mid, discard larger speeds -> high = mid
answer stays inside + interval shrinks -> one minimum speed
one scan per probe + repeated halving -> O(n * (1 + log M))
fixed scalar state -> O(1) auxiliary space
```
