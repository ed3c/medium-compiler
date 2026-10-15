# Public Loop snapshots

The original Loop owner prepares the public projection. Its shape is
[`public-loop-snapshot.schema.json`](../../contracts/public-loop-snapshot.schema.json).
The owner supplies observed state, display-only source references and a plain-text
next-step description. This renderer does not inspect private receipts or infer
execution, acceptance, permission or missing values.

After the projection is reviewed for public disclosure, add its repository-relative
`path` and SHA-256 to `catalog.json` under `snapshots`. The existing site build checks
those exact bytes and renders each run at `/loops/<id>/`. Only catalog-listed files
are consumed. The catalog initially contains no runs. Public source changes require
updating the catalog digest with the reviewed snapshot.

All supplied text is HTML-escaped. References and next steps are plain text, with
no execution controls or source-supplied links. The renderer rejects unknown fields,
known local-path forms and recognizable credential patterns. These checks cannot
recognize every possible secret in free text; the original owner's public projection
and disclosure review remain necessary. Do not include environment dumps, raw
receipts, private prompts, credentials or absolute local paths.

The builder records each route, snapshot digest, repository, mode and observed status
under `loops` in `/provenance.json`. It does not publish raw snapshots. Build and Git
deployment use the existing medium-compiler owners. Reading a page does not run or
resume a Loop. Native acceptance and deployment readback remain separate observations.
