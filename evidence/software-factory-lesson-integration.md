# One frozen lesson, consumed by Medium

This continues PR #29. The earlier English-first Git decision evidence remains historical in
`learning-article-english-first.md`; the observations below were collected on 2026-10-04.

## Accepted source and bounded change

[CEFR Issue #8](https://github.com/ed3c/cefr-alg-c2-plus/issues/8) completed through its original
Soodles/Noodle owner. [PR #9](https://github.com/ed3c/cefr-alg-c2-plus/pull/9) merged as
`b4b37fd95e9e654aa11c70ce76333aaeea683cd1` after exact-candidate
`164b1601a78e3de001635e62c14c6ee80e8a8a5d` passed
[Actions run 37187333321](https://github.com/ed3c/cefr-alg-c2-plus/actions/runs/37187333321).
The owner returned resolved, closed the issue, reconciled the original order, removed its worktree
and restored host configuration. The upstream result is product acceptance, not learner acceptance.

Medium imports twelve complete skill files at that merge revision and nine changed/new website
files. The other 45 snapshot files retain their bytes, including the existing narration and Voice Lab
assets. Separate skill and site locks preserve both inventories. The doctor verifies skill Git blobs
and relative references; the site builder verifies the complete snapshot before copying it.

`verify-learning-article` now routes learning-content work through the supplied compiler and vocabulary
skill, and video work through the frozen-input renderer and the available Hypit runtime. Existing
frozen packages are reused. Pure link/format repairs do not compile a lesson. `verify-medium` remains
the mechanical verifier; its success does not prove translation equivalence or source truth.

The selected lesson is `software-factory-sole-acceptance@1.0.0`. Its seven English clarity, C2 precision
and Traditional Chinese sentences are preserved. The public JSON removes the two private source paths
and makes the compiler path relative; all other values equal the frozen original. Four selected source
slices support this lesson. It is not completion of all 27 supplied cards or a full Medium long article.

Original lesson SHA-256 is `4dd5d0c09ee829290db29c58cff78c1f3f2e14bbb6261cc424f148cc328e19c1`.
Portable lesson SHA-256 is `ba829a6fede10a3b7dfb6c3b999f554159bbdec94b2540e630ef951a747b715c`.
Narration SHA-256 is `9ee68b89c9fce494e50f14d24a847620cb40bedfe6bb0d19cdcb128a1ebb6e31`.
Video SHA-256 is `f171144553782a2af03a0fb33f6375abdd963563a1b2522a35d32842da0bd050`.
The supplied Hypit video is 41.233 seconds, 1280×720, 30 fps, H.264/AAC. No render or TTS was repeated
for this import. The editable Hypit project remains a separate retained deliverable.

## Build and real browser controls

The homepage links to `/cefr-alg-c2/technical?lesson=software-factory-sole-acceptance`.
Only built HTML receives the Medium return link, base URL, current query/fragment navigation and
an accurate imported-snapshot label. Vendored HTML/JavaScript remain upstream bytes. Source and
output hashes are recorded separately in `/cefr-alg-c2/provenance.json`.

Chrome 154.0.8037.93 drove a fresh local build at 1280×900 and 390×844. The test server supported
byte ranges and emulated clean HTML routes; this is local evidence, not deployment evidence.
The run made ordinary clicks, keyboard actions and downloads. It did not invoke runtime handlers
or media playback through page evaluation.

- Homepage entry, all four directory links and keyboard skip link preserved the named lesson query.
- Directory ownership preceded the source-bound decision diagram and practice. Mobile had no horizontal overflow.
- Default lesson still loaded; unknown lesson displayed an explicit error with content hidden.
- Rendered clarity/C2/Traditional Chinese arrays matched the frozen lesson; Pass 3 transcript was available by default.
- Typed text alone did not unlock reveal. An empty draft plus oral-attempt acknowledgment did.
- Withdrawal before reveal disabled the gate. Reveal latched acknowledgment, retained GENERATED and exposed no receipt.
- Separate comparison confirmation enabled the receipt. Shadowing alone remained COMPARED; semantic practice could record ACTIVE_PRACTICED.
- Actual downloaded receipt bytes equaled the preview. Navigation retained history; reload cleared it and required new events.
- Native video controls advanced to 1.362485 seconds, paused at 1.364679 seconds, then sought to 25.031231 seconds.
- No page errors or eager model downloads occurred. Dynamic Kokoro synthesis was not exercised by this import test.

The first browser attempt stopped when a mouse click targeted the keyboard-only skip link while it
was outside the viewport. The second attempt used focus and Enter, then passed the complete controls.
Both attempts are retained. No product workaround or forced click was added.

## Verification and independent review

- `skill-creator` metadata/structure validation passed.
- Doctor passed with 22 registered skills and the accepted CEFR revision.
- Complete unittest suite passed, 158 tests. New controls reject missing/changed/extra dependency files and unresolved relative paths.
- Four mechanical drives passed: staged-authoring, bounded-revision, lossless-drilldown and delivery.
- Behavior evaluator still exited 3 with BLOCKED. No separate writer/reader experiment or learner-effect result was invented.
- Build, source/output hashes, retained audio manifests and actual browser controls passed.
- A separate source reviewer found no P1/P2 in the Medium diff. This review did not repeat browser or software execution.

The first suite run exposed an old link checker treating a query as part of a filename. Its URL parsing
now separates the path and resolves configured clean HTML URLs before checking existence. The second
complete suite passed; the failed output remains available. No guard, hook or test was disabled.

A fresh native consumer with no inherited turns read the modified skill and pinned dependencies for
three requests. It selected frozen-package reuse for existing media, source acquisition before new
compilation for a new article, and bounded source correction for a link-only repair. It preserved the
English-first request and did not infer mastery or a new render. It also reported the deliberately
unavailable new article and URLs, and the absent project-local narration file rather than inventing them.
This is a scoped consumer report, not filesystem read isolation, a complete private reasoning trace,
cross-model evidence, or general semantic-quality proof.

## Retained evidence identities and limits

The external task evidence directory is named `software-factory-e8nm4zgm`; current Medium outputs are
in `pr29-verification/`. Commands record cwd, argv, exit status and duration. Important SHA-256 values:

- `commands.json`: `7dca32eafb61bb832341b75804db03f3c726619c0e25ff16efe58c671138735a`
- `browser-attempt02/browser-observations.json`: `5b950b6cc32530c4d8e7c2ffd4c59f432130ff00bb4d9d5dfc269b37190d6361`
- `browser-attempt02/receipt-active.txt` and `receipt-after-navigation.txt`: `dd1363816823452e8b4c3d579f6f02eb3672613ffeb193201b9048285f16a645`
- `browser-attempt02/receipt-new-session.txt`: `8ba1127f2eb075a1bb91030dde7022df9031355930ac0b88026aceec1ed7bf1d`

These are synthetic UI operations and learner-report fields. They do not prove actual learner cognition,
pronunciation, retention, CEFR level, flow or taste. STE-inspired prose is not ASD-STE100 certification.
Supplied source reports remain unverified, the failed-button example remains hypothetical, and the
long-horizon completion boundary remains open. Exact-head CI and deployed-route readback are subsequent
delivery observations and must be linked to their actual commit; this local report does not claim them.
