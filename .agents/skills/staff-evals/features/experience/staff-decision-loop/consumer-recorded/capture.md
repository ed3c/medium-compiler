# Consumer capture (self-report)

Consumer: AI assistant `/root/decision_recorded_consumer`. Review mode: `combined`. This document lists actual sources and operations performed by this consumer. It is not a complete independent platform transcript and does not claim filesystem isolation.

Scope was the recorded task, its nine selected instructions, eleven required evidence files and the non-case feature-map guidance needed to use staff-evals. I did not read other cases, observer files, sibling output directories or other worktrees. I wrote only the five requested outputs under `/tmp/staff-decision-loop/consumer-recorded/`. No product edits, product tests, suite execution, provider mutations, publishing or delegation were performed. Historical commands in observations.json were read, not executed.

## Sources read

Task: `/tmp/staff-decision-loop/inputs/recorded/task.json`, actual SHA-256 `2af1b599b0321950a94b76f2b727f26eab27a318454f48c5dbe3f88ececdc135`.

The exact nine selected instruction paths and actual digests are in `consumer-report.json`. All match task.instructions. I read SKILL.md, agents/openai.yaml, assets/experience-case.json, features/experience-review.md, features/instruction-feedback.md, features/report-delivery.md, features/workflow-review.md, references/engineering-role.md and references/experience-records.md. An initially combined tool result truncated a portion of engineering-role.md; I then reread that reference in full.

Additional method guidance: `/workspace/scratch/7ed56a5a2a33/medium-decision-loop/.agents/skills/staff-evals/features/README.md`, SHA-256 `e4c06a39410892c699d416c67ca3bfc133dee8fee2b54d8832e5c1344029a058`. This method file is deliberately outside the consumer-report instruction map. No linked case index or case was opened.

All eleven evidence files were read in full under `/tmp/staff-decision-loop/inputs/recorded/`: AGENTS.md, before-test.py, after-test.py, ai_evals_site.py, writing-verification.yml, observations.json, job-context.txt, delivered-assessment.md, failed-ci-jobs.json, passed-ci-jobs.json and patch-commit.json. Actual digests and evidence classes are in case.json; every digest matches task.evidence.

## Operations and observed results

1. Used ordinary shell `cat` to read the selected staff-evals SKILL.md and task.json. Both commands exited 0.
2. Ran a Python file-reading/hash script using pathlib, json and hashlib. It hashed task.json and all selected instructions/evidence, reported every expected hash matched, and printed the remaining selected instructions. Exit 0. Read features/README.md with cat, exit 0.
3. Reread engineering-role.md with cat. Ran Python to print line-numbered AGENTS.md, job-context.txt, observations.json, before-test.py, after-test.py, ai_evals_site.py and writing-verification.yml. Both commands exited 0. These line numbers supply assessment locators.
4. Ran Python to print line-numbered delivered-assessment.md, failed-ci-jobs.json, passed-ci-jobs.json and patch-commit.json, exit 0.
5. Ran `git rev-parse HEAD` in the specified medium-decision-loop directory: exit 0, output `ce5ed482e16917debb1f944c97d16b8afd0761bc`. Ran `git status --short` there: exit 0, reporting the nine selected skill files as modified. No unselected content was opened from that status.
6. Ran a Python read-only script calling `git show bc68aa025a26124ccbf6a0afc94c380dad4af0be:<relative-selected-path>` for each of the nine selected instructions. Each nested git call exited 128; the script itself exited 0. It printed match=false for these unsuccessful Git reads. It separately hashed the additional README, parsed before-test.py, after-test.py and ai_evals_site.py with ast.parse, and compared assertion-call ASTs. All parses succeeded. It found 12 old assertion calls, 16 new calls and 10 exact unchanged old calls. No imported product code or test was executed.
7. Repeated the SKILL.md Git read alone to inspect the diagnostic. It exited 128 with: `fatal: path '.agents/skills/staff-evals/SKILL.md' exists on disk, but not in 'bc68aa025a26124ccbf6a0afc94c380dad4af0be'`. I did not search other paths or cases to repair this discrepancy. Task-hash byte binding is verified; named-commit binding is not verified.
8. Sent the parent a concise findings/provenance status update and then clarified the exact Git diagnostic. These communications did not obtain other case evidence or change the judgments.
9. Created the requested output directory with `mkdir -p`, exit 0. Wrote assessment.md with a shell heredoc, exit 0. Wrote guide.md with a heredoc and case.json/consumer-report.json with Python, exit 0. The JSON script used the supplied experience-case template, actual input hashes, observed episodes and explicit null costs. No new prediction was invented.
10. Wrote this capture with an ordinary shell heredoc. Final file readback and structural verification are recorded below after execution.

The process record above is self-reported from this consumer's actual tool results. Raw supplied sources remain at their original authorized paths; no extra copies or files were written. Stdout from file reads was inspected in the tool results. No independent full platform/tool transcript was available to attach.

## Interpretation limits

The CI provider JSON is archived evidence, not a fresh provider query. Agent actions, focused test outputs, merge and deployment readback are coordinator-transcribed selected observations. The delivered Soodles assessment is reviewed as authored prose; this consumer did not retrieve its underlying source/logs or rerun its API projection. Provider job timestamps yield 11 and 20 seconds, but differing paths prevent a performance inference. Complete call counts, token use, model time and whole-task handling time are unknown. No measured waste claim, human skill claim, calibrated model ranking or prospective accuracy claim was made.

Final verification completed with exit 0: all five requested files were readable and nonempty; both JSON files parsed; the output directory contained exactly the five deliverables; the instruction map contained exactly task.instructions and every actual digest matched; the three response judgments were false/true/false; case.json retained five decision episodes, `combined` mode and a null retrospective prediction. This checked artifact structure and identity, not semantic quality or product behavior. The assessment, guide and recorded episodes were also compared against the already-read source locations during authoring. No further product verification was run.
