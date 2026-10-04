# Task outcome, error discovery and evaluator evidence

## Source navigation

Read [Hamel Husain and Shreya Shankar’s FAQ](https://hamel.dev/blog/posts/evals-faq/)
by its original section order. Consult the question relevant to the present uncertainty.
This navigation is a short synthesis, not a copied rubric or universal sample requirement.

| FAQ section | Directly relevant question or principle |
| --- | --- |
| Getting Started & Fundamentals | Define the product outcome and retain the trace. |
| Error Analysis & Data Collection | Inspect examples before fixing a failure taxonomy. |
| Evaluation Design & Methodology | Prefer code for objective checks; validate subjective judges. |
| Human Annotation & Process | Preserve domain-expert judgment and reviewer disagreements. |
| Tools & Infrastructure | Make source evidence readable and keep versions identifiable. |
| Production & Deployment | Distinguish regression checks, monitoring and inline guardrails. |
| Domain-Specific Applications | Evaluate coding and agentic workflows from task outcome to diagnostic steps. |

## Apply to Staff Evals

The following is this repository’s adaptation for the supplied job and Soodles owners.
It is not Hamel’s schema, G2i’s grading rubric or evidence of a completed human review.

Start each case with the requested deliverable. For example, distinguish a correct patch,
a passing selected check, and a delivered website. State which boundary the evidence reaches.
A local PASS cannot answer a deployment question. If the task outcome is unavailable,
retain `unobserved` and continue the supported implementation review.

Locate the first observed divergence from the required outcome. Preserve its input,
expected effect and actual result. Follow the concrete caller, condition, state change
and owner response before assigning responsibility. A tool, fixture, contract or evaluator
can be defective. Do not label every failure a model error. Use the smallest reproduction
that retains the disputed dependency; preserve preceding turns when that dependency needs them.

Route a known contract to its existing code or owner oracle. Route an unknown engineering
quality question to case inspection and, when needed, the existing evals skills. Use
`error-discovery` for an actual interactive human annotation task, not to rename an Agent’s
own notes as human open coding. Use `eval-audit` for an existing pipeline. Keep a proposed
failure category provisional until the relevant quality owner reviews actual cases.

Keep these data uses distinct in `evaluation.dataset_use`:

- `case_review`: a scoped engineering lesson, including retrospective review.
- `error_discovery`: examples and original notes used to investigate possible failures.
- `evaluator_validation`: labeled cases assigned to assess a particular evaluator.

Do not promote one use by renaming it. Before claiming evaluator validation, retain the
actual expert labels, criterion version, grouped train/dev/test assignment and untouched
test results. The installed `write-judge-prompt` and `validate-evaluator` methods own that
work. Show per-class errors and unresolved disagreements. This requirement applies to
judge reliability claims, not ordinary code review or deterministic owner checks.

For the user’s experience, keep a separate human prediction before revealing the outcome
or Agent judgment. If no human answer exists, retain null. When expertise is missing,
prepare the code, trace and competing explanations for a qualified reviewer; continue
facts that code can resolve. Record whose judgment settled which question. An Agent’s
review may assist practice but cannot certify that the user acquired Staff experience.

For Soodles cost, reuse Test Manager’s normal measurements and necessity decisions.
Bind the observation to the operation and task it serves. Keep missing cost unknown.
Send resulting evidence through Schema Manager’s existing feedback interface and consume
its next action. Do not turn a fast DAG projection into a forecast of external success.
Trigger repair only for a supported defect or design risk within the existing owner’s
scope. A long task alone supplies neither a defect nor permission to remove its controls.

For a proposed abstraction plus lint rule, use [the abstraction feature](../features/abstraction-review.md) before promotion:
identify the invalid choice it excludes and a valid alternative it preserves. Compare
normal-use verification, repair and maintenance costs when observations exist. Fewer lines
or tokens alone cannot prove design quality; no new cost benchmark is required for prose.
