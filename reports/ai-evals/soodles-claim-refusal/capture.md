# Consumer capture and scope

Consumer: `/root/eval_consumer`. Task: `/tmp/ai-evals-consumer-20261004/task.json`. This is a truthful action summary, not an independently captured complete platform transcript.

Actual tools/actions performed:

1. Used `functions.exec` to call `tools.exec_command` with shell `cat` for the assigned skill and task JSON.
2. Used `rg --files` to inventory skill documents and locate an eval-audit method. This filename discovery traversed the workspace; it did not read discovered supervisor, decision, verdict, or results contents. It first located an archived eval-audit copy, which was read as method guidance. The existing installed method at `medium-work/.agents/skills/eval-audit/SKILL.md` was subsequently read; both method files are included in instruction hashes.
3. Read all Markdown references within the selected skill directory, the allowed supplied audit JSON, and every one of the 25 listed raw archive files. Python printed each permitted archive file for assessment. Launch strings containing historical commands were read as data and never executed.
4. Ran a fresh Python deterministic check. It called only read-only Git commands: `git rev-parse HEAD`, `git status --short`, and 25 `git show REV:path` operations for allowed archive paths. It compared raw-byte SHA-256 against the audit and pinned bytes, and checked six reports against owner/identity fields. All Git operations exited 0; their exact argument arrays and stderr are in `technical-checks.json`. HEAD matches the requested revision, checkout status is empty, and every source matches.
5. Wrote `technical-checks.json`, `report.json`, `assessment.md`, and this `capture.md` only within the assigned output directory. Instruction SHA-256 values were computed from actual Markdown bytes; the task digest was computed from actual task JSON bytes.

The tool outputs in this consumer session include the read outputs and deterministic check summary. The retained technical-checks JSON contains exact Git commands, exit codes, source hashes, and per-report observations; it does not contain an independent recording of this consumer's full platform activity. There is no claim of filesystem isolation. No subagent was spawned by this consumer.

Unavailable capture: historical full platform transcripts, independently observed all-effects activity, exact model/reasoning identity, tokens and timing. Archived records state these limits explicitly. Historical read receipts, handoffs, instruction bytes, and broader implementation are outside this task's allowed slice. No repository AGENTS.md was read because the task restricts readable sources. No provider or lifecycle command, historical argv, schema feedback, site build, network request, or repository mutation was performed. The existing audit helper was not rerun; the narrower byte/field checks above were newly performed.

The assessment is independent AI-authored interpretation of the allowed source slice. It is not the user's independent work, a hiring certificate, or proof that unobserved historical effects did not occur.
