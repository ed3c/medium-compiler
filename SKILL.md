---
name: zero-context-medium-writing
description: >-
  Draft technical Medium articles in Traditional Chinese from a zero-context reader
  perspective. Preserve a causal chain from problem constraints to runtime, cost and
  implementation. Use the repository CLI for stage order and completion; keep semantic
  choices in the writing layer. No generated images are required.
metadata:
  version: "1.1.0"
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

The writing layer owns five semantic choices:

1. **Central question** — the smallest reader question that unlocks the topic.
2. **Governing property** — the invariant, constraint or system property that explains the
   main decision.
3. **Primary representation / architecture** — the state or structure that most directly
   expresses that property.
4. **Runtime witness** — one concrete example that crosses the material state boundaries.
5. **Alternative** — one competing approach that teaches a real decision boundary.

Everything else should follow from those choices and the source.

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

Fenced code blocks are protected bytes. Do not hide a technical correction inside copyedit.

### A semantic correction before assembly

Run `next` to observe the current state. If the correction belongs to an earlier
semantic stage, choose the earliest affected stage from the article's meaning;
do not always choose Stage 4. If that target is listed in `reopen_stages`, invoke:

```sh
python3 medium_compiler.py reopen --run-dir <run> --stage <target>
python3 medium_compiler.py next --run-dir <run>
```

The CLI owns invalidation and accounting. Follow its `next` and `next_stage`,
re-submit only the required suffix, then repeat the constrained prose pass.
Edit external stage inputs, never `state.json`, admitted parts, or their digests.
Pure wording cleanup before Stage 6 submission stays in Stage 6; do not reopen.

An imported draft has no admitted Stages 1-5. An assembled run, changed admitted
bytes, or a correction requiring a changed spec is not this operation's scope.
Stop and report the missing technical-edit prerequisite in those cases. Do not
invent stage history, weaken a guard, guess a replacement route, or restart the
whole article merely to obtain a green receipt.

## Stage 7 — Assembly

Do not author new prose.

The CLI takes the admitted Stage 6 article and creates the canonical Medium artifact. If a
new fact is needed before assembly, use the semantic-correction path above.
Do not decide invalidation or completion from prose.

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
