# 指定正文的 Zero Context Reader 重建

新合法輸入：`piles = [2, 7, 8]`, `h = 6`，原規則答案 **4**。

## 狀態與結果

最大值 scan：`high: 1 -> 2 -> 7 -> 8`，`low = 1`。

| 區間 | mid | 逐 pile 小時 | hours 累積 | 判斷與更新 |
|---|---:|---|---|---|
| [1, 8] | 4 | 1 + 2 + 2 | 0 -> 1 -> 3 -> 5 | 5 <= 6，high = 4 |
| [1, 4] | 2 | 1 + 4 + 4 | 0 -> 1 -> 5 -> 9 | 9 > 6，low = 3 |
| [3, 4] | 3 | 1 + 3 + 3 | 0 -> 1 -> 4 -> 7 | 7 > 6，low = 4 |

區間成為 [4, 4]，回傳 4。k = 3 失敗，單調性排除更小的速度；k = 4 用 5 小時可行。

## 證明與成本

- **逐 pile 向上取整恰好算出需求。** 整除時 q 個完整群足夠；餘數非零時多 1 小時。這不是只給 ceiling 公式：正文有 q、r 分解與兩種情形。 引句：ceiling, rounding_proof。
- **總時數條件是充要條件。** 每個 pile 都要自己的整數小時，所以下界是逐 pile 時數之和；依序吃完每個 pile 能達到這個和。 引句：sum。
- **可行速度是失敗後接成功的排列。** 加速不會使任何一個 pile 多花小時，加總也不會增加；所以失敗的 mid 排除 <= mid，而成功的 mid 保留下來。 引句：monotonic, update。
- **初始化、更新、終止一起證明最小值。** M 用 n 小時，保證可行；起點涵蓋最小值。失敗移 low 到 mid + 1，成功移 high 到 mid，兩者都保留最小值與可行 high。端點嚴格移動、候選數減少且不空，最後唯一候選必是最小值。 引句：bounds, invariant, update, progress, return_proof。

### 主程式：一般輸入

- time_as_stated：O(n * (1 + log M))；正文也聲稱至多 ceiling log base two of M 次 probe。
- concrete_work：新輸入先讀 3 個 pile 找 M，再做 3 次完整 probe，每次讀 3 個 pile；共 12 次 pile 訪問。這是讀取次數，不宣稱是全部 Python 指令數。
- auxiliary_space：O(1)，排除呼叫者供應的 piles；固定 scalars、迭代狀態與固定數量算術暫存。
- output_space：O(1)：一個 bounded integer。
- explained：每次 scan 的線性 pile 訪問數與固定活躍儲存值有因果說明；有區間變小的終止證明。
- not_explained：log base two、ceiling log 的意義與一般 probe 次數上界的推導；Big-O 記號的意義。不能把直接出現的公式當作已向目標讀者解釋。
- exact quote IDs：cost_model, numeric_range, scans, main_bound, space, output_space

### 主程式：M = 1 邊界

- time_as_reconstructed：找最大值仍讀 n 個 pile；0 次 probe。由正文 scan 說明可寫成 O(n)，與它保留 1 + log M 的總公式相容；這裡的 O(n) 是 scan 數的直接歸納，沒有導入外部演算法。
- auxiliary_space：O(1)
- output_space：O(1)
- exact quote IDs：boundary, scans, space, output_space

### 替代：逐一增加速度

- time_as_stated：答案 a 時 a 次 scan、n * a 次 pile 訪問；最壞 O(nM)。若另外先求 M，另加 n 次 pile 訪問，不改最壞階。
- concrete_work：k = 1 -> [2,7,8] 小時 -> 17；k = 2 -> [1,4,4] -> 9；k = 3 -> [1,3,3] -> 7；k = 4 -> [1,2,2] -> 5，首次通過。4 次 scan，共 12 次 pile 訪問；若先求最大 pile，合計 15 次。
- auxiliary_space：O(1)：重用 current speed、hours 與可選 M。
- output_space：O(1)
- explained：正文把 a scans 乘以每次 n visits，再用 a <= M 得最壞界，並給單 pile、h = 1 的達界情況；最小值由先前速度都明確失敗證成。
- not_explained：Big-O 記號本身仍未定義。
- exact quote IDs：ascending, ascending_worst, ascending_space, ascending_min

