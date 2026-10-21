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
