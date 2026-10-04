# Medium verification feature map

Read this index before driving. These are user-facing features, not claim sentences.
Source reads and live drives are both required by the pstack upkeep procedure.

Baseline: repository main ad1b76fd9c0c0ed8f48aecae54aa987964049ce1 plus this issue's changes.
Use Python 3.10+, a clean checkout and a new external --out. No API keys or Medium login
are needed for the mechanical paths. Do not drive another actor's run or discard proof.

- [Write a new article in stages](staged-authoring.md) — staged-authoring; source: medium_compiler.py: init_run / submit_stage / next_action.
- [Revise an existing article without changing protected material](bounded-revision.md) — bounded-revision; source: medium_compiler.py: _validate_copyedit / _stage6_source_link / prove_article_update.
- [Continue from the real boot article with two source-bound additions](lossless-drilldown.md) — lossless-drilldown; source: scripts/lossless_batch.py; evidence/issue-8/plan.json.
- [Read and concatenate one approved Medium article edition](delivery.md) — delivery; source: articles/ai-engineer-learning-path.parts/manifest.json; tests/test_reader_navigation.py.
- [Measure actual writer behavior and zero-context reading](behavior-evals.md) — behavior-evals; source: ../../medium-behavior-evals/SKILL.md; imported eval-audit and validation methods.
- [Verify one selected learning article](learning-article.md) — learning-article; opt-in with --article, outside the default all/mechanical set; source: scripts/verify.py: Driver.learning_article.
