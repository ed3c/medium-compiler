# Pending learning-handoff writer experiment

One Issue #8 continuation. This is a writer-only, frozen pending-state experiment, not a
new Ops feature. `experiment.json` pins the common task, actual article, raw source snapshots,
owner observation and both historical writing implementations. No accepted record is invented.

## What is being compared

- Baseline writer instructions/prompt/CLI: `71fce847f6b521d812ba8179dcf4f53e06a69ef6`.
- Treatment writer instructions/prompt/CLI: `df138896a7e6190650b22478801953628e261481`.
- Common original compiler, retained writing contract, task, article and source bytes.
- Fixed interleaved order: baseline, treatment, treatment, baseline, baseline, treatment.
- One pilot is explicitly outside those six runs. No resume, reseeding or automatic retries.

The plan has `purpose=learning-episode` with no learning handoff. Both old and new versions
can read that same input shape. It does NOT send a v2-only ACCEPTED record to the old CLI and
score its parser failure. The owner observation is a dated snapshot of Ops PR24, not a live
revocation query. A real owner must select this frozen observation for the comparison.

The common capsule AGENTS.md scopes this task to writing, not verification. Only the versioned
writer skill, drill-down task adapter and lossless helper vary. The canonical writing contract
is common. Full repo history, new article explanations, expected answers, evaluator code,
review artifacts and prior experiment reports are NOT copied into writer workspaces.
This measures the selected bounded writing route, not unrestricted Codex auto-discovery.

## Executable path

Use two existing exact checkouts. Preparing only reads selected source files; it does not
checkout branches, copy credentials, install Codex, invoke models or alter global skills.

```sh
python3 scripts/run_writer_pair.py doctor
python3 scripts/run_writer_pair.py prepare \
  --spec evals/writing/ops-evidence-handoff/experiment.json \
  --baseline-root /absolute/checkouts/71fce847 \
  --treatment-root /absolute/checkouts/df138896 \
  --out /absolute/new-writer-packet
```

Preparation checks every input hash BEFORE creating the output directory. It returns the
packet digest. Retain that digest outside the writer. Six selected jobs are fixed in packet.json.
A single current working tree cannot substitute for the two pinned input implementations.

## Carrier boundary: required before model calls

The runner is NOT a container manager or a read-isolation implementation. Codex workspace-write
limits writes but does not by itself hide sibling files or global instructions. Before a pilot,
the host owner must actually establish and reference an isolated host where:

- each model sees only its selected workspace, not sibling arms, controller files, scorer
  answers, repository history, host memories or unrelated personal/global skills;
- model authentication is already provisioned through the authorized host; no GitHub/product
  credentials are available to tools; raw outputs cannot expose the host's credential store;
- external recording is not writable by the model; only the recorder can write capture files;
- policy/tool/config inputs are matched across arms; no external MCP/web/production access.

The host approval is NOT a provider credential. Never put secrets in it. It contains
schema_version=writer-host-approval@1, packet_sha256, owner, isolation_evidence_ref,
effective_config_ref, authentication_ref (a non-secret reference), model, codex_sha256,
codex_version, expires_at (offset-aware), isolation_verified=true and
`effects=["model-invocation","workspace-only-writes"]`. These are owner declarations bound
by an externally supplied digest, not cryptographic proof that the host is isolated.
The runner must not fabricate that approval. Missing qualification means BLOCKED.

The runner reads `codex --version` and `codex exec --help`, and requires the documented flags
in the installed version. It launches only `exec --json --ephemeral`, never resume. It uses
workspace-write with network tools disabled, never a sandbox/managed-rule bypass. It filters
process environment variables and does not forward API/GitHub keys or copy auth.json.
Provider authentication and managed policies remain host responsibilities.

```sh
python3 scripts/run_writer_pair.py run \
  --packet /absolute/new-writer-packet --packet-sha256 <prepared-digest> \
  --phase pilot \
  --host-approval /external/host-approval.json --host-approval-sha256 <owner-selected-digest>
```

A human/operator reviews the pilot's actual lifecycle, requests/results, last message,
file observations and isolation evidence. Only then supply a new host approval containing
`pilot_run_sha256` and `capture_review_ref`, and invoke the same command with `--phase comparison`.
Pilot logs are kept outside the six comparison jobs. File hashes alone are not pilot success.
Any failed/incomplete attempt is retained; the runner stops remaining launches rather than
retrying until green. New folders cannot be used to silently resample a fixed experiment.

## What is recorded and judged

Each job records exact prompt bytes, argv, requested model, executable/version, session ID,
raw stdout JSONL, stderr, final message, exit, elapsed time and before/after file hashes.
The observed model is UNKNOWN unless separate host evidence establishes it. Returned CLI
JSONL plus end snapshots do not prove kernel-level complete reads/writes or hidden context.

The observer validates evidence first: missing/mutated logs, unfinished tools, duplicate
sessions, mismatched models/inputs, a pilot relabeled as a scored run, or an absent selected
run cannot become zero errors. Unknown event types require requalification rather than being
silently discarded. There is no uncalibrated automated LLM judge.

An external reviewer must label every observable completed command/file/message event using
five separate booleans: wrong_owner, premature_article_writing, production_promotion,
unneeded_observation and premature_learning_done. Each label cites an exact event quote and
explains its decision. Rejected attempts still count when they were wrong; successful guard
refusal is not zero writer mistakes. Repeated reads and the word DONE are never scored by
keywords alone. The reviewer also records instruction-read observation, task outcome and
scoped source fidelity; absent/author-only review cannot produce an independent comparison.

Review shape: schema_version=writer-route-review@1, run_sha256, events_sha256, reviewer,
independent=true, instruction_read_observed=true, source_fidelity=PASS|FAIL,
task_outcome=PASS|FAIL, and ordered events=[{line, quote, reason, barriers:{...}}].
An unreviewed capture returns behavior=null, not an all-clear. Reviews are external,
controller-selected artifacts; hashes bind them but do not authenticate the reviewer.

```sh
python3 scripts/evaluate_writer_run.py run \
  --capture /absolute/new-writer-packet/runs/run-01/capture \
  --run-sha256 <controller-recorded-digest> --review /external/review-run-01.json
python3 scripts/evaluate_writer_run.py compare \
  --packet /absolute/new-writer-packet --packet-sha256 <prepared-digest> \
  --selection /external/selection.json
```

Selection maps every predeclared run ID to {run_sha256, review, review_sha256}. Neither
worker outputs nor candidate-authored scores serve as selection. Review and host claims
retain their external trust boundary. No report grants landing/publication/progress authority.

## Evidence ceiling

The primary scope is legal continuation in this pending state. Baseline zero -> treatment
zero is scoped nonregression, not improvement. Article effects and wrong attempts are kept
separate. A lower event count cannot outweigh a forbidden treatment write or semantic/task
failure. The positive accepted-handoff path needs a genuinely accepted episode and a separately
fixed compatible input packet; this first runner deliberately rejects an `accepted` scenario.
It cannot certify positive-path writing, independent reading, human mastery or full Issue #8
closure. Existing reviewer/carrier prerequisites are not waived by installing this runner.

Official CLI references checked 2026-09-27:
- https://developers.openai.com/codex/noninteractive/
- https://developers.openai.com/codex/cli/reference/

Synthetic transport/reviewer tests exercise capture and observer discrimination only. They
are never counted as a natural nonzero baseline, pilot qualification or human labels.
