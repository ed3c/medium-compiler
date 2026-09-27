# Measure actual writer behavior and zero-context reading

## Sub-features

- Inspect actual traces and use the relevant evals-skills method.
- Compare fresh baseline/treatment writer sessions under a frozen task and observer.
- Independently check reader causal reconstruction from the article alone.

## How to get to it (user POV)

Invoke medium-behavior-evals with an approved isolated writer/reader carrier and actual
traces. The verification wrapper probes runner readiness only; it never launches models from ordinary
verification or CI. The explicit runner below can launch after its separate host/pilot gates.

## Driving it with verify-medium

Source: ../../medium-behavior-evals/SKILL.md, scripts/run_writer_pair.py, scripts/evaluate_writer_run.py
and evals/writing/ops-evidence-handoff/. Imported methods retain their own prerequisites.

Run `python3 .agents/skills/verify-medium/scripts/verify.py --feature behavior-evals --out /tmp/medium-behavior-NEW`.
The doctor executes only Codex version/help when available and records missing prerequisites.
The wrapper remains BLOCKED, exit 3, until actual comparison/reader evidence is reviewed;
an installed binary or a unit-test PASS cannot clear this feature.
Do not replace this missing drive with a scripted path or report an unexecuted source wave.
For actual runs, follow the behavior skill: fixed identities, every raw trace, per-run
quality/nonregression and a source-bound final article diff. Reader answers must cite the
article, not an answer key supplied to the reader.

## Gotchas

A nonzero natural baseline is needed for improvement. 0->0 is scoped nonregression, missing
runs are not zeros, and planted controls measure sensitivity only. No uncalibrated judge,
word-count reduction or writer self-review proves improved human understanding.


### Drive the new mechanism without inventing a study

Run `python3 -m unittest discover -s tests -p 'test_writer_observer.py' -v` for labelled
synthetic transport/observer controls. Then prepare the real packet using exact baseline
71fce847 and treatment df138896 checkouts (see experiment README). Inspect that both capsules
contain the same common source bytes and no expected answer, review or other arm output.
Run `python3 scripts/run_writer_pair.py doctor`: missing Codex must return BLOCKED with
model_calls=0. Save these as mechanism/readiness evidence, never fresh-writer results.

On an actually qualified host, drive unscored pilot -> external capture review -> fixed
comparison -> external event review -> observer comparison. Preserve failed/incomplete runs.
No token/credential is copied by this workflow. The writer sandbox must also isolate reads
from controller data and other sessions; workspace-only writes alone are not sufficient.

The same-article writer-pair/replay.py inserts one source-grounded explanation separating
wrong attempted actions from blocked effects. It is an author-reviewed product delta, not
an accepted Ops PR24 learning episode or a replacement for the pending no-write behavior.
