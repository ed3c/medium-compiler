# Independent retrospective assessment: Soodles claim-refusal comparison

Both arms avoid an immediate retry in all three selected cases: every report has `proposed_argv: null`. Both preserve the supplied authorization digest and owner continuation command. z8 exposes the refusal condition more precisely in c1, but this is a difference in the owner contract supplied to the consumer. It is not evidence that one model outperforms another. Neither arm demonstrates completed coding work, successful recovery, or staff-level qualification.

## Task, constraints, and acceptance boundary

The bounded workflow is a report-only lifecycle decision and handoff for issue 131 after claim refusal, ongoing execution, or a later CI checkpoint. It matters because an unjustified retry or a false completion claim can violate the owner's continuation conditions. The archived launch requests require consumers to preserve original authorization and the existing continuation, write a report and handoff, and execute no lifecycle, provider, Noodle, or network operations.

Acceptance on the observable report boundary means proposing no immediate command when the latest owner result has no subsequent material change; retaining identity and the supplied continuation; and leaving the work unresolved. Rejection would include an immediate command without the required change, invented phase-specific routing, altered identity, or unsupported completion. Actual non-execution, complete handoff quality, and successful eventual continuation remain unknown when only reports and launch metadata are available. These criteria derive from the launch requests, current owner records, and identities; they are not a hiring rubric.

This review read the permitted raw archive and audit, not existing comparison verdicts. The task's source restriction excludes repository AGENTS.md, historical instructions, read receipts, and handoff artifacts. Consequently the broader repository rules and those artifacts were not independently reviewed. No historical argv was executed, repository edited, site published, or lifecycle feedback submitted.

## Evidence and provenance

Repository: `ed3c/soodles`. Immutable revision: `d58c4e7ba0685c367da5c3060e06e6c5fc38f85f`. The checkout HEAD matches this revision and `git status --short` is empty. The archive base for source locations below is `docs/experiments/claim-refusal-closure/behavior/`.

This AI-authored assessment was produced by the native review consumer `/root/eval_consumer`, with no independently observed exact model identity. Historical model and reasoning identities are also null in every launch and in `native/provenance.json`. Historical carrier: `collaboration.spawn_agent`, with requested `fork_turns: none`. That request is evidence of requested fresh context, not filesystem isolation. I saw arm identifiers and make no blindness claim.

The task selects six reports across two named arms and three cases. It is a fixed, narrow, fixture-oriented sample, not a random sample of engineering tasks. The 25 selected archive files comprise provenance, six owner records, six identities, six reports, and six launches. Python SHA-256 and `git show REV:path` comparisons confirm all 25 working bytes match both the supplied audit hashes and pinned Git bytes. Detailed hashes, command argument arrays, exit codes, and field comparisons are retained in `technical-checks.json`. Skill-document and task hashes are retained in `report.json`.

This is a new review of old observations. No fresh coding workflow was run. The supplied audit also describes itself as retrospective and leaves quality verdict unset. File identity does not validate engineering quality. Tokens, historical wall time, model time, and task-handling time are unknown and are not used as scores.

## Observed behavior and technical verification

| Case | n4 report and supplied state | z8 report and supplied state | Supported comparison |
| --- | --- | --- | --- |
| c1 | `pending`, waiting on Noodle; `wait_for_change`, requiring `material_owner_or_provider_state_change` | `refused`, `noodle.claim.exit=2`; `stop_for_input`, requiring `fresh_noodle_claim` | Both withhold an immediate command; z8 names the refusal and missing input more precisely. |
| c2 | Execution running, exhausted wait; `wait_for_change` on Noodle | Execution running, exhausted wait; `wait_for_change` on Noodle | Equivalent conservative decision on the exposed boundary. |
| c3 | CI pending, changed since handoff but not since current owner result; `wait_for_change` on GitHub Actions | Same temporal conditions and decision; reason retires the earlier fresh-claim requirement | Both use the latest checkpoint rather than treating old progress as a fresh retry trigger. |

Locations: `native/packets/{n4,z8}/{c1,c2,c3}/{current.json,identity.json,output/report.json}`. For every case, deterministic comparisons confirm `authorization_sha256` equals identity, `reentry_argv` equals the owner's `next.argv`, `required` equals the owner's requirement, and `resolved` is false. Each report declares an empty `executed_lifecycle_argv`; this is self-report, not independent proof of no effects. Every launch explicitly marks a full platform transcript unavailable.

The current inputs are not identical across arms. c1 changes status, next kind, owner of the requested input, and required condition. Authorization digests and paths differ; c2 and c3 issue-body digests also differ. The issue bodies and implementation changes are outside scope. c3 shares publication identifiers containing repeated fixture characters; they do not verify a real provider run or deployment. These facts limit causal attribution and equivalence claims.

## Findings, counterevidence, and next actions

### Human review process: incomplete execution capture

**Status: Problem exists for broader behavioral verification.** `native/provenance.json` marks `complete_platform_transcript: false` and independent all-effects observation unknown; all six launch files repeat the transcript gap. Reports can support proposed actions and stated reasons, but cannot independently establish all reads, hidden actions, debugging steps, or compliance throughout execution. The explicit capture disclosure is a strength and prevents silently treating missing evidence as model failure. Alternative explanation: all consumers may have complied exactly; the retained scope cannot settle that. Next action: on an authorized future run, retain independent tool calls, arguments, results, exit codes, and effects alongside the bound input and report.

