---
name: maintain-medium-verification
description: Maintain the complete medium-compiler verification skill and feature map using the pstack source-wave and actual-drive standard. Use for full-map audits, not a single writing edit.
---

# Maintain the verification map

Read ../verify-medium/references/maintain-verification.md and ../verify-medium/SKILL.md.
The upstream method is the standard; this adapter changes the target directory to .agents.

1. Index hygiene: read ../verify-medium/features/README.md; compare entries to sibling
   feature files. Missing/duplicate/dead links are drift. Do not generate a replacement registry.
2. Source wave: one independent, read-only subagent per feature, concurrently when the
   carrier supports it. Each returns summary / actual source entry points / drift or none /
   one user-path recipe. Children never drive or edit. Without that capability, label
   coordinator-only review and BLOCKED for the strict source wave; do not impersonate children.
3. Reconcile: inspect each returned source citation. Combine overlapping recipes without
   skipping any feature; check recent changed user surfaces against actual commands/files.
4. Live pass: coordinator alone runs verify-medium --feature all in a new external --out.
   Doctor before each fresh CLI drive and after surprises. Keep failed traces and retain
   evidence after cleanup. A documented missing prerequisite may make one feature unreachable;
   do not call a different route proof for the missing one.
5. Triage within edit scope: only ../verify-medium/ (skill, map, harness). Product defects
   in medium_compiler.py, scripts/lossless_batch.py or article meaning are reported separately;
   do not rewrite the map to hide them. Re-drive any corrected harness before shipping.
6. Outcome: clean only when every source and live row completes and no change is needed;
   changed for one proven correction PR; blocked when coverage/delivery cannot complete.
   Keep run notes in scratch. Product Issue evidence belongs to the product task, not an
   excuse to enlarge routine maintenance into a new governance system.
