# Failures and expected negative controls

Unexpected failed commands: none. All executed shell and detector/runtime commands returned exit 0.
Unexpected failed runtime cases: none.

Intentional incorrect-algorithm controls (actual observed results in runtime.json):

1. Overwrite component end with latest end: input [[1,5],[2,3]], observed [[1,3]], required [[1,5]]. Root cause: forgetting the component's furthest reach. Article already uses max; no repair.
2. Treat equality as a gap: input [[1,2],[2,3]], observed [[1,2],[2,3]], required [[1,3]]. Root cause: violating closed-endpoint overlap. Article already uses strict > gap; no repair.
3. Apply last-only frontier without sorting: input [[5,6],[1,2],[2,5]], observed [[5,6]], required [[1,6]]. Root cause: nondecreasing-start premise absent. Article already sorts; no repair.

The first combined instruction read was output-truncated, so the complete construction file and the first 130 lines of sloptrim were then read separately before drafting. This was a tool-output display limitation, not a failed source read or invented evidence.

Author-only edits, before first delivery: see author-repairs.md. First complete drafts remain unchanged. No external Reader revision was received or applied.