### 改限制：M 是很小的固定常數，仍用逐一增加速度

- time_as_reconstructed：沿用 n * a <= n * M；若 M 固定，最多固定次 scan，所以工作隨 n 成正比，通常寫 O(n)。正文只稱這是合理的簡單選擇，沒有把固定 M 代入後明寫這個界。
- concrete_work：以本例 M = 8 若當作允許的固定上限，最壞最多 8 次 scan，至多 24 次 pile 訪問；實際答案 4，所以 12 次。選擇性最大值 scan 同上。
- auxiliary_space：O(1)，沿用相同 accumulator 模型。
- output_space：O(1)
- exact quote IDs：tiny_M, ascending, ascending_space

### 改每小時規則：允許 pile 之間共用容量

- time_as_stated：O(n)：一次加總 S，之後固定次數算術。
- concrete_work：S 的變化 0 -> 2 -> 9 -> 17；3 次 pile 訪問；(17 + 6 - 1) // 6 = 22 // 6 = 3。速度 3 可在 6 小時的 18 容量內處理 17；速度 2 只有 12 容量。這個任務的答案 3 與原任務的 4 不同。
- schedule：每小時最多 3：第 1 小時 pile 2 的 2 加 pile 7 的 1；第 2、3 小時各吃 pile 7 的 3；第 4、5 小時各吃 pile 8 的 3；第 6 小時吃最後 2。
- auxiliary_space：O(1)：總和與固定 scalar。
- output_space：一個 bounded integer，即沿用模型的 O(1)。
- explained：正文解釋總容量的必要性，以及可跨邊界吃時能用滿容量而得到充分性。向上取整公式可接前面已給的 positive integer rounding 證明。
- not_explained：Big-O 記號本身仍未定義。
- exact quote IDs：pool_rule, pool_proof, pool_cost, ceiling, rounding_proof, output_space

### 改輸入：任意長度整數

- time_as_stated：沒有給新的時間界；正文明說須另做 bit-size analysis。
- auxiliary_space：沒有給新的空間界；不能把固定 scalar 數量當成任意長度 integer 的固定儲存量。
- output_space：沒有給新的界；一個 integer 不保證固定 bit 數。
- classification：明確限制適用範圍，未提供此改限制的完整分析；不是錯誤宣稱。
- exact quote IDs：big_integer_caveat

## 缺口與 bounded verdict

正文足以按新合法輸入重建答案 4、逐 pile 時數、狀態轉移、最小值證明；逐速替代與可跨 pile 改規則的實際工作量也可重建。

對指定無 logarithm/algorithm 背景的讀者，完整主時間界的 log 次數推導與 Big-O 意義未被說明；任意長度 integer 的成本也未分析且正文已明示。

缺 log/Big-O 說明不等於公式為 false；本次沒有辨識出有證據可判為 false 的明述主張。

僅這一版公開英文正文、這個新例子及 task.json 的單次 Reader 重建。不是 semantic score，也不是人類理解或學習成效證據。

具體成本是按照公式推演的 pile 訪問次數，沒有把它誤標成 Python 指令總數。Big-O 與 log 的公式可引用，但不能視為已解釋。未使用外部來源或執行 solution。

## 精確正文引句

**contract**

> The constraints are `1 <= n <= 10^4`, `n <= h <= 10^9`, and `1 <= piles[i] <= 10^9`, where `n` is the number of piles.

**rule**

> During each hour she eats from one pile. Finishing that pile early does not let her start another pile during the same hour.

**result**

> Return the smallest speed that finishes all piles in at most `h` hours.

**ceiling**

> For positive integers, `(p + k - 1) // k` instead gives the required upward rounding.

**rounding_proof**

> When `r = 0`, adding `k - 1` still leaves the quotient at `q`. When `r > 0`, `r + k - 1` lies between `k` and `2 * k - 2`, so the quotient becomes `q + 1`.

**sum**

> Each pile requires its own hours, so any valid schedule needs at least `T(k)` hours. Eating one pile to completion and then the next achieves exactly that total. Thus `T(k) <= h` is both necessary and sufficient for speed `k` to work.

**monotonic**

> Increasing `k` cannot increase the hours for any individual pile: a speed that clears it in a given number of hours can still clear it within those hours when increased. Adding the pile counts preserves that direction.

**bounds**

