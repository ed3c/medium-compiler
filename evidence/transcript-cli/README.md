# Transcript acquisition and independent article delivery

Baseline: `e88bd741faa69ae13b094383088402a9ad924c36`.

The user authorized CLI acquisition of the third-party transcript, a separate article using
medium-writing without changing the original, and delivery through the existing deployed site.
This is a source-explanation task, not a curriculum learning-episode or whole-episode translation.

## Actual source drive

```sh
python3 scripts/transcript.py fetch --url https://podscripts.co/podcasts/the-a16z-show/beyond-the-god-model-alex-atallah-amjad-masad --video-url https://youtu.be/ekK8urKHPMQ --out .transcripts/openrouter-agent-primitives
python3 scripts/transcript.py verify --snapshot .transcripts/openrouter-agent-primitives
python3 scripts/transcript.py receipt --snapshot .transcripts/openrouter-agent-primitives --out references/transcripts/openrouter-agent-primitives.json
```

All three commands returned exit 0. The fetch used a real HTTPS provider page, with 95 timestamp
groups, from 00:00:00 to 00:47:58. The retained public metadata records the actual retrieval time
and SHA-256 of raw HTML, JSON extraction and readable Markdown. The raw snapshot stays in the
ignored source cache and is not copied into Git or the public site. The public metadata is not
a replacement for that private cache or a provider signature. Re-fetching may yield new bytes.

Author source review read the 14:05, 14:46, 14:58 and beginning of 15:18 spans. The later enterprise
response in 15:18 is excluded from the article's source claims. The article independently develops
an explicitly hypothetical product-page case. No audio checking, automatic speaker attribution,
episode completeness or measured product advantage is claimed.

## Actual writing and build

The six `stage-00.md` through `stage-05.md` inputs were authored for this article and admitted in
order. Stage 6 kept the reviewed semantic draft unchanged; Stage 7 copied admitted bytes. The
compiler receipt is retained in `validation-receipt.json`; `replay.py` repeats those real CLI
invocations into a new external output directory and records stdout/stderr/exit for each command.
This is not an independent writer/reader comparison.

```sh
python3 evidence/transcript-cli/replay.py --out /tmp/transcript-article-replay-NEW
python3 -m unittest discover -s tests -v
python3 .agents/skills/verify-medium/scripts/verify.py --feature mechanical --out /tmp/transcript-mechanical-NEW
python3 scripts/build_site.py --out /tmp/transcript-site-NEW
```

171 tests pass, including 9 focused transcript/article/site checks. Controlled synthetic HTML
tests cover malformed/blocked pages, timestamps, duplicated source phrases, target/redirect
restrictions, timeout without a success snapshot, overwrite refusal and changed source bytes.
Tests also replay the real article through the compiler, check its exact downloadable bytes,
reject stale article/source metadata, and ensure raw transcript files are not published.

The existing four mechanical drives pass. All 20 previously tracked files in `articles/` are
unchanged from the baseline. Existing workflow and compiler bytes are unchanged. `proof.json`
records scoped local results; the PR's actual Actions result is the separate cloud evidence.

Site readback targets: `/transcripts/`, `/articles/agent-primitives-product-differentiation/`,
the latter route's `article.md` and `source.json`, and `/provenance.json`. An HTTP 200 alone is
insufficient: compare article and source digests, navigation and source/analysis notes.

Remaining limitations: one provider's observed HTML layout, no YouTube-to-transcript discovery,
no speech recognition, no audio verification, no independent semantic or learner evaluation.
Publishing to this site does not publish to Medium.com. Existing behavior-evals remain separate.
