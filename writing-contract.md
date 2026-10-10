---
name: zero-context-medium-writing
description: >-
  Draft zero-context Medium articles in English, review English prose with
  sloptrim, then translate to Traditional Chinese with English technical terms. Preserve a causal chain from problem constraints to runtime, cost and
  implementation. Use the repository CLI for stage order and completion; keep semantic
  choices in the writing layer. No generated images are required.
metadata:
  version: "1.2.0"
---

# Zero-Context Medium Writing

## Purpose

Produce one technical article that a software engineer can understand without prior
conversation context.

The article must make this causal chain reconstructable:

```text
Problem
-> Decision
-> Representation
-> Runtime
-> Internals
-> Alternatives
-> Complexity / Cost
-> Implementation
-> Interview
-> Master Map
```

This is a writing skill, not a generic summarizer. A reader should be able to explain why
the main design follows from the stated constraints and what happens to one concrete input
at runtime.

## Authority split

Do not decide stage order, completion, claim accounting, term identity, or final-byte
freshness from prose. The CLI owns those deterministic questions.

The writing layer uses five organizing questions (not an exhaustive count of semantic judgments):

1. **Central question** — the smallest reader question that unlocks the topic.
2. **Governing property** — the invariant, constraint or system property that explains the
   main decision.
3. **Primary representation / architecture** — the state or structure that most directly
   expresses that property.
4. **Runtime witness** — one concrete example that crosses the material state boundaries.
5. **Alternative** — one competing approach that teaches a real decision boundary.

Correctness, source interpretation, scope and cost derivations still require semantic judgment. The five questions organize the work; they do not count the reader decisions in a particular article.

## Stage 0 — TOC and maps

Output the table of contents first.

Then show two narrow text diagrams:

- a decision map: constraint -> choice -> consequence;
- a runtime/data-flow map: input/state -> operation -> new state/output.

These maps are reader aids. They do not introduce claims that the prose will never explain.
Use fenced `text` blocks. Do not require images, Mermaid, or decorative diagrams.

## Stage 1 — Problem, property, representation

Explain:

- exact problem / task contract;
- the constraints that matter;
- the governing property;
- why the selected representation follows from it.

Do not begin with APIs or a final implementation.

## Stage 2 — Runtime witness and internals

Follow one concrete input.

For every material transition, make this reconstructable:

```text
current input/state
-> executed operation
-> new state
-> lookup/identity/ownership boundary when relevant
-> visible effect
```

Introduce only the runtime internals necessary to explain those transitions.

## Stage 3 — Alternative and cost

Compare one useful alternative under the same task contract.

State the decision boundary: under what changed constraint would the alternative become
reasonable?

Derive time, space, latency, bandwidth, memory or other cost from actual operations and
resource movement. Define variables before using them. Do not paste a memorized Big O or
benchmark number without a supported derivation/source.

## Stage 4 — Implementation and correctness

Present the complete implementation or concrete architecture after the reasoning exists.

Map important code/architecture pieces back to the runtime witness. Explain correctness or
safety from preconditions, maintained properties, transitions and the resulting state.
Include edge cases that change behavior.

## Stage 5 — Interview and Master Map

Give concise English answers only for claims already established in the article.

End with one text Master Map containing only previously explained relationships. It is a
compression of the article, not a place to introduce new facts.

## English-first article and bilingual fidelity

