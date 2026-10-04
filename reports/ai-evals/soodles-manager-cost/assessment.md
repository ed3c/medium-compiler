# Soodles: cost evidence is available; cost-directed repair is not established

Soodles already implements a useful separation: Test Manager selects verification and reviews recorded cost; Schema Manager projects that review beside the original owner's continuation. The current implementation does not establish the stronger claim that it identifies avoidable engineering cost, repairs its cause, and measures the improvement automatically. Its millisecond projections describe known transitions. They are not calibrated forecasts of a coding agent's future success.

This assessment reviews `ed3c/soodles@d58c4e7ba0685c367da5c3060e06e6c5fc38f85f`, using source, PR #273's completed runtime, and one new data-only projection. It does not change Soodles, rerun its tests, launch a coding model, or establish the user's Staff-level ability. The implementation's coding agent and model are unknown. The reviewer is AI assistant `/root`; there is no independent human calibration or complete implementer transcript.

## Task, inputs and ownership

The requested design should use normal logs and the schema DAG to keep ordinary decisions cheap. Physical verification should answer a changed engineering question. Observed runtime waste, repeated decision barriers or unnecessary tests should reach Test Manager, then Schema Manager and the existing repair owner. Missing evidence must remain unknown. A slow observation alone must not grant repair or mutation authority.

The pinned `AGENTS.md` and Test Manager skill already state substantially this policy. That is an intended contract, not evidence that every part exists. This review tests the implementation against that contract rather than proposing another manager, scheduler, benchmark service or parallel policy engine.

The concrete historical task is PR #273, preserving exact CI acceptance when a target PR intentionally skips deployment. Its candidate is `75c453fe1e104f530a9800784eddb3f169951480`, base `71b8ea60614c9729e51b87f8602384f654984300`. It changes `landing.py`, `repository_binding.py`, shared test fixtures and delivery evidence. Runtime run `37185131471`, attempt 1, job `111385372510` passed. The review revision is its merged main commit, not a new execution of that merge.

## One concrete input-to-output path

`test_manager.select` follows `BOUNDARIES` for changed product paths and transitive AST imports for changed test modules. The CI request supplies the actual candidate/base. Unknown scope produces `needs_scope`; it does not silently select the full suite. `_run_suite` executes selected modules with up to four workers and checks observed test identities, skips, missing cases and unexpected cases. Timing spans record each module and each case.

For this review, 654 existing `test.*` and `acceptance.*` timing lines were selected from the runtime log. Nested fixture `issue_atom` events were excluded: those simulated task executions are not production CI lifecycle costs. `cost_telemetry.timing_log` normalized the selected events. `cost_telemetry.project` validated and aggregated them, called `TestManager.review_cost`, then called `SchemaManager.project_cost`. The saved `schema-cost-feedback.json` is that actual response, not a proposed payload.

The response was `reviewed`, with 23 explicit unknown entries, no effects, no test demand and no landing authority. The caller then invoked `project_owner_feedback` without inventing a current atom owner. It correctly returned an unknown owner transition. The review coordinator consumed the result and retained the investigation targets. This is completed data feedback to the existing Schema Manager API; live atom continuation is still unverified.

In normal atom execution, `issue_atom.run` obtains the owner's result before attaching cost feedback. `project_owner_feedback` preserves `result.next`. Thus a cost review is available to the consumer, but it does not rewrite the action already selected in that invocation. The CLI `atom cost-report` additionally requires the original authorization, manifest and bound state; those inputs were not supplied for this review. No replacement authorization was created.

## What the existing run actually cost

| Measurement | Observed value | Interpretation |
| --- | --- | --- |
| Selected tests | 28 modules, 617 cases | Focused module selection; not proof that every case was necessary. |
| Unit phase | 203.815 seconds | Elapsed duration of this phase. |
| Sum of module workers | 504.086 seconds | Overlapping worker occupancy, not wall time or measured CPU time. |
| Four physical controls | 58.299 seconds total | Cleanup recovery 21.361, cleanup lock recovery 25.791, delivery recovery 5.047, base recovery 6.100. |
| Provider runtime job | 272 seconds | Separate completed-provider observation; canonical acceptance step 263 seconds. |
| Model tokens, price, human wait, whole-atom wall | Unknown | Do not infer zero from absent spans or use provider duration as the whole task. |

