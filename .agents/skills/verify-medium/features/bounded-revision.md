# Revise an existing article without changing protected material

## Sub-features

- Import a real article directly at Stage 6, without invented earlier authoring.
- Refuse a protected-content edit; accept a scoped prose edit.
- Bind a same-article proof and refuse a stale canonical file after validation.

## How to get to it (user POV)

Use medium_compiler.py init --draft, next, submit --stage 6, assemble, verify and prove-update.
Work on an isolated copy of evidence/issue-8/before.md. Never drive another actor's run.

## Driving it with verify-medium

Source: medium_compiler.py: _validate_copyedit / _stage6_source_link / prove_article_update.

Run `python3 .agents/skills/verify-medium/scripts/verify.py --feature bounded-revision --out /tmp/medium-revision-NEW`.
After doctor, the wrapper attempts a protected number change inside a fenced block and
requires exit 2. It submits a one-phrase prose replacement, assembles, verifies and records
prove-update. It then mutates only the scratch final file and requires stale-receipt refusal.
The unmodified retained run is re-read after scratch cleanup. Keep commands.json,
revision-run/ and revision-proof.json.

## Gotchas

The one-phrase edit is a route control, not this Issue's shipped expansion. The explicit
single-link source_correction route is not a general semantic rewrite; its separate tests
remain in the suite. Current CLI help, not an old Issue title, defines available commands.
