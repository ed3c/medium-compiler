---
name: podcast-to-medium
description: Find a user's podcast transcript through the repository CLI, locate and review the relevant timestamped passages, then use medium-writing to produce a source-grounded Traditional Chinese Medium article and deliver it through the existing website when requested. Use for podcast/video/topic-to-article requests, not verbatim full-transcript republication or browser-only searching.
---

# Podcast to Medium

Work from the selected medium-compiler checkout. Read its AGENTS.md and README entrypoints.
Keep the user's input, question and requested publishing scope. Use this skill as the
orchestrator; [medium-writing](../medium-writing/SKILL.md) owns prose and Stage 0–7.
Do not create another writer, model API, scheduler, approval loop or publishing service.
An end-to-end writing/deployment request authorizes its ordinary steps; do not repeatedly
ask to proceed. Skill availability itself does not authorize a new deployment.

## 1. Resolve the source with the existing CLI

Run `python3 scripts/transcript.py --help`. Read
[the command and handoff reference](references/workflow.md) for arguments and delivery fields.

- For a supplied PodScripts episode URL, use `inspect` directly.
- For a YouTube URL, episode title, guest or content description, run `search` first.
  Select the named show; otherwise use the video/channel or topic evidence to choose a
  supported show. Expose that scope. Do not silently treat the a16z default as a universal search.
- Search returns candidates, not a confirmed identity. Read the candidate title, show,
  available metadata and actual transcript context. Prefer matching guest/title/content
  evidence; do not accept result number one solely because the provider ranked it first.
- If the first search is empty or irrelevant, use shorter source-language keywords, title
  mode, or another supported show indicated by evidence. Keep a bounded search record.
  For an unsupported show, use an available web search to find its public transcript;
  use this CLI only for its supported PodScripts URLs. Do not invent an adapter, URL or result.
  Ask a focused question only when remaining episode ambiguity affects what can be written.
- Respect source access restrictions. Keep missing, blocked and unrelated results distinct.
  Do not mistake a description, search snippet or paid preview for a transcript.

Fetch the chosen episode into a **new ignored `.transcripts/` snapshot** and verify it.
A user-supplied video association is not audio verification. Omit `--video-url` when absent;
do not invent a video to satisfy the command. Retain the original HTML and extracted text.
Reuse a verified existing snapshot for the same source; do not overwrite it on retries.

## 2. Find the passages that answer the user's question

Use `locate` with a small set of source-language phrases corresponding to the user's topic
or supplied quote. Its exact-substring ranking proposes timestamp groups only; it does not
measure relevance or establish source meaning. With no hit, try a synonym from the source
or read the snapshot; do not declare that the topic is absent from lexical failure alone.

Use `passage` to save complete matching groups plus nearby context to a new private JSON
packet. Read the packet's segments AND context before writing. Expand the window if a
pronoun, condition, rebuttal or causal link starts outside it. Distinguish the final group's
start timestamp from the actual end of an utterance. Run `verify-passage` before handoff.

Record in the article's companion: the user's input/question, candidate selection reason,
source URL, source and passage digests, selected timestamps, what each passage supports,
necessary qualifiers, explicit exclusions and unresolved identity/speaker/audio questions.
Do not put the transcript text into the public companion. If only part of a timestamp group
supports the article, record the exact textual boundary privately and explain the exclusion.
Never label the whole episode read because a few passages were selected.

## 3. Delegate writing to medium-writing

Load `../medium-writing/SKILL.md`, its complete retained writing contract and
`../../../prompts/medium-article.md`. Supply the user's question and verified private packet
as source material. Select `source-explanation` for an ordinary podcast article; preserve
real learning-owner requirements if the user actually requested a learning-episode task.

Show the article outline and scope first, then follow the existing CLI `next` through
Stage 0–7. For an authorized uninterrupted task, continue internally to completion.
Keep supported source claims separate from author interpretation and hypothetical examples.
Preserve negation, uncertainty, terminology and causal conditions. Write an independent
explanation, with necessary short quotations and timestamp/source links. Do not publish a
third-party full transcript or a near-verbatim substitute. A genuinely user-provided or
licensed full-text appendix is a separate explicitly reviewed publication scope.

Use a new article slug unless the user asked to revise an existing one. Existing prose
revisions use medium-writing's implemented revision route, not invented prior stages.
Do not blindly run the historical Alex Atallah replay to claim a new article was written.
Retain actual stage inputs, command results and the canonical article receipt.

## 4. Build and deliver through the existing website

Follow the delivery fields in [workflow.md](references/workflow.md). Export the metadata-only
source receipt; bind it and the final article bytes in the context JSON. Register the new
article in `scripts/build_site.py`'s ARTICLES using its source_manifest and context paths.
Declare this episode's source scope; never reuse the Alex Atallah timestamps or case notes.

Run the affected checks, `verify-medium` and the site build. Inspect article rendering,
source links, Markdown download and navigation. Confirm neither private transcript packets
nor raw source files were copied into public output. Keep existing article bytes unchanged.

When deployment is requested, use the existing GitHub PR/Actions and Git-linked Vercel route.
Read matching-head checks; merge/publish within the user's scope, then read back the actual
production article, download and provenance bytes. A successful build or HTTP 200 alone is
not full delivery. If deployment is not requested, stop at the reviewable article/build.

Report the article URL, source passages used, actual checks and remaining limitations.
Distinguish source acquisition, author review, mechanical checks and deployment. Do not
claim independent semantic review, audio verification or improved behavior without evidence.
