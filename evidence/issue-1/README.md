# Issue #1: actual article revision and revalidated final bytes

## What was necessary

One real before/after article, one bounded prose instruction, protected technical
material, and one re-read final-byte receipt. Existing authoring stages remain for
new topics. Existing articles now import directly into Stage 6; no fictional
Stage 0-5 history is needed. No card graph, publishing adapter, scheduler or new
model pipeline was added.

## Observed defect and controlled correction

Baseline CLI: `3876cbbf1cff627647e2c3c6c13ffda80fa8c1c0`, blob
`dd968bdd6afc75311affe6d28b3ae068f94db1b8`.

The old `verify` compared canonical bytes to the editable Stage 6 file, then wrote
literal `true` values for the checks. After both copies' code was changed it still
issued a fresh valid receipt. The same planted fixture and mutation now exit 2,
leaving the earlier receipt untouched. This is a deterministic false-acceptance
correction, not evidence of a naturally occurring model failure.

Actual CLI results:

| Drive | Baseline | Candidate |
| --- | --- | --- |
| Valid staged fixture | exit 0 | exit 0 |
| Modify admitted Stage 6 and canonical code; run verify again | exit 0, false acceptance | exit 2, refusal |
| Real article import -> copyedit -> assembly -> verify -> prove-update | unsupported import entry | exit 0, VALID |
| Mutate actual article code after admission | not the paired fixture | exit 2, refusal |

## Real product evidence

Article: `articles/ai-engineer-learning-path.md`.

The retained [before.md](before.md) is the exact article at the baseline commit:
Git blob `aed314c86ef9bf6af33af95a9f193b86be9b9f79`.
The updated article blob is `4e57eef57fa5d84f8dbc58790947bcef067eb463`.

Four prose spans changed. `edit-review.json` records every before/after pair. The
replay reconstructs the after article from exactly those changes and rejects any
other textual change. All 10 fenced blocks and the ordered numeric tokens remain
identical. The CLI also checks inline code, link destinations and specified literals.
The four-span semantic review was performed by the authoring assistant, not by an
independent reader; no human-preference or universal-style claim is made.

Files:

- `execution.json`: executed result and explicit evidence ceilings.
- `run/`: retained actual article run; check-receipt can reread it without a model.
- `article-update.json`: actual prove-update output.
- `tests.txt`: actual 32-test output; the original 17 also passed before this patch.
- `edit-review.json`: the scoped author review, separate from CLI correctness.
- `replay.py`: actual command driver, rebuilding full stdout/stderr logs in a new directory.

The earlier `article-update.candidate.json` remains historical. Its NOT_RUN statuses
are not current execution results, and its earlier 35-line manual edit is not the
paired verifier experiment reported here.

## Reproduce

```sh
python3 -m unittest discover -s tests -v
python3 medium_compiler.py check-receipt --run-dir evidence/issue-1/run
python3 evidence/issue-1/replay.py --out /tmp/article-replay-new
```

For the old/new verifier control:

```sh
git show 3876cbbf1cff627647e2c3c6c13ffda80fa8c1c0:medium_compiler.py > /tmp/medium-old.py
python3 evidence/issue-1/replay.py --out /tmp/article-replay-paired --baseline-cli /tmp/medium-old.py
```

Both extracted baseline Python files used for the original run were checked against
the provider Git blob identities before execution. The environment was this task's
Linux/Python container, not the user's macOS machine or GitHub Actions. Network clone
was unavailable; source text was retrieved through the GitHub connector and its exact
Git blob identity verified locally before testing.

## Result boundary

- Scoped deterministic correction: demonstrated.
- Real article revision and matching final receipt: demonstrated.
- Four-span author review: performed, not independent.
- Fresh writer A/B and held-out different-topic style: NOT_RUN.
- Independent zero-context reader: NOT_RUN.
- Medium publication or editor rendering verification: NOT_PERFORMED.

The style lint reports 0 before and 0 after. This is explicitly not a measured style
improvement. The article revision is justified by the four concrete edit rationales.
GitHub merge/closure is a separate provider action; this directory does not authorize it.
