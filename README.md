# medium-compiler

A writing-only CLI and [P-class skill](SKILL.md) for technical Medium articles.
No model adapter, publishing service, image generator, card compiler or scheduler.
The Agent writes prose; the CLI controls accepted files and assembles the result.

## Writing prompts and the current article

Start with [SKILL.md](SKILL.md), then the reusable
[task / continue / assembly prompts](prompts/medium-article.md).
The [v7.1 context reference](references/card-context-v7.1.md) is optional input guidance,
not a card compiler dependency. The five organizing questions in the skill do not fix how
many decisions the reader must understand.

For the actual AI Engineer article:

- [Stage 0: contents, 14 principal decisions and runtime maps](articles/ai-engineer-learning-path.stage-00.md)
- [Continuous Medium article](articles/ai-engineer-learning-path.md)
- [Context and source anchors](articles/ai-engineer-learning-path.context.json)
- [Ordered delivery manifest](articles/ai-engineer-learning-path.parts/manifest.json)

The five delivery parts are contiguous slices of that existing article, not recreated
Stage 1–5 generation history. Stage 0 is a separate reading plan; do not prepend it to
all five parts. The article itself already contains the reader TOC/decision overview and
its existing runtime diagrams. Concatenate the manifest's parts without adding separators
to obtain exactly the same canonical article bytes.

This edition adds only a source-grounded navigation section. All earlier prose, code,
links and section ordering remain unchanged. [Issue #4 evidence](evidence/issue-4/README.md)
separates literal preservation from author review and unrun independent-reader tests.

## Two entry paths

A new article uses the existing stages:

```text
0 TOC + decision/data-flow maps
1 Problem -> property -> representation
2 Runtime witness -> internals
3 Alternative -> decision boundary -> cost
4 Implementation -> correctness -> edge cases
5 Interview -> master map
6 Prose-only edit
7 Exact-byte assembly
```

```sh
python3 medium_compiler.py init --spec examples/spec.json --run-dir /tmp/new-article
python3 medium_compiler.py next --run-dir /tmp/new-article
```

For an existing article, do not fabricate earlier stages or regenerate the whole piece:

```sh
python3 medium_compiler.py init --spec spec.json --draft before.md --run-dir /tmp/revision
python3 medium_compiler.py next --run-dir /tmp/revision
# next_stage = 6
python3 medium_compiler.py submit --run-dir /tmp/revision --stage 6 \
  --input after.md --coverage copyedit.json
python3 medium_compiler.py assemble --run-dir /tmp/revision
python3 medium_compiler.py verify --run-dir /tmp/revision
python3 medium_compiler.py prove-update --run-dir /tmp/revision --issue 1 \
  --before before.md --after after.md --output /tmp/article-update.json
python3 medium_compiler.py next --run-dir /tmp/revision
# VALIDATED, next = null; this does not mean semantic correctness was assessed.
```

`copyedit.json` contains:

```json
{"elements":["copyedit"],"claims":[],"terms":[]}
```

`spec.json` contains a topic and optional claim/term declarations. See
[examples/spec.json](examples/spec.json). For authoring stages, each coverage sidecar
names the exact elements and claim/term IDs due in that stage. These are structural
accounting declarations, not evidence that the prose entails each claim. Imported
articles explicitly report declared claim coverage as `NOT_ASSESSED`.

## What is enforced

- Bind the imported draft, spec and accepted parts/coverage to their exact bytes.
- Refuse out-of-order submissions on the authoring path.
- Preserve fenced code/text blocks, inline code, Markdown link destinations and
  the exact literals/terms named in the spec during prose-only editing.
- Assemble by copying admitted Stage 6 bytes, without another prose generation.
- Recheck current artifacts when producing or checking a receipt. Merely replacing
  the recorded digest cannot turn mutated code into a new valid receipt.
- End the local flow after successful validation. `check-receipt` is read-only.
- Bind `prove-update` to the imported baseline and current canonical article;
  refuse unchanged/edge-whitespace-only articles and output paths that overwrite inputs.

The prose guard supports top-level Markdown fences and ordinary inline links,
reference definitions and autolinks. It is conservative, not a full Markdown parser.
An intentional code, link, markup or technical-claim change needs an explicitly
scoped technical revision; do not weaken this prose-only check to make it pass.

## Issue evidence

Every writing atom uses a real article before/after, not only synthetic fixtures.
The after article must match the canonical file and its current validation receipt.
The article identity/revision, changed passages and semantic review belong in the
issue evidence, outside the copyable Medium text. Byte inequality alone is not
proof of useful improvement; a keyword count is not a style score.

[Issue #1 evidence and replay](evidence/issue-1/README.md) contains one real four-span
article revision plus a planted control demonstrating the old verifier's false PASS.
The old candidate JSON is historical; the executed evidence is now authoritative for
this scoped local experiment.

## Limits

`VALIDATED` means the stated mechanical contract passed. The CLI does not prove
factual truth, no semantic loss, human preference, or cross-topic writing quality.
Author review, independent-reader testing, fresh writer A/B and publication retain
separate statuses. No command publishes to Medium or closes a GitHub issue.

Local admission state assumes a single cooperative writer. It is not a security
boundary against an actor rewriting the source, state, verifier and receipt together.
A changed admitted artifact requires a fresh run. Legacy unbound runs are refused;
there is no silent migration or invented authoring history.

The style lint is advisory:

```sh
python3 medium_compiler.py style-lint --input articles/ai-engineer-learning-path.md
```

## Tests

Python 3.10+ standard library only:

```sh
python3 -m unittest discover -s tests -v
python3 medium_compiler.py check-receipt --run-dir evidence/issue-1/run
```

To reproduce the real article and candidate controls in a fresh output directory:

```sh
python3 evidence/issue-1/replay.py --out /tmp/medium-replay-new
```

To also reproduce the historical false acceptance, extract the pinned old CLI first:

```sh
git show 3876cbbf1cff627647e2c3c6c13ffda80fa8c1c0:medium_compiler.py > /tmp/medium-old.py
python3 evidence/issue-1/replay.py --out /tmp/medium-replay-paired --baseline-cli /tmp/medium-old.py
```

The replay writes only to its new output directory. It does not call a model or
regenerate the article. It records a deterministic correction, not a fresh-writer A/B.


## Medium output policy

The final Medium article does not use Markdown/HTML tables. Use headings, labeled blocks,
lists and text diagrams instead. The current AI Engineer worked article uses the public
Ops Reconciliation Copilot as its running product example. Reader-facing links are
open-access only and enumerated in `references/open-access-resources.json`.
