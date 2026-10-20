# User-supplied Group Anagrams teaching reference

Supplied in this task on 2026-10-20. This is the user's comparison source, not an independently fetched Medium body or an approved technical edition. Preserve its teaching questions and granular examples; verify technical claims before reusing them. See [source status and applicability](medium-reference.md).

---

Group Anagrams：從 Problem 到 Python Runtime
用一道 LeetCode 題目串起 invariant、canonical key、ASCII、mutable / immutable、hashing、dict、Timsort 與 Big O
LeetCode 49 — Group Anagrams
[COVER IMAGE]
Cover concept: Group Anagrams: Problem → Invariant → Runtime → Hash Map → Complexity
 
⸻
 
LeetCode 49 看起來只是一道 Hash Map 題目。
但如果不只背 solution，而是沿著資料真正的 runtime data flow 往下追，這一道題其實會把許多平常分開學習的概念串在一起：
* anagram
* invariant
* canonical key
* ASCII / Unicode code point
* ord
* mutable list
* immutable tuple
* hashability
* tuple hashing
* dict lookup
* defaultdict(list)
* hash collision
* Python sorting
* Timsort
* log₂ K
* O(NK)
* O(NK log K)
這篇文章的目的不是再記住一份 LeetCode code。
而是建立一條可以從零重新推導答案的 reasoning chain：
Problem → Decision → Representation → Runtime → Complexity
只要這條 chain 沒有斷，就不需要把每個知識點分開死背。
 
⸻
 
1. Problem：我們到底要 group 什麼？
題目給一組 strings：
["eat", "tea", "tan", "ate", "nat", "bat"]
我們要把互為 anagram 的 strings 放在同一組。
其中一個合法答案是：
[
    ["eat", "tea", "ate"],
    ["tan", "nat"],
    ["bat"]
]
group 的順序不重要。
每個 group 內 string 的順序也不重要。
真正的第一個問題不是：
我要用什麼 Python API？
而是：
什麼 property 可以判斷兩個 strings 應該屬於同一組？
 
⸻
 
2. Decision 1：找到 invariant
看三個 strings：
eat
tea
ate
它們的 character order 不同。
但它們都有：
a: 1
e: 1
t: 1
也就是：
Anagrams have the same character frequencies.
character order 可以改變。
character frequency 不會改變。
這個不變的 property，就是這題的 invariant。
eat
tea
ate
 │
 └── same letter frequency
這一步非常重要。
因為我們不是直接解：
How do I group strings?
而是先把問題改寫成：
How do I give all equivalent strings
the same identity?
 
⸻
 
3. Decision 2：把 invariant 變成 canonical key
題目提供一個非常強的 constraint：
每個 string 只包含 lowercase English letters。
也就是只有：
a ... z
總共二十六種可能。
因此我們可以建立固定二十六個 counters：
a b c d e f ... t ... z
0 0 0 0 0 0 ... 0 ... 0
處理 "eat" 後：
a b c d e f ... t ... z
1 0 0 0 1 0 ... 1 ... 0
處理 "tea"：
結果完全一樣。
處理 "ate"：
結果仍然一樣。
因此：
eat ─┐
tea ─┼──> same 26-letter frequency
ate ─┘
這個二十六個數字組成的 representation，就可以成為 canonical key。
Canonical key 的作用是：
讓外觀不同、但邏輯上等價的資料，得到同一個標準 identity。
 
⸻
 
[FIGURE 1 — Problem & Decision Map]
Caption: From problem statement to deterministic algorithm: find the invariant, encode it as a canonical key, and let the hash map perform the grouping.
Alt text: Group Anagrams 的 decision-flow diagram。從 anagram 的共同 invariant 開始，經過 lowercase a-z constraint、二十六個 letter counters、character-to-index mapping、list 到 tuple 的 conversion，最後以 canonical key 進入 hash-map grouping。
 
⸻
 
4. 真正的 Decision Points
如果把語法細節全部拿掉，這題真正需要做的 decision 只有幾個。
Decision 1
什麼 property 定義同一組？
same character frequency
Decision 2
怎麼 representation 這個 invariant？
26 counters
因為 alphabet 固定只有 a-z。
Decision 3
怎麼把 character 映射到 counter index？
ord(c) - ord('a')
Decision 4
怎麼 group 相同 identity？
Hash Map
Decision 5
counter list 可以直接當 dictionary key 嗎？
不行。
要先轉成：
tuple
完成這五個 decision 後，後面的 algorithm 幾乎就是 deterministic runtime。
 
