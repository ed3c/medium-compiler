# Group Anagrams: from letter counts to Python runtime

A derivation of canonical keys, `ord`, mutable lists, hashable tuples, `defaultdict(list)`, and the cost of counting versus sorting.

![Group Anagrams: problem, frequency equivalence, canonical key, runtime, proof and cost.](https://medium-compiler.vercel.app/assets/alg-four/cover.svg)

*One causal path connects the problem constraints to grouping and its expected O(M + N) cost.*

The strings `"eat"`, `"tea"`, and `"ate"` look different when read from left to right. Each contains one `a`, one `e`, and one `t`. Giving those three strings the same key turns a grouping problem into a dictionary lookup.

That key must preserve enough information to decide whether two strings are anagrams. Its Python representation must also be usable in a dictionary. The algorithm follows from those two requirements: count letters in a list, convert the completed counts to a tuple, and append the original string to the group stored under that tuple.

## What a correct answer must preserve

In [LeetCode 49, Group Anagrams](https://leetcode.com/problems/group-anagrams/), the input is a list of strings. Anagrams use the same letters with the same multiplicities, possibly in a different order. For example:

```python
strs = ["eat", "tea", "tan", "ate", "nat", "bat"]
```

One valid result is:

```python
[
    ["eat", "tea", "ate"],
    ["tan", "nat"],
    ["bat"],
]
```

The order of the groups and the order within a group do not affect acceptance. Every input occurrence must appear exactly once: two occurrences of `"eat"` must produce two occurrences in the output. This is grouping, so removing duplicates would change the task.

The published constraints allow between 1 and 10,000 strings, each between 0 and 100 characters long, using only lowercase English letters. The empty string is therefore a real case, not invalid input. Our implementation builds new containers and leaves the input list and its strings unchanged.

A direct baseline would keep a list of groups and compare each incoming string against a representative of every group until it finds an anagram. If many strings belong to different groups, the first string faces no existing representative, the second faces one, the third faces two, and so on. Up to `N(N - 1) / 2` comparisons arise before accounting for the characters examined inside each comparison.

The repeated work is searching through groups to discover the right one. A dictionary can avoid that search if we first give every group a reliable key.

## Find what survives rearrangement

For `"eat"`, `"tea"`, and `"ate"`, position changes but letter frequency does not:

```text
             a   e   t
"eat"        1   1   1
"tea"        1   1   1
"ate"        1   1   1
```

This is the equivalence property we need: two lowercase strings are anagrams if and only if their counts agree for every letter.

The forward direction follows because rearranging letters cannot add or remove an occurrence. The reverse direction matters just as much. If every count agrees, take the letters required by the second string one position at a time. The first string has exactly the required supply of every letter, so its characters can fill all those positions. Equal counts are sufficient, as well as necessary.

A *canonical key* is one standard representation shared by every member of an equivalence class. Here, a class is one anagram group. We want:

```text
anagrams          -> equal keys
not anagrams      -> unequal keys
```

Letter presence alone is too weak. `"ab"` and `"aab"` both contain the letters `a` and `b`, but the second has an extra `a`. A set discards that multiplicity. Counts keep it.

Because the alphabet is fixed to `a` through `z`, we can reserve 26 positions in a fixed order:

```text
position:  0  1  2  3  4  5  ...  19  ...  25
letter:    a  b  c  d  e  f  ...   t  ...   z
```

The order of the positions is part of the representation. A value of `1` at position 0 means one `a`; the same value at position 1 means one `b`. We must preserve both the counts and which letters they belong to.

For `"eat"`, the completed representation has 1 at positions 0, 4, and 19, and 0 everywhere else. Counting `"tea"` gives the same representation without having to rearrange either original string.

The design decisions now have explicit reasons:

- Preserve frequencies because rearrangement preserves multiplicity.
- Use 26 counters because the input alphabet has exactly 26 possible letters.
- Use a dictionary from a completed key to a list of original strings because the required output contains whole groups.
- Use a mutable list while counting, then a hashable tuple for dictionary lookup.

![Decision map: lowercase a-z permits 26 counters; equal count tuples identify anagram groups.](https://medium-compiler.vercel.app/assets/alg-four/figure-1.svg)

*Fixed letter positions preserve the anagram equivalence property in a canonical key.*

## Turning a character into a counter position

Start one word with:

```python
count = [0] * 26
```

`count[0]` will hold the number of `a` characters seen, `count[1]` the number of `b` characters, and so on. The list is *mutable*: assigning a new value to one of its positions changes that list.

The next operation needs a number between 0 and 25 for the current character. Python's [`ord`](https://docs.python.org/3.14/library/functions.html#ord) returns the Unicode code point of a one-character string. For these letters, the values also agree with ASCII:

```text
ord('a') = 97
ord('b') = 98
ord('c') = 99
...
ord('z') = 122
```

The values are consecutive. Subtracting the value for `a` shifts the range from 97–122 to 0–25:

```python
index = ord(c) - ord('a')
count[index] += 1
```

`ord` does not return an alphabet position by itself. The subtraction supplies that position under the lowercase `a`–`z` constraint.

For `"eat"`, the working state changes as follows. Each description of nonzero entries below means that every unlisted counter is still zero.

```text
Before scanning:       all 26 counters are 0

c = 'e'
ord('e') = 101
index = 101 - 97 = 4
count[4]: 0 -> 1        nonzero entries: e:1

c = 'a'
ord('a') = 97
index = 97 - 97 = 0
count[0]: 0 -> 1        nonzero entries: a:1, e:1

c = 't'
ord('t') = 116
index = 116 - 97 = 19
count[19]: 0 -> 1       nonzero entries: a:1, e:1, t:1
```

`count[index] += 1` reads the integer in one slot, adds one, and assigns the resulting integer back to that slot. The list changes; the integer object does not change in place.

The expression `[0] * 26` is safe here even though it initially repeats references to the same integer value. Integers are immutable, and updating one slot replaces that slot's reference. This differs from repeating a mutable object such as `[[]] * 26`, where all positions would refer to the same inner list.

There is a precise checkpoint property inside this loop:

> Before processing character position `j` of `s`, `count[p]` equals the number of occurrences of the letter at alphabet position `p` in `s[:j]`, for every `p` from 0 to 25.

At `j = 0`, the processed prefix is empty, so zeros are correct. Processing one character increments exactly the corresponding counter. When the character loop ends, the prefix is the entire string and all 26 counts are complete.

The lowercase condition makes every index valid. This code should not be generalized by assuming that all Unicode letters occupy one consecutive range. Even uppercase `A` gives `65 - 97 = -32`, outside this list's valid negative-index range. A different alphabet requires a different mapping.

![Character trace: eat maps to indexes 4, 0 and 19, completed counts form a tuple, and equal keys share a group.](https://medium-compiler.vercel.app/assets/alg-four/figure-2.svg)

*One word moves from characters to counters to a tuple key. The first equal key is a MISS; later equal keys reuse the existing group.*

## Why the counting list becomes a tuple

The list has served as working state. The dictionary needs a key whose hashing and equality behavior stay valid while it is stored.

Python calls an object *hashable* when it has a lifetime-stable hash and supports comparison, with equal objects required to have equal hashes. Built-in lists are unhashable; a tuple is hashable only when all its elements are hashable. These rules are stated in the [Python hashable definition](https://docs.python.org/3.14/glossary.html#term-hashable).

Why would changing a key's value be a problem? Suppose a dictionary chose a search location from a list's contents, then those contents changed. Looking up the modified contents could lead to a different search path from the one used to store the original entry. Python avoids this problem for ordinary lists by rejecting them as keys:

```python
count = [1, 0, 0]
# {count: []} would raise TypeError: unhashable type: 'list'
```

This is a rule about the type, even if a particular program promises never to change that list. Mutability also does not universally imply unhashability: custom objects can define different identity rules. For this solution, the relevant facts are that a built-in list cannot be the key and a tuple of integers can.

After counting, create the key:

```python
key = tuple(count)
```

The complete tuple for `"eat"` is:

```python
(1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0,
 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0)
```

`tuple(count)` creates a new container with the current 26 values. It does not turn the original list into a tuple, and it does not make that list immutable. Changing `count[0]` later would leave `key` unchanged. Calling this a *freeze boundary* describes the snapshot used as the key.

A tuple's fixed positions alone are insufficient if an element is unhashable. For example, `(1, [2, 3])` contains a list and cannot be hashed. Our key contains only integers, so this restriction is satisfied.

The roles are different: the list holds counts that are still changing; the tuple records completed counts for identification. The next word receives a fresh counting list, while the dictionary retains any tuple needed to identify an existing group.

## Equal keys, hashes, and dictionary lookup

A dictionary, also called a hash map, stores associations from keys to values. Our association will be:

```text
26-count tuple -> list of original input strings
```

The tuple for `"tea"` is a newly constructed object, but its 26 values equal those of the tuple for `"eat"`. Dictionary keys do not have to be the same object to refer to the same entry. Equal tuple values identify the same key.

Hashing helps find that entry. A hash function combines information about a key into an integer. For a tuple, its elements' hashes contribute to that calculation; hashing a sequence is not generally free regardless of its length. Here the length is always 26.

A useful conceptual lookup is:

```text
key -> hash -> candidate table position
                  |
                  +-> matching key: return its value
                  |
                  +-> different key: keep searching
                  |
                  +-> absence established: key is missing
```

[Python's design FAQ](https://docs.python.org/3.14/faq/design.html#how-are-dictionaries-implemented-in-cpython) describes CPython dictionaries as resizable hash tables. The diagram abstracts away their exact layout and probing rules; it is not a promise of one memory access per lookup.

Two unequal keys can have the same hash. This is a *hash collision*. They can also initially compete for a table position even when their full hash values differ. In either case, a dictionary resolves the search rather than declaring the keys equal. Where a hash permits a possible match, equality distinguishes the actual keys.

For anagrams, the reasoning is therefore:

```text
same letter frequencies -> equal tuples -> same dictionary entry
```

It would be wrong to replace the tuple with `hash(tuple(count))` as the sole key. That would discard the information needed to distinguish unequal frequency tuples if their hashes collided.

Under the usual assumption of well-distributed hashes and a maintained table size, the average lookup takes constant time with respect to the number of dictionary entries. `O(1)` describes that scaling, not a literal count of CPU instructions. Severe collisions can require a search through many entries, so the bound is not an unconditional worst-case guarantee.

## What `defaultdict(list)` does on a miss

Create the mapping with:

```python
from collections import defaultdict

groups = defaultdict(list)
```

`list` is a callable stored as the dictionary's `default_factory`. Passing `list` gives the factory itself; `list()` would call it immediately and pass an empty list instead.

The subscription `groups[key]` uses `__getitem__`; if the key is absent, that method invokes `__missing__`. With this factory, Python calls `list()` without arguments, inserts the resulting empty list under the missing key, and returns that list. A hit returns the stored list. The [defaultdict documentation](https://docs.python.org/3.14/library/collections.html#collections.defaultdict) specifies this behavior and notes that `get()` does not trigger the factory.

That makes the grouping operation:

```python
groups[key].append(s)
```

On a miss, the subscription creates and returns the group before `append` runs. On a hit, `append` extends the existing group. Each missing key receives a separately created list.

With an ordinary dictionary, the corresponding missing-key logic would be:

```python
if key not in groups:
    groups[key] = []
groups[key].append(s)
```

This shows the same grouping behavior; it is not a claim that the two spellings execute the same number of lookups internally.

The return value of `append` is `None`. Its useful effect is mutating the group list, so we do not assign its return value back to `groups[key]`. Python documents this convention for collection-mutating methods in [Built-in Types](https://docs.python.org/3.14/library/stdtypes.html).

![Python data model: mutable counting list, tuple snapshot of integers, hash candidates and key equality.](https://medium-compiler.vercel.app/assets/alg-four/figure-3.svg)

*The completed tuple identifies the group. Hashing locates candidates; equality determines whether the key matches. The list remains mutable after its tuple snapshot is created.*

## A program movie: from the first character to the returned groups

Use the original example with an empty string and a duplicate added:

```python
["eat", "tea", "tan", "ate", "nat", "bat", "", "eat"]
```

For compact state displays, call the completed frequency keys `E`, `T`, `B`, and `Z`:

```text
E: a:1, e:1, t:1; all other counts 0
T: a:1, n:1, t:1; all other counts 0
B: a:1, b:1, t:1; all other counts 0
Z: all 26 counts 0
```

These letters are display labels, not the dictionary keys used by the program. The actual keys remain 26-integer tuples.

Initially `groups` is empty. For the first string, `"eat"`, the character trace above produces `E`. `groups[E]` misses, calls `list()`, stores `E -> []`, and returns that empty list. Appending changes it to `["eat"]`.

For `"tea"`, a fresh zero-filled list receives three updates:

```text
read 't': index 19; nonzero counts t:1
read 'e': index  4; nonzero counts e:1, t:1
read 'a': index  0; nonzero counts a:1, e:1, t:1
```

Its completed tuple equals `E`. The lookup hits the existing `["eat"]` and appends `"tea"`. No new value list is created:

```text
groups before: E -> ["eat"]
groups after:  E -> ["eat", "tea"]
```

For `"tan"`, the indexes are 19, 0, and 13. Its tuple is `T`, different from `E` at the `e` and `n` positions. The lookup misses and creates a second group:

```text
E -> ["eat", "tea"]
T -> ["tan"]
```

The next words reuse or create the appropriate entry:

```text
"ate": indexes 0, 19, 4  -> E -> ["eat", "tea", "ate"]
"nat": indexes 13, 0, 19 -> T -> ["tan", "nat"]
"bat": indexes 1, 0, 19  -> B -> ["bat"]
```

For `""`, no character iteration runs. The initial zeros are already the completed counts, so `Z` is a valid key. Its missing-key path produces `Z -> [""]` without a special empty-string branch.

The final `"eat"` produces `E` again. Appending it preserves the second input occurrence:

```text
E -> ["eat", "tea", "ate", "eat"]
T -> ["tan", "nat"]
B -> ["bat"]
Z -> [""]
```

Only now, after the outer loop is exhausted, does `list(groups.values())` build an outer list from the stored group lists:

```python
[
    ["eat", "tea", "ate", "eat"],
    ["tan", "nat"],
    ["bat"],
    [""],
]
```

The result contains references to those group lists. The strings inside are the original string objects; counting did not replace them with tuples or sorted spellings. No early return occurs after finding the first matching group, because future input occurrences still need to be included.

## The complete Python solution

The implementation follows the same order as the movie:

```python
from collections import defaultdict
from typing import List

class Solution:
    def groupAnagrams(self, strs: List[str]) -> List[List[str]]:
        groups = defaultdict(list)

        for s in strs:
            count = [0] * 26

            for c in s:
                index = ord(c) - ord('a')
                count[index] += 1

            key = tuple(count)
            groups[key].append(s)

        return list(groups.values())
```

A standalone call is:

```python
result = Solution().groupAnagrams(
    ["eat", "tea", "tan", "ate", "nat", "bat", "", "eat"]
)
print(result)
```

`groups` survives across word iterations because it contains the accumulated answer. `count` is created inside the outer loop because it describes only the current word. The inner loop completes before `tuple(count)` because a partial prefix is not the identity of the complete word. The append happens once per outer iteration, after the key is ready. Returning the values after all iterations exposes the groups rather than their implementation keys.

A single-character input such as `["a"]` increments slot 0 and returns `[["a"]]`. An input of two empty strings returns `[["", ""]]`. Neither requires an additional branch. Although the published input contains at least one string, the same code also returns `[]` for an empty input list.

## The property that stays true during grouping

The fact that anagrams share counts describes the relationship between strings. A *loop invariant* describes what the program state means at a particular time. The outer-loop invariant is:

> Before processing input index `i`, `groups` partitions exactly the occurrences in `strs[:i]` by their complete 26-letter frequency tuples: each processed occurrence appears once in its matching group, each stored group is nonempty, and no occurrence at index `i` or later has been added.

This wording includes the checkpoint, the processed prefix, the exclusion of future inputs, and the meaning of every stored group.

Initially, `i = 0`. No occurrences have been processed and the empty dictionary represents the empty prefix, so the invariant holds.

Suppose it holds before processing `strs[i]`. The inner-loop property established earlier proves that `count` records every letter of this word when the scan ends. Converting those counts to a tuple preserves the values. If the key already exists, the word is appended to its one matching group. If it is missing, a new empty list is stored and the word is appended there. The program adds exactly the current occurrence once and changes no other group's contents. The dictionary therefore partitions `strs[:i + 1]`, restoring the invariant for the next iteration.

At termination, `i = N`: the processed prefix is the entire input. Every occurrence appears once. Equal tuple keys put anagrams together, and the equivalence proof ensures that unequal anagram classes cannot share a tuple. Returning all the value lists therefore returns exactly the required partition.

Hash collisions do not invalidate this proof because the dictionary retains the tuple keys and uses their equality rules. The proof would fail if we stored only a hash integer and treated it as a unique group identity.

## A small wrong implementation and its first failure

Moving the counting list outside the outer loop may look like a harmless allocation saving:

```python
count = [0] * 26
for s in strs:
    for c in s:
        count[ord(c) - ord('a')] += 1
    groups[tuple(count)].append(s)
```

It changes the meaning of `count`. After the first word, it still contains that word's counts when the next word begins.

A two-word separating example is:

```python
["a", "a"]
```

The first word produces a key with `a:1` and creates `["a"]`. Before the second scan, `count[0]` is already 1. Reading the second `a` raises it to 2. The second word is stored under the key for two `a` characters, producing two separate groups instead of `[["a", "a"]]`.

The first incorrect state is the start of the second word: the current word has an empty processed prefix but its working counters are not zero. The inner-loop invariant already fails there, before the dictionary can do anything useful. Creating `count = [0] * 26` inside the outer loop is the direct repair.

This example also separates the lifetimes of the two containers. The dictionary must accumulate across words. The counting list must start fresh for each word.

## Sorting provides another canonical key

An alternative is to sort the characters and join them into a string:

```python
key = ''.join(sorted(s))
```

For the same three anagrams:

```text
"eat" -> ['a', 'e', 't'] -> "aet"
"tea" -> ['a', 'e', 't'] -> "aet"
"ate" -> ['a', 'e', 't'] -> "aet"
```

`sorted(s)` creates a new list; `join` forms the key string. The original `s` remains available to append to the group. Sorting preserves all occurrences, so `"ab"` becomes `"ab"` and `"aab"` becomes `"aab"`; the multiplicity problem of a set does not arise.

The grouping architecture is unchanged:

```text
original string -> canonical key -> dictionary lookup -> append original string
```

Only the canonicalization method differs. Counting describes how many of each letter exist. Sorting puts all those occurrences into one standard order.

### Deriving the logarithm

Let one word have length `k`. A balanced merge-sort model explains the familiar `k log k` sorting bound. Start with eight one-element sorted pieces. Pairwise merging changes their sizes:

```text
Initial pieces:   1 1 1 1 1 1 1 1
After level 1:    2   2   2   2
After level 2:    4       4
After level 3:    8
```

Merging two already sorted pieces means repeatedly taking the smaller next element until both pieces are consumed. Each element is handled a constant number of times in that merge. At level 1, four merges each handle two elements: eight elements in total. At level 2, two merges each handle four: again eight. At level 3, one merge handles eight.

There are three levels because doubling a piece of size 1 three times reaches 8:

```text
1 * 2 * 2 * 2 = 8
2**3 = 8
log2(8) = 3
```

For `k` elements, after `L` doublings the piece size is `2**L`. Setting that equal to `k` gives `L = log2(k)`. Non-powers of two need rounding, which does not change the growth bound. Up to `O(k)` work on each of `O(log k)` levels gives `O(k log k)` work.

A logarithm counts how many times a quantity can be repeatedly reduced by its base before reaching 1, or equivalently how many multiplications of that base build the quantity. The base 2 matches the halving and doubling in this model. Big O usually omits the base because, for any fixed base `b > 1`,

```text
log_b(k) = log_2(k) / log_2(b)
```

The denominator is a constant, and Big O ignores fixed multiplicative factors. Thus `O(k log2 k)`, `O(k log10 k)`, and `O(k ln k)` describe the same asymptotic growth.

### What Python actually sorts

CPython sorting is adaptive and stable. Its [v3.14.0 implementation note](https://raw.githubusercontent.com/python/cpython/v3.14.0/Objects/listsort.txt) describes Timsort as a natural mergesort that detects ordered runs and merges them; its merge scheduling uses Powersort. A run is a region that is already ordered. Adaptivity means the implementation can exploit such regions, so some inputs require much less work than a worst-case `O(k log k)` bound suggests. Stability preserves the relative order of equal elements, though that property is not needed for our key of repeated characters.

The balanced levels above explain the cost model. They are not an exact trace of the Python sorting implementation, which does not always split a word into a perfectly balanced tree. Sorting also needs storage: `sorted(s)` materializes `k` character entries, and CPython's merges may use linear temporary space.

![Counting and sorting are alternative canonical key builders, followed by the same hash-map grouping.](https://medium-compiler.vercel.app/assets/alg-four/figure-4.svg)

*Counting and sorting are alternative canonicalizations. The balanced merge derivation above explains the logarithmic factor; this schematic compares the two choices.*

## Deriving time from the operations

Big O describes how a resource bound grows as input size grows. Constants such as a fixed 26-slot alphabet can be suppressed, but work that happens once per string cannot disappear when a string is empty.

Define:

- `N`: number of input strings.
- `k_i`: length of string `i`.
- `M = sum(k_i)`: total number of input characters.
- `K`: maximum string length, so every `k_i <= K`.
- `A`: alphabet size, equal to 26 here.
- `G`: number of anagram groups, at most `N`.

For one string of length `k_i`, the counting solution performs these operations:

```text
create count list          O(A)
scan and update counts     O(k_i)
create tuple               O(A)
hash the tuple             O(A)
lookup/insert group        expected O(1) table work
                           with up to O(A) key-comparison work
append the original string amortized O(1)
```

The tuple and equality costs are constant with respect to `N` and `K` only because `A = 26` is fixed. A tuple of growing length would not justify the same simplification. The table may perform more than one lookup on a miss, but a constant number does not change the bound.

"Amortized" describes a sequence of operations. A growing list occasionally needs a larger backing array and copies its existing references. That individual append can cost more than constant time. Spread over a sequence of appends, the aggregate growth work is linear in the number appended, yielding amortized `O(1)` per append in the usual dynamic-array model.

Summing per-word work gives `O(M + N A)` expected time under normal hash-table behavior. Building the outer result list costs `O(G)`, already covered since `G <= N`. With `A = 26`, the complete bound is:

```text
O(M + N)
```

This includes an input containing only empty strings: `M = 0`, yet creating and hashing keys and appending occurrences still takes work proportional to `N`.

Since `M <= N K`, a maximum-length formulation is `O(N(K + 1))`. When `K >= 1`, this is commonly shortened to `O(NK)`. If using average length `K_avg = M / N`, write `O(N(K_avg + 1))`; omitting the `+1` needs a positive lower-bound convention on that average. These are alternative notations for the same operations, not different algorithms.

The assumptions matter. If severe collisions force each dictionary operation to inspect up to `G` entries, the table work can approach `O(N²)` for fixed-size keys. The expected linear result is not a collision-proof worst-case claim. The standard analysis also treats bounded-size index and count operations as constant time; the published length limit keeps counts at most 100. Extending to arbitrarily huge integers would require a bit-cost model.

For the sorting solution, each word needs `O(k_i log k_i)` sorting work when `k_i >= 2`, plus linear materialization, joining, and key hashing. A form that also covers length 0 and 1 is:

```text
O(N + sum(k_i * log(k_i + 1))) expected total time
```

Using maximum length gives `O(N + N K log(K + 1))`, usually written `O(NK log K)` when `K >= 2`. With unequal word lengths, substituting the arithmetic average into a logarithmic expression is not generally an equivalent bound; the sum or maximum-length form avoids that ambiguity.

Counting is the better asymptotic choice for this fixed small alphabet. This does not prove it is faster for every short Python input: allocation costs, implementation constants, and existing ordered runs also affect elapsed time.

![Expected counting time O(M + 26N), extra keys and references, and the original grouped strings as output.](https://medium-compiler.vercel.app/assets/alg-four/figure-5.svg)

*Time and space measure the work and storage of one algorithm. Fixed per-string work remains even when there are no characters to scan.*

## What extra memory is actually allocated

The temporary counting list holds `A` entries. Only one current counting list is needed at a time. The dictionary retains one `A`-element tuple per distinct group, so its keys take `O(G A)` space. A newly built tuple that equals an existing key need not become another retained dictionary key.

Across all group lists there are exactly `N` references to input strings, including duplicates. There are `G` list objects, dictionary entries for `G` keys, and an outer return list with `G` references. Their total new container space is:

```text
O(G A + N + A)
```

For a fixed alphabet and nonempty input, this is `O(N)`. The implementation does not copy every string's character contents when appending; it stores references. The returned groups still keep those original strings reachable.

"Auxiliary space excluding the output" depends on which containers an analysis counts as output. If the returned inner and outer lists are excluded, the working dictionary, keys, and counters still use `O(G A + A)` space. If the abstract output is described as containing all string contents, its logical size is `O(M + N)`, often bounded by `O(NK + N)`. That is different from claiming this Python implementation newly allocates `M` character copies.

The sorting alternative also allocates character lists and key strings. Temporary sorting storage is `O(K)` in the worst case. Stored key strings can occupy up to `O(M)` characters across distinct groups, alongside the `N` references and dictionary containers. Fixed-size count keys avoid that length-dependent retained key storage.

## When the alphabet changes, reconsider the key

Suppose the input may contain uppercase letters, punctuation, or arbitrary Unicode code points, with anagrams defined by exact code-point multiplicities. The dictionary grouping pattern survives. The 26-slot representation and `ord(c) - ord('a')` indexing do not.

Sorting becomes a simple alternative because it does not need us to allocate one slot for every possible character:

```python
from collections import defaultdict
from typing import List

class Solution:
    def groupAnagrams(self, strs: List[str]) -> List[List[str]]:
        groups = defaultdict(list)

        for s in strs:
            key = ''.join(sorted(s))
            groups[key].append(s)

        return list(groups.values())
```

The changed implementation replaces counting and tuple construction with one sorted-string key. For example, `"A!"` and `"!A"` both produce `"!A"`, so they share a group. The sorting time and storage bounds derived above apply.

A sparse character-to-count mapping can also avoid allocating the entire alphabet, but it needs a stable, hashable representation of those character/count pairs. Sorting is often easier to explain and implement when the alphabet is unrestricted and exact character equality is sufficient.

Human text may need a further contract decision: whether case differences or different Unicode representations of visually identical text should count as equivalent. Sorting code points does not choose that policy. Any required normalization must be specified before canonicalization, because it changes which strings belong together.

## Explaining the solution in an interview

### How would you solve it?

I use a dictionary from a 26-letter frequency tuple to a list of words. For each word, I count its letters in a fresh list, convert that list to a tuple, and append the original word to the corresponding group. `defaultdict(list)` creates the group when the key is first encountered. After every word has been processed, I return the value lists.

### Why do equal counts prove that the words belong together?

Rearranging a word preserves each letter's count. Conversely, if all counts agree, both words contain exactly the same supply of every letter, so one can be rearranged into the other. The tuple preserves all 26 counts in a fixed letter order.

### What is your loop invariant?

Before processing input index `i`, the dictionary partitions exactly the occurrences in `strs[:i]` by their complete frequency tuples, each occurrence appears once, and no current or future occurrence has been added.

### How does that prove correctness?

The empty dictionary correctly represents the empty prefix. Each iteration computes the current word's complete key and appends it once to its matching group, restoring the property for the next prefix. When the loop ends, the prefix is the entire input, so every occurrence is in exactly the correct group.

### Why a list first and a tuple afterward?

I update the counts while scanning, so a mutable list is convenient. A built-in list is unhashable. The completed tuple contains only integers, so it is hashable and can serve as the dictionary key.

### What if two keys have the same hash?

The dictionary distinguishes keys using equality. A collision can affect lookup cost, but unequal tuples still identify different groups. I store the tuple itself rather than only its hash integer.

### What does `defaultdict(list)` save you from writing?

On a missing `groups[key]` subscription, it calls `list()`, stores the new empty list, and returns it. Then `append` adds the word. On a hit, it returns the existing group's list.

### What is the time complexity?

Let `M` be total characters and `N` the number of words. I scan every character once and do fixed 26-slot work per word, so expected time is `O(M + N)` under normal hash-table behavior. With maximum word length `K >= 1`, the usual shorthand is `O(NK)`. The bound assumes constant-size count operations and amortized constant-time append.

### What is the space complexity?

I retain up to one fixed-size key per group and `N` references to original strings. The new container space is `O(N)` for the fixed alphabet; it does not include new copies of all string characters.

### Can you use sorting instead?

Yes. Sorting every word gives a canonical string key, such as `"aet"` for `"eat"`, `"tea"`, and `"ate"`. With maximum length `K >= 2`, the usual worst-case sorting shorthand is `O(NK log K)`, plus the standard hash-table assumptions. It becomes attractive when the character set is not a small fixed alphabet.

During coding, the state changes can be narrated directly: "I create the dictionary once because it accumulates groups. I reset the 26 counters for each new word. I finish counting before constructing the key. I append once under that complete key. I return all group lists after the outer loop finishes."

## A master map for reconstructing the code

To rebuild the solution, start with what the output must preserve: every original occurrence, grouped by anagram equivalence. The following dependencies supply the representation and operation order.

```text
Need to group every input occurrence
    |
    v
Rearrangement preserves every letter's multiplicity
    |
    v
Lowercase a-z -> 26 fixed letter positions
    |
    v
For EACH word: fresh mutable count list
    |
    v
For EACH character: ord(c) - ord('a') -> index -> increment
    |
    v
All characters counted -> tuple(count)
    |
    v
Tuple of integers: complete canonical key, hashable
    |
    v
Dictionary uses hash for search and equality for key match
    |
    +-> HIT: get existing group list
    |
    +-> MISS: defaultdict calls list(), stores and returns []
    |
    v
Append original string exactly once
    |
    v
Outer loop exhausted -> list(groups.values())

Counting, fixed alphabet:
    expected O(M + N) time; O(N) new container space
    common time shorthand O(NK), for maximum K >= 1

Sorting alternative:
    sort characters -> canonical string -> same grouping operation
    common time shorthand O(NK log K), for maximum K >= 2
    useful when a fixed small alphabet is unavailable
```

![Zero-context master map: grouping task, frequency equivalence, counting list and tuple, dictionary HIT or MISS, invariant and cost.](https://medium-compiler.vercel.app/assets/alg-four/figure-6.svg)

*The map connects facts established in the article. Reconstruct the representation, runtime and cost from the same problem constraints.*
