# Issue #3: pre-assembly semantic reopen

Status: implementation and deterministic controls complete; **issue closure is NOT_ELIGIBLE**.
This is a combined P-class + CLI candidate, not a measured P-class improvement.

## Exact scope

Baseline: `6b9b24f35c8f3271ff04673efad337db2e60371f` (main after PR #2).
The old admission/receipt weakness was already repaired there. This change adds only
`reopen --stage 1..5`, its current-state projection in `next`, a narrow Skill rule,
focused tests and these evidence files. No hooks, models, publisher or second engine.

A staged run frozen at Stage 6 or waiting for Stage 7 may reopen its semantic suffix.
The writer selects the earliest affected stage. The CLI validates the current run,
preserves the prefix, invalidates the suffix, rebuilds accounting and returns `next`.
The refreshed Stage 6 still protects code, inline literals and links.

## Executed evidence

| Check | Result |
|---|---|
| Original unit suite at pinned baseline | 32 tests PASS |
| Candidate suite | 52 tests PASS, including 20 reopen tests |
| Scripted Stage 1 correction | baseline missing operation (exit 2); candidate VALIDATED |
| Scripted Stage 4 correction | baseline missing operation (exit 2); candidate VALIDATED |
| Scripted prose-only edit | baseline and candidate VALIDATED without reopen |
| Fresh natural Agent A/B | NOT_RUN |
| Real article update via this reopen path | NOT_PERFORMED |
| Independent semantic review / Medium publication | NOT_RUN / NOT_PERFORMED |

Execution was in this task's Linux/Python container using source fetched from GitHub
and checked against the original Git blob identities. It was not GitHub Actions,
the user's Mac, or a fresh Agent session. `tests.txt` is the actual 52-test output;
`baseline-tests.txt` is the original 32-test output. `execution.json` binds the tested
source and raw output bytes. The accompanying task archive
`medium-compiler-issue-3-evidence.zip` contains the unabridged `replay/result.json`
with all 81 subprocess records, both reopen outputs and observation digests.
The repository keeps this summary and the replay script; the script regenerates
the full traces into a fresh directory.

The refusal controls cover invalid targets, unfrozen/imported/assembled runs,
changed or missing admissions, false rebound coverage, symlinks and unexpected
final artifacts. Injected rename/state-commit errors restored the original bytes.
No power-loss recovery or concurrent-writer guarantee is claimed.

## Remaining closure gates

The current real article `articles/ai-engineer-learning-path.md` is unchanged.
Its retained run at the pinned baseline is `mode=revision`, `status=ASSEMBLED`,
`submitted_stages=[6]`; state Git blob `2a63f13064daa3b3f2e5b9fce5162763455e4c10`.
It has no admitted semantic stages to reopen. Reconstructing fictional Stages 1-5
would violate the current Skill, so it was not used as this atom's product proof.
This observation does not assert that no genuine article defect exists.

Keep #3 open and the PR draft until a genuine staged article correction traverses
reopen -> next -> suffix submission -> copyedit -> assembly -> verification, with
same-article before/after/canonical bindings, AND fresh isolated Agent baseline /
treatment traces establish the stated routing behavior. A scripted missing command
is not a nonzero natural-behavior baseline. Zero-to-zero natural runs would support
only scoped nonregression, not hill-climb improvement. Do not average away a wrong
route. Never manufacture an article error or authoring history to fill these gates.

## Replay

From a checkout containing the pinned baseline and this candidate:

```sh
git show 6b9b24f35c8f3271ff04673efad337db2e60371f:medium_compiler.py > /tmp/medium-before-reopen.py
python3 -m unittest discover -s tests -v
python3 evidence/issue-3/replay.py --baseline-cli /tmp/medium-before-reopen.py --out /tmp/medium-reopen-new
```

The replay refuses an existing output directory and writes only to its fresh output.
It uses controlled synthetic inputs, never a model or network. Its results prove
an available legal continuation and retained guards, not author preference, semantic
truth, natural tool choice, or publication. `semantic_correctness` remains NOT_ASSESSED.
Historical #1 receipts bind their original compiler bytes and remain untouched.
