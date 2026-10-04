# Soodles manager cost review

This is case data, not new P-class guidance. Read `case.json`, then the bound English
assessment and Chinese guide under `reports/ai-evals/soodles-manager-cost/`.

## Capture and scope

GitHub connector reads retrieved PR #273, its changed files, runtime job 111385372510,
and collector job 111386059544. `runtime.log` and `collector.log` preserve decoded
connector text with terminal newline normalized, not original HTTP transport bytes.
The repository source revision and provider identities are in the report's source audit.

The coordinator saved `prediction.json` in one execution, retained its SHA-256, then ran
`python3 -B /tmp/staff-evals-manager-review-20261004/project-review.py` from the Soodles
checkout in a later execution. It exited 0 and printed matching output expectations,
28 modules, 504.086 worker seconds and 23 unknown entries. `outcome.json` retains the
observed values and timings. This description is coordinator-authored capture, not an
independent platform transcript or proof of unseen-outcome conditions.

The script used the existing Soodles APIs. No Soodles suite or physical control was
launched. The two synthetic controls changed in-memory review input only. No original
atom authorization, checkpoint, lifecycle admission or current owner response was created.

## Retention and replay

The script is retained exactly as executed, including the session-local source and output
paths. Files formerly under `/tmp/staff-evals-manager-review-20261004/` are retained here
under the same basename. Its exact source checkout was
`/workspace/scratch/7ed56a5a2a33/soodles-work` at the audit's pinned revision.
Its forecast binds both the decoded runtime log and filtered verification log.
`observations.json` and the all-event parse are reproducible intermediates and are not
duplicated in the permanent record; the raw input and actual downstream outputs are.

To replay elsewhere, use a separate copy of the script, change only those two local
paths, and map the forecast's original input locators to the retained files after
checking their hashes. Write into a new directory; preserve these original outcomes.
The expected statuses are deterministic. New timings are new observations and must not
overwrite the measured values. No model/provider credentials or Noodle runtime are needed.

`schema-cost-feedback.json` is actual Test Manager → Schema Manager data feedback.
`owner-feedback.json` retains the unknown current owner transition.
`owner-consumption.json` is the review coordinator's consumption, not a live atom owner's
continuation. The provider's separate 272-second job observation is in `collector.log`;
it was not added to the timing-only API input or confused with whole-task elapsed time.

The case is excluded from population prediction metrics: historical logs and source were
already visible. Eight matched expectations from one source-informed projection exercise
are not eight independent real-agent tasks. Human prediction and calibration are absent.
