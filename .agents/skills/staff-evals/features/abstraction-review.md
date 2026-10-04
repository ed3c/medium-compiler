# Evaluate abstractions and constraints

## Sub-features

Use observed engineering decisions to assess whether an abstraction reduces unnecessary
choices while preserving required behavior. Evaluate strict rules against both forbidden
and legitimate implementations. More abstractions are not an objective by themselves.

## How to get to it (user POV)

Select a case, repeated failure or proposed design rule. Ask Staff Evals what belongs in
an existing API/type boundary, lint/CLI check, contextual guidance or further investigation.
Read the task's constraints and current enforcement before recommending another mechanism.

## Driving it with source review and the target's checks

1. State the concrete invalid decision, its consequence and the valid choices that must remain.
   For a hypothesis without observations, keep it proposed and specify a discriminating check.
2. Trace the existing owner/API/type/lint/test. If it already enforces the invariant, map to it.
   Prefer Shape: make invalid states hard to express through types, ownership or a narrow API.
   Use Guard for a decidable violation that Shape cannot remove. Use Guide for contextual choice.
3. For a Guard, name its predicate, input, enforcement point, owner and actionable diagnostic.
   Check a real violation, a valid alternative and a boundary/exception case. A static lint
   cannot prove runtime freshness, external effects or architectural quality by itself.
   Use owner readback or runtime checks for freshness and effects. Review architecture through
   constraints, tradeoffs and the relevant executable invariants. Keep exceptions explicit and owned.
4. Compare the simpler existing solution with the proposed abstraction. Trace caller, input,
   hidden state, ownership, effects, error/recovery and migration behavior. Freeze a prediction
   of which failure disappears and which valid behavior remains before the trial.
5. Compare like tasks under recorded agent/model/harness/tool conditions. Disclose P-only,
   code-only or combined changes; a combined result cannot isolate the prompt's effect.
   Measure correctness, regressions, false rejections, retries and decision burden. Record
   actual context/input/output tokens, tool calls, review time, repair and verification cost
   when available. Fewer source lines do not prove lower total tokens or cheaper repair.
6. Retain the result in the case and index. Promote only the supported invariant, with its
   applicability, counterexample, owner and check. Retest on a held-out task before claiming
   transfer. Keep a narrow local improvement local when broader evidence is absent.
7. When changing P-class, apply review-writing to the saved reasoning and consumer behavior.
   Follow instruction-feedback through the existing Soodles response and owner consumption.
   When changing code, retain target tests, relevant regression checks and delivery readback.

Use the experience seed as a source review: a missing owner snapshot in a test fixture
does not justify a global rule requiring every test to boot a live Noodle. Compare a narrow
preclaim test seam with complete disposable owner evidence, including each option's coverage.
This is a review exercise; do not modify the frozen oracle or start a live owner.

## Gotchas

Known invariant: use its existing oracle; use write-code-eval only for a missing objective check.
Unknown failure modes in traces: use error-discovery and retain actual human annotations when
required. No traces: collect authorized observations or use labeled synthetic discovery data.
Pipeline trust question: use eval-audit. Unclear method: use evals-start. Use write-judge-prompt
and validate-evaluator only for remaining semantic judgments with genuine calibration data.
These methods also verify changed P-class; review-writing and evals are not exclusive routes.

Preserve minimum sufficient implementation context behind the abstraction. A clean interface
is useful for normal use, but debugging still needs access to its implementation and failures.
Cheap code generation does not establish cheap data recovery, migration or production repair.
