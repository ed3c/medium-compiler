# Daily Temperatures: let each new day answer the days still waiting

For a day at 70 degrees, a later day at 70 does not end the wait. A day at 72 does, even if several colder days come between them. The answer is the distance to the first qualifying day, measured in days rather than degrees.

In [LeetCode 739, Daily Temperatures](https://leetcode.com/problems/daily-temperatures/), `temperatures` is a list of integers. It contains between 1 and 100,000 entries, each between 30 and 100. Return a list of the same length: position `i` holds the smallest positive distance `j - i` for which `temperatures[j] > temperatures[i]`, or `0` if no such future position exists. Positions start at zero. The statement asks for a returned answer; the solutions below leave the supplied list unchanged and allocate a separate result.

Suppose the input is `[70, 70, 69, 72, 71]`. Day 0 must wait until day 3, so its answer is `3`. Day 1 reaches that same warm day in `2` days. Day 2 waits `1` day. Neither day 3 nor day 4 has a warmer future day. The full answer is `[3, 2, 1, 0, 0]`.

## A direct search establishes what must be preserved

One correct method handles each day separately. Start at the following day, move right, and stop at the first strictly greater temperature. Stopping there matters: a still hotter day farther away cannot improve the required waiting time.

```python
def daily_temperatures_scan(temperatures: list[int]) -> list[int]:
    n = len(temperatures)
    answer = [0] * n
    for i in range(n):
        for j in range(i + 1, n):
            if temperatures[j] > temperatures[i]:
                answer[i] = j - i
                break
    return answer
```

Here `i` is the day receiving an answer and `j` is the candidate future day. The initialized zero survives if the inner search finds nothing. `break` ends that inner search, so the next outer iteration handles the next `i`. Each candidate before the chosen `j` has failed the comparison; that is why the first success gives the correct answer. Every inner search advances `j` toward `n`, and there are finitely many `i`, so the method ends.

The cost becomes troublesome when nothing ever gets warmer. On an all-equal list of length `n`, the searches inspect `n - 1`, then `n - 2`, down to `0` candidates. Pairing the ends of that sum gives `n(n - 1)/2` comparisons. At 100,000 days, that is 4,999,950,000 comparisons. The temperature range does not prevent this input: repeated 70s are legal.

Big O describes how an upper bound grows with input size, suppressing fixed factors and lower-order terms. The sum above has a quadratic leading term, so the worst-case time is `O(n²)`. This assumes reading a list entry, comparing these bounded integers, and updating an index cost constant time. The method retains only `n`, `i`, and `j` beyond its answer, so it uses `O(1)` auxiliary space and `O(n)` output space. A `range` describes the progression of indices without building a list of them. For a tiny input, this direct search can be preferable because it needs no growing collection of pending days. Its memory advantage remains meaningful even though its repeated scans become expensive on long inputs.

The repeated work suggests turning the question around. When day 3 brings 72, it can answer several older days at once. We need to retain the days that have not yet found a warmer successor.

## Derive the pending state before naming the stack

A pending entry must identify a day, not merely its temperature. The two 70s in the example have the same threshold but different distances to day 3. Storing their indices preserves both the output positions and the subtraction needed for each answer. The original list remains available to recover a stored day's temperature.

Process days from left to right and keep pending indices in that same order. The latest pending day goes at the right end of a Python list. If today's temperature exceeds that day's temperature, remove the pending index, fill its answer, and test the new rightmost entry. Once a day has its first warmer successor, it never needs another answer and can be removed permanently.

Why is the right end enough? The temperatures of pending days will be non-increasing from left to right: each entry is at least as warm as the next. If today cannot answer the rightmost, coldest pending day, it cannot answer any warmer or equally warm entry to its left. If today can answer the rightmost day, removing it exposes the next threshold to test. This lets the algorithm avoid scanning the rest of the pending list after a failed comparison.

To keep that order, remove every rightmost entry colder than today, then append today. After the removals, the list is empty or its last temperature is at least today's temperature. Appending today therefore preserves the non-increasing order. Equal temperatures stay pending together because equality does not answer either day's strict-warmer question. This ordered use of a last-in, first-out collection is called a monotonic stack; here its temperatures are non-increasing, allowing ties.

The word stack describes the access rule. Its top is the rightmost entry, and removing that entry exposes the one below it. Python's [list-as-stack documentation](https://docs.python.org/3.14/tutorial/datastructures.html#using-lists-as-stacks) supports `append` at the right end and `pop()` from that same end. No sorting happens: the indices stay in time order, and valid answers determine which indices leave.

## Follow the program through a complete input

Start the input `[70, 70, 69, 72, 71]` with `answer = [0, 0, 0, 0, 0]` and `pending = []`. In the states below, `pending` contains indices, not temperatures.

At day 0, the pending list is empty, so there is no older day to answer. Appending `0` changes it to `[0]`. The answer stays all zeros; day 0 is now waiting.

At day 1, the top index is `0`, whose temperature is 70. The comparison `70 > 70` is false. No index leaves and no answer changes. Appending `1` gives `[0, 1]`. These equal temperatures represent two separate unanswered days.

At day 2, `69 > temperatures[1]`, or `69 > 70`, is false. Appending `2` gives `[0, 1, 2]`, whose associated temperatures are `[70, 70, 69]`. The answer is still `[0, 0, 0, 0, 0]`.

At day 3, today's 72 exceeds `temperatures[2]`, which is 69. `pending.pop()` returns `2` and mutates `[0, 1, 2]` into `[0, 1]`. Store that returned index as `previous`; then `answer[previous] = 3 - 2` makes the answer `[0, 0, 1, 0, 0]`. The subtraction measures elapsed days. The difference in temperature, `72 - 69`, would answer a different question.

The loop tests again. Its new top is `1`, with temperature 70. Pop returns `1`, leaves `[0]`, and the write `answer[1] = 3 - 1` produces `[0, 2, 1, 0, 0]`. Another comparison finds `72 > temperatures[0]`. Pop returns `0`, empties the pending list, and `answer[0] = 3 - 0` gives `[3, 2, 1, 0, 0]`. There is now no top to inspect. Append `3`, leaving `[3]`.

At day 4, `71 > temperatures[3]`, or `71 > 72`, is false. Append `4` to get `[3, 4]`. The input ends, so those two days never receive a successful comparison. Return the existing `[3, 2, 1, 0, 0]`; the last two zeros already express their lack of a warmer future day.

A single `if` would be insufficient on day 3: after the first pop, two more days still need this same day's answer. The `while` repeats until today has answered every pending day it can answer.

## Connect the state changes to Python

The complete solution uses `enumerate` to obtain each index and temperature together. Its default count begins at zero, so the first pair is `(0, 70)` for our example. It yields pairs as the loop advances rather than creating a separate list of all pairs. See the official [`enumerate` definition](https://docs.python.org/3.14/library/functions.html#enumerate).

```python
class Solution:
    def dailyTemperatures(self, temperatures: list[int]) -> list[int]:
        answer = [0] * len(temperatures)
        pending = []

        for day, temperature in enumerate(temperatures):
            while pending and temperature > temperatures[pending[-1]]:
                previous = pending.pop()
                answer[previous] = day - previous
            pending.append(day)

        return answer
```

`pending[-1]` reads the last pending index. The outer indexing in `temperatures[pending[-1]]` then reads that day's temperature. For example, when `pending` is `[0, 1, 2]`, these reads produce `2` and then `69`. Reading the top leaves the pending list unchanged; popping it removes and returns the index.

The guard has two parts because an empty list has no last element. Python considers an empty list false, and `and` evaluates its right operand only when the left one is true. Thus `pending and ...` skips the indexing when `pending` is empty, including when a pop has just emptied it. That order prevents `IndexError`. These are [Python truth-value and Boolean-operation rules](https://docs.python.org/3.14/library/stdtypes.html#truth-value-testing).

`answer = [0] * len(temperatures)` creates the output positions in advance. The entries initially refer to the immutable integer zero. Assigning `answer[previous]` replaces one position; it does not change all zero entries. `pending.append(day)` mutates the existing list and returns `None`, so the code does not assign its return value to `pending`. The two mutable lists have separate purposes: `pending` tracks unfinished work, while `answer` receives completed distances. Neither operation modifies `temperatures`.

With one input day, the loop only appends index 0, and the return is `[0]`. With all equal temperatures, every index stays pending and every answer stays zero. With increasing temperatures, each new day answers the preceding day. These cases exercise an empty top, equality, and repeated successful answers without requiring separate branches.

## Why every answer is the first warmer day

Use a checkpoint immediately before processing a new day `d`. The loop invariant is the following claim about the entire state at that checkpoint: `pending` contains exactly the processed days still lacking a warmer day among the days already seen; their indices increase and their temperatures are non-increasing. Every processed index outside `pending` already has its correct first-warmer distance in `answer`. Pending and unprocessed positions still hold zero.

Initially no day has been processed, so the empty pending list and zero-filled answer satisfy the claim.

Now suppose the claim holds before day `d`. If today is warmer than the top pending day `p`, no day between `p` and `d` was warmer than `p`; otherwise the checkpoint claim would not allow `p` to remain pending. Today qualifies, and all earlier future candidates failed, so `d` is the first warmer day for `p`. Writing `d - p` is correct, and removing `p` discards only a completed obligation. Repeat this argument for every pop.

If the top is not colder than today, every earlier pending entry is at least as warm as that top. Today cannot answer any of them. The remaining entries therefore stay unresolved. Append `d`: it cannot already have a future day among the processed days, and the temperature order is preserved by the stopping comparison. This establishes the invariant before the next day.

The outer loop processes exactly `n` days. Each inner iteration removes one pending index, so it also ends. At the final checkpoint all days have been seen. Every remaining pending day has no warmer future day anywhere in the input and correctly retains zero. All removed days already have their first-warmer distance. The returned list is therefore correct.

This proof concerns unfinished days at a checkpoint. The task's separate result condition is about the earliest qualifying future index for each individual day. The invariant connects partial progress to that final condition; the two statements serve different purposes.

Changing `>` to `>=` breaks the original contract. On `[70, 70]` it would return `[1, 0]` instead of `[0, 0]`. This counterexample has the shortest possible length for that bug: a one-day input has no later day to compare. Another tempting change, replacing `while` by `if`, fails on `[71, 70, 72]`: it answers day 1 but leaves day 0 at zero, returning `[0, 1, 0]` instead of `[2, 1, 0]`.

## Count the work across the whole scan

Let `n` be the number of days. `O(n)` time means total work grows at most in proportion to `n`, apart from fixed overhead under the cost assumptions. A nested loop does not by itself establish quadratic work; count what its body can consume.

Each index enters `pending` exactly once. It leaves at most once because a removed index is never added again. There are therefore `n` appends and at most `n` pops over the whole run. Each successful temperature comparison causes a pop. For each outer iteration, at most one failed temperature comparison stops the inner loop; an empty pending list can also stop it without a temperature comparison. The total number of loop checks is consequently proportional to `n`, even when one day triggers many pops. Each answered position is written once, and initializing the output takes `n` positions.

This operation count assumes constant-time list indexing and bounded-integer arithmetic. List growth needs a qualification. In [CPython v3.14.0's list implementation](https://github.com/python/cpython/blob/v3.14.0/Objects/listobject.c), a list stores references in an indexed array and reserves spare capacity when growing. An append can occasionally copy many references, but a long run of appends has linear total resizing work. End pops avoid shifting the remaining entries; occasional shrinking also costs work. Shrinking waits until length falls below half the allocated capacity, leaving a gap before another comparable resize. These implementation facts support amortized constant time per end operation, meaning constant cost averaged across a sequence of operations, rather than a promise that each individual call takes equal time. Geometric growth or shrink sizes make the copied capacities sum to a constant multiple of the largest reached size; interleaved growth and shrink must cross those capacity gaps again, so their work can be charged to the intervening updates.

Combining the counts with those costs gives `O(n)` total time under this CPython-style model. The algorithm does not depend on temperatures staying within 30–100 for correctness; that bound makes the arithmetic cost assumption immediate. Python's language documentation specifies behavior, while the cited CPython source supplies these implementation details.

At most `n` pending indices remain live. An all-equal input reaches that maximum even with only one distinct temperature. Spare list capacity and temporary old/new arrays during a resize add only a constant multiple of that storage. The loop's current pair and index variables retain only a fixed number of values. Auxiliary space is thus `O(n)` in the worst case. The separately returned answer has `n` entries, so output space is also `O(n)`, and combined additional space is `O(n)`. The supplied input is excluded from additional space; exact byte counts depend on the Python build and are not claimed here.

## If equal temperatures should also end the wait

Suppose a different contract asks for the first future day at least as warm as today. Then `>=` becomes the correct comparison in the stack solution. Keep the same index representation, zero-filled output, processing direction, repeated pops, and distance writes. On `[70, 70, 71]`, day 1 now pops day 0 and writes `1`; day 2 pops day 1 and writes `1`, giving `[1, 1, 0]`. Under the original strict-warmer contract the answer is `[2, 1, 0]`.

The changed invariant says pending days lack a future temperature greater than or equal to their own among the days seen. Their temperatures are now strictly decreasing: equal entries get removed before the new one enters. If today's temperature is less than the top's, it is less than every earlier pending temperature, so the stopping rule remains valid. A popped day had no earlier qualifying successor under the changed condition, making today's distance its first qualifying answer. The original termination argument still applies.

This adaptation adds no collection, pass, or output entry. It still appends each index once, pops it at most once, and performs only a constant number of failed checks per day. The same arithmetic and list-cost assumptions therefore give `O(n)` time. Pending storage remains bounded by `n`, with fixed temporary state and `n` output entries. In fact, with the original 30–100 temperature bound, the strictly decreasing pending temperatures allow at most 71 entries. Thus auxiliary space for this changed contract is `O(1)` when that range is fixed, while output and total additional space remain `O(n)`. If the temperature range is allowed to grow, a decreasing input can retain all `n` indices, restoring `O(n)` worst-case auxiliary space. None of that smaller bound applies to the original solution, where equal temperatures accumulate.

## Interview English and a final Master Map

Why store indices? "Equal temperatures can belong to different days. An index identifies the output position and lets me compute the wait as the current index minus the previous index."

Why can the algorithm stop at the top? "Pending temperatures are non-increasing. If today cannot resolve the coldest pending day at the top, it cannot resolve any earlier pending day."

Why is a pop safe? "That day has remained unresolved through every earlier day we processed. Today is warmer, so today is its first warmer successor."

Why is the nested loop linear? "Every index is pushed once and popped at most once. The total stack work is linear, assuming amortized constant-time end operations."

What changes for warmer-or-equal? "I use `>=`, remove equal pending temperatures, and restate the invariant for the new qualifying condition. The work count stays linear; with a fixed 71-value range, the strictly decreasing stack has at most 71 entries."

The Master Map starts with the requested first future warmer day. Left-to-right processing makes a new qualifying day the earliest one for every still-pending index it resolves. Indices preserve both the destination in the answer and the elapsed-day calculation. Non-increasing pending temperatures make the top a valid stopping boundary. Repeated pops complete obligations; append creates today's obligation. Each obligation enters once and leaves at most once, giving the linear work count. At the end, the obligations that never left retain zero because the entire future has been exhausted.
