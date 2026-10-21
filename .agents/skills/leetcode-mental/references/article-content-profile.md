# LeetCode complete-article content profile — source of truth

## Selection and ownership

Use this profile only when a LeetCode/coding-interview task asks for a **complete, publishable Medium article** (including staged parts and final assembly). Ordinary `leetcode-mental` v4 exercises retain the 14-block / Five-Anchor / Four-Pass / Oracle contract in [v4-contract.md](v4-contract.md). Selecting the article profile changes the *presentation*, not algorithmic correctness or the user's opted-in learning mode.

For this profile, **leetcode-mental is the sole semantic Content Owner**: it produces and approves the entire source-grounded English technical narrative and the full Traditional Chinese final draft, including examples, reference code, decisions, invariants, proof, runtime internals, alternatives, complexity, limits, figures and interview content. It owns approval of any changes suggested by sloptrim, translation or semantic review.

**medium-writing is the Medium formatter and assembler** for an already approved article edition. It owns Medium-native headings, readable code and figure placement, captions/alt text placement, contiguous delivery parts, and the existing CLI's legal Stage 0–7 admission/assembly. It may not invent facts, delete qualifications, paraphrase protected code, shorten the article as a summary, or editorially rewrite accepted content. A content defect goes back to leetcode-mental for a new approved edition; do not use Stage 7 as a repair step. For non-LeetCode routes, medium-writing's existing writer ownership is unchanged.

The `alg-four` annotation owner is downstream only: it reads the accepted article bytes and adds Passive/Active notes without rewriting the base article. Neither this profile nor the formatting stage creates a Four-Pass learner session, runtime mastery evidence, new CLI stage, or publication authority.

## Construct the reasoning, then check coverage

Use [the article construction method](article-construction.md) to derive the
reader's questions, prerequisite relations, worked states, correctness argument
and cost explanation from the current problem. Its final-body reconstruction
checks each method and conditional adaptation actually introduced, before
English approval and again where editing changes its premises. Supporting
passages must allow the cost inference to be rebuilt from explained premises
or explicit elementary cost assumptions; quotation presence is not completion.
It applies without a polished example. The following coverage list checks the resulting
article; it does not replace construction with a topic checklist.

## Required complete content, not fixed headings

From the *actual* problem statement and assumptions derive a connected, zero-context explanation. Preserve, where applicable:

1. Contract: task, input/output, constraints, success condition, tricky inputs and mutation permission.
2. Reader decision chain: decision question, competing methods, governing constraint/invariant, why the choice follows, and a falsifier. Number of decisions is source-derived, not fixed by a past problem or a five-question writing lens.
3. Meaning of representation: canonical key, state, ownership and identity when relevant. Distinguish task-equivalence properties from the checkpointed loop invariant used in correctness proof.
4. One discriminating input-to-output **Program Movie**: exact state before/after material operations, branches, mutation, data-structure or API boundaries, return. Explain a key runtime fact where its behavior changes a decision; do not produce a glossary as a substitute for causal transitions.
5. Complete, readable Python 3 solution consistent with the trace; initial state, operation order, invariant/proof (initialization, maintenance, termination where applicable), minimal counterexample to a real incorrect approach, one changed-constraint pivot.
6. Independently derived time and space complexity with variables, loops, allocations and assumptions, including output versus auxiliary space when relevant; avoid treating a mental trace as execution evidence.
7. A relevant alternative and its trade-off. Clearly name the constraint under which it becomes preferable.
8. Concise English interview Q&A *grounded in the approved technical claims*, plus a closing zero-context Master Map that only connects facts already established.

This is a **content coverage contract**, not eight mandatory section names. The number of sections is determined by the actual reader decisions and distinct runtime boundaries, not a default quota. Build a single causal narrative in natural paragraphs. Merge passages only when they perform the same teaching work, **without dropping examples, intermediate states, derivations, limitations, proof obligations or decision outcomes**. For the Medium edition do not force the ordinary v4 fourteen pedagogical blocks into fourteen article headings; Four-Pass exercise material remains on the separate selected teaching route.

## Reader prerequisites and explanatory steps