> Speed `M` clears every pile in one hour, using exactly `n` hours, which fits the guaranteed `h >= n`. No positive answer lies below `1`, and an answer exists by `M`, so start with the inclusive interval `[low, high] = [1, M]`.

**invariant**

> The minimum feasible speed lies in the inclusive interval [low, high], and high is feasible.

**update**

> Choose `mid = (low + high) // 2`, the lower middle integer. When `T(mid) > h`, set `low = mid + 1`: `mid` and every smaller speed have failed. Otherwise set `high = mid`: larger speeds are unnecessary, but the successful `mid` must remain a candidate.

**progress**

> When `low < high`, the lower middle satisfies `low <= mid < high`. In the failure branch the lower endpoint strictly increases; in the success branch the upper endpoint strictly decreases. The interval stays nonempty and has fewer integer candidates, so it must eventually contain one candidate.

**return_proof**

> The invariant then says that this sole candidate is the minimum feasible speed. Returning `low` is justified even if that exact speed was not separately tested after the final update.

**cost_model**

> Use a bounded-integer cost model: reading a list element, comparing these integers, and doing arithmetic on values within this problem's limits each count as constant work.

**numeric_range**

> Pile sizes and speeds are at most `10^9`, and an hours total is at most `n * M <= 10^13`, so their required numeric range is bounded.

**scans**

> The largest-pile loop visits `n` elements. A proposed speed also visits all `n` piles, performing a fixed number of arithmetic and update operations for each, so one test costs proportional to `n`. The code deliberately computes the complete total even when it already exceeds `h`.

**main_bound**

> Finding the maximum takes one scan. Each midpoint takes another scan, and halving the candidate range needs at most ceiling log base two of the largest pile. The total is O(n times (1 plus log M)), with constant auxiliary space under the bounded-integer model.

**space**

> Only a fixed number of scalars and a loop's traversal state remain live. Reassigning `hours` or an endpoint replaces its previous value; it does not retain one entry per pile or per iteration. Auxiliary space is therefore `O(1)` in the same bounded-integer model, excluding the supplied input list.

**output_space**

> The returned output is one integer, also `O(1)` space under this model.

**big_integer_caveat**

> If arbitrary-length integer inputs replaced the stated limits, arithmetic and integer storage would need a separate bit-size analysis; the scalar model here does not claim otherwise.

**ascending**

> If the answer is `a`, it performs `a` scans of `n` elements, or `n * a` pile visits; since `a <= M`, its worst-case time is `O(nM)`.

**ascending_worst**

> A single pile of size `M` with `h = 1` forces it to test every speed through `M`.

**ascending_space**

> Reusing the accumulator on each scan keeps auxiliary and output space `O(1)` under the same numeric model.

**ascending_min**

> All earlier speeds have been explicitly rejected, so its first success is minimal.

**tiny_M**

> If a changed task guaranteed that `M` was a tiny fixed value, ascending search would be a reasonable choice for its simpler control flow; it has no speed advantage promised here.

**pool_rule**

> Suppose Koko could switch piles within an hour and use the entire capacity `k` across them.

**pool_proof**

> In that changed task, `h` hours can consume at most `h * k` bananas, and continuously taking bananas across pile boundaries can achieve that capacity until the supply ends. Therefore `h * k >= S` is sufficient as well as necessary, and the minimum integer speed is `(S + h - 1) // h`.

**pool_cost**

> A single pass adds each pile to `S`, followed by a fixed amount of arithmetic: `O(n)` time, `O(1)` auxiliary space, and one integer output under the same bounded model.

**boundary**

> With all piles of size `1`, `M = 1` and the search loop never runs; speed `1` is already the answer.

**no_sort**

> These numbers are speeds, not indices into `piles`; no sorted pile list or stored list of candidates is needed.

## 讀取來源與環境 receipt

僅讀取：

- `/var/folders/l6/44bf7nvs64j60f1mpyy88hdm0000gn/T/article-entailment-2x13kv72/control-input/task.json`
- `/var/folders/l6/44bf7nvs64j60f1mpyy88hdm0000gn/T/article-entailment-2x13kv72/control-input/article.en.md`

`CODEX_THREAD_ID = 01a15ce6-a8a6-7943-b21a-036cd8ae2146`；僅讀取這個環境 key。

這是 Reader 自己記錄的 read receipt；不宣稱獨立 observer 已證實隔離。
