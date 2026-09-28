---
name: verify-medium
description: Verify medium-compiler through actual CLI and article-delivery paths. Use after changes to writing skills, batch continuation, source-link handling or assembly, before proposing a PR.
---

# Verify Medium writing

Read [features/README.md](features/README.md) and the matching feature recipe. Full-map
requests cover every row. Source creation standard: [create-verification.md](references/create-verification.md);
upkeep standard: [maintain-verification.md](references/maintain-verification.md). Their
.cursor placement is adapted to .agents; neither file is a new correctness authority.

## Launch

From repository root, use Python 3.10+ (standard library). There is no server, no provider
key and no publishing login. Every drive starts a short-lived CLI in its own new scratch
run. The wrapper waits for each process, records its exit and then ends it; no shared session.

`python3 .agents/skills/verify-medium/scripts/verify.py --feature doctor --out /tmp/medium-doctor-NEW`

Ready means the recorded Python/CLI help and registered-skill/source checks pass. Do not
create a second driver on the same run directory. Outputs must be new and outside the checkout.

## Doctor

Use the doctor command above first and after surprising behavior. It is read-only to the
checkout. It checks source presence, the actual CLI help, unique registered skill names,
vendored file hashes and the current article. It does not probe Codex, credentials or
ChatGPT tool exposure. Cloud native capabilities belong to the current Host Session;
an explicitly selected local run has its own separate runner doctor.

## Drive

`python3 .agents/skills/verify-medium/scripts/verify.py --feature all --out /tmp/medium-verify-NEW`

Or select staged-authoring, bounded-revision, lossless-drilldown, delivery, behavior-evals.
The wrapper executes CLI commands rather than setting runtime state. The lossless recipe
uses the actual AI Engineer article. The staged smoke input is explicitly a fixture,
not fictional prior authorship of the real article. All mode runs the five default recipes;
a BLOCKED behavior row makes the overall outcome partial, not a full verification PASS.

For a course article, also run the explicit selected-article drive:
`python3 .agents/skills/verify-medium/scripts/verify.py --feature learning-article --article articles/git-collaboration.md --out /tmp/medium-git-NEW`.
Replace --article with the current lesson; its adjacent .context.json must bind the current
article hash. This opt-in no-change recompile is not included in all/mechanical and does not
assess source meaning or learner understanding. Read features/learning-article.md.

## Evidence

Keep commands.json, feature-results.json and article/run outputs in --out. Each command
has argv, stdout, stderr, exit and feature ID. Keep both valid and refusal paths. Live
CLI proof is distinct from a unit test, author semantic review, a fresh writer A/B and
an isolated reader. No fake provider or scripted cursor transition is a natural Agent run.

## Cleanup

Each drive owns a temporary scratch directory; cleanup removes only that directory after
copying the needed run/article evidence to --out. Subprocesses are waited for with timeouts.
Never kill by process name, delete user runs, or delete --out. Check proof files still exist
following cleanup. Failed drives preserve their action logs and are reported, not averaged away.

## Helpers

The executable helper is scripts/verify.py in this skill. All invocation forms are above.
For product commands, use `python3 medium_compiler.py --help` and
`python3 scripts/lossless_batch.py --help`; do not infer commands from old issue titles.
The helper reports source hashes, not a fabricated parallel source-review wave.
