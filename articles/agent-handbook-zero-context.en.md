# An Agent Is Not a Prompt: Seven Engineering Decisions Behind a Safe Patch

A payment service needs an urgent dependency upgrade. The security advisory names a vulnerable package, and the team wants a fix without disrupting payments. Someone suggests an AI agent: it can search the code, edit a manifest, run tests, and prepare a release. The missing design question is not whether a language model can write the patch. It is who knows which state is authoritative, who may change it, and what evidence proves the service was actually repaired.

This is a worked learning case—not a claim that a live vulnerability was repaired. It follows the mechanisms in the AI Agent Handbook's Harness, Task, Information, Action, Evaluation, and Controlled Self-Evolution chapters. You do not need an earlier chat or a particular vendor's agent to read it.

## The contract before the model

Imagine a payment-service repository whose dependency manifest lists a vulnerable library. A task owner asks to upgrade to a safe compatible version, preserve payment behavior, demonstrate test and security-scan results, and prepare a change ticket. Production release requires separate human approval. The model may propose an upgrade; it has no authority to approve deployment. A timeout while publishing must not become permission to publish again.

A useful task representation keeps `goal`, `source_revision`, `selected_dependency`, `constraints`, `stage`, `observations`, `effect_authorization`, and `unknown_effects` distinct. Here `source_revision` identifies the version inspected. `observations` are test or provider results, not self-reported completion. A `WAITING_FOR_APPROVAL` state is legitimate progress; it is not task failure. These field names form an explanatory model, not an existing Alibaba Cloud or Soodles API.

## One input through the runtime

```text
Vulnerability request + pinned repository revision
  -> PREPARE: load goal, allowed tools, prior authoritative state
  -> MODEL: propose dependency analysis and a compatible upgrade
  -> ACTION POLICY: verify tool, arguments, identity and write scope
  -> SANDBOX: apply patch; run focused tests and dependency scan
  -> OBSERVE: save actual patch, test exits, scan output and revision
  -> CHANGE TICKET: create only with task-authorized credentials
  -> WAIT: production deployment approval not yet granted
  -> DEPLOY (only after approval): execute once with idempotency/readback
  -> VERIFY: inspect live deployed revision and independent health signals
  -> DONE, RECOVER, or UNKNOWN: based on real environment facts
```

The arrows are conceptual transitions. Real behavior, interfaces, and commands must be observed in the selected platform. The Handbook's chapters distinguish model intent, task state, action authorization, and feedback. The purpose of the trace is to explain the causal order, not to imply this example ran.

## D1 — Model versus Harness

A model estimates useful next steps from context; a Harness supplies the executable loop, environment, durable state, policy checks, observation and recovery. A longer system prompt cannot guarantee that a prior deployment was not already accepted by the provider. When a state transition has a unique machine-verifiable answer, it belongs in an existing deterministic owner or tool. When two safe versions require a trade-off, the model or engineer may reason from constraints. **Decision boundary:** which part is a semantic choice, and which part must be a reproducible system fact?

## D2 — Who owns the current task state?

A model response saying “finished” is not evidence. Persist stage and effects outside the context window. If a tool invocation returns an ambiguous network failure after a ticket submission, the system must read the provider's ticket state before retrying. A new task plan does not resolve an unknown external write. The alternative—replaying the last instruction—can create duplicate tickets or deployments. A durable state machine is worth the additional complexity when requests outlive one response or produce effects.

## D3 — What may be compressed?

Logs and long analyses can be summarized or left retrievable. The user's goal, negative constraints, pinned revision, unfinished checks, approval boundary and unresolved effect cannot silently disappear. Compression fidelity has three distinct questions: did invariant task fields survive; can an independent reader recover the necessary decisions from compressed context; and does a downstream replay still respect the constraints? A successful question-answer probe is useful but does not mathematically prove lossless compression. If the original request said “do not deploy,” a summary that only says “prepare a deployment” is unsafe even if it sounds relevant.

## D4 — Direct tool or subagent?

