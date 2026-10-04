# medium-compiler

A writing-only CLI and repository-local Codex skills for zero-context technical Medium
articles. The running article uses Ops Reconciliation Copilot, source-backed explanations,
text runtime maps and exact final delivery. No model adapter, publisher, card database,
scheduler or image-generation pipeline is added.

## Delivery scope

Issue #8 / PR #9 deliver the registered writing skills, mechanically verified lossless
continuation and the source-bound article. Issue #10 / PR #11 deliver the static learning
site. Acceptance requires the exact-head test suite and four mechanical drives, preserved
article/source identities, and (for the site) build plus deployed route/provenance readback.

The owner separated writer A/B, independent reader/semantic assessment, the real accepted
learning-episode positive path and measured human benefit into [Issue #12](https://github.com/ed3c/medium-compiler/issues/12).
These are research follow-ups, not prerequisites for this scoped product delivery. No
behavior improvement, full-map behavior PASS or completed learning is claimed. Existing
runtime prerequisite checks and all tests stay enabled; explicit learning-episode tasks
still require a genuine accepted upstream handoff. The behavior verifier continues to
report BLOCKED / NOT_RUN and all mode remains partial until that separate evidence exists.

## Choose the execution host before the writing task

ChatGPT cloud repository work uses GitHub and the existing writing-verification Actions.
Independent cloud writers/readers use the exposed native subagent tool: see the
[cloud-native recipe](evals/writing/ops-evidence-handoff/cloud-native.md). No Codex install,
API key, browser login or Local Codex host approval is required for that native route.
The repository cannot create a native tool or install ChatGPT Project instructions.

The [Codex runner](evals/writing/ops-evidence-handoff/README.md) is retained for explicitly
selected local work only. Its frozen inputs and evidence are not native-cloud runs.
The earlier GitHub-hosted Codex probe is historical, superseded routing evidence under
[evidence/issue-8/cloud](evidence/issue-8/cloud/README.md), not a native prerequisite.
The erroneous cloud CLI workflow/probe were removed; the original writing CI is unchanged.

## Entry points

- [Canonical registered writer](.agents/skills/medium-writing/SKILL.md)
- [Retained complete writing contract](writing-contract.md)
- [Planning/continuation prompts](prompts/medium-article.md)
- [Boot-to-drill-down task prompt](prompts/drill-down.md)
- [Verification and feature map](.agents/skills/verify-medium/SKILL.md)
- [Full-map maintenance](.agents/skills/maintain-medium-verification/SKILL.md)
- [AI Engineering course article workflow and verification](.agents/skills/verify-learning-article/SKILL.md)
- [Behavior and reader evals](.agents/skills/medium-behavior-evals/SKILL.md)

Codex repository skills live under .agents/skills/<name>/SKILL.md. Root SKILL.md is a
compatibility pointer, not a second registered writer. The prior root writing contract is
preserved verbatim in writing-contract.md and explicitly loaded by the registered entrypoint.
No user-global directory is modified. File registration is checked; actual Codex selection
must still be verified in the user's Codex session. See [OpenAI's repository-skills example](https://developers.openai.com/zh-Hant/blog/skills-agents-sdk).

## Current article

[Continuous Medium article](articles/ai-engineer-learning-path.md),
[reading plan](articles/ai-engineer-learning-path.stage-00.md),
[context](articles/ai-engineer-learning-path.context.json), and
[five delivery parts](articles/ai-engineer-learning-path.parts/manifest.json).
The ten reader decisions are this article's grouping, not a quota. The latest expansion
explains why transaction IDs map to lists and why finding classification precedes subtraction.
Its two runtime insertions and later learning-owner explanation are separately recorded; removing the three declared additions reconstructs the original article exactly.

## Writing routes

New articles use the existing CLI: Stage 0 contents/maps; Stage 1 problem/property/representation;
Stage 2 witness/internals; Stage 3 alternative/cost; Stage 4 implementation/correctness;
Stage 5 interview/master map; Stage 6 prose pass; Stage 7 exact assembly.

```sh
python3 medium_compiler.py init --spec examples/spec.json --run-dir /tmp/new-article
python3 medium_compiler.py next --run-dir /tmp/new-article
```

`submit --stage N --input part.md --coverage coverage.json` admits the current stage.
For prose-only revisions, use `init --draft before.md`; no fictional authoring stages.
Then submit 6, assemble, verify, check-receipt and prove-update as required. The existing
single-link source_correction route is not arbitrary technical rewriting. Read actual
CLI help rather than assuming an old proposed reopen command exists.

## Learning handoff before article Boot

The user/task selects `purpose: source-explanation` (the legacy default) or
`purpose: learning-episode`. Source explanations may be written independently; an unfinished
learning task must not be relabeled to bypass its prerequisites.

```sh
python3 scripts/lossless_batch.py preflight --article before.md --plan plan.json
# READY / exit 0: boot is permitted. BLOCKED / exit 3: return next.owner + missing_input.
# boot enforces the same gate before making its output directory.
```

A learning plan adds `learning: {episode_id, lesson_ref, handoff_source}`. The last field names
one existing pinned source containing JSON with `schema_version: medium-learning-handoff@1`,
matching `episode_id`, `lesson_ref` and `case`; `status: PENDING | ACCEPTED`;
`product_decision: PENDING | IMPLEMENT | NO_CHANGE`; `evidence_refs` (list);
`human_checkpoint` and `learning_record` (reference or null). Every reference is
`{source_id, anchor}` into a separate source snapshot in the existing plan. The upstream
learning owner supplies acceptance and the progress-record reference; the writer does not.
Product code/test/eval sources stay bound to the case revision. Learning and human records
retain their own provenance rather than pretending to be Ops source files.

Missing product decision -> product-owner; missing evidence -> evidence-owner; missing
human checkpoint -> learner; missing acceptance/progress record -> learning-owner.
No handoff at all -> learning-owner. NO_CHANGE is not completed learning. Malformed identities,
references or stale bytes refuse; genuine missing prerequisites are BLOCKED. The admitted
source snapshots survive restarts and are covered by the existing batch/final byte checks.
This is a single-writer snapshot protocol, not an authenticity, revocation or grading service.

The post-article `checkpoint` records reader comprehension only, not curriculum advancement.
No command writes LEARNING.md, selects a phase or fabricates a response. A successful ready-path
fixture is not evidence of an actual accepted learner. See
[evidence and replay](evidence/issue-8/handoff/README.md) for the actual missing-handoff
refusal and the separate, explicit source-explanation update to the same article.

## Boot Batch and incremental continuation

An overview is not completion while source-bound knowledge units remain. The add-only helper
owns source snapshots, a fixed work queue and an ordered patch journal. P-class chooses what
the reader needs explained and writes the content. A source-anchor or term match does not
prove semantic fidelity.

```sh
python3 scripts/lossless_batch.py boot --article evidence/issue-8/before.md --plan evidence/issue-8/plan.json --run-dir /tmp/medium-expand
python3 scripts/lossless_batch.py next --run-dir /tmp/medium-expand
python3 scripts/lossless_batch.py drill-down --run-dir /tmp/medium-expand --patch evidence/issue-8/patch-01.json
python3 scripts/lossless_batch.py next --run-dir /tmp/medium-expand
python3 scripts/lossless_batch.py drill-down --run-dir /tmp/medium-expand --patch evidence/issue-8/patch-02.json
python3 scripts/lossless_batch.py render --run-dir /tmp/medium-expand --output /tmp/medium-expanded.md
python3 scripts/lossless_batch.py finish --run-dir /tmp/medium-expand --review evidence/issue-8/review.json
```

Every patch names the next unit and current article hash and inserts only at its declared
heading. Identical retry is NOOP; stale/out-of-order/conflicting edits refuse. Each patch
closes its own fences. Empty queue still returns CONTINUE for review. Finish uses the
existing compiler to finalize the expanded draft and records a separate boot-to-final proof.
DONE covers the declared queue and current recorded review, not universal source completeness
or measured human understanding. New gaps or changed scope require a new explicit plan;
never edit admitted state to erase pending work.

The Ops plan also binds a stable case ID and public source commit. `next` gives the current
AI Engineer learning step, one decision prompt and exact code/test/eval anchors. The human
checkpoint stays deferred until all patches are delivered. Afterward, `next` exposes both
prompts together; an actual reader can submit a JSON response with `case`, the current
`article_sha256`, and ordered `answers` (`unit_id`, `answer`):

```sh
python3 scripts/lossless_batch.py checkpoint --run-dir /tmp/medium-expand --response /tmp/reader-answers.json
```

The checkpoint receipt is `RECORDED_UNGRADED`. No answer has been submitted for the checked-in
evidence. The historical Ops model eval is source evidence for a narrow smoke result; it does
not validate reconciliation priority or prove that a reader has learned it.

`python3 evidence/issue-8/replay.py --out /tmp/medium-replay-NEW` replays the exact real article
without changing the checkout. Its optional --update-article is an explicit developer action
limited to the known before/after edition and dependent article/evidence/parts files.

## Verification

Python 3.10+ and the standard library are sufficient. Use new directories outside the checkout.

```sh
python3 -m unittest discover -s tests -v
python3 .agents/skills/verify-medium/scripts/verify.py --feature mechanical --out /tmp/medium-mechanical-NEW
python3 .agents/skills/verify-medium/scripts/verify.py --feature all --out /tmp/medium-all-NEW
```

Four mechanical features are actually driven. All mode additionally checks behavior readiness;
missing an approved isolated writer/reader experiment returns BLOCKED and exit 3. Full pstack
maintenance also requires an independent source-review wave per feature. Coordinator review
plus scripted drives must not be called that full pass. Evidence survives owned-scratch cleanup.

## Pinned methods and limits

Nine original evals-skills workflows are registered with their license and
[content lock](references/upstream/skills-lock.json). The real entrypoint is evals-start.
Load only the needed audit/discovery/code-eval/judge/validation method. Other upstream routes
are retained so their references resolve; installing them does not execute providers or create
human labels. The [v7.1 adapter](references/card-context-v7.1.md) preserves evidence-first
processing, task-value-first prose, uncertainty and incremental identity. No cards are invented.

[Issue #8 evidence](evidence/issue-8/README.md) separates mechanical proof, author review,
fresh writer A/B, independent readers and publication. The helper assumes one cooperative
writer, not hostile state mutation, simultaneous writers or power-loss recovery. No command
merges a PR, closes an issue, publishes Medium content or changes Ops production.


## AI Engineer learning site (Issue #10)

A separate stacked slice builds a public learning website from source-owned state:

```text
AI Engineering from Scratch skills
        ↓
LEARNING.md (when placement exists)
        ↓
Ops experiment catalog / evidence
        ↓
medium-compiler article
        ↓
static site
```

Core upstream tutor skills are vendored project-locally at exact upstream Git blobs and pinned
in `references/upstream/ai-engineering-skills-lock.json`. No placement is fabricated: until
`start-learning` creates `LEARNING.md`, the site shows `NOT_INITIALIZED`.

Ops implementation remains in `ed3c/ops-reconciliation-copilot`; this repo consumes only a
pinned experiment snapshot for cards and explanation. Run `python3 scripts/build_site.py` to
generate `dist/`. `vercel.json` is preview-ready.

The [Four-Pass technical lesson](https://medium-compiler.vercel.app/cefr-alg-c2/technical?lesson=software-factory-sole-acceptance)
can play a video from your device: choose **Choose local video**, select a video, then use
the existing player controls. The browser reads the selected file without uploading it.
It cannot read an arbitrary local path; reload requires selecting the file again.
**Restore supplied video** restores the supplied video and captions. Local playback disables
those captions because they describe the supplied narration. Lesson hashes and practice
receipts still refer to the supplied lesson; the selected file is not checked against it.
For the entire site to run locally, serve its build through localhost; opening its HTML
with `file://` does not support the site's existing module and lesson-data loading.

## Course article progression

Use [verify-learning-article](.agents/skills/verify-learning-article/SKILL.md) for the
lesson-to-article-to-site workflow demonstrated by the development-environment article.
Its three feature recipes cover original lesson requirements and real practice, existing
medium-compiler writing routes, and deployed article/navigation readback. It also adapts
the retained pstack maintenance procedure to this one skill; full-map maintenance needs
both independent source review and actual drives. It does not create learner acceptance,
require Colab for every lesson, or authorize publishing by itself.

Course articles follow the pinned Software Engineering Fundamentals route in
`references/upstream/software-engineering-fundamentals.json`, not numeric folder order.
Each course entry in `scripts/build_site.py` declares its exact `lesson`, `lesson_title`
and `next_lesson_title`. The builder renders previous/next navigation inside the article;
a published next article takes precedence, otherwise it links the original next lesson
and explicitly states that the local article is not yet published.

Before adding an article, read the original lesson and relevant implementation, execute
its practical exercises, inspect failures and state transitions, then explain valuable
operational questions with answers and evidence. Keep original requirements distinct
from supplemental experiments. Do not make publication wait on invented learner questions
or record agent execution as learner mastery. Preserve actual commands and results,
source refs, and any incomplete requirement. Add the article to navigation and verify
its build, links, provenance and deployed page.
