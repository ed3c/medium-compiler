# Group Anagrams: From the problem contract to Python runtime

LeetCode 49 · A zero-context reconstruction of invariant, canonical identity, mutability, hashing, sorting, proof and complexity.

![Cover: problem, invariant, representation, runtime, verified result.](https://medium-compiler.vercel.app/assets/alg-four/cover.svg)

*Cover · One problem, one causal path — The cover introduces the transformation from problem constraints to a verified algorithm, not a second explanation of every Python feature.*

The problem asks for groups of anagrams. Choosing a hash map is easy to memorize, but that answer hides the crucial step: how does the algorithm decide two differently ordered words belong to the same group? We will derive a stable identity from the input constraints, trace it through actual Python operations, and derive the cost from the work performed.

## The problem: what exactly must the result preserve?

Given an array of lowercase English words, return a list of groups. Each input word occurrence must appear exactly once in the output. Within a group, words are anagrams; words with different letter counts must not share a group. Group order and the order inside each group are unrestricted.

~~~python
input = ["eat", "tea", "tan", "ate", "nat", "bat"]
one_valid_output = [
    ["eat", "tea", "ate"],
    ["tan", "nat"],
    ["bat"],
]
~~~

Important constraints are the alphabet a–z, an input array that may contain repeated words, and strings that may be empty. Because the alphabet is fixed, we can build a complete identity using exactly 26 counters. That constraint—not a generic belief that hash maps are fast—is what determines our primary approach.

## Decision: find equivalence before choosing an API

Anagrams can change character order, but every character occurs the same number of times. Thus two words are anagrams if and only if their complete character-frequency counts agree. This equivalence property describes the relation between words; it is not yet the algorithm's loop invariant.

A canonical key is a representation that gives logically equivalent inputs equal keys. For a–z words, key position zero is the count of a, position one is the count of b, and so on through z at position 25. Every relevant frequency is preserved, including repeated letters; a set of distinct letters would fail for 'a' versus 'aa'.

![Decision map: a–z → letter frequency → 26 counters → equal tuple keys → one group.](https://medium-compiler.vercel.app/assets/alg-four/figure-1.svg)

*From equivalence to a canonical key — The alphabet constraint leads to fixed counters, which become a grouping identity.*

The decision sequence is now constrained: define the equivalence property, count its information, convert the count into a usable dictionary key, and insert the original word into that key's group. Hashing is a lookup mechanism; it does not define what an anagram is.

## Character-to-index mapping: why ord works

Python ord returns a Unicode code point. For lowercase English letters, those code points coincide with the ASCII range: ord('a') is 97 and ord('z') is 122. Subtracting ord('a') maps a to zero, e to four, t to nineteen, and z to twenty-five. The formula is correct here only because the problem restricts the input to the contiguous a–z range.

~~~python
ord("e") - ord("a")   # 101 - 97 = 4
ord("a") - ord("a")   #  97 - 97 = 0
ord("t") - ord("a")   # 116 - 97 = 19
~~~

An uppercase character or arbitrary Unicode symbol would violate this representation contract. A changed alphabet would require a different indexing or frequency-map strategy rather than silently reusing 26 counters.

## Program Movie: watch one word reach its group

For every word, create a fresh list containing 26 zeroes. Scan its characters from left to right, convert each character into an index, and increment that counter. The temporary list is mutable because counting is an updating operation; it is discarded as working state after a separate tuple key is created.

~~~python
word = "eat"
counts = [0] * 26
# e -> counts[4] += 1
# a -> counts[0] += 1
# t -> counts[19] += 1
# counts now has 1 at positions 0, 4 and 19
~~~

On the first word 'eat', the dictionary contains no matching key, so it creates a group holding ['eat']. The word 'tea' generates the same count tuple and appends to that group. 'tan' produces a different tuple and starts another group. 'ate' rejoins the first group; 'nat' joins the second. 'bat' starts a third. The dictionary never predicts future words: after each iteration it contains only the processed prefix.

![Runtime diagram: eat character indexes 4,0,19; tuple key; MISS creates eat; tea HIT appends.](https://medium-compiler.vercel.app/assets/alg-four/figure-2.svg)

*One runtime trace, from character to bucket — A count list is updated, converted into a tuple, then used to create or retrieve one group.*

## Python internals: mutable list, immutable tuple, dictionary

The list is suitable for repeated mutation but cannot itself be used as a dictionary key: Python lists are unhashable. Calling tuple(counts) creates a separate immutable tuple snapshot; it does not freeze or mutate the original list. This tuple is hashable because all 26 elements are integers. An immutable tuple containing an unhashable list would still be unhashable.

When looking up a tuple key, Python's dictionary hashes it to find candidate entries and checks equality where required. Two unequal keys can collide in hash value without being treated as equal. The grouping is correct because canonical tuples compare equal exactly when the complete frequency counts are equal—not because equal hash values prove equivalent words.

Our reference implementation uses an explicit missing-key branch: if the key is absent, assign an empty list, then append the original word. defaultdict(list) is an equivalent convenience for that missing-key path; only a missing-key bracket lookup invokes its factory. Neither approach copies or sorts the string that is appended.

![Python runtime: mutable list → tuple of hashable integers → hash candidates → equality → group; MISS/HIT.](https://medium-compiler.vercel.app/assets/alg-four/figure-3.svg)

*Stable identity is not the hash value — List mutation and tuple identity have different responsibilities; hash collisions still require equality.*

## Alternative strategy: sorting canonicalization

We could instead sort every word and join the sorted characters into a string key. For example, 'eat', 'tea', and 'ate' all become 'aet'. This uses the same hash-map grouping architecture, but a different canonicalization algorithm: counting works on frequencies; sorting works on ordered character sequences.

~~~python
key = "".join(sorted(word))
# "eat", "tea", "ate" -> "aet"
~~~

For a word of length K, counting reads K characters, so its per-word scan is O(K), plus fixed-alphabet overhead. General comparison sorting has O(K log K) worst-case order. A balanced merge illustration shows roughly log2(K) levels, each doing O(K) total work. It is a complexity model, not a literal step-by-step trace of CPython's adaptive, stable Timsort-family implementation or its modern Powersort merge ordering.

![Two paths: count K chars O(K) vs comparison sort K chars O(K log K), conceptual levels labelled non-literal.](https://medium-compiler.vercel.app/assets/alg-four/figure-4.svg)

*Why counting and sorting have different costs — Counting scans characters once; sorting organizes them through comparisons/merges.*

Because the input contract fixes a small alphabet, counting is the primary interview solution. If the alphabet were unknown or broad, a sorted string might be simpler to implement correctly, although its comparison-sorting cost would remain. There is no one universally best canonicalization independent of constraints.

## Derive time and space from operations

Let N be the number of words, M the sum of all word lengths, K the average word length when that shorthand is meaningful, and Σ the alphabet size, fixed here at 26. For each word we initialize Σ counters, scan each character once, construct and hash a Σ-element tuple, do an average-case dictionary lookup, and amortized O(1) list append. Therefore expected total counting time is O(M + NΣ), which becomes O(M + N) for Σ = 26; common interview shorthand is O(NK) when K is positive and fixed overhead is suppressed.

Sorting performs a comparison sort for each word. A useful upper bound is O(N + Σ over words of k_i log(k_i+1)) for K-dependent work plus grouping overhead, usually expressed as O(NK log K) for typical nontrivial word lengths. Dictionary O(1) is an average-case expectation, not a universal worst-case guarantee; both approaches still store their groups in a hash map.

For memory, the temporary counter list is O(Σ). Up to N distinct fixed-size tuple keys require O(NΣ) storage; grouping containers hold N references to existing string objects, so the additional container memory is O(NΣ + N), which is O(N) for fixed Σ. If a convention counts the full character content represented by returned strings, abstract output size can be O(M). Do not confuse the output value with the definition of space complexity, and do not claim the algorithm physically copies every character when it appends a reference.

![Cost chart: O(NΣ + M) expected time; O(NΣ+N) extra container space; output convention separated.](https://medium-compiler.vercel.app/assets/alg-four/figure-5.svg)

*Operation accounting for time and space — One pass of characters dominates; fixed counter-key work repeats once per word.*

## A complete, readable Python 3 reference

The following implementation makes its missing-key branch explicit, matching the program movie. It creates a new count list for every word, freezes it as a tuple, and appends only the original word. No special-case branch is needed for the empty string.

~~~python
from typing import List

class Solution:
    def groupAnagrams(self, strs: List[str]) -> List[List[str]]:
        groups: dict[tuple[int, ...], list[str]] = {}
        for word in strs:
            counts = [0] * 26
            for char in word:
                counts[ord(char) - ord("a")] += 1
            key = tuple(counts)
            if key not in groups:
                groups[key] = []
            groups[key].append(word)
        return list(groups.values())
~~~

### Correctness: initialize, maintain, terminate

Loop invariant: before processing index i, groups contains exactly the original words from strs[0:i], each once, partitioned by their complete character-frequency tuple; no future word is present. Initially i = 0 and the dictionary is empty, so the invariant holds. Processing a word computes the unique frequency tuple for its anagram-equivalence class, creates the group if necessary, and appends that word exactly once. The invariant is restored for i + 1.

When the loop exhausts all N words, the processed prefix is the full input. The invariant proves coverage and no duplicate insertion. Since equal tuples are equivalent to matching frequencies, each group contains only anagrams and every pair of anagrams shares a group. Returning the dictionary values therefore satisfies the task. This argument assumes the stated lowercase alphabet and Python's ordinary key equality.

### Edge cases and the first falsifier

An empty string executes no character updates and produces the all-zero tuple, so multiple empty strings naturally join the same group. A one-letter word increments exactly one counter. Repeated identical inputs are appended once for each occurrence. In contrast, a key built from only the distinct character set incorrectly groups 'a' with 'aa'; the first missing property is multiplicity, not hash-table speed.

## English interview pack: keep the meaning, simplify the speech

Approach: I use a hash map. For each word, I count the 26 lowercase letters. The count tuple is the key. Words with the same key go into the same group. I return all groups after scanning every word.

Invariant: Before processing word i, the map contains exactly the earlier words, grouped by their frequency keys. Correctness: each word enters its matching group once; after the last word, all groups are complete.

Complexity: With a fixed 26-letter alphabet, each word is scanned once. Expected time is O of N plus the total number of characters. The extra group containers and tuple keys use O of N space. Sorting also works, but each word takes O of K log K instead of a linear scan.

## Zero-context Master Map

Keep the distinctions visible: the task equivalence defines correct groups; the count tuple represents that equivalence; the loop invariant tracks the processed prefix; and dictionary hashing accelerates lookup without replacing key equality. The answer is the grouped original words. Time and space are measurements of the route taken to produce that answer, not intermediate or final data stages.

![Master map with constraints, equivalence, mutable list, tuple, dict, group output and distinct time/space measurements.](https://medium-compiler.vercel.app/assets/alg-four/figure-6.svg)

*Complete causal map — Problem → invariant → representation → runtime → correctness → complexity.*

The reusable interview habit is simple: when the task asks you to group equivalent items, first define what makes them equivalent. Then choose a canonical representation that preserves every distinguishing property. Only after that should you select the storage structure and derive its performance from the actual operations.
