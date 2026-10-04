# Source standards and responsibility

Use the original files at these immutable versions:

- Soodles `d58c4e7ba0685c367da5c3060e06e6c5fc38f85f`:
  https://github.com/ed3c/soodles/blob/d58c4e7ba0685c367da5c3060e06e6c5fc38f85f/.agents/skills/review-writing/SKILL.md
  and its `features/writing-review.md` and `features/pclass-feedback.md`.
- pstack `e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a`:
  https://github.com/cursor/plugins/blob/e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a/pstack/skills/create-verification-skill/SKILL.md
  https://github.com/cursor/plugins/blob/e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a/pstack/skills/maintain-verification-skill/SKILL.md
- Existing eval method: `../../eval-audit/SKILL.md`; its upstream identity is in
  `../../../../references/upstream/skills-lock.json`.

This repository uses `.agents/skills`, as required by AGENTS.md.
Soodles owns its behavior and lifecycle. This skill evaluates a selected evidence scope.
medium-compiler owns report presentation. The report grants no product, merge or model authority.
Do not substitute a generated rubric for the original requirements.
Use [engineering-role.md](engineering-role.md) for the Notion-derived role responsibilities,
their source locations and applicability limits. Read engineering details before assigning
coverage labels. Notion design guidance does not establish the target's runtime behavior.

The G2i Staff Software Engineer (AI Evals) description supplied by the user motivates
seven review dimensions: engineering judgment, debugging quality, reasoning clarity,
architectural thinking, communication, attention to detail and developer trust.
It is not a disclosed G2i grading rubric. No hiring pass or personal qualification is inferred.
The job's approximately five-hour handling time is context, not a speed gate for this skill.

The FAQ navigation and local adaptation live in [evaluation-method.md](evaluation-method.md).
Source: https://hamel.dev/blog/posts/evals-faq/ (read 2026-10-04). Treat its examples and
sample-size advice as context, not universal gates. The original FAQ is not copied here.
