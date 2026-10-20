# LeetCode 78: keeping a subset while undoing a choice

For `nums = [2, 5]`, the required result contains `[]`, `[2]`, `[5]` and `[2, 5]`. The empty list records the choice to take nothing. `[5, 2]` would describe the same subset as `[2, 5]`; choosing elements in input order gives each subset one list representation.

[LeetCode 78](https://leetcode.com/problems/subsets/) asks for every subset of an array of distinct integers, without duplicate subsets. Result order is unrestricted. The input has between 1 and 10 elements, each between -10 and 10. A negative number is an ordinary candidate; neither its sign nor its magnitude changes whether it can be selected.

The statement does not require changing `nums`. The implementations below leave it unchanged and return a new outer list containing new subset lists. They also return `[[]]` for an empty input, although that input is outside the stated constraints. Repeated input values are outside the contract: `[2, 2]` would need a different uniqueness argument.

## A choice for each position

Looking only for contiguous pieces misses `[2, 7]` from `[2, 5, 7]`. Subsets may skip elements. Choosing arbitrary orders creates the opposite problem: selecting 2 then 5 and selecting 5 then 2 would repeat the same membership choice.

Process positions from left to right. At each position there are exactly two choices: exclude its value, or include it once. Advancing to the next position after either choice prevents reusing that position. Since values are distinct, two different sequences of these yes/no decisions must disagree on membership of some value. They therefore produce different subsets. Conversely, any required subset tells us exactly which positions to include, so this procedure can reach it.

This is a correspondence between decision sequences and subsets. It explains why duplicate removal is unnecessary. It is separate from the checkpoint rule that will keep the running program correct.

We need to remember the next undecided position, `i`, and the values already selected, `path`. At entry to a call `visit(i)`, `path` contains exactly the included values among `nums[0:i]`, in input order. No position from `i` onward has been decided in that call. The outer list `result` retains completed answers.

To explore both choices, a function can call itself with `i + 1`. This is recursion: the caller pauses until that call finishes, then resumes at its next statement. Each active call retains its own `i` and where to resume. All calls use the same `path` and `result` lists from their enclosing function. They do not each receive a private copy. Python's [function tutorial](https://docs.python.org/3.14/tutorial/controlflow.html#defining-functions) describes local function state and recursive calls.

The exclude branch needs no list change. For the include branch, append `nums[i]`, explore the remaining positions, and remove that appended value. This restoration is called backtracking. It lets a later branch start from the same choices the current call received. The checkpoint has a return condition too: when `visit(i)` finishes, it must leave `path` as it found it, while retaining the new completed subsets in `result`.

## Why an answer needs its own list

Python's `append` changes an existing list; it returns `None`. `pop()` removes and returns the last item. `copy()` returns a shallow copy: a new list containing references to the same elements. These are documented in [Python's list methods](https://docs.python.org/3.14/tutorial/datastructures.html#more-on-lists).

Here the elements are integers. Copying their references is sufficient because the algorithm changes list membership, not the integers themselves. A new subset list can keep its entries even when `path` later loses an entry. This independence is the reason to copy at a completed answer.

Consider a tempting replacement: `result.append(path)` instead of `result.append(path.copy())`. `append` would store a reference to the working list itself. It would not freeze its contents. [Python assignment semantics](https://docs.python.org/3.14/reference/simple_stmts.html#assignment-statements) distinguish binding a name to an object from copying that object.

The smallest legal input already breaks this replacement. For `[2]`, the exclude leaf appends the empty `path`. The include branch changes that same list to `[2]` and appends it again. Both result entries then refer to `[2]`. The final `pop()` empties the one shared list, so the returned result becomes `[[], []]`, with both entries referring to the same object. The required `[2]` has disappeared. No smaller legal input exists because the minimum input length is 1.

Copying only when saving an answer preserves cheap updates to the working path while giving every answer stable membership. The return value of `path.copy()` goes into `result.append(...)`; the return value of `append` is ignored.

## The complete search

```python
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
```

At `i == n`, no positions remain. Even an empty `path` is now a completed answer, so the code saves it before returning. At a nonterminal call, the first child handles exclusion. The second child handles inclusion while the appended value is present. The final `pop()` undoes this call's inclusion after the second child has restored any choices of its own.

`visit` communicates answers through `result`; its own return value is `None`. `subsets` waits for `visit(0)` to finish and returns the accumulated outer list. Neither `append` nor `pop` touches `nums`.

## Follow `[2, 5]` through every branch

Start with `result = []`, `path = []` and `visit(0)`. Position 0 contains 2. Its exclude call enters `visit(1)` with `path = []`; position 1 contains 5.

That call first excludes 5, entering `visit(2)` with `path = []`. Since `2 == n`, it allocates an empty snapshot and appends it: `result = [[]]`. It returns to `visit(1)` without changing `path`.

Back in that `visit(1)`, `path.append(5)` changes `path` from `[]` to `[5]`. Its include call enters `visit(2)`, copies `[5]`, and appends the copy: `result = [[], [5]]`. After this child returns, `path.pop()` returns 5 and restores `path = []`. The entire exclude-2 subtree is finished. Execution resumes in the original `visit(0)`.

The original call now appends 2: `path = [2]`. Its second child enters `visit(1)`. Excluding 5 reaches a leaf with `[2]`, giving `result = [[], [5], [2]]`. That child leaves `[2]` intact.

The active `visit(1)` next appends 5, so `path = [2, 5]`. The leaf copies this list and adds it: `result = [[], [5], [2], [2, 5]]`. Returning to `visit(1)`, a `pop()` removes 5 and restores `[2]`. Returning to `visit(0)`, another `pop()` removes 2 and restores `[]`.

`visit(0)` finishes and `subsets` returns `[[], [5], [2], [2, 5]]`. Emptying `path` has not emptied any saved snapshot. The output order follows exclude before include; it is allowed by the problem. This is a hand-worked execution trace, not a measurement of an interpreter's execution time.

## Why the search finishes with exactly the right answers

Initially, `visit(0)` has an empty `path`: there are no earlier positions to include. Its entry checkpoint holds.

Suppose it holds at a nonterminal `visit(i)`. The exclude call leaves the earlier selections unchanged and advances past position `i`, so its own entry checkpoint holds. When it returns, the return condition gives back the original `path`. Appending `nums[i]` then establishes the include child's checkpoint. That child restores this longer path when it returns; the parent's `pop()` removes exactly its own appended entry. The parent's return condition follows.

At a leaf, the checkpoint means that `path` is one complete membership choice. Copying saves that choice and leaves the working list unchanged. Induction from leaves back toward the first call proves the restoration condition for every call, so the reasoning about siblings does not assume an unproved cleanup step.

Each recursive call increases `i` by 1. It stops at `n`, so there are at most `n + 1` active calls and no branch can continue forever. Every position receives both decisions. The earlier correspondence proves that all subsets appear once and only once. Restoring `path` preserves the checkpoint; making a snapshot preserves the answer. Both obligations are needed.

## Count the work, including the copies

Let `n` be the input length. For a growth comparison, treat the number of positions as variable while keeping the same algorithm and distinct-value assumption. The official maximum is still 10. We count list-reference operations and active function calls, assume sufficient memory and recursion capacity, and ignore platform byte sizes. For much larger inputs, Python's recursion limit and the exponentially large output become practical constraints.

After one decision there are 2 branches. After two there are 4. Each extra position doubles the number, so there are `2**n` leaves. Across all levels there are `1 + 2 + 4 + ... + 2**n = 2**(n + 1) - 1` calls: doubling this sum and subtracting the original cancels all middle terms. Thus visiting calls alone grows in proportion to `2**n`.

A copy of a path of length `r` writes `r` element references into a new list, plus fixed list-creation work. For `n >= 1`, each particular input value appears in half the subsets: pair each subset without it with the corresponding subset containing it. Across `n` values, the output therefore contains exactly `n * 2**(n - 1)` element entries. These are precisely the entries copied at leaves. The empty subset still needs its own list.

The total time is consequently `Theta(n * 2**n)` for `n >= 1`. `Theta` means the growth has both an upper and a lower bound of that form, up to fixed multipliers. `O` alone gives an upper bound. A lower bound follows here from having to write that many output entries; enumerating all explicit lists cannot take linear time in `n`.

The main live working state is one path of length at most `n` and at most `n + 1` active calls. Its auxiliary space, meaning storage beyond the input and retained output, is `O(n)`. A snapshot being built before its append has length at most `n` too, so counting that transient list separately leaves this bound unchanged. The returned output uses `Theta(n * 2**n)` space, counting its outer references, inner list objects and element-reference slots. Integer objects need not be duplicated. At `n = 10`, there are 1,024 subset lists containing 5,120 element entries altogether.

These costs use the usual aggregate cost for end appends rather than assuming every append has identical duration. CPython 3.14 grows list capacity with spare room; occasional resizes are spread across many appends. Here `m` is the number of appends in a growing sequence; spreading resize work across that sequence is called amortized analysis. A run of `m` appends costs `O(m)` in aggregate. Copying and concatenation explicitly visit their input references. The relevant implementation is [CPython v3.14.0 `listobject.c`](https://raw.githubusercontent.com/python/cpython/v3.14.0/Objects/listobject.c), particularly `list_resize`, `list_slice_lock_held` and `list_concat_lock_held`. This is an implementation cost model, not a promise about exact allocation times on every Python implementation.

## An iterative alternative: keep the old half

If recursion is undesirable, build complete subsets for a growing prefix instead. Start with `[[]]`. When the next value is `x`, keep every old row to represent excluding `x`, and add a fresh `old_row + [x]` to represent including it.

```python
def subsets_iterative(nums: list[int]) -> list[list[int]]:
    result = [[]]
    for x in nums:
        old_count = len(result)
        for j in range(old_count):
            result.append(result[j] + [x])
    return result
```

For `[2, 5]`, processing 2 changes `[[]]` to `[[], [2]]`. Processing 5 fixes `old_count = 2`. At `j = 0`, `[] + [5]` creates `[5]`; at `j = 1`, `[2] + [5]` creates `[2, 5]`. The final result is `[[], [2], [5], [2, 5]]`.

Python list concatenation produces a new list; it does not append into the old row. `range(old_count)` supplies indices from 0 through `old_count - 1`, so rows appended during this iteration are not revisited. The stored count remains 2 even after the outer list grows. Python documents [sequence concatenation and mutable-sequence iteration](https://docs.python.org/3.14/library/stdtypes.html#common-sequence-operations) and [range endpoints](https://docs.python.org/3.14/tutorial/controlflow.html#the-range-function).

The loop checkpoint is that before processing `x`, `result` contains every subset of the already processed prefix exactly once. The old half lacks `x`; the added half contains it, and removing `x` recovers a unique old row. Distinct input values make the halves disjoint. Initially the empty prefix has just the empty subset. Each completed outer iteration extends the checkpoint, and after all positions it is the required result.

There are `1 + 2 + ... + 2**(n - 1) = 2**n - 1` new rows. Each nonempty final subset is created once by copying its earlier entries and adding its last value. Thus concatenations write exactly the same `n * 2**(n - 1)` output entries counted above. Time and returned output space are again `Theta(n * 2**n)`. The loop retains only a few control values beyond the output. It never copies the outer list: the old rows remain part of the final output. A temporary `[x]` has one entry, and the new concatenated row has at most `n` entries before its append. Under the convention that a newly constructed row counts as transient until appended, peak auxiliary space is `O(n)`; if it is counted as output immediately, control and singleton-list scratch space are `O(1)`.

This alternative avoids recursive calls and a mutable shared path, so it is preferable when recursion depth or a no-recursion requirement controls the choice. Backtracking is useful when future restrictions can reject a partial choice before constructing every completion.

## Change the request: only subsets of size `k`

Suppose values remain distinct but the caller now asks for subsets containing exactly `k` values, where `0 <= k <= n`. Generating the full power set and filtering would still build all `2**n` rows. The search can instead stop once it has enough values, or reject a path that can no longer reach the target.

```python
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
```

The path and position retain their original meanings. Now `n - i` is the number of undecided positions. Even including all of them cannot succeed when `len(path) + (n - i) < k`; rejecting that call loses no valid answer. When `len(path) == k`, every remaining position must be excluded. Saving once and stopping represents that one completion, rather than exploring additional inclusions. Neither early return changes `path`, so the restoration proof still applies. The code assumes the stated bounds on `k`.

For `[2, 5, 7]` and `k = 2`, excluding 2 then excluding 5 reaches `i = 2`, `path = []`. Only one undecided value remains, so `0 + 1 < 2` rejects the call. Excluding 2 and including 5 instead leaves `[5]`; including 7 completes `[5, 7]`. Including 2 eventually yields `[2, 7]` and `[2, 5]`. The early success condition prevents a three-element result. Every size-`k` subset still has its unique decision route: no prefix of that route is impossible, and once it reaches `k` selected values its remaining exclusions are forced. Thus both early returns preserve completeness and uniqueness. At `i == n`, either success or impossibility must hold, so no code reads `nums[n]`.

Let `C(n, k)` mean the number of ways to choose `k` distinct positions from `n`; each unordered choice is counted once. Those are the leaves saved here. Calls are a subset of the original binary search tree, hence at most `2**(n + 1) - 1`. Copies write `k * C(n, k)` entries, and creating the lists costs another `C(n, k)` units. A valid upper bound is `O(2**n + (k + 1) * C(n, k))`; it is deliberately not a tight bound for every `k`. Auxiliary space stays `O(n)` for the active calls, path and temporary snapshot. Output space is `Theta((k + 1) * C(n, k))`, including an object and outer reference even for an empty row. For `k = 0`, the first call saves `[]` and stops in constant work. For `k = n`, the only surviving route includes every value; excluded siblings fail immediately, giving `O(n)` calls and one length-`n` copy. These boundaries show why rejecting partial paths can matter.

## Interview English and the master map

Why are there no duplicate subsets? Each distinct input value receives one include/exclude decision, and positions are processed in one fixed order. Different decisions change membership of some value.

Why copy the path? The working list is mutated after a leaf returns. A shallow copy gives the saved answer an independent list while safely sharing integer elements.

What does backtracking restore? Every `visit(i)` leaves `path` with exactly its entry contents. Its final `pop()` reverses its own inclusion after its children finish.

Why is time `Theta(n * 2**n)`? There are `2**n` subsets and exactly `n * 2**(n - 1)` element entries in their explicit lists. Saving those entries dominates the call overhead.

When would you choose the iterative version? When recursive calls are unsuitable and all subsets are still required. Its old-prefix checkpoint replaces the recursive path-restoration checkpoint.

The task requires every membership choice. Distinct values and fixed position order give each choice one representation. The recursive position marks unfinished decisions; the path holds selected values; two branches cover the next decision. Restoring the path protects sibling searches, and copying at completion protects saved answers. The output count explains the exponential cost. A size restriction changes which partial choices can still succeed and permits safe early returns.
