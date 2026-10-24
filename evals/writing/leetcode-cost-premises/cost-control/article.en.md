# Course Schedule: count the obligations that remain

Suppose course 3 requires both course 1 and course 2. Finishing course 1 helps, but course 3 is still unavailable. A solution must remember how many requirements remain, then notice the moment that number becomes zero.

## What finishing all courses means

In [LeetCode 207](https://leetcode.com/problems/course-schedule/), course identifiers run from `0` through `numCourses - 1`. A pair `[a, b]` means that `b` must be finished before `a`. Return a Boolean indicating whether every course can be finished. A schedule itself is not required. There are 1 to 2000 courses and 0 to 5000 distinct prerequisite pairs; both identifiers belong to the course range. The statement does not exclude `[a, a]`, which makes that course impossible to start. The implementation below leaves the input unchanged.

A course with no requirements may be taken immediately. A course absent from every pair still exists and must count toward the result. Conversely, `[[1, 0], [0, 1]]` makes courses 0 and 1 wait for each other. No choice of first course can satisfy those requirements.

Draw a directed edge `b -> a` for `[a, b]`. A directed graph is simply the collection of course nodes and these one-way prerequisite edges. A directed cycle follows one or more edges back to its starting node. Each course on that cycle must wait for another course on the same cycle, so there can be no first completion there. A self-loop is a cycle containing one node.

The converse also holds for this finite graph. If every remaining course has a remaining prerequisite, start at any remaining course and repeatedly follow a prerequisite backward. There are finitely many course identifiers. Some identifier must repeat, which exposes a cycle. Thus a nonempty remainder without a cycle must contain an available course. Repeatedly taking an available course can finish everything exactly when the graph has no directed cycle. This equivalence describes the task; a changing loop invariant will describe our implementation.

## Retain a count and the courses it can release

Scanning every pair after every completion would rediscover which courses depend on the completed one. Instead, build `after[b]`, a list of courses directly waiting for `b`. Store `a` in that list for each pair `[a, b]`. This is an adjacency list: each node owns the list of destinations of its outgoing edges.

Also build `remaining[a]`, initially the number of incoming prerequisite edges for `a`. This incoming-edge count is often called indegree. After some completions, its useful meaning changes to the number of prerequisites of `a` that have not yet been completed. A count of two means that two distinct obligations remain; knowing only whether the course has any prerequisites would lose the information needed after the first completion.

Use `after = [[] for _ in range(numCourses)]`. Evaluating `[]` separately for each course makes independent inner lists. Writing `[[]] * numCourses` would repeat references to one shared list: adding a dependent for course 0 would also appear to add it for every other course. In contrast, `[0] * numCourses` is safe here. Integers are immutable, and `remaining[a] += 1` replaces the value in slot `a`; it does not mutate a shared zero. Python's [sequence operations](https://docs.python.org/3.14/library/stdtypes.html#common-sequence-operations) distinguish repetition of references from copying their objects.

Keep available courses in `ready`, a queue. The queue holds entries waiting to be processed; removing the oldest entry and adding new entries at the other end gives first-in, first-out behavior. The choice among available courses cannot invalidate a requirement: each chosen course already has no unfinished prerequisite. FIFO supplies a definite trace without searching for the smallest course number.

Use an unbounded `collections.deque`. `deque()` creates the queue, `append(x)` adds `x` on the right and returns `None`, and `popleft()` removes and returns the leftmost entry. Assigning the result of `append` back to `ready` would therefore replace the queue with `None`. A bounded deque can discard entries when full, so no `maxlen` belongs here. These behaviors are specified by the [Python 3.14 deque documentation](https://docs.python.org/3.14/library/collections.html#collections.deque).

Whenever a course is removed from `ready`, mark one more completion in `finished`. Visit only its dependents in `after[course]`. Each loses exactly one outstanding obligation, so subtract one from its count. Append a dependent precisely when its count becomes zero. Counts never increase during this phase. A positive count crosses zero only once, and initially zero courses enter during initialization, so each course enters the queue at most once. No additional visited set is needed.

## A program movie with a delayed release

Consider this constructed input:

```text
numCourses = 5
prerequisites = [[1, 0], [2, 0], [3, 1], [3, 2]]
```

Course 4 is independent. Course 0 releases 1 and 2; both must finish before 3. Reading the pairs in their listed order produces:

```text
after     = [[1, 2], [3], [3], [], []]
remaining = [0, 1, 1, 2, 0]
ready     = deque([0, 4])
finished  = 0
```

Initialization checks course identifiers in increasing order, so 0 enters before 4. Now `popleft()` returns 0 and mutates `ready` to `[4]`. Incrementing `finished` gives 1. The first dependent is 1: its count changes from 1 to 0, so `append(1)` makes the queue `[4, 1]`. The second dependent is 2: its count also changes from 1 to 0, producing `[4, 1, 2]`. Counts are now `[0, 0, 0, 2, 0]`.

The next removal returns 4, leaving `[1, 2]`; `finished` becomes 2. Its dependent list is empty, so no count changes. An isolated course contributes a completion even though it releases nothing.

Removing 1 leaves `[2]` and raises `finished` to 3. Course 3 changes from 2 to 1. The zero test fails: 3 stays out of the queue because course 2 is still unfinished. This is the branch a Boolean notion of readiness would mishandle.

Removing 2 empties the queue and raises `finished` to 4. Course 3 changes from 1 to 0. Appending 3 gives `[3]`, with counts `[0, 0, 0, 0, 0]`. Finally, removing 3 gives an empty queue and `finished = 5`; its dependent list is empty. The loop stops and `5 == numCourses` returns `True`. The conceptual completion sequence is `[0, 4, 1, 2, 3]`; the Boolean implementation does not retain it.

For a rejection, use `numCourses = 3` and `[[1, 0], [0, 1]]`. Initial counts are `[1, 1, 0]`, and only course 2 enters the queue. It finishes without releasing anything. The empty queue now accompanies `finished = 1`, so the comparison with 3 returns `False`. Having one available course was insufficient: a different component still contains a cycle.

## Complete Python solution and its checkpoint

```python
from collections import deque


class Solution:
    def canFinish(self, numCourses: int, prerequisites: list[list[int]]) -> bool:
        after = [[] for _ in range(numCourses)]
        remaining = [0] * numCourses

        for course, prerequisite in prerequisites:
            after[prerequisite].append(course)
            remaining[course] += 1

        ready = deque()
        for course in range(numCourses):
            if remaining[course] == 0:
                ready.append(course)

        finished = 0
        while ready:
            course = ready.popleft()
            finished += 1
            for dependent in after[course]:
                remaining[dependent] -= 1
                if remaining[dependent] == 0:
                    ready.append(dependent)

        return finished == numCourses
```

The checkpoint is just before each evaluation of `while ready`, after all updates for the preceding completion. At that point, `finished` counts distinct completed courses; every unfinished course's count equals its number of unfinished prerequisites; and the queue contains every available unfinished course exactly once. Completed courses are outside the queue. The queue's internal order is an implementation choice, separate from these conditions.

Initially nothing is completed, so the counts built from all pairs have the required meaning. The initialization scan includes exactly the zero-count courses. Thus the checkpoint holds before the first iteration, including when the queue is initially empty.

For maintenance, removing an available course is legal because all its prerequisites are completed. Its outgoing edges describe exactly the obligations that this completion satisfies. Decrementing those destinations updates the counts correctly, without changing any unrelated count. Each destination newly reaching zero enters once; other available courses remain queued. Increasing `finished` records this one new completion. The checkpoint holds again after the whole dependent list is processed, rather than midway through it.

For termination, at most `numCourses` distinct courses can be removed. If all were removed, those legal steps establish a schedule. Otherwise the queue is empty with some courses unfinished. The checkpoint says each such course still has an unfinished prerequisite. The finite backward-following argument above then finds a cycle, so no full schedule is possible. The final comparison therefore covers both results. This algorithm is often called Kahn's topological sort; a topological order places every prerequisite before its dependent.

A tempting wrong return is `True` whenever the initial queue is nonempty. The three-course rejection above refutes it. It is smallest by number of courses if a two-course cycle and a separate available course are required: two course identifiers form the cycle and a third supplies the misleading start. Without that requirement, the smaller `numCourses = 2, prerequisites = [[0, 0]]` already refutes the shortcut: course 1 is available while course 0 waits for itself.

## Where the running time comes from

Let `V = numCourses` and `E = len(prerequisites)`. Big O describes an upper bound on growth, ignoring fixed multipliers; `O(V + E)` means work grows no faster than a constant times the number of courses plus pairs, under the following model. Reading or writing one list slot, comparing bounded integers, incrementing a counter, and moving or retaining one object reference are elementary constant-size operations. Course identifiers fit within 0 to 1999 and counts within 0 to 5000; treating these scalars as bounded units is appropriate for this contract. This is an operation-count model, not a statement that all Python instructions take identical physical time. Allocating or copying `k` slots costs proportional to `k`.

The queue choice affects this count. A Python list stores references in consecutive indexed slots. Removing its first item must shift the later references left so indexing still starts at zero. With `V` initially available courses, draining a list through `pop(0)` moves `(V - 1) + (V - 2) + ... + 1` references. Pairing the terms gives `V(V - 1)/2`, quadratic growth even with no prerequisite edges. The [Python tutorial](https://docs.python.org/3.14/tutorial/datastructures.html#using-lists-as-queues) describes the shifting cost.

CPython v3.14.0's [deque implementation](https://github.com/python/cpython/blob/v3.14.0/Modules/_collectionsmodule.c) uses fixed-length blocks joined by links. An endpoint operation changes an endpoint position and, at a block boundary, a fixed-size block connection; it does not shift all queued references. With fixed-size block allocation treated as bounded work, each queue endpoint operation has constant cost in this model, matching the documented approximately `O(1)` behavior. Queue size can grow, but the work of a single endpoint update does not grow with it.

Adjacency lists use `list.append`, which needs a different argument. A list sometimes runs out of allocated slots. CPython v3.14.0's [list resize policy](https://github.com/python/cpython/blob/v3.14.0/Objects/listobject.c) reserves spare capacity on single-item growth, roughly one eighth of the requested size beyond the items, with small rounding and padding. A growth may copy the old references, so one append is not always constant work.

For an append-only sequence, final capacity is proportional to the final length, so d single-item appends, including their ordinary writes, take O(d) total work. This aggregate guarantee is called amortized constant time per append. It applies here because each adjacency list only grows by one appended item at a time; no alternating deletion or bulk update is being smuggled into the argument.

Building the `V` independent lists and `V` counts costs `O(V)`. Reading `E` pairs does `E` counter updates and `E` appends. If course `b` has `d_b` dependents, its append sequence costs `O(d_b)`; summing `d_b` across all courses gives exactly `E`. Small-list overhead contributes at most another `O(V)`. Building the representation therefore costs `O(V + E)`.

The readiness scan checks `V` slots and enqueues at most `V` courses. During processing, each course is enqueued and removed at most once. Each edge appears in exactly one dependent list, and that list is visited at most once. Hence all executions of the inner loop total at most `E`, even though the code nests that loop inside a `while`. Setup, queue operations and edge updates sum to worst-case `O(V + E)` time, with list construction analyzed over its append sequences. A cycle may stop processing early, but cannot avoid the initial pair-reading work.

For auxiliary space, the outer adjacency list and its inner-list headers use `O(V)` slots or fixed-size records. The inner lists retain `E` references plus spare capacity proportional to `V + E`, by the same growth policy. Counts use `V` scalar slots, and the queue holds at most `V` entries plus fixed-size block overhead proportional to that capacity. Scalar loop variables need constant space. A resize can temporarily keep old and new storage alive, but both have size proportional to the list being grown; this leaves the peak bound `O(V + E)`. The existing input is excluded from auxiliary space, and the returned Boolean is `O(1)` output space. No recursion stack is used.

## Trading stored edges for repeated scans

If storing another `E` references is unacceptable but the original pair list can be scanned repeatedly, there is a slower alternative. Keep `done[V]` Booleans. In each round, allocate a fresh `blocked[V]` array of false values. Scan every pair `[a, b]`; if both `a` and `b` are unfinished, set `blocked[a]` to true. Then identify all unfinished, unblocked courses and mark that whole group done only after the scan has finished. These are exactly the courses with no unfinished prerequisite at the start of that round. Stop successfully when all are done, or unsuccessfully when a round adds none.

The same legality and finite-cycle argument applies to these groups. Group members cannot require one another, since any such edge would have marked its destination blocked. Each successful round completes at least one new course, so there are at most `V` successful rounds and at most one final failed round. Initializing flags and inspecting courses costs `O(V)` per round; checking every pair costs `O(E)`. The resulting bound is `O(V(V + E))`. A length-`V` prerequisite chain releases only one course per round, showing why the repeated work can persist as size grows. `done`, `blocked` and an optional group buffer each hold at most `V` entries, so peak auxiliary storage is `O(V)`; old round buffers are released before the next round. The Boolean output stays `O(1)`. The input's `E` pairs remain live and are excluded under the same convention. Prefer this trade-off only when the extra adjacency storage matters more than repeated scans.

A different requirement changes what the main solution must retain: return one valid course order, or `[]` if impossible. Start an empty `order` list and append `course` immediately after each removal. Return `order` if its length equals `V`, otherwise return `[]`. Each retained entry records a legal completion, so the earlier proof establishes the returned ordering. No smallest-first guarantee follows from FIFO; for the movie, 4 appears before 1.

This adaptation adds at most `V` single-item appends to one growing list. The append-only argument still applies, so the added work is `O(V)` and the whole algorithm remains `O(V + E)`. The adjacency representation, counts and queue remain, so auxiliary storage excluding a successful returned order stays `O(V + E)`. Successful output contains exactly `V` references and takes `O(V)` output space. On failure, the partial order is temporary auxiliary storage of at most `V` entries and the returned empty list has constant size. Keeping an order changes storage accounting, not the cost of visiting each edge.

## Interview English and a master map

Why use indegree? "It counts unfinished prerequisites. A course becomes available exactly when its count reaches zero."

Why can each edge be handled once? "I store each dependent under its prerequisite. When that prerequisite finishes once, I visit that edge once and remove one obligation."

Why does an empty queue sometimes mean failure? "If unfinished courses remain, each still waits for an unfinished prerequisite. Following those prerequisites in a finite graph must reach a cycle."

What are the bounds? "Construction and traversal take `O(V + E)` time under the stated bounded-scalar and container cost model. Adjacency storage, counts and the queue use `O(V + E)` auxiliary space. The result is one Boolean."

The master map connects the argument: `[a, b]` creates `b -> a`; outgoing lists locate the obligations a completion removes; remaining counts decide availability; a queue retains that availability until processing; the checkpoint keeps counts aligned with unfinished prerequisites; and the completed-course count distinguishes a finished graph from a blocked remainder. Counting one visit per course and edge gives the time bound only after the queue and append-sequence costs have been explained.
