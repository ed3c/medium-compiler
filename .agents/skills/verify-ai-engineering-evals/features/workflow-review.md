# Evaluate a pinned coding workflow

## Sub-features

Inspect the claim-refusal archive, verify file identities, and assess all seven job-relevant dimensions.

## How to get to it (user POV)

Open `/ai-evals/` and select the Soodles report. For a new review, supply a pinned Soodles checkout.

## Driving it with file tools and Python

Run `python3 .agents/skills/verify-ai-engineering-evals/scripts/audit_archive.py --soodles /absolute/soodles --revision FULL_SHA --out /tmp/ai-evals-archive-NEW`. Resolve paths and SHA from the selected checkout. Read every selected owner record, consumer report and available capture. Write a fresh English assessment, then compare it with the recorded evidence. Preserve the audit JSON and assessment.

## Gotchas

A successful audit proves file identity and extracts observations. It does not prove model quality. Archived reports are retrospective data. Missing full traces leave debugging and hidden actions unassessed.
