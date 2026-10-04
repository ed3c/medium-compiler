# Case data and prediction feedback

## Record and retrieve

Use `features/experience/index.json` as the feature map's data index. Store a new case under
`features/experience/<case-id>/` with its raw evidence or authorized durable references.
Use the JSON template in `assets/experience-case.json`; replace empty values with facts or
explicit nulls and gaps. Never treat the template as an observed case. Keep bulky/private
traces in the target's authorized evidence store; index the permitted locator and digest.
Do not publish private code, credentials or customer traces merely to fill a public case.

The reviewer writes these files with ordinary file tools. This skill has no automatic trace
collector, model trainer, new lifecycle owner or prediction-scoring service. Parse the JSON,
read referenced files and recompute hashes. Structural validity does not establish meaning.

Every case retains:

| Field | Meaning |
| --- | --- |
| `id`, `schema`, `feature` | Stable case ID, format version 1 and mapped user-facing feature. |
| `target` | Repository/revision or equivalent immutable source identity; task and patch references. |
| `actor` | Coding agent/model/harness when known, or explicit unknown; do not infer from a file author. |
| `reviewer` | Actual human or Agent identity; assistance and prior exposure to the answer. |
| `evidence` | Selected artifact locators and SHA-256, plus source/runtime/report/capture distinctions. |
| `review_mode` | `implementation_review`, `agent_workflow_evaluation`, or `combined`, selected from available evidence. |
| `decision_episodes` | Observed Agent choices with evidence available before action, action, stated reason or null, later observation, judgment, alternative and correction. |
| `disagreements` | Actual reviewer disagreements and later corrections; preserve original judgments. |
| `decision` | Requirement, concrete mechanism, consequence, alternative and tradeoff. |
| `prediction` | Null for retrospective work; otherwise reference the separately frozen forecast. |
| `outcome` | Actual observation and scope; null while unobserved. |
| `lesson` | Applicable conditions, counterexample, next check and proposed/locally supported/retired status. |
| `role_feedback` | Applicable JD concerns and locators to substantive reasoning; not seven generic scores. |
| `cost` | Available token, tool, elapsed, review and repair measurements; null means unmeasured. |
| `closure` | Product, Agent and evaluator results; owner response/consumption when applicable; remaining gaps. |

Retrieve by subsystem, decision, failure boundary and applicability before using similarity.
Re-check changed contracts. A case is evidence for its task, not a new universal instruction.
Link contradictory cases. Keep the old lesson and explain supersession rather than deleting misses.

For each decision episode, use a stable local ID and locators into retained evidence.
Keep observation and interpretation separate. A minimal episode has `id`, `before_refs`,
`action`, `stated_reason`, `result_refs`, `judgment`, `alternative`, and `next_check`.
Add fields only when the case needs them. Source-only cases keep `decision_episodes` empty.
These optional additions retain schema 1 compatibility with earlier cases. Missing fields
in historical records do not become evidence of observed Agent behavior.

## Freeze before resolving

A prospective prediction file contains `case_id`, `reviewer`, `input_refs`, `condition`,
`predicted_observable`, `reason`, `falsifier`, `resolving_check`, `confidence` and `created_at`.
Confidence may be null; if numeric, use a stated probability for a well-defined event.
Bind exact inputs and the prediction bytes. The observer retains the file/hash before
launching the resolving check or revealing held-out results. Save the actual observation
order from the available carrier. Commit time alone does not prove lack of prior exposure.
Record exposure and capture limits; exclude contaminated or unproven ordering from prospective metrics.

The outcome file references the prediction hash, actual check/input identity, observed value,
raw result, `resolution` (confirmed/contradicted/unresolved) and the resolving authority.
Use code/owner truth for deterministic outcomes. For subjective quality, retain independent
expert judgment and disagreements. An uncalibrated Agent judge cannot supply expert ground truth.
Append the corrected reasoning and next prediction separately. Do not alter the original forecast.

Report performance only within its evidence scope. Show numerator, denominator, unresolved
and excluded cases, sampling and task families. Keep software forecasts, Agent decisions and
human predictions separate. For probabilistic forecasts use a proper score such as Brier only
on resolved, eligible predictions; expose sample size and calibration limits. For binary judges,
define positive/negative labels and show per-class errors/TPR/TNR on held-out expert labels.
Do not convert an accuracy percentage on a convenient sample into job readiness.

## Connect to the role and Soodles

Use the supplied G2i role to ask concrete questions: did the reviewer predict the failure
path, select an informative debugging check, compare architecture tradeoffs, notice missing
evidence and communicate an actionable English explanation? Verify observable predictions.
Review reasoning quality separately; a lucky correct answer can have a defective rationale.
Human experience requires actual human decisions and feedback. Agent-only records remain
valuable engineering evidence but cannot establish the user's independent skill.

Keep three closure questions distinct:

- Product: did the target implementation meet the scoped contract, including relevant regressions
  and provider effects? Use its existing owners and final readback when delivery is in scope.
- Agent: did the observed workflow make defensible decisions under the supplied constraints?
  P-class edits require review-writing, fresh bound consumer evidence and Soodles feedback.
- Evaluator: did the check reach the intended behavior and discriminate a meaningful violation
  from a valid alternative? An oracle failure can leave the product outcome unknown.

For Soodles, use schema-1 public feedback for scoped cloud consumer evidence; use schema 2
and stage-outcome for an already admitted writer. Retain validity, behavior, returned next
operation and actual owner consumption. A forecast cannot authorize next actions or replace
owner truth. Closure follows affected owners/evidence, never a mandatory N → P → L → R sequence.

## Source and scope

This data contract is an adaptation for the user's requested experience loop, not an upstream
evals-skills schema or a G2i interview rubric. It composes the pinned review-writing and eval
methods in standards.md with the Notion Shape → Guard → Guide principles linked in
engineering-role.md. The Domain Context Pack was reread on 2026-10-04 and remains staging,
not proof of runtime enforcement. Token savings and cheap repair are hypotheses to measure.