A deterministic version lookup or CI-status read usually needs a bounded tool call, not another agent. Independent dependency impact analysis and read-only policy review may be delegated if they have clear inputs and output checks. Yet the security review may depend on the precise patch. Forking both branches before the patch exists only creates stale review and rework. The total path includes fork setup, the slowest branch, rate-limit retries and merge validation. Compare single-agent/direct-tool and delegated alternatives on equivalent tasks; do not use a fixed token-count threshold or assume two agents are twice as fast.

## D5 — Tool visibility is not authorization

Three separate facts matter: a tool description reached the model, the Harness has registered the capability, and the present identity and task are authorized to execute this action. Only the third permits a production write. A proposed `deploy(version=X)` call is an intent. The policy layer must validate parameters, tenant, credentials, environment and approval, then execute through the actual provider and record the result. A model may request a high-risk action without being allowed to perform it. This separation is essential whenever an effect cannot be undone by editing the conversation.

## D6 — What proves completion?

Passing unit tests establishes a narrow property of one candidate revision. It does not prove that the provider deployed that exact revision or that payments still work. Completion evidence may include the pinned diff, relevant regression tests, scan results, approval, deployment identity and live readback. Choose only the checks capable of distinguishing the targeted failure. If release returns a timeout, the state is UNKNOWN until readback—not FAILED with permission for silent retry, and not DONE because a model wrote a success sentence.

## D7 — When does an experience become reusable engineering capability?

Suppose the team repeatedly forgets the post-patch security scan. First confirm the failure from real traces and compare with successful neighboring tasks. If the scan command and required conditions already exist, a targeted Skill or CI check may be enough. If every agent keeps reconstructing the same exact invocation, a deterministic tool or workflow can be cheaper and safer than another paragraph of instructions. If the failure is an uncertain external effect, fix the Harness recovery boundary rather than merely improving wording. Promote a candidate only after held-out negative and positive cases, latency/cost measurements where available, and source-bound owner acceptance. A published Skill is an asset, not proof that future agents will use it correctly.

## Cost and alternative derivation

For a simple serial path, total latency is roughly `T_read + T_patch + T_tests + T_review + T_publish`, excluding human approval wait. In a genuinely independent fork, compute `T_fork + max(T_analysis, T_review) + T_join + T_rework + T_publish`. Parallelism wins only when the saved critical-path time exceeds fork, join, retries, contention and dependency rework. There is no universal token threshold. Likewise, adding a dense knowledge search or memory retrieval is not automatically valuable; compare it with exact revision/identifier lookup when precision is a hard requirement. The system-design-notes resource is an optional index for trade-offs such as rate limiting, message queues and monitoring—not authority for the Handbook's behavior.

## Reproducible experiments, not invented success

A useful first test freezes the request and tool environment, then compares (A) direct deterministic lookup and single-agent patch preparation with (B) delegated investigation for the same candidate issue. Record total wall time, consumed tokens or real billing where available, duplicate actions, test evidence and eventual task correctness. Include a network timeout after the provider accepted a write as a negative case; the expected behavior is authoritative readback without automatic duplicate publishing. The observation is currently NOT_RUN. Any numerical outcome would require a real run.

Before claiming a learner understands the design, ask them to identify a safe and unsafe transition, explain the owner of each state, and predict the correct behavior after an ambiguous result. The article can be evaluated for source fidelity; actual human comprehension is separate evidence.

## Master map

```text
Payment-service request + pinned vulnerability/repository evidence
  -> Model suggests a compatible dependency candidate (D1)
  -> Durable task owner records goal, stage and unknown effects (D2)
  -> Context retains constraints and approval after compression (D3)
  -> Direct tools or justified independent investigation (D4)
  -> Action policy checks identity, permission and effect scope (D5)
  -> Sandbox patch + tests + scan + approval + provider readback (D6)
  -> Compare failures and transfer proven behavior into tools/skills (D7)
```

