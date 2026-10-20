# Author English approval before translation

Approved at UTC: 2026-10-20T18:59:22.493935+00:00

The first complete English body was preserved; the final complete body was read from article.en.md before this approval. This is author reconstruction, not an independent Reader or learner claim. No translation file exists yet in this author's workflow.

## Scope reconstructed from the actual final body

The final body proposes three working methods: recursive include/exclude enumeration, iterative prefix doubling, and exact-size pruned search. Contiguous pieces, arbitrary ordering, and storing the mutable path are rejected approaches, not recommended methods. No bitmask, generator, duplicate-input adaptation or count-only implementation is proposed.

### Recursive enumeration

Permission: distinct input values and unrestricted result order. Exact passage: "Since values are distinct, two different sequences of these yes/no decisions must disagree on membership of some value." Representation and checkpoint: "At entry to a call `visit(i)`, `path` contains exactly the included values among `nums[0:i]`, in input order." Runtime ownership: "All calls use the same `path` and `result` lists from their enclosing function." Updates/result: "The exclude branch needs no list change. For the include branch, append `nums[i]`, explore the remaining positions, and remove that appended value." Return requirement: "when `visit(i)` finishes, it must leave `path` as it found it". Preservation: "A new subset list can keep its entries even when `path` later loses an entry." These passages explain why mutable state may be reused and why the result must be copied.

Initialization is empty prefix/empty path; children advance `i`; leaves save only complete choices; postorder induction proves restoration before using it for sibling correctness. Termination passage: "Each recursive call increases `i` by 1. It stops at `n`". Cost passages: "there are `2**n` leaves"; "the output therefore contains exactly `n * 2**(n - 1)` element entries"; "one path of length at most `n` and at most `n + 1` active calls". Temporary snapshot is counted explicitly: "counting that transient list separately leaves this bound unchanged." Returned output includes outer references, inner objects and element slots; inputs are excluded from auxiliary space. n=0 is a defensive extension, and formulas are restricted to n>=1. Large-n extrapolation assumes recursion capacity/memory and counts list-reference operations, not exact bytes.

New reconstruction from body alone: for [0,-1], exclude 0 then exclude -1 saves []; include -1 saves [-1] then removes it. Back at position 0 append 0; exclude -1 saves [0]; include -1 saves [0,-1]; pop -1 then pop 0. Result order [[],[-1],[0],[0,-1]], working path empty. Every discard is an undo after completed traversal, never loss of an unvisited branch.

Rejected mutable-answer replacement: exact passage "The final `pop()` empties the one shared list, so the returned result becomes `[[], []]`, with both entries referring to the same object." The size-one witness is minimal under legal input length. Runtime controls will execute that mutation separately. Contiguous shortcut fails on the explicit noncontiguous [2,7] witness; arbitrary order duplicates membership [2,5].

### Iterative doubling

Condition: all subsets requested and recursive calls undesirable. State: "before processing `x`, `result` contains every subset of the already processed prefix exactly once." Initialization [ [] ]; each old row is retained, and concatenation allocates an include row. Boundary: "The stored count remains 2 even after the outer list grows." Keeping the fixed old count ensures newly appended rows never receive x twice. Uniqueness: "The old half lacks `x`; the added half contains it, and removing `x` recovers a unique old row." The preserved premise is distinct values and fixed position order, giving disjoint halves. The loop advances through finite nums and fixed finite ranges. For new input [0,-1], old_count 1 produces [0], next old_count 2 produces [-1], [0,-1], giving [[],[0],[-1],[0,-1]].

Costs are independently accounted rather than copied from recursive syntax: "There are `1 + 2 + ... + 2**(n - 1) = 2**n - 1` new rows." "Each nonempty final subset is created once by copying its earlier entries and adding its last value." Consequently same final entry writes, Theta(n*2**n) time/output. Additional operations: a singleton temporary for each concat and a fixed-count index loop. Retained state passage: "It never copies the outer list: the old rows remain part of the final output." Temporary state: "A temporary `[x]` has one entry, and the new concatenated row has at most `n` entries before its append." O(n) auxiliary under transient-row convention, O(1) control/singleton if new row classified as output immediately. No recursive stack or path is retained. Allocator implementation scratch is outside the article's high-level container/call-state model.

### Exact-size search

Changed premise: "exactly `k` values, where `0 <= k <= n`". State remains next undecided index and selected path; storage and operation order remain those of main recursion. New rejection: "Even including all of them cannot succeed when `len(path) + (n - i) < k`". New success: "When `len(path) == k`, every remaining position must be excluded." Return safety: "Neither early return changes `path`, so the restoration proof still applies." Completeness passage added during review: "Every size-`k` subset still has its unique decision route: no prefix of that route is impossible, and once it reaches `k` selected values its remaining exclusions are forced." It preserves the original bijection premise, merges only a forced exclusion suffix, and cannot duplicate a saved subset. At i=n, success or impossibility prevents index access.

New reconstruction [0,-1], k=1: exclude 0 leaves one undecided position; excluding -1 fails 0+0<1; include -1 saves [-1] and returns. Include 0 saves [0] immediately with remaining exclusion forced. Result [[-1],[0]], path restored. k=0 saves the empty subset at the root. k=n permits only the all-include route, with O(n) rejected siblings.

Cost passages: "Calls are a subset of the original binary search tree"; "Copies write `k * C(n, k)` entries, and creating the lists costs another `C(n, k)` units." Therefore O(2**n+(k+1)*C(n,k)) is an upper bound, expressly not tight for every k. O(n) auxiliary includes stack/path/transient snapshot; output Theta((k+1)*C(n,k)) counts the empty list object at k=0. Both changed early returns reduce operations while preserving the same state discipline.

## Primary-source and editorial review

LeetCode description read directly: unique integers, every subset, any result order, length 1..10, values -10..10. No editorial/community content was read. Official Python 3.14 documentation read for list append/pop/copy, binding, recursive calls, list concat, ranges and mutable-sequence iteration. CPython exact v3.14.0 listobject.c checked for copy/concat reference loops and list_resize overallocation. Python docs currently identify 3.14.8; runtime evidence will record its actual installed version separately and is not relabeled as 3.14.0 execution.

The supplemental reader-attention review was actually applied sentence by sentence: retained the worked trace, identity failure, copy-cost derivation, state restoration proof, alternate-state/cost explanation, and exact-size pruning witnesses because each performs a different reconstruction step. Removed only the false generic append-assignment warning and bold markup; local clarity changes are listed in author-revisions.md. Added missing causal premises before approval. Code and citations preserved. No figures needed: the sequential concrete-value trace carries all state transitions without a compressed state poster. No assets generated.

Source/meaning check completed across the entire English body including alternative, changed constraint, interview English and closing map. Negation, assumptions, values, snapshots, input immutability, time versus output/auxiliary space, and hypothetical trace status checked. CONTENT_REVIEWED=author; English approved for translation.

## English reapproval after bilingual terminology discovery

UTC: 2026-10-20T19:01:30.741091+00:00

Re-read the repaired contract paragraph and entire exact-size section. Correct support passage now: "Calls occur only where the original include/exclude search would also call `visit`, hence there are at most `2**(n + 1) - 1`." The new operations stop paths earlier; they create no additional recursive branch, so the original full-call-count upper bound still applies. Definition added: "The collection of all subsets is called the power set." This introduces no new approach or changed cost. Other final-body passages quoted above remain present. English approved again before revising the final translation. The initial full translation did begin only after the first full English semantic approval; this later author correction is recorded rather than hidden.
