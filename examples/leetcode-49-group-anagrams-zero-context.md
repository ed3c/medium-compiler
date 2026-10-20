# 49. Group Anagrams — invariant、canonical key 與 Python 資料模型

原題： [LeetCode 49 — Group Anagrams](https://leetcode.com/problems/group-anagrams/)。
本示範由使用者提供的 *ALG-LeetCode Mental Simulator v4.0* 契約獨立撰寫；文章顆粒度的參考連結與無法直接讀取原文的限制記錄在 [Medium reference](../.agents/skills/alg-leetcode-mental-simulator/references/medium-reference.md)。這是 source-grounded 教學範例，不是從該 Medium 文章轉錄的內容。

## Five-Anchor Memory Card

1. **Signal** — 「將相同字母組成的 words 分組」→ 找同類識別碼 → canonical key + dictionary grouping。
2. **State** — `groups[key]` 精確存放**已走訪 words** 中，字母頻次等於該 key 的所有原始 word，且各出現一次。
3. **Invariant** — Before processing word index i, each group contains exactly the words from strs[0:i] with its canonical character-count key, each once; no unprocessed word is present.
4. **Transition** — Count current word → freeze counts as tuple → look up/create bucket → append original word → continue。
5. **Bug Alarm** — 用 distinct-letter set 當 key 會遺失重複次數；`["a", "aa"]` 被錯誤合併。

## Invariant Memory

**Full proof form**

> Before processing word index i, each group contains exactly the words from strs[0:i] with its canonical character-count key, each once; no unprocessed word is present.

**Compact memory form**

> Before i, each bucket holds exactly its matching words from the processed prefix.

**Recall cue**

> Before index i, which words may each bucket contain, and can any future word appear?

繁中 runtime 直覺：字典目前只存已走訪的原始字串。每個 word 要先得到完整的字母頻次，才知道該進哪個 bucket。

## Program Movie

使用縮小後的 `strs = ["eat", "tea", "tan"]`，只播放資料變化，不逐行翻譯：

1. **Opening:** `groups = {}`；scanner 尚未讀取任何 word。
2. **First word:** `"eat"` 的 a/e/t 各一，產生 26 個數字的 tuple key；不存在相同 bucket，建立 `["eat"]`。
3. **Next:** `"tea"` 的 key 與 `"eat"` 完全相同；找到原 bucket，append 成 `["eat","tea"]`。
4. **Different branch:** `"tan"` 有 a/n/t；key 不同，建立另一個 bucket `["tan"]`。
5. **Exhaustion:** scanner 到尾端，回傳兩個 bucket。這題沒有「找到就 return True」分支；只有走完所有 word 後才回傳完整分組。

若輸入是 `[""]`，空字串的 26 個計數都為零，仍建立一個合法的 bucket，而非遺失空字串。

## Reference Answer

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

這是完整、可單獨執行的 Python 3 參考解。回傳群組的順序可以不同，因為題目允許任意順序。

## Pass 1 — Whole Encounter

**Contract:** Input 是 `strs` 字串陣列；Output 是 anagram groups；每個原始 word 必須**恰好出現一次**，同一群具有完全相同的字母數量，群與群不能混放。依原題：`1 ≤ n ≤ 10^4`，每個 word 長度 `0 ≤ k ≤ 100`，字符只包含 `a` 至 `z`。不得偷偷把 Alphabet 假設換成任意 Unicode，也不能漏掉 empty word。

如果每兩個字串都比較，重複執行的是判斷「這兩個 word 是否為同類」。我們改為為每個 word 算一次**完全相同的 canonical key**，讓 dictionary 在平均情況下能快速找到該群。

**為什麼 counts 足夠？** 兩個字串互為 anagrams，當且僅當 26 個小寫字母各自的出現次數完全相同。這個條件不是「兩字串含有同一組不同的字母」；`"a"` 與 `"aa"` 擁有相同字母種類，卻不是 anagrams。

**ASCII 與 ord:** Python 的 `ord("a")` 是 97、`ord("z")` 是 122。對 lowercase ASCII 字母，`ord(char) - ord("a")` 介於 0–25；第 0 格代表 `a`，第 25 格代表 `z`。`ord` 取的是 Unicode code point，但這個 26-slot mapping 的有效性來自**題目明確的 lowercase English-letter constraint**。

**Mutable → Immutable → Hashing:** `counts` 是 list，可在掃字母時原地改值；Python 的 list 不可作 dict key，因為它不可雜湊。完成計數後使用 `tuple(counts)`，讓固定順序的 26 個整數形成 hashable key。tuple 仍需其元素 hashable；這裡的元素都是 int，所以成立。dict 按 key 的 hash 定位候選位置，必要時也比較 key 相等性。重複的 word 與不同排列的 word 將命中同一 key。

**Runtime 的守恆:** `groups[key].append(word)` 保存的是原始 word，不是排序後的字母；因此輸出保持原值而不修改 Input。

**成本概況:** `n` 個 words，每個最多 `k` 個字母，alphabet size `Σ=26`；時間平均 `O(n(k+Σ))`，包括初始化及 tuple/hash；空間包含輸出 bucket/原字串 references 與 keys，約 `O(n(k+Σ))` 的保守上界（若重複利用輸入字串而不計字元儲存，可再細分）。

學習狀態：`PASSIVE_EXPOSURE`，不是已經會獨立重建的證據。

## Pass 2 — Structural Compression

**Chunk 1 — Initialize state:** 建立 dict。讀取：無；改變：空 bucket registry；若移除：沒有跨 word 的分類記憶。

**Chunk 2 — Scan + count:** 掃每個 word，建立 26-slot counts。讀取：當前 word；改變：當前局部 counts；若移除：無法區分 `"ab"` 和 `"aab"`。

**Chunk 3 — Freeze canonical key:** list → tuple。讀取：完整 counts；改變：建立不可變 key；若移除：直接以 list 查 dict 會出現 TypeError。

**Chunk 4 — Lookup/create bucket:** 以 key 取得對應群；讀取：groups 與 key；改變：必要時建立 list；若移除：新的 key 無法收納。

**Chunk 5 — Append original + finish:** append 原始 word，最後 return values；讀取：原 word 與 bucket；改變：該群的內容；若移除：Invariant 無法保證每個 word 恰好被歸檔。

**Pseudocode**

~~~text
create empty groups
for each word:
    compute exact letter frequencies
    freeze frequencies into a hashable canonical key
    if key has no group: create group
    append original word to matching group
return all groups
~~~

學習狀態：`STRUCTURAL_RECOGNITION` 代表有提供辨認材料，不表示讀者真的辨認成功。

## Pass 3 — Top-Down Back-Compilation

**Required Output** → every word in exactly one correct anagram group。

**Success Event** → one input word has been appended to the bucket matching its complete letter-count vector。

**Required Knowledge** → whether the current complete frequency signature has appeared before。

**Surviving State** → mapping from exact canonical key to accumulated original words in processed prefix。

**Fast Operation** → average dictionary key lookup/insert, independent of the number of existing groups under average hashing assumptions。

**Data Structure** → dict whose immutable tuple key represents 26 counts, with a mutable list as each value。

**Transition Order** → count → freeze → find/create bucket → append → continue。

**Termination** → after the last word, all input occurrences have been assigned and no future word is pending。

Q: 為何不直接使用 word 當 key？ A: anagrams 可有不同字母排列；`"eat"` 與 `"tea"` 是不同 strings，但要使用同一群 ID。

Q: 為何不能只存 `set(word)`？ A: set 去除了 multiplicity；`"a"` 和 `"aa"` 將得到同一組 distinct letters，導致錯誤合併。

Q: 為何先建立 key 才 append？ A: bucket 的身份取決於完整字母頻次。尚未掃完的 counts 只是 partial state；此時分類會違反 invariant。

Q: `sorted(word)` 不能用嗎？ A: 可以作為另一種 canonical representation，但 `sorted(word)` 直接回傳 list，不可作 dict key；先以 `"".join(sorted(word))` 得到 hashable string 才可用。Python sorting 使用 Timsort，最壞時間上界 `O(k log k)`，對近乎有序資料可能更快；不能拿 Timsort 當本題字母頻次方案的 Runtime 步驟。

## Pass 4 — Active Reconstruction + Oracle Diff

先遮住上方完整程式碼，從 Invariant 和 Program Movie 重建：

~~~python
class Solution:
    def groupAnagrams(self, strs):
        groups = ______
        for word in strs:
            counts = ______
            for char in word:
                ______
            key = ______
            if ______:
                ______
            ______
        return ______
~~~

**Bug reconstruction:** 某實作把 key 寫成 `tuple(sorted(set(word)))`。請找出最早偏離正確分類的地方，並用最小字串組合作反證。

**STOP HERE — recall before reading the Oracle below.** 不用先回覆聊天，答案已在同一文件。

### Oracle

~~~python
class Solution:
    def groupAnagrams(self, strs):
        groups = {}
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

**Self-Diff:** State 初始化是否為空 dict？是否真的計算 multiplicity？Key 是否是 hashable tuple？是否先完成 Key 再查找？不存在群時是否建立？是否 append *原始 word*？return 是否在 loop 之後？是否維持「只包含已處理 prefix 且每個 word 恰好一次」？是否說明每個 word 的固定 26-slot 初始化與計數成本？

本文件只能記錄 `ACTIVE_RECALL_EXERCISE_PROVIDED`、`MASTERY_NOT_YET_OBSERVED`；沒有讀者的實際重建答案及 Diff。

## Correctness Proof

**Invariant:** Before processing word index i, each group contains exactly the words from strs[0:i] with its canonical character-count key, each once; no unprocessed word is present.

**Initialization:** 在 index 0，處理過的 prefix 為空，groups 也是空 dict。每群都精確表示空 prefix，Invariant 成立。

**Maintenance:** 假設處理 index i 之前 Invariant 成立。完整 26-count tuple 是該 word 的 canonical key，因為相同 counts 與 anagram 等價。程式只在此 key 的群尾 append 這一次 word，不修改其他 group，也不加入未處理 word；因此處理後的 groups 正好反映 `strs[0:i+1]`，並維持每個輸入 occurrence 恰好一次。

**Termination:** 此方案不需要 early return。當 loop 結束 `i=n`，Invariant 告訴我們每個輸入 word 都在其唯一的正確 bucket 中，且沒有多餘的 word；回傳 groups.values() 即滿足題目。若有 empty word，其 count tuple 仍有效，證明沒有例外。

## Complexity and Assumptions

定義 `n = len(strs)`，`k = max(len(word))`，`Σ=26`。

**Time:** 平均 `O(n(k+Σ))`。每個 word 建立 Σ slot（`O(Σ)`），掃 k 個字母（`O(k)`），tuple 建立與 hash 至多 `O(Σ)`，平均 dict lookup/append 為常數階攤銷。固定 26 字母時，通常簡寫 `O(nk)`，但若 k 可為 0，精確式保留 `+Σ` 更容易解釋。

**Space:** 最多 n 個不同 key，各有 Σ 個 int，因此 metadata 需要 `O(nΣ)`；group lists 的引用需要 `O(n)`，本演算法不複製每個原字串的字符。若計算包含 Input/Output 的完整字符量，可用保守 `O(n(k+Σ))`。局部 counts/tuple 另外使用 `O(Σ)`。

**Assumptions:** Python dict 平均 hash lookup/insert 為 O(1)（不保證對所有碰撞情況都如此）；輸入僅 a–z；不要求群組或群內 word 的排序。沒有改動 Input Strings。

## Bug Alarm and Minimal Counterexample

**First suspicious operation:** 用 `set(word)`（只記出現過的字母）取代完整頻次 key。

**Runtime consequence:** `"a"` 與 `"aa"` 的 distinct letters 都是 `{"a"}`，導致同群。

**Violated invariant:** 兩個不同 canonical **frequency** signatures 被誤視為相等，bucket 不再精確表示 anagram equivalence。

**Minimal counterexample:** `["a", "aa"]`，正確應是 `[["a"], ["aa"]]`（群組可交換）。

**Minimal repair:** 使用 26 個完整計數值並 freeze 成 tuple，而不是 set 的 distinct-only 內容。

## What-if Pivot

**Changed assumption:** 不再保證字元僅包含 a–z，可能有混合 Unicode。

**What remains reusable:** 必須有穩定且完整的等價類 canonical key，dict 仍可分組。

**What breaks:** `ord(char)-ord("a")` 不再保證介於 0–25。直接照搬 26-slot mapping 可能 IndexError 或分類錯誤。

**New state/algorithm:** 若要按 Unicode code-point 精確比對，可用 `tuple(sorted(word))` 作 key（tuple of characters），或用 `Counter(word)` 的完整頻次後排序固定鍵；需先明確定義 normalization/combining characters 的業務等價關係。不要自行宣稱經過 Unicode normalization 後的視覺等價字串就是本題的「相同字母」。

**Complexity:** Sorted-key 方案時間最壞 `O(nk log k)`、key 儲存 `O(nk)`，sorting 暫時空間與 Python 實作有關。

**Minimal implementation delta:** 把固定 counts/count loop 改為 `key = tuple(sorted(word))`，其他 dict bucketing/append/return 可以重用。

## English Interview Pack

**Approach**

I use a dictionary to group strings by a canonical character-frequency key. For each word, I count all 26 lowercase letters, convert the mutable list into a hashable tuple, and append the original word to the matching bucket. Two strings are anagrams exactly when their frequency tuples are equal. The algorithm takes O(n(k + 26)) average time and stores one entry for each input occurrence plus the group keys.

**Invariant**

The loop invariant is: before processing word index i, each group contains exactly the words from strs[0:i] with its canonical character-count key, each once; no unprocessed word is present.

**Correctness**

Initially, no words have been visited, so the dictionary is empty and the invariant holds. Each iteration computes the exact frequency key and appends the current word only to its matching group, preserving the invariant for the next input prefix. When the loop finishes, every input occurrence belongs to exactly one correct anagram group, so returning the dictionary values satisfies the contract.

**Live-coding narration**

I’ll use a dictionary keyed by an immutable 26-count tuple.  
I first build the count vector for the current word.  
A matching tuple means the word belongs to an existing anagram group.  
I create the bucket only if it is missing, then append the original word.  
At the end, I return all groups.

**Complexity**

Let n be the number of strings and k the longest string length. Each word costs O(k + 26) to count and freeze its key, plus average constant-time dictionary access. The total is O(n(k + 26)) average time, with up to O(26n + n) grouping metadata and references, excluding the source strings.

**Likely follow-up: Why not sort each word?**

Sorting is a valid alternative: use the sorted character sequence as the canonical key. In Python, `sorted(word)` returns a list, which is unhashable; convert it to a string with `"".join(sorted(word))` or to a tuple. The sorted-key method needs O(nk log k) worst-case sorting time and can be more convenient if the alphabet is not fixed at 26 characters.

## Spaced Recall Card

- **Day 0:** 只看 5-frame Program Movie，重播 word 如何抵達 bucket。
- **Day 1:** 回想五個 anchors，直接用英文說出完整 invariant。
- **Day 3:** 從空白 Python 檔重建 key construction、bucket lookup 與 final return。
- **Day 7:** 用 `["a", "aa"]` 推翻 distinct-letter set key。
- **Day 14:** 轉成 Unicode 字元時，改寫 canonical key 並用英文說明 correctness/complexity。

**Learning Status:** Five anchors PROVIDED · Four Passes PROVIDED · Active reconstruction opportunity PROVIDED · Active mastery evidence NOT YET OBSERVED · Execution status **MENTAL_TRACE**（本文沒有將實際測試紀錄當成文章自身的執行結果）。
