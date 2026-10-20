# Construct a Zero Context algorithm article

Use this method inside the [complete-article profile](article-content-profile.md).
The profile owns coverage, language order and handoff. This reference explains
how its Content Owner builds the reasoning, including when no model article is
provided. These are authoring actions, not new compiler stages or required
public headings. Keep working notes outside the copyable article.

## Derive the explanation before choosing its headings

Start from the actual statement, constraints and result contract. Work one
small input by hand and describe what makes its output correct. Try a nearby
input that separates a plausible shortcut from the required behavior. Use
that difference to ask what information the algorithm must retain and what
it can safely forget. Derive the representation from that need; do not start
with a data structure name and rationalize it afterward.

Write a short causal spine in the author's notes: the required result, the
constraint that permits a choice, the information represented, the operations
that preserve it, the stopping condition, and the returned result. Where an
algorithm discards candidates or reuses a partial answer, explain what
justifies that action. An equivalence key is useful for some problems, but is
not a universal spine. A checkpointed search interval, unresolved obligations,
reachable states or an optimal subproblem value can play different roles.
Choose from the current problem rather than copying this list as an outline.

Inspect the spine in both directions. Forward: can the input reach the result
through the stated state changes? Backward: what must already be true for each
operation and for the final return to be valid? Turn a missing premise into a
reader question. Order the explanations so that the reader learns that premise
before relying on it. A sketch of dependencies is useful when the relations are
hard to see; a diagram or a separate planning file is not mandatory.

Fix the reader's actual prerequisites. Knowing Python syntax does not establish
knowledge of the chosen algorithm, library behavior or cost model. Introduce
an unfamiliar term at the point where it answers a reader question. Expand a
runtime detail when it explains a choice, a state change, correctness or cost.
Stop expanding once those relations follow from the stated prerequisites and
documented semantics. Do not recurse through unrelated internals or require a
glossary chapter before the problem has a purpose.

## Build worked states that explain the mechanism

Choose witnesses from the algorithm's actual branches and proof obligations.
A successful example should expose the mechanism, rather than merely produce
the advertised answer. Add a short separating example when the main trace
cannot show rejection, repeated state, a boundary or why a shortcut fails.
Check that each witness satisfies the selected input contract. Call a
counterexample *minimal* only if its stated size convention and minimality
have been checked; a small distinguishing example is sufficient.

For a material transition, explain what the current state means, why the next
operation is permitted, its concrete operands, and the resulting state. Name
what the operation returns, mutates, allocates or leaves unchanged when that
distinction matters. Then explain why the next operation uses that result.
For a library call, connect the actual expression to its documented behavior;
do not leave an API name detached from its role in the algorithm. Distinguish
language guarantees, qualified implementation facts and conceptual diagrams.
If a source does not establish an internal detail, omit or qualify that detail
instead of inventing an exact runtime trace.

Interleave these explanations with concrete values. Do not replace the chain
with either a list of definitions or a long state dump whose transitions are
unexplained. Keep names, operation order and states consistent across prose,
figures and the complete runnable solution. Give an early orientation, then
let the developed explanation make the compact code understandable. A source
link supports a claim; the body still needs the explanation required by this
reader. A closing Master Map can recall this chain, but cannot repair it.

Derive the correctness argument from the same states. State the checkpoint
and what the state represents there. Explain why it is true initially, why
each branch preserves it or validly rejects, and why termination establishes
the result. Connect the failure example to the exact premise that the wrong
approach breaks. A changed constraint must change a premise and motivate a
specific adaptation, rather than simply attach another problem at the end.

## Derive cost from the operations the reader just followed

Define the input-size variables and the execution assumptions before using
Big O. State what a unit of work and a stored unit mean in this model, including
the range or representation that makes a scalar operation a unit. This is a
model for comparing growth, not a claim that Python instructions take equal
physical time. It gives the explanation a stopping point at declared elementary
operations; it does not require a proof of hardware or memory allocation.
Count how often the actual operations occur, how much each costs and
which allocations survive. Derive a logarithm, amortized bound or reuse bound
when the reader would otherwise have to memorize it. Explain the changing
quantity and why the bound follows; do not infer quadratic work merely from
nested syntax or constant work merely from one source-code line.

Keep an assumed elementary cost separate from a property of a growing data
structure or a sequence of operations. For a nonconstant cost or an aggregate
bound that the argument needs, explain the size-dependent work and why its
total has that bound. A concrete small sequence can make the mechanism visible;
also explain why the relationship continues as size grows. Naming a series,
amortization or a source theorem is not that argument. Qualify implementation
claims using the actual source and operation pattern. A bound for a restricted
sequence cannot be reused for a different update pattern without justification.
Do not declare an unfamiliar structure's central performance property a unit
cost merely to avoid explaining the comparison that motivated the algorithm.

Keep variable-size work distinct from fixed-size work. For unequal inputs,
derive the total or a justified bound before offering a conventional shorthand.
Check empty or smallest legal inputs and distinguish worst-case, expected and
amortized claims. Account separately for retained auxiliary state, transient
state and returned output when their conventions differ. Compare the relevant
alternative through the same result contract and cost assumptions. The reader
should see which changed condition would reverse the choice.
For an alternative, reconstruction or output builder, separate what it retains
from what it changes. Count the added and removed operations and the state
that remains live. Reuse a bound only after explaining why its operation
frequencies and primitive-cost assumptions still apply. A similar result or
the same problem name does not establish that reuse.

