# Same Issue #8: learning-owner admission before article Boot

## Narrow scope

Baseline: medium-compiler 71fce847f6b521d812ba8179dcf4f53e06a69ef6.
The added entry gate distinguishes a source-explanation task from learned-result publication.
No scheduler, provider adapter, curriculum parser, progress writer or new skill is added.
The existing lossless CLI has one read-only preflight and enforces it before boot effects.
The P correction makes the writer consume the owner/missing_input rather than guessing a
lesson, supplying answers or downgrading a blocked learning task to ordinary writing.

The user/task determines purpose. This cooperative snapshot gate is not a security boundary
against a writer replacing the plan, sources and code together. Hash/anchor agreement is not
human identity authentication, source truth, grading, mastery or current upstream revocation.

## Actual observable result

The same existing plan and real article, with explicit purpose=learning-episode and no
learning handoff, are used on both CLI versions. Old boot creates a run and returns
next=drill-down. Candidate preflight/boot return BLOCKED, learning-owner,
missing_input=learning_handoff and create no run. This is a controlled deterministic
reproduction of a missing prerequisite gate, not a fresh natural writer baseline.

Accepted learning-owner records, human responses and progress anchors exist only in
explicitly synthetic unit tests. No real acceptance or human answer is fabricated.
Ops PR24 remains draft with pending human gates; its candidate experiment is not consumed
for the article and no Ops files, LEARNING.md, global skills or production resources change.

## Real product evidence

Same article: articles/ai-engineer-learning-path.md.
Its immediately preceding version is evidence/issue-8/expected-after.md.
One 2,043-byte insertion explains curriculum/learning ownership, NO_CHANGE, experiment
evidence, learner checkpoint versus article-reader checkpoint. It is clearly labeled a
teaching arrangement, not proof of completed placement or a learner achievement.
The pinned upstream learn skill excerpt supports progress ownership; proposed workflow
rules are identified as the article's design. Removing the insertion reconstructs the
preceding article exactly. The earlier two runtime insertions remain unchanged.

article-plan.json deliberately selects source-explanation: this is the authorized
writing-method correction, NOT a renamed attempt to publish the blocked Ops episode.
The legacy compiler is unchanged. finish imports the expanded article without fictional
prior stages, validates exact assembly, and retains its receipt. Five delivery parts are
from the same new edition. Reader review is author-only, not an independent study.

## Execute

Use new output directories outside the checkout:

```sh
python3 -m unittest discover -s tests -v
python3 evidence/issue-8/handoff/replay.py --out /tmp/handoff-proof-NEW
python3 .agents/skills/verify-medium/scripts/verify.py --feature lossless-drilldown --out /tmp/lossless-NEW
```

For the controlled before/after comparison, extract the exact old scripts/lossless_batch.py
from baseline 71fce847 into a separate checkout with its unchanged medium_compiler.py, then
pass --baseline-cli /path/to/baseline/scripts/lossless_batch.py to replay.py. No baseline
is rewritten to make the comparison pass. Per-process argv/exit/stdout/stderr/timing are
saved in commands.json; the retained run is reread in a new process after scratch cleanup.

98 tests PASS on the final local candidate. Four mechanical feature drives PASS separately;
the behavior feature is still BLOCKED / exit 3. Full mechanical CI will exercise the combined
command on the exact remote head. validation.json records the raw output digests and scope.
Local timeout/driver attempts are retained in the downloadable evidence archive, not hidden.

## Not closed

No fresh isolated writer/reader experiment, trusted learning-owner acceptance or real
curriculum progression was executed. Independent pstack source-review wave and human
learning outcome remain unmeasured. Keep Issue #8 OPEN and PR #9 DRAFT. Do not substitute
this deterministic correction for the original behavioral/human acceptance gates.
