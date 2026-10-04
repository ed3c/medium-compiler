# Podcast-to-Medium orchestration

Baseline: `5ed8b5ef165b32a6252c601d0fef790c5ca580bf`.

The existing Alex Atallah article was authored through the retained Stage 0–7 inputs in
`evidence/transcript-cli/`; transcript retrieval and selection preceded that writing.
This change makes the source-to-writer handoff reusable. It does not pretend the historical
article was written by this newly added skill or regenerate it to manufacture new evidence.

`podcast-to-medium` is a repository-local skill, discovered through AGENTS.md and README.
It reuses search/inspect/fetch/verify, adds locate/passage/verify-passage for a local verified
snapshot, and hands actual source passages to medium-writing. Writing, mechanical admission
and Git-linked deployment retain their existing owners. It adds no model API or scheduler.

`source-drive.json` records actual locate and verify-passage invocations against the retained
real source. The passage packet includes exact source groups and separate surrounding context;
only its metadata/digest is retained here. Raw transcript text stays in the ignored snapshot.
The final selected timestamp is a group start, not an exact utterance endpoint. The author
still must interpret context and distinguish source claims from hypothetical analysis.

`verification.json` records skill validation, 184 passing tests, the four existing mechanical
drives and exact existing-article replay/build identity. Five new tests cover no-video sources,
lexical matching, unchanged text/context, tampering/refusal, actual CLI overwrite refusal and
article-specific scope rendering. The skill-registration count changes from 23 to 24 because
one repository skill was added; the uniqueness and name checks remain enabled.

Website support now reads each new podcast article's own timestamp and scope/analysis notes.
The old article/source context remains supported unchanged. Optional missing video associations
are explicit; a source-only episode no longer needs a fabricated video URL to be acquired.

The separate fresh-thread source-handoff exercise is a scoped skill-use observation, not a
writer A/B, independent semantic approval, audio check, or evidence of learner improvement.
Any child-authored command log is labeled as such, not independent native tool capture.
Matching-head Actions and actual production readback belong to the PR delivery record.
