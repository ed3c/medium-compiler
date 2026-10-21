---
name: speed-reading
description: >-
  Produce ALG Four paragraph-index annotations from approved bilingual articles:
  concise Traditional Chinese explanation, complete English chunk/stress reading,
  cognitive skeleton and source-supported Active practice. Preserve source meaning and bytes.
---

# Cognitive Linguistics & Speed-Reading Engine

Transform supplied English into a **Dual-Layer Streamlined Annotated Text**.
Aim for easier scanning and lower avoidable reading effort. This is a reading
layout hypothesis: do not promise faster comprehension, one fixation per chunk,
eliminated regression, or reduced working memory without reader measurements.
Original wording, punctuation, quantities, code, conditions, negation and causal
scope remain intact. The skeleton supplements the paragraph; it never replaces it.

## Annotation Owner and input

**speed-reading owns the annotation content shown in the ALG Four article index.**
Read the complete approved English and Traditional Chinese article, not just the
current heading. For every aligned prose paragraph/blockquote, produce its concise
Traditional Chinese explanation with exact English technical terms, complete
English reading projection, short cognitive skeleton and any source-supported
Active terms, production sentences and self-expression cue/oracle.

[alg-four](../alg-four/SKILL.md) supplies the paired source identity and existing
manifest contract, binds paragraph anchors, validates coverage and renders the
index. It consumes this skill's annotations; it does not independently author a
second annotation set. `leetcode-mental` retains article meaning and `medium-writing`
retains assembly. The source article is never rewritten by annotation work.

Follow [the existing annotation contract](../alg-four/references/lesson-contract.md)
for paragraph/decision links, exact original Git blobs, overlapping Passive/Active
roles and cumulative admission. A primary source quote is not the complete causal
proof. If a sentence/oracle uses another paragraph's premise or cost derivation,
bind each supporting paragraph and exact English quote and expose its link. Keep
operation count, aggregate work and cost conditions together; do not fill an
absent argument from the author's private knowledge. Return a missing premise to
the article Owner instead of silently fixing it in a note.

Active words must help explain an actual decision/runtime fact, with a faithful
complete English sentence and source-bound cue/oracle. No per-article quota,
mechanical vocabulary harvesting or inferred learner mastery. Review the complete
meaning before applying the display rules below. Review data and uncertainty
belong in the existing evidence/sidecar, not copyable prose. Source identity is
not semantic proof. Existing approved annotations may be retained as legacy
inputs; changing the Owner contract does not relabel them as newly generated.

## Outer layer: syntax before word count

- Insert `/` before a prepositional, participial or infinitive phrase when it
  preserves attachment and makes the sentence easier to follow. Prefer roughly
  3–5 words per visual chunk where syntax allows; never split a tight unit merely
  to meet that target. A chunk is not an observed ocular fixation.
- Insert `//` at a meaningful major clause boundary and **immediately follow it
  with a line break**. Relative/subordinate clauses and a long subject/predicate
  boundary are candidates, not automatic rules. Keep a condition with its scope;
  do not make a dependent claim look unconditional.
- Enclose a genuine lexical bundle, idiom or tight modifier in `[ ]` when useful.
  Do not bracket every chunk or split a source identifier, formula or literal.
- Existing slashes, brackets, Markdown/code syntax and technical identifiers are
  source characters. Preserve them distinctly from added annotation markers.

## Inner layer: primary stress, not first letters

- Bold **only the orthographic span representing the primary stressed syllable**
  of a content word: noun, main verb, adjective or key adverb in this sentence.
- Check the word's pronunciation, grammatical role and intended sense using an
  authoritative pronunciation source. Keep the URL/entry, pronunciation and
  reviewed spelling span in the existing evidence. Phonetic syllables do not
  always map unambiguously to spelling; leave an uncertain span plain.
- Never derive stress from word length, the first letters, or another word's
  suffix. Do not copy unverified stress examples from a prompt as authority.
  A checked example is `**al**gorithm` (Cambridge `/ˈæl.ɡər.ɪ.ðəm/`).
