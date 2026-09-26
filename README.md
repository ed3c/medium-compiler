# medium-compiler

A small, writing-only compiler for staged Medium technical articles.

The repository intentionally does **not** contain a card pipeline, publisher, model adapter,
Google integration, landing framework, image generator, or general Agent runtime. It owns one
thing: turning a zero-context technical article into a staged, checkable writing flow.

Tracked by [#1](https://github.com/ed3c/medium-compiler/issues/1).

## Writing contract

The P-class skill preserves this causal spine:

```text
Problem -> Decision -> Representation -> Runtime -> Internals
-> Alternatives -> Complexity -> Implementation -> Interview -> Master Map
```

Only five choices stay semantic:

1. the central reader question;
2. the governing property/invariant;
3. the primary representation or architecture;
4. one runtime witness;
5. one useful alternative.

The CLI owns the mechanics: legal stage order, declared claim coverage, technical-term
identity, protected literals/code blocks, deterministic final assembly, and validation bound
to the final article bytes.

A green CLI result is **not** proof that a technical claim is true. It proves only the
mechanically checkable writing contract.

## Stages

```text
0  TOC + decision map + runtime/data-flow map
1  Problem -> governing property -> representation
2  runtime witness -> necessary internals
3  alternative -> decision boundary -> complexity/cost
4  implementation -> correctness -> edge cases
5  interview compression -> master map
6  meaning-preserving prose pass after semantic freeze
7  deterministic canonical Medium assembly
```

Stage 0 is planning output and is not concatenated into the final article. Stages 1-5 form
the semantic draft. Stage 6 is the complete copyedited article. Stage 7 is not another model
generation step: the CLI copies the admitted Stage 6 bytes into `medium-canonical.md`.

## Quick start

The implementation uses only the Python standard library.

```sh
python3 medium_compiler.py init --spec examples/spec.json --run-dir /tmp/article-run
python3 medium_compiler.py next --run-dir /tmp/article-run
```

For each stage 0-6, provide the text and a small coverage sidecar:

```sh
python3 medium_compiler.py submit \
  --run-dir /tmp/article-run \
  --stage 0 \
  --input stage-00.md \
  --coverage stage-00.coverage.json
```

The coverage file declares only the structural obligations and bound IDs for that stage:

```json
{
  "elements": ["toc", "decision_map", "runtime_map"],
  "claims": [],
  "terms": []
}
```

After Stage 5 the compiler materializes `semantic-draft.md`. Stage 6 must preserve all
protected literals, canonical technical terms, and fenced code blocks from that draft.

Then:

```sh
python3 medium_compiler.py assemble --run-dir /tmp/article-run
python3 medium_compiler.py verify --run-dir /tmp/article-run
python3 medium_compiler.py check-receipt --run-dir /tmp/article-run
```

`verify` writes `validation-receipt.json`; `check-receipt` refuses if the canonical
article or bound spec bytes have changed.

An advisory style lint is also available:

```sh
python3 medium_compiler.py style-lint --input /tmp/article-run/medium-canonical.md
```

It flags repeated generic scaffolding such as `本文將` or `前進條件`. Findings are not a
hard correctness gate because those phrases can occasionally be legitimate.

## Spec

A spec binds the topic, article claims that must be accounted for, and technical terms that
must not drift.

```json
{
  "topic": "Example topic",
  "claims": [
    {
      "id": "C1",
      "stage": 1,
      "description": "The source-backed claim rendered in Stage 1",
      "protected_literals": ["exact identifier or number that must survive copyedit"]
    }
  ],
  "terms": [
    {
      "id": "T1",
      "canonical": "canonical key",
      "first_stage": 3,
      "forbidden_variants": ["標準鍵值"]
    }
  ]
}
```

Use `protected_literals` only for exact values, identifiers, quotations within the allowed
quotation policy, versions, or other bytes that truly must survive. Do not freeze whole
sentences merely to make semantic evaluation deterministic.

## Verification boundary

The CLI can prove:

- stages were submitted in the fixed order;
- each stage declared the exact structural elements and claim/term IDs due there;
- forbidden term variants did not enter the draft;
- canonical terms introduced by the spec survive the final prose pass;
- exact protected literals survive;
- fenced code blocks are byte-identical through Stage 6;
- Stage 7 adds no prose because assembly is deterministic;
- the validation receipt names the current canonical/spec bytes.

It cannot prove:

- a claim is factually true;
- the selected invariant is the best one;
- an alternative is pedagogically useful;
- a paragraph preserves meaning merely because IDs were declared;
- a human prefers the prose.

Those remain source review / semantic-eval responsibilities.

## Tests

```sh
python3 -m unittest discover -s tests -v
```

The tests include planted negative controls for skipped stages, dropped coverage, technical
term drift, code-block mutation, protected-literal loss, machine-sidecar leakage and stale
final-byte receipts.
