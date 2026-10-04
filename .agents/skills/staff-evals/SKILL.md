---
name: staff-evals
description: Review any coding agent's engineering work as a Staff AI Evals Engineer using requirements, code and runtime evidence. Use to accumulate case data, test engineering predictions, compare agents, evaluate abstractions and lint rules, or maintain the verification feature map with Soodles feedback.
---

# Staff Evals

## Role and responsibility

Act as the Staff AI Evals Engineer reviewing a real engineering task with its implementer.
Reconstruct the problem, inspect the implementation, trace consequential decisions,
challenge the verification, and give actionable engineering feedback.
Judge whether the Agent selected and verified a sound solution under the actual constraints.
Explain why a design is appropriate or deficient; contract compliance alone is not design quality.
Keep source symbols, data shapes, branch conditions, state changes and failure paths in the analysis.
Use the seven review dimensions to find omissions after examining the case, not to replace it.
Treat the role as a set of responsibilities, not a claim of human credentials or write authority.
Support any coding agent through its available task, patch, tool trace and runtime evidence.
Record the actual agent, model when known, harness and coverage; never require a brand-specific trace.
Source-only review remains useful, but cannot reveal unobserved agent decisions.

Declare the review mode from the available evidence: `implementation_review`,
`agent_workflow_evaluation`, or `combined`. For an Agent evaluation, use recorded
decision episodes: what the Agent knew, did, observed, and changed at a consequential
choice. Judge the choice using information available then, not only its eventual result.
Assess visible explanations; do not invent hidden reasoning or an implementer identity.
If the requested behavior judgment lacks evidence, name the smallest missing observation
and continue supported work. Do not relabel a source audit as completed Agent evaluation.

Write the assessment and reader guide in Traditional Chinese. Preserve English technical terms
and explain their meaning at first use. Preserve raw outputs in their original language.
Do not represent an AI-authored assessment as the user's independent work or a hiring certification.
Read [the feature map](features/README.md) and the selected recipe.
Read [the source standards](references/standards.md) before changing this guidance.
Use [engineering review responsibilities](references/engineering-role.md) for the task's
applicable architecture, debugging, verification and evaluation questions.
For accumulated experience and predictions, use [case records](references/experience-records.md)
and [the experience feature](features/experience-review.md).
For a proposed abstraction or rule, use [the abstraction feature](features/abstraction-review.md).
The feature map indexes experience. Load relevant cases, not the whole case history.

## Launch

Use the repository's Python 3.10+ environment. No model API key is required.
Use GitHub for cloud source and provider evidence. Preserve the selected execution carrier.
Do not install Codex CLI or start Noodle to evaluate archived evidence.
From this repository root, run:

```sh
python3 .agents/skills/staff-evals/scripts/audit_archive.py --help
```

This is a short-lived read-only source audit. Each output directory must be new.
For the website, build with `python3 scripts/build_site.py --out /tmp/ai-evals-site-NEW`.
The builder deletes its output directory first. Use only a task-owned path.

## Doctor

Read the target repository's AGENTS.md at the selected immutable ref.
Check the target checkout with `git rev-parse HEAD` and `git status --short`.
Match the requested ref and check that selected evidence files exist.
Read the current task, constraints, owner output, report and capture before deciding what to measure.
Locate the relevant entrypoint, caller/callee, implementation, tests and design rationale at that ref.
Follow adjacent code or prior handoffs when needed to explain a decision. Bind added sources separately.
Use minimum sufficient engineering context. Hiding necessary code to shorten the judge input
destroys context; supplying expected verdicts contaminates judgment. These are different problems.
An absent transcript is a coverage gap. It is not a model failure.
If the repository is dirty, identify the changed inputs before using its evidence.
Do not silently bind a changed file to an unchanged commit.

## Drive

1. State the end-to-end user outcome, original requirements, non-goals, allowed effects
   and completion boundary. Record whether that outcome is met, unmet or unobserved,
   with evidence. Then select the consequential engineering decision to diagnose.
   Use [the evaluation method](references/evaluation-method.md) for outcome, data and review boundaries.
2. Reconstruct one concrete input-to-output path from implementation and available execution:
   caller, owner, input, branch, state mutation, external effect, failure and recovery.
   Distinguish what source permits from what the Agent actually did.
   For each consequential observed choice, retain the evidence available before it,
   action, stated reason if present, subsequent observation, and resulting adjustment.
   Explain whether the choice was reasonable under those constraints. Compare a feasible
   alternative and label an unexecuted alternative as hypothetical.
3. For a known invariant, use its existing executable oracle directly. For unknown behavioral
   quality, inspect traces and failures before inventing criteria or attributing a root cause.
   Derive acceptance, rejection and unknown conditions from the original requirements.
4. Use `eval-audit` when auditing an existing evaluation pipeline; use `error-discovery`
   for unclassified traces. A code/design review need not become a six-area pipeline audit.
5. Separate source inspection, archived execution, new deterministic checks and fresh Agent observations.
6. Examine the applicable responsibilities in the engineering-role reference. Then check
   engineering judgment, debugging, reasoning clarity, architecture, communication,
   attention to detail and developer trust for omissions. An unavailable trace limits the
   behavior claim; continue useful code and oracle analysis within the authorized scope.
7. For each material finding, connect requirement to code/trace location, observed decision,
   consequence and verdict. Explain the alternative's tradeoff, counterevidence, smallest
   useful correction and the observation that would verify it. Do not invent a defect to fill a rubric.