- Do not insert syllable dots or hyphens into words. Keep their original shape.
  A one-syllable content word may be fully bold only when its role is appropriate.
- Leave articles, prepositions, auxiliaries/modals, conjunctions and pronouns
  plain. Optional backticks may recede a structural lead-in; do not suppress
  negation or scope cues. Do not bold a form of *have* merely because it looks
  like a main verb elsewhere; determine its role here.
- If stress evidence is absent, retain faithful plain English for that word.
  This fallback preserves meaning; it is not a claim of verified prosody.

## Output and review

For a direct English-text request, output only this transformed text and skeleton;
no explanations, analysis or verification report. For ALG Four, save these two
parts in the existing paragraph annotation along with the required Traditional
Chinese explanation and any admitted Active content; the rendered reading block
uses the same template:

### 【極速流暢標註文本】
[Complete source paragraph with the reviewed annotation marks]

---
* **極簡認知骨架**：`[Core Node 1]` → `[Core Action/Node 2]` → `[Core Node 3]`

The standalone template retains a 10–15-word cognitive cue. In the ALG Four
adapter, label it **閱讀提示（非獨立結論）** and use a short question or topic chain
that tells the reader what to inspect. Do not compress a theorem into an
unqualified verdict. No reader should need to infer that a cue supplies proof.

The acceptance unit is the **complete paragraph annotation**, including its
source-bound context and any linked premises, not the short cue alone. For each
annotation save `reading_context` with:

- `premises`: one or more concise Traditional Chinese statements specifying the
  applicable input, selected object, quantifier, representation or cost assumption.
  Each has `text` and `supporting_sources` containing paragraph indices and exact
  English quotes. Link other paragraphs when the current paragraph depends on them.
- `checkpoint`: a statement with the same source bindings when a result depends
  on observation time, loop boundary, completed updates or operation order; use
  null when no state/ordering checkpoint is needed. Do not invent a temporal rule
  for a purely descriptive paragraph.

Keep the complete English and concise explanation visible with these conditions;
15 words constrain only the reading cue, never the premises or proof. The UI must
show the conditions/checkpoint before the cue. A reader follows the linked source
when a note depends on a derivation elsewhere. An absent source argument remains
an article-Owner issue; adding a note cannot invent it.

Review the *whole annotation*, including retained notes and Active text, rather
than only paraphrasing its main topic. Compare its factual assertions with the
source in both directions: an example or sufficient mechanism does not establish
an exclusive or necessary mechanism. For words such as only, must and cannot,
check whether the source licenses that strength; try a different legal mechanism
that produces the same effect. Narrow the statement to its actual scope if the
reverse implication fails. Then distinguish each licensed conclusion from a
nearby illegal inference by changing an input assumption, selected set, cost model
or observation checkpoint. Require a reader to quote the explicit context/source
that licenses each distinction. A cited paragraph's existence is
not enough: the displayed explanation must say why its premise matters. Record
missing conditions and counterexamples before repair. If repeated attempts fail,
stop and reconsider the representation or acceptance unit rather than adding
another exhortation or silently supplying the missing premise while scoring.
A bounded fresh Reader result does not establish general stability or human benefit.

Before handing the complete annotation back to ALG Four, recover the original text by removing
only **added** marks, and compare it to the complete approved paragraph. Independently
check clause attachment, bundles, every bold stress span, full-annotation scope
and checkpoint, and that the cue does not assert an unsupported conclusion. A lossless comparison cannot prove those semantic judgments. If a
needed pronunciation or reading observation is unavailable, record that gap in
the existing evidence and use the plain-word fallback; do not fabricate PASS.

Pronunciation reference: [Cambridge algorithm](https://dictionary.cambridge.org/us/pronunciation/english/algorithm).
Evidence limit: [Rayner et al., 2016](https://doi.org/10.1177/1529100615623267)
reviews the speed/comprehension trade-off; it does not validate this layout.
