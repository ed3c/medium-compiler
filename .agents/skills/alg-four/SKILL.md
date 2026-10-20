---
name: alg-four
description: Add source-bound Passive/Active English reading projections in a right-hand article outline, with paragraph-accurate anchors, yellow Active terms and Mode C syntactic chunk/stress cues. Preserve complete original Medium content and four encounters without rewriting it.
---

# ALG Four — annotate original articles, never rewrite them

## Three Owners

- [leetcode-mental](../leetcode-mental/SKILL.md) owns the original coding problem and **complete article semantic content** under its [complete-article profile](../leetcode-mental/references/article-content-profile.md), including decisions, invariant, runtime, code, proof and constraints. Ordinary v4 teaching retains its original scope.
- [medium-writing](../medium-writing/SKILL.md) owns **Medium layout and exact-edition assembly** for the selected complete-article profile; other writing routes retain their existing ownership. The accepted original article stays byte-identical when ALG Four projects its notes.
- **alg-four** owns the separate **annotation projection**, English Passive/Active selection, semantic word-to-concept links, productive English sentences, practice cues and source oracles **only in a right-hand, paragraph-indexed reading outline, not inserted below the original paragraphs**. It does not own rewritten versions of the article, a new Writer, a new LMS, a new CLI stage, or a second Router.

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

Every original prose paragraph/blockquote must have exactly one source-bound **sidecar entry** in the right-hand hierarchical outline, accessible by a stable paragraph anchor. Expand the current section/subsection and paragraph entry as reading position changes; clicking outline headings or paragraph entries navigates to the original article. Keep headings, paragraph sequence, code, technical semantics, original article facts and word choice **unchanged**. Annotation decisions come from the entire article, not a quota of exactly five; include the original engineering claims throughout. Notes must be concise Traditional Chinese with the canonical English terms intact and tied to an actual decision and the paragraph's subject.

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
collapses unrelated branches. Wide screens put the sticky outline on the right;
small screens provide an accessible collapsible outline above the article.
Do not infer reading completion or record learning events from viewport tracking.

**Active**: mark admitted lexical items yellow within the expanded annotation
entry, with the bound English production sentence and optional recall/oracle.
Yellow is a visual training cue, not measured mastery.

**Passive Mode C**: add a derived *English reading projection* inside the expanded
entry, not a rewrite of the immutable article. Preserve every source-attested
claim, lexical sequence, condition and negation. Use `/` for relevant syntax
phrase boundaries, `//` plus line break at major clause boundaries, and
`[ ]` around supported lexical bundles. Prefer chunks of three to five words
when grammar allows; do not insert separators mechanically where they change
syntax or meaning. Never insert syllable dots/hyphens. Bold **only** the primary
stressed syllable of a content word when its pronunciation has been checked;
unverified words stay unbolded. Function words are plain, with no fake acoustic
emphasis or bionic initial-letter pattern. An annotation can additionally
compress the sentence's subject-action-object relationship to 10–15 words,
but that optional skeleton must be source-grounded and must not replace the
article, original sentence or its nuance.

This Mode C projection is a reading layout hypothesis, not a proven speed,
fixation, neurological or comprehension improvement. For text without verified
English stress/chunk annotations, show faithful plain English rather than
inventing phonology. The cumulative Active target and ALG Four four-encounter
policy are unchanged. A host that lacks user input/response evidence must still
say `NOT_OBSERVED`.

## Evidence and limits

The [full annotation contract](references/lesson-contract.md) defines source identity, paragraph coverage and 2000-item admission; the [Thinking Route](references/thinking-route.md) chooses only necessary cognitive interventions and the [migration](references/migration.md) preserves legacy consumers. Freeze the source Git blob; refuse a changed original or missing paragraph. `RUNTIME_TESTED`, `ACTIVE_PRACTICED`, response latency and acquired vocabulary need real runtime/learner evidence; website build and 4 available passes establish none of these.

The fourth encounter is an instructional procedure **not** a scientifically established neural consolidation threshold. No invented repetition schedule, credential, learning database, or mastery claim.
