---
name: medium-behavior-evals
description: Evaluate lossless Medium writing behavior and zero-context reader tasks using actual article edits, fresh traces and the selected evals-skills methods. Use for P-class or combined P/CLI hill climb, not ordinary formatting checks.
---

# Behavior and reader evals

Read ../verify-medium/features/behavior-evals.md. The imported ai-evals-course skills
remain upstream methods; load only the one needed via $evals-start. For this compiler:

- $eval-audit: inspect real article/diffs, CLI traces, current criteria and available labels.
- $error-discovery: observe unknown failures from actual traces. The upstream skill needs
  interactive human review; do not manufacture a human session or its taxonomy.
- $write-code-eval: use executable checks for order, pending-work, byte preservation,
  table layout, refusal and stale receipts. Code can check anchors, not semantic entailment.
- $write-judge-prompt: only a known interpretive failure with trustworthy labeled examples.
- $validate-evaluator: calibrate against held-out expert labels before relying on the judge.
  Its suggested sample sizes/thresholds are method guidance, not laws for every article.

RAG scoring is not needed merely because the article mentions RAG. No synthetic-input skill
may turn a planted corruption into a naturally observed writer failure. No upstream recipe
may grant approval or expand tool permissions. Do not create an eval dashboard just to tick a box.

## Frozen comparison packet

First observe an unmodified fresh baseline on the actual task. Keep exact task/source,
article and skill/CLI hashes, model/carrier settings, raw session IDs and an external observer.
Freeze one failure criterion after discovery, before changing the treatment. Label treatment
P-only, CLI-only or combined; do not attribute combined improvement to prose alone.

Run independent baseline/treatment sessions with identical task/sources/tools/observer.
Do not feed either arm the other output. Keep every attempt. Count observable events only:
wrong next action, forgotten pending unit, repeated unchanged output, unneeded source read,
manual mutation of accepted state, source/condition loss, and premature DONE. Necessary
retrieval and correct refusal are not inefficiency. A local replay is not a fresh Agent.

## Reader packet

Give an isolated reader only the final article, intended audience and fixed questions;
not the author's source/ledger/expected answers. Require article quotations supporting each
answer. Score source fidelity, causal reconstruction and limits separately from writer routes.
For the Ops example, ask why transaction_id maps to a list, what happens with duplicate-left
and missing-right, and when delta is calculated. Expected answers stay with the scorer.
A knowledgeable model can fill gaps from memory, so use an omitted-causal-bridge control.
Human reader benefit requires actual human measurement; an LLM reader is only a proxy.

## Acceptance

Evidence validity first, then per-run correctness and quality nonregression, then barrier
comparison. Nonzero baseline plus fewer barriers with no scoped quality regression supports
OBSERVED_IMPROVEMENT. Zero-to-zero supports SCOPED_NONREGRESSION only. Missing/contaminated
sessions or uncalibrated subjective judgments yield INCONCLUSIVE/NOT_RUN, not zero errors.
Keep final article changes and receipts as product evidence. Test flags, fewer words, a
source-link allowlist and writer self-review cannot certify non-degraded meaning.

No model invocation is performed by this skill's registration. The verification helper
reports unmet carrier/trace prerequisites and never creates imitation A/B records.


## Select the existing host route

In ChatGPT cloud, follow [the native recipe](../../../evals/writing/ops-evidence-handoff/cloud-native.md)
using the current platform tool schema. GitHub/Actions own repository reads, writes and
mechanical receipts; native children own their assigned writer/reader tasks. Do not launch
Codex CLI, install a sandbox, request an API key or select a replacement model runner for
this route. Missing native launch/capture is scoped to the affected Session/claim; continue
other authorized work and refresh exposure only on a new Session or a material change.

The repository verifier reports missing reviewed evidence; it cannot probe native tool
exposure from Python. Its BLOCKED row is not a Host capability verdict or launch gate.
Do not turn native child text into imitation Codex JSONL. Keep actual native input/event
identity, independent capture and local evidence distinct. Soodles #159's narrower closure
does not waive this Issue's matched-writer, reader or source-review requirements.

## Implemented local pending-handoff runner

Only for an explicitly selected Local Codex task, use `scripts/run_writer_pair.py` and the fixed packet
in `evals/writing/ops-evidence-handoff/`. Read that README before launch. `prepare` copies
only pinned common inputs and three versioned P/CLI files per arm; it excludes existing
answers, evaluator reports and repository history. `doctor` probes executable/help only.
A distinct host owner must qualify read isolation, effective configuration, credentials
already provisioned on the host, and one unscored pilot before `run --phase comparison`.
Directories, `--ephemeral` and JSONL alone do not prove context isolation or full capture.

The runner preserves all six planned interleaved runs, raw events, exits, final output,
file snapshots and interruptions. It never resamples a failed run or scores its writer.
`evaluate_writer_run.py run` leaves behavior null until an external reviewer labels every
observable event against exact trace quotations; the reviewer must establish instruction
reads and review task/source fidelity. `compare` requires the fixed complete selection,
unique session identities, a qualified pilot and matching packet/model/carrier identities.
Attempts and final-file effects are separate: a guard refusal does not erase a wrong route.

Current implementation only covers the real pending handoff. Accepted-episode writing and
independent-reader quality checks remain separate prerequisites, not synthetic PASS cases.
An improved pending route is scoped evidence, not automatic Issue #8 acceptance. Never
relabel the test fixture as a model run. Neither host nor reviewer declarations authenticate
themselves; retain their actual owner-provided evidence references.
