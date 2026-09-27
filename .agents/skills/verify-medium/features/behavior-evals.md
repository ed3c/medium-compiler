# Measure actual writer behavior and zero-context reading

## Sub-features

- Inspect actual traces and use the relevant evals-skills method.
- Compare fresh baseline/treatment writer sessions under a frozen task and observer.
- Independently check reader causal reconstruction from the article alone.

## How to get to it (user POV)

Invoke medium-behavior-evals on the already selected host route. ChatGPT cloud uses the
platform's exposed native subagent tool; Local Codex uses the retained local runner.
Neither ordinary verification nor writing CI launches a model. A missing local executable,
API key or local sandbox is not a prerequisite for the native-cloud route.

## Driving it with verify-medium

Source: ../../medium-behavior-evals/SKILL.md and
evals/writing/ops-evidence-handoff/cloud-native.md. Only the explicitly selected local
route uses scripts/run_writer_pair.py and scripts/evaluate_writer_run.py.

Run `python3 .agents/skills/verify-medium/scripts/verify.py --feature behavior-evals --out /tmp/medium-behavior-NEW`.
It checks repository/CLI integrity and reports missing reviewed experiment evidence without
probing Codex or native capabilities. BLOCKED / exit 3 is evidence readiness, not a Host
launch gate. It does not certify a carrier, launch children, import reviews or grant closure.

For cloud repository validation, use the existing writing-verification Actions at the exact
candidate head and read back its jobs/artifacts through GitHub. For native writer/reader
work, use the actual current schema, no inherited conversation, pinned inputs and actual
request/result capture. Follow the native recipe's pilot and comparison limits.

For deliberately selected local work, the existing experiment README retains offline packet
preparation, local doctor, real host qualification, unscored pilot and the fixed six runs.
Those records stay local; never relabel them or native child messages to fit another format.

Keep fixed identities, every attempt, per-run quality/nonregression and a source-bound
article diff. Reader answers must cite the article, not an answer key given to the reader.

## Gotchas

A nonzero natural baseline is needed for improvement. 0->0 is scoped nonregression, missing
runs are not zeros, and planted controls measure sensitivity only. No uncalibrated judge,
word-count reduction or writer self-review proves improved human understanding.

Soodles #159 proves scoped Host routing and an uncounted task-local native launch, not a
matched writer study or a complete independent child transcript. Its scope amendment is
not this Issue's acceptance. Missing capture blocks the affected comparison; missing native
launch applies to this Session, not every cloud Session or unrelated authorized work.

`test_verification_host_route.py` drives the real verification entry with and without a
Codex trap on PATH. It checks absence of an unintended executable probe, not model behavior.
`test_writer_observer.py` retains synthetic local transport/observer controls. Neither is
fresh writer/reader evidence. The source-review wave remains independent and required.

The same-article writer-pair/replay.py remains author-reviewed product evidence, not an
accepted Ops PR24 episode. The old cloud CLI probe and its failures remain historical under
evidence/issue-8/cloud; its executable/workflow are retired, not native-cloud prerequisites.
