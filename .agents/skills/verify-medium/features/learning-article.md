# Verify the selected learning article without changing it

## Sub-features

- Bind the selected Markdown bytes to its adjacent context's assembly.article_sha256.
- Drive a no-change Stage 6–7 recompile and verify the retained compiler receipt.
- Refuse missing/stale context; keep semantic and human-learning claims unassessed.

## How to get to it (user POV)

Use this after assembling a course article and updating its context from the real receipt.
The Ops mechanical examples do not verify another article's identity.

## Driving it with verify-medium

Source: scripts/verify.py: Driver.learning_article; medium_compiler.py revision/receipt path.

`python3 .agents/skills/verify-medium/scripts/verify.py --feature learning-article --article articles/git-collaboration.md --out /tmp/medium-git-NEW`

Replace --article with the current lesson. Relative paths resolve from repository root;
absolute paths permit controls on external copies. The adjacent .context.json must contain
assembly.article_sha256 as 64 lowercase hex digits. The driver snapshots both inputs, checks
their identity, imports the unchanged article at Stage 6 and rechecks the copied run after
scratch cleanup. It refuses concurrent input drift. Keep input-identity.json, input.md,
input.context.json, article-run/, commands.json and feature-results.json under the new --out.

For a refusal control, copy the real article/context outside the checkout and alter the
article or its context hash. Run the same command on that copy; require exit 2 and inspect
the error. Never mutate the actual article to drive a negative control.

## Gotchas

This opt-in drive requires an explicit article; all/mechanical retain their original scope.
The context hash is a consistency declaration, not trusted semantic approval. Changing both
inputs consistently cannot be detected as loss of meaning. PASS proves only current input
identity and no-change compilation; it does not validate original authorship, source claims,
decision completeness, runtime diagrams, publication, learner mastery or a learning handoff.
