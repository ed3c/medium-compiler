# Actual author revisions

First complete English draft retained in article.first.en.md.

- Replaced two `refers to` phrases with `contains` after reading sloptrim pattern 51. The original wording described array positions correctly; this is a local clarity edit.
- Removed bold markup from the five interview questions after reading pattern 56. Interview claims and technical wording retained.
- Final-body reconstruction identified an undefined `m` and an unexplained term behind the aggregate append cost. Defined `m` and amortized analysis in place.
- The iterative alternative needed explicit accounting for retained old rows and transient singleton/new-row lists. Added those state and allocation bridges before its auxiliary-space convention.
- The exact-size adaptation stated safe rejection and restoration but left its completeness/uniqueness reuse implicit. Added the decision-route argument connecting pruning to the original bijection.
- No code, input constraint, quantity, negation, branch order, example output, citation or qualification was removed.
- No new approach added in editing. First-draft deficiencies above were author-discovered before translation; no Reader feedback was accessed.
- Before English approval, removed the generic `path = path.append(...)` warning: inserted literally into this nested function it also triggers local-binding rules, so the claimed failure order was not established. The documented `append` return value and code-to-operation bridge remain.

## Translation-stage author discovery

After the first complete translation was preserved, bilingual review caught the English phrase `binary search tree` in the exact-size cost paragraph. It was the wrong data-structure term for this search. Preserved that approved English edition separately as article.before-translation-repair.en.md, then replaced it with the explicit original include/exclude-call containment argument. Added the definition of power set at its first encounter because the pivot used the term later. No code, count, assumption or method changed. The first complete Chinese draft retains the original terminology, and final Chinese receives the matching repair.
