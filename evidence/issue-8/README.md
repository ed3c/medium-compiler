# Issue #8 — skills and lossless article continuation

## Scope and sources

Baseline main: ad1b76fd9c0c0ed8f48aecae54aa987964049ce1.
Same article before blob: 19c0ef18be878324fde4670e5d3ad03fcf42e00d.
Ops source: ed3c/ops-reconciliation-copilot@24a56d18661630b0dba97dcb0b057dce07b0ab32:app/main.py.
Soodles verification reference: e4b73508dacd149a31c05ba1168818031bff84dd.
Pstack create/maintain reference: ed3c/plugins@68836ddaf5697224520f1847d90cdb90ca8babaa.
Evals skills: ai-evals-course/evals-skills@80d5f7b0127c7572ed9e9339937adbfd7240ffeb.
The vendor lock binds original files and license. No upstream skill is claimed executed merely
because it was installed. Codex registration is repository-local, not user-global.

## Real article change

The old article had transaction_id -> rows and a success subtraction, but did not unpack
why duplicates remain visible or why classification precedes subtraction. Two source-grounded
insertions now connect list representation, row identity, duplicate/missing/currency priority
and the conditions for delta. They are an expansion of a retained article, not a fabricated
fresh Boot writer history. Removing both exact delta texts yields the original article.

Before SHA-256: c5e7b5ca7a02f5b8bc9b5b19d4ad58fe2e386be55b5051815d017c6c21d3fb82.
After SHA-256: 2fe1433a2e4f7ed4dfc83936617c22b915532ceeb29397773332c8564a55ad0f.
Added bytes: 3272. The same five delivery parts still concatenate to the final edition.
No original paragraph, code block, link or qualifier was removed by this expansion.

## Executable route

The helper freezes boot, sources and the ordered work queue. Each content-addressed patch
names the next unit and current article hash and only inserts at its declared heading.
Wrong order, stale input, changed retry, original-byte replacement and incomplete fences
refuse. Identical retry is NOOP. Every patch independently closes its own fences.

Pending units prevent finish. An empty queue still requests a current review. Finalization
uses the existing compiler via subprocesses and records boot/source/patch/review/final
bindings separately; it does not manufacture earlier authoring stages. DONE is scoped to
this queue. Source matching and author review do not prove arbitrary semantic preservation.

## Checks and evidence

The baseline workflow run 36245831032 executed 48 tests. The local candidate executed
76 tests before repository delivery. Four mechanical feature routes were driven with raw
argv/stdout/stderr/exit and artifact readback following scratch cleanup. The behavior route
is BLOCKED because no approved fresh writer/reader experiment has been run.

Four tests execute only the unmodified normalize/reconcile AST from the pinned source:
duplicate rows survive, a unique pair yields 2.00, duplicate precedes missing/currency precedes
amount, and ID case is preserved while currency is uppercased. These are extracted-function
controls, not HTTP, production, a provider call or a human financial review.

The first local negative test caught a partial delta borrowing a later closing fence. The
helper was fixed to validate each delta separately and the suite rerun. Controls prove
sensitivity, not naturally observed writer failures. Fresh CI results belong to their actual
checkout and must be read separately from this local record.

## Replay

```sh
python3 evidence/issue-8/replay.py --out /tmp/medium-replay-NEW
python3 -m unittest discover -s tests -v
python3 .agents/skills/verify-medium/scripts/verify.py --feature mechanical --out /tmp/medium-mechanical-NEW
python3 .agents/skills/verify-medium/scripts/verify.py --feature all --out /tmp/medium-all-NEW
```

The last command currently exits 3 with behavior BLOCKED. Preserve feature-results.json,
commands.json and lossless-run/final/ after cleanup. Author review is in review.json.

## Evidence ceiling and remaining acceptance

Strict pstack maintenance requires the independent source wave AND all applicable live
feature evidence. This task's coordinator-only source review does not satisfy that wave.
Fresh Codex selection, writer baseline/treatment, independent reader, calibrated semantic
judge and measured human decision-barrier reduction are NOT_RUN. Medium publication is
NOT_PERFORMED. The issue remains open for that behavioral closure, regardless of test counts.

## Flow-learning continuation on the same atom

The two accepted additions remain the same article edition. The updated plan binds both
units to one stable Ops case at `24a56d18661630b0dba97dcb0b057dce07b0ab32` and
labels their AI Engineer learning steps. Pinned snapshots now include actual Ops
`app/main.py`, `scripts/verify_runtime.py`, `evals/run.py` and the historical live-model
report. The latter records 4/4 fixed mapping cases at checkout
`78ea5882fa996cf9ef4c900bcc53cd79911b7a7a`; it does not test finding priority.
On the pinned Ops checkout, Python 3.12.4 ran 17 unit tests and the actual HTTP/restart
runtime verifier: 10/10 checks passed, including duplicate-key and cross-currency cases
and a planted wrong-amount control. The retained manifest and JUnit XML are in `inputs/`.
That runtime run used no live LLM; it is separate from the historical model report.

`next` exposes the current source-bound question, code/test/eval anchors and decision
prompt. The human checkpoint is DEFERRED until both patches are admitted, then PENDING.
No human answer is checked in. A future answer can be recorded once against the case
revision, final article digest and ordered unit IDs, with a content-addressed receipt;
its status is RECORDED_UNGRADED. DONE remains article compilation completion and reports
human learning NOT_MEASURED.

`flow-red-green.json` retains a planted baseline failure: the prior helper returned
CONTINUE without case identity or a deferred checkpoint; the candidate returns both.
The five new focused controls cover source/case anchors, stale answers, stable unit order,
receipt mutation and DONE versus learning status. This is mechanical sensitivity, not a
fresh Agent comparison or evidence of improved human judgment.
