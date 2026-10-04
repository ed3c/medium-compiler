# Engineering review responsibilities

- [Reconstruct the task](#reconstruct-the-engineering-task)
- [Apply engineering concerns](#apply-the-relevant-engineering-concerns)
- [Choose the next check](#decide-the-next-useful-check)
- [Write engineering feedback](#write-useful-engineering-feedback)
- [Implement the job requirements](#job-requirement-implementation)
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

## Job-requirement implementation

The user's G2i job description defines the intended work. This mapping is our practical
adaptation, not G2i's private rubric. Select the concerns that the actual case can support.
Do not turn hiring conditions or missing evidence into invented engineering failures.

| Job requirement | Reviewer action and evidence | Judgment boundary |
| --- | --- | --- |
| Evaluate and improve coding systems | Inspect observed Agent choices and give a specific correction or justified retention. | A report or published site alone is not measured model improvement. |
| Not production-feature delivery | Deliver defensible evaluation and feedback; use a small reproduction or patch when it resolves the question. | Shipping a feature is supporting work, not the quality verdict. |
| Realistic, complex workflows | Keep relevant callers, shared state, dependencies, constraints and external effects. | Complexity comes from the task, not a forced trace length. |
| Evaluate end-to-end | Reconstruct observed understanding, exploration, implementation, verification and handoff. | Partial capture supports named episodes; missing spans remain explicit. |
| Engineering judgment | Assess problem selection, scope, risk, alternatives and stopping decisions. | Judge with information available at the time, not success alone. |
| Debugging quality and instincts | Trace symptom, competing hypotheses, discriminating checks, new observations and adjustment. | Repeating a check without a new premise is different from necessary waiting. |
| Reasoning clarity | Inspect the stated premise and evidence-to-conclusion link. | Do not invent hidden reasoning from correct code. |
| Architectural thinking | Compare ownership, dependency direction, failure isolation, migration and maintenance cost. | Names, diagrams and compliance do not prove a good abstraction. |
| Written communication | Write an actionable verdict in the requested language with evidence, consequence and correction. Assess English fluency only from actual English work. | A reader must be able to decide what to retain, change or investigate. |
| Attention to detail | Check versions, callers, input shape, units, edge cases, mocks and negative assertions. | A detail matters through its effect on correctness or judgment. |
| Developer trust | Compare completion claims with observed actions and current results; inspect correction of mistakes. | Honest limits support trust but do not fill the missing evaluation. |
| Nuanced subjective judgment | State a defensible position, its premises, counterevidence and applicable exception. | Uncertainty does not require neutrality between unequally supported choices. |
| Subtle response differences | Compare feasible alternatives under the same constraints and completion boundary. | Label unexecuted alternatives hypothetical; do not fabricate an A/B run. |
| Misleading, weak, incomplete or low-signal output | Locate the actual statement or action, failed premise and resulting bad decision. | Do not report a generic issue disconnected from the observed task. |
| Structured high-quality feedback | Link each material finding to the choice, code/trace, consequence and resolving check. | Matching required fields does not certify semantic quality. |
| Define great engineering | Retain a supported good behavior, failure contrast and legitimate exception for later cases. | Do not promote one case into an unconditional instruction. |
| Staff/Principal/Architect/Tech Lead experience | Review cross-component impact, durable interfaces, operational constraints and tradeoffs when present. | A skill, case count or model-generated report grants no seniority. |
| Deeply hands-on; strong fundamentals | Read the patch and relevant implementation; check state, errors, concurrency and language semantics. | Source summary alone is insufficient where a concrete claim can be checked. |
| Deep TS/JS, Python or Go expertise | Use one known stack deeply; verify unfamiliar semantics before judging. | Multiple shallow stacks do not satisfy depth; do not infer expertise from a test count. |
| High quality bar; confident judgment | Preserve important negative controls and challenge plausible but unsupported reasoning. | Do not invent defects or arbitrary numeric scores to appear strict. |
| Ambiguous, fast-moving work | Choose the next observation that changes a material decision and continue independent work. | Unknown input does not justify an unrelated full suite or architecture rewrite. |
| Complex debugging and large/high-context systems | Examine actual boundary interactions, state lifetime and recovery. | A small fixture cannot establish large-scale operational competence. |
| Technical leadership, review and mentoring | Explain why a correction works and what the implementer should recognize next time. | Feedback must teach a reusable decision without adding unnecessary rules. |
| AI-assisted workflows; Codex, Claude Code, Cursor | Read available tool use, context acquisition, retries, patch and final claim. | Brand use alone is not evaluation experience; no brand-specific trace is mandatory. |
| Quality and execution velocity | Track necessary versus uninformative investigation, rework and available elapsed/token costs. | Speed cannot compensate for omitted outcomes; unknown costs are not zero. |
| Technical review/calibration resembles the work | Review real code and choices, compare genuine expert judgments and retain disagreement. | Fresh AI feedback is not human calibration. |

Compensation, approximately two weeks, substantial focused availability, 40+ hours,
ASAP start, geography, English fluency, and security onboarding are engagement conditions.
Track them separately when helping with an application. Do not make them evaluator features.
The stated roughly five-hour handling time is context, not a minimum duration or pass gate.
Okta, Kolide, NDA and customer access require the real employer's onboarding. The company
background and evaluation-phase payment terms do not define engineering acceptance.

For code quality, inspect the actual API use, invalid states, error propagation, mutable
fixture sharing and maintainability consequence. A lint result is one bounded observation.
For cost-related decisions, Staff Evals judges the Agent's choice and its rationale;
Test Manager owns necessary verification and cost review; Schema Manager projects supported
facts and gaps; the original owner selects effects. Known-state millisecond projection is
not a forecast of engineering quality. Do not force every review into a prediction exercise.

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
