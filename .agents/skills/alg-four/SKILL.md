---
name: alg-four
description: Integrate speed-reading annotations into a source-bound right-hand article index with paragraph anchors, admission validation and reading navigation. Preserve complete original Medium content and four encounters without rewriting it.
---

# ALG Four — annotate original articles, never rewrite them

## Owners

- [leetcode-mental](../leetcode-mental/SKILL.md) owns the original coding problem and **complete article semantic content** under its [complete-article profile](../leetcode-mental/references/article-content-profile.md), including decisions, invariant, runtime, code, proof and constraints. Ordinary v4 teaching retains its original scope.
- [medium-writing](../medium-writing/SKILL.md) owns **Medium layout and exact-edition assembly** for the selected complete-article profile; other writing routes retain their existing ownership. The accepted original article stays byte-identical when ALG Four projects its notes.
- [speed-reading](../speed-reading/SKILL.md) owns **article-index annotation content**: every paragraph's Traditional Chinese explanation, complete English chunk/stress reading, cognitive skeleton and source-supported Passive/Active production sentences, cues and oracles. It reviews semantic support across the complete paired article; the source body remains immutable.
- **alg-four** owns the **source-bound annotation integration**: paired source identity, one-to-one coverage, admission validation, paragraph anchors, right-hand index navigation and rendering. It receives speed-reading's content in the existing sidecar rather than authoring another annotation set. It does not own a rewritten article, new Writer, LMS, CLI stage or second Router.

[alg-vocab-encounter](../alg-vocab-encounter/SKILL.md) remains the passive lexical-practice leaf. Historical [cefr-alg-four-pass](../cefr-alg-four-pass/SKILL.md), its 12-file upstream Git Blob lock, frozen lessons and original CEFR session oracle gate remain unchanged.

## Cumulative 2000 Active terms and 2000 related sentences

This is a cross-article, deduplicated **target corpus**, NOT a requirement to find two thousand words inside one LeetCode explanation.

An Active lexical item must satisfy every admission condition:
1. It is necessary or reusable for explaining a **real decision, invariant, canonical identity, state transition or underlying runtime mechanism** from the source.
2. It has an exact source-article identity and paragraph index; the term or its meaning is actually supported by that paragraph.
3. It helps an engineer independently *produce* an explanation in precise English, not merely recognize a rare word.
4. It has at least one fully formed English sentence faithful to the same original technical claim, actor, condition, negation and consequence.
5. A source-bound question or meaning oracle can distinguish an accurate response from a superficially fluent one.
6. Repeated terms with equivalent meanings across articles share one corpus identity; record more contexts, do not inflate the distinct count.

The wider **Passive** inventory covers encounter and recognition. Classify each original article paragraph as `PASSIVE` or `PASSIVE_AND_ACTIVE`; the same core concept may be encountered receptively and later generated actively. The labels are practice roles, not grammatical passive/active voice and not achievements. Reject nonsource filler rather than manufacturing 2000 entries.

## Four cognitive encounters, always on the SAME original paragraphs

1. Encounter the actual original paragraph, notice term form, sound and the short zh-TW meaning annotation with original English technical terms.
2. Revisit that same paragraph and recognize the engineering decision and its word-to-runtime link.
3. Re-read or listen to the **same** paragraph with original context and trace its invariant, actor, branch or state change.
4. Without copying the original, generate an English sentence and decision explanation; compare to the source-bound oracle after an authentic attempt.

These are **four operations over the same prose**, not `pass1/pass2/pass3` replacement texts or separate rewritten sections. A published site may expose a non-tracking expandable prompt/oracle in the **right-hand section/paragraph outline**, linked to the unmodified source paragraph. It is not a native CEFR Session. That older UI still requires an acknowledged attempt before reveal and a distinct reported comparison event.

