# Issue #8: fresh-writer runner and external observer

This continuation implements the approved pending-handoff experiment mechanism. It does not
claim a natural writer result or close Issue #8. The product problem is distinguishing a
writer's wrong attempted next action from a guard that successfully prevented its effect.

## Minimal implementation

- scripts/run_writer_pair.py prepares exact allowlisted inputs and records a separately
  qualified Codex exec pilot / six interleaved fresh runs. No model installation or credential
  copying. A real external host owner must establish read isolation and protected recording;
  workspace-only writes and JSONL are not themselves an isolation proof.
- scripts/evaluate_writer_run.py checks capture validity before accepting externally reviewed
  event judgments. Missing, changed, truncated, duplicate or unreviewed runs never become zero
  errors. Rejected attempts and final-file effects are reported separately.
- evals/writing/ops-evidence-handoff fixes actual pending Ops PR24 state and matching inputs
  for baseline71 / treatmentdf. It never invents an accepted learning record. The positive
  accepted path is deliberately unsupported until actual owner evidence and a compatible
  input packet are selected.

The tested fake Codex executable and synthetic reviewer records are UNIT TEST CONTROLS ONLY.
They test transport/observer behavior, not model judgment or independent human performance.

## Actual article delta

The same AI Engineer article gains one 1,705-byte source-explanation insertion before section
7. It explains wrong attempts versus prevented effects and why incomplete observations are
not zero errors. The scenario is explicitly hypothetical; no pending Ops candidate is consumed
as completed learning evidence. Removing this insertion reproduces the entire df138896 article.
Existing source links and prose remain unchanged; five parts reconstruct exactly the final
article. Author review is recorded, not misrepresented as independent reader review.

## Executed local evidence

Baseline: 102 tests PASS. Candidate: 131 tests PASS, including 29 runner/observer controls.
The four mapped mechanical feature routes pass. The actual packet prepares and validates all
selected files; doctor returns BLOCKED because Codex is absent, with model_calls=0. The existing
behavior feature correctly remains BLOCKED. No host qualification/pilot/fresh writer/reader
experiment was performed. No lesson progress, Ops runtime, global skill, publishing, original
article compiler, lossless helper or GitHub workflow was changed.

validation.json retains source and result hashes. Raw test/process logs and failed preliminary
attempts are retained in the delivered evidence archive. CI on the committed tree will run the
mechanical suite; a green CI result still cannot supply missing natural writer evidence.

## Reproduce

```sh
python3 -m unittest discover -s tests -v
python3 scripts/run_writer_pair.py doctor
python3 evidence/issue-8/writer-pair/replay.py --out /tmp/writer-article-NEW
python3 .agents/skills/verify-medium/scripts/verify.py --feature mechanical --out /tmp/writer-mechanical-NEW
```

Use the experiment README for exact-checkout preparation and external host/pilot/review steps.
Do not populate the host approval or an ACCEPTED learning record on another owner's behalf.
Do not merge or close #8 on mechanism-only evidence.
