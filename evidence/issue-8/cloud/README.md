# Issue #8: actual cloud prerequisite probe

The user asked whether the remaining fresh-writer/reader work can run in the cloud.
This continuation executes the existing doctor in a GitHub-hosted Ubuntu 24.04 job.
It does not change writer/observer code, A/B pins, comparison criteria, Ops or LEARNING.md.

## Measured result

Codex 0.157.1 installs and advertises every flag required by the writer runner. The first
standalone distribution lacked bubblewrap; installing the hash-pinned full official
package fixes that packaging gap, but native sandbox launch then fails with:

```text
bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted
```

The controlled probe reads/writes only freshly generated sentinel files. Its unsandboxed
control works; the sandboxed child does not start. No claim of successful read or write
isolation is made. No sudo/sysctl/security bypass was used to force a result.

The selected Actions job also receives `OPENAI_API_KEY configured = false`. It receives
only that boolean, never a key value. This does not inventory keys in other environments
or validate a model subscription. No authentication request or model invocation was made.

Both runs and their raw stdout/stderr are retained. A successful qualification workflow
means its diagnostic completed, not that the host qualified. `qualification.json` binds
run IDs, heads and downloaded artifact hashes; `sandbox-commands.json` retains exact argv
and outcomes from both attempts. Full raw archives are also attached to the conversation.

## Reuse and stop

Workflow: `.github/workflows/cloud-writer-doctor.yml` (scoped branch push or manual dispatch).
Helper: `scripts/cloud_writer_doctor.py`. It always leaves external host qualification and
pilot review outstanding, even if the bounded canaries pass. It never emits host approval.

The next owner is the execution-host owner: provide validated model authentication AND
an enforced, supported read/write-isolated environment with an external recorder. A key
alone does not solve the observed sandbox failure. Do not copy personal auth.json into CI.

The existing qualified pilot -> six fixed sessions -> external review path is unchanged.
Fresh writer A/B, isolated reader, accepted-episode positive path and strict pstack review
remain outstanding. Keep #8 open and PR #9 draft. The real article is intentionally unchanged:
this is an execution prerequisite failure, not a newly completed learning experiment.
