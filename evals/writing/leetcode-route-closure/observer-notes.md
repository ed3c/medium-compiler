# Observer notes

- App captures use includeOutputs=true, turnLimit=10, maxOutputCharsPerItem=20000.
  Captured command-output truncation: criteria 0; temperatures Writer 2;
  subsets Writer 2; temperatures Reader 1; subsets Reader 0; deletion Reader 0.
  These are observer capture limits, not proof that consumer tool responses were truncated.
  The complete responses and command inventory stay in external observer/capture-audit.json.
- An observer JavaScript template attempted to interpolate an undefined EV variable.
  functions.exec returned ReferenceError before any shell call or write.
  The corrected script independently checked all 115 quotes and copied the existing Schema consumed record.
- Two observer inspections printed overly large capture command text and were truncated.
  They were not used to establish article quality; articles/reports/Reader output were inspected separately,
  and the quote verifier reads complete files. Original captures were not overwritten.
- No post-Reader article or frozen method edits. Negative results remain visible.

- git diff --cached --check exited 2 on author-provided unified-diff blank context lines.
  Exact original diff bytes are preserved in two .diff.gz files; observer zero-context diffs remain readable.
  No original article, first draft or raw result was trimmed.
- The first wrapper for that preservation script had an unescaped template backtick;
  JavaScript parsing failed before execution. Corrected wrapper completed without changing preserved bytes.
