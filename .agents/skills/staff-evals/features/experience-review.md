# Accumulate engineering experience

## Sub-features

Review any coding agent's implementation. Retain the engineering decision, prediction,
observation and correction as a reusable case. Track the human and Agent separately.
Use cases to improve later judgments without turning historical explanations into forecasts.

## How to get to it (user POV)

Ask Staff Evals to review an Issue, PR, local diff or coding-agent trace and retain the lesson.
For practice, ask the human to record a prediction before revealing the Agent assessment.
Continue the Agent's own analysis when no human answer is available; human progress stays unknown.
Read [the record contract](../references/experience-records.md) and the relevant indexed cases.

## Driving it with file tools and existing verification

1. Bind the task, source revision, patch and available trace. Identify the observed actor.
   Reconstruct the code/runtime mechanism using the workflow-review feature.
2. Save a case using [the template](../assets/experience-case.json). Use a new case ID and
   retain exact evidence bytes and hashes. Record missing inputs and who made each judgment.
   For observed Agent work, add decision episodes with before-action evidence, actual action,
   stated reason, observation, reviewer judgment and alternative. Keep source-only findings
   outside the list of observed Agent choices. Preserve disagreement and later correction.
3. Before a new outcome, freeze a separate prediction file. State the condition, observable
   result, reason, falsifier and resolving check. Have the observer retain its hash before
   the check. Keep that ordering evidence. A self-entered timestamp is not independent proof.
4. Run the target's existing authorized check. Save actual argv, input identity, stdout,
   stderr, exit and owner readback. If execution is unavailable, leave the prediction open.
5. Append an outcome record referencing the frozen prediction. Compare result with forecast;
   distinguish confirmed, contradicted and unresolved. Never rewrite the original prediction.
   Review the causal explanation and counterevidence separately from matching output fields.
6. Index the case in `experience/index.json`. Link the case to its feature and relevant role
   concerns. Preserve previous versions and supersession when a lesson changes.
7. For a resulting P-class edit, use review-writing and instruction-feedback. For a target
   product correction, follow its existing implementation, verification and delivery owners.
   Record each completed and outstanding boundary; feedback PASS is not product closure.

Drive the retained retrospective seed by reading its JSON, bound stderr and cited code.
Verify file hashes, reconstruct the failure path and check its missing prediction status.
For a prospective drive, supply an unseen task outcome and retain the pre-observation freeze.
Success is a retrievable case whose conclusions and limits another engineer can challenge.

## Gotchas

Keep unseen cases out of prompt examples until their predictions are frozen and scored.
Split related tasks, retries and source revisions as a group to avoid train/test leakage.
Do not count a replay of a known result as new predictive experience. Report eligible,
resolved, unresolved and excluded counts before rates; explain selection bias and sample size.
One case cannot establish generalization, token savings or staff-level readiness.
The case store supports retrieval and reflection; it does not update model weights.
Retrospective judgment is useful experience even when no forecast exists. Do not force
predictions into every review or count output-field matches as independent engineering tasks.
