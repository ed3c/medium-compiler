# Number of Islands: claim every cell, count each region once

Two land cells can belong to one island without touching each other. They need a route through land, and that route may bend. Counting cells, horizontal strips, or visible corners therefore answers a different question from counting islands.

A useful procedure is to find one land cell, record every land cell reachable from it, and count that whole region once. Then continue looking for land that no earlier search recorded. The discovery record must prevent a region from being counted twice.

## What the map permits

In [LeetCode 200](https://leetcode.com/problems/number-of-islands/), `grid` is a rectangular collection of rows. A cell contains the string `"1"` for land or `"0"` for water. Rows and columns each number from 1 to 300. The answer is one integer: how many separate islands the map contains. Movement joins land through a shared horizontal or vertical edge; touching at a corner does not join it. Outside the rectangle is water.

Use `(r, c)` for a cell's row and column, both starting at zero. For example, `(1, 3)` means the second row's fourth cell. A land path is a sequence of land cells in which each consecutive pair shares an edge. Cells belong to the same island exactly when such a path connects them. A cell connects to itself by a path with no moves; reversing a path preserves connection, and joining two paths extends connection. Thus land separates into groups with no land path between groups. These groups are also called connected components.

All-water input returns 0; one land cell returns 1. A rectangle full of land also returns 1, however many cells it contains. The two land cells in `[["1", "0"], ["0", "1"]]` return 2 because their contact is diagonal. An empty grid is outside the stated contract, so the solution below reads `grid[0]` without an empty-input guard.

The solution preserves the supplied map. It keeps a separate record of discovered cells, avoiding a requirement that callers let it overwrite land. No area, coordinates, or island labels are returned.

## A scan finds starts; a search claims whole islands

Read the map row by row, moving left to right within each row. Water cannot start an island. Previously discovered land cannot start a new island either: an earlier search already claimed it. When the scan finds undiscovered land, increase `count` by one and search from that cell until there is no reachable land left to discover.

Why must that search finish before the scan continues? Consider this constructed map, with strings abbreviated as digits:

```text
1 0 1
1 1 1
```

There is one island: the bottom row connects both top cells. A tempting rule, "count land when neither its upper nor its left neighbor is land," counts both top cells and returns 2. The connection appears later in scan order. Inspecting only already-scanned neighbors cannot justify a final new-island decision unless the algorithm also knows how to merge earlier groups. Searching the complete reachable region avoids that extra machinery.

For discovery records, `seen[r][c]` is a Boolean: `True` means this cell has already been claimed for a search. It does not mean that all the cell's neighbors have been examined. That distinction leaves room for unfinished work.

Keep that unfinished work in `stack`, a list of coordinates waiting for neighbor examination. A stack uses last-in, first-out order: the most recently added coordinate is processed next. This is an iterative depth-first search, or DFS. Its order tends to follow newly discovered branches before returning to older waiting cells. Any pending-cell order works for this count if it eventually examines every discovered cell.

When a land cell is discovered, set its `seen` entry to `True` immediately and put its coordinates on the stack. Marking at discovery ensures that another neighboring cell cannot schedule it again while it is still waiting. When a coordinate is removed from the stack, examine its four neighboring positions. Schedule only neighbors that are inside the rectangle, land, and still undiscovered.

## The Python objects carry different kinds of state

The discovery record needs one independently writable Boolean entry per cell:

```python
seen = [[False] * cols for _ in range(rows)]
```

`[False] * cols` makes a row containing `cols` entries, initially all `False`. The comprehension evaluates that row-building expression once for each row, creating separate row lists. The variable `_` has an unused value. For two rows and three columns, the initial values look like `[[False, False, False], [False, False, False]]`.

Separate row lists matter. The shorter-looking `[[False] * cols] * rows` repeats references to a single row. Changing `seen[0][0]` would then also change what `seen[1][0]` reads. Our construction shares only the immutable Boolean values, not the mutable row lists. Python's documentation explains this [sequence repetition behavior](https://docs.python.org/3.14/library/stdtypes.html#common-sequence-operations).

`seen[nr][nc] = True` replaces one entry of one row. It does not change `grid`, and it does not modify the `False` object. A coordinate such as `(0, 1)` is a two-item tuple holding a row number and a column number. Storing the pair keeps those numbers together as one pending task. The later assignment `r, c = stack.pop()` puts the pair's first item into `r` and its second into `c`; this is [assignment unpacking](https://docs.python.org/3.14/reference/simple_stmts.html#assignment-statements).

For a stack equal to `[(0, 1), (1, 0)]`, `stack.pop()` returns `(1, 0)` and leaves `[(0, 1)]`. `stack.append((1, 1))` then changes the list to `[(0, 1), (1, 1)]`. `append` returns `None`, so use it as a statement; assigning its result back to `stack` would lose the list reference. Neither operation copies the grid. These are the documented [Python list stack operations](https://docs.python.org/3.14/tutorial/datastructures.html#using-lists-as-stacks).

The loop `while stack:` runs while pending coordinates remain. The empty list is false in a condition, so the loop stops before calling `pop()` on an empty stack. Neighbor tests check bounds before indexing. Python accepts negative list indices, so an unchecked row `-1` would read the last row instead of representing outside water. In an `and` expression, Python stops as soon as a condition is false; placing bounds first prevents an invalid position from reaching the grid access. These rules follow Python's [truth-value and Boolean operation semantics](https://docs.python.org/3.14/library/stdtypes.html#boolean-operations-and-or-not).

## Follow one complete search

Suppose the input is:

```text
       c=0 1 2 3
r=0     1 1 0 0
r=1     1 1 0 1
r=2     0 0 1 1
```

The upper-left square is one island. The three cells near the lower-right corner form another; `(1, 1)` and `(2, 2)` do not connect diagonally. The expected answer is 2.

Initially `count = 0`, every `seen` entry is `False`, and there is no active stack. The scan reaches `(0, 0)`, sees undiscovered land, and changes `count` to 1. It marks `(0, 0)` and initializes `stack = [(0, 0)]`.

Use neighbor order up, right, down, left throughout this trace and the code. Popping `(0, 0)` leaves `[]`. Up `(-1, 0)` fails bounds. Right `(0, 1)` is undiscovered land: mark it and append it. Down `(1, 0)` is also undiscovered land: mark it and append it. Left `(0, -1)` fails bounds. Now `stack = [(0, 1), (1, 0)]`; exactly `(0, 0)`, `(0, 1)`, and `(1, 0)` are marked.

Next, `pop()` returns `(1, 0)`, leaving `[(0, 1)]`. Its upper neighbor `(0, 0)` is already marked. Its right neighbor `(1, 1)` is new land, so mark and append it. Down `(2, 0)` is water, and left `(1, -1)` is outside. The stack becomes `[(0, 1), (1, 1)]`, with all four square cells marked.

Popping `(1, 1)` leaves `[(0, 1)]`. Up `(0, 1)` is marked even though its own neighbor examination has not happened yet. Right `(1, 2)` and down `(2, 1)` are water; left `(1, 0)` is marked. Nothing is appended. Finally pop `(0, 1)`: up is outside, right is water, and down and left are marked. The stack becomes empty. This search claimed exactly the square, and `count` is still 1.

This square also exposes the reason for marking when scheduling. If marking were delayed until popping, `(0, 1)` would still look undiscovered when `(1, 1)` checks its upper neighbor. The stack could become `[(0, 1), (0, 1)]`. A carefully written delayed-marking algorithm can reject repeated entries later, but it needs that extra rule. This solution prevents them from entering.

The row scan resumes. It skips `(0, 1)` because it is marked, `(0, 2)` and `(0, 3)` because they are water, `(1, 0)` and `(1, 1)` because they are marked, and `(1, 2)` because it is water. At `(1, 3)`, it finds new land and changes `count` to 2. Mark and push `(1, 3)`. Popping it discovers only `(2, 3)`; popping `(2, 3)` discovers only `(2, 2)`; popping `(2, 2)` discovers nothing. In each case the popped coordinate is removed before the new one is appended, so the successive stacks after neighbor examination are `[(2, 3)]`, `[(2, 2)]`, and `[]`.

The remaining scan positions `(2, 0)` and `(2, 1)` are water, and `(2, 2)` and `(2, 3)` are marked. Return 2. The final `seen` values are:

```text
True  True  False False
True  True  False True
False False True  True
```

Water remains unmarked. The input grid retains its original strings.

## The complete solution

```python
class Solution:
    def numIslands(self, grid: list[list[str]]) -> int:
        rows = len(grid)
        cols = len(grid[0])
        seen = [[False] * cols for _ in range(rows)]
        count = 0
        directions = ((-1, 0), (0, 1), (1, 0), (0, -1))

        for row in range(rows):
            for col in range(cols):
                if grid[row][col] != "1" or seen[row][col]:
                    continue

                count += 1
                seen[row][col] = True
                stack = [(row, col)]

                while stack:
                    r, c = stack.pop()
                    for dr, dc in directions:
                        nr, nc = r + dr, c + dc
                        if (0 <= nr < rows and 0 <= nc < cols
                                and grid[nr][nc] == "1"
                                and not seen[nr][nc]):
                            seen[nr][nc] = True
                            stack.append((nr, nc))

        return count
```

`directions` holds four changes to a coordinate. For example, adding `(0, 1)` keeps the row and increases the column, moving right. `row, col` belong to the outer scan; `r, c` belong to the current search. Keeping different names prevents a popped coordinate from overwriting the scan's current start position. `continue` skips the rest of the inner scan iteration when a cell cannot start a new island.

The code compares strings with `"1"`; comparing a cell to the integer `1` would reject every legal land cell. It assumes rectangular rows containing the specified strings. It does not validate ragged rows or convert integer grids into this contract.

## Why every island contributes exactly one

The path-based grouping describes what an island is, regardless of the program. A loop invariant describes what the program has accomplished at a particular checkpoint. These are different claims.

During one search, consider the checkpoint just before each `while stack` test. Every coordinate on the stack is marked land belonging to the starting cell's original island, and no coordinate appears twice. Every marked cell from this search is either waiting on the stack or has already had all four neighbors examined. Any land neighbor of an already examined cell has already been marked.

The checkpoint holds initially: the only marked cell of this search is its start, waiting for examination. A pop removes one pending coordinate. For each neighbor, bounds and land checks ensure that any newly scheduled cell is connected by a legal edge to the popped cell. The `seen` check and immediate marking prevent duplicate scheduling. After all four checks, the popped cell has been fully examined, restoring the invariant.

At most one push occurs for each land cell, and every loop iteration pops one item. The finite grid therefore makes the search terminate. When the stack is empty, all cells discovered by this search have been examined. If some land cell in the same island were still undiscovered, take a land path from the start to it. The first undiscovered cell on that path has a discovered predecessor. That predecessor was examined and would have discovered it, a contradiction. The search reaches the entire island and cannot reach a different one.

For the outer scan, use the checkpoint before examining its next cell, after any preceding search has finished. All islands already counted have been completely marked, `count` is their number, and every earlier scan position that contains land is marked. Initially there are no earlier positions and `count` is zero. Water and marked land preserve the claim without increasing the count. Undiscovered land belongs to an island not previously counted, so adding one and completing its search preserves the checkpoint. After the last scan position, every land cell belongs to a counted island. No island can have contributed twice because its first search marked all of it.

## Count the work, including the waiting list

Let `m` be the number of rows, `n` the number of columns, and `L` the number of land cells, with `L <= mn`. Big O describes how a cost can grow with input size while ignoring fixed multipliers. Here `O(mn)` means bounded by a fixed multiple of the number of cells, under the operation assumptions below; it is not a timing prediction.

Building `seen` writes `mn` Boolean references. The outer scan examines `mn` cells. Across all searches together, each land cell is pushed and popped once, so there are `L` pops and `4L` neighbor checks. The search inside the scan does not imply `mn` whole-grid searches: completed discoveries remain marked and cannot be repeated. The total is `O(mn + L) = O(mn)` time.

This count treats bounded-size integer arithmetic, coordinate access, Boolean access, and one-character comparison as constant work. List end operations require a qualification. In CPython v3.14, a list keeps an array of object references with spare capacity; growth can allocate space and copy references, so a particular append need not be constant time. Capacity grows proportionally for repeated small extensions. For capacities growing by a factor greater than one, the copied sizes form a geometric sum bounded by a constant times the final size: read backward as `K + K/q + K/q² + ...`, for a fixed `q > 1`. Across many appends this spreads resizing work over the operations. "Amortized constant time" means that total bound per operation, not a guarantee for each call. Shrinking also leaves capacity room before another resize, so alternating end pushes and pops do not force a copy on every operation. The [CPython v3.14 list implementation](https://github.com/python/cpython/blob/v3.14.0/Objects/listobject.c) supplies these growth and shrink policies; they are implementation details, not a Python-language timing guarantee.

The `seen` matrix retains `mn` entries. At most `L` coordinates can be pending simultaneously, and each coordinate contains two bounded-size integers. Thus auxiliary space, meaning storage added beyond the input, is `O(mn)` in the worst case. An explicit stack does not make DFS constant-space. The directions and current coordinates occupy fixed extra space. The returned integer is one value, counted as `O(1)` output space under this bounded-input model. Counting its digits for unbounded dimensions would require a different numeric model.

## When a different choice earns its place

Recursive DFS replaces the explicit stack with a function that calls itself on neighbors. Each unfinished function call must retain enough state to resume its neighbor checks after the child returns. A long, thin land path can require many simultaneous calls, so recursion does not remove the storage cost. Python has a [recursion limit](https://docs.python.org/3.14/library/sys.html#sys.getrecursionlimit); a legal large island can require a depth beyond the configured limit. The iterative version makes the pending storage explicit and avoids relying on that call depth.

Breadth-first search, or BFS, processes the oldest pending cell first. A `collections.deque` supports appending at one end and removing from the other with `popleft()`. With the same discovery marking, BFS counts the same islands in `O(mn)` time and `O(mn)` worst-case auxiliary space. Avoid replacing `pop()` with list `pop(0)`: removing the front of a list shifts remaining entries. Python documents [deque operations](https://docs.python.org/3.14/library/collections.html#collections.deque) as approximately constant-time at either end.

BFS becomes preferable if the task changes to finding the fewest edge moves from one land cell to another. Put the start in a queue at distance zero. Its neighbors receive distance one, their newly discovered neighbors receive distance two, and so on. Oldest-first processing finishes each distance layer before the next, so the first discovery of the destination has the smallest move count. Our DFS stack does not preserve that ordering, so a first-found route need not be shortest. This adaptation also needs a stored distance or queue-layer counter; merely returning the island count cannot answer it.

If memory matters and the caller explicitly allows overwriting the map, land can be changed from `"1"` to `"0"` when discovered. Later checks then treat claimed land like water, replacing the separate `seen` matrix. The stack can still require `O(mn)` space, and callers lose the original map. Copying first to preserve it restores `O(mn)` copy storage; copying only the outer list shares the original row lists and does not protect their entries.

A change to the connection rule has a different effect. If diagonal contact also joins land, add the four diagonal coordinate changes and use that rule consistently in the proof. The two-cell diagonal witness then changes from 2 islands to 1. There are eight checks per popped cell instead of four, still a fixed number, so the `O(mn)` bounds remain.

## Interview answers and a reconstruction map

Why increase the count before the search? An undiscovered land start identifies one previously uncounted island. The search records that entire island before scanning resumes.

Why mark before pushing? A waiting cell is already discovered. Immediate marking prevents another neighbor from placing the same coordinate on the stack again.

Why examine four directions? The statement connects cells by shared horizontal or vertical edges. Diagonal contact does not establish a legal path.

Why is the time linear in the number of cells? The scan checks every cell once, and each land cell causes one pop and four neighbor tests across all searches.

What does preserving the input cost? The Boolean matrix uses `O(mn)` auxiliary space. Even if permitted mutation removes it, the explicit stack still has an `O(mn)` worst-case bound.

The reconstruction chain is: edge-connected land defines one region; the scan selects an undiscovered representative; discovery marks prevent duplicate scheduling; the stack retains neighbor work; exhausting that work records the whole region; the next undiscovered representative must belong to another island. The return value counts those completed regions.
