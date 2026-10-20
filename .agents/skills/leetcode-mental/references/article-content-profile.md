# LeetCode complete-article content profile — source of truth

## Selection and ownership

Use this profile only when a LeetCode/coding-interview task asks for a **complete, publishable Medium article** (including staged parts and final assembly). Ordinary `leetcode-mental` v4 exercises retain the 14-block / Five-Anchor / Four-Pass / Oracle contract in [v4-contract.md](v4-contract.md). Selecting the article profile changes the *presentation*, not algorithmic correctness or the user's opted-in learning mode.

For this profile, **leetcode-mental is the sole semantic Content Owner**: it produces and approves the entire source-grounded English technical narrative and the full Traditional Chinese final draft, including examples, reference code, decisions, invariants, proof, runtime internals, alternatives, complexity, limits, figures and interview content. It owns approval of any changes suggested by sloptrim, translation or semantic review.

**medium-writing is the Medium formatter and assembler** for an already approved article edition. It owns Medium-native headings, readable code and figure placement, captions/alt text placement, contiguous delivery parts, and the existing CLI's legal Stage 0–7 admission/assembly. It may not invent facts, delete qualifications, paraphrase protected code, shorten the article as a summary, or editorially rewrite accepted content. A content defect goes back to leetcode-mental for a new approved edition; do not use Stage 7 as a repair step. For non-LeetCode routes, medium-writing's existing writer ownership is unchanged.

The `alg-four` annotation owner is downstream only: it reads the accepted article bytes and adds Passive/Active notes without rewriting the base article. Neither this profile nor the formatting stage creates a Four-Pass learner session, runtime mastery evidence, new CLI stage, or publication authority.

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

This is a **content coverage contract**, not eight mandatory section names. The number of sections is determined by the actual reader decisions and distinct runtime boundaries, not a default quota. Build a single causal narrative in natural paragraphs. Merge repeated claims across teaching passes, repeated summaries and duplicated introduction/closing sections, **without dropping unique examples, limitations, proof obligations or decision outcomes**. For the Medium edition do not force the ordinary v4 fourteen pedagogical blocks into fourteen article headings; Four-Pass exercise material remains on the separate selected teaching route.

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

## Part delivery and Stage boundary

The existing medium-compiler **Stage 0–7 remains unchanged**. Leetcode-mental supplies content needed for those stages; medium-writing sends it through the actual legal CLI steps and preserves source/code semantics. Stage 6 for this profile is a format-preserving pass over already approved wording (not a second editorial author); Stage 7 copies admitted bytes. Existing-article revisions follow the CLI's supported `init --draft` or authorized technical correction route; do not fabricate historical stages.

`Part 1..Part N` are **contiguous slices of one approved edition**, not new versions of authoring Stages 1..N. Use actual manifest/CLI output to pin order and exact bytes; place title only in Part 1, preserve complete code fences, number headings consistently, never duplicate sections or continuation narration within pasteable prose. If deduplication requires changing approved content, return to leetcode-mental and reapprove **before** Stage 7.

The assembled Medium result must contain the complete approved article once, with figure slots at the agreed positions, and no private sidecars, audit IDs, placeholders not intentionally marked as figure slots, or "continue?" chatter. Medium formatting does not prove semantic correctness, actual rendering, publication or learner comprehension.

## Minimal acceptance and stopping rule

Before handoff, check that an unfamiliar reader can reconstruct: goal and constraints; each material decision; why the representation works; an actual input-to-output trace; relevant language/runtime mechanism; alternative and failure case; cost derivation; full code/proof; what is a mental demonstration versus a test. Use another problem with different constraints in focused regression/evals to ensure no solution-specific fixed alphabet, key, Big O, section count or figure count leaks into the general profile.

Acceptance claims must separate `CONTENT_REVIEWED`, `SLOPTRIM_RUN/NOT_RUN`, `TRANSLATION_REVIEWED`, `CLI_VALIDATED`, `RUNTIME_TESTED/NOT_RUN`, `INDEPENDENT_READER/NOT_RUN`, `IMAGES_RENDERED/NOT_RUN` and `PUBLISHED/NOT_RUN`. These are reporting labels, **not** new CLI statuses.

Stop cognitive recursion once no new source-grounded, falsifiable issue could change scope, owner, behavior or verification. Do not re-run thinking methods as ceremony.
