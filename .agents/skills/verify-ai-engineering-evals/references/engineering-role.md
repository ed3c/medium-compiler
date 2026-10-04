# Engineering review responsibilities

- [Reconstruct the task](#reconstruct-the-engineering-task)
- [Apply engineering concerns](#apply-the-relevant-engineering-concerns)
- [Choose the next check](#decide-the-next-useful-check)
- [Write engineering feedback](#write-useful-engineering-feedback)
- [Source notes](#source-notes)

Use one accountable AI Evals Engineer role. Select the concerns needed by the case;
do not create a mandatory multi-agent team or a new approval pipeline.

## Reconstruct the engineering task

Start with the actor's problem, expected observable behavior and actual constraints.
Read the selected Issue/requirements, design rationale, affected code and test contracts.
Name which source defines the requirement and which only describes a past result.
Explain the subsystem's purpose before judging a local decision. Follow one concrete
input through the entrypoint, calls, condition, state, effect, failure and recovery.
Use exact file/symbol references, relevant input/output fields and small code excerpts.
Keep unfamiliar domain terms with their definitions and role in that execution path.

For Soodles, establish the selected revision's actual division of responsibility among
Session, Soodles owner, Noodle and providers. Identify the existing writer of each
affected mutable fact and the legal continuation entrypoint. Do not import the older
`ed3c/noodles` repository's implementation into `ed3c/soodles` by analogy.
Use the target's definitions of N/P/L/R; explain only the classes touched by the case.
The affected authority/evidence graph is not a mandatory N → P → L → R state machine.

## Apply the relevant engineering concerns

| Concern | Work to perform | Evidence limit |
| --- | --- | --- |
| Hands-on reviewer | Trace code, patch and runtime decisions against requirements; identify correctness, edge cases and maintainability consequences. | A plausible implementation does not prove execution. |
| Debugger | Reconstruct symptom, reproduction, hypotheses, discriminating observations, root cause, repair and regression check. Inspect failed attempts and whether they produced new evidence. | Separate an observed failure from a proposed cause. Missing reproduction limits the cause claim. |
| Architect | Inspect ownership, dependency direction, state authority, lifecycle, failure isolation and interface depth. Compare a simpler feasible alternative and its cost. | File length and symbol graphs can guide investigation; they do not prove design quality or behavior preservation. |
| Verification engineer | Distinguish observable-behavior regression checks, oracle sensitivity, architecture invariants and provider readback. Inspect what each check executes, mocks and cannot see. | A green suite, mutation result or hash proves only its own scoped property. |
| Evaluation engineer | Read actual inputs, tool observations and outputs; explain task-local Agent choices, counterevidence and uncertainty. Inspect evaluator validity when it affects the verdict. | A final report is not a full trace; different inputs do not isolate a model or prompt effect. |

These are review responsibilities, not separate product owners. Verify a scope with its
existing owner and oracle. The evaluator does not obtain mutation or admission authority.

## Decide the next useful check

For an existing deterministic contract, inspect and use its oracle. Do not delay it
for trace quotas, a new rubric, or a model judge. For unknown behavioral quality, inspect
real observations before forming categories or attributing the cause to instructions.
Consider code, CLI discoverability, owner projection, stale state, tool schema and carrier
as competing causes when the evidence supports them.

When recommending a change, check the existing system first. If the invariant is already
encoded, map to it. Otherwise prefer repository/API shape, then a deterministic guard;
leave contextual judgment in guidance. Do not translate every design observation into
a new gate. Separate invalid states, deliberate debt ratchets and investigation signals.

For a refactor, identify the observable contracts that must remain unchanged. Check
before/after behavior and relevant architecture invariants. Code-intel helps locate
a seam; it is not the equivalence oracle. Mutation or fault injection tests whether an
oracle detects meaningful errors; it does not establish refactor equivalence or provider
completion. Use changed, risky semantic surfaces to choose those checks. A pure move
does not automatically require exhaustive mutation. Explain relevant surviving mutants
instead of optimizing a global score.

For Agent debugging, distinguish safe waiting from an unproductive retry. Read the
current owner state and the new observation needed to proceed. When attempts repeat
without new evidence, recommend a bounded change of strategy, narrower task or the
missing owner input. Do not demand an unauthorized operation to obtain a fuller trace.

## Write useful engineering feedback

For each consequential decision, explain:

1. The requirement and concrete failure or success condition.
2. The code/trace location and what happened at that point.
3. Why that choice follows from the constraints, or which premise fails.
4. The runtime consequence and credible counterevidence.
5. A feasible alternative, its tradeoff and the smallest justified correction, if any.
6. The existing check or next observation that could confirm or overturn the judgment.

Use these connections within coherent prose; do not force six headings per finding.
A reader should be able to inspect the cited code and challenge the judgment. A report
that only says "source-bound", "owner respected", or "NOT_ASSESSED" leaves that job undone.
If only source is available, perform a source review and explain the missing execution
observation. Do not pretend to have observed Agent debugging. If only reports are
authorized, evaluate that slice and name which implementation question remains open.

Keep software correctness, Agent behavior and evaluator adequacy distinguishable.
Use the job's seven dimensions as a final coverage check, not a universal grading rubric.
Missing capture limits the associated claim; it does not erase code facts already checked.
Retain an actual tradeoff or counterexample instead of expanding generic eval terminology.

## Source notes

The user selected these Notion engineering notes. Read on 2026-10-04. They supply design
principles, not evidence that Soodles implements them. Their native verification state
was unverified. The role and workflow above are this skill's adaptation, not a quotation
or a claim that the notes prescribe this exact job role.

- [Agentic Engineering Quality Laws](https://app.notion.com/p/3ce3cec038da8076aa24f97dd5bb6411):
  Q1/Q2 support making the correct path easier and mechanically enforcing decidable
  invariants; Q3 separates gates, debt and signals; Q5/Q6 separate truth owners and
  acceptance; Q7/Q8 distinguish semantic seams and test sensitivity; Q9 bounds repair.
  Its historical examples concern `noodles`; check Soodles source before applying them.
- [noodles Refactor Safety](https://app.notion.com/p/3cf3cec038da812fa7a9fe4e5ff3eccf):
  sections 2–6 separate discovery, behavior preservation, oracle sensitivity, architecture
  and admission; sections 7–8 distinguish role concerns and source claims from adaptation.
  Cleaner, Architect, Hardener and QA are distinct concerns, not a mandate for four agents.
- [Hamel & Shreya: Semantic Degradation × Soodles N/P/L/R Closure](https://app.notion.com/p/3e33cec038da811fa26cf4dda7269459):
  the two starting paths preserve known deterministic contracts and open discovery;
  "four misreadings" calls for minimum sufficient evidence rather than minimum tokens;
  closure covers the affected authority/evidence graph, not an automatic full-repo audit.
- [Agent-Friendly Architecture: Domain Context Pack v0](https://app.notion.com/p/3cc3cec038da818c8708eb6eac9a9f46):
  Shape → Guard → Guide and the Promotion Gate require checking existing enforcement
  before adding mechanisms. The page is explicitly staging, not runtime-verified.

Re-read the relevant source if its meaning is disputed or this adaptation changes.
Do not copy the whole Notion corpus into each evaluation. Select only the engineering
context needed for the current decision and retain source locations and uncertainty.
