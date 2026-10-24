# Medium article as a granularity and prose reference

- User-supplied exemplar: [LeetCode Group Anagrams: Invariant, Canonical Key, ASCII, Mutable/Immutable, Hashing, Dict, Timsort](https://medium.com/@ga874199/leetcode-group-anagrams%E4%B8%B2%E8%B5%B7-invariant-canonical-key-ascii-mutable-immutable-hashing-dict-timsort-%E8%88%87-39ef598b2776)
- User-supplied exact title/link and the **ALG-LeetCode Mental Simulator v4.0** specification are the selected style/design inputs.
- **Source-access status:** the public Medium link did not return readable full text in the October 20, 2026 lookup. The user subsequently supplied the complete comparison text in this task; it is retained in [the user reference](group-anagrams-user-reference.md). Its body can now support a direct teaching-granularity comparison. This does not establish independent retrieval from Medium or verify its claims. Correct technical imprecision rather than copying it as authority; do not invent a quality score or claim learner benefit.
- [Official LeetCode 49 contract](https://leetcode.com/problems/group-anagrams/) validates the input/output/constraints of our original example; it does not validate the Medium article's wording.

## Observable design target (derived from the supplied title and v4 prompt)

The level of specificity connects **problem contract → the classifying invariant → canonical representation → Python data-model constraints → exact runtime mutations → correctness/complexity → nearest counterexample → another implementation**. For this supplied article, the teaching scope includes why keys must be hashable, list/tuple roles, ordinal-to-index mapping, dictionary equality and collisions, the full `defaultdict(list)` missing-key path, and the sorting/logarithm derivation. These requested explanations survive an equivalent code choice. Other problems derive their mechanisms from their own task and audience; this example supplies no fixed algorithm, section or figure quota.

- An invariant must name its checkpoint and exactly which input prefix the state represents.
- A Program Movie must reflect actual code and early/final exits; avoid tool or type capabilities that do not exist.
- Expose the simplest effective baseline, the chosen operation, and the point where the alternative becomes useful.
- Explain the true performance assumption. Timsort is an implementation detail of Python sorting, not the core invariant of a frequency-key grouping algorithm.
- Treat memory anchors as a retrieval index into the full causal explanation, not a license to erase complexity, proof, failure branches or technical distinctions.
- An interview-ready explanation should be executable, falsifiable, and self-contained, not a phrase-only summary.

For generic infrastructure tutorials, replace the Python/LeetCode subject with its actual actors, API contracts, state transitions, independent readbacks and failure cases. Do **not** impose a five-anchor quota there.
