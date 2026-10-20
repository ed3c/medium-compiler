# Author delivery record

Task: independent COMPLETE_MEDIUM_ARTICLE for LeetCode 207. Only task.json, the four listed instruction snapshots, the snapshot detector, primary web sources, and this assigned output directory were read. No reference article, repository article, other writer output or observer material was read. No agents were launched; no Git, repository, provider or publication write occurred.

## Construction and English approval before translation

Causal spine: all courses must finish; prerequisite pairs impose directed obligations; a count retains how many obligations remain while an outgoing list locates those affected by a completion; zero-count courses can be legally processed; decrementing exactly outgoing destinations preserves the meaning of counts; an empty frontier with an unfinished course implies a finite backward prerequisite chain and hence a cycle; completed-course count therefore decides the Boolean result. The representation was selected from the two-prerequisite witness, not copied from a reference article.

Source contract checked from https://leetcode.com/problems/course-schedule/: identifiers 0..numCourses-1; pair [a,b] means b precedes a; n 1..2000; pair count 0..5000; pairs unique; no exclusion of self-loops. Only statement text read, not editorials/community solutions. Input preservation is an implementation property, not an attributed mutation rule.

Python primary sources read:

- https://docs.python.org/3.14/library/collections.html#collections.deque: construction, unbounded default, endpoint methods, None return for append, bounded deque discard behavior and approximate endpoint cost.
- https://docs.python.org/3.14/tutorial/datastructures.html#using-lists-as-queues: list front removal moves later elements; deque endpoint use.
- https://docs.python.org/3.14/library/stdtypes.html#common-sequence-operations (redirects to builtins/stdtypes): sequence reference repetition, mutable operations and immutable integers.
- https://github.com/python/cpython/blob/v3.14.0/Objects/listobject.c, list_resize, lines approximately 98-126 and pop implementation: proportional over-allocation for single-item append, padding/rounding, reference copying/movement.
- https://github.com/python/cpython/blob/v3.14.0/Modules/_collectionsmodule.c, block representation comments approximately lines 65-118: fixed-size linked blocks, endpoint positions, no shifting other entries on endpoint operations.

Live 3.14 documentation identified itself as 3.14.8. Internal implementation claims are explicitly pinned to v3.14.0 in the article. Runtime uses the actual host version separately recorded in runtime.json. Sources establish language/implementation facts; graph proofs, witnesses and operation sums are author derivations.

The first complete English draft was saved as article.first.en.md before editing. Snapshot detect.py ran on it and wrote sloptrim.first.json (exit 0). It reported clean, score 7, with unlock vocabulary and bold question spans. The final removes one redundant opening sentence, changes unlock/release wording in the flagged spans, and removes bold from interview questions. No code, numerical conditions, examples or complexity claims changed. prepare.py preserves the exact transformation. The detector then ran on article.en.md and wrote sloptrim.final.json. No character contamination was reported.

The reader-article supplement was actually applied as an author sentence-by-sentence pass: the removed opening sentence narrated the intended explanation without adding an actor, condition or mechanism. Worked-state transitions, append cost premises, the self-loop counterexample and recurring interview explanations were retained because they serve reconstruction or recall. No semantic meaning was cut to lower a detector score.

English semantic approval occurred after the final detector run and actual runtime verification, and BEFORE creating any translation. Checked contract, arrow orientation, two-to-one delay, queue side effects, distinct-list construction, exact loop checkpoint, success/failure proof, all methods' operation/storage derivations, source qualifications and input preservation. Approved complete edition: article.en.md. This approval is the author's review, not an independent Reader result.

## Final-body reconstruction with exact supporting passages

These reconstructions use the final English body rather than an outline. Each quotation below is exact article text. A supporting citation alone was not treated as an explanation.

### Main algorithm, representation and proof

Condition and state: “A count of two means that two distinct obligations remain; knowing only whether the course has any prerequisites would lose the information needed after the first completion.” The body derives outgoing adjacency from avoiding rediscovery after a completion, then says “Store a in that list for each pair [a, b]” with code formatting in the original. Storage direction and counter direction agree with the complete code.

Checkpoint: “At that point, finished counts distinct completed courses; every unfinished course's count equals its number of unfinished prerequisites; and the queue contains every available unfinished course exactly once.” (Identifiers carry Markdown code formatting in the body.) This is checked only after the previous dependent list finishes, so a partially updated count vector is not falsely treated as a checkpoint.

