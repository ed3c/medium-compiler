# Issue #3 — one bounded source correction

This atom proves a writing-specific path for one real existing article. It does not add
stage rollback, hooks, a generic technical-edit manifest, or a semantic score.

## Real defect

Article: `articles/ai-engineer-learning-path.md`

Before (`main` commit `6b9b24f35c8f3271ff04673efad337db2e60371f`, Git blob
`4e57eef57fa5d84f8dbc58790947bcef067eb463`) the Chip Huyen learning-resource link
pointed to the GOTOP commercial book page.

The replacement is the author's public `chiphuyen/aie-book` companion repository. Provider
readback pinned for this atom: `f375e0065ef19e4f411b809a2f9a2d65582db287`. Its README
links the Table of contents, chapter summaries, study notes, AI engineering resources,
prompt examples and case studies.

After Git blob: `e3c1ad1f3e76179d94e797436aaf9048e85216c8`.

## Smallest mechanism

Existing revision flow is unchanged:

```text
init --draft -> submit 6 -> assemble -> verify -> prove-update
```

Stage 6 now accepts either ordinary copyedit coverage or exactly one imported-article
`source_correction` declaration with one `source_link.from -> source_link.to`. The CLI
allows that one destination change and continues to protect every other link destination,
fenced block, inline code, protected literal and canonical term.

No new command is added. `semantic_correctness` remains `NOT_ASSESSED`.

## Executed controls

Executed locally in this task's Linux/Python 3.13 container from the exact main source
blobs and the candidate source blobs later uploaded to GitHub.

- full candidate suite: **35 PASS**;
- real article, same after bytes with ordinary copyedit sidecar: **REFUSED, exit 2**,
  `copyedit changed protected source links`;
- same real article with the one declared source correction: **PASS**;
- `check-receipt`: **VALID**;
- `prove-update --issue 3`: **VALID**;
- after bytes equal `medium-canonical.md` exactly;
- terminal `next`: `VALIDATED`, `next = null`;
- source-correction fixture plus an unrelated second link change: **REFUSED**;
- source-correction fixture plus fenced-code mutation: **REFUSED**;
- ordinary wording-only revision remains **PASS**.

`summary.json` records the exact digests and statuses. `article.diff` is limited to the one
Chip Huyen resource paragraph. `source-correction.json` is the exact declaration used for
the real run.

## Evidence boundary

This proves a real product path and mechanical discrimination. It does not claim universal
writer behavior improvement or semantic correctness. A fresh-agent A/B would answer a
different question and is deliberately outside this atom.
