# Continue from the real boot article with source-bound additions

## Sub-features

- Boot snapshots the existing article, explicit knowledge units and source bytes.
- Drill-down accepts only the next unit; retry is NOOP, skipped/stale units refuse.
- Empty queue still requires a current review before final exact assembly.
- One stable Ops case and source commit carry the two learning steps; code/test/eval
  anchors are byte-bound. Human prompts appear together at the patch boundary.

## How to get to it (user POV)

Use scripts/lossless_batch.py boot, next, drill-down, render and finish with the actual
article and patch inputs in evidence/issue-8/. No network, provider key or Medium account.
`checkpoint` accepts an actual reader's ordered answers; the checked-in run has no such
answer. A synthetic answer is used only in unit tests of the receipt mechanism.

## Driving it with verify-medium

Source: scripts/lossless_batch.py; evidence/issue-8/plan.json and pinned Ops code,
runtime test, eval runner and historical report snapshots.

Run `python3 .agents/skills/verify-medium/scripts/verify.py --feature lossless-drilldown --out /tmp/medium-lossless-NEW`.
Observe CONTINUE after boot, refusal on premature finish and patch 2 before patch 1,
then patch 1, new-process next, identical retry NOOP, patch 2 and review-and-finish.
The actual review is author-only. Finish drives the existing compiler and preserves
boot -> deltas -> canonical bindings. After copying proof and cleaning scratch, re-run
next on the relocated retained run; expect DONE scoped to these declared units.
Confirm the checkpoint is DEFERRED during patches, then PENDING after the queue and after
DONE. Verify the 4/4 historical model result is labeled separately from runtime finding
tests, and DONE reports human_learning_outcome=NOT_MEASURED.
Keep commands.json, lossless-run/ and article.md under --out.

## Gotchas

Removing the two inserted delta byte strings reconstructs the original article. That is
literal preservation, not universal semantic correctness. A source-anchor match cannot
judge explanation quality. The queue is frozen; new scope needs a new explicit plan,
not deleting pending work. Technical replacements are outside this add-only path.
