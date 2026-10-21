# ALG-LeetCode Mental Simulator v4.0 — operational contract

This is a repository-local, scoped adaptation of the user-provided **Five-Anchor / Invariant-Centered / Program-Movie / Answer-First / Single-Turn Four-Pass** specification. It is not a separate system-role prompt or permission grant.

**Profile selection:** The mandatory 14-block order, exactly-five anchors and same-response printable Oracle apply to the ordinary v4 teaching profile. A user request for a complete publishable Medium article selects the sibling [complete-article content profile](article-content-profile.md), which retains the underlying algorithmic truth requirements but produces one nonduplicative narrative and owns its semantic English/zh-TW contents before medium-writing formats it. Do not reinterpret the original teaching contract as 14 mandatory Medium headings, or silently turn a selected Four-Pass learning session into a Medium article.

## Runtime defaults and exception

| Parameter | Default |
| --- | --- |
| MODE | FULL_SINGLE_TURN, unless explicit /compact, /review, /bugfree, /interview, /cold-interview or /interactive |
| EXPLANATION_LANGUAGE | zh-TW |
| INTERVIEW_LANGUAGE and INVARIANT_LANGUAGE | English |
| CODE_LANGUAGE | Python 3 |
| LEARNING_DIRECTION | TOP_DOWN: whole before parts |
| REFERENCE_ANSWER | REQUIRED and visible near the top |
| FIVE_MEMORY_ANCHORS | EXACTLY_5 (for LeetCode cases only) |
| FOUR_PASS_LOOP | SAME_RESPONSE, even when a recall prompt is included |
| ORACLE_ANSWER | SAME_RESPONSE, with reveal affordance if the medium supports it |
| INTERVIEW_OUTPUT | REQUIRED |
| EXECUTION_TRUTH / SCIENTIFIC_HONESTY | REQUIRED |
| PRIMARY_SOLUTION | Explicit interview-friendly; never compressed one-liner merely for brevity |

Except under **explicit** /interactive, do not ask a prediction then stop, withhold the solution, wait for the learner, split Passes 1–4 into turns, or terminate after a practice exercise. Oracle on the same page is a *learning document* behavior, not a substitute for the separate CEFR gated interactive runtime.

## Mandatory 14-block LeetCode output order

1. Five-Anchor Memory Card
2. Invariant Memory: English Full Proof Form, Compact Memory Form, Recall Cue; one brief zh-TW intuition
3. Program Movie: a small discriminating input, about 5–7 scenes including initial state, motion, decision, mutation and terminal/fallback meaning
4. Reference Answer: full, readable Python 3 code, not a one-liner
5. Pass 1 — Whole Encounter
6. Pass 2 — Structural Compression
7. Pass 3 — Top-Down Back-Compilation
8. Pass 4 — Active Reconstruction + Oracle Diff
9. Correctness Proof (Initialization, Maintenance, Early and Exhaustive Termination as applicable)
10. Complexity and Assumptions
11. Bug Alarm and Minimal Counterexample
12. What-if Pivot
13. English Interview Pack
14. Spaced Recall Card; end with honest Learning/Execution Status outside the card

Use clear prose rather than mechanical jargon. The 14 blocks are a LeetCode teaching sequence, **not** 14 Session routing decisions, 14 new compiler stages or general engineering article section requirements.

## Five anchors — exactly five, one or two lines each

| Anchor | Memory question and required precision |
| --- | --- |
| Signal | Which wording implies which operation and pattern? `problem signal → algorithmic need → pattern` |
| State | What exact semantic information survives across iterations? The data-structure name alone is insufficient. |
| Invariant | A single English sentence at a fixed checkpoint, defining what has and has not been processed. |
| Transition | Correct query/branch/mutation/continue-or-return order; name a relevant ordering risk. |
| Bug Alarm | The first likely wrong operation plus a minimal distinguishing counterexample. |

Complexity, full traces, proofs, interview scripts, variants and alternative code belong *outside* this card. A learner should be able to replay the code using the card; this is a design intention, not an observed timing measurement.

## Invariant-quality and source contract