Progress premise: “Counts never increase during this phase. A positive count crosses zero only once, and initially zero courses enter during initialization, so each course enters the queue at most once.” Together with one removal per entry, this limits distinct completions to V. Maintenance is supported by “Its outgoing edges describe exactly the obligations that this completion satisfies.” Initial meaning comes from counting every input pair. The finite backward-following paragraph closes failure: following unfinished prerequisites repeats an identifier in a finite set. This is a separate logical equivalence, not a restatement of the loop invariant.

Fresh reconstruction using body premises: n=4, pairs [[2,0],[2,1],[3,2]]. after=[[2],[2],[3],[]], remaining=[0,0,2,1], ready=[0,1]. Remove 0: count[2]=1 and no release; remove 1: count[2]=0, queue=[2]; remove 2: count[3]=0, queue=[3]; remove 3: finished=4, True. The two-to-one delay and zero crossing follow from the stated obligation meaning alone. For n=2 and [[0,0]], initial queue=[1]; its removal leaves finished=1 and an unfinished self-dependency, hence False.

### Elementary cost boundary

Exact premise: “Reading or writing one list slot, comparing bounded integers, incrementing a counter, and moving or retaining one object reference are elementary constant-size operations.” Bounds on identifiers and counts immediately follow in the body. Allocation/copy of k slots is separately proportional to k. No growing container operation is declared elementary solely to obtain the desired bound.

Queue mechanism: “An endpoint operation changes an endpoint position and, at a block boundary, a fixed-size block connection; it does not shift all queued references.” With fixed-size block allocation declared bounded, per-endpoint work does not depend on queued length. This reaches an explicit elementary allocation assumption, qualified to CPython v3.14.0 rather than inferred from API syntax.

List append dependency: “After growing a sufficiently large list of size m, proportional spare room allows at least a fixed fraction of m further single-item appends before another growth.” The body then gives the backward-size sum and subtraction: “Their copying work is bounded by C + rC + r²C + ... = C/(1-r) for some fixed r < 1.” This follows from multiplicative single-item growth, with small sizes bounded separately. It states why final C is proportional to final length and adds ordinary writes. Hence d appends cost O(d), without claiming each append individually constant. The actual lists are append-only, so the precondition applies.

Frequency sum: “If course b has d_b dependents, its append sequence costs O(d_b); summing d_b across all courses gives exactly E.” The body explicitly adds O(V) small-list overhead, so many empty lists do not disappear from accounting. Construction O(V+E), initialization O(V), at most V queue additions/removals, and summed adjacency traversals <=E produce O(V+E). There is no unexplained multiplication of nested loop limits. This reconstruction uses the explanatory paragraphs, not memorized graph-algorithm folklore.

Live space: “The inner lists retain E references plus spare capacity proportional to V + E, by the same growth policy.” Outer slots/headers, V counts, queue at most V entries and scalar locals are counted. Exact transient premise: “A resize can temporarily keep old and new storage alive, but both have size proportional to the list being grown; this leaves the peak bound O(V + E).” Input is excluded, output Boolean constant. Internal allocator/address sizes are fixed-unit model assumptions, not runtime measurements.

### List-front-removal comparison

Exact body argument: “With V initially available courses, draining a list through pop(0) moves (V - 1) + (V - 2) + ... + 1 references.” The body explains why references shift, then pairs terms to V(V-1)/2. Thus this boundary comparison has a changing quantity and sum, not an unsupported claim that lists are slow. No claim is made that every use of list has this behavior.

### Repeated-scan alternative

Exact state/update: “Keep done[V] Booleans. In each round, allocate a fresh blocked[V] array of false values.” Then every pair with both endpoints unfinished marks its destination; completion occurs after this scan. “Group members cannot require one another, since any such edge would have marked its destination blocked.” Thus a round does not incorrectly allow a prerequisite completed midway through the scan to alter the meaning of flags. Every successful round removes >=1 course; <=V successful plus <=1 failed round follows. Exact count premise: “Initializing flags and inspecting courses costs O(V) per round; checking every pair costs O(E).” Multiplication gives O(V(V+E)); a chain makes V rounds necessary. Each of the retained done/blocked/optional group buffers has <=V entries, with old rounds released, giving O(V) peak auxiliary; input E stays live but excluded; result constant. This method is not exempted because it lacks article code. It prefers less extra edge storage at the price of repeated scans.

