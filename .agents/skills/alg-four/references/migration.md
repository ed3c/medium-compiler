# ALG Four owner migration — source-level boundary and legacy compatibility

Decision Q50 B selects an **independent project-local** `alg-four` for **new** learning lessons rather than a second alias pointing to the old `cefr-alg-four-pass`.

| Consumer or artifact | New owner/action | Why the old bytes remain |
| --- | --- | --- |
| New article→English lesson (verify-learning-article) | `alg-four` owns the full-article lesson. | Existing recipe currently says one decision only; that is replaced for new lessons. |
| Writer (medium-writing) | Reuses `alg-four` for acquisition outputs; writer still sole Medium publisher. | Doesn't adopt CEFR learning/publishing authority. |
| LeetCode simulator | Remains algorithm/solution owner; optional handoff to `alg-four` for English learning. | Its printable /full oracle is not a gated learner session. |
| Passive vocabulary | Retain pinned `alg-vocab-encounter` leaf and its exact bytes. | Reuses lexical recognition instead of creating a second vocabulary trainer. |
| Frozen existing lesson and CEFR technical UI | Legacy source-bound `cefr-alg-four-pass`; **read-only** compatibility. | `references/upstream/cefr-alg-skills-lock.json`, `site/cefr-alg-c2` snapshot and existing `lesson.json` point at exact historical file revisions. |
| Old `alg-explainer-video` handoff | Frozen legacy packages only until consumer version supports new `alg-four` package. | It is pinned and still names the historical upstream Skill. Rewriting it would defeat the lock. |
| New standalone English learning page | Source-bound ALG Four **worksheet**, separate from Medium article, non-tracking. | Not a new LMS, video renderer or runtime gate. |

**A source lock is not a writable router.** The older 12-file `cefr-alg-skills-lock.json` authenticates upstream history; it must not be deleted, overwritten or altered merely because a future Authoring Owner changed. The new `alg-four` lives outside that 12-file scope and is registered normally. New lesson sources are bound by their own source blob in the learning manifest and site provenance.

**Migration stop:** A true dynamic native CEFR lesson using `alg-four` must obtain a versioned consumer schema, an actually compatible runtime/renderer and fresh attempt/reveal/compare readback before claiming migrated execution. Until then new lessons can be authored and published as evidence-labeled **worksheet** pages; the old live CEFR route retains its historical operation. This is a deliberate partial boundary, not an implicit claim of full runtime migration.
