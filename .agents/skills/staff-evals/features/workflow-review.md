# Evaluate a pinned coding workflow

## Sub-features

Review a concrete engineering decision through requirements, implementation, runtime and
verification. Use the claim-refusal archive as one bounded example, not the only supported task.

## How to get to it (user POV)

Select a task/Issue, source revision and available execution evidence. Use SKILL.md's
engineering role to review it. The historical example is at `/ai-evals/` → Soodles report.

## Driving it with file tools and Python

Run `python3 .agents/skills/staff-evals/scripts/audit_archive.py --soodles /absolute/soodles --revision FULL_SHA --out /tmp/ai-evals-archive-NEW` for the existing claim-refusal archive. Resolve paths and SHA from the selected checkout. Read back its 25 bound files, six observations, selected revision and null quality verdict. This helper does not select a general engineering task for you.

Read the selected requirements, caller/callee and tests alongside owner records, consumer
outputs and available capture. At the pinned Soodles example, follow `_run_claim`, its
caller in `issue_atom.py`, `refusal_output` and the focused claim-refusal tests. Explain
how nonzero claim status changes continuation and which effects the tests distinguish.
Bind supporting source files separately to pinned Git bytes and SHA-256. For handoff or
A/B judgments, also read the relevant comparison freeze, input manifests, instructions,
read receipts and handoffs; those are outside the helper's 25-file set. Do not execute
historical argv or turn a source example into a live lifecycle command.

Write an English assessment and Chinese guide that connects the requirement, code/trace,
decision, consequence, alternative and check. Re-read the prose against those sources.
Success means a reproducible, scoped engineering judgment with explicit unobserved claims,
not merely matching hashes or filling seven labels. Retain the audit, added bindings,
actual commands/results, assessment and substantive review after cleanup.

For an Agent workflow evaluation, build a short evidence-linked decision sequence first.
Separate information available before the action from facts learned afterward. For each
important choice, read the relevant code or diff and explain its runtime consequence.
Inspect whether a debugging check distinguishes competing causes, whether a test preserves
the required behavior, and whether failure changes the next action. Include the Agent's
stated reason only when recorded. A successful outcome cannot supply a missing rationale.
Partial capture supports the observed episodes; it does not prove the whole workflow.

Use the job-requirement mapping in [engineering-role.md](../references/engineering-role.md#job-requirement-implementation)
to check the relevant work. Do not require every job dimension in every case.
For a weak output, quote or locate the actual claim, identify the failed premise, and
describe the decision it could mislead. For subtle quality differences, compare alternatives
under the same constraints; do not attribute a hypothetical alternative to another Agent.
Make a defensible judgment before filling coverage labels. Missing behavior evidence
requires a scoped collection step or an explicit incomplete behavior outcome.

## Gotchas

A successful audit proves file identity and extracts observations. It does not prove model
quality. Source inspection can establish a branch's implementation while archived reports
support only the decisions they expose. Missing execution leaves actual debugging and
hidden actions unassessed, not the whole implementation unknowable. Review only authorized
source scope; request the specific missing artifact when it changes a material judgment.
