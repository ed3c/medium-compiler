# Consumer capture

This is consumer self-report, not a complete independent platform transcript. It records the sources and operations used for this source-only review. Native shared files do not provide filesystem isolation. No claim of independent capture is made.

## Actual sources

- Task: `/tmp/staff-decision-loop/inputs/source-only/task.json`; SHA-256 `ca1ca5dc65e877980cfab9066ab835d606213d1f27c4c93a520c6fdaaffa23a2`.
- The task supplied the target and skill revisions. File hashes were verified against the supplied manifest; no target checkout or other worktree was inspected.

Selected instruction files (exactly these nine enter consumer-report.json):

- `/workspace/scratch/7ed56a5a2a33/medium-decision-loop/.agents/skills/staff-evals/SKILL.md` — `80dfb9ca406c3dcfbed4f49ffe24dd23b20967d209f33e2e8ce5bbb1ee7a9c23`.
- `/workspace/scratch/7ed56a5a2a33/medium-decision-loop/.agents/skills/staff-evals/agents/openai.yaml` — `9a9e40998bbcb1db04899e58cada8a7bcac4bfd4cc02d757bc70fccc4a34fa6b`.
- `/workspace/scratch/7ed56a5a2a33/medium-decision-loop/.agents/skills/staff-evals/assets/experience-case.json` — `ca0808d65fd27e8e37169f8b2c2332e960d167887c4277ff4c21d19c673fd65e`.
- `/workspace/scratch/7ed56a5a2a33/medium-decision-loop/.agents/skills/staff-evals/features/experience-review.md` — `a2830cc3cab9bab67cf421fd65c4d2501daa1681f7884b7373e91aba9a1b86f0`.
- `/workspace/scratch/7ed56a5a2a33/medium-decision-loop/.agents/skills/staff-evals/features/instruction-feedback.md` — `8a5391277c74b7e442e1f86fe7b28852eeb5541e215e312c385cd1393ad4292b`.
- `/workspace/scratch/7ed56a5a2a33/medium-decision-loop/.agents/skills/staff-evals/features/report-delivery.md` — `1102511a34cacdb0c2c3924550594e10a3761fb78d7ca9b0e47edce96466171d`.
- `/workspace/scratch/7ed56a5a2a33/medium-decision-loop/.agents/skills/staff-evals/features/workflow-review.md` — `149f2eba07df7a692ae4a6eadb6acd3c163446f64e2bdc6ca9b02f2472ed603b`.
- `/workspace/scratch/7ed56a5a2a33/medium-decision-loop/.agents/skills/staff-evals/references/engineering-role.md` — `cac64a2381be66eb159d84faf030706ba5e2bc9c0d42ac21482fac2576affd87`.
- `/workspace/scratch/7ed56a5a2a33/medium-decision-loop/.agents/skills/staff-evals/references/experience-records.md` — `2cd1ee85453a168c514ba6631a638824db2292a405c679b6e9b86fcac0f51953`.

Required raw evidence:

- `/tmp/staff-decision-loop/inputs/source-only/AGENTS.md` — `42b977450ed7912008a3c837c119742449c204ad23f86a57455fe14543df66d6`.
- `/tmp/staff-decision-loop/inputs/source-only/cost_telemetry.py` — `6eae5e249819e9ad3c4e0f405a1f4bfdcd59fe22e130ca86fe31ca62297e1857`.
- `/tmp/staff-decision-loop/inputs/source-only/schema_manager.py` — `4ac062c469db1cc4df93912665977caaa1ebd8ac601f30cfec67b47648e3b368`.
- `/tmp/staff-decision-loop/inputs/source-only/test_manager.py` — `a992fab7bd1fb73d7e0722663a0d39e68069e48f16a4cb98637532c1df2e1bca`.

Additional non-case method guidance:

- `/workspace/scratch/7ed56a5a2a33/medium-decision-loop/.agents/skills/staff-evals/features/README.md` — `e4c06a39410892c699d416c67ca3bfc133dee8fee2b54d8832e5c1344029a058`. This feature map was read to use the skill. Its case links were not followed. It is excluded from the report instruction map.

## Actual operations and observations

1. Used functions.exec with exec_command to cat the task and selected SKILL.md. Both commands exited 0.
2. Used a Python standard-library reader to read task.instructions and task.evidence, compute SHA-256 for each, and display their contents. It also read the feature README. The combined tool output was truncated. This did not execute the source files.
3. Read the selected instruction recipes/references again with cat. Read source line counts with wc -l. Commands exited 0.
4. Read AGENTS.md with cat and re-read ranges 280–380 and 380–442 with sed to recover truncated display. Read cost_telemetry.py using nl -ba and sed ranges 1–260, 254–510 and 506–780. Read schema_manager.py ranges 1–230, 230–465 and 465–680. Read test_manager.py ranges 1–170, 164–360 and 360–545. All commands exited 0. These reads covered all required raw source files.
5. Recomputed the task digest and all nine instruction/four raw evidence hashes in Python. All 13 supplied hashes matched. No Git command, product import or product function execution was used.
6. Wrote assessment.md and guide.md using a shell heredoc inside the authorized output directory. The write command exited 0. Wrote consumer-report.json, case.json and this capture using Python standard-library JSON and file tools. The case starts from the selected empty template and contains no observed-agent episodes.
7. Performed file-only readback and JSON structure/hash verification of the five deliverables. The check reads files, recomputes hashes and validates exact report identities and Boolean values. It does not run Soodles or a software suite. The tool result supplies the actual verification exit status.

The only constructed runtime example is an explicitly unexecuted interval-union illustration in the assessment. Source inspection establishes the described branches; no archived or fresh target execution result was available. No source audit helper, site builder, model launcher, test suite, provider operation, publication, delegation, feedback submission, product edit or instruction edit occurred. No other cases, observer files, sibling outputs, other worktrees or surrounding conversation were consulted.

## Retained outputs

- `/tmp/staff-decision-loop/consumer-source/assessment.md` — SHA-256 `b29324dab786933ad8dc4e1a3f1b1ba6130f51b8885aa4fedfb43ca721fac590`.
- `/tmp/staff-decision-loop/consumer-source/guide.md` — SHA-256 `910c734ad9ad3db95da2c5d5eb76460bae1713edcd28b7a4eae57f98abd4526f`.
- `/tmp/staff-decision-loop/consumer-source/case.json` — SHA-256 `c2a0394d87720b990b1a44b96afc2016f55dcbc41cb67f58545b4562894d972f`.
- `/tmp/staff-decision-loop/consumer-source/consumer-report.json` — SHA-256 `3a02b6759b96fdd291486cb4d9e8704d1e4f8fc45dd39a48ecbc584c405a9568`.
- `/tmp/staff-decision-loop/consumer-source/capture.md` — this self-report; its digest is emitted by the final file check to avoid a self-referential hash.

Exact command requests and tool results remain in the available native tool record. This summary does not reconstruct full stdout/stderr as an independent transcript. The initial truncated display is disclosed rather than represented as complete capture. No performance measurements or token counts for the implementation were derived from review-tool timings.