The semantic writing owner first completes the English prose for the entire
requested article, or the currently admitted incremental unit. Before making
a Traditional Chinese translation, apply the upstream
[sloptrim](https://github.com/seyedehsanhadi/sloptrim) skill to this English
prose, then check each changed passage against source facts, causal reasoning,
technical terms, attribution, negation, qualifications and failure cases.
The tool is a local style detector and rewrite method, not an authorship
classifier or semantic oracle. Record the actual run or `NOT_RUN`; do not
fabricate style or semantic PASS. Do not scrub code, logs, exact quotations,
receipts or protected identifiers. Do not use sloptrim to alter an approved
Traditional Chinese canonical article.

Translate the approved English prose into natural Traditional Chinese with
exact English technical terms. Preserve all source-grounded claims, limits,
examples, diagrams and runtime transitions. Check the English and Chinese
versions line-by-line where decisions or qualifiers matter. Preserve both
draft identities in external/context evidence. A missing independent reader
remains `NOT_RUN`; author comparison is not independent review. For new
articles submit the Chinese units through the existing Stage 0–7 order; for
incremental writing, translate and review each completed English unit before
its legal patch/submit. Neither process creates a new compiler stage.

## Stage 6 — Natural prose after semantic freeze

Treat the Stage 1-5 semantic draft as frozen meaning. Rewrite expression, not technical
content.

Prefer natural Traditional Chinese with exact English technical terms where they carry
technical identity.

Remove or rewrite when they add no independent information:

- staged openers such as 「接下來讓我們」 or 「本文將深入探討」;
- repeated meta narration such as 「本文」「這一階段」「前進條件」 used as curriculum
  bookkeeping instead of explanation;
- fake emphasis and dramatic one-line closers;
- forced three-part summaries whose items repeat each other;
- repeated defensive disclaimers that can be expressed once at the actual boundary;
- abstract verdicts when a concrete operation/condition already explains the point.

Preserve when technically meaningful:

- real negation and contrasts;
- qualifiers such as only, may, average-case, under this workload, NOT_RUN;
- canonical English technical terms;
- code identifiers, API names, versions, numbers and supported quotations;
- source attribution and uncertainty;
- correctness conditions and failure boundaries.

Do not optimize for an AI-detector score. Do not invent anecdotes or personal experience.
Do not rotate technical synonyms simply to reduce repetition.

Fenced code blocks are protected bytes. If code needs a technical correction, return to the
earlier stage instead of hiding it inside copyedit.

## Stage 7 — Assembly

Do not author new prose.

The CLI takes the admitted Stage 6 article and creates the canonical Medium artifact. If a
new fact is needed, return to the affected semantic stage, update coverage, and repeat the
prose pass.

## Zero-context check

Before declaring the prose ready for deterministic assembly, ask whether a reader who has
only this article can answer:

- What problem is being solved?
- Which constraint caused the main decision?
- What does the representation mean?
- What happens to the concrete runtime witness?
- Why is the alternative different, and when would it be preferable?
- Where does the stated cost come from?
- How does the implementation correspond to the runtime explanation?

If the article itself does not contain the answer, repair the affected stage. Do not rely on
the reader's outside knowledge to fill the gap.

## Existing article: bounded revision, not fictional regeneration

When the task is to improve an existing article, use `init --draft BEFORE.md`.
The CLI snapshots that article and routes directly to Stage 6. Do not manufacture
Stages 0-5, a fresh writer run, or coverage claims for work that did not occur.
New articles keep the staged path above.

Choose a concrete prose defect and edit only its affected passages. Replace vague
checkpoint narration with the existing operation, output or reader question;
do not simply replace 「前進條件」 with 「做到這裡」 everywhere. Do not turn all
headings into questions. Preserve the exact technical claim, scope, negation,
uncertainty and reading goal. Keep a before/after note for each changed passage.

Use the CLI to preserve fenced blocks, inline code, source-link destinations and
specified literals. Submit once, assemble, verify, then prove-update against the
imported baseline. A changed admitted file requires a new run; do not repair the
state JSON or refresh a receipt to hide the change. `next` returns no next action
after a valid receipt. Code or source corrections require a separately declared
technical edit, not a weakened prose-only guard.

A nonempty diff is only change evidence. Keep author review, independent reader
results, natural writer A/B and publication status separate; report only what was
actually executed. Identical protected bytes do not prove semantic fidelity.

## Reader decisions and source-preserving staged output

Use [the task prompts](prompts/medium-article.md) for task, continuation and assembly input.
This SKILL is the writing contract; the prompt file is a task adapter, not a second system
prompt. For supplied v7.1 cards, use only the optional
[card-context reference](references/card-context-v7.1.md).

### Three different counts

Keep separate: numbered article sections; principal reader decisions within the topic;
and the five organizing questions above. Derive the decision count after mapping the
actual source. Neither 5, 12 nor the example's 14 is a quota for another subject.
A principal reader decision has a reader question, competing action, a condition that
changes the choice, a consequence and an exact source/section anchor. Merge adjacent
steps that serve the same choice; do not equate every if statement with a teaching decision.

### Stage 0 presentation

Show the article table of contents first. Then explain the scope and necessary terms,
list the derived decisions with their condition and destination section, and show:

- a text mind map of decision/dependency relationships;
- a directory or symbol tree of the actual subject, labeled observed/proposed/embedded;
- one input-to-output data-flow map with relevant refusal and missing-evidence branches.

Distinguish the subject's runtime from medium-compiler's writing runtime. A directory
shows containment, not execution order. Every map label must be explained in nearby
prose or assigned to a named section; a map cannot silently add facts. A design sketch
is not execution evidence. Existing code identifiers and conditions stay exact.

### Carry context without printing the audit

Keep one compact companion with source/revision, decision anchors, canonical terms,
necessary claims/qualifiers, unresolved gaps and the next delivery part. Reuse imported
stable card IDs and typed relationships, never make up a completed card batch. Mark
rendered / deferred-to-section / explicitly excluded-with-reason / unknown; never silently
drop material. Required claims cannot be excluded merely to satisfy a gate.

The companion is a review aid, not semantic authority. Literal preservation checks
cannot prove that every relevant source claim was captured in a writer-created ledger.
Source review must also look outside the ledger. Preserve contradictions and unknowns.

### Authoring stages are not delivery parts

For new articles, keep the CLI's Stage 0–7 authoring flow. By default stop the current
chat response after the requested stage; resume only the next stage when asked. An
explicit uninterrupted request executes the phases internally. Do not ask whether to
continue when the user has already requested uninterrupted execution.

For an existing article, read the complete baseline and keep its organization unless
structural revision was requested. Do not rewrite it into a different subject or invent
prior authoring events. A requested reading overview can be added as a declared,
source-grounded insertion, preserving the original body. That is an editorial addition,
not an independent semantic PASS from the CLI.

Delivery parts are contiguous slices of an approved article edition. They may group
sections differently from authoring stages. Name their order, byte digests and final
article digest in one assembly manifest. Keep the title only in the first part and
source/limitation notes in the final part. Do not split a fenced block. No generic
recap, repeated heading or continuation note belongs inside a copyable part.

Stage 6 may revise earlier drafts. After it does, use a complete set of parts from that
same approved edition; never mix earlier chat drafts with final parts. Stage 7 remains
a copy of accepted bytes, not an opportunity to add or compress information. The Stage-0
planning companion is not automatically pasted into the article; any reader-facing TOC
or map needed in the final piece must already be in its admitted prose.

When a change touches protected code, link or diagram bytes, do not weaken the prose
check or edit state.json. Record the intended technical change and follow only a
currently implemented route. Issue #3 owns the separate reopen path; its issue text is
not evidence that the command exists.

Report artifact assembly, mechanical preservation, author review, independent reader
and fresh-writer transfer separately. No skill or digest can guarantee lossless meaning
or identical writing quality for every future topic.


## Medium-native final body

The final reader-facing Medium article uses headings/subheadings, paragraphs, emphasis,
links, quotes, lists, inline code and fenced code/text blocks. Do not use Markdown or HTML
tables in the final body. Internal audit files may use tables. Render matrices as labeled
blocks, short lists, Option A / Option B, or fixed-width text only when alignment matters.

Medium web builds table-of-contents navigation from headings/subheadings. Stage 0 may show
an outline for planning; do not duplicate a manual TOC into final prose unless requested.

## Reader-link access gate

Every reader-facing link must be readable without purchasing a book or crossing an
owner-only login gate. Prefer pinned public source files/commits, open-source books/repos,
public official docs, or complete public articles. Do not link stores, paid previews,
private repos, owner-only workspaces, or login-gated evidence. Public provider docs are
allowed even when actual API execution later needs credentials; state that distinction.

For the worked AI Engineer article, every external URL must appear in
`references/open-access-resources.json`.

## Real public running examples

When the user names a real public repository as the running example, use that product's
actual problem, state, code and retained evidence rather than preserving a synthetic case
for convenience. Do not force RAG, Agent, fine-tuning or another layer into the narrative
when the repository does not need or implement it.

The current worked article uses
`ed3c/ops-reconciliation-copilot@24a56d18661630b0dba97dcb0b057dce07b0ab32`.


## Substantive learning-resource gate

Open access is necessary but not sufficient for a core learning recommendation.

A reader-facing **core learning resource** must lead directly to at least one of:

- a complete book chapter or full open manuscript;
- a complete lesson with explanation plus runnable code/tests;
- a full open-source book whose chapter body is directly readable;
- a complete technical tutorial/article with enough detail to perform the stated task.

Do not use a companion/index repository, bookstore page, preview page, summary-only page or
link collection as the primary resource for a concept. An index may remain a secondary
navigation aid only when the article also links the exact substantive chapter/lesson.

For the worked AI Engineer article, core teaching links are marked
`learning_depth: substantive` in `references/open-access-resources.json`.