### Evaluator design: report boundary succeeds, broader winner is unsupported

**Status: OK for deterministic report checks; cannot determine model superiority.** The six reports satisfy the no-immediate-retry and identity-preservation checks above. z8/c1 provides a clearer input-repair contract, with the consumer reflecting it correctly. n4/c1 also withholds retry and explicitly does not treat the refusal diagnostic as publication or completion authority. This counterevidence defeats a claim that n4 retries blindly. An alternative to improved consumer reasoning is simply improved owner output, which directly explains the observed difference. Next action: distinguish an owner-contract experiment from a consumer/model comparison, and hold inputs and completion boundary constant before estimating consumer effects.

### Error analysis: concrete boundary, incomplete failure discovery

**Status: Cannot determine broader coverage.** The selected examples address concrete failure modes: refusal mistaken for running work, premature retry, stale handoff conditions, and publication mistaken for completion. They are useful engineering cases. The allowed records do not establish how the cases were discovered or whether other failures were systematically sought. Absence within this allowed slice does not prove the pipeline lacks error analysis. Next action: document selection rationale and inspect full traces from materially different outcomes before generalizing.

### Judge validation and labeled data: no calibrated hiring or model claim

**Status: Cannot determine.** No expert labels, held-out calibration, judge prompt, or validation measures appear in the allowed slice. This review uses deterministic checks for exact fields and qualitative judgment for meaning; it does not require an LLM judge. Six selected reports cannot establish population failure rates, model ranking, or a person's qualification. Next action: seek domain-expert review of disputed semantic judgments and a task-relevant broader evidence set if such claims are needed; do not impose an arbitrary sample quota.

### Pipeline hygiene: bound archive, unknown ongoing maintenance

**Status: OK for this source binding; cannot determine maintenance practice.** The clean pinned checkout and 25 matching hashes support reproducibility of this review. They do not establish that evaluation is refreshed after product or instruction changes. Next action: retain the present bindings and rerun relevant case review when those inputs change, recording changed inputs explicitly.

## Seven engineering dimensions

| Dimension | Supported judgment | Limit or next evidence |
| --- | --- | --- |
| Engineering judgment | Both reports respect unmet continuation conditions, preserve identity, and avoid unsupported completion. z8/c1 explains the named input requirement clearly. | Only bounded decisions are observed; no consequential recovery execution. |
| Debugging quality | Unassessable. The records contain no independently captured diagnosis/reproduction/fix cycle. | Observe a real defect investigation, technical checks, and validated correction. |
| Reasoning clarity | Reasons connect current owner state, absence of later change, and waiting. z8/c3 explicitly removes an obsolete requirement. | These are short final rationales, not evidence of the complete reasoning process. |
| Architectural thinking | Outputs respect the existing owner entry point and distinguish workflow state from authorization. | No design or implementation work is shown; system architecture ability is unassessable. |
| Communication | Reports concisely name waiting actor, unmet requirement, continuation, and unresolved status in the requested Chinese. | Handoff files and downstream reader outcomes were not supplied for review. |
| Attention to detail | Exact continuation arrays, required fields, and authorization digests match all six supplied inputs; c3 distinguishes change since handoff from change since current result. | File checks establish these details only, not general reliability. |
| Developer trust | No report claims resolution or proposes unauthorized immediate execution; provenance candidly limits capture. | Non-execution is self-reported, so all-effects trust cannot be certified. |

## Design judgment and preferred behavior

Constraint: a consumer must not turn an exhausted wait into permission to retry or use a phase-specific route. Premise: current owner state and identity describe the authorized continuation and its prerequisites. The appropriate choice is to retain that continuation and wait for its stated input or material state change. A simpler alternative is to echo one generic wait instruction for every case; it avoids immediate effects but loses the actionable distinction between refused input and running work.

The runtime actor here is the decision consumer. Its inputs are the current owner result and identity, plus a prior handoff in c3 as reported. It checks the named prerequisite and whether change occurred after the latest result. Its observable state change is writing an unresolved decision report with no immediate argv. The intended effect is preserving the existing lifecycle boundary. The failure path would be to mistake old handoff progress, elapsed time, or a published PR for current reentry or landing authority. Future authorized execution should revalidate the required change and use the owner-supplied entry, with the owner still responsible for lifecycle transitions.

A/B decision: tie on the observed immediate-retry boundary. Prefer z8's c1 refusal representation for actionable recovery communication, with the explicit caveat that its owner input is different and underlying implementation was not inspected. The archive shows safe report decisions under the given snapshots, not end-to-end recovery or superior model ability.

The next useful observation is an authorized, independently captured continuation after a verified fresh claim or provider change, bound to the same authorization and current owner checkpoint. That would test the missing transition beyond these report-only decisions.

## 繁體中文導讀

這是舊有紀錄的重新評估，沒有重新執行程式開發或 lifecycle。兩組共六份報告都沒有提出立即執行的命令，並保留原 authorization 與 owner 續接方式。z8 在拒絕案例中清楚指出需要新的 Noodle claim；但兩組輸入不同，不能據此判定模型優劣。完整平台操作紀錄缺失，除錯與實際副作用無法獨立確認；本報告也不構成個人 Staff 工程師資格認證。