Prefer `Before processing index i, ...` / `At the start of each iteration, ...`. Identify: checkpoint, state meaning, processed prefix, excluded current/future, completeness. The invariant must support **Initialization**, **Maintenance** and **Termination**. Do not write imprecise slogans (e.g. “contains some past items”). Explain why correct early-return proves success and why exhausting the loop proves the fallback.

State the full English invariant once, its compact English form once, and one recall question; subsequent passes should reuse English directly instead of repeated translations. Teach the difference between input properties, chosen representation, runtime state and proof property. If an input includes only lowercase English letters, do not silently generalize a 26-slot key to arbitrary Unicode.

## Program Movie and reference solution

Opening → scanner/phase movement → membership/branch → state mutation → success/partial output → exhaustion/final output. A movie is a compressed truthful execution, **not** one cute analogy per code line. When an algorithm does not early-return, show the final result and the failure/no-match meaning actually supported by that contract. If two input strings map to one canonical key, show both key construction and accumulation; never imply the dictionary predicts future items.

Provide full readable code immediately after the anchors and movie. Prioritize visible state transitions and deterministic condition/mutation ordering. Code and trace must agree byte-for-byte on operations; add imports as required to be runnable. A successful mental proof without executing code remains `MENTAL_TRACE`.

## Four distinct passes (same answer)

**Pass 1 — Whole Encounter:** the known complete code, task input/output, chosen pattern/state, the invariant, one runtime movie, time/space and relevant assumptions; status only `PASSIVE_EXPOSURE`. Do not claim comprehension.

**Pass 2 — Structural Compression:** pick 3–6 function chunks; for each: *why this exists*, *what it reads*, *what it changes*, *what removing it breaks*. Then code-language-independent pseudocode. This is `STRUCTURAL_RECOGNITION` as a teaching opportunity, not independently assessed skill.

**Pass 3 — Top-Down Back-Compilation:** `Required Output → Success Event → Required Knowledge → Surviving State → Fast Operation → Data Structure → Transition Order → Termination`. Ask the key what/why questions and **immediately provide full answers**. Do not request a learner reply before proceeding.

**Pass 4 — Active Reconstruction + Oracle Diff:** provide 1–3 relevant exercises (blank skeleton, mental movie reconstruction, deliberate wrong-order bug). The same response must include an Oracle after a visible separator, or an optional collapsed reveal **within the same page**. Diff dimensions: initialization, query/condition, order, success action, mutation, fallback/final output, invariant, complexity. Without a real attempt, status remains `ACTIVE_RECALL_EXERCISE_PROVIDED`, `MASTERY_NOT_YET_OBSERVED`.

The Four-Pass learner-session compiler (`cefr-alg-four-pass`) uses a different progress model: it keeps oracle hidden until a recorded learner acknowledgement. Never weaken that existing policy by referring to this printable single-turn contract.

## Top-down engineering analysis

Declare only result-affecting contract elements: input, output, success/failure, constraints, mutation permission. Then name the brute-force baseline and the **repeated work** it wastes. Explain what state is stored, what operation becomes faster, what space or other cost is traded for time. Show temporal order where it changes correctness and the simplest wrong-order case.

Output first and structural understanding first. Do not require line-by-line guessing to reach the algorithm. Derive the code from what completion means and the information needed to decide it.

## Correctness and complexity

**Initialization:** prove the invariant on the empty processed prefix. **Maintenance:** show the state update exactly restores it for the next checkpoint; if returning early prove the required result. **Termination:** account for early and exhaustion paths independently when present.

Give **Time**, **Space**, and **Assumptions**, deriving costs from actual operations. Distinguish average hash complexity, worst-case theoretical behavior, amortized operations, sorting implementation memory and input mutation. Define `n` (number of items), `k` (max item length) and `Σ` (alphabet size) before expressions. Avoid `O(nk)` if a fixed per-item `Σ` initialization dominates and k may be zero; state `O(n(k+Σ))` with `Σ=26`, and only then simplify under the stated convention.

## First-divergence, what-if and interview

**Bug Alarm** names the first suspicious operation, runtime consequence, violated invariant, minimal separating input and minimal repair. One evidence-bearing bug beats a generic catalogue.

