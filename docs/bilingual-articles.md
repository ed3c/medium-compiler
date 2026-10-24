# Bilingual article website handoff

Use this contract when website delivery is selected. The semantic Content Owner
supplies complete approved English and Traditional Chinese Markdown plus the
index data below. The site builder owns presentation and navigation.
Existing Medium Stage 0–7, ALG Four annotations and Provider deployment retain
their original owners; this is not another admission stage or publication gate.

## Article-list data

Add an explicitly selected entry to `ARTICLES` in `scripts/build_site.py`:

- `slug`: a unique lowercase ASCII slug with digits and single hyphens.
- `source`, `english_source`: the complete approved repository Markdown files.
- `title`, `english_title`: each edition's exact H1 text.
- `description`, `english_description`: short source-faithful public summaries,
  approved by the Content Owner, without private review or learning claims.
- `bilingual`: `True` to render the two complete pages and their source-bound reading navigation.
- `annotations`: explicit reviewed `references/learning/` manifest integrated by `alg-four`, with annotation content owned by `speed-reading`,
  binding both source Git blobs and every paired prose paragraph.
- `download_markdown`: `True` to retain the source-download convention.

Keep registry data outside article prose. Copy approved bodies unchanged into
`articles/`; preserve first drafts, repairs and evaluations in their original
evidence locations. Do not auto-discover or expose `evals/` directories.
Missing complete editions or index metadata are errors, not reasons to render
an empty page or silently fall back to another language.

## Reader-visible behavior

Traditional Chinese uses `/articles/<slug>/`; English uses
`/articles/<slug>/en/`. The home page and `/articles/` list the article with
both language links. Each page has its own title, description, document language,
a centered reading column, language switch and Markdown download. A collapsed
middle-right rail shows one bar per top-level chapter, including the introduction;
bar length encodes rendered text amount. Hover/click opens a scrollable dialog
with heading hierarchy, every paragraph, current location and its reviewed note.
The dialog shows chapter/paragraph counts. Touch/keyboard do not depend on hover;
Escape/close restores focus. Heading navigation selects the first following
paragraph. Contents and notes use the same source anchors. English reading annotations use
[the speed-reading method](../.agents/skills/speed-reading/SKILL.md); reviewed
formatting is stored on the existing paragraph sidecar and rendered locally.
No browser/CI model calls or dictionary requests are introduced. A plain-English
fallback is required when reviewed chunks or stress evidence are absent. Headings inside code fences do not enter the contents.
Contents links have unique targets even when headings repeat.

The global site's existing navigation and styling remain shared. This feature
does not translate the entire site. speed-reading owns the reviewed paragraph/Passive/Active annotation content;
ALG Four owns its source binding, admission validation and navigation;
the builder reuses its validator/projection for each explicitly registered article.
Language switching goes to the other complete edition; it does not invent a
paragraph alignment or claim a corresponding scroll position.

## Verification and effect boundary

Each article update follows [local review before deployment](../writing-contract.md#article-updates-local-preview-before-deployment).
Serve the current build on localhost, inspect the affected language pages and
article list, and provide the actual preview URL. Website-ready handoff and CI
do not request a release; stop locally unless this update includes deployment.

Build through `npm run build:cloudflare:full -- --no-deployment-manifest` for
content/browser verification. The complete-site config remains
`wrangler.full-site.jsonc`; `npm run deploy` still targets only Reliability Lab.
Run focused site tests and actual Chromium desktop/mobile drives. Check home
and article-list discovery, both language routes, chapter/paragraph navigation, direct hashes, position tracking, dialog scrolling,
close/focus behavior and keyboard activation, readable code without document overflow, language switching and
exact source downloads. Keep screenshots and actual errors outside public prose.
Code/fence and byte comparisons need no extra SHA-256 report.

Use the existing matching-head CI. A build, artifact or browser PASS means
website verification within that scope, not semantic truth, learner mastery,
an admitted compiler history or a deployed Provider URL. Merge and deployment
require the original task's authorization; preserve Sandbox/API/Lab boundaries.

For speed-reading-authored notes, the complete annotation is the acceptance unit:
show source-bound premises and any state/order checkpoint before the short
reading cue (閱讀提示，非獨立結論). A source citation alone does not explain why
its premise matters. Follow the speed-reading Owner contract; the UI/validator
checks presence and exact bindings, while Owner/Reader review completeness.