Apply the prerequisite check to caveats, alternatives and output analysis too.
Explain each new symbol's role and technical qualifications when introduced, even
if they occur after the main solution. Where deeper machinery is unnecessary,
state the limitation in plain language without losing its condition or scope.
A correct formula or qualification can still leave a novice unable to follow
the explanation.

## Reconstruct, then edit and translate

After a complete English draft exists, read it without the planning notes or
reference example. Identify the proposed approaches and conditional adaptations actually
introduced anywhere in that draft, including prose after the main cost section
and methods without code. Do not reconstruct this scope from the original
outline: the finished article may have added another claim.

For each proposed approach, reconstruct the condition that permits it, the
meaning of its retained state, its material updates and result, and the work
and storage that those operations require. Locate the exact body passages
supporting that reconstruction in the existing private author review. Then
check the inference between those passages, not just their presence. Work
backward from each cost conclusion: which operation counts and per-operation
or aggregate costs make it follow, under which size and sequence conditions?
For each necessary dependency, distinguish an explained body argument from a
declared elementary cost assumption or an unresolved claim. Follow an unfamiliar
dependency until it reaches the stated reader prerequisites or the explicit
elementary model; do not stop at a sentence that restates the desired bound.
If two claims only justify each other, neither closes the explanation.

Try to rebuild that argument using only those passages. Show the connecting
calculation or reason in the private review, and identify anything supplied
from memory or source notes rather than the body. A quotation, source citation,
successful runtime or author confidence establishes no missing inference.
Repair such a dependency in the body before approval, or keep the affected
claim incomplete. The review needs no new fields or exhaustive inventory of
every CPU operation. When a method reuses an earlier argument, name the preserved
premise and explain why the new operations or state do not invalidate it.
Check auxiliary, transient
and output storage under the article's stated convention. A global "cost
checked" label or a correct main solution cannot stand in for this review.
These notes need no new schema, compiler status or public checklist.

A short boundary comparison need not become a second full implementation.
Explain enough to support the claims it makes, including a storage or speed
trade-off; do not silently treat it as exempt because it has no Big O formula.
Keep the required relevant alternative and changed-constraint pivot. Do not
delete them, rename them as a caveat, or replace their reasoning with a link
to make the review appear complete. Unrelated internals remain out of scope.

Also reconstruct a new small input, why important updates or discards are
valid, progress and termination, and the concrete failure of a tempting
alternative. Use the article's premises, not the author's background. If a
needed passage is absent, keep that part of self-review incomplete, repair the
earliest missing premise or transition, and recheck dependent code, examples,
proof and costs. Preserve the first complete draft and the actual repair;
repeating a conclusion does not repair a missing causal link.

Follow the profile's actual English editorial and semantic approval route
before translating. Review an editorial cut against the reasoning it enables,
not only against retained keywords. Mechanism explanation, a worked example,
code mapping and short English interview recall do different teaching work.
Retain useful recurrence while removing repetition that adds no understanding.
Before approving the edited English edition, repeat the reconstruction for
any method, claim or premise added or changed since the earlier review. Read
the final body, including its alternatives, caveats and closing recall. Do not
carry approval forward solely because the main code and formula are unchanged.

Translate the approved edition, preserving code, values, links, conditions,
negation, technical terms and the English interview practice. Check passages
that carry decisions, exceptions and state changes against the English text.
Make figure captions describe their actual assets; a rendering brief is not a
rendered figure. A language or figure defect returns to this Content Owner
before the existing formatter admits the new edition.
Check the same method-specific passages in the translation. Record unresolved
gaps separately from bilingual agreement: both languages can preserve the
same missing explanation.

## Observe transfer without mistaking a sample for reliability

An exemplar can calibrate the reader depth and presentation. Reverse-engineer
its useful teaching actions and the relations they explain, not its topic
sequence, APIs, algorithm or number of sections. Keep that case separate from
this method. When a user supplies a complete reference, the profile still
requires its material teaching work to be accounted for and technical errors
to be corrected.

When evaluating a changed method, include a fresh task from a different
algorithm family with only the selected instructions, problem and primary
sources. Do not provide the polished exemplar or problem-specific outline to
that Writer. Preserve its first output and any later repairs separately. An
independent article-only Reader reconstructs answers with exact supporting
passages and marks missing information rather than supplying prior knowledge.
The observer checks those passages, concrete states and executable code;
author self-review and a Reader's report are distinct evidence.

Repeated uncoached tasks and different proof/runtime mechanisms can expose
whether the method depends on a particular example. Record what was actually
sampled, failures, interventions and remaining gaps. Do not infer stable
general performance from a polished example, one successful transfer, a small
sample, a detector score, a compiler receipt or an uncalibrated model verdict.
Human understanding remains unobserved without actual learner evidence.
Stop revising when no new supported defect changes the method or its checks;
continue the original authorized handoff and report the measured scope.