**What-if Pivot:** choose one meaningful constraint/output change (space, stream, duplicates, sorting allowed, character set, concurrency or proof assumption); specify what survives, what breaks, new state/method, new complexity and minimal implementation difference.

**English Interview Pack:** a natural 3–6 sentence approach (core pattern, state, success event, time/space), invariant stated in full, spoken correctness with Initialization/Maintenance/Termination, 3–5 live-coding narration sentences, natural complexity answer with assumptions, and one follow-up with complete model answer. Interview material follows the proven code, never invents additional behavior.

**Spaced Recall Card:** Day 0 replay movie; Day 1 recall five anchors/English invariant; Day 3 rebuild from blank; Day 7 identify minimal bug; Day 14 solve changed constraint and explain in English. These are prompts and suggested times, not reminders scheduled on the user's behalf or evidence of long-term learning.

## Modes and learner-evidence boundary

- **/full** = all fourteen blocks, no wait.
- **/compact** = shorter optional prose, but still anchors, invariant, movie, code, four passes, proof and interview.
- **/review** = Recall Cue → Exercise → same-response Oracle → Anchors → Interview Replay.
- **/bugfree** = stronger assumptions, boundary counterexamples, property-based test proposal and execution status.
- **/interview** = full English clarification/approach/code/tests/invariant/complexity/follow-up within this response.
- **/cold-interview** = candidate attempt framework + answer, still same-response.
- **/interactive** = *only explicit opt-in* to multiple turns, subject to the host/runtime's actual oracle/attempt policy.

Never conflate `L0 PASSIVE_EXPOSURE`, `L1 STRUCTURAL_RECOGNITION`, `L2 GUIDED_RECALL`, `L3 ACTIVE_RECONSTRUCTION`, `L4 TRANSFER_READY`, `L5 INTERVIEW_READY`. Providing the material is not learner performance. Do not claim guaranteed bug-free code, universal fixed-four-exposure acquisition, C2 mastery or a neurological learning law.

## Acceptance and rejection (QG-01–QG-20)

1. QG-01 Five anchors: exactly Signal/State/Invariant/Transition/Bug Alarm.
2. QG-02 Precision: five entries identify true state and discriminating bug.
3. QG-03 English invariant in position two.
4. QG-04 The same invariant supports the correctness proof.
5. QG-05 Movie is small, truthful and includes terminal meaning.
6. QG-06 Full reference code appears before explanatory Passes.
7. QG-07 Whole code precedes chunks.
8. QG-08 Passes 1–4 all appear in one answer.
9. QG-09 Fourth pass contains an actual fill/rebuild challenge and Oracle Diff.
10. QG-10 No learner-response wait except explicit /interactive.
11. QG-11 No false mastery/retention claim.
12. QG-12 Explain state meaning, not merely set/dict/list.
13. QG-13 Explain query/mutation timing where relevant.
14. QG-14 First divergence and minimal counterexample.
15. QG-15 Explain actual average/worst/amortized/hidden assumptions.
16. QG-16 Complete English interview approach, invariant, proof, complexity and narration.
17. QG-17 No filler or redundant line-by-line paraphrase that obscures mechanisms.
18. QG-18 Actual runtime only reported as tested when a real execution was observed; otherwise `MENTAL_TRACE`.
19. QG-19 No unsupported claim that precisely four passes neurologically guarantee acquisition.
20. QG-20 Same-turn answer, recall and Oracle all available without a learner reply.

**Semantic inspection** is required for mechanism, source boundaries, proof, and fidelity; a checker that counts headings alone cannot pass those claims.

## Transferable Zero Context lens

For general Systems/Agent/Database articles take these ingredients when applicable: **Answer/Architecture First → Whole Runtime Witness → governing Invariant or Contract → precise State/Owner meaning → causal design trade-off → first falsifying counterexample → minimal alternative → independently observable verification → reader reconstruction**. The number of reader decisions and representation steps follows the actual Domain, not the five LeetCode anchors or fourteen-block template. Never turn a teaching diagram into a live execution proof, and never let a prompt count become a new CLI/Owner gate.
