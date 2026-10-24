# Koko Eating Bananas：找出第一個足夠的速度

替 Koko 找出可接受的最慢進食速度，可以先問一個較容易的問題：某個速度需要多少小時？只要這個計算準確，一個失敗的速度就能排除所有更慢的速度。一個成功的速度則讓我們繼續往下找。這是對可能答案進行 binary search，不需要先把香蕉堆排序。

## 一小時只屬於一堆香蕉

在 [LeetCode 875](https://leetcode.com/problems/koko-eating-bananas/description/) 中，`piles` 是非空 list，裡面每個正整數代表一堆香蕉的數量。Koko 選定一個正整數速度 `k`，單位是每小時吃掉幾根香蕉。每小時她只能吃其中一堆；提早吃完那堆，也不能在同一小時開始吃另一堆。要求回傳能在至多 `h` 小時內吃完所有香蕉的最小速度。

限制是 `1 <= n <= 10^4`、`n <= h <= 10^9`，以及 `1 <= piles[i] <= 10^9`，其中 `n` 是香蕉堆數。每堆至少需要一小時，因此 `h >= n` 很重要：題目保證速度夠大就一定能完成。下面的解法只讀取輸入 list，不排序，也不改動其中的元素。空 list 和 `h < n` 不在這份 contract 內。[題目敘述與限制](https://leetcode.com/problems/koko-eating-bananas/description/)。

看一個小例子：`piles = [4, 4]`、`h = 3`。速度 `3` 讓每堆各花兩小時，總共四小時。速度 `4` 讓每堆各花一小時，總共兩小時。答案是 `4`，儘管把八根香蕉除以三小時再向上取整，會得到 `3`。這個捷徑把一堆剩下的處理容量挪給另一堆，違反每小時的規則。

## 計算一個候選速度，不必逐小時模擬

對大小為 `p` 的一堆香蕉，以速度 `k` 進食，先數出完整的 `k` 根一組有幾組。若還有剩餘香蕉，就需要額外一個完整小時。這個數量是 `p / k` 的 ceiling，也就是不小於該商的最小整數。例如 `p = 11`、`k = 4`，會分成 `4, 4, 3`，因此需要三小時。

Python 的整數 `//` 運算會把商向下取整。對正整數而言，`(p + k - 1) // k` 則能得到需要的向上取整結果。原因可以從 `p = q * k + r` 看出，其中 `q` 是完整組數，remainder `r` 滿足 `0 <= r < k`。當 `r = 0`，加上 `k - 1` 後，整數商仍是 `q`。當 `r > 0`，`r + k - 1` 落在 `k` 到 `2 * k - 2` 之間，整數商便成為 `q + 1`。兩種情況都恰好算出需要的小時數。[Python 算術語意](https://docs.python.org/3/reference/expressions.html#binary-arithmetic-operations)。

逐堆算出這個數量，再分別加起來，把總和稱為 `T(k)`。每堆都需要自己的時段，因此任何合法 schedule 至少需要 `T(k)` 小時。而先吃完一堆、再吃下一堆，就能恰好達到這個總時數。因此，`T(k) <= h` 是速度 `k` 能完成任務的必要且充分條件。調換香蕉堆的順序，不會改變這個總和。

以 `k = 4` 處理 `[3, 6, 7, 11]` 時，名為 `hours` 的 accumulator 從零開始。第一堆貢獻 `(3 + 3) // 4 = 1`，讓 `hours` 變成 `1`。下一堆貢獻 `2`，讓它變成 `3`；再下一堆貢獻 `2`，讓它變成 `5`；最後一堆貢獻 `3`，讓它變成 `8`。計算只保留累計總和，不會為這四個貢獻值另建 list，也不會改動香蕉堆。

## 更快的速度不會需要更多小時

增加 `k` 不會讓任何一堆需要更多小時：某個速度若能在指定時數內吃完一堆，提高速度後仍能在那些時數內吃完。把各堆的小時數相加，也會保留這個方向。因此，`T(k)` 不會隨著 `k` 增加而增加。檢查式 `T(k) <= h` 呈現 monotone 的形狀：前面是一段失敗的速度，這段可能為空，後面則都是成功的速度。

這個性質允許我們一次排除整段範圍。如果速度 `6` 失敗，從 `1` 到 `6` 的每個速度都失敗。如果速度 `6` 成功，最小成功速度至多是 `6`，但也可能更小。一遇到成功的 probe 就回傳，會忽略這個差別。

令 `M` 是最大那堆的大小。速度 `M` 能在一小時內吃完任一堆，總共恰好需要 `n` 小時，符合題目保證的 `h >= n`。正整數答案不可能低於 `1`，而最遲在 `M` 就有答案，所以從 inclusive interval `[low, high] = [1, M]` 開始。這兩個數字表示速度，不是 `piles` 的 index；不需要已排序的香蕉堆 list，也不需要儲存所有候選速度的 list。

在每次 search iteration 開始時，維持這個 invariant：**The minimum feasible speed lies in the inclusive interval [low, high], and high is feasible.** 意思是最小可行速度仍在包含兩端的 `[low, high]` 裡，而且 `high` 本身可行。這裡 feasible 指速度通過小時數檢查。monotone 性質描述所有速度的答案如何變化；invariant 描述目前搜尋狀態仍保證哪些事。

選擇 `mid = (low + high) // 2`，也就是偏下方的中間整數。當 `T(mid) > h`，設定 `low = mid + 1`：`mid` 和所有更小速度都已失敗。否則設定 `high = mid`：更大速度已無必要，但成功的 `mid` 仍須留作候選。當 `low == high` 時停止，回傳該數值。這種把有序候選範圍反覆減半的方法，就是 binary search。

## 從輸入一路追到答案

使用 `piles = [3, 6, 7, 11]`、`h = 8`。先初始化 `low = 1` 和 `high = 1`。尋找最大香蕉堆的 scan 依序讀取 `3, 6, 7, 11`；每個值都超過當時儲存的 upper bound，因此 `high` 依序變成 `3`、`6`、`7`、`11`。每次計算 `hours` 都重新從零開始。

```text
[low, high] = [1, 11]
mid = 6
pile hours: 1 + 1 + 2 + 2 = 6
6 <= 8 -> high = 6 -> [1, 6]

[low, high] = [1, 6]
mid = 3
pile hours: 1 + 2 + 3 + 4 = 10
10 > 8 -> low = 4 -> [4, 6]

[low, high] = [4, 6]
mid = 5
pile hours: 1 + 2 + 2 + 3 = 8
8 <= 8 -> high = 5 -> [4, 5]

[low, high] = [4, 5]
mid = 4
pile hours: 1 + 2 + 2 + 3 = 8
8 <= 8 -> high = 4 -> [4, 4]

low == high -> return 4
```

第一次 probe 在 `6` 就成功，但最後答案是 `4`。速度 `3` 的失敗，一次排除了 `1, 2, 3`。速度 `4` 和 `5` 都需要八小時，因此總時數恰好等於 deadline，也不能成為立即回傳的理由。即使數個速度給出相同總時數，搜尋仍須找出第一個成功速度。

速度 `4` 處理大小為 `11` 的那堆時，三個小時分別吃 `4`、`4`、`3` 根。最後那個未用滿容量的小時，仍只屬於這一堆。這正是 pooling 會建立錯誤模型的位置，而 scalar 計算仍符合實際進食規則。

## 完整 Python 解法

第一個 loop 明確找出最大香蕉堆：每讀取一個元素後，`high` 就保留目前看過的最大值；因為所有香蕉堆都是正整數，初始值 `1` 合法。之後每次 search iteration 都走訪同一份 list，計算候選速度所需的總時數。`Solution` class 是提交程式的 wrapper；`self` 指向它的 instance，演算法不會在該 instance 上儲存狀態。

```python
class Solution:
    def minEatingSpeed(self, piles, h):
        low = 1
        high = 1
        for pile in piles:
            if pile > high:
                high = pile

        while low < high:
            mid = (low + high) // 2
            hours = 0
            for pile in piles:
                hours += (pile + mid - 1) // mid

            if hours > h:
                low = mid + 1
            else:
                high = mid

        return low
```

`hours = 0` 必須放在 `while` loop 裡，因為每個新速度都需要新的總和。`hours += ...` 加到這個 scalar，不是加到輸入 list。scan 後的兩個 assignment，就是前面 trace 中的兩種 interval 更新。所有候選速度都保持正值，所以不會出現零 divisor。這裡沒有 recursion、sorting、輸入副本，也不儲存歷次 probe。

## 為什麼回傳的一定是最小速度

一開始，答案在 `1` 到 `M` 之間，而且 `M` 可行。假設某次 iteration 開始前 invariant 成立。如果 `mid` 失敗，monotonicity 排除所有至多為 `mid` 的速度，因此答案仍在 `[mid + 1, high]`；未變動的 `high` 仍然可行。如果 `mid` 成功，我們便知道 `mid` 是一個可行速度。最小值因此落在 `[low, mid]`，設定 `high = mid` 也讓 upper endpoint 保持可行。兩個 branch 都保留 invariant 的兩項保證。

當 `low < high`，偏下方的中間值滿足 `low <= mid < high`。失敗 branch 嚴格提高 lower endpoint；成功 branch 嚴格降低 upper endpoint。interval 維持非空，整數候選卻變少，因此最後一定只剩一個候選。invariant 此時保證這個唯一候選就是最小可行速度。即使最後一次更新後沒有另外測試那個確切速度，回傳 `low` 仍有根據。

若失敗時改成更新 `low = mid`，就會破壞前進的保證。對 `piles = [2]`、`h = 1`，interval 是 `[1, 2]`，而 `mid = 1` 失敗。錯誤的 assignment 會讓 `[1, 2]` 永遠不變。`+ 1` 是為了移除小時數檢查已經否定的候選。

邊界輸入也遵循同一套推理。若每堆大小都是 `1`，則 `M = 1`，search loop 完全不執行；速度 `1` 已是答案。若 `h = n`，每堆都必須在分配給自己的一小時內吃完，因此最大那堆迫使答案為 `M`。若 `h` 至少等於香蕉總數，速度 `1` 可行，搜尋便收斂到 `1`。`h >= n` 這項保證不可省略：在它不成立時，即使速度無限大，也無法在 deadline 內處理所有正數香蕉堆。

## 數出 scan 次數與儲存的值

採用 bounded-integer cost model：讀取一個 list 元素、比較這些整數，以及對本題限制內的值做算術，都各算 constant work。這是在比較 operation count 的成長，不是宣稱每個 Python instruction 的實際耗時相同。香蕉堆大小和速度至多是 `10^9`，總時數至多是 `n * M <= 10^13`，因此需要的數值範圍有界。Python 的整數在這些值上保持精確，不會在固定的 machine limit 發生 wraparound。[Python numeric types](https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex)。

尋找最大香蕉堆的 loop 走訪 `n` 個元素。測試一個候選速度也會走訪全部 `n` 堆，每堆執行固定數量的算術與更新，因此一次檢查的成本與 `n` 成正比。這份程式即使累計總和已超過 `h`，仍會刻意把總時數算完。

偏下方的中間值把 interval 分成兩組：包含 `mid` 的下半組，以及不包含它的上半組。候選數 `L` 為偶數時，每組都有 `L / 2` 個；`L` 為奇數時，下半組比上半組多一個。成功保留下半組，失敗保留上半組，因此任一更新後都至多剩下 `ceil(L / 2)` 個候選。例如初始 `M = 11` 時，候選數的 worst-case 上界依序是 `11 -> 6 -> 3 -> 2 -> 1`。減半 `t` 次後，至多剩下 `ceil(M / 2^t)` 個候選。只要 `2^t` 達到 `M` 就足夠；`ceil(log2 M)` 就是滿足此條件的最小整數減半次數。因此，總工作量至多是某個常數乘上 `n + n * ceil(log2 M)`，記為 `O(n * (1 + log M))`。當 `M >= 2`，常見簡寫是 `O(n log M)`。保留起初的 `n` 這一項，也能說明 `M = 1` 的情況。因為 `2^30 > 10^9`，在題目限制內至多需要三十次候選速度的 scan。

同時存活的只有固定數量的 scalar 和 loop 的 traversal state。重新賦值給 `hours` 或 endpoint，會取代前一個值，不會為每堆或每次 iteration 保留一筆紀錄。因此，在相同 bounded-integer model 下，auxiliary space 是 `O(1)`，不計入呼叫者提供的輸入 list。暫時算術結果也只增加固定數量的有界數值。回傳 output 是一個整數，在此模型下同樣使用 `O(1)` 空間。如果把題目限制換成任意長度的整數輸入，算術和整數儲存就需要另做 bit-size analysis；這裡的 scalar model 並未宣稱涵蓋那種情況。

## 何時適合更簡單的替代方法

Ascending search 可以依序嘗試 `k = 1, 2, 3, ...`，每次完整 scan 各堆的小時數，遇到第一個成功速度就回傳。它只保留當前速度、累計總和，以及選擇使用時的最大香蕉堆上界。之前所有速度都已明確被拒絕，因此第一次成功就是最小值。如果答案是 `a`，它會對 `n` 個元素 scan 共 `a` 次，也就是走訪 `n * a` 堆；因為 `a <= M`，worst-case time 是 `O(nM)`。單獨一堆大小為 `M` 的香蕉、`h = 1`，就會迫使它測試從 `1` 到 `M` 的每個速度。每次 scan 重用 accumulator，讓 auxiliary 和 output space 在相同 numeric model 下維持 `O(1)`。若改題後保證 `M` 是很小的固定值，ascending search 因為 control flow 較簡單，會是合理選擇；這裡沒有承諾它比較快。當 `M` 可達十億時，跳過整段候選才是有用的差別。

另一種每小時規則，會更大幅地改變計算。假設 Koko 能在一小時內切換香蕉堆，把完整容量 `k` 用在多堆之間。令 `S` 是香蕉總數。在這個改題版本中，`h` 小時至多能吃 `h * k` 根；持續跨堆取香蕉，也能在香蕉吃完前用滿這個容量。因此，`h * k >= S` 既是必要條件，也是充分條件，最小整數速度便是 `(S + h - 1) // h`。只需一次 pass 把每堆加到 `S`，再做固定數量的算術：在相同 bounded model 下，time 是 `O(n)`、auxiliary space 是 `O(1)`，output 是一個整數。不再需要逐堆的小時數或候選搜尋。這個公式套在原題的 `[4, 4], h = 3` 會失敗，正是因為原題不允許在一小時中途換堆。

## 重建選擇，並用英文說明

對 `piles = [2, 5]`、`h = 4`，從 `[1, 5]` 開始。在看答案前，試著重建候選速度、每次總時數，以及兩個 endpoint 的更新。問自己：為什麼能移除那些未逐一測試的更小速度，而不是只記住 assignment 的形式？

重建結果是 `[1, 5] -> mid 3 -> 1 + 2 = 3 -> [1, 3]`；接著 `mid 2 -> 1 + 3 = 4 -> [1, 2]`；再來 `mid 1 -> 2 + 5 = 7 -> [2, 2]`，回傳 `2`。最後一次失敗排除 `1`，而一直維持的 interval 只剩 `2`。

Why can we use binary search without sorting the piles? "We search integer speeds, not pile positions. Increasing the speed cannot increase the required hours, so feasibility changes only from false to true."

Why do we round each pile upward? "An unfinished remainder takes a whole hour, and unused capacity cannot move to another pile in that hour. The required time is the sum of the per-pile ceilings."

What does the search invariant guarantee? "The minimum feasible speed remains in the inclusive interval, and the upper endpoint is feasible. A failed midpoint removes itself and all smaller speeds; a feasible midpoint stays in the interval."

What is the cost? "Finding the maximum takes one scan. Each midpoint takes another scan, and halving the candidate range needs at most ceiling log base two of the largest pile. The total is O(n times (1 plus log M)), with constant auxiliary space under the bounded-integer model."

題目規則來自連結中的 LeetCode statement；取整與整數保證來自連結中的 Python documentation。上面的 interval 推理、具體 trace、替代方法與 proof，則由那些規則推導而來。

```text
Master Map
one pile per hour -> round each pile upward -> add hours
higher speed -> no more hours -> monotone feasibility
h >= n -> largest pile M is feasible -> start [1, M]
mid fails -> discard all speeds <= mid -> low = mid + 1
mid works -> keep mid, discard larger speeds -> high = mid
answer stays inside + interval shrinks -> one minimum speed
one scan per probe + repeated halving -> O(n * (1 + log M))
fixed scalar state -> O(1) auxiliary space
```
