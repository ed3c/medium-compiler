# Derivation notes

Only task, four instruction snapshots, primary LeetCode/Python sources and own output were read. No exemplar.

Causal spine: choose two original positions; shorter side sets water level, distance sets width. Remember maximum already witnessed and interval of positions whose pairs remain unresolved. Evaluate widest remaining pair, discard shorter endpoint because keeping it and moving the other inward cannot beat its evaluated area. Repeat until interval cannot contain a pair; recorded maximum covers all discarded choices.

Decisions: area rather than height-only selection; exhaustive baseline rather than unexplained shortcut; safe discard rather than chasing a visually tall wall; index state rather than copied slices. Separate pair-area geometric identity from loop invariant about coverage.

Witnesses: [2,5,1,4] -> 8 exposes left move, right move and tie; [1,2,3] -> 2 disproves moving taller endpoint (wrong returns 2 too! use [1,2,4,3] -> 4 instead); choose [1,2,4,3] wrong moves taller: area 3, then2,then1 =>3, true4. For a minimal length witness use [1,3,2]: current2 then wrong1, missed3 =>3. n=2 cannot fail because only pair evaluated.

Changed constraint: arbitrary increasing x coordinates supplied alongside heights; replace r-l by x[r]-x[l], because shrinking interval reduces distance even when gaps differ. Explain main discard still holds, extra coordinate access and subtraction per iteration; no new growing storage; discuss coordinate bound as cost premise.

Alternative: exhaustive all pairs, preferable as tiny-case oracle and when extra scoring destroys discard premise. Derive triangular pair count by pairing counts rather than quoting formula. No sorting alternative or extra unproved data structure introduced.

Sources fetched: exact LeetCode statement; Python3.14 builtin types, functions, assignments, compound statements; CPython v3.14.0 list source/header for direct index and saved size. Current actual execution Python recorded separately; no claim runtime is3.14 unless observed.