### Return-order adaptation

Exact change: “Start an empty order list and append course immediately after each removal. Return order if its length equals V, otherwise return [].” Existing legality proof applies because every recorded course was available at removal; FIFO imposes no sorted-order promise. Exact cost bridge: “This adaptation adds at most V single-item appends to one growing list. The append-only argument still applies, so the added work is O(V) and the whole algorithm remains O(V + E).” Frequencies of old graph and queue operations are unchanged. Adjacency, counts and queue remain live, so auxiliary excluding returned output stays O(V+E); success output V references, failure partial list <=V transient auxiliary and empty output constant. This explicitly reuses the preserved append-only premise instead of merely reusing the formula.

### Wrong shortcut

The actual incorrect rule is True for any nonempty initial queue. n=2, [[0,0]] yields initial available course 1, then an impossible self-loop remains; extracted final code returns False while the wrong rule actually returns True. Three-course two-node-cycle case supports the disconnected-component explanation, with the claimed minimum carefully conditional on having that two-node cycle plus separate available course. No unqualified minimality claim was made.

## Runtime controls

verify.py extracts the final English's single complete Python block, saves extracted_solution.py, and executes that code. Literal cases, exhaustive all directed graphs including self-loops for n=1..3, random n=4..6 checked against complete permutation enumeration, and legal maximum-size controls ran successfully. The independent oracle enumerates schedules and tests positions of prerequisites; it does not reuse indegree logic. Input equality is checked after every call. sys.settrace observes actual extracted-function locals at each while checkpoint; ObservedDeque records actual removals and checks uniqueness, exact unfinished counts, queue membership and adjacency edge count. Container controls execute append's None return, FIFO removals crossing deque blocks, shared-list aliasing versus independent comprehension lists, and growing-list size observations. Front-removal shift sum is checked arithmetically; asymptotic conclusions come from body reasoning and source structure, not timing data.

All command outputs and stderr are retained. No runtime verification command or solution test case failed. A later bilingual editorial-control failure and repair are recorded below; there was no hidden repair or discarded failing run. runtime.json gives host version and exact counts. Runtime controls do not prove an asymptotic theorem or learner comprehension.

## Remaining delivery scope

No figure asset was necessary: ordered state text and a concrete adjacency vector make all dependencies readable without a separate diagram. No placeholder figure or unrendered image is included. Section order is contract, representation, program movie, code/proof, costs, alternative/adaptation, interview/master map. Complete code and both approved narratives are supplied directly; no formatter, Stage 0–7 assembly, website rendering or publication was requested/executed in this isolated task. Independent Reader review and learner achievement are unobserved.

CONTENT_REVIEWED: author complete English review recorded above. SLOPTRIM_RUN: actual snapshot detector plus manual reader supplement. RUNTIME_TESTED: yes. CLI_VALIDATED: NOT_RUN. INDEPENDENT_READER: NOT_RUN. IMAGES_RENDERED: NOT_RUN. PUBLISHED: NOT_RUN. Translation review will be appended after the complete first translation exists.

## Preserved editorial-control failure and repair

The first finish.py command failed with AssertionError: inline_code_sequence_identical=False, while all fenced blocks, links, heading counts and English interview text matched. Exact failed program, JSON and stderr are preserved as finish.failed.py, bilingual-controls.failed.json and bilingual.failed.stderr.txt. SequenceMatcher inspection showed Chinese clause reordering moved [a,b], while and V; Chinese also repeats the already defined m once more when explaining proportional spare room. Counter inspection showed no missing English inline token and only that one extra m. This is a test-design error: token order does not express bilingual semantic equivalence. No article correction was required. The repaired control checks identical inline-token vocabulary, retaining exact fenced-block and URL equality; author semantic review checks the reordered clauses, quantities and conditions. The repaired control ran successfully below. This was one failed control command, followed by diagnosis and one repair, not a failed solution case.

## Translation review and immutable support excerpts

