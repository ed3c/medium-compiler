# Continue from the real boot article with source-bound additions

## Sub-features

- Boot snapshots the existing article, explicit knowledge units and source bytes.
- Drill-down accepts only the next unit; retry is NOOP, skipped/stale units refuse.
- Empty queue still requires a current review before final exact assembly.

## How to get to it (user POV)

Use scripts/lossless_batch.py boot, next, drill-down, render and finish with the actual
article and patch inputs in evidence/issue-8/. No network, provider key or Medium account.

## Driving it with verify-medium

Source: scripts/lossless_batch.py; evidence/issue-8/plan.json and the pinned Ops main.py.

Run `python3 .agents/skills/verify-medium/scripts/verify.py --feature lossless-drilldown --out /tmp/medium-lossless-NEW`.
Observe CONTINUE after boot, refusal on premature finish and patch 2 before patch 1,
then patch 1, new-process next, identical retry NOOP, patch 2 and review-and-finish.
The actual review is author-only. Finish drives the existing compiler and preserves
boot -> deltas -> canonical bindings. After copying proof and cleaning scratch, re-run
next on the relocated retained run; expect DONE scoped to these declared units.
Keep commands.json, lossless-run/ and article.md under --out.

## Gotchas

Removing the two inserted delta byte strings reconstructs the original article. That is
literal preservation, not universal semantic correctness. A source-anchor match cannot
judge explanation quality. The queue is frozen; new scope needs a new explicit plan,
not deleting pending work. Technical replacements are outside this add-only path.
