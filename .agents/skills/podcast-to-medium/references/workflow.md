# Commands and writing handoff

All commands run from the repository root. Use fresh output paths. This file documents
existing execution owners; it does not add a second workflow state machine.

## Discover and preserve

```sh
python3 scripts/transcript.py search --query 'https://youtu.be/ekK8urKHPMQ'
python3 scripts/transcript.py search --query 'Alex Atallah' --podcast a16z --mode episode
python3 scripts/transcript.py inspect --url '<candidate-podscripts-episode-url>'
python3 scripts/transcript.py fetch --url '<chosen-podscripts-episode-url>' \
  --video-url '<supplied-video-url>' --out .transcripts/<new-snapshot>
python3 scripts/transcript.py verify --snapshot .transcripts/<snapshot>
```

Omit `--video-url` when no video is known. The supported podcast keys are `a16z`,
`a16z-podcast`, `latent-space`, `dwarkesh`, `no-priors`, `lenny`, `lex-fridman`.
Each search covers one show's first public result page, at most five candidates, with at
most one visible broader retry. Chinese matching uses a finite glossary, not an LLM.
The current video example reuses an explicitly unverified caller association. General
video queries use public oEmbed titles; neither establishes episode/audio identity.

## Locate and read

```sh
python3 scripts/transcript.py locate --snapshot .transcripts/<snapshot> \
  --term '2005' --term 'table stakes' --term 'agent loop'
python3 scripts/transcript.py passage --snapshot .transcripts/<snapshot> \
  --start 00:14:05 --through 00:15:18 --context 1 \
  --out .transcripts/<snapshot>/selected-passage.json
python3 scripts/transcript.py verify-passage --snapshot .transcripts/<snapshot> \
  --packet .transcripts/<snapshot>/selected-passage.json
```

Use timestamps actually returned by that snapshot. `through` includes the entire last
timestamp group, not an exact utterance endpoint. `context` adds 0–3 groups on each side,
separately from selected groups. `passage` preserves extraction text byte-for-byte in JSON
values, refuses existing output and prints metadata only. Read the private packet locally.
`verify-passage` checks the snapshot and regenerates the selection to reject changed text,
wrong source, changed boundaries or stale snapshot identity. These are mechanical checks.

## Write with the existing owner

Handoff the following task-local values to medium-writing (no invented generic rubric):

- User input and central reader question; selected source and reasons for selection.
- Private passage path/hash and source receipt; timestamp-to-claim mapping and boundaries.
- Required terms, qualifiers, disagreements, unknowns and explicitly excluded material.
- Target article slug, audience, Traditional Chinese with English terms, deployment scope.

Use `python3 medium_compiler.py --help` and the current `init`, `next`, `submit`, `assemble`,
`verify`, `check-receipt` commands. The writer authors the actual spec, coverage and stages;
the transcript CLI does not generate prose or confer semantic approval.

## Register the reviewed article

```sh
python3 scripts/transcript.py receipt --snapshot .transcripts/<snapshot> \
  --out references/transcripts/<new-slug>.json
```

Create `articles/<new-slug>.context.json` with the existing contract:

```json
{
  "schema_version": "medium-transcript-article@1",
  "purpose": "source-explanation",
  "article_sha256": "<SHA-256 of canonical article bytes>",
  "source_manifest": "references/transcripts/<new-slug>.json",
  "source_manifest_sha256": "<SHA-256 of that public receipt>",
  "source_scope": {
    "timestamps": ["<selected exact HH:MM:SS timestamps>"],
    "public_note": "<readable description of this article's source scope>",
    "analysis_note": "<which material is author analysis or hypothetical>"
  },
  "passage_sha256": "<verified private packet digest>",
  "author_review": {"independent": false, "audio_verified": false, "unresolved": []}
}
```

Populate real values and unresolved gaps. Add an ARTICLES item with unique `slug`, `title`,
`description`, `source`, `source_manifest`, `context`. The builder uses the source scope's
first timestamp for video links, or omits the video link when no video exists. It does not
infer a precise source-span end or reuse another article's analysis note. The historical
Alex Atallah context remains supported without rewriting its previously reviewed bytes.

Run focused tests and the existing mechanical checks and build:

```sh
python3 .agents/skills/verify-medium/scripts/verify.py --feature mechanical --out /tmp/podcast-mechanical-NEW
python3 scripts/build_site.py --out /tmp/podcast-site-NEW
``` Inspect generated article, `article.md`, `source.json`
and `/provenance.json`. No local input packet belongs in these public outputs.

For authorized deployment, use the existing PR workflow and Vercel Git integration. Keep
exact-head Actions and production readback evidence in the PR. If a provider is unavailable,
retain completed work and identify the actual blocker rather than declaring publication.