Fix the actual audience before choosing detail. A reader who knows basic Python syntax
does not thereby know hashability, a library factory, a data-structure operation or a
logarithmic cost derivation. Naming a mechanism, stating its result or linking to a
source does not explain it. Supply the missing steps where that reader would otherwise
have to obtain the answer from prior knowledge.

Separate **algorithm decisions** from **teaching steps**. One design choice can require
several explanations: what information an object represents, why the next operation is
valid, its input state, the operation itself, its returned value or mutation, and the
effect on the next operation. A small decision count does not justify compressing those
steps into one paragraph. Use prose and worked states as needed; neither a sentence per
operation nor a fixed section count is required.

When a complete reference is supplied, read its body and account for its material
explanations, examples and derivations before drafting. Correct technical mistakes while
preserving their teaching purpose. A previously unreadable external link is not a reason
to ignore a later user-supplied full text. A requested API or runtime mechanism remains
in scope if the author chooses an equivalent implementation; changing code cannot silently
remove the teaching requirement. Explain that mechanism and show how it relates to the
chosen solution, or resolve a real scope conflict with the user.

Keep purposeful recurrence. Explaining a mechanism, following it with concrete values,
mapping it to complete code, and recalling it in concise interview English have different
reader purposes even when they mention the same fact. Preserve the necessary bridge in
each context; remove verbatim repetition that does no additional teaching work. This does
not require every concept to appear a fixed number of times. A Master Map may compress
previously explained relations, but cannot supply an explanation missing from the body.

Before accepting an editorial deletion, test the result against this reader and the
requested source coverage. Can the reader derive the next state and explain why it
follows, using the remaining article alone? If not, restore or rewrite the bridge.
Preserving the conclusion, technical terms and code is insufficient. Keep this semantic
review outside copyable prose; the detector, heading count, paragraph count and digest
cannot certify it.

## Language, editorial review and evidence

1. Produce the **entire English technical content** for the declared scope before formatting or translating. A source-bound incremental unit is allowed only if its place in the complete plan and pending coverage is recorded; a Boot Batch is not a completed article.
2. Apply the installed upstream `sloptrim` and its reader-article supplement to the English content **before translating**, when this execution host can actually run it. The Content Owner reviews every proposed change against technical claims, negation, conditions, versions, examples and code; `clean` is a style diagnostic, not semantic acceptance. If execution is unavailable, mark `NOT_RUN` and do not claim success.
3. Approve English content on semantic grounds. Translate that approved complete text to natural **Traditional Chinese with exact English technical terms** (and unchanged identifiers, source links, code, quantities and qualifications). Have the Content Owner check decision-bearing and exception-bearing English/zh-TW passages against the same pinned sources. Distinguish author's check from independent reader review.
4. Approve a **single complete Traditional Chinese content edition** before the formatter partitions or admits it. Do not let each delivery part become a different writer's or earlier draft's edition.
5. Preserve source locators, counterexamples, unknowns and evidence status. Source descriptions, algorithm traces, actually executed tests, learner achievement, CLI receipts and Medium publication are different kinds of evidence.

## Figure and article handoff

Figures are derived from material reader questions and runtime boundaries, not a universal count. For each necessary figure preserve: its unique conceptual purpose, supported nodes/edges and state values, exact article insertion anchor, caption and alt text in the approved language, and a self-contained rendering brief. Label illustrative complexity diagrams as conceptual rather than exact runtime traces. Explain every nontrivial diagram edge in the article or point to its explicit section. Avoid compressed vocabulary clouds or one poster containing all internals.

A cover is optional; figure image generation is **not** mandatory. Generate image assets only when the user requests them. When requested, produce individually usable figures in the requested count/order and review each for source-fidelity, legibility and correct terms; do not pretend a collage is multiple ready-to-insert files.

Handoff to medium-writing contains the approved full English and zh-TW narratives, source/claim coverage and unresolved limits, complete reference code, ordered section plan, figure positions/captions/alt text/briefs, and the actual editorial/execution evidence status. This is a semantic handoff description **using existing article/coverage/CLI inputs**, not a new persistent schema, state machine or invented hash/digest. Deterministic byte IDs come only from the original CLI/producer.

## Website-ready handoff when website delivery is selected

