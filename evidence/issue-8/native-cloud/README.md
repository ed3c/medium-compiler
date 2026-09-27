# Native cloud writer route

This replaces the attempted GitHub-runner/Codex cloud qualification as the selected cloud
carrier for Issue #8.

The selected cloud path follows the Soodles rule:

```text
current ChatGPT cloud Session
  -> native collaboration.spawn_agent
  -> fork_turns: none
  -> pinned read-only GitHub inputs
  -> distinct evidence destination
  -> external supervisor review
```

Codex CLI, browser login and a local launcher are not prerequisites. GitHub Actions remains a
repository/process verifier only; it is not a second Agent.

`scripts/native_writer_packet.py` validates the frozen experiment and emits one unscored pilot
request plus the six preregistered baseline/treatment requests. It does **not** call the native
tool because repository code cannot grant or discover Session-local platform capabilities.

The supervisor must use the platform's actually exposed native subagent schema. If this Session
does not expose it, record that Session-local capability gap and keep the comparison NOT_RUN.
Do not install a CLI, create a replacement runner, change carrier, or reinterpret the packet as
a completed experiment.

Consumer inputs contain the neutral task, pinned common inputs and the assigned arm's pinned
P/CLI source files. Expected answers, observer criteria, prior reports, other-arm outputs and
later explanations stay with the external supervisor. Requested model and observed model are
separate; unavailable native transcript/model provenance remains UNKNOWN.

The earlier `evidence/issue-8/cloud/` GitHub runner attempts are retained as historical
wrong-carrier observations. They do not block or qualify this native path.

Current status: packet mechanism implemented; actual native pilot and six fresh consumers
NOT_RUN in this repository evidence until a cloud Session exposing the native action executes
them. No learning progress, product write, publication, merge or Issue closure is authorized.