The largest modules are `test_scope_amendment` (150.761 worker seconds), `test_lifecycle_activation` (84.674), `test_correction_preparation` (63.205), and `test_cleanup_continuation` (62.198). Together they account for about 71.6% of recorded module worker duration. Inclusive case, module and acceptance durations must not be added together. Provider duration is retained in `collector.log`; the narrower timing-only projection intentionally leaves its provider-job metric unknown rather than relabeling a log family.

The completed-runtime collector run `37185368947` read existing provider jobs and uploaded its cost artifact. Its manual full-quality observation job was skipped. Current workflows do not support the allegation that every normal PR automatically reruns the full quality suite or reruns runtime on main merge. The old CI cost audit explicitly retains earlier behavior as history. Different historical workloads do not establish a cost regression or savings here.

## Finding 1: focused selection does not yet establish test necessity

`test_manager.select` expands changed test imports to whole consumer modules. Product selection uses a static boundary map. This is conservative and understandable, but it cannot establish a minimal set of necessary cases. The cost review also cannot decide whether each selected case's discriminator was already covered.

PR #273 changed `GenericBindingTests.target`: even the default fixture's workflow event shape changed from `pull_request` to `[pull_request, push]`. Consumers of that fixture receive changed inputs. The tempting alternative, testing only the newly added `ConditionalAcceptanceTests`, could miss behavior affected by those shared inputs. A method body remaining unchanged is insufficient reuse evidence.

The slowest recorded case, `RevisionActivationTests.test_origin_changes_and_unknown_effects_refuse_before_provider`, took 49.581 seconds. Its nine iterations cover session, config, candidate, review, partial, journal, control, repair and scope defects. Each creates a substantial `RevisionActivationFixture`, adopts a scope amendment, mutates an input, runs the original workflow and asserts refusal before provider calls. These are distinct safety boundaries. Removing them merely because they repeat setup would discard meaningful negative coverage.

The smallest useful next investigation is to separate fixture preparation from those discriminating actions during the next already-required execution, if the existing spans cannot answer the question. Then consider sharing only immutable preparation while keeping mutable custody/session state isolated. Accept a scope or fixture reduction only when the same required refusal boundaries and affected consumers remain checked. Current data establishes a cost concentration, not a safe deletion list or a predicted savings amount.

## Finding 2: cost review identifies observations, not avoidable accumulation

`review_cost` reports measured phase costs. Failed/refused observations request owner readback. More than one `test.module` observation for a worker produces `repeated_module_observations` and explicitly leaves `repeat_necessity` unknown. It does not compare the runs' input identities, changed discriminators or required owner evidence, and it has no demonstrated causal classification of runtime waste or decision barriers.

That restraint prevents a historical failure or harmless repeated observation from starting an unsafe repair. However, status `reviewed` must not be read as “cost is necessary,” “cost is optimized,” or “no design risk exists.” A duration-only synthetic control multiplied phase durations by 100 and still returned `reviewed`; a synthetic repeated-module control returned `needs_owner_readback` with no tests requested. These were data-only boundary probes, not new measured production costs.

The next useful addition belongs in the existing review contract: retain the original owner's comparison of repeat inputs and the behavior each run was meant to discriminate. Classify the specific observation as necessary, avoidable or unresolved only when that comparison supports it. A new counter, threshold or broad test runner would not resolve missing causal evidence. Decision-barrier and model/provider costs also require actual observations; no such measurements were obtained here.

## Finding 3: the DAG projects known state quickly; future behavior remains unknown

