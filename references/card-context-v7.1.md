# Optional v7.1 context adapter for writing

This is a writing-side interpretation, not a copy, patch or execution of the card compiler.
No card runtime, registry, Google persistence or permission machinery is installed here.
A complete article may be written without supplied cards.

## Source boundary

Reference: ed3c/ai-content-notes, governance/CARD_PROTOCOL_CURRENT.json, selecting
`governance/CARD_PROTOCOL_V7_1.md`, Git blob
`7f3019f4b41a90728cd48a523d742c7c59721bf6` (checked 2026-09-26).
The consulted portions are sections 2.1–2.3 and I-01–I-16. This pointer identifies the
reference text, not evidence that medium-compiler executed its full QG contract.

## What is retained

- **Evidence-first compilation, task-value-first rendering** (2.1–2.3, I-02): examine
  claims and evidence internally; begin the article with the problem the reader can grasp.
  Do not concatenate card headers or expose a registry as the story.
- **One decision-relevant case, not one sentence** (I-03/I-04): keep the condition,
  operation and outcome together. Separate incompatible versions, outcomes or evidence.
- **Lossless batching and exact detail** (I-01/I-05/I-06): preserve qualifiers, numbers,
  versions, code and real locators. Deferred content names a future section; it is not
  replaced by a summary. Missing locators remain missing.
- **Source dependency and epistemic separation** (I-07/I-08): several cards from one
  source are not independent corroboration. SOURCE_STATEMENT stays source-reported;
  OBSERVATION, INFERENCE, HYPOTHESIS and NORMATIVE keep their separate meanings.
- **Conflict/unknown remain explicit** (I-09/I-10): keep supplied X/K material and its
  affected claims. Do not silently resolve or delete it for narrative smoothness.
- **Stable identity and typed relationships** (I-11/I-12): reuse supplied stable IDs,
  canonical keys, scope and revision. DEPENDS_ON is a dependency, FLOW is a causal or
  enabling relation, VALIDATED_BY refers to evidence; none is an interchangeable arrow.
- **Execution and style limits** (I-14/I-16): unrun checks remain NOT_RUN/UNTESTED.
  Style cannot strengthen certainty or replace the original terminology.

## Small writing projection

Use one context companion, not a mandatory new card per sentence:

```text
source/revision + supplied card identity
  -> claim with scope, condition, qualifier, status and locator
  -> reader question / decision / concrete example
  -> destination article section
  -> rendered / deferred(section) / excluded(reason) / unknown
```

This is an editorial data flow, not a security or execution state machine. Do not write a
private source body or private locator into a public article. Use only material authorized
for that destination. Required information cannot be marked excluded just to finish.

N/C/D/S/T/P/V/X/K remain the supplied card types; a P procedure card is not Soodles
P-class authority. Reader aliases such as A01 are local presentation labels, not imported
permanent card IDs. No supplied cards means `supplied: false`, not a fabricated registry.

Preservation needs source review as well as literal checks: a writer-created claim ledger
can itself omit a condition. A complete ledger or valid digest does not prove zero-context
comprehension, technical correctness, rights clearance or full card-pipeline completion.
