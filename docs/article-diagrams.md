# Build-time diagrams: source-bound and read-only

This is an authoring/rendering feature, **not** a second article Content Owner
or a source of Soodles/Noodle runtime evidence.

The canonical article Markdown remains the Source of Truth.
For registered fenced Mermaid blocks, the build substitutes an approved,
content-addressed SVG image. The registry binds the exact Mermaid block
(index and SHA-256), SVG bytes, and human-reviewed alt text. An unregistered
or changed block inside a registered article fails the build.

Normal articles and ALG Four's source-locked annotation pipeline are unchanged.
SVGs are displayed through IMG (not injected as active inline HTML). The
asset verifier refuses scripts, external resources, unsafe tags and digest
changes. The production build does not download packages or invoke a model.

Future authoring can use the MIT-licensed beautiful-mermaid renderer to create
SVG candidates; candidates must be reviewed and committed with registry
entries before publish. Do not silently fall back to a different engine,
rewrite the article, fabricate runtime evidence, or turn an infographic into a
causal DAG.

Acceptance layers: source registry and negative controls; real article
build and SVG asset; desktop/mobile browser screenshot and accessibility;
independent reader comprehension is NOT_OBSERVED. Performance numbers
must come from measured fixture distributions, not marketing claims.

## Candidate authoring engine

The MIT-licensed beautiful-mermaid `1.1.3` package is an isolated authoring dependency in `tools/article-diagrams`, not a runtime site dependency. Install locally within that directory and run `node tools/article-diagrams/render.mjs articles/example.md 0 "Description"` from the repository root. A new SVG is content-addressed and registered as `reviewed: false`; source-fidelity review, actual browser output inspection, accessibility, and promotion to `reviewed: true` are mandatory before the build will publish it. The CI smoke tests one real SVG conversion and reports its elapsed time without inventing P95 metrics.