⸻
 
5. Runtime：從 
"eat"
開始
現在不要看 final code。
直接追蹤：
"eat"
在 runtime 裡如何一路變成某個 group 裡的 element。
首先建立：
count = [0] * 26
這個 list 是：
mutable working state
因為接下來我們要一直修改它。
 
⸻
 
6. 
ord('a') == 97
到底在做什麼？
我們需要把 character：
'e'
轉成 array index：
4
Python 的 ord() 可以取得 character 的 Unicode code point。
對 lowercase English letters：
ord('a') = 97
ord('b') = 98
ord('c') = 99
...
ord('z') = 122
這些 values 也和 ASCII 對應一致。
所以：
ord(c) - ord('a')
可以把：
a → 0
b → 1
c → 2
...
z → 25
完整映射到二十六個 counters。
例如：
'e'

ord('e') = 101

101 - 97
=
4
所以：
e → count[4]
再看：
't'

ord('t') = 116

116 - 97
=
19
所以：
t → count[19]
 
⸻
 
7. 
"eat"
的完整 Character Runtime
現在實際走一次。
Character 1：e
'e'
↓
ord('e')
↓
101
↓
101 - 97
↓
4
↓
count[4] += 1
Character 2：a
'a'
↓
ord('a')
↓
97
↓
97 - 97
↓
0
↓
count[0] += 1
Character 3：t
't'
↓
ord('t')
↓
116
↓
116 - 97
↓
19
↓
count[19] += 1
最後得到：
a b c d e ... t ... z
1 0 0 0 1 ... 1 ... 0
這就是 "eat" 的 frequency representation。
 
⸻
 
[FIGURE 2 — End-to-End Runtime Data Flow]
Caption: A string moves through several runtime representations: characters become indexes, indexes mutate a counting list, the list freezes into a tuple, and the tuple becomes the dictionary identity used for grouping.
Alt text: 輸入 "eat" 後建立二十六個元素的 mutable list，逐一讀取 e、a、t，透過 ord(c) - ord('a') 得到 index 4、0、19 並更新 counters。掃描完成後將 list 轉成 tuple，再進入 hash 與 dictionary lookup。
 
⸻
 
8. 為什麼先用 List？
因為 scanning 過程中 state 需要一直改變。
例如：
0 → 1
Python list 是：
mutable
所以非常適合：
computation state
也就是：
scan
↓
update
↓
update
↓
update
這裡 list 的 semantic role 是：
用來計算。
 
⸻
 
9. 為什麼 List 不能當 Dictionary Key？
dictionary key 必須具有 stable hash identity。
但 list 可以被修改。
例如：
x = [1, 2]
x.append(3)
representation 從：
[1, 2]
變成：
[1, 2, 3]
如果 dictionary key 在 insert 之後還能任意改變，
原本計算出的 hash 與 lookup location 就可能失去一致性。
因此普通 list：
mutable
↓
unhashable
↓
cannot be dict key
 
⸻
 
10. Freeze Boundary：List → Tuple
完成 character counting 之後，我們不再需要修改這二十六個 counters。
所以：
key = tuple(count)
可以理解成：
mutable computation
       │
       ▼
      list
       │
       │ freeze
       ▼
     tuple
       │
       ▼
immutable representation
這是一個很有用的 mental model：
list
→ calculate

tuple
→ identify
 
⸻
 
11. Tuple Immutable，不代表任何 Tuple 都能 Hash
常見簡化說法是：
Tuple is immutable, so it is hashable.
這句不夠精確。
真正的 rule 是：
tuple 本身 immutable，而且它包含的所有 elements 也必須是 hashable，整個 tuple 才能 hash。
這題的 key 是：
tuple of 26 integers
而 int 是 hashable。
因此：
tuple(count)
↓
hashable
成立。
但像概念上的：
(1, [2, 3])
裡面包含 list，
仍然不能拿來 hash。
 
⸻
 
12. Canonical Key 與 Hash 是兩件不同的事
假設 "eat" 最後得到：
(1, 0, 0, 0, 1, ..., 1, ...)
"tea" 也得到完全相同 tuple。
"ate" 也是如此。
因此：
eat ─┐
tea ─┼──> same tuple
ate ─┘
真正決定「它們屬於同一組」的是：
tuple equality
不是 hash value。
這兩層責任應該分開：
Canonical key
→ correctness

