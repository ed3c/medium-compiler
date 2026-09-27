# AI Engineer learning site

Static, dependency-free presentation layer for Issue #10.

Sources:
- curriculum/tutor contracts: pinned `rohitg00/ai-engineering-from-scratch` skills;
- learning progress: `LEARNING.md` when it exists;
- experiment templates/evidence: pinned Ops Reconciliation Copilot snapshot;
- article: `articles/ai-engineer-learning-path.md`.

Build:

```sh
python3 scripts/build_site.py
```

Output is `dist/`. No CMS/database. The site does not write Ops, learning progress, or
product promotion. It displays source-owned state.
