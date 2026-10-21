# Group Anagrams：從題目契約到 Python Runtime

LeetCode 49 · 從零串起 invariant、canonical identity、mutability、hashing、sorting、correctness proof 與 complexity。

![封面：題目、invariant、representation、runtime 與驗證結果。](https://medium-compiler.vercel.app/assets/alg-four/cover.svg)

*封面 · 一道題目，一條因果鏈 — 封面只呈現 Problem Constraint 到 Verified Algorithm 的主線，不把所有 Python 機制擠進一張圖。*

題目要我們把 anagrams 分組。背下 Hash Map 不難，但這個答案隱藏了真正的決策：為什麼字母順序不同的兩個 words 應該進入同一組？我們將從 constraint 推導穩定的 identity，追蹤實際 Python runtime，最後由發生過的操作推導成本。

## 題目真正要求保留什麼？

輸入是一組只包含 lowercase English letters 的 words；輸出是分組後的 list。每一次輸入的 word occurrence 都必須恰好出現一次；同一組互為 anagrams，不同 letter counts 不能混放。Group 的順序與 group 內的順序不受限制。

~~~python
input = ["eat", "tea", "tan", "ate", "nat", "bat"]
one_valid_output = [
    ["eat", "tea", "ate"],
    ["tan", "nat"],
    ["bat"],
]
~~~

最重要的 constraints 是 alphabet 固定為 a–z、輸入可能包含重複 words，而且字串可能為 empty string。因為 alphabet 大小固定，剛好 26 個 counters 就能表示完整的 identity。決定主要方法的，是這項 constraint，而不是「Hash Map 很快」這種泛泛印象。

## 先找 equivalence，再選 API

Anagrams 可以改變字母順序，但每個 character 的出現次數保持相同。因此兩個 words 互為 anagrams，若且唯若所有 character-frequency counts 完全一致。這是字串之間的 equivalence property，還不是演算法的 loop invariant。

Canonical key 讓邏輯上等價的 inputs 得到相等的 keys。對 a–z words，位置 0 表示 a 的次數、位置 1 表示 b，直到位置 25 的 z。這個 representation 保留重複字母的數量；只保存不同字母的 set，會把 'a' 與 'aa' 誤判成同組。

![決策圖：a–z → letter frequency → 26 counters → 相同 tuple keys → 同一組。](https://medium-compiler.vercel.app/assets/alg-four/figure-1.svg)

*從等價關係建立 canonical key — Alphabet constraint 導出固定 counters，再成為分組 identity。*

Decision chain 因此可以確定：先定義 equivalence property，再統計所需資訊、轉成 dictionary 可接受的 key，最後把原始 word 放進對應 group。Hashing 是 lookup 機制，不負責定義 anagram。

## Character 如何對應 counter index？

Python 的 ord() 取得 Unicode code point。對 lowercase English letters，這些 code points 與 ASCII 範圍相同：ord('a') 是 97，ord('z') 是 122。減去 ord('a') 會讓 a → 0、e → 4、t → 19、z → 25。公式之所以正確，完全依賴題目限制輸入是連續的 a–z。

~~~python
ord("e") - ord("a")   # 101 - 97 = 4
ord("a") - ord("a")   #  97 - 97 = 0
ord("t") - ord("a")   # 116 - 97 = 19
~~~

如果 character 是 uppercase 或任意 Unicode symbol，這個 representation contract 就不成立。Alphabet 改變時，必須重新選擇 indexing 或 frequency map，而不能默默沿用 26 個 counters。

## Program Movie：一個 word 如何進入 group

對每個 word 重新建立一個由 26 個 zeros 組成的 list。從左到右讀取 characters，把每個 character 轉成 index，再增加對應 counter。計數需要更新狀態，所以暫時使用 mutable list；建立獨立的 tuple key 後，這個 list 就完成了 working state 的工作。

~~~python
word = "eat"
counts = [0] * 26
# e -> counts[4] += 1
# a -> counts[0] += 1
# t -> counts[19] += 1
# counts now has 1 at positions 0, 4 and 19
~~~

第一個 word 'eat' 的 key 尚不存在，dictionary 建立 ['eat']。下一個 'tea' 得到相同的 count tuple，append 到原 group。'tan' 產生不同 tuple，建立新 group。接著 'ate' 回到第一組，'nat' 進第二組，'bat' 開第三組。Dictionary 不會預測未來；每次 iteration 結束後，只包含已處理 prefix 的 words。

![Runtime 圖：eat indexes 4、0、19；tuple key；MISS 建立 eat；tea HIT 後 append。](https://medium-compiler.vercel.app/assets/alg-four/figure-2.svg)

*一條真實的 character → bucket Runtime Trace — 更新 count list、轉換 tuple，再用 key 新增或查找 group。*

## Python Internals：list、tuple 與 dictionary

List 適合持續 mutation，但不能直接當 dictionary key：Python list 是 unhashable。呼叫 tuple(counts) 會建立獨立的 immutable tuple snapshot，不會凍結或修改原本的 list。這個 tuple 可以 hash，是因為 26 個 elements 都是 integers；若 tuple 裡包含 unhashable list，整個 tuple 仍無法 hash。

查詢 tuple key 時，Python dictionary 會先 hash 它以定位候選 entries，必要時再檢查 equality。兩個不相等的 keys 即使發生 hash collision，也不會因此被視為相等。分組正確的原因是完整 frequency counts 相同時 canonical tuples 才會相等，不是因為相同 hash value 足以證明兩個 words 等價。

參考實作使用明確的 missing-key branch：key 不存在就先配置 empty list，再 append 原始 word。defaultdict(list) 可以簡化相同的 missing-key path；只有透過方括號 lookup 並發現 key 缺失時才會呼叫 factory。兩個做法 append 的都是原始字串，沒有複製或排序該字串。

![Python runtime：mutable list → 可 hash 的 integer tuple → hash candidates → equality → group；MISS/HIT。](https://medium-compiler.vercel.app/assets/alg-four/figure-3.svg)

*穩定 Identity 不是 Hash Value — List mutation 與 tuple identity 分工不同；hash collision 仍需 equality。*

## 替代方案：Sorting Canonicalization

也能先排序每個 word，再把排序後的 characters join 成 string key。例如 'eat'、'tea'、'ate' 都會變成 'aet'。後面的 Hash Map 分組架構相同；不同的是 canonicalization：counting 直接累計 frequency，sorting 產生有序 character sequence。

~~~python
key = "".join(sorted(word))
# "eat", "tea", "ate" -> "aet"
~~~

一個 word 長度為 K 時，counting 只掃描 K 個 characters，主要成本是 O(K)，另外還有固定 alphabet 的 overhead。一般 comparison sorting 的 worst-case 量級是 O(K log K)。用 balanced merge 圖理解：大約 log2(K) 層、每層總共做 O(K) 工作。但這只是 complexity mental model，並非 CPython adaptive、stable 的 Timsort family 或現代 Powersort merge ordering 的逐步 trace。

![雙路徑：count K chars O(K)，comparison sort K chars O(K log K)，並註明層級圖不是字面 runtime。](https://medium-compiler.vercel.app/assets/alg-four/figure-4.svg)

*Counting 與 Sorting 為何成本不同 — Counting 掃過 characters 一次；sorting 還需要 comparisons 與 merge 的組織成本。*

因為題目限制了固定且很小的 alphabet，counting 是主要的 interview solution。若 alphabet 未知或很大，sorted string 可能更容易寫對，但也會保留 comparison sorting 的成本。離開 constraint 就沒有 universally best canonicalization。

## 從實際操作推導 Time 與 Space

定義 N 為 word 數、M 為所有字串長度總和、K 為平均 word 長度（在此簡寫有意義時），Σ 為 alphabet size，這題固定 26。每個 word 要初始化 Σ 個 counters、逐字掃描、建立並 hash 長度 Σ 的 tuple、做 average-case dictionary lookup，以及 amortized O(1) append。所以 counting 的 expected total time 是 O(M + NΣ)；Σ = 26 時為 O(M + N)。面試常簡寫 O(NK)，但必須注意 K 可能為 0，不能把每個 word 的固定成本忽略成零。

Sorting 對每個 word 做 comparison sort。若第 i 個 word 長度是 k_i，常用上界可寫成 O(N + Σ_i k_i log(k_i+1))，還要理解其中包含固定分組工作；典型非短字串情況常簡寫 O(NK log K)。Dictionary 的 O(1) 是 average-case expectation，不是所有輸入都保證的 worst case；兩個方案最後都用 Hash Map 保存 groups。

Space 要分層看：暫時的 counter list 是 O(Σ)。最多 N 個不同的固定長度 tuple keys 需要 O(NΣ)；groups 裡總共保存 N 個指向既有 string objects 的 references，因此額外 container memory 是 O(NΣ + N)，Σ 固定時是 O(N)。若採把回傳字串所代表的 characters 全算入 output size 的 convention，抽象輸出大小可以是 O(M)。不能把 output value 誤當成 space complexity，也不能因為引用了字串就宣稱實作複製每個 character。

![成本圖：expected time O(NΣ + M)，extra container space O(NΣ + N)，獨立標示 output convention。](https://medium-compiler.vercel.app/assets/alg-four/figure-5.svg)

*Time / Space 的操作成本帳本 — 主要工作是掃描 characters；固定 counters 與 key 成本每個 word 重複一次。*

## 完整、可執行的 Python 3 Reference

下方實作將 missing-key branch 明確寫出，與前面的 Program Movie 完全一致。它為每個 word 建立新 count list、轉為 tuple key，只 append 原始 word。即使是 empty string，也不需要額外 special-case branch。

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

### Correctness：Initialization、Maintenance、Termination

Loop invariant：處理 index i 之前，groups 恰好包含 strs[0:i] 中的所有原始 words，每個各一次，並按完整 character-frequency tuple 分組；沒有任何 future word。開始時 i = 0 且 dictionary 為空，因此成立。處理一個 word 時，計算它所屬 anagram-equivalence class 的唯一 frequency tuple；必要時建立 group，再 append 原始 word 恰好一次，因而恢復 i + 1 的 invariant。

當 loop 完成所有 N 個 words 時，processed prefix 等於整份輸入。Invariant 保證沒有遺漏、也沒有重複插入。由於 tuple equality 等價於完整 frequency equality，同一 group 中全部互為 anagrams，而且所有互為 anagrams 的 words 進入同組。回傳 dictionary values 因此符合題目要求。這個證明依賴 lowercase alphabet contract 與 Python 正常的 key equality。

### Edge Cases 與最早的反例

Empty string 不執行任何 character update，得到全零 tuple；多個 empty strings 自然進同一 group。單字母 word 只更新一格。完全重複的 inputs 則按 occurrence 各 append 一次。反過來說，只用 distinct character set 當 key 會誤把 'a' 和 'aa' 分在一起；第一個錯誤是遺失 multiplicity，不是 Hash Map 不夠快。

## English Interview Pack：保留意義，簡化口說

Approach：I use a hash map. For each word, I count the 26 lowercase letters. The count tuple is the key. Words with the same key go into the same group. I return all groups after scanning every word.

Invariant：Before processing word i, the map contains exactly the earlier words, grouped by their frequency keys. Correctness：each word enters its matching group once; after the last word, all groups are complete.

Complexity：With a fixed 26-letter alphabet, each word is scanned once. Expected time is O of N plus the total number of characters. The extra group containers and tuple keys use O of N space. Sorting also works, but each word takes O of K log K instead of a linear scan.

## Zero-context Master Map

最後必須保留幾個不同層次：task equivalence 定義什麼是正確分組；count tuple 表示該 equivalence；loop invariant 描述已處理的 prefix；dictionary hashing 加快 lookup，卻不取代 key equality。Output 是分組後的原始 words；Time 與 Space 是取得答案所走路徑的成本量測，不是中間或最終資料階段。

![總圖包含 constraints、equivalence、mutable list、tuple、dict、group output，以及獨立的 Time/Space measurements。](https://medium-compiler.vercel.app/assets/alg-four/figure-6.svg)

*完整因果圖 — Problem → invariant → representation → runtime → correctness → complexity。*

可以轉移到其他題目的習慣是：當題目要求分組等價項目，先定義 equivalence；再選擇不遺失關鍵差異的 canonical representation。之後才決定用什麼資料結構保存、再由實際操作推導 performance。