Supply both complete approved Markdown editions and the article-list data in
[the existing bilingual website contract](../../../../docs/bilingual-articles.md):
one stable slug, each language's title and short source-faithful description,
and the exact repository source paths. Titles must match their edition's H1;
do not put registry metadata, review notes or generated HTML into the prose.
The Content Owner approves both descriptions as well as the unchanged bodies.
An already approved edition can be handed off without reauthoring it; retain
its original draft, review and failure evidence separately.

Use the site's explicit article registry. Do not publish by scanning evaluation
directories or treating every generated draft as an accepted article.
The formatter/build owner preserves the supplied Markdown, renders separate
language routes and their own heading contents, and connects the article list,
language links and source downloads. Missing titles, descriptions or a complete
language edition return to the Content Owner; a build or navigation defect
belongs to the site builder. Do not shorten prose to make a page fit.

Verify the built article list and both complete pages through real desktop and
mobile navigation, heading links, language switching and source downloads.
Compare downloaded bytes and rendered code with the supplied editions.
When the selected site includes ALG Four reading support, hand both approved
editions to `speed-reading` for annotation content and the existing `alg-four`
integration for source binding, admission validation and navigation. Include its source-bound
per-paragraph notes in the website handoff, not just heading links. The site
builder validates the paired editions, original Git blobs and full annotation
coverage before rendering; it must refuse missing or stale notes. Active items
require paragraph evidence and a faithful production sentence/cue/oracle, without
per-article quotas. Plain English is the fallback when pronunciation or chunk
annotation has not been verified. Keep annotations outside the complete body.

Keep content/reader evidence, website runtime, compiler admission and Provider
publication distinct. Website-ready files and a successful CI do not authorize
merge or deployment; preserve the task's selected host and explicit effect scope.

## Part delivery and Stage boundary

The existing medium-compiler **Stage 0–7 remains unchanged**. Leetcode-mental supplies content needed for those stages; medium-writing sends it through the actual legal CLI steps and preserves source/code semantics. Stage 6 for this profile is a format-preserving pass over already approved wording (not a second editorial author); Stage 7 copies admitted bytes. Existing-article revisions follow the CLI's supported `init --draft` or authorized technical correction route; do not fabricate historical stages.

`Part 1..Part N` are **contiguous slices of one approved edition**, not new versions of authoring Stages 1..N. Use actual manifest/CLI output to pin order and exact bytes; place title only in Part 1, preserve complete code fences, number headings consistently, never duplicate sections or continuation narration within pasteable prose. If deduplication requires changing approved content, return to leetcode-mental and reapprove **before** Stage 7.

The assembled Medium result must contain the complete approved article once, with figure slots at the agreed positions, and no private sidecars, audit IDs, placeholders not intentionally marked as figure slots, or "continue?" chatter. Medium formatting does not prove semantic correctness, actual rendering, publication or learner comprehension.

## Minimal acceptance and stopping rule

Before handoff, check that an unfamiliar reader can reconstruct: goal and constraints; each material decision; why the representation works; an actual input-to-output trace; relevant language/runtime mechanism; alternative and failure case; cost derivation; full code/proof; what is a mental demonstration versus a test. Use another problem with different constraints in focused regression/evals to ensure no solution-specific fixed alphabet, key, Big O, section count or figure count leaks into the general profile.

Acceptance claims must separate `CONTENT_REVIEWED`, `SLOPTRIM_RUN/NOT_RUN`, `TRANSLATION_REVIEWED`, `CLI_VALIDATED`, `RUNTIME_TESTED/NOT_RUN`, `INDEPENDENT_READER/NOT_RUN`, `IMAGES_RENDERED/NOT_RUN` and `PUBLISHED/NOT_RUN`. These are reporting labels, **not** new CLI statuses.

Stop cognitive recursion once no new source-grounded, falsifiable issue could change scope, owner, behavior or verification. Do not re-run thinking methods as ceremony.

For speed-reading-authored notes, the complete annotation is the acceptance unit:
show source-bound premises and any state/order checkpoint before the short
reading cue (閱讀提示，非獨立結論). A source citation alone does not explain why
its premise matters. Follow the speed-reading Owner contract; the UI/validator
checks presence and exact bindings, while Owner/Reader review completeness.