The complete first translation was preserved as article.first.zh-TW.md. Author review found no required correction; article.zh-TW.md therefore retains its exact bytes. Full sections were read against English in order. Checked pair orientation, legal self-loop, isolated courses, None return, no bounded deque, all movie vectors and completion totals, zero crossing, checkpoint timing, finite-cycle proof, fixed-scalar assumptions, geometric append-only argument, per-list sum, old/new resize overlap, repeated-scan rounds and buffers, returned-order auxiliary/output split, and conditional minimality. English interview practice is deliberately identical. These are author checks, not independent review or learner evidence.

bilingual-controls.json records actual exact equality controls for all fenced blocks, inline-code token coverage, source URL sequence, heading count and interview English. TRANSLATION_REVIEWED: yes. No revised English edition was translated after approval, and no later English repair was made.

The following excerpts are copied mechanically from the actual final English body, preserving Markdown identifiers and complete causal paragraphs. They support the reconstructions above; each inference is explained there and in these body passages, rather than inferred merely from quotation presence.

```text
The checkpoint is just before each evaluation of `while ready`, after all updates for the preceding completion. At that point, `finished` counts distinct completed courses; every unfinished course's count equals its number of unfinished prerequisites; and the queue contains every available unfinished course exactly once. Completed courses are outside the queue. The queue's internal order is an implementation choice, separate from these conditions.
```

```text
Whenever a course is removed from `ready`, mark one more completion in `finished`. Visit only its dependents in `after[course]`. Each loses exactly one outstanding obligation, so subtract one from its count. Append a dependent precisely when its count becomes zero. Counts never increase during this phase. A positive count crosses zero only once, and initially zero courses enter during initialization, so each course enters the queue at most once. No additional visited set is needed.
```

```text
Let `V = numCourses` and `E = len(prerequisites)`. Big O describes an upper bound on growth, ignoring fixed multipliers; `O(V + E)` means work grows no faster than a constant times the number of courses plus pairs, under the following model. Reading or writing one list slot, comparing bounded integers, incrementing a counter, and moving or retaining one object reference are elementary constant-size operations. Course identifiers fit within 0 to 1999 and counts within 0 to 5000; treating these scalars as bounded units is appropriate for this contract. This is an operation-count model, not a statement that all Python instructions take identical physical time. Allocating or copying `k` slots costs proportional to `k`.
```

```text
The queue choice affects this count. A Python list stores references in consecutive indexed slots. Removing its first item must shift the later references left so indexing still starts at zero. With `V` initially available courses, draining a list through `pop(0)` moves `(V - 1) + (V - 2) + ... + 1` references. Pairing the terms gives `V(V - 1)/2`, quadratic growth even with no prerequisite edges. The [Python tutorial](https://docs.python.org/3.14/tutorial/datastructures.html#using-lists-as-queues) describes the shifting cost.
```

```text
CPython v3.14.0's [deque implementation](https://github.com/python/cpython/blob/v3.14.0/Modules/_collectionsmodule.c) uses fixed-length blocks joined by links. An endpoint operation changes an endpoint position and, at a block boundary, a fixed-size block connection; it does not shift all queued references. With fixed-size block allocation treated as bounded work, each queue endpoint operation has constant cost in this model, matching the documented approximately `O(1)` behavior. Queue size can grow, but the work of a single endpoint update does not grow with it.
```

```text
Adjacency lists use `list.append`, which needs a different argument. A list sometimes runs out of allocated slots. CPython v3.14.0's [list resize policy](https://github.com/python/cpython/blob/v3.14.0/Objects/listobject.c) reserves spare capacity on single-item growth, roughly one eighth of the requested size beyond the items, with small rounding and padding. A growth may copy the old references, so one append is not always constant work.
```

```text
Here is why a whole append-only sequence is still linear. After growing a sufficiently large list of size `m`, proportional spare room allows at least a fixed fraction of `m` further single-item appends before another growth. Charge the cost proportional to `m` of that growth across those following appends; each receives only a constant charge. Equivalently, look backward from final capacity `C`: successive earlier growth sizes shrink by a fixed factor below one, apart from small sizes. Their copying work is bounded by `C + rC + r²C + ... = C/(1-r)` for some fixed `r < 1`. To see the bound, multiplying the sum by `r` leaves the original sum minus its first term; subtraction gives `(1-r)S = C`. Small initial capacities add fixed work. Final capacity is proportional to the final length, so `d` single-item appends, including their ordinary writes, take `O(d)` total work. This aggregate guarantee is called amortized constant time per append. It applies here because each adjacency list only grows by one appended item at a time; no alternating deletion or bulk update is being smuggled into the argument.
```