Hash
→ lookup efficiency
 
⸻
 
13. Dict 拿到 Tuple 後發生什麼？
概念上：
tuple key
   │
   ▼
hash(key)
   │
   ▼
hash value
   │
   ▼
candidate table location
   │
   ▼
inspect entry
接著可能有三種情況。
Empty
沒有 entry：
MISS
Matching key
hash candidate 對應的實際 key 也相等：
HIT
Hash collision
hash 相同，但實際 key 不相等：
collision
↓
continue lookup
所以：
same hash
≠
same key
但：
equal keys
→
same hash
dictionary 不會因為 collision 就把兩個不同 tuple 錯誤合併。
 
⸻
 
14. Dict Lookup 為什麼通常是 O(1)？
如果沒有 hash table，
可能要：
entry 1
entry 2
entry 3
...
一路比較。
但 hash table 可以：
key
↓
hash
↓
candidate location
快速縮小 lookup path。
因此 normal average-case：
dict lookup
≈
O(1)
這不是說永遠只執行一個 CPU instruction。
它代表：
當 dictionary 變大時，正常 lookup cost 不會跟 entry 數量線性增加。
 
⸻
 
15. 
defaultdict(list)
到底做了什麼？
建立：
groups = defaultdict(list)
這裡的：
list
是一個 default_factory。
當：
groups[key]
找不到 key 時，conceptual runtime 是：
lookup
↓
MISS
↓
call list()
↓
[]
↓
insert key → []
↓
return []
然後：
.append(s)
繼續執行。
所以：
groups[key].append("eat")
第一次實際上代表：
key
↓
MISS
↓
create []
↓
store []
↓
append "eat"
↓
["eat"]
 
⸻
 
16. 第二次遇到相同 Key
現在處理：
"tea"
character frequency 相同。
因此產生相同 tuple。
dictionary：
same tuple
↓
hash
↓
lookup
↓
HIT
↓
existing list
得到：
["eat"]
然後：
append("tea")
變成：
["eat", "tea"]
再處理：
"ate"
得到：
["eat", "tea", "ate"]
這就是整題最重要的 runtime invariant：
same letter frequency
↓
same tuple
↓
same dictionary key
↓
same group
 
⸻
 
[FIGURE 3 — Python Data Model & Dict Internals]
Caption: The counting list is mutable working state. After counting finishes, it freezes into a tuple of integers, producing a hashable canonical key. The dictionary uses hashing for lookup, while defaultdict(list) owns the missing-key path.
Alt text: 圖中先以 mutable list 保存二十六個 letter counters，再經 freeze boundary 轉成由 integers 組成的 immutable tuple。Tuple 作為 canonical key 經過 hashing 進入 dictionary lookup；HIT 取得既有 list，MISS 則由 defaultdict(list) 建立空 list，再 append 原始 string。
 
⸻
 
17. 現在再看核心 Code
前面所有 runtime 最後壓成：
groups[tuple(count)].append(s)
現在這一行不再只是 Python syntax。
它代表：
count
↓
finish mutable computation
↓
tuple(count)
↓
canonical identity
↓
hash
↓
dict lookup
↓
HIT / MISS
↓
existing / new list
↓
append original string
 
⸻
 
18. Sorting 其實也能建立 Canonical Key
另一個直覺方法是：
key = ''.join(sorted(s))
例如：
eat → aet
tea → aet
ate → aet
因此：
sorted representation
同樣可以當 canonical key。
高層 architecture 沒變：
input
↓
canonicalization
↓
canonical key
↓
Hash Map
↓
group
真正不同的只是：
canonicalization strategy
Counting：
count letters
Sorting：
sort characters
 
⸻
 
19. 為什麼 Sorting 是 K log K？
假設一個 string 長度是：
K
用 balanced merge-style mental model 理解 sorting：
1 1 1 1 1 1 1 1
↓
2 2 2 2
↓
4 4
↓
8
如果：
K = 8
層數是：
3
因為：
log₂ 8 = 3
一般來說：
K
→ K/2
→ K/4
→ ...
→ 1
需要大約：
log₂ K
層。
而每一層總共仍然要處理約：
K
個 elements。
所以：
K work per level
×
log K levels
得到：
O(K log K)
 
⸻
 
