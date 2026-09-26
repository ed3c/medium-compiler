# Measure actual writer behavior and zero-context reading

## Sub-features

- Inspect actual traces and use the relevant evals-skills method.
- Compare fresh baseline/treatment writer sessions under a frozen task and observer.
- Independently check reader causal reconstruction from the article alone.

## How to get to it (user POV)

Invoke medium-behavior-evals with an approved isolated writer/reader carrier and actual
traces. The deterministic verification wrapper only checks readiness; it cannot run those
experiments or certify their results.

## Driving it with verify-medium

Source: ../../medium-behavior-evals/SKILL.md; imported eval-audit/error-discovery and judge methods.

Run `python3 .agents/skills/verify-medium/scripts/verify.py --feature behavior-evals --out /tmp/medium-behavior-NEW`.
The doctor checks local prerequisites and records Codex availability. In this environment
expect BLOCKED, exit 3, with missing carrier/session/label prerequisites in feature-results.json.
Do not replace this missing drive with a scripted path or report an unexecuted source wave.
For actual runs, follow the behavior skill: fixed identities, every raw trace, per-run
quality/nonregression and a source-bound final article diff. Reader answers must cite the
article, not an answer key supplied to the reader.

## Gotchas

A nonzero natural baseline is needed for improvement. 0->0 is scoped nonregression, missing
runs are not zeros, and planted controls measure sensitivity only. No uncalibrated judge,
word-count reduction or writer self-review proves improved human understanding.
