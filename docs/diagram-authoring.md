# Diagram authoring, derived knowledge and ownership

## Frozen route decisions (2026-10-21)
VIS-15 A: allow explicitly nominated SeeCode and oh-my-mermaid exceptions to the earlier OpenAI/Anthropic/Cursor employee-only preference. Neither is attributed to those companies.
VIS-16 A: SeeCode is editorial/teaching design-time renderer: standalone HTML in an isolated preview, reviewed static SVG in an approved article. The original Noodle canonical Native Runtime Graph remains unchanged.
VIS-17 A: oh-my-mermaid generates candidate multi-perspective architecture docs. After independent source review, commit versioned derived Mermaid/Markdown into docs/derived-architecture; no Cloud Push.

All ViewEnv Q1–36, VIZ-01–04, VIS-06–14 and DuckDB selections remain frozen. No new decision was needed after the bounded Thinking × Ambitious cross-check.

## Counterexamples / methodology
- SeeCode import can simplify a large graph, so a visually appealing Figure may omit or merge nodes; disclose the loss relative to its original source.
- OMM scanner may infer code relationships; recursive .omm nodes describe static source interpretation, not observed runtime handoffs.
- Noodle Graph v2 keeps original Owners, IDs, conditions and acceptance evidence; neither new tool creates green runtime edges.
- Baseline and treatment require side-by-side real browser interaction, a semantic source check and a second review independent of the candidate producer. It is not sufficient to pass a SVG validator.

## Frozen upstream source and commercial rights
SeeCode at Aryanutkarsh/SeeCode commit 067ca2594e8e8ec87e7bcd14e9dcf7549f0f9913, MIT.
oh-my-mermaid at oh-my-mermaid/oh-my-mermaid commit 38ccdb69298adec949177c92c88d6e3ddfb5bab7, MIT.
The optional installer preserves upstream LICENSE and full selected SKILL tree. No global install and no runtime network or Provider effects. Fonts, encoders and other assets retain separate third-party rights.

SeeCode's font mode is SYSTEM: no Google Fonts request. An isolated browser fixture is allowed; no same-origin inclusion of arbitrary generated HTML in private Host sessions. For other documents export SVG first, with original source and human reviewed metadata. Images are lower-trust than primary technical sources.

OMM's selected SKILLs are omm-scan and omm-view only; omm-push is excluded. AI-generated .omm files are candidates, and source revisional changes require re-review. OMM's source scanner/CLI is not automatically executed by installing its SKILL.md. No cloud login, arbitrary repository upload or remote push.

## Source-bound review and implementation
Use python3 scripts/install_diagram_authoring.py --dry-run then python3 scripts/install_diagram_authoring.py in a trusted checkout. A fixture is tests/fixtures/visual-authoring/flowchart.json. Optional local candidate rendering:
node .agents/skills/seecode/scripts/seecode.mjs render tests/fixtures/visual-authoring/flowchart.json --out /tmp/review-example.html

A real standalone HTML output is inert with respect to the Soodles/Noodle Native API: test its isolated browser screenshot, focus, contrast, motion and refusal of network resources before optional reuse. CI runs the real pinned SeeCode CLI on the fixture and captures an actual Chromium screenshot; it does not publish a new article. OMM's actual semantic scan of a live repository, native tool installation and codebase review are not claimed by a source-only test.

The registry at design/diagram-candidates/manifest.json is empty initially. scripts/verify_diagram_candidates.py checks exact source/candidate hashes, loss report and asserted review identity when entries are proposed. Review metadata alone does not establish independent review or prove figure fidelity. The reviewed architecture output directory is docs/derived-architecture/, not .omm cloud state; no generated real architecture has been approved for this first slice.

Published diagrams need exact original source references and a disclosure review by the current content Owner; Graph Viewer needs original v2 Event/Provider Owner readback. Browser PASS is not Native Runtime Acceptance. Main site and Cloudflare Production remain unchanged.

## ARC-02 A — first codebase target

The initial actual source-read target is medium-compiler at a chosen pinned revision. Only approved source paths in this repository may be analyzed for new OMM candidates; Soodles, Noodle and NeoWeaver are reference names, not authorized additional scan targets. The OMM skill installation/CI render of an unrelated SeeCode fixture does not prove an OMM scanner was invoked. No OMM-derived medium-compiler architecture diagram has passed independent review or been committed as an approved artifact. See [the unified routing map](visual-architecture.md) before extending source scope.
