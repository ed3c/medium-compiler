# Loop Workbench (isolated TanStack Start preview)

This is a source-bound UI scaffold, **not** a deployment migration or a
new LoopManager / Agent RL execution route. The existing medium-compiler
production site remains unchanged.

- npm install (freeze generated lockfile before making this a CI dependency)
- npm test
- npm run typecheck
- npm run dev
- Visit / for an empty truthful readout. Add a URL search parameter
  manifest=/assets/loop-data/<64 lowercase hex digest>/graph.json only
  for an owner-reviewed, same-origin snapshot already served by the host.

No sample runs, synthetic PASS, scalar reward, Host RPC or write APIs are
included. Current isometric cubes are **visual index affordances**, not the
canonical Noodle mechanism geometry. The pinned Noodle canonical `/panorama` renderer is integrated for source-only
inspection and has a Chromium fixture smoke test. Actual native task readback,
original run acceptance and Production promotion remain **NOT_RUN**.

Component outline:
- TanStack Start root / route + URL state
- Pure v2 public graph projection with Node tests
- Source-identity-aware node/edge inspection
- FineEnvs-style environment model placeholders for the future NeoWeaver
  adapter and paired replay UI; never infer a reward from missing data

Security: browser only fetches same-origin, strict content-addressed
public graph JSON. It cannot fetch arbitrary remote URLs, SSR private files,
or dispatch original Owner effects. The reviewed static publisher remains authoritative. `src/public-artifact.mjs`
verifies the exact public artifact URL, byte count and SHA-256 before revealing
text to the original Noodle inspector. A manifest URL alone is never a
native observation or an authorization receipt.

## Visualization extension, VIZ-01–04

See ../../docs/visualization-integration.md. Noodle remains the canonical geometry/evidence graph producer. Public artifact payloads are resolved through the digest-bound `src/public-artifact.mjs` reader only. No live Host or production deployment is implied.


## Local Learning Lab (VIS-12–14 A)

The isolated preview route /learning uses a pinned DuckDB-Wasm OPFS file for local learning drafts, with export/import JSON and exported DuckDB snapshot for optional native CLI Agent Mode. Source: docs/learning-duckdb-architecture.md. Python Run is deliberately unavailable until a dedicated-origin, no-network, bounded Pyodide Sandbox passes its own acceptance. Local attempt records do not represent native task receipts, and this preview is not deployed on Production.

For the cross-domain source/renderer/consumer matrix and honest acceptance map, see [Unified Visual Architecture](../../docs/visual-architecture.md). ARC-02 A limits new OMM architecture analysis to medium-compiler; no actual reviewed repo scan has occurred in this slice.