20. 為什麼 Big O 不寫 log₂？
因為 logarithm 的不同 base 只差 constant factor。
在 asymptotic complexity 裡：
O(K log₂ K)
O(K log₁₀ K)
O(K ln K)
都可以寫成：
O(K log K)
但在理解「一直除二需要幾層」時：
log₂ K
最直覺。
 
⸻
 
21. Python Sorting 與 Timsort
Python sorting 可以視為：
stable
+
adaptive
+
merge-based
它屬於 Timsort family。
和單純 textbook merge sort 不同，它可以利用 input 裡已存在的 ordered runs。
因此：
K × log K
是理解 general comparison-sorting complexity 的 mental model，
不是在聲稱 Python runtime 一定精確建立 log₂ K 個完全 balanced levels。
Modern CPython 的 run merge scheduling 也使用 Powersort strategy。
對 LeetCode interview 而言，真正要記的是：
sorting K characters
→
O(K log K)
不需要主動展開 Timsort internals。
 
⸻
 
[FIGURE 4 — Sorting、Timsort 與 K log K]
Caption: Sorting adds organization work: a useful complexity model is roughly K elements of work across log K levels, giving O(K log K). Counting only scans K characters once.
Alt text: 左側以八個 elements 顯示 balanced merge-style hierarchy，每層總工作量約 K，共約 log₂ K 層，所以得到 O(K log K)。右側顯示 counting 只掃描 K 個 characters 一次，因此為 O(K)。圖中特別標註這是 complexity mental model，而不是 Timsort 的精確 runtime trace。
 
⸻
 
22. 為什麼這題應優先 Counting？
題目已經給：
lowercase English letters only
也就是 alphabet size 固定為：
26
所以 canonical key 不需要 sorting。
只需要：
scan each character once
即可建立。
因此：
Counting
→ O(K)

Sorting
→ O(K log K)
在這個 constraint 下，counting 是更好的 asymptotic choice。
可以把 decision rule 壓成：
Fixed small alphabet?
        │
    ┌───┴───┐
   YES      NO
    │        │
    ▼        ▼
 counting   sorting can be simpler
這樣就不用每次解題重新猶豫。
 
⸻
 
23. 完整 Time Complexity
定義：
N
=
number of strings

K
=
average string length
現在逐步計算。
建立 26 counters
O(26)
=
O(1)
因為 26 是固定常數。
掃描 K characters
O(K)
這是主要成本。
tuple(count)
tuple 長度固定 26：
O(26)
=
O(1)
注意：
這不是說任何 tuple() 都是 O(1)。
只是這題 tuple size 永遠固定為 26。
Hash tuple
同樣處理固定 26 個 integers：
O(26)
=
O(1)
relative to N 和 K。
Dictionary lookup
average case：
O(1)
List append
amortized：
O(1)
所以一個 string：
O(1)
+
O(K)
+
O(1)
+
O(1)
+
O(1)
+
O(1)
最後：
O(K)
N 個 strings：
N × O(K)
得到：
O(NK)
 
⸻
 
24. 更精確的 Time 表達方式
如果每個 string 長度不同，
其實最精確的是：
O(total number of characters)
也就是假設全部 input characters 總數為 M：
O(M)
但 LeetCode interview 一般使用：
N strings
×
average K characters
所以：
O(NK)
更方便溝通。
 
⸻
 
25. Sorting 版本的 Complexity
Sorting 一個 string：
O(K log K)
N 個 strings：
O(NK log K)
因此：
Counting
O(NK)

Sorting
O(NK log K)
差別全部來自 canonicalization。
Hash-map grouping 本身是兩種 solution 共用的部分。
 
⸻
 
[FIGURE 5 — End-to-End Complexity Map]
Caption: The only operation that grows with string length in the counting approach is scanning K characters. Fixed-size counter creation, tuple construction, tuple hashing, average dictionary lookup, and amortized append remain constant with respect to K.
Alt text: 每個 string 建立固定二十六個 counters 為 O(1)，掃描 K 個 characters 為 O(K)，建立 tuple、hash tuple、average dictionary lookup 與 amortized append 都相對於 K 為 O(1)。所以每個 string 為 O(K)，N 個 strings 為 O(NK)；右側比較 sorting solution 的 O(NK log K)。
 
⸻
 
