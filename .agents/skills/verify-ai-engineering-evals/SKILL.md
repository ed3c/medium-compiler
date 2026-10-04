---
name: verify-ai-engineering-evals
description: Evaluate AI coding workflows and staff-level engineering judgment with pinned source, actual traces, scoped technical checks, English feedback, and a medium-compiler report. Use for Soodles AI Evals, coding-agent A/B review, or maintenance of this evaluation feature map.
---

# Verify AI engineering evaluations

Evaluate what the coding Agent did and what the evidence supports.
Use English for the technical assessment. Add a Traditional Chinese reader guide.
Do not represent an AI-authored assessment as the user's independent work or a hiring certification.
Read [the feature map](features/README.md) and the selected recipe.
Read [the source standards](references/standards.md) before changing this guidance.

## Launch

Use the repository's Python 3.10+ environment. No model API key is required.
Use GitHub for cloud source and provider evidence. Preserve the selected execution carrier.
Do not install Codex CLI or start Noodle to evaluate archived evidence.
From this repository root, run:

```sh
python3 .agents/skills/verify-ai-engineering-evals/scripts/audit_archive.py --help
```

This is a short-lived read-only source audit. Each output directory must be new.
For the website, build with `python3 scripts/build_site.py --out /tmp/ai-evals-site-NEW`.
The builder deletes its output directory first. Use only a task-owned path.

## Doctor

Read the target repository's AGENTS.md at the selected immutable ref.
Check the target checkout with `git rev-parse HEAD` and `git status --short`.
Match the requested ref and check that selected evidence files exist.
Read the current task, constraints, owner output, report and capture before deciding what to measure.
An absent transcript is a coverage gap. It is not a model failure.
If the repository is dirty, identify the changed inputs before using its evidence.
Do not silently bind a changed file to an unchanged commit.

## Drive

1. Select a bounded real engineering workflow. Record the task and why this case matters.
2. Inspect the actual failure or comparison before defining criteria.
3. Derive acceptance, rejection and unknown conditions from the original requirements.
4. Use the installed `eval-audit` for an existing pipeline. Use `error-discovery` for unclassified traces.
5. Separate source inspection, archived execution, new deterministic checks and fresh Agent observations.
6. Check engineering judgment, debugging, reasoning clarity, architecture, communication,
   attention to detail and developer trust only where the evidence permits judgment.
   Explain an unassessable dimension instead of assigning a default pass.
7. For each finding, state the observation, source location, impact, supported conclusion,
   relevant alternative, and next action. Include strengths and counterevidence.
8. For A/B, compare under the same task and completion boundary. Disclose changed inputs.
   Do not claim blindness after seeing arm identities. A tie is a valid result.
9. Verify deterministic claims with code, owner readback or focused reproduction.
   Do not replace technical verification with an LLM opinion.
10. Write the English assessment with the report structure below. Publish through the existing site builder.

For model-judge scoring, load `write-judge-prompt` and `validate-evaluator`.
Missing expert labels or held-out calibration remains a gap. Never fabricate labels.
Do not impose a sample quota, arbitrary numeric quality score or mandatory model judge.
A small case review cannot establish a population failure rate or a frontier-model ranking.

## Report structure

State task and constraints; evidence and provenance; observed behavior;
technical verification; findings and counterevidence; A/B decision when applicable;
preferred behavior; uncertainty; and concrete next observation.
For a design judgment, explain the constraint, premise, choice, simpler alternative,
and runtime actor, input, check, state change, effect and failure path.
Use short active sentences and stable terms. Preserve raw bytes, negations and uncertainty.
Write an English verdict that a reviewer can understand without this chat.
Keep tokens, wall time, model time and task-handling time separate. Unknown values stay unknown.

## Evidence

Pin repository and full commit SHA. Bind selected files with SHA-256.
Retain raw inputs, outputs, commands, exit codes and captures before interpretation.
State evaluator identity, known model identity, sample selection and observation scope.
Keep expected answers outside fresh consumer inputs. Do not claim filesystem isolation.
Native child reports and final messages are not a complete independent tool transcript.
A new review of an old trace remains a retrospective evaluation.

For new or changed P-class guidance, follow Soodles review-writing and its pclass-feedback recipe.
Freeze requirements and a bound protocol before consumer observation.
Use a fresh native consumer when authorized. Give it only the task, saved skill and raw inputs.
Submit the actual report and available capture to the existing command:
`./soodles schema pclass-feedback SELECTION_JSON SELECTION_SHA256`.
Resolve the two arguments from saved files; they are not literal executable values.
Read `evidence_validity` before `behavior`. Consume `next.operation` and retain the response.
Treat `next.operation` as a decision label, never an executable command.
When it is `supply_behavior_evidence`, complete the returned `next.input.selection`.
Use `next.input.requests` for exact report identities and requested fields.
Preserve the observations already selected by the owner. Add actual reports and captures.
Match the report's instruction map exactly to the supplied instruction list.
Keep method files in the protocol's methods list, not the report's instruction map.
Save and hash the completed draft before submission. Do not reconstruct it from case names.
For an admitted Noodle writer, use `./stage-outcome feedback` instead, with its existing identity.
Do not create admission, claim lifecycle completion, or infer landing authority from feedback.
A scoped structured PASS does not certify the English analysis or staff-level ability.

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