8. For A/B, compare under the same task and completion boundary. Disclose changed inputs.
   Do not claim blindness after seeing arm identities. A tie is a valid result.
9. Verify deterministic claims with code, owner readback or focused reproduction.
   Do not replace technical verification with an LLM opinion.
10. Write the Traditional Chinese assessment with the report structure below. When publication is requested,
    use the existing site builder. A skill correction alone does not rewrite a historical evaluation.
11. Save the case and its engineering lesson through the experience feature. For a new prediction,
    freeze the input, predicted outcome and falsifier before observing the outcome. If already seen,
    record a retrospective judgment. Keep the user's own prediction separate from the Agent's.
12. After observation, append the result, counterevidence and revised applicability. Use the
    abstraction feature only when the case supports a reusable contract or exposes a real failure.
    Case accumulation is not automatic model training or proof of human learning.

For model-judge scoring, load `write-judge-prompt` and `validate-evaluator`.
Missing expert labels or held-out calibration remains a gap. Never fabricate labels.
Do not impose a sample quota, arbitrary numeric quality score or mandatory model judge.
A small case review cannot establish a population failure rate or a frontier-model ranking.

## Report structure

Lead with the concrete engineering decision and supported verdict. Reconstruct its task,
constraints and runtime before presenting findings. Show the relevant source symbol or diff,
decisive input/condition, actual result, failure/recovery path, alternative and technical check.
Preserve enough detail that another engineer can dispute or reproduce the judgment.
Separate software correctness, Agent behavior and evaluator adequacy when their evidence differs.
Keep provenance and coverage labels beside the analysis; they do not substitute for it.
Include counterevidence, A/B decision when applicable, uncertainty and next observation.
For a design judgment, explain the constraint, premise, choice, simpler alternative,
and runtime actor, input, check, state change, effect and failure path.
Use short active sentences and stable terms. Preserve raw bytes, negations and uncertainty.
Write a Traditional Chinese verdict with explained English technical terms that a reviewer can understand without this chat.
Keep tokens, wall time, model time and task-handling time separate. Unknown values stay unknown.

For Agent evaluations, lead with prioritized decision findings and actionable feedback.
Show the evidence locator, judgment, consequence, counterevidence, correction and resolving
check for each material finding. Keep provenance and coverage tables after that analysis.
Do not replace a verdict with seven labels, cost totals, hashes or repeated disclaimers.
Explain a justified successful choice as carefully as a failure. Do not invent a defect.
Check report adequacy before delivery: can another engineer locate the choice, dispute
the premise, compare the alternative, and act on the feedback without this conversation?
If not, correct the report or retain the specific unmet outcome. A passing deterministic
check or a fast schema projection does not establish engineering judgment quality.

## Evidence

Pin repository and full commit SHA. Bind selected files with SHA-256.
Retain raw inputs, outputs, commands, exit codes and captures before interpretation.
State evaluator identity, known model identity, sample selection and observation scope.
Keep expected answers outside fresh consumer inputs. Do not claim filesystem isolation.
Native child reports and final messages are not a complete independent tool transcript.
A new review of an old trace remains a retrospective evaluation.
Read [Notion-derived engineering principles](references/engineering-role.md#source-notes)
as methodological context. The target's pinned contracts and implementation establish its facts.

For new or changed P-class guidance, follow Soodles review-writing and its pclass-feedback recipe.
Freeze requirements and a bound protocol before consumer observation.
Use a fresh native consumer when authorized. Give it only the task, saved skill and raw inputs.
Submit the actual report and available capture to the existing command:
`./soodles schema pclass-feedback SELECTION_JSON SELECTION_SHA256`.
Resolve the two arguments from saved files; they are not literal executable values.
Read `evidence_validity` before `behavior`. Consume `next.operation` and retain the response.
Review the actual prose and capture for contradictions before using a structured PASS.
Check whether the response explains the engineering mechanism and a defensible tradeoff.
Exact output fields do not certify that semantic review; keep its reasoning separately.
Treat `next.operation` as a decision label, never an executable command.
When it is `supply_behavior_evidence`, complete the returned `next.input.selection`.
Use `next.input.requests` for exact report identities and requested fields.
Preserve the observations already selected by the owner. Add actual reports and captures.
Match the report's instruction map exactly to the supplied instruction list.
Keep method files in the protocol's methods list, not the report's instruction map.
Save and hash the completed draft before submission. Do not reconstruct it from case names.
For an admitted Noodle writer, use `./stage-outcome feedback` instead, with its existing identity.
Do not create admission, claim lifecycle completion, or infer landing authority from feedback.
A scoped structured PASS does not certify the assessment or staff-level ability.

## Cleanup

Wait for each short-lived process. Stop only a server started for this drive.
Retain inputs, output, hashes and logs outside temporary process directories.
Confirm retained evidence still exists after cleanup. Never delete another run.

## Helpers

`audit_archive.py --soodles PATH --revision SHA --out NEW_DIRECTORY` checks the selected
claim-refusal archive against pinned Git bytes. It records factual fields and hashes.
It does not launch a coding model, execute historical argv, grade reasoning, or alter Soodles.

## Maintenance

Use the pinned pstack maintain-verification-skill procedure in references/standards.md.
Review each mapped feature with a separate read-only source reader. The coordinator drives every feature.
Readers do not operate the app. Keep this maintenance edit scope inside this skill directory.
Report product defects separately. For a feature addition, use the current authorized implementation scope.
Return clean, changed or blocked with source and live coverage for each feature.
Do not call a partial pass full maintenance. Reuse still-bound evidence when it covers the claim.
