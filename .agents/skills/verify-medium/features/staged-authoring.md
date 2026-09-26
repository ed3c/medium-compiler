# Write a new article in stages

## Sub-features

- Submit stages 0-6 in the declared order; no skipping or duplicate admission.
- Assemble accepted Stage 6 bytes and verify the current canonical artifact.
- Read next after validation; it must not invent further work.

## How to get to it (user POV)

From repository root, use medium_compiler.py init, next, submit, assemble, verify and check-receipt.
Python 3.10+ and a new run directory are required; no model credentials are needed for this drive.

## Driving it with verify-medium

Source: medium_compiler.py: init_run / submit_stage / next_action / assemble.

Run `python3 .agents/skills/verify-medium/scripts/verify.py --feature staged-authoring --out /tmp/medium-stages-NEW`.
The doctor checks the checkout, then the wrapper starts fresh short-lived CLI commands.
It attempts Stage 1 before Stage 0 (exit 2), then drives each legal stage, assembles and
verifies. Observe status VALIDATED and next=null. Inspect commands.json and staged-run/.
After scratch cleanup, the retained validation receipt must still exist.

## Gotchas

The staged input is a controlled fixture, not a fresh Agent run or the real article's
prior authorship. Declared claim IDs are not semantic proof. Full source/reader evaluation
is separate. Do not write runtime state by hand.
