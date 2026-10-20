---
name: alg-leetcode-mental-simulator
description: Source-grounded LeetCode/code interview Zero Context explanations using the user-provided ALG-LeetCode Mental Simulator v4.0. Five anchors, English invariant, program movie, code-first single-turn four passes, reconstruction oracle, correctness, transfer and English interview. Not a universal article format or learner-mastery oracle.
---

# ALG-LeetCode Mental Simulator v4.0

## Entry and applicability

Select this Skill when the original task requests **a LeetCode problem, an algorithmic coding interview, or an algorithm-specific Zero Context tutorial** with v4-style reconstruction. The registered [medium-writing](../medium-writing/SKILL.md) remains the article writer/CLI owner. This Skill provides a **scoped teaching contract** and never creates its own writer, Stage, scheduler, CI state, model router, publishing authority or learner grade.

Read the [full operational v4 contract](references/v4-contract.md). Read the [article style/source boundary](references/medium-reference.md) when a Medium-style example or granular explanation is requested. To see one complete adapted output, read [LeetCode 49 Group Anagrams example](../../../examples/leetcode-49-group-anagrams-zero-context.md) and its [replayable Python reference](../../../examples/leetcode-49-group-anagrams.py). The example is a *reference*; do not copy its state, invariant, number of loops or complexities into different problems.

## Keep writing routes separate

- **LeetCode full default:** `FULL_SINGLE_TURN`; zh-TW explanation, English invariant and interview narration, Python 3 reference; five anchors exactly; one complete answer, four distinct passes and on-page Oracle. Only explicit `/interactive` may wait for a learner turn.
- **General engineering/More Route article:** use the transferable [invariant-centered Zero Context lens](references/v4-contract.md#transferable-zero-context-lens), **not** mandatory five anchors, Python code, exact 14 sections, or a LeetCode-specific proof. Its actual Reader Decision Points come from the chosen Domain and evidence.
- **CEFR ALG Four-Pass frozen lesson:** [alg-four](../alg-four/SKILL.md) is the new English-acquisition lesson owner. The
[previous CEFR four-pass](../cefr-alg-four-pass/SKILL.md) remains an exact-pinned historical frozen package and its existing native attempt-before-reveal policy is unchanged. Do not rewrite its vendored files or apply the single-response Oracle exception inside its live gated session. An article may include a printable same-page oracle without claiming its controlled CEFR practice has run.

## Source, truth and handoff

The original user-supplied v4.0 specification is the **task source**; the linked Medium example is a style pointer and is not executable authority. Read exact LeetCode problem constraints, Python semantics and available code before asserting invariants, asymptotics or result. Keep `MENTAL_TRACE` separate from a genuinely executed `RUNTIME_TESTED`, and `ACTIVE_RECALL_EXERCISE_PROVIDED` separate from observed learner reconstruction or mastery.

For original article delivery, preserve [medium-writing](../medium-writing/SKILL.md): source-backed English drafting, existing sloptrim+editorial handling, Traditional Chinese final with unchanged English technical terms, article compiler's actual Stage 0–7 or supported revision path, and optional site deployment/owner readback. This Skill does not replace those steps. The English invariant and interview pack are content inside the source-grounded draft/final, not evidence that these steps have run.

## Response outcome

Produce a complete, self-contained explanation in the [contract order](references/v4-contract.md), with one traceable failure and one valuable changed constraint. A correctness argument is only valid under its listed contract/assumptions. Ensure readers can reconstruct the **why** behind each data structure and operation; reject decorative vocabulary paragraphs that do not affect a decision or runtime behavior. When no real learner attempt is observed, report learning state as unverified.
