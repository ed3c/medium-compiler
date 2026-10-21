# Migration: source annotation is not a second article or native CEFR

The old ALG Four PR design generated four rewritten sections and a standalone summary. That inference is superseded: **new alg-four renders source-bound zh-TW Passive/Active annotations in a right-side heading/paragraph index without changing source prose, code, layout order or narrative.** The same source is revisited for four different learning operations.

| Owner | Responsibility |
| --- | --- |
| [leetcode-mental](../../leetcode-mental/SKILL.md) | Algorithm constraints, decisions, loop invariant, canonical key, runtime trace, proof and runnable code. Renamed from `alg-leetcode-mental-simulator`. |
| [medium-writing](../../medium-writing/SKILL.md) | Original Medium style, writing/editorial acceptance, source fidelity and publication. |
| [alg-four](../SKILL.md) | New annotation layer in a right-hand source-paragraph outline; source-bound Passive and Active term/sentence corpus and non-tracking learning cues. |
| [alg-vocab-encounter](../../alg-vocab-encounter/SKILL.md) | Existing Passive vocabulary leaf. |
| Frozen [cefr-alg-four-pass](../../cefr-alg-four-pass/SKILL.md), old technical UI and [alg-explainer-video](../../alg-explainer-video/SKILL.md) | Historical upstream lock and exact frozen lesson/renderer compatibility; do not rewrite or rename. |

The original 12-file CEFR upstream Git Blob lock remains untouched. New article overlays are not supported native CEFR lesson packages, do not bypass attempt → reveal → comparison gates, do not record mastery or create an LMS. The 2000 Active items and related sentences are **cross-article targets**, not per-article filler quotas.
