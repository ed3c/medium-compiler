# Group Anagrams：從字母計數到 Python runtime

推導 canonical key、`ord`、mutable list、hashable tuple、`defaultdict(list)`，以及 counting 與 sorting 的成本差異。

![Group Anagrams：題目、frequency equivalence、canonical key、runtime、proof 與成本。](https://medium-compiler.vercel.app/assets/alg-four/cover.svg)

*從題目限制出發，沿著同一條因果脈絡理解分組與其 expected `O(M + N)` 成本。*

字串 `"eat"`、`"tea"` 與 `"ate"` 從左到右讀起來不同，但各自都包含一個 `a`、一個 `e` 和一個 `t`。只要給這三個字串相同的 key，就能把分組問題轉成 dictionary lookup。

這個 key 必須保留足夠資訊，才能判斷兩個字串是否為 anagrams；它在 Python 中的表示方式也必須能作為 dictionary key。這兩個要求導出演算法：用 list 計算字母次數，把完成的計數轉成 tuple，再把原始字串加入該 tuple 對應的群組。

## 正確答案必須保留什麼

在 [LeetCode 49, Group Anagrams](https://leetcode.com/problems/group-anagrams/) 中，輸入是一個由字串組成的 list。Anagrams 使用相同字母，且每個字母的出現次數相同，只是排列順序可能不同。例如：

```python
strs = ["eat", "tea", "tan", "ate", "nat", "bat"]
```

其中一個合法結果是：

```python
[
    ["eat", "tea", "ate"],
    ["tan", "nat"],
    ["bat"],
]
```

群組之間的順序，以及群組內部的順序，都不影響答案是否被接受。每一筆輸入都必須在輸出中恰好出現一次：輸入有兩筆 `"eat"`，輸出就必須保留兩筆。題目要求的是分組，移除重複值會改變任務。

題目公布的限制是 1 到 10,000 個字串，每個字串長度介於 0 到 100，且只使用 lowercase English letters。因此 empty string 是合法案例，不是無效輸入。本實作會建立新的 containers，不改動輸入 list 或其中的字串。

一個直接的 baseline 是保留一個群組 list，將每個新字串逐一與各群組的代表字串比較，直到找到 anagram。若許多字串各屬不同群組，第一個字串沒有既有代表要比，第二個要比一個，第三個要比兩個，依此類推。光是比較的次數就可能達到 `N(N - 1) / 2`，還沒計入每次比較所檢查的字元。

這裡反覆付出的成本，是在各群組中搜尋正確的歸屬。只要先為每個群組建立可靠的 key，就能用 dictionary 避免這種逐組搜尋。

## 找出重新排列後不變的性質

對 `"eat"`、`"tea"` 與 `"ate"` 而言，字母位置會改變，但 letter frequency 不會：

```text
             a   e   t
"eat"        1   1   1
"tea"        1   1   1
"ate"        1   1   1
```

這正是需要的 equivalence property：兩個 lowercase 字串互為 anagrams，若且唯若它們對每個字母的計數都相同。

正向推論成立，因為重新排列字母不會增加或移除任何一次出現。反向推論同樣重要：若所有計數都一致，依序取出第二個字串各位置所需的字母，第一個字串恰好擁有每種字母所需的數量，因此能填滿所有位置。計數相同不只是必要條件，也是充分條件。

*canonical key* 是同一個 equivalence class 中所有成員共用的標準表示方式。這裡的一個 class 就是一個 anagram 群組。我們需要：

```text
anagrams          -> equal keys
not anagrams      -> unequal keys
```

只記錄字母是否存在還不夠。`"ab"` 與 `"aab"` 都包含 `a`、`b`，但後者多了一個 `a`。set 會丟掉這種 multiplicity，計數則會保留它。

因為 alphabet 固定為 `a` 到 `z`，所以可以依固定順序保留 26 個位置：

```text
position:  0  1  2  3  4  5  ...  19  ...  25
letter:    a  b  c  d  e  f  ...   t  ...   z
```

位置順序本身就是 representation 的一部分。位置 0 的值是 `1`，代表一個 `a`；同樣的值放在位置 1，則代表一個 `b`。我們必須同時保留計數，以及每個計數所屬的字母。

對 `"eat"` 而言，完成的 representation 在位置 0、4、19 都是 1，其餘位置都是 0。計算 `"tea"` 也會得到相同 representation，不需要重新排列任何一個原始字串。

現在，各項設計決策都有明確理由：

- 保留 frequencies，因為重新排列會保留 multiplicity。
- 使用 26 個 counters，因為輸入 alphabet 恰好只有 26 種字母。
- 用 dictionary 將完成的 key 對應到原始字串 list，因為輸出需要完整群組。
- Counting 過程使用 mutable list，之後轉成 hashable tuple 供 dictionary lookup。

![Decision map：lowercase a-z 允許使用 26 個 counters；相等的 count tuples 識別 anagram 群組。](https://medium-compiler.vercel.app/assets/alg-four/figure-1.svg)

*固定的字母位置，讓 canonical key 能保留 anagram 的 equivalence property。*

## 把字元轉成 counter 位置

每個字串都先從這個狀態開始：

```python
count = [0] * 26
```

`count[0]` 保存目前看過的 `a` 的數量，`count[1]` 保存 `b` 的數量，依此類推。list 是 *mutable*：對其中一個位置指定新值，就會改變這個 list。

下一步需要把目前字元轉成 0 到 25 之間的數字。Python 的 [`ord`](https://docs.python.org/3.14/library/functions.html#ord) 會回傳單一字元字串的 Unicode code point。對這些字母而言，數值也與 ASCII 一致：

```text
ord('a') = 97
ord('b') = 98
ord('c') = 99
...
ord('z') = 122
```

這些數值連續排列。減去 `a` 的數值，就把範圍從 97–122 平移成 0–25：

```python
index = ord(c) - ord('a')
count[index] += 1
```

`ord` 本身不會直接回傳字母在 alphabet 中的位置。在 lowercase `a`–`z` 的限制下，是減法運算把 code point 轉成了位置。

處理 `"eat"` 時，working state 會如下變化。下方每次列出非零項目時，未列出的 counter 都仍然是零。

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

`count[index] += 1` 會讀取一個 slot 中的 integer，加上一，再把得到的 integer 指定回該 slot。發生改變的是 list；integer object 本身沒有被原地修改。

`[0] * 26` 一開始雖然重複了指向同一 integer 值的 references，在這裡仍然安全。Integers 是 immutable，更新其中一個 slot 時，替換的是該 slot 的 reference。這與重複 mutable object 不同：例如 `[[]] * 26` 的所有位置都會指向同一個 inner list。

這個迴圈內有一個精確的 checkpoint property：

> 處理 `s` 的字元位置 `j` 之前，對每個從 0 到 25 的 `p`，`count[p]` 都等於 alphabet 位置 `p` 的字母在 `s[:j]` 中出現的次數。

當 `j = 0`，已處理的 prefix 是空的，因此全零計數正確。每處理一個字元，恰好只遞增對應的 counter。字元迴圈結束時，prefix 就是整個字串，26 個計數也全部完成。

lowercase 條件保證每個 index 都有效。不能假設所有 Unicode 字母都落在同一段連續範圍，就直接把這段程式推廣出去。即使是 uppercase `A`，也會得到 `65 - 97 = -32`，超出這個 list 合法的負 index 範圍。換了 alphabet，就需要不同的 mapping。

![Character trace：eat 映射到 indexes 4、0、19，完成的計數形成 tuple，相等 keys 共享群組。](https://medium-compiler.vercel.app/assets/alg-four/figure-2.svg)

*一個字串依序經過字元、counters，再成為 tuple key。首次查找這個相等 key 時是 MISS；之後的相等 key 則沿用既有群組。*

## 為什麼 counting list 要轉成 tuple

list 已經完成 working state 的任務。dictionary 需要一個 key，讓它在儲存期間的 hashing 與 equality 行為持續有效。

Python 將具有 lifetime-stable hash、且支援比較的 object 稱為 *hashable*；相等的 objects 必須具有相同 hash。內建 list 是 unhashable；tuple 則只有在所有 elements 都是 hashable 時才是 hashable。這些規則記載於 [Python 的 hashable 定義](https://docs.python.org/3.14/glossary.html#term-hashable)。

改變 key 的值為何會有問題？假設 dictionary 依 list 內容決定搜尋位置，之後 list 內容卻變了。此時依修改後的內容查找，可能會走向與原先儲存 entry 時不同的搜尋路徑。Python 對一般 list 的處理方式，是直接拒絕它作為 key：

```python
count = [1, 0, 0]
# {count: []} would raise TypeError: unhashable type: 'list'
```

這是型別本身的規則，即使某個程式承諾永遠不改動那個 list，也不例外。Mutability 也不普遍等同於 unhashability：custom objects 可以定義不同的 identity 規則。對這個解法而言，關鍵事實是內建 list 不能作為 key，而由 integers 組成的 tuple 可以。

完成計數後，建立 key：

```python
key = tuple(count)
```

`"eat"` 的完整 tuple 是：

```python
(1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0,
 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0)
```

`tuple(count)` 會用目前的 26 個值建立新的 container。它不會把原 list 原地變成 tuple，也不會讓原 list 變成 immutable。之後即使修改 `count[0]`，`key` 也不會改變。將這裡稱為 *freeze boundary*，描述的是拿來作為 key 的 snapshot。

若某個 element 是 unhashable，tuple 的位置固定仍然不夠。例如 `(1, [2, 3])` 包含 list，所以無法 hash。我們的 key 只包含 integers，因此符合這項限制。

兩者的角色不同：list 保存仍在變動的計數，tuple 記錄已完成的計數以識別群組。下一個字串會取得新的 counting list，dictionary 則保留識別既有群組所需的 tuple。

## 相等的 keys、hashes 與 dictionary lookup

dictionary 也稱為 hash map，儲存 key 到 value 的對應關係。這裡要建立的對應是：

```text
26-count tuple -> list of original input strings
```

`"tea"` 的 tuple 是新建的 object，但它的 26 個值與 `"eat"` 的 tuple 相等。Dictionary keys 不必是同一個 object，也能指向同一個 entry。tuple 的值相等，就代表相同的 key。

Hashing 協助找出該 entry。hash function 將 key 的資訊組合成一個 integer。對 tuple 而言，各 elements 的 hash 都參與這個計算；對 sequence 做 hashing，一般不能不論長度都當成沒有成本。這裡的長度始終是 26。

可以用下面的概念流程理解 lookup：

```text
key -> hash -> candidate table position
                  |
                  +-> matching key: return its value
                  |
                  +-> different key: keep searching
                  |
                  +-> absence established: key is missing
```

[Python 的 design FAQ](https://docs.python.org/3.14/faq/design.html#how-are-dictionaries-implemented-in-cpython) 說明，CPython dictionary 採用可調整大小的 hash table。圖中省略了實際 layout 與 probing 規則，不代表每次 lookup 都只存取一次記憶體。

兩個不相等的 keys 可以有相同 hash，這稱為 *hash collision*。即使完整 hash 值不同，它們一開始也可能競爭同一個 table position。不論哪種情況，dictionary 都會繼續解析搜尋，而不是直接宣告 keys 相等。當 hash 顯示可能相符時，equality 會區分真正的 keys。

因此，anagrams 的推論鏈是：

```text
same letter frequencies -> equal tuples -> same dictionary entry
```

若把 tuple 換成 `hash(tuple(count))`，並只用這個值作為 key，就會出錯。當不相等的 frequency tuples 發生 hash collision 時，這樣會丟失區分它們所需的資訊。

在 hash 分布良好、table size 維持適當大小的一般假設下，average lookup 相對於 dictionary entry 數量需要 constant time。`O(1)` 描述的是這種成長關係，不是 CPU instruction 的實際數量。嚴重的 collisions 可能需要搜尋許多 entries，因此這個界線不是無條件的 worst-case 保證。

## `defaultdict(list)` 遇到 MISS 時做了什麼

用以下方式建立 mapping：

```python
from collections import defaultdict

groups = defaultdict(list)
```

`list` 是一個 callable，儲存在 dictionary 的 `default_factory` 中。傳入 `list` 是交出 factory 本身；傳入 `list()` 則會立刻呼叫它，交出去的是一個空 list。

Subscription `groups[key]` 使用 `__getitem__`；若 key 不存在，這個 method 就會呼叫 `__missing__`。使用這個 factory，Python 會不帶 arguments 呼叫 `list()`，把產生的空 list 存入該 missing key，然後回傳這個 list。HIT 則回傳已儲存的 list。[defaultdict 文件](https://docs.python.org/3.14/library/collections.html#collections.defaultdict) 規定了這個行為，也指出 `get()` 不會觸發 factory。

因此，分組操作可以寫成：

```python
groups[key].append(s)
```

遇到 MISS 時，subscription 會先建立並回傳群組，之後才執行 `append`。遇到 HIT 時，`append` 會擴充既有群組。每個 missing key 都會得到分別建立的 list。

若使用一般 dictionary，對應的 missing-key 邏輯會是：

```python
if key not in groups:
    groups[key] = []
groups[key].append(s)
```

這段程式呈現相同的分組行為，但不代表這兩種寫法在內部執行相同次數的 lookup。

`append` 的 return value 是 `None`。它有用的效果是修改群組 list，因此不能把 return value 指定回 `groups[key]`。Python 在 [Built-in Types](https://docs.python.org/3.14/library/stdtypes.html) 中記載了這個 collection-mutating methods 的慣例。

![Python data model：mutable counting list、integer tuple snapshot、hash candidates 與 key equality。](https://medium-compiler.vercel.app/assets/alg-four/figure-3.svg)

*完成的 tuple 識別群組。Hashing 定位候選項目，equality 決定 key 是否相符。建立 tuple snapshot 後，原 list 仍然是 mutable。*

## Program movie：從第一個字元到回傳群組

在原始範例中加入一個 empty string 與一筆重複輸入：

```python
["eat", "tea", "tan", "ate", "nat", "bat", "", "eat"]
```

為了精簡 state 展示，將完成的 frequency keys 分別稱為 `E`、`T`、`B` 與 `Z`：

```text
E: a:1, e:1, t:1; all other counts 0
T: a:1, n:1, t:1; all other counts 0
B: a:1, b:1, t:1; all other counts 0
Z: all 26 counts 0
```

這些字母只是展示標籤，不是程式真正使用的 dictionary keys。實際 keys 仍然是由 26 個 integers 組成的 tuples。

一開始 `groups` 是空的。處理第一個字串 `"eat"` 時，上方的 character trace 產生 `E`。`groups[E]` 發生 MISS，呼叫 `list()`，儲存 `E -> []`，然後回傳該空 list。Append 後，它變成 `["eat"]`。

處理 `"tea"` 時，新的全零 list 會經過三次更新：

```text
read 't': index 19; nonzero counts t:1
read 'e': index  4; nonzero counts e:1, t:1
read 'a': index  0; nonzero counts a:1, e:1, t:1
```

完成的 tuple 與 `E` 相等。Lookup 命中既有的 `["eat"]`，並加入 `"tea"`，不會建立新的 value list：

```text
groups before: E -> ["eat"]
groups after:  E -> ["eat", "tea"]
```

處理 `"tan"` 時，indexes 依序是 19、0、13。它的 tuple 是 `T`，在 `e`、`n` 兩個位置與 `E` 不同。Lookup 發生 MISS，建立第二個群組：

```text
E -> ["eat", "tea"]
T -> ["tan"]
```

接下來的字串會重用或建立對應的 entry：

```text
"ate": indexes 0, 19, 4  -> E -> ["eat", "tea", "ate"]
"nat": indexes 13, 0, 19 -> T -> ["tan", "nat"]
"bat": indexes 1, 0, 19  -> B -> ["bat"]
```

處理 `""` 時，字元迴圈一次都不執行。初始的全零狀態就是完成的計數，因此 `Z` 是合法 key。它的 missing-key path 會產生 `Z -> [""]`，不需要特別處理 empty string 的 branch。

最後一筆 `"eat"` 再次產生 `E`。Append 保留了這個字串在輸入中的第二次出現：

```text
E -> ["eat", "tea", "ate", "eat"]
T -> ["tan", "nat"]
B -> ["bat"]
Z -> [""]
```

直到 outer loop 全部結束後，`list(groups.values())` 才會從已儲存的群組 lists 建立 outer list：

```python
[
    ["eat", "tea", "ate", "eat"],
    ["tan", "nat"],
    ["bat"],
    [""],
]
```

結果保存了指向這些群組 lists 的 references。其中的字串仍是原始 string objects；counting 沒有把它們換成 tuple 或排序後的拼法。找到第一個相符群組後不會 early return，因為後面的輸入仍然需要加入。

## 完整的 Python 解法

實作遵循與 movie 相同的順序：

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

獨立呼叫的方式是：

```python
result = Solution().groupAnagrams(
    ["eat", "tea", "tan", "ate", "nat", "bat", "", "eat"]
)
print(result)
```

`groups` 保存累積的答案，所以它跨越各字串的 iteration 持續存在。`count` 只描述當前字串，因此建立在 outer loop 內。Inner loop 必須先完成，才能執行 `tuple(count)`，因為部分 prefix 不能代表完整字串的 identity。每次 outer iteration 在 key 準備好後，恰好執行一次 append。所有 iterations 結束後回傳 values，才會取出群組，而非實作使用的 keys。

像 `["a"]` 這樣的單一字元輸入，會遞增 slot 0，並回傳 `[["a"]]`。兩個 empty strings 的輸入會回傳 `[["", ""]]`。兩者都不需要額外 branch。雖然題目規定輸入至少有一個字串，同一份程式對 empty input list 也會回傳 `[]`。

## 分組過程中持續成立的 property

Anagrams 共享計數，描述的是字串之間的關係。*loop invariant* 描述的則是特定時間點的 program state 意義。Outer-loop invariant 是：

> 處理輸入 index `i` 之前，`groups` 恰好依完整的 26-letter frequency tuples，將 `strs[:i]` 中每筆出現分組：每筆已處理輸入在相符群組中恰好出現一次，每個已儲存群組都非空，而且尚未加入 index `i` 或之後的任何輸入。

這個敘述包含 checkpoint、已處理的 prefix、尚未納入的未來輸入，以及每個已儲存群組的意義。

初始時 `i = 0`。尚未處理任何輸入，空 dictionary 代表空 prefix，因此 invariant 成立。

假設 invariant 在處理 `strs[i]` 之前成立。前面建立的 inner-loop property 證明，掃描結束時，`count` 已記錄這個字串的所有字母。將計數轉成 tuple 會保留這些值。若 key 已存在，就將字串加入唯一相符的群組；若 key 不存在，就先儲存新的空 list，再把字串加入其中。程式只把當前這筆輸入加入一次，不改動其他群組的內容。因此 dictionary 現在將 `strs[:i + 1]` 正確分組，為下一次 iteration 恢復 invariant。

終止時 `i = N`，已處理的 prefix 就是整個輸入，每筆出現都被保留一次。相等的 tuple keys 將 anagrams 放在一起，而 equivalence proof 保證不同的 anagram classes 不會共享同一 tuple。因此回傳所有 value lists，恰好得到題目要求的 partition。

Hash collisions 不會破壞這個證明，因為 dictionary 保留了 tuple keys，並使用它們的 equality 規則。若只儲存 hash integer，並將其視為唯一的群組 identity，這個證明就無法成立。

## 一個錯誤實作與它首次失敗的位置

把 counting list 移到 outer loop 外面，看起來可能只是省下一些 allocation：

```python
count = [0] * 26
for s in strs:
    for c in s:
        count[ord(c) - ord('a')] += 1
    groups[tuple(count)].append(s)
```

但這會改變 `count` 的意義。第一個字串結束後，下一個字串開始時，它仍然保留上一個字串的計數。

以下是能區分對錯的兩字串範例：

```python
["a", "a"]
```

第一個字串產生 `a:1` 的 key，並建立 `["a"]`。第二次掃描之前，`count[0]` 已經是 1；再讀入第二個 `a`，就把它加到 2。第二個字串因此被存到代表兩個 `a` 的 key 之下，產生兩個分開的群組，而非 `[["a", "a"]]`。

第一個錯誤 state 出現在第二個字串開始時：當前字串已處理的 prefix 還是空的，working counters 卻不是零。Dictionary 還沒發揮作用，inner-loop invariant 就已經失效。直接的修正方式，是把 `count = [0] * 26` 放回 outer loop 裡。

這個例子也區分了兩個 containers 的 lifetime：dictionary 必須跨字串累積，counting list 則必須在每個字串開始時重新建立。

## Sorting 也能提供 canonical key

另一個方法是將字元排序，再串接成字串：

```python
key = ''.join(sorted(s))
```

對同樣的三個 anagrams：

```text
"eat" -> ['a', 'e', 't'] -> "aet"
"tea" -> ['a', 'e', 't'] -> "aet"
"ate" -> ['a', 'e', 't'] -> "aet"
```

`sorted(s)` 建立新的 list，`join` 則組成 key string。原始 `s` 仍然可以加入群組。Sorting 保留每一次字元出現，因此 `"ab"` 變成 `"ab"`，`"aab"` 變成 `"aab"`，不會出現 set 遺失 multiplicity 的問題。

分組架構沒有改變：

```text
original string -> canonical key -> dictionary lookup -> append original string
```

不同的只有 canonicalization 方法。Counting 描述每種字母各有多少個；sorting 則將所有字元出現排成同一種標準順序。

### 推導 logarithm

設一個字串長度為 `k`。Balanced merge-sort model 可以解釋常見的 `k log k` sorting bound。先從八個各有一個 element 的已排序片段開始，兩兩 merge 後，大小會如下變化：

```text
Initial pieces:   1 1 1 1 1 1 1 1
After level 1:    2   2   2   2
After level 2:    4       4
After level 3:    8
```

Merge 兩個已排序片段時，會反覆取出下一個較小的 element，直到兩個片段都用完。在這次 merge 中，每個 element 只被處理 constant 次數。Level 1 有四次 merge，每次處理兩個 elements，總計八個；level 2 有兩次 merge，每次處理四個，總計仍是八個；level 3 的一次 merge 則處理八個。

總共有三層，因為大小為 1 的片段加倍三次後就會到達 8：

```text
1 * 2 * 2 * 2 = 8
2**3 = 8
log2(8) = 3
```

對 `k` 個 elements 而言，加倍 `L` 次後，片段大小為 `2**L`。令它等於 `k`，得到 `L = log2(k)`。若 `k` 不是 2 的次方，雖然需要取整，仍不影響成長界線。每層最多 `O(k)` 的工作量，乘上 `O(log k)` 層，就得到 `O(k log k)`。

Logarithm 表示一個數量反覆除以 base，直到到達 1 所需的次數；等價地，也是在問這個 base 要相乘幾次才能得到該數量。Base 2 對應這個模型中的減半與加倍。Big O 通常省略 base，因為對任何固定的 base `b > 1`，

```text
log_b(k) = log_2(k) / log_2(b)
```

分母是常數，而 Big O 忽略固定的乘法因子。因此 `O(k log2 k)`、`O(k log10 k)` 與 `O(k ln k)` 描述相同的 asymptotic growth。

### Python 實際如何排序

CPython sorting 具有 adaptive 與 stable 特性。它的 [v3.14.0 實作說明](https://raw.githubusercontent.com/python/cpython/v3.14.0/Objects/listsort.txt) 將 Timsort 描述為會偵測 ordered runs 再將其合併的 natural mergesort；merge scheduling 使用 Powersort。Run 是已經排好序的區域。Adaptivity 代表實作能利用這些區域，因此某些輸入的工作量會遠低於 worst-case `O(k log k)` 界線所暗示的程度。Stability 會保留相等 elements 的相對順序，不過我們用重複字元建立 key 時，並不需要這項特性。

上方的 balanced levels 用來解釋成本模型，不是 Python sorting 實作的 exact trace；實作不一定把字串切成完全平衡的樹。Sorting 也需要儲存空間：`sorted(s)` 會具體建立 `k` 個字元 entries，而 CPython 的 merges 可能使用 linear temporary space。

![Counting 與 sorting 是可替換的 canonical key 建立方法，之後都接到相同的 hash-map grouping。](https://medium-compiler.vercel.app/assets/alg-four/figure-4.svg)

*Counting 與 sorting 是兩種可替換的 canonicalization。上方的 balanced merge 推導解釋了 logarithmic factor；這張示意圖則比較兩種選擇。*

## 從操作推導時間成本

Big O 描述資源上界如何隨輸入大小成長。固定 26 個位置的 alphabet 這類常數可以省略，但每個字串都要執行一次的工作，不會因為字串是空的就消失。

定義以下變數：

- `N`：輸入字串數。
- `k_i`：第 `i` 個字串的長度。
- `M = sum(k_i)`：全部輸入字元數。
- `K`：maximum string length，因此每個 `k_i <= K`。
- `A`：alphabet size，在這裡等於 26。
- `G`：anagram 群組數，最多為 `N`。

對一個長度為 `k_i` 的字串，counting solution 會執行以下操作：

```text
create count list          O(A)
scan and update counts     O(k_i)
create tuple               O(A)
hash the tuple             O(A)
lookup/insert group        expected O(1) table work
                           with up to O(A) key-comparison work
append the original string amortized O(1)
```

Tuple 與 equality 的成本相對於 `N`、`K` 能視為常數，只因為 `A = 26` 是固定的。若 tuple 長度隨輸入成長，就不能做同樣的簡化。Table 在 MISS 時可能執行不只一次 lookup，但固定次數不會改變成長界線。

「Amortized」描述的是一連串操作。持續成長的 list 偶爾需要更大的 backing array，並複製既有的 references；單次 append 因此可能超過 constant time。把這些擴充成本分攤到整串 appends，總工作量會與加入的項目數呈線性關係，因此在一般 dynamic-array model 下，每次 append 的 amortized 成本為 `O(1)`。

在正常的 hash-table 行為下，將每個字串的工作量加總，可得 expected time `O(M + N A)`。建立 outer result list 的成本是 `O(G)`，因為 `G <= N`，已包含在上述界線內。令 `A = 26`，完整界線就是：

```text
O(M + N)
```

這也涵蓋了輸入全是 empty strings 的情況：即使 `M = 0`，建立與 hash keys、append 每筆輸入，仍然需要與 `N` 成正比的工作量。

因為 `M <= N K`，以 maximum length 表示的界線是 `O(N(K + 1))`。當 `K >= 1`，通常簡寫為 `O(NK)`。若使用 average length `K_avg = M / N`，則寫成 `O(N(K_avg + 1))`；要省略 `+1`，必須約定這個平均值有正的下界。這些只是相同操作的不同表示法，不是不同演算法。

這些假設不能省略。若嚴重的 collisions 迫使每次 dictionary operation 都檢查最多 `G` 個 entries，對固定大小的 keys，table 工作量可能逼近 `O(N²)`。Expected linear result 不是不受碰撞影響的 worst-case 宣稱。標準分析也將有界大小的 index 與 count 操作視為 constant time；題目的長度上限讓計數最多為 100。若要擴展到任意大的 integers，就需要 bit-cost model。

對 sorting solution 而言，當 `k_i >= 2`，每個字串需要 `O(k_i log k_i)` 的 sorting 工作量，另外還有 linear materialization、joining 與 key hashing。也能涵蓋長度 0、1 的表示式是：

```text
O(N + sum(k_i * log(k_i + 1))) expected total time
```

以 maximum length 表示，得到 `O(N + N K log(K + 1))`；當 `K >= 2`，通常寫成 `O(NK log K)`。若字串長度不同，直接把 arithmetic average 代入 logarithmic expression，一般不能得到等價界線；使用總和或 maximum-length 形式，可以避免這個歧義。

在這個固定且小的 alphabet 下，counting 是較好的 asymptotic 選擇。但這不能證明它對每個短 Python 輸入都比較快：allocation 成本、實作常數與既有的 ordered runs，也會影響實際執行時間。

![Expected counting time O(M + 26N)、額外的 keys 與 references，以及作為輸出的原始字串群組。](https://medium-compiler.vercel.app/assets/alg-four/figure-5.svg)

*Time 與 space 分別衡量同一個演算法的工作量與儲存量。即使沒有字元可掃描，每個字串固定要做的工作仍然存在。*

## 實際額外配置了哪些記憶體

暫時的 counting list 有 `A` 個 entries；同一時間只需要一個目前使用中的 counting list。Dictionary 為每個不同群組保留一個含 `A` 個 elements 的 tuple，因此 keys 需要 `O(G A)` 空間。新建 tuple 若與既有 key 相等，不必再成為另一個被保留的 dictionary key。

所有群組 lists 合計恰好有 `N` 個指向輸入字串的 references，包括重複輸入。此外還有 `G` 個 list objects、`G` 個 keys 的 dictionary entries，以及包含 `G` 個 references 的 outer return list。新配置的 container space 總計為：

```text
O(G A + N + A)
```

對固定 alphabet 與非空輸入而言，這是 `O(N)`。Append 時，實作不會複製每個字串的字元內容，而是儲存 references。回傳的群組仍會讓這些原始字串保持可達。

「不含輸出的 auxiliary space」取決於分析將哪些 containers 算作輸出。若排除回傳的 inner lists 與 outer list，working dictionary、keys、counters 仍需 `O(G A + A)` 空間。若把 abstract output 描述為包含全部字串內容，其 logical size 是 `O(M + N)`，通常可用 `O(NK + N)` 作為上界。這不同於宣稱這份 Python 實作新配置了 `M` 個字元副本。

Sorting alternative 還會配置字元 lists 與 key strings。最壞情況下，temporary sorting storage 是 `O(K)`。除了 `N` 個 references 與 dictionary containers，各個不同群組儲存的 key strings 合計最多還能佔用 `O(M)` 個字元。固定大小的 count keys 避免了這種隨長度成長的 retained key storage。

## Alphabet 改變時，重新選擇 key

假設輸入可以包含 uppercase letters、標點或任意 Unicode code points，且 anagrams 依精確的 code-point multiplicities 定義。Dictionary grouping pattern 仍然適用，但 26-slot representation 與 `ord(c) - ord('a')` indexing 不再適用。

Sorting 會成為簡單的替代方案，因為不必為每一種可能的字元配置一個 slot：

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

修改後的實作用一個 sorted-string key，取代 counting 與 tuple construction。例如 `"A!"` 與 `"!A"` 都會產生 `"!A"`，因此屬於同一群組。前面推導的 sorting 時間與儲存界線仍然適用。

Sparse character-to-count mapping 也能避免配置整個 alphabet，但必須替這些 character/count pairs 建立穩定且 hashable 的 representation。當 alphabet 不受限，而且精確的 character equality 已足夠時，sorting 往往更容易解釋與實作。

處理人類文字時，contract 可能還需要決定：大小寫差異，或視覺上相同文字的不同 Unicode representations，是否視為等價。Sorting code points 不會替我們決定這項政策。任何必要的 normalization，都必須先於 canonicalization 定義，因為它會改變哪些字串應該歸在一起。

## English Interview Q&A：在面試中解釋解法

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

## 用來重建程式的 Master Map

要重建解法，先從輸出必須保留的內容出發：每一筆原始輸入，都依 anagram equivalence 分組。下列依賴關係提供了 representation 與操作順序。

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

![Zero-context Master Map：分組任務、frequency equivalence、counting list 與 tuple、dictionary HIT 或 MISS、invariant 與成本。](https://medium-compiler.vercel.app/assets/alg-four/figure-6.svg)

*這張 map 連接了文章已建立的事實。從同一組題目限制，重建 representation、runtime 與成本。*
