# Author construction notes

Selected host: local assigned task only; no compiler/provider/publication route authorized.
Read the four exact instruction snapshots. No exemplars followed. No repository files read.

Causal spine: output must preserve the exact union of closed intervals while removing every overlap. Unsorted input cannot establish that an apparent gap is permanent. Sorting by start establishes nondecreasing future starts. Keep a list of already merged components; its final component alone may still grow. If a new start exceeds its end, the gap cannot be bridged by any future interval; otherwise extend to the greater end, preserving containment. New output pairs avoid writes through shared source pairs. The loop ends after every sorted pair has been incorporated; the invariant yields the complete union and pairwise gaps.

Separating witnesses: [[1,5],[2,3]] defeats overwriting the frontier with the latest end; [[1,2],[2,3]] defeats a strict-overlap test; [[5,6],[1,2],[2,5]] shows a gap in unsorted order can be bridged later. The Program Movie combines nesting, touching, disjoint output and singleton/equal-start behavior: [[8,10],[1,7],[3,4],[7,8],[12,12],[12,14]].

Audience dependency order: closed interval and exact union -> why input order is unsafe -> sorted frontier -> state meaning -> Python new outer list / shared source pairs / fresh output pairs -> full code -> full state transitions -> invariant proof -> cost model and logarithm -> sorted-stream pivot -> interview reconstruction and Master Map.

Figure choice: no image is necessary. Literal state blocks and the single Program Movie show all state changes without a visual encoding to learn. No figures rendered or image generation launched.

Source selection: LeetCode statement; Python 3.14 builtins, sorting howto, list tutorial, sequence semantics; CPython v3.14.0 listobject.c and listsort.txt. Online docs currently identify themselves as 3.14.8; runtime is local Python 3.14.6. Implementation discussion is explicitly qualified to pinned CPython v3.14.0 and is not an exact trace of this runtime.
