# Read and concatenate one approved Medium article edition

## Sub-features

- Read the ordered manifest and match every part to its Git blob identity.
- Concatenate with no added separators and compare to the canonical article.
- Detect missing, reordered or modified parts; preserve a tableless complete body.

## How to get to it (user POV)

Read articles/ai-engineer-learning-path.parts/manifest.json, then its five part files.
These are delivery partitions of one edition, not separate fictional authoring sessions.

## Driving it with verify-medium

Source: the article, delivery manifest, tests/test_reader_navigation.py and the driver.

Run `python3 .agents/skills/verify-medium/scripts/verify.py --feature delivery --out /tmp/medium-delivery-NEW`.
After doctor, the wrapper reads and hashes each part, checks concatenation and writes
assembled-from-parts.md. It checks missing/reordered/modified control assemblies differ,
and validates table/fence/sidecar rules. Inspect feature-results.json and the assembled file.
The checkout is not changed; evidence stays under --out.

## Gotchas

Update affected parts and the manifest whenever the approved edition changes. A manifest
proves byte identity, not Medium browser rendering, learning outcomes or anonymous URL
access. Resource-depth review remains a source-reading obligation, not an allowlist score.
