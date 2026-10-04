# Public transcript discovery

Live CLI observations on 2026-10-04, separate from synthetic offline tests:

- `video-search.json`: user-provided YouTube link resolves via the existing caller-supplied association to a live public single-show title search. It returns the requested Alex Atallah / Amjad Masad episode. This is not an audio match claim.
- `topic-search.json`: `Agent 記憶` in Latent Space searches `Agent memory` and returns first-page candidates. Provider order is retained; topical relevance is not independently judged. Captured before the bounded empty-search retry was added; nonempty-search behavior is unchanged.
- `episode-inspect.json`: live source parses to 95 timestamped segments (00:00:00–00:47:58). Only metadata and a fixed short excerpt are public. Raw HTML is not committed.

Public search route and parameter names come from PodScripts' published search UI (`/js/podsearch.js`). Its pricing page explicitly offers single-podcast keyword search for free; the paid mass-search episode results are not accessed. Seven show IDs were read from the public homepage catalog. Each request searches only the selected show, with at most one broader keyword retry if the first search is empty.

Vercel uses the documented `api/*.py` / `BaseHTTPRequestHandler` Python runtime: https://vercel.com/docs/functions/runtimes/python/api-directory . Shared functions in `scripts/transcript_discovery.py` serve both CLI and API. Network targets, redirects, size and timeout are bounded. The client renders provider strings with textContent, cancels stale requests, handles empty/error states, and auto-inspects only the first candidate.

Validation before PR: 179 tests passed; `verify-medium` doctor plus staged-authoring, bounded-revision, lossless-drilldown and delivery passed. No fresh independent writer/reader experiment or learning claim. Matching-head GitHub Actions and deployed route checks are recorded in the PR. Existing article and source receipt files are unchanged.
