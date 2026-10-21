# Medium Compiler Handoff | Source-bound Visual + Modular Migration

> **Next conversation's parent Goal:** Finish the previously selected medium-compiler paper/teaching/code/evals/visual/Agent-evidence integrations using **Soodles migrate-class** (AST/code-intel → preserve original modules → minimum adapter → independent consumer parity) while respecting the original Soodles Outer / Noodle Poteto Inner admission and each independent Owner. This is a **phased product/integration workstream**, not permission to recreate the product, merge PRs or deploy Production.

Date: 2026-10-21 (Asia/Taipei). Authoritative current state is the **fresh GitHub/Owner readback**, not this handoff's historical refs.

## 1. Current branches, source and verification

| Repository | Working PR and Head at handoff | Scope |
| --- | --- | --- |
| [medium-compiler](https://github.com/ed3c/medium-compiler/pull/72) | **#72** Open Draft, `836f6886898c40a4266b24bed69a3892877ab6c9`, branch `codex/loop-workbench-tanstack-visual-skills` | **Single writable target** of the first selected visual integration task. This handoff commit advances the PR Head; refresh before next action. |
| [Soodles migrate-class](https://github.com/ed3c/soodles/pull/444) | **#444** Open Draft, `287e03fd052381b0c5909ebff0b9819dfab2e3ed`, branch `codex/migrate-class-source-bound-parity` | Read-only method/source reference. It is not yet part of Soodles main; don't pretend a fresh Session loaded the skill. |

Selected historical provider observations (not outcomes for this handoff commit):
- medium-compiler [Loop Workbench Contract 39569797506](https://github.com/ed3c/medium-compiler/actions/runs/39569797506) **SUCCESS** at the recorded PR #72 head. Source-only fresh Chromium AIFS direct vs iframe behavior for 3 Math/Demo figures and SeeCode standalone vs sandboxed consumer for 4 nodes / 3 edges; a planted dropped edge was rejected. **This is bounded SOURCE_BROWSER_DIFFERENTIAL_PASS, not universal equivalence or Native Agent Success.**
- medium-compiler [Writing Verification 39569796739](https://github.com/ed3c/medium-compiler/actions/runs/39569796739) **SUCCESS** at the preceding PR Head: original writing/build and ALG Four tests.
- Soodles [runtime 39570046404](https://github.com/ed3c/soodles/actions/runs/39570046404) **SUCCESS** at the noted Soodles Head. Original Test Manager classified **SOURCE_CI_ONLY**; it did not run original Issue Admission/Noodle Writer/native P-class/Provider Landing.

**No merge/main readback or Cloudflare/Vercel Production deployment was performed.** On new sessions, query each live PR/Head, main, check run+attempt and selected tests before using these historical results.

## 2. All frozen decisions (do not repeat scope questions)

- **ViewEnv Q1–Q36** remain valid, including Source-based Noodle Panorama, green only for *observed* handoff, yellow expected/falsifiable contracts, red failed findings and distinct UNKNOWN. No extra Graph Truth Owner or public Host effect API.
- **VIZ-01 A / 02 A / 03 A / 04 A:** Graph→Evidence→Article with separate acceptance; reviewed Static Snapshot and Recorded Replay, not an Event Bus; canonical Markdown/Mermaid to reviewed build-time SVG without rewriting the article or ALG Four; continue existing PR #72.
- **VIS-06 B / 07 B / 08 A / 09 A / 10 A / 11 A:** Full learning platform goal, real browser Pyodide as planned runner, Typed Code Explorer, Claim→Method→Trace→Metric evidence-first articles, Paper Reader and rights-reviewed source-bound figures (PaperBanana only research), Anthropic HTML editorial + explorable figures + canonical runtime renderer.
- **VIS-12 A / 13 A / 14 A:** Local-first learning, restricted untrusted Python runner, *browser-untrusted* grader; **DuckDB-Wasm + OPFS** replaces IndexedDB-primary. Native DuckDB 2.x Agent Mode CLI remains an *optional separate read-only* consumer of an explicitly exported file, not the browser engine.
- **VIS-15 A / 16 A / 17 A:** Explicit SeeCode and oh-my-mermaid source exceptions to earlier OpenAI/Anthropic/Cursor-author preference. SeeCode is Editorial/Teaching Renderer only (interactive HTML isolated, approved SVG static). OMM creates review-gated, versioned **derived** architecture knowledge with no Cloud Push.
- **ARC-01 A / ARC-02 A:** Unified Visual Router and original Owner/Consumer/Acceptance matrix, phased functional delivery; **medium-compiler is the sole initial OMM source-scan target**, no unsanctioned cross-repo scan.
- **MIG-01 A / 02 A / 03 A:** Precise selected-module migration, immutable vendor + thin adapter, actual language-specific **AST/code-intel** prior to every *actual* upstream integration. Reference-only libraries do not need arbitrary full AST indexing.
- **MGC-01 A / 02 A / 03 A / 04 A:** Soodles `migrate-class` engineering Skill, not new P-class/CLI life cycle; Consumer-observable parity with only Owner-authorized normalization; multi-source read/**single-target write**; two-source AIFS + SeeCode fresh differential pilot.

The next Session may follow valid original Owner continuations without another planning loop. Thinking Router V2 is default; use V3 + Ambitious only when a new falsifiable premise actually changes implementation/verification; otherwise `PromptDelta=NOOP`. Do not infer permission for unrelated repos or broaden ARC-01 A into a rewrite-everything sprint.

## 3. Existing architecture: read these sources, not a repeated summary

- [Single Visual Architecture/Owner matrix](visual-architecture.md): paper, teaching, code, Evals, architecture, Noodle Graph, DuckDB and distinct verification oracles.
- [Existing visualization history/contracts](visualization-integration.md), [Panorama](viewenv-unified-panorama.md), [reviewed Graph snapshots](public-loop-graph.md); `apps/loop-workbench/src/routes/panorama.tsx`, `src/public-artifact.mjs`, `vendor/noodle/loop-panorama.mjs`.
- [Diagram authoring & OMM review rules](diagram-authoring.md), `design/diagram-authoring.lock.json`, `design/diagram-candidates/manifest.json` (currently **0 reviewed**), `references/article-diagrams.json` (**0 promoted figures**), [article SVG contract](article-diagrams.md), `tools/article-diagrams`.
- [Cross-repo TypeScript 7 / Bun / TanStack / tsrs workbench](ts7-bun-tanstack-tsrs.md) and [Cloudflare tsrs faithful-port method](typescript-rust-port-integration.md). The isolated Workbench now uses native TS7.0.2 for typecheck + TS6 Compiler JS API for code-intel + Bun 1.4.3 as a secondary runtime + isolated tsrs 7.1-dev WASM diagnostic tests. TS7.1-dev is **not** a matching compiler for TS7.0 native parity.
- [AIFS precise modular source integration](aifs-modular-migration.md), `references/aifs-figure-vendor.json`; `apps/loop-workbench/public/aifs/` holds **exact MIT upstream source modules** and LICENSE at revision `45fa4084de6ba2f88fa96a41e69efa2166f868b3`. `apps/loop-workbench/scripts/aifs-code-intel.mjs` uses TS AST; `src/routes/figures.tsx` hosts a sandbox. SeeCode source pinned at `067ca2594e8e8ec87e7bcd14e9dcf7549f0f9913`, OMM at `38ccdb69298adec949177c92c88d6e3ddfb5bab7`.
- [DuckDB learning architecture](learning-duckdb-architecture.md); `apps/loop-workbench/src/routes/learning.tsx` + `learning-store.ts`, `scripts/learning_duckdb_agent.py`.
- Original [medium-compiler AGENTS.md](../AGENTS.md), original `docs/loop-entry.md`, [Soodles state-machine change application](state-machine-change.md), `.agents/skills/medium-writing/SKILL.md`, `.agents/skills/verify-learning-article/SKILL.md`. Never mutate original source-locked accepted article/ALG Four content.
- Soodles [migrate-class Skill on PR #444](https://github.com/ed3c/soodles/blob/codex/migrate-class-source-bound-parity/.agents/skills/migrate-class/SKILL.md), [method](https://github.com/ed3c/soodles/blob/codex/migrate-class-source-bound-parity/.agents/skills/migrate-class/references/method.md), [two-source pilot](https://github.com/ed3c/soodles/blob/codex/migrate-class-source-bound-parity/.agents/skills/migrate-class/references/aifs-seecode-pilot.md), [Thinking Router](https://github.com/ed3c/soodles/blob/main/.agents/skills/thinking-router/SKILL.md), [Code-intel](https://github.com/ed3c/soodles/blob/main/.agents/skills/code-intel/SKILL.md) and Test Manager.

The **OpenAI, Anthropic, Cursor examples** provide design/test methods, not blanket approvals to install runtime packages. SeeCode/OMM and AIFS are explicitly selected and source-pinned. PaperBanana and distill-figure remain research/method references. Additional tools require specific AST/rights/runtime review before actual migration.

## 3A. Resource Registry — websites, upstream code, Skills and migration methods

**Scope of this registry:** All concrete websites and public source repositories discussed/selected in this conversation, rather than a vague "OpenAI/Anthropic/Cursor examples" label. Links point to the **original project or primary source**. Integration decisions, actual copied bytes and acceptance remain governed by the locked manifests and documents in section 3. The items below are **not automatically authorized dependencies**.

**Status vocabulary:** `INTEGRATED/TESTED` = actual selected target source or Chromium evidence; `PINNED/DESIGN-TIME` = immutable original Skill/CLI sources available for controlled design use, not automatically a native invocation; `DESIGN REFERENCE` = useful specific upstream UI or method but not copied into the target; `RESEARCH/DEFERRED` = studied or proposed, not approved or installed for product runtime.

### A. Website examples and concrete design patterns

| Primary public site / source | Exact method/pattern wanted in medium-compiler | Status |
| --- | --- | --- |
| [AI Engineering from Scratch](https://aiengineeringfromscratch.com/) · [original MIT repository](https://github.com/rohitg00/ai-engineering-from-scratch) | Course lesson structure, re-computed Math/ML figures, reusable `window.LF` widget runtime, Build/quiz/progress examples. **Only three source-preserved JS figure modules** are currently imported; not the full website. | INTEGRATED/TESTED selected figures |
| [Anthropic HTML Effectiveness](https://github.com/anthropics/html-effectiveness) — [04 Code Understanding](https://github.com/anthropics/html-effectiveness/blob/main/04-code-understanding.html), [10 SVG Illustrations](https://github.com/anthropics/html-effectiveness/blob/main/10-svg-illustrations.html), [12 Incident Report](https://github.com/anthropics/html-effectiveness/blob/main/12-incident-report.html), [13 Flowchart Diagram](https://github.com/anthropics/html-effectiveness/blob/main/13-flowchart-diagram.html), [14 Research Feature Explainer](https://github.com/anthropics/html-effectiveness/blob/main/14-research-feature-explainer.html), [15 Research Concept Explainer](https://github.com/anthropics/html-effectiveness/blob/main/15-research-concept-explainer.html) | HTML-first editorial hierarchy, code navigation, research explainer, readable graphics and incident timelines; **design reference, not a copied Anthropic UI runtime**. | DESIGN REFERENCE |
| [Deep-ML problemset](https://www.deep-ml.com/problems) | Topic-based ML problemset, Python solutions, visible test feedback, progress. The original challenges are not source assets licensed for reuse by this record. | DESIGN REFERENCE |
| [TrenTorch Problemset](https://trentorch.com/problemset) | ML/Math problem categories, real code execution and progression; compare UX and grader behavior, do not copy proprietary problem content. | DESIGN REFERENCE |
| [David Blass technical site](https://ssalbdivad.com/) | Typed Code Explorer / TypeScript/validator explanation and code-navigation inspiration. | DESIGN REFERENCE |
| [Rohit Ghumare — Evals and Benchmarks](https://rohitghumare.com/guides/evals/) | Evidence-first writing, evaluator calibration, failure analysis, Trace/Metric/Counterexample explanation. | DESIGN REFERENCE |
| [Distill](https://distill.pub/) | Explorable Explanations, linked math/graphics, reader-operated recalculation and direct causal explanation. | DESIGN REFERENCE |

### B. Selected implementation stack and exactly adopted upstream modules

| Repository/primary source | Target role, binding and adoption limit |
| --- | --- |
| [TanStack Router / Start](https://github.com/TanStack/router) | Isolated React/TypeScript `apps/loop-workbench` app; not a replacement for the original static Cloudflare/Vercel article builder. `INTEGRATED/TESTED`. |
| Soodles/Noodle canonical renderer — see `apps/loop-workbench/vendor/noodle/loop-panorama.mjs` and [Graph v2 public contract](public-loop-graph.md) | Actual Agent/Replay display only from owner-reviewed data; no second owner, graph edges, or Host API. `INTEGRATED` browser projection; fresh native Agent result `NOT_RUN`. |
| [AIFS repository](https://github.com/rohitg00/ai-engineering-from-scratch) pinned `45fa4084de6ba2f88fa96a41e69efa2166f868b3` — [LF runtime](https://github.com/rohitg00/ai-engineering-from-scratch/blob/45fa4084de6ba2f88fa96a41e69efa2166f868b3/site/lesson-figures.js), [math providers](https://github.com/rohitg00/ai-engineering-from-scratch/blob/45fa4084de6ba2f88fa96a41e69efa2166f868b3/site/figures-math.js), [demo-token-bucket provider](https://github.com/rohitg00/ai-engineering-from-scratch/blob/45fa4084de6ba2f88fa96a41e69efa2166f868b3/site/figures-demo.js) | **Byte-identical vendor** in `apps/loop-workbench/public/aifs/` and thin sandboxed React `/figures`. Three visual examples tested; upstream MIT LICENSE preserved. `INTEGRATED/TESTED`. |
| [SeeCode](https://github.com/Aryanutkarsh/SeeCode) pinned `067ca2594e8e8ec87e7bcd14e9dcf7549f0f9913` | JSON Spec → editorial standalone HTML, SVG candidate, step/node inspector; repo-local pinned Skill plus genuine CLI/Chromium and source-to-sandbox Figure differential. **Not** Native Graph Renderer. `PINNED/DESIGN-TIME + TESTED FIXTURE`. |
| [oh-my-mermaid](https://github.com/oh-my-mermaid/oh-my-mermaid) pinned `38ccdb69298adec949177c92c88d6e3ddfb5bab7` | `omm-scan` and `omm-view` Skills only; inferred, versioned Codebase Architecture Knowledge. `omm-push` excluded. **Actual medium-compiler source scan and independent diagram review NOT_RUN**. `PINNED/DESIGN-TIME`. |
| [beautiful-mermaid](https://github.com/lukilabs/beautiful-mermaid) | MIT renderer (selected authoring package 1.1.3) for source-bound, reviewed build-time Mermaid→SVG; not runtime authority. Source-to-SVG fixture tests exist, **zero newly promoted article figures**. `INTEGRATED authoring`. |
| [DuckDB-Wasm](https://github.com/duckdb/duckdb-wasm) + [DuckDB CLI Agent Mode announcement, 2026-10-09](https://duckdb.org/2026/10/09/agent-mode) | DuckDB-Wasm 1.32.0 + OPFS = **local untrusted learner state**, with Chromium write/reopen/export evidence. **CLI Agent Mode is a separate optional read-only SQL-output interface**, not a browser autonomous Agent/grader; actual CLI v2 execution remains NOT_RUN. |
| [Pyodide](https://github.com/pyodide/pyodide) | Selected real Browser Python Runner direction (VIS-07 B). Bounded sandbox, no network, grading semantics and security **NOT_ACCEPTED/NOT_IMPLEMENTED**; not an installed production grading system. |

### C. Pinned design-Skill sources and OpenAI/Anthropic/Cursor sources

| Public source | Intended responsibility, NOT an independent Owner |
| --- | --- |
| [Taste Skill](https://github.com/Leonxlnx/taste-skill), lock `f624f37a8c650b9cc550253104925efe4c8de246` (MIT) | Public editorial art direction, **PINNED/DESIGN-TIME** in `design/visual-skills.lock.json`. |
| [Anatomy](https://github.com/wheresryan22/anatomy) / [demo](https://skills.wheresryan.sh/anatomy), lock `e9488296a44211c42701ff71705b7901470ec78f` (MIT) | Source-grounded machine anatomy and isometric illustration, **PINNED/DESIGN-TIME**. |
| [Impeccable](https://github.com/pbakaus/impeccable), lock `9304afa97f89b30609e4c538584fb3e0cd4df013` (Apache-2.0) | Operations/dashboard UX, legibility and accessibility, **PINNED/DESIGN-TIME**. |
| [Emil Kowalski Skills](https://github.com/emilkowalski/skills), lock `2d228630ba1446365f614a108cb8252f1feda202` (MIT) | Motion, animations and interaction audit, **PINNED/DESIGN-TIME**. |
| [OpenAI build-web-data-visualization Skills](https://github.com/openai/plugins/tree/main/plugins/build-web-data-visualization/skills): [strategy and critique](https://github.com/openai/plugins/blob/main/plugins/build-web-data-visualization/skills/visualization-strategy-and-critique/SKILL.md), [node-link & diagram layout](https://github.com/openai/plugins/blob/main/plugins/build-web-data-visualization/skills/node-link-and-diagram-layout/SKILL.md), [testing data visualizations](https://github.com/openai/plugins/blob/main/plugins/build-web-data-visualization/skills/testing-data-visualizations/SKILL.md), [UML/software architecture](https://github.com/openai/plugins/tree/main/plugins/build-web-data-visualization/skills/uml-and-software-architecture-visualization) | Choosing chart/layout, Graph/DAG node-link readability and real visual regression/testing. **REFERENCE only; no global OpenAI visualization runtime installed**. |
| [OpenAI Codex Mermaid renderer](https://github.com/openai/codex/tree/main/codex-rs/mermaid) | Rust Mermaid rendering reference, not selected as website build renderer. |
| [Anthropic frontend-design](https://github.com/anthropics/skills/tree/main/skills/frontend-design) / [web-artifacts-builder](https://github.com/anthropics/skills/tree/main/skills/web-artifacts-builder) | Editorial typography, components and interactive web-Artifact method. **REFERENCE**, not target dependencies. |
| [Cursor pstack / teach](https://github.com/cursor/plugins/blob/main/pstack/skills/teach/SKILL.md) / [docs-canvas](https://github.com/cursor/plugins/blob/main/docs-canvas/skills/docs-canvas/SKILL.md) | Progressive visual explanation and architecture documentation examples. Canvas SDK availability/license is **not** treated as a full open-source distributable renderer. **REFERENCE only**. |

Source attribution boundary: OpenAI/Anthropic official repository links and Sasha Rush/Cursor-associated individual work below are different authorship categories. **AIFS, SeeCode and oh-my-mermaid are explicit later user-selected exceptions**; do not claim they were written by OpenAI/Anthropic/Cursor employees.

### D. Research, figure and ML teaching sources evaluated

| Source URL | Practical pattern | Status |
| --- | --- | --- |
| [distill-figure](https://github.com/unumbrela/distill-figure) | Linked Graph/Matrix, user-driven math re-computation and render/screenshot/probe workflow | RESEARCH/METHOD, not chosen as global runtime |
| [PaperBanana](https://github.com/dwzhu-pku/PaperBanana) / [paper arXiv:2601.23265](https://arxiv.org/abs/2601.23265) | Multi-agent planning/critique of paper methodology and plots, source-bound figure candidate | RESEARCH ONLY; academic figure/asset rights checked separately |
| [Sasha Rush / pydiagrams](https://github.com/srush/pydiagrams) | Chalk-style declarative Python geometry and research diagrams | DESIGN REFERENCE (individual author, MIT repo); not production engine |
| [Sasha Rush / Tensor Puzzles](https://github.com/srush/Tensor-Puzzles) | True tensor operations and original explainable ML exercises | TEACHING REFERENCE |
| [Sasha Rush / Transformer Puzzles](https://github.com/srush/transformer-puzzles) | Attention and Transformer operations as explorable puzzles | TEACHING REFERENCE |
| [Annotated Transformer](https://github.com/harvardnlp/annotated-transformer) | Authoritative paper-to-Python-to-HTML engineering explanation | TEACHING REFERENCE |
| [AIFS authoring sources: blueprint-figure](https://github.com/rohitg00/ai-engineering-from-scratch/tree/main/skills/blueprint-figure), [motion-figure](https://github.com/rohitg00/ai-engineering-from-scratch/tree/main/skills/motion-figure), [course-guide](https://github.com/rohitg00/ai-engineering-from-scratch/tree/main/skills/course-guide), [lesson template](https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/LESSON_TEMPLATE.md), [site/build.js](https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/site/build.js) | Source-bound blueprint visuals, JS widgets, `figure` fence/registry, course metadata and lesson build. **Method/reference for selecting new modules**, not a full course copy. Existing old Skill curriculum count vs live website count is source drift; don't overwrite learner progress to "fix" it. |

**Explicitly compared but NOT selected as whole-platform replacement:** [Observable Framework](https://github.com/observablehq/framework) (publication/build shell), [Mafs](https://github.com/stevenpetryk/mafs) (React math), [UW Mosaic](https://github.com/uwdata/mosaic) (DuckDB linked analytics), [AntV Infographic](https://github.com/antvis/Infographic) (infographics), [Evidence](https://github.com/evidence-dev/evidence) (Markdown+SQL), [Vega-Lite](https://github.com/vega/vega-lite) (stat charts), [Sandpack](https://github.com/codesandbox/sandpack) (JavaScript playground), [JupyterLite](https://github.com/jupyterlite/jupyterlite) (browser notebooks), [Idyll](https://github.com/idyll-lang/idyll) (interactive essays). Their useful methods can be reconsidered per Consumer after Code-intel/rights checks; do **not** install all packages or replace the existing TanStack/static site architecture.

### E. The migration engineering method sources (not just visual libraries)

| Original source | Selected, measurable responsibility |
| --- | --- |
| [Soodles migrate-class](https://github.com/ed3c/soodles/blob/codex/migrate-class-source-bound-parity/.agents/skills/migrate-class/SKILL.md) · [method](https://github.com/ed3c/soodles/blob/codex/migrate-class-source-bound-parity/.agents/skills/migrate-class/references/method.md) | **Primary method Owner as a Skill**: reuse target → immutable vendor → codemod → minimal adapter → required rewrite; **not** a new execution/acceptance Owner. |
| [Soodles Thinking Router](https://github.com/ed3c/soodles/blob/main/.agents/skills/thinking-router/SKILL.md), [Ambitious Route](https://github.com/ed3c/soodles/blob/main/.agents/skills/ambitious-route/SKILL.md), [Code-intel](https://github.com/ed3c/soodles/blob/main/.agents/skills/code-intel/SKILL.md), [Test Manager](https://github.com/ed3c/soodles/blob/main/.agents/skills/test-manager/SKILL.md), [handoff](https://github.com/ed3c/soodles/blob/main/.agents/skills/handoff/SKILL.md) | Existing Outer cognitive selection, independently grounded Python structural index, authoritative test scope and manual transfer. Original Noodle Poteto remains the only selected Inner writer. |
| [Martin Fowler / Refactoring](https://refactoring.com/) | Behavior-preserving restructuring and tests that distinguish externally observable changes. |
| [Tree-sitter](https://github.com/tree-sitter/tree-sitter) | Incremental mixed-language syntax trees / structural navigation; **not** a proven semantic dependency graph. |
| [ast-grep](https://github.com/ast-grep/ast-grep) | Structural search and bounded declarative rewriting. |
| [jscodeshift](https://github.com/facebook/jscodeshift) / [Recast](https://github.com/benjamn/recast) | JavaScript/TypeScript codemod and source-format-preserving AST generation. |
| [OpenRewrite](https://github.com/openrewrite/rewrite) | Typed recipe-based mass migration, especially for compatible Java/API ecosystems. |
| [Comby](https://github.com/comby-tools/comby) | Structural text replacement when a language-specific AST recipe is not necessary. |
| [ApprovalTests Python](https://github.com/approvals/ApprovalTests.Python) | Golden Master / observed output snapshot; reviewer must not silently adopt new output as truth. |
| [Pact](https://docs.pact.io/) / [Pact JS](https://github.com/pact-foundation/pact-js) | Consumer-driven API/message contract tests. Review the chosen SDK's exact license and real provider verification separately. |
| [Cloudflare tsrs announcement (2026-10-20)](https://blog.cloudflare.com/typescript-rust-port/) · [oxc-project/tsrs](https://github.com/oxc-project/tsrs) at `0341578031c47ecf555a35492554b4d212d07459` (Apache-2.0 + NOTICE) | **Faithful Go→Rust port**, original TypeScript semantic authority, upstream symbol/function mapping, parity of diagnostics and output, explicit known gaps; [porting guide](https://github.com/oxc-project/tsrs/blob/main/docs/PORTING.md), [compatibility](https://github.com/oxc-project/tsrs/blob/main/docs/COMPATIBILITY.md). **REFERENCE only**, not installed as a new compiler. |
| [Cloudflare Vinext](https://github.com/cloudflare/vinext) at `9fcbed8634be6ba3cadfb1383153963febb5456f` (MIT) · [compatibility matrix](https://vinext.dev/compatibility) | Upstream changes → affected Consumer tests → focused reproduction → selected regression → periodic compatibility matrix. **METHOD REFERENCE**, not another scheduled agent. |


For every **actual new migration**, select source+target revisions, use the appropriate AST/structural parser, locate real API callers and reachable dependency closure, preserve original implementation when possible, separately run original and candidate under matched inputs, compare **outputs, error types, ordered events, state, DOM, network/effects** with only original-Owner-authorized normalization, run planted false-equality controls, and obtain original scoped Test Manager and Owner receipts. Source code listings alone are NOT AST proof. A browser test for an illustration is not a native Agent execution.

### F. Rights and adoption readback

- **PINNED commit/identity ledgers (authoritative):** `design/visual-skills.lock.json`, `design/diagram-authoring.lock.json`, `references/aifs-figure-vendor.json`. This resource registry provides discovery links; it must not supersede those exact checkout bytes.
- All GitHub-source Code/Skills/Assets must be checked for **their selected revision and license** before copying. Original MIT or Apache-2.0 permission never automatically licenses externally hosted lesson material, images, fonts, academic figures or brand assets. Preserve complete mandatory attribution and notices. Do not assume all web content is transferable.
- The separate **employee-origin shortlist** was only a research filter at the beginning of this conversation. Later user decisions explicitly admitted AIFS, SeeCode and OMM; do not reject them for not being employee-authored, and do not pretend the list is a blanket license for every other project.
- No automatic full-repository imports, migration to another writable repository, model-authored rewrites of original verified algorithms, OMM Cloud Push, Production dependency additions, Provider writes or public publication result from this list. Fresh Source and native Permission/Acceptance each have their own required proof.


## 3B. Five-repository TS7 Stable / Bun / TanStack Start / tsrs integration — 2026-10-21

**Parent Goal:** Apply the actual TypeScript 7.0 Stable + Bun + TanStack Start + Rust tsrs stack only where a real code Consumer exists, while retaining all previously frozen MIG-01/02/03 A, MGC-01/02/03/04 A, ARC-01/02 A, VIZ, VIS and ViewEnv constraints. The umbrella request is multi-repository, but **each PR** preserves its own original Owner/write Scope, not a new cross-repository admission.

**Exact selected PRs and observed status at this historical handoff** (refresh HEAD and CI before any next operation):

| Original repository/PR | Concrete TypeScript/Bun/TanStack/tsrs outcome | Original source/verification |
| --- | --- | --- |
| [Soodles PR #444](https://github.com/ed3c/soodles/pull/444), `c45d566e69bb074da33b63a89060022c893ff7de` | Python-only orchestration/Code-intel: no fictitious TS7 package. `migrate-class` routes language-specific AST, Bun/TS7/TS6 and tsrs 7.1-dev to actual target Consumer without changing original Outer/Poteto. | [migrate-class Skill](https://github.com/ed3c/soodles/blob/codex/migrate-class-source-bound-parity/.agents/skills/migrate-class/SKILL.md). [Source-only Runtime CI 39590124507](https://github.com/ed3c/soodles/actions/runs/39590124507) **SUCCESS**. |
| [Noodle PR #122](https://github.com/ed3c/noodle/pull/122), `fee03884f2990eb3676ab74cc44e4b538aab6e23` | Original Go Host + TanStack **Router** React UI; official TS7.0.2 native checker, TS6 JS compiler API bridge, pnpm-generated frozen lock. Added **Bun 1.4.3 secondary `bun check` and Bun-driven Vite build**. No forced Router→Start server rewrite; tsrs is an independent research candidate, not Noodle production checker. | [Noodle toolchain contract](https://github.com/ed3c/noodle/blob/codex/typescript-7-stable-ui-compat/docs/typescript-7-migration.md), [Test CI 39590037299](https://github.com/ed3c/noodle/actions/runs/39590037299) **SUCCESS** (Bun Checker/Vite/UI/Docs/Go tests); [exact pinned-Bun CI 39591295224](https://github.com/ed3c/noodle/actions/runs/39591295224) **SUCCESS** at the recorded Noodle Head with pinned Bun 1.4.3, UI/Vite, docs, Graph and Go regression checks. |
| [NeoWeaver PR #23](https://github.com/ed3c/NeoWeaver/pull/23), `3bcdb11fddc64362f39fd45056001968cf1d7cf2` | Harness/spec and card semantics have **no JS/TS application**. Versioned source-only Toolchain Profile for future authorized Consumer; **NO local Bun/TanStack/tsrs installation**. | [Toolchain Profile](https://github.com/ed3c/NeoWeaver/blob/codex/ts7-bun-tanstack-tsrs-contract/docs/toolchain-profile.json), [CI 39589724540](https://github.com/ed3c/NeoWeaver/actions/runs/39589724540) **SUCCESS** source-only. |
| [FactoryWeaver PR #32](https://github.com/ed3c/factoryweaver/pull/32), `f38abc7ff458277bb25c4160378328d8527db743` | Python specification compiler + Skills have **no JS/TS frontend**. Portable Toolchain Card/Profile, keeping original Knowledge/Card Owner, without a fake package.json, JS AST runtime or invented admission. | [FactoryWeaver Toolchain Profile](https://github.com/ed3c/factoryweaver/blob/codex/ts7-bun-tanstack-tsrs-contract/docs/toolchain-profile.json), [CI 39589772441](https://github.com/ed3c/factoryweaver/actions/runs/39589772441) **SUCCESS** source-only. |
| [medium-compiler PR #72](https://github.com/ed3c/medium-compiler/pull/72), `a45b30cf647476053005e97fb5d9b22a11140035` (before this handoff edit) | **Real isolated TanStack Start Preview**: npm-generated exact `package-lock.json`, `@typescript/native=7.0.2` for `tsc`, TypeScript 6 JS API alias for source-bound AST, pinned Bun **1.4.3** as a secondary checker/runtime, and pinned Rust `@tsrs/wasm@0.18.0-ts7.1.0-dev.20260929` in-memory positive/negative diagnostic tests. Original Python/static site/Cloudflare deployment unchanged. | [Workbench toolchain](ts7-bun-tanstack-tsrs.md), [Source+Browser CI 39590649274](https://github.com/ed3c/medium-compiler/actions/runs/39590649274) **SUCCESS** and [exact-head Contract CI 39591176287](https://github.com/ed3c/medium-compiler/actions/runs/39591176287) **SUCCESS**; [post-handoff original source/Browser CI 39591555567](https://github.com/ed3c/medium-compiler/actions/runs/39591555567) **SUCCESS**, including actual tsrs-WASM execution and paired original AIFS/SeeCode Browser controls; [Writing CI 39591176254](https://github.com/ed3c/medium-compiler/actions/runs/39591176254) was in progress when read. |

**Compiler Truth:** Microsoft stable TypeScript 7.0.2 is Go-native; Bun `bun check` has its own TS7 semantics; `tsrs` is a **Rust** TypeScript **7.1-dev** port. It is invalid to treat diagnostics from tsrs 7.1-dev and official TypeScript 7.0.2 as a same-revision Differential Test. tsrs's new `@tsrs/wasm` smoke proves local source-directed Rust checker invocation (one error code 2322 and one legitimate valid input), **not a completed Typed Code Explorer browser view, universal parity, Runtime/P-class acceptance or perf gain**. Preserve the original `@tsrs/wasm` Source/NOTICE constraints.

**Next Session Source Readback:** Read all five PR Heads/CI runs and original Owner next. No PR is merged or Production deployed; do not assume code from Draft Noodle/Soodles PRs is installed in the current Host or live user device. For medium-compiler, run the selected TypeScript7/native CLI, Bun check, TS6 JS Code-intel, tsrs positive/negative controls, Chromium AIFS/SeeCode parity and writing regression. For Noodle, retain Go Host/Graph validity and TanStack Router. NeoWeaver/FactoryWeaver need an **actual selected JS consumer** before claiming environment installed. Any external Noodle Native Evals remain NOT_RUN.


**Lock and default runtime:** medium-compiler Workbench now commits actual npm-generated `apps/loop-workbench/package-lock.json` and uses exact `npm ci` in CI. Bun 1.4.3 runs as a *secondary executable/checker*, not as an uncommitted Bun package-manager replacement; maintain exactly one source-owned lock per installation path. Rust `@tsrs/wasm` runs in-memory fixtures without Host tool invocation or a TypeScript 7.0 version-matched oracle. No merge or deployment is authorized.

## 3C. Exact-HEAD five-repository verification readback (2026-10-22)

The following were read from **GitHub PR Head and GitHub Actions provider**, not guessed from the prior historical Handoff or prompt text. These are original Consumer-specific checks, **not** joint production deployment, an installed Native Host or a fully equivalent Rust compiler.

| Original repo / Draft PR | Exact observed PR Head | Exact-head CI readback | Scope of PASS |
| --- | --- | --- | --- |
| [Soodles #444](https://github.com/ed3c/soodles/pull/444) | `c45d566e69bb074da33b63a89060022c893ff7de` | [runtime 39590124507](https://github.com/ed3c/soodles/actions/runs/39590124507) **SUCCESS** | Python `migrate-class` integration Source-only; no TS runtime to install; Native Poteto eval **NOT_RUN** |
| [Noodle #122](https://github.com/ed3c/noodle/pull/122) | `fee03884f2990eb3676ab74cc44e4b538aab6e23` | [Test 39591295224](https://github.com/ed3c/noodle/actions/runs/39591295224) **SUCCESS** | Microsoft native TS7.0.2 `tsc`, TS6 JS API, Bun **1.4.3** `bun check` (7.0.2, **81 files**), Bun-driven Vite build, TanStack **Router** UI, Docs and Go original tests; no Router→Start server rewrite |
| [NeoWeaver #23](https://github.com/ed3c/NeoWeaver/pull/23) | `3bcdb11fddc64362f39fd45056001968cf1d7cf2` | [compiled-specification-consistency 39589724540](https://github.com/ed3c/NeoWeaver/actions/runs/39589724540) **SUCCESS** | Versioned source-only toolchain compatibility profile; no native JS/Bun package created |
| [FactoryWeaver #32](https://github.com/ed3c/factoryweaver/pull/32) | `f38abc7ff458277bb25c4160378328d8527db743` | [verify-public-contract 39589772441](https://github.com/ed3c/factoryweaver/actions/runs/39589772441) **SUCCESS** | Versioned source-only card/toolchain profile; existing Python distribution validated; no native TS app created |
| [medium-compiler #72](https://github.com/ed3c/medium-compiler/pull/72) | `2306e45f3c612bc4a24a519e1654571a6f6f2cca` **prior to this Handoff commit** | [Loop Workbench 39591806183](https://github.com/ed3c/medium-compiler/actions/runs/39591806183) **SUCCESS** and [Writing Verification 39591806149](https://github.com/ed3c/medium-compiler/actions/runs/39591806149) **SUCCESS** | Isolated TanStack **Start** Preview; Microsoft TS7.0.2, TS6 JS AST, Bun **1.4.3** `bun check` (7.0.2, **12 files**), Vite/Playwright, AIFS/SeeCode fixtures, `@tsrs/wasm` (TS7.1-dev) isolated type-error/valid-neighbor tests, original article/ALG Four regression |

**Source-verified sample outputs** from Noodle and medium-compiler exact-head Actions jobs: `tsc Version 7.0.2`, `JS API: 6.0.3`, Bun `1.4.3`, Bun bundled TypeScript `7.0.2`. Although Bun and Microsoft native compiler identify the **same TS minor in these observed runs**, that is **not** a substitute for same-fixture diagnostic Differential Oracle. `tsrs` remains at `7.1.0-dev.20260929` and cannot participate in a TypeScript **7.0.2** same-revision comparison.

**Open work / Stop:** all five PRs remain **Open Draft**, zero merged or deployed. No evidence of true Native Soodles↔Noodle Poteto Consumer acceptance, no accepted Paper/OMM architecture review, no arbitrary-code Browser execution security acceptance, no full Typed Code Explorer. To complete a real runtime promotion, original Owners must authorize that action, choose actual minimal tests and read back effects. The next Session should consult this source ledger and current PR HEAD rather than rerun completed tests or ask for already resolved migration scope. A changed HEAD requires new provider readback at that HEAD.

## 3D. 續行讀回與第一份 OMM 候選 — 2026-10-22

本次重新讀回五個 PR，Head 均與 §3C 的 Soodles／Noodle／NeoWeaver／FactoryWeaver 記錄一致。
medium-compiler #72 的 Head 為 `5994e2b998f8baabf998c9a07e12211907ec67d3`。
該 Head 的 [Loop Workbench 39635681178](https://github.com/ed3c/medium-compiler/actions/runs/39635681178) 與 [Writing verification 39635681181](https://github.com/ed3c/medium-compiler/actions/runs/39635681181) 現已全部 `completed / success`。
這是原候選的 Provider 讀回，不是以下新增文件之後的 CI 結果。

沿 §5 的第一項工作，已完成一份局部 OMM 原始碼分析與可審查候選：
[公開 Snapshot／artifact 讀回](derived-architecture/public-artifact.md)、[Mermaid](derived-architecture/public-artifact.mmd) 與[八檔來源索引](derived-architecture/public-artifact-sources.json)。
來源固定在上述 medium-compiler Head；沒有掃描其他 repository。
固定版本 OMM CLI 已在任務暫存目錄建置並執行 `write`／`validate`。
Session 先讀 Python／TypeScript AST 與實際呼叫，再產生 7 個節點、7 條關係。
獨立來源 reviewer 指出一般「選取來源」不一定 fetch；候選已縮準到 mechanism principle／本次原要求讀回。
虛構 Panorama 直接呼叫 `readReviewedArtifact` 的負向對照被拒絕。

本次沿原 `loop-workbench-contract.yml` 使用 diagram-authoring 的 4 個測試、現有候選 checker，以及 artifact reader 的 4 個正反案例，均成功。
另外核對八個來源 bytes／digest，並確認 source／candidate digest 漂移及無 receipt 的 reviewed 狀態均被原 checker 拒絕。
Registry 是 **1 candidate、0 reviewed**；靜態語義審查沒有自動批准 promotion。
完整 repository OMM 掃描、獨立 Browser 視覺驗收、Native Soodles／Noodle Acceptance、Merge 與 Production 仍未完成。

首次保存候選的 commit `5b0f1f5a9bcaa6aa4d8ab7b85d54e3a25b212a33` 在
[Workbench 39638146934](https://github.com/ed3c/medium-compiler/actions/runs/39638146934) 的 visual-architecture 測試失敗。
舊斷言要求候選清單永遠為空，與本次新增合法候選的要求衝突。
修正將該斷言改為逐項要求 `candidate` 與空 review receipt；文章圖 registry 的空清單限制保持原樣。
原候選 checker 繼續核對來源與圖檔摘要，沒有停用任何測試。
修正後必須讀回新 Head 的 CI；前一次失敗保留為歷史，不重標為成功。

本次未重建工具鏈，也未改產品程式、已接受文章或 ALG Four。
原 §4 backlog 與 §5 分階段契約保持有效；第一份局部候選不能關閉 Parent Goal。

## 4. What is delivered vs. what is still missing

| Domain | Verified/delivered subset | Next real gap / acceptance required |
| --- | --- | --- |
| Canonical Graph / Panorama | Source-bound Noodle renderer integrated in isolated TanStack; static public-artifact digest+bytes reader and Chromium fixtures | New real original Native Graph v2 event/owner acceptance and audited disclosure **NOT_RUN** |
| Editorial/interactive diagrams | SeeCode isolated CLI+Chromium and a first bounded source→sandbox differential PASS | Actual **independently reviewed** source-bound article figure + approved public SVG still **NOT_RUN** |
| Codebase Architecture Knowledge | OMM `omm-scan`/`omm-view` pinned SKILL source and reviewer contract; `omm-push` excluded | Perform real **medium-compiler-only** source scan, prove source/edge refs and loss report, independent review, then versioned `docs/derived-architecture/` if approved |
| AIFS Explorable Figures | Byte-pinned LF/math/demo modules, local JS/TS AST Code-intel, sandboxed `/figures` preview; Chromium input→output differential for three samples | More source-authorized modules only as needed, genuine larger parity+accessibility sample and published-article insertion separate |
| Learning Platform | Two original Python exercises, local DuckDB-Wasm OPFS drafts and JSON/.duckdb export, Chromium write/reopen smoke | Real isolated, no-network bounded Pyodide execution, browser grader with honest untrusted results, browser/Safari persistence, full learning catalog/progress |
| Typed Code Explorer | Defined VIS-08 A/source requirement; new [Cloudflare/tsrs method](typescript-rust-port-integration.md) for faithful-port reference | **NOT_IMPLEMENTED**; TS7.0 stable vs tsrs 7.1-dev remains a mismatched-revision pair despite the real in-memory WASM smoke; future original-revision-matched tsgo/tsrs and browser type-hover require separate admission |
| Research Paper / Evals | Source-bound article builder and owner/rights methodology | New reviewed Paper Reader/Figure and Evidence-first interactive Claim/Method/Trace/Metric UI **NOT_IMPLEMENTED** |
| Native Skill Evals | Soodles `migrate-class` source-only CI and medium-compiler browser differential | Actual admitted Noodle Poteto run, independent Observer, matched native baseline/treatment and original Owner readback **NOT_RUN** |
| Delivery | Existing PRs Draft, independent source/browser CI success at cited heads | Neither PR merged; **no Production deploy** authorized. Exact-head checks required for any later action |

## 5. Next conversation: phased execution contract

**First task, not a new global migration:** Read current PR #72 and Soodles PR #444 Heads; confirm live AGENTS, frozen decisions, exact CI/selection and destination-only writes. Use `migrate-class` to select the earliest *observable consumer gap* in medium-compiler; avoid moving source files just because more tools exist. For first Architecture/Editorial closure, prefer **real medium-compiler OMM analysis + one source-bound independently reviewable diagram candidate** if live evidence still confirms these are missing. Keep candidates unpromoted until original review, even if CI succeeds.

For each next actual source/feature: select original Consumer and Source contract → language-correct AST/structural facts and complete needed dependency closure → reuse existing target or byte-pinned vendor/codemod → only minimum necessary Adapter written by original authorized Writer → same-input **original vs migrated** outputs (including failures, event order and effects) + planted false equality → original Test Manager scoped tests → authorized original Owner readback. If original OMM scanner/Native Host cannot run, do not write synthetic PASS or fabricate source edges; continue independent authorized slices and explicitly report the named blocker.

The full backlog (Learning/Pyodide, Typed Code Explorer, research/Evals and paper figures) remains part of the **Parent Goal** but is delivered as separately scoped tasks with their own original source/independent acceptance. Do not declare the whole Goal complete from the first migrated graphic.

## 6. Suggested Skills for the next Agent

When the native Skill tool is actually available, use **migrate-class** (Soodles PR #444 selected ref), **thinking-router** (V2/conditional V3), **ambitious-route** only for meaningful Outcome change, **code-intel** on applicable Python sources, original **test-manager**, and medium-compiler **loop-visual-design**, **viewenv**, **medium-writing** and **verify-learning-article** as domain-selected. Use original **check** or **ponytail-review** only when a concrete candidate requires independent diff review; use **handoff** when manually ending another session.

Important: original [Soodles handoff SKILL.md](https://github.com/ed3c/soodles/blob/main/.agents/skills/handoff/SKILL.md) is `disable-model-invocation: true` and requests a temporary OS-path handoff first. This checked-in document is the **user-explicitly requested durable Git copy prepared using those content rules**; it is **not evidence that a native Skill tool was automatically invoked**.

## 7. Hard stops and non-claims

- **No new Graph Truth Owner, P-class type, CLI state machine, Scheduler, Native runner, new global dependency or Provider authority.** Original Soodles/Noodle semantics, existing Source Owners and admitted Stage inputs prevail.
- **No automatic cross-repository writes, OMM Cloud Push, external network/resource loading in untrusted previews, credential leakage, unreviewed SVG promotion or silent user-data collection.**
- **No changed accepted article/ALG Four bytes**, fabricated PaperBanana experimental result, made-up digest, guessed `next.argv`, retry of unknown external effect, false native acceptance, PR merge or Production deployment.
- Keep statuses separate: Source Identity, selected Browser/Differential, independent semantic/parity Oracle, Fresh Native Agent, Human Comprehension, Provider Landing. Unknown stays UNKNOWN/NOT_RUN/INCONCLUSIVE.
- New chat should preserve this document and update it **only after fresh Source and actual test evidence**; do not copy whole specs/diffs into handoff. Original GitHub branches, receipts and referenced contracts remain authoritative.
