> Historical hosted-Codex diagnostic; superseded by the user-selected ChatGPT native route.
> The probe workflow/executable have been retired. Missing keys and sandbox failures below
> apply only to those recorded Codex attempts, not to native cloud launch. Raw evidence is
> retained unchanged. The former implementation remains available at `bea94040` in Git history.
> Continue with [the native recipe](../../../evals/writing/ops-evidence-handoff/cloud-native.md).

# Issue #8: actual cloud prerequisite probe

The user asked whether the remaining fresh-writer/reader work can run in the cloud.
The earlier, now superseded continuation executed a Codex doctor in a GitHub-hosted Ubuntu 24.04 job.
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

## Historical instructions, not the current native route

Retired workflow: `.github/workflows/cloud-writer-doctor.yml`. Retired helper:
`scripts/cloud_writer_doctor.py`. Their original source remains at `bea94040`.
They did not emit host approval; neither is an entry for native ChatGPT work.

The original `qualification.json.next` described a Codex-host authentication/isolation
gap. It is retained as historical evidence, not an instruction to provision a native-cloud
API key. The current next operation is native launch/capture qualification in a Session
that exposes that tool. Do not copy personal auth.json into CI or switch carriers.

The existing qualified pilot -> six fixed sessions -> external review path is unchanged.
Fresh writer A/B, isolated reader, accepted-episode positive path and strict pstack review
remain outstanding. Keep #8 open and PR #9 draft. The real article is intentionally unchanged:
this is an execution prerequisite failure, not a newly completed learning experiment.