Every original prose paragraph/blockquote must have exactly one source-bound **sidecar entry** in the right-hand hierarchical outline, accessible by a stable paragraph anchor. Expand the current section/subsection and paragraph entry as reading position changes; clicking outline headings or paragraph entries navigates to the original article. Keep headings, paragraph sequence, code, technical semantics, original article facts and word choice **unchanged**. The speed-reading Owner makes annotation decisions from the entire article, not a quota of exactly five; include the original engineering claims throughout. Notes must be concise Traditional Chinese with the canonical English terms intact and tied to an actual decision and the paragraph's subject.

## Right-hand source-preserving reading projection

The site must first receive one approved, **complete** article from the selected
`leetcode-mental → medium-writing` route. `alg-four` reads that pinned source and
projects annotations **alongside**, never into, the article. It may continue to
display the currently pinned original sample until an approved replacement article
is available; a Skill change alone does not prove that a new article was authored.

For the complete LeetCode article profile, require an approved English source
that aligns **one-to-one with the current Traditional Chinese prose paragraphs**.
Validate both original Git blobs, rendered heading and paragraph structure,
protected code and all section/figure placements before emitting any annotations.
A changed paragraph or edition requires source re-review and a newly pinned
manifest; decision-level English summaries cannot silently replace paragraph
English in Mode C.

Build the outline from actual Markdown heading levels (H1/H2/H3/H4 as supported by
the local renderer) and the exact paragraphs that follow them. Every paragraph
has a stable anchor and one annotation; click a heading/paragraph to jump.
Scrolling expands the active headline, subheadline and paragraph note and
collapses unrelated branches. Keep the complete article centered. At the middle
right, a normally closed rail has one bar per top-level chapter (including the
introduction), with bar length proportional to that chapter's rendered text and
an explicit chapter/paragraph count in the expanded panel. The selected bar
reflects reading position, not completion. Hover or button activation opens a
scrollable contents-and-notes dialog; touch and keyboard must also work without
hover. Escape/close restores the trigger's focus. Navigating to a heading must
select its first following paragraph, rather than a note in the preceding chapter.
Do not infer reading completion or record learning events from viewport tracking.

**Active**: render speed-reading’s admitted lexical items yellow within the expanded annotation
entry, with the bound English production sentence and optional recall/oracle.
Yellow is a visual training cue, not measured mastery.

**Passive Mode C**: consume the repository [speed-reading Owner](../speed-reading/SKILL.md)'s
annotation for the complete aligned English paragraph. Its dual-layer result and short
cognitive skeleton belong only in the expanded annotation, never the original
body. Review syntax, scope and pronunciation separately from lossless identity.
Store reviewed formatting with the existing paragraph sidecar; no model or
dictionary requests run in the browser or CI. Without reviewed formatting or
pronunciation, keep faithful plain English rather than generating mechanical
chunks or initial-letter bolding. Preserve existing approved projections until
a reviewed replacement is available.

This Mode C projection is a reading layout hypothesis, not a proven speed,
fixation, neurological or comprehension improvement. For text without verified
English stress/chunk annotations, show faithful plain English rather than
inventing phonology. The cumulative Active target and ALG Four four-encounter
policy are unchanged. A host that lacks user input/response evidence must still
say `NOT_OBSERVED`.

## Evidence and limits

The [full annotation contract](references/lesson-contract.md) defines source identity, paragraph coverage and 2000-item admission; the [Thinking Route](references/thinking-route.md) chooses only necessary cognitive interventions and the [migration](references/migration.md) preserves legacy consumers. Freeze the source Git blob; refuse a changed original or missing paragraph. `RUNTIME_TESTED`, `ACTIVE_PRACTICED`, response latency and acquired vocabulary need real runtime/learner evidence; website build and 4 available passes establish none of these.

The fourth encounter is an instructional procedure **not** a scientifically established neural consolidation threshold. No invented repetition schedule, credential, learning database, or mastery claim.

For speed-reading-authored notes, the complete annotation is the acceptance unit:
show source-bound premises and any state/order checkpoint before the short
reading cue (閱讀提示，非獨立結論). A source citation alone does not explain why
its premise matters. Follow the speed-reading Owner contract; the UI/validator
checks presence and exact bindings, while Owner/Reader review completeness.