```text
Building the `V` independent lists and `V` counts costs `O(V)`. Reading `E` pairs does `E` counter updates and `E` appends. If course `b` has `d_b` dependents, its append sequence costs `O(d_b)`; summing `d_b` across all courses gives exactly `E`. Small-list overhead contributes at most another `O(V)`. Building the representation therefore costs `O(V + E)`.
```

```text
The readiness scan checks `V` slots and enqueues at most `V` courses. During processing, each course is enqueued and removed at most once. Each edge appears in exactly one dependent list, and that list is visited at most once. Hence all executions of the inner loop total at most `E`, even though the code nests that loop inside a `while`. Setup, queue operations and edge updates sum to worst-case `O(V + E)` time, with list construction analyzed over its append sequences. A cycle may stop processing early, but cannot avoid the initial pair-reading work.
```

```text
For auxiliary space, the outer adjacency list and its inner-list headers use `O(V)` slots or fixed-size records. The inner lists retain `E` references plus spare capacity proportional to `V + E`, by the same growth policy. Counts use `V` scalar slots, and the queue holds at most `V` entries plus fixed-size block overhead proportional to that capacity. Scalar loop variables need constant space. A resize can temporarily keep old and new storage alive, but both have size proportional to the list being grown; this leaves the peak bound `O(V + E)`. The existing input is excluded from auxiliary space, and the returned Boolean is `O(1)` output space. No recursion stack is used.
```

```text
If storing another `E` references is unacceptable but the original pair list can be scanned repeatedly, there is a slower alternative. Keep `done[V]` Booleans. In each round, allocate a fresh `blocked[V]` array of false values. Scan every pair `[a, b]`; if both `a` and `b` are unfinished, set `blocked[a]` to true. Then identify all unfinished, unblocked courses and mark that whole group done only after the scan has finished. These are exactly the courses with no unfinished prerequisite at the start of that round. Stop successfully when all are done, or unsuccessfully when a round adds none.
```

```text
The same legality and finite-cycle argument applies to these groups. Group members cannot require one another, since any such edge would have marked its destination blocked. Each successful round completes at least one new course, so there are at most `V` successful rounds and at most one final failed round. Initializing flags and inspecting courses costs `O(V)` per round; checking every pair costs `O(E)`. The resulting bound is `O(V(V + E))`. A length-`V` prerequisite chain releases only one course per round, showing why the repeated work can persist as size grows. `done`, `blocked` and an optional group buffer each hold at most `V` entries, so peak auxiliary storage is `O(V)`; old round buffers are released before the next round. The Boolean output stays `O(1)`. The input's `E` pairs remain live and are excluded under the same convention. Prefer this trade-off only when the extra adjacency storage matters more than repeated scans.
```

```text
A different requirement changes what the main solution must retain: return one valid course order, or `[]` if impossible. Start an empty `order` list and append `course` immediately after each removal. Return `order` if its length equals `V`, otherwise return `[]`. Each retained entry records a legal completion, so the earlier proof establishes the returned ordering. No smallest-first guarantee follows from FIFO; for the movie, 4 appears before 1.
```

```text
This adaptation adds at most `V` single-item appends to one growing list. The append-only argument still applies, so the added work is `O(V)` and the whole algorithm remains `O(V + E)`. The adjacency representation, counts and queue remain, so auxiliary storage excluding a successful returned order stays `O(V + E)`. Successful output contains exactly `V` references and takes `O(V)` output space. On failure, the partial order is temporary auxiliary storage of at most `V` entries and the returned empty list has constant size. Keeping an order changes storage accounting, not the cost of visiting each edge.
```

```text
A tempting wrong return is `True` whenever the initial queue is nonempty. The three-course rejection above refutes it. It is smallest by number of courses if a two-course cycle and a separate available course are required: two course identifiers form the cycle and a third supplies the misleading start. Without that requirement, the smaller `numCourses = 2, prerequisites = [[0, 0]]` already refutes the shortcut: course 1 is available while course 0 waits for itself.
```
