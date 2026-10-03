# AI Engineer learning site

Static, dependency-free presentation layer for Issue #10.

Sources:
- curriculum/tutor contracts: pinned `rohitg00/ai-engineering-from-scratch` skills;
- learning progress: `LEARNING.md` when it exists;
- experiment templates/evidence: pinned Ops Reconciliation Copilot snapshot;
- article: `articles/ai-engineer-learning-path.md`.
- CEFR ALG C2+ and Voice Lab: `site/cefr-alg-c2/`, an exact static snapshot of
  `ed3c/cefr-alg-c2-` at `5a149d25b2613c772c8fcc18eb14eecb9d718c28`.

Build:

```sh
python3 scripts/build_site.py
```

Output is `dist/`. No CMS/database. The site does not write Ops, learning progress, or
product promotion. It displays source-owned state.

## CEFR ALG C2+

The homepage section and shared navigation lead to `/cefr-alg-c2/`; Voice Lab is
`/cefr-alg-c2/compare.html` (Vercel redirects to the clean URL). Both HTML files
receive an absolute `<base>` and a return link during build, so assets and module
workers resolve even when Vercel removes a trailing slash. The source snapshot
itself remains byte-identical to the pinned repository.

`references/cefr-alg-site-lock.json` records every imported file's SHA-256. Build
refuses a changed/incomplete snapshot. `/cefr-alg-c2/provenance.json` additionally
records output hashes; root provenance links this manifest. To refresh, replace
the complete snapshot from a reviewed source commit and update the lock together.
Do not copy model weights, local environments, or inference caches into this repo.

Five actual quick-conversation samples ship with WAV checksums and generation
metadata. Native LiteRT-LM remains unverified with no sample; Python generation
requires the original repository's local server. Browser Kokoro downloads public
model assets without an inference API key. Source documentation retains model,
data, license and trace limitations; this import makes no additional commercial
licensing or proficiency claims. Writing and recording are optional output
practice, not strict ALG or a CEFR assessment.

Deployment reuses the existing `noodles8/medium-compiler` Git integration and
`vercel.json`: repository root, Python build, `dist` output, clean URLs. No new
project, environment secret or paid integration is required.