`schema_manager` uses a finite field catalog and rules for owned transitions. Its typed projection checks source and subject identity, finite nonnegative numeric evidence, original hard gates and non-authorizing review fields. `project_owner_feedback` emits cost-review, owner-transition and effectiveness nodes. The effectiveness node still requires `task_selected_normal_use_evidence` and remains unknown.

On this single local, warm-process observation, parsing/normalization took 7.555 ms; aggregation plus Test Manager and Schema Manager cost projection took 2.923 ms; owner-feedback projection reported 0.005698 ms. This excludes interpreter startup, file retrieval, provider calls, model work and physical execution. It is neither a latency SLA nor a benchmark distribution. It does support keeping deterministic known-state reasoning outside expensive physical verification.

A forecast was saved and hashed before the new API call. Eight named output expectations matched, including unknown wall time and the synthetic boundaries. The reviewer had already read the source and historical run. Therefore this is a local source-informed oracle check, excluded from population prediction accuracy. It is not an unseen coding-agent trajectory prediction. Predicting that an actual engineering change will reduce avoidable work without weakening a discriminator requires a frozen forecast followed by a later comparable normal run.

## Finding 4: autonomous cost repair and outcome consumption remain open

The completed-runtime collector produces an artifact; its workflow does not call Test Manager or Schema Manager. The atom cost path can consume correctly bound evidence, but this review has no original atom authorization, checkpoint or current typed owner response with which to demonstrate that final integration. `owner-consumption.json` records the review coordinator's action and marks live owner feedback incomplete.

`atom_repair.DECISIONS` provides finite existing recovery signals, such as stale PR readback and missing-projection rebuild. Its action/time budgets constrain those repairs; they are not whole-Issue cost budgets. There is no general slow-test or accumulated-cost repair signal. Unknown external effects require original-owner readback, not replay. A `failed_process` entry requiring a bounded patch capability does not prove an arbitrary optimizer is implemented.

A compatible proposed trigger is an observed, source-bound, avoidable cost or design defect, interpreted against the current owner's state and an available bounded repair action. Duration alone, missing timing, or an old failure does not meet that condition. The existing owner must preserve unknown-write handling, allowed effects and budgets. The next normal execution must then measure both the intended cost change and the original behavioral discriminator. This proposal is not an implemented repair or authorization to mutate Soodles.

## Engineering quality and abstraction judgment

The implementation earns specific positive findings: a single verification scope owner; typed, finite schema boundaries; exact observed test-identity checks; replay-aware cost aggregation; unknown values preserved; and no data-derived executable command or automatic full-suite fallback. These constrain bad decisions without pretending that hashes or lint prove semantic quality.

The material limits are equally concrete: module-granularity selection; shallow repeat-necessity analysis; post-action feedback that preserves the original next step; and no demonstrated cost-directed repair followed by measured improvement. More abstraction is justified only where one of these observed decisions can be represented by a useful stable contract. A broad lint rule such as “reject slow tests” would encode the wrong decision and incentivize lost coverage. Token savings and cheaper repair remain unmeasured hypotheses.

The Staff Evals role was exercised through source reconstruction, a targeted discriminator analysis, deterministic boundary checks and explicit architectural tradeoffs. Implementer reasoning, debugging behavior across a full transcript, expert agreement and the user's independent judgment remain unassessed. There is no A/B comparison or general model ranking.

## Retained lesson and next prediction

The feature-map case stores source hashes, original decoded logs, the filtered input, frozen prediction, actual responses and coordinator consumption. Keep the distinction between “measured,” “necessary,” and “authorized to repair.” Those are three different engineering conclusions.

For the next actual repair candidate, freeze the changed input set, affected discriminator, proposed removal/reuse, expected outcome and falsifier before the normal run. A useful falsifier is a lost required refusal, a changed input incorrectly reused, or no observed reduction under comparable conditions. Keep the user's own prediction separate. This case contributes engineering evidence; it does not itself establish human learning or calibrated Staff-level forecasting.
