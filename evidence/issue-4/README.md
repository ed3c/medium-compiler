# Issue #4 — final scoped evidence

## Real problem

The previous article satisfied the first link gate—public and no purchase required—but still
recommended `chiphuyen/aie-book` as a main learning resource. That repository is a
companion/index surface, not the substantive chapter content the reader needs.

This atom therefore distinguishes:

```text
open access
!=
substantive learning content
```

## Real article correction

Same article: `articles/ai-engineer-learning-path.md`.

Resource-specific before:
- commit: `84090e8af9e8f66ce06ff42b4d9bcdbc2a41a8cc`
- article blob: `11250c64c4131440edc7bb54f41c89347472e8f3`

After:
- article blob: `19c0ef18be878324fde4670e5d3ad03fcf42e00d`
- article diff: 4 additions / 10 deletions across four learning-resource passages

The companion link is removed. The article now sends readers directly to:
- SLP 2026 Chapters 7, 8 and 11;
- Happy-LLM Chapters 5, 6 and 7;
- Hugging Face LLM Course SFT and Evaluation;
- the full AI Engineering from Scratch curriculum.

## Minimal repository mechanism

`SKILL.md` and `prompts/medium-article.md` add one rule: a core learning recommendation
must point to a complete chapter, full open manuscript/book, complete lesson with
implementation, or complete tutorial. A public companion/index alone is not sufficient.

`references/open-access-resources.json` records `learning_depth` so the article can
separate substantive teaching material from product/operational references.

No compiler runtime code is changed by this issue. The branch is rebuilt on the latest main
so Issue #3's runtime changes remain intact.

## Verification

GitHub readback checks prove:
- the real article changed;
- `chiphuyen/aie-book` is absent;
- direct SLP 7/8/11, Happy-LLM 5/6/7 and HF SFT/Eval links are present;
- the required direct teaching links are marked substantive;
- all reader URLs remain allowlisted and paid-preview patterns are absent;
- five delivery parts concatenate exactly into the article and match their manifest blobs;
- the Skill and task prompt contain the substantive-resource rule.

External source review confirmed the linked SLP chapters are full public chapter PDFs,
AI Engineering from Scratch exposes its full curriculum, Happy-LLM exposes full practical
chapters, and Hugging Face exposes the full SFT/evaluation lessons.

## Evidence ceiling

This closes the reader-resource-depth defect. It does not claim that every reader will
prefer the selected books, that an independent reader study was run, or that the article
was published to Medium.
