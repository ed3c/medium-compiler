# Loop Studio — source-bound design pipeline (2026-10-18)

## Existing source and ownership
- Runtime: Soodles \`contracts/loop-interface.md\`, \`loop_graph.py\`, and \`contracts/loop-view-v2.md\`.
- Local display: Noodle \`/loops\` original Host readback, review selection and Session feedback; no browser authority to invoke a task.
- Public display: medium-compiler \`scripts/import_loop_snapshot.py\`, \`scripts/loop_graph_site.py\`, \`site/loop-*.mjs\`; importer requires an owner-reviewed snapshot and public content hashes.
- Noodle's latest focused local work in PR #118 is not identical to medium-compiler's public renderer, and cloud PR #70 was still draft when this contract was authored. Do not advertise parity or production deployment without fresh source/browser readback.

## Design product — immutable inputs, explicit transformations
\`\`\`text
Owner source / source versions / original Contract
    -> LoopManager Original Admission + readback (no UI permission)
    -> Loop v2 Graph {repositories, objects, ports, nodes, edges, artifacts, findings, metrics}
    -> Disclosure review (for cloud) -> verified public snapshot + catalog
    -> View IR (selected run, causal edges, owner capability, evidence statuses)
    -> Design Brief (problem/mode/selected skill/interaction)
    -> TanStack Start React route + shared projector/isometric SVG (presentation only)
    -> Browser capture + Test Manager verification + source-bound UI artifact
\`\`\`
The View IR may *select and explain* existing source IDs. It cannot add a causal edge, operation, result, reward, or executable next. Keep original producer and consumer reference identities. Existing \`site/loop-graph-layout.mjs\` and \`site/loop-panorama.mjs\` logic remain the reference projection through migration.

### Required view semantics
- **Architecture**: one unique Owner object with capabilities/ports, plus Run-scoped occurrences; capability does not imply invocation.
- **Actual**: current observed handoffs only if both endpoints, input/output, evidence and Owner conditions match. Observed failure stays a red finding and retains history.
- **Expected**: source-backed contract steps (solid amber); hypotheses (dashed amber) only with known endpoints; unknown hypothesis has no drawn edge.
- **Inspector**: synchronized selected Run, origin references, schema/role, before/after content, original Owner next as inert JSON; missing public content displays UNKNOWN, never silently fetches private Host paths.
- **Counters**: denominators from Owner observation only; no fabricated success rate; no progress inferred from animation.
- **Action labels**: local “Hand off to Session” requires original Host review-selection custody and authorized Session call. Cloud offers no task action.
- **Accessibility**: keyboard traversal/focus, scalable SVG, touch/mobile stacked inspector, reduced-motion variant and readable light panels; hide no failure to simplify aesthetics.

## TanStack Start React adoption boundary
Target **new, isolated** \`apps/loop-studio\` frontend using official file-based routes and TypeScript. Propose \`/loops\` (overview), \`/loops/$runId\` (inspector), and \`/experiments/$experimentId\` (future RL read-only telemetry). Create with the official TanStack CLI on a host with package-network access. Do not replace existing site routes or deployment owner until the new build and UI have parity acceptance.

- Loaders: public same-origin *digest-checked* snapshot/assets only. Source data comes from the existing public exporter; route params may select only catalog-backed IDs. No server function can read local Noodle Host receipts or privileged/private files.
- UI: React shells may consume the existing framework-independent projector and isometric SVG via a thin adapter; don't fork causal reduction. Keep bundle/budget measured.
- Distinguish static public site hosting from owner-authenticated local reviewer endpoints. Do not expose a TanStack mutation action, a local proxy, arbitrary filesystem path, SSR secret, generic URL fetch, or tool invocation through a public route.
- A build is **not** a deployment; a deployment is **not** native Agent/semantic acceptance. Migrate one route behind an independent preview first. Record exact source revision, UI bundle and browser proof before changing main-site routing.

## Skill routing / install contract
\`build-review-interface\` already exists in this repo for annotation; it does **not** certify an observed Loop invocation. New optional pinned project-local skills: Anatomy for source-linked physical metaphors; Impeccable for operate/read design and audit; Emil's individual skills for motion and component interaction; Taste for public story/landing pages only. Select a single primary skill per output. Do not run every Skill, let the external Skill rewrite AGENTS, or let Skill instructions change graph validation, source authority, evaluation outcomes or browser network access.

\`python3 scripts/install_loop_design_skills.py --plan\` is safe without network. \`--install\` clones **exact commits** from the lock into project-local \`.agents/skills\`; it does not execute downloaded binaries, npm installers or instruction payloads. Use reviewed explicit updates for newer commits; runtime skill activation must be checked separately. Current cloud Session cannot install into the user's Mac through GitHub.

## Final design artifact (not task authority)
\`contracts/loop-ui-artifact-v1.schema.json\` defines \`LoopUIArtifactV1\` — source sha/visibility, selected mode and Skill pin, view IDs and artifact references, observed/unknown/failure states, actual browser/method/native-consumer check results, and **four always-false authority fields**. Native Evals and protected Oracle results stay with their original owners. Persist design artifact only with an original source revision. An artifact may be source-only; don't call a design concept a finished web page.

## NeoWeaver / Harness² / RL readiness: reserved, not connected
The future \`ExperimentView\` reads **only** an independently accepted \`EpisodeView\` sidecar:
\`environment_ref, episode_id, reset_ref, ordered (observation_ref, action_ref, step_receipt_ref), terminal_ref, verifier_ref, reward_ref, dataset_partition, policy_ref, harness_ref, rights_ref, knownness\`.
No adapter invents these references or turns a model transcript into a verified environment step. Keep two existing roles separate:

1. Harness²: task-level **Propose–Probe–Compose** plus harnessing-level persistent improvement; eight edit surfaces (system prompt, guardrails, memory, tool guidance, subagents, skills, scripts, plugins). It can propose harness changes but does not imply training model weights or RL reward.
2. FineEnvs: select environment interface (OpenEnv, OpenReward/ORS, Verifiers, NeMo Gym) according to original Reset/Step/Verify/reward owner. Training, evaluation and deployment remain separate. Exact environment state transitions, terminal reward source, delayed effects, seeds and data rights require observed adapters.

NeoWeaver's existing \`learned-harness-coevolution.md\` ten REQ, frozen Codex boundary, immutable verifiers, train/validation/held-out and source-bound permissions remain original. "Seamless" means a typed export/import **after** adapter and held-out proof; no new scheduler, CLI prediction of unknown IDs, Agent self-issued PASS, or automatic RL training.

## Verifiable checkpoints
1. Installer plan works offline; pins and paths are checked; any partial/missing install reports NOT_RUN.
2. Current public graph snapshot still validates; missing content, stale version, failed/unknown edge, and repeated import remain faithful.
3. TanStack prototype compiles with an explicitly pinned toolchain and browser checks at wide/narrow widths, keyboard, \`prefers-reduced-motion\`, exact-content comparison and source drift. **NOT_RUN** until implemented.
4. Local Host review-selection and original Session feedback exercised on an authorized existing Run; cloud page cannot perform either effect.
5. Harness² and RL adapters tested with a disposable known-episode replay and protected negative, then paired/held-out evaluation before any claim of learned improvement.

References: https://tanstack.com/start/latest/docs/framework/react/build-from-scratch ; https://github.com/google-research/harness2 ; https://github.com/adithya-s-k/FineEnvs ; https://huggingface.co/spaces/FineEnvs/simulation-rl-environments (requested design reference; direct read unavailable in this review).