A runtime diagram is a model of a design. An actual patch, approved release, and repeated improvement each require a matching independent observation. The accompanying [More Route article handoff](https://github.com/ed3c/medium-compiler/blob/main/docs/more-route-handoff.md) documents the separate writing and website delivery responsibilities.

## Sources and scope

- [AI Agent Handbook, Chapter 3: Model versus Harness](https://github.com/aliyun/ai-agent-handbook/blob/a5028af381306fd0f65c11f56a18fcbbb814d4f8/02-build/%E7%AC%AC%203%20%E7%AB%A0%20%E8%8C%83%E5%BC%8F%EF%BC%9AHarness%20%E7%9A%84%E4%B8%BB%E6%B5%81%E6%9E%84%E5%BB%BA%E6%96%B9%E5%BC%8F%E5%92%8C%E8%B4%A3%E4%BB%BB%E8%BE%B9%E7%95%8C.md)
- [AI Agent Handbook, Chapter 4: Task state and delegation](https://github.com/aliyun/ai-agent-handbook/blob/a5028af381306fd0f65c11f56a18fcbbb814d4f8/02-build/%E7%AC%AC%204%20%E7%AB%A0%20%E4%BB%BB%E5%8A%A1%EF%BC%9A%E7%BC%96%E6%8E%92%E3%80%81%E9%95%BF%E7%A8%8B%E6%8E%A8%E8%BF%9B%E4%B8%8E%E5%8D%8F%E4%BD%9C%E6%B5%81%E8%BD%AC.md)
- [AI Agent Handbook, Chapter 5: Context and durable state](https://github.com/aliyun/ai-agent-handbook/blob/a5028af381306fd0f65c11f56a18fcbbb814d4f8/02-build/%E7%AC%AC%205%20%E7%AB%A0%20%E4%BF%A1%E6%81%AF%EF%BC%9A%E4%B8%8A%E4%B8%8B%E6%96%87%E3%80%81%E7%8A%B6%E6%80%81%E4%B8%8E%E5%8F%AF%E5%A4%8D%E7%94%A8%E8%83%BD%E5%8A%9B%E8%B5%84%E4%BA%A7.md)
- [AI Agent Handbook, Chapter 6: Action and verification](https://github.com/aliyun/ai-agent-handbook/blob/a5028af381306fd0f65c11f56a18fcbbb814d4f8/02-build/%E7%AC%AC%206%20%E7%AB%A0%20%E8%A1%8C%E5%8A%A8%EF%BC%9A%E5%8F%97%E6%8E%A7%E6%89%A7%E8%A1%8C%E3%80%81%E9%AA%8C%E8%AF%81%E5%8F%8D%E9%A6%88%E4%B8%8E%E4%BA%A4%E4%BB%98%E5%87%86%E5%A4%87.md)
- [AI Agent Handbook, Chapter 22: Badcase evaluations](https://github.com/aliyun/ai-agent-handbook/blob/a5028af381306fd0f65c11f56a18fcbbb814d4f8/05-optimization/%E7%AC%AC%2022%20%E7%AB%A0%E3%80%80Agent%20%E4%BC%98%E5%8C%96%EF%BC%9ABadcase.md)
- [AI Agent Handbook, Chapter 23: Validated reusable assets](https://github.com/aliyun/ai-agent-handbook/blob/a5028af381306fd0f65c11f56a18fcbbb814d4f8/05-optimization/%E7%AC%AC%2023%20%E7%AB%A0%E3%80%80%E5%8F%97%E6%8E%A7%E8%87%AA%E8%BF%9B%E5%8C%96.md)
- [System Design Notes, System Design Framework](https://github.com/liquidslr/system-design-notes/tree/9d8388721e7231442763ad37398b8d82224aa68f/03.%20System%20Design%20Framework) and [Rate Limiter](https://github.com/liquidslr/system-design-notes/tree/9d8388721e7231442763ad37398b8d82224aa68f/04.%20Rate%20Limiter); an external read-only index, not copied content.
- [Pinned source and evidence scope](../references/upstream/more-route-learning-sources.json) (repository file; it does not attest to any live experiment).