26. Space Complexity 為什麼常看到兩個答案？
這裡需要區分：
Auxiliary Space
與：
Output Space
Temporary count
26 counters
固定：
O(1)
Dictionary keys
每個 anagram group 最多保存一個固定 26-element tuple。
最多可能有 N 個 groups。
所以：
O(26N)
=
O(N)
Group lists
這個 Python implementation append 的主要是原本 string objects 的 references。
總共 N 個 references：
O(N)
所以從 Python container structure 的角度：
auxiliary container space
=
O(N)
但如果把 output 所代表的所有 string characters 都計入 abstract output size，
最多可以到：
O(NK)
面試時最安全的說法是：
The extra hash-map structure stores up to N fixed-size keys and N string references, so the auxiliary container space is O of N. If we count the full returned string content, the output size can be O of N times K.
 
⸻
 
27. Edge Cases 不需要額外 Branch
好的 representation 應該自然吸收 edge cases。
Empty String
""
character loop 一次都不執行。
所以：
count
=
all zeros
轉成：
(0, 0, 0, ..., 0)
自然成為合法 key。
結果：
[""]
不需要：
if s == ""
Single Character
例如：
"a"
得到：
count[0] = 1
也自然形成自己的 canonical key。
不需要 special case。
 
⸻
 
28. Final Python Implementation
現在完整 code 可以非常短：
from typing import List
from collections import defaultdict


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
如果把 code 映射回 runtime：
groups = defaultdict(list)
↓
canonical key → list of strings


for s in strs
↓
process N strings


count = [0] * 26
↓
mutable working state


for c in s
↓
scan K characters


ord(c) - ord('a')
↓
character → index


count[index] += 1
↓
update frequency


tuple(count)
↓
freeze into canonical identity


groups[key].append(s)
↓
hash lookup
↓
existing or new group
↓
append original string


groups.values()
↓
return all groups
 
⸻
 
29. English Interview Q&A
理解完整 runtime 之後，面試反而應該講得更短。
How would you solve this problem?
I use a hash map.
For each word, I count the twenty-six letters.
The letter count is the key.
Words with the same key go into the same group.
At the end, I return all groups.
 
⸻
 
What is the key idea?
Anagrams have the same letter counts.
The order can change.
The counts do not change.
 
⸻
 
Why does this work?
If two words are anagrams, they have the same letter counts.
So they get the same key.
The same key goes to the same group.
 
⸻
 
Why twenty-six counters?
The input only has lowercase English letters.
There are twenty-six possible letters.
So I use one counter for each letter.
 
⸻
 
Why use a list first?
I need to update the counts while scanning the word.
A list is mutable.
 
⸻
 
Why convert it to a tuple?
A list cannot be a dictionary key because it is mutable.
A tuple is immutable.
This tuple contains only integers, so it is hashable.
 
⸻
 
Does the hash define the group?
No.
The tuple defines the group.
The hash only helps the dictionary find the key quickly.
 
⸻
 
What about hash collisions?
The dictionary also checks key equality.
The same hash does not mean the same key.
 
⸻
 
Why 
defaultdict(list)
?
If a key is new, it creates an empty list for me.
Then I can append the word directly.
 
⸻
 
What is the time complexity?
Let N be the number of words.
Let K be the average word length.
I scan every character once.
So the total time is O of N times K.
 
⸻
 
Can you solve it with sorting?
Yes.
I can sort each word and use the sorted word as the key.
For example, eat, tea, and ate all become aet.
 
⸻
 
What is the sorting complexity?
Sorting one word takes O of K log K.
For N words, the total is O of N K log K.
 
⸻
 
Why do you prefer counting here?
The alphabet is fixed to twenty-six lowercase letters.
So I can build the key in one scan.
That gives O of N K instead of O of N K log K.
 
⸻
 
30. 最短 Interview Pack
如果只保留最少英文：
Approach
I count the twenty-six letters.
The count is the key.
Same key means same group.
I use a hash map to store the groups.
Invariant
Anagrams have the same letter counts.
Tuple
The count list is mutable.
I convert it to a tuple so it can be a dictionary key.
Complexity
I scan every character once.
Time is O of N K.
Sorting
Sorting also works.
It takes O of N K log K.
 
⸻
 
