# Loop Workbench | TanStack Start delivery architecture

Status: design contract and isolated preview scaffold. Not an authorized
production migration, native Agent RL trainer, or cloud-control endpoint.

## Existing source of truth

- Soodles LoopManager owns admission composition and evidence projection, not
  a separate scheduler. Noodle owns the local Host and shared isometric renderer.
- Medium-compiler public importer owns disclosure-reviewed, static v2 graph
  snapshots and content-addressed artifacts. Its current production site still
  uses the existing static build route.
- Original graph v2 objects/nodes/edges/artifacts/findings/metrics and run
  identities are the only inputs for execution visualization. Source labels
  and matching prose do NOT establish causal edges. Cross-repo links need
  observed producer/consumer evidence.
- The UI must never infer semantic consumption, training gain, reward or whole
  goal acceptance from geometry, colors, timestamps or a successful build.

## Selected stack

TanStack Start (React, file-based TanStack Router, Vite, TypeScript) is the
future application shell, not a replacement for the evidence owner. Use
route loaders for read-only public data and typed URL filters, keeping raw
private/native evidence inaccessible. The prototype lives under
apps/loop-workbench, isolated from existing Vercel and Cloudflare builds.
No production routing/deployment changes are part of this slice.

Before a production cutover, pin and review all package-lock entries, run
npm ci, typecheck, SSR/hydration/browser tests, same-origin disclosure
checks and exact-head release acceptance. No npm dependency installation
or hosted browser acceptance has happened in this commit.

## Final product information hierarchy (FineEnvs-inspired)

1. Workspace: Goal, repository/run filter, actual execution topology,
   original Owner boundaries and known causal breaks.
2. Mechanism: source-bound isometric render of one selected Object. Ports,
   tools and visual machinery reference immutable IDs. Visible animation
   means inspection or replay positioning, NOT a native action.
3. Timeline: stage, input representation, action, output, observation,
   review and original successor. Show original content and semantic review
   side-by-side. Distinguish timestamp and causal order.
4. Environment Lab: Task, dataset, available actions, observation contract,
   backend, state, reward/rubric, termination. A saved episode is replayed
   deterministically; unknown reward is null, not zero. No generated synthetic
   reward can be presented as measured feedback.
5. Comparison: baseline/candidate paired replay, immutable oracle,
   protected regressions, decision count, token/tool/latency cost,
   validity & missing evidence. Eligibility and acceptance are separate.
6. Lessons: evidence-supported rework lineage and candidate adoption.
   No visual UI action may automatically promote a patch or update weights.

The reference FineEnvs simulation article describes PortSimEnv, a
deterministic port-berthing simulation using historical cases, events,
one graded submission per episode and a CP-SAT comparison. Borrow the
contract discipline (task/actions/observations/state/reward/termination),
NOT the marine domain, reward function or training claims.

## Visual-design skill routing

Use design/visual-skills.lock.json and loop-visual-design/SKILL.md:
Impeccable leads the operating workspace and responsive system; Emil owns
motion critique. Anatomy is selected for inspectable source-bound
mechanisms. Taste is reserved for an optional public demonstration page.
Never apply all four for every UI change. The build-review-interface skill
supports trace annotation, not runtime auth.

## Authority and future NeoWeaver integration

Read-only cloud: GET reviewed, same-origin, digest-verified assets. No
cloud POST, Host connection, action/probe endpoint, credential access or
unreviewed local paths. A future private experimental application may use
TanStack Start server routes/functions ONLY after per-request authentication,
authorization, CSRF and original Owner approval; do not turn this preview
into that endpoint implicitly.

NeoWeaver's three planes remain independent:
- Learning: propose bounded harness/skill/MCP edits, own lineage.
- Execution: source-pinned, isolated snapshot/replay, original Host effects.
- Verification: original independent oracle and protected regressions.

Harness² offers task-level Propose–Probe–Compose and a separate improvement-
harness recursion with fixed model weights. Map these to NeoWeaver's
PatchProposal, paired replay and lesson artifacts, not to a new permission
system. Training open Solver weights is separately gated and not implied by
Harness² recursion. The bridge schema/entry lives in NeoWeaver.

## Product acceptance

- A selected source id opens the same versioned artifact, without cross-run
  selection races or false causal edges; unknown/not_public contents are clear.
- Paired replay includes genuine same-task/environment/seed/budget controls,
  source-bound reward identity, preserved negative controls and original gates.
- Read-only cloud and zero-effect tests refuse malicious paths, redirects,
  source-provided HTML and attempts to dispatch any tool.
- Minimum tested surfaces: desktop, tablet, mobile, keyboard-only, reduced
  motion; original renderer parity and screenshots from actual browser.
- No demo UI labels count as native end-to-end acceptance.

Source references:
https://tanstack.com/start/latest/docs/framework/react/build-from-scratch
https://tanstack.com/start/latest/docs/framework/react/guide/server-functions
https://github.com/adithya-s-k/FineEnvs
https://huggingface.co/spaces/FineEnvs/simulation-rl-environments
https://github.com/google-research/harness2
