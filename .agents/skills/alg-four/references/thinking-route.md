# Thinking Route applied to English acquisition, not a second router

The current Soodles Thinking Router is a **design reference** for Goal, Measurement, Effort Horizon, First Causal Breakpoint, V2 default and conditional V3. It is not a guaranteed dynamically installed skill and does not introduce a new tool or Owner.

## Stable Goal and questions

**Goal:** A learner can *retrieve*, in natural English and with minimal prompting, each engineering decision and core runtime mechanism from the selected source article, explain why it follows from constraints, and respond correctly to changed assumptions. The article may be complete without the learner having met this goal.

**Measurement:** Actual English response transcription or text, response latency measured from cue to onset or to complete explanation (identify which), author/reader-assessed technical invariant + actor/condition/negation coverage, next-day and later recall where evidence exists. No invented ms target, baseline, achieved mastery or long-term improvement.

**Effort Horizon:** The selected article and its source-bounded English lesson; no automatic repeated schedule or extra model agents.

## V2: one necessary intervention

1. Determine the first **observed** breakpoint: recognize meaning, comprehend engineering reasoning, generate the English explanation, preserve semantics, or speak promptly.
2. Choose one differentiating probe: contextual re-encounter, causal explanation, diagram-to-English retell, source-diff, premise mutation, or timing.
3. If the learner has not attempted anything, mark the breakpoint **UNKNOWN** and provide the complete four-pass study material. Do not infer inability from a model-written answer.
4. Select a minimal prompt or presentation change. Reuse the original source-bound oracle. No duplicate Skill router, per-word Method selection, schedule or receipt authority.

## V3: bounded adversarial review only with a new falsifiable condition

For example, if the learner produces exact terminology rapidly but reverses a critical condition, latency alone is a bad outcome metric. Differentiate lexical retrieval from semantic reconstruction by comparing two otherwise equivalent cues. If the comparison does not change an action, return NOOP.

Ablation, where meaningful, compares the same decisions under context-only versus source-cued reconstruction versus active recall using comparable source conditions; avoid removing source safety facts or real learner authorization. A single demo, an LLM success sentence, a printed oracle, or one fourth pass does not establish causal improvement.

## Passive and Active as overlapping content roles

A selected claim can appear in both groups. For example:

- Receptive: “The mutable frequency list is converted into a tuple before the dictionary lookup.”
- Active cue: “Why freeze a mutable working state, and what exactly guarantees hashability?”
- Oracle: “A list is not hashable. After counting, a tuple of integers is hashable and serves as a stable canonical key, while dictionary key equality—not hash equality alone—determines grouping.”

The goal is English recall plus *correct engineering mechanism*. A learner who sounds fluent but invents a runtime property has not satisfied the source contract.