[FIGURE 6 — Zero-Context Master Map]
Caption: Group Anagrams is one continuous transformation: the problem constraint gives a fixed alphabet, the invariant becomes a twenty-six-counter representation, mutable counting state freezes into a hashable tuple, the dictionary groups equal keys, and the total runtime becomes O(NK).
Alt text: Group Anagrams 的 Zero-context master map。從 lowercase a-z constraint 推導 letter-frequency invariant 與二十六個 counters；characters 經 ord(c) - ord('a') 映射到 index，更新 mutable list，再轉成由 integers 組成的 immutable、hashable tuple。Tuple 作為 canonical key 經 hash 進入 dictionary lookup；existing key 取得原 group，missing key 由 defaultdict(list) 建立空 list。旁邊展示 "eat" 的 index 4、0、19 runtime trace，以及 sorting fallback、Timsort、log₂ K、O(NK) 與 O(NK log K)。
 
⸻
 
31. Zero-Context Master Map
如果最後只保存一張圖，它應該長這樣：
                         GROUP ANAGRAMS
                                │
                                ▼
                 Constraint: lowercase a-z
                                │
                                ▼
                     What stays the same?
                                │
                                ▼
                      LETTER FREQUENCY
                         ← invariant
                                │
                                ▼
                         26 COUNTERS
                                │
                     mutable list[26]
                                │
                                ▼
                    CHARACTER MAPPING
                                │
                     ord('a') = 97
                                │
                    ord(c) - ord('a')
                                │
                     a → 0 ... z → 25
                                │
                                ▼
                         SCAN K CHARS
                                │
                                ▼
                       FREEZE BOUNDARY
                                │
                    list → tuple(count)
                                │
                 immutable + hashable here
                                │
                                ▼
                       CANONICAL KEY
                                │
                                ▼
                         hash(tuple)
                                │
                                ▼
                         DICT LOOKUP
                                │
                  ┌─────────────┴─────────────┐
                  │                           │
                 HIT                         MISS
                  │                           │
                  ▼                           ▼
           existing group             defaultdict(list)
                  │                           │
                  │                         list()
                  │                           │
                  │                           ▼
                  │                          []
                  │                           │
                  └─────────────┬─────────────┘
                                ▼
                           append(s)
                                │
                                ▼
                              RESULT
左邊可以掛 concrete trace：
"eat"

e
↓
101 - 97
↓
4

a
↓
97 - 97
↓
0

t
↓
116 - 97
↓
19
右邊掛 sorting fallback：
eat → aet
tea → aet
ate → aet

sort K chars
↓
O(K log K)
最下面只留：
COUNTING

N strings
×
K characters once
=
O(NK)


SORTING

N strings
×
K log K
=
O(NK log K)
 
⸻
 
32. 最後真正需要記住的是什麼？
不是：
ASCII
tuple
dict
Timsort
defaultdict
Big O
log K
這些孤立名詞。
真正需要記的是它們的 causal relationship：
Problem constraint
↓
Invariant
↓
Representation
↓
Runtime behavior
↓
Complexity
對 Group Anagrams：
Need to group anagrams
↓
What stays the same?
↓
letter frequency
↓
Give it one identity
↓
26-count tuple
↓
Use the identity as a hash-map key
↓
same key
↓
same group
Python runtime：
character
↓
ord
↓
index
↓
mutable list
↓
immutable tuple
↓
hash
↓
dict
↓
defaultdict list
↓
append
Complexity：
Counting
N × K
=
O(NK)

Sorting
N × K log K
=
O(NK log K)
只要這三條線還在，
就算忘記 exact code，
也可以從零重新把 solution 推導回來。
 
⸻
 
Key Takeaways
1. 先找 invariant，不要先找 API。 Anagrams 的 invariant 是 character frequency。
2. 把 invariant 轉成 canonical key。 題目只有 lowercase a-z，所以二十六個 counters 足夠。
3. Runtime working state 與 identity state 不同。 list 用來修改；tuple 用來作為穩定 identity。
4. Hash 不負責 correctness。 tuple equality 決定是否為同一 key；hash 只幫助 dictionary 快速 lookup。
5. defaultdict(list) 消除 missing-key branch。 新 key 自動建立 empty list。
6. Counting 是 O(NK)。 每個 character 只掃一次。
7. Sorting 是 O(NK log K)。 每個 string 需要 O(K log K) 的 sorting canonicalization。
8. Constraint 應該消除 decision。 fixed small alphabet 已經告訴我們：這題主路徑應該直接收斂到 counting，而不是每次重新在 sorting 和 counting 之間猶豫。
最終要形成的能力不是：
我記得 Group Anagrams 怎麼寫。
而是：
我看到 grouping problem 時，會先找 invariant，再把 invariant 轉成 canonical key。
這個 pattern 才是這題真正可以帶走、並在其他問題重複使用的部分。

