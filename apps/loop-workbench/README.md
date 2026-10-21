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
canonical Noodle mechanism geometry. The native renderer and its source
identity must be integrated and browser-verified before product acceptance.

Component outline:
- TanStack Start root / route + URL state
- Pure v2 public graph projection with Node tests
- Source-identity-aware node/edge inspection
- FineEnvs-style environment model placeholders for the future NeoWeaver
  adapter and paired replay UI; never infer a reward from missing data

Security: browser only fetches same-origin, strict content-addressed
public graph JSON. It cannot fetch arbitrary remote URLs, SSR private files,
or dispatch original Owner effects. Do not assume the manifest itself
certifies upstream artifact body digests; the eventual static importer
remains authoritative and the browser content reader must verify each
public artifact's digest before exposing its text.

## Visualization extension, VIZ-01–04

See ../../docs/visualization-integration.md. Noodle remains the canonical geometry/evidence graph producer. Public artifact payloads are resolved through the digest-bound `src/public-artifact.mjs` reader only. No live Host or production deployment is implied.
