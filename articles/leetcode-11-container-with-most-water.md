# Container With Most Water：為什麼可以捨棄較短的牆

兩面高牆若靠得太近，組成的容器容量也可能很小。在 LeetCode 11，必須一起考慮一對牆的高度與距離。

## 把圖像轉成數字

輸入 `height` 依序列出位置 `0, 1, ..., n - 1` 上各面垂直牆的高度。選擇兩個不同的位置 `i < j`，讓地面與兩面牆形成直立容器。回傳最大的容量，結果是一個 integer，而不是牆的位置。題目限制為 `2 <= n <= 100000`、`0 <= height[i] <= 10000`。題目沒有要求修改輸入，以下解法也都保留原始輸入。空輸入與只有一面牆的輸入不在這份 contract 內。[LeetCode 題目敘述](https://leetcode.com/problems/container-with-most-water/)。

水位不能高於較短的牆，否則水會從那一側流出去。水平距離是 `j - i`，算的是間隔數，而不是牆的數量。因此，一對牆的容量就是長方形截面面積：

`area(i, j) = (j - i) * min(height[i], height[j])`。

以自製範例 `[2, 5, 1, 4]` 而言，位置 `1` 與 `3` 的牆寬度為 `2`、水高為 `4`，面積是 `8`。位置 `0` 與 `3` 雖然更遠，面積卻只有 `3 * 2 = 6`。最高的牆本身無法決定答案。中間的牆不會讓這個長方形扣除相應高度；這個問題選擇的是兩個邊界，並不是把各處積存的雨水加起來。

若兩個選定高度都是零，面積也是零。所有高度都是零時，正確最大值就是零。因此，每個合法輸入都可以從 `best = 0` 開始。

## 先保留所有可能的配對

直接的解法是固定左邊位置，再嘗試它右邊的每個位置。`best` 保留目前算過的最大面積；保存舊配對的所有面積，只會增加儲存量，無助於下一次比較。

```python
def max_area_all_pairs(height: list[int]) -> int:
    n = len(height)
    best = 0
    for i in range(n - 1):
        for j in range(i + 1, n):
            area = (j - i) * min(height[i], height[j])
            best = max(best, area)
    return best
```

`range(i + 1, n)` 產生從 `i + 1` 到 `n - 1` 的位置，不包含 `n`。因此每次取值都在合法範圍內，每對牆都不相同，也不會反過來重算同一對。`min(a, b)` 回傳較小的 argument；`max(best, area)` 回傳較大的值。兩者都不修改 list。這裡使用的是文件中 [Python built-in functions](https://docs.python.org/3.14/library/functions.html) 的雙 argument 形式。

對 `[2, 5, 1, 4]`，六組配對依執行順序的面積為 `2, 2, 6, 1, 8, 1`。對應的 `best` 依序是 `2, 2, 6, 6, 8, 8`。因為每個候選都看過，最後回傳 `8`。

輸入接近上限時，候選數量就很重要。位置 `0` 有 `n - 1` 個搭檔，位置 `1` 有 `n - 2` 個，最後一個有用的左邊位置有 `1` 個。把這些數量正序、倒序各寫一次後相加，每組對應數的和都是 `n`，共有 `n - 1` 組。這樣把候選算了兩次，所以配對總數是 `n * (n - 1) / 2`。當 `n = 100000`，就要計算 `4,999,950,000` 次面積。若要跳過候選又不漏掉最大值，需要一個理由。

## 先計算尚未排除範圍中最寬的配對，再移除一面牆

保留 `left` 與 `right` 兩個 index，起初分別位於兩端。這裡稱它們為 two pointers；它們只是一般的整數位置，不是複製出來的 sublist，也不是 Python 記憶體位址。包含兩端的 `[left, right]` 區間，代表尚未解決配對可用的位置。捨棄任何位置前，先計算兩端形成的配對。

假設 `height[left] <= height[right]`。剛量到的面積是 `(right - left) * height[left]`。考慮保留 `left`，把 `right` 換成內部位置 `k` 的任何配對。新寬度 `k - left` 比原來小，而且即使新牆高很多，水高也不可能超過 `height[left]`。由於牆高非負，

`area(left, k) <= (k - left) * height[left] <= (right - left) * height[left]`。

所以這些配對都不可能勝過已記錄的兩端面積。把 `left` 加一，就能一次捨棄所有仍涉及 `left` 的候選。這是對它所有可能搭檔的上界證明，並不是預測下一面牆更高，也不是說下一次面積一定更大。

右牆較短時，把左右反過來即可：保留 `right`、把左邊往內移，不可能改善剛量過的面積，所以將 `right` 減一。若兩側一樣高，同一個不等式允許捨棄任一側。程式選擇捨棄左側。兩側同為零也安全，因為保留其中任何零高牆的配對，面積都是零。

這項規則會主動放棄寬度，但只有先證明失去的配對已被記錄值涵蓋，才移除牆。每次都移動較高牆的規則沒有這個證明。對 `[1, 3, 3]`，外側配對面積為 `2`。若把較高的右牆往內移，接著得到面積 `1`，最後回傳 `2`，卻漏掉位置 `1` 與 `2` 的面積 `3`。以牆的數量衡量，這是最小 counterexample：只有兩面牆時，在任何移動前就已算過唯一候選。

## 追蹤狀態直到回傳

對 `[2, 5, 1, 4]`，初始狀態是 `(left, right, best) = (0, 3, 0)`。

讀取 `height[0] = 2` 與 `height[3] = 4`。寬度為 `3`、水高為 `2`，面積是 `6`。先把 `best` 改成 `6`，再移動。因為 `2 <= 4`，將 `left` 加一，新狀態為 `(1, 3, 6)`。被跳過、仍保留位置 `0` 的配對，不可能超過剛量到的 `6`。

現在讀到高度 `5` 與 `4`。寬度為 `2`，面積是 `8`。`best` 變成 `8`。左牆較高，所以將 `right` 減一，得到 `(1, 2, 8)`。其中，配對 `(2, 3)` 可以安全捨棄：寬度是 `1`，水高不可能超過被捨棄右牆的高度 `4`。

讀到高度 `5` 與 `1`。寬度為 `1`，面積是 `1`。比較後 `best` 維持 `8`。再次將 `right` 減一，得到 `(1, 1, 8)`。此時 `left < right` 為 false：一個位置無法提供兩面不同的牆。回傳 `8`。

另外用 `[3, 3, 3]` 查看等高情況：先得到面積 `6`，移動左側，再量到面積 `3`，再次移動左側，最後回傳 `6`。移動後的當前面積可能變小；保存最大值才能保住先前答案。

```python
class Solution:
    def maxArea(self, height: list[int]) -> int:
        left = 0
        right = len(height) - 1
        best = 0

        while left < right:
            left_height = height[left]
            right_height = height[right]
            area = (right - left) * min(left_height, right_height)
            best = max(best, area)

            if left_height <= right_height:
                left += 1
            else:
                right -= 1

        return best
```

`while` 在每次執行迴圈主體前測試條件；`if` 恰好選擇一個 branch。因此，每次 iteration 恰好改動一個 index。[Python compound statements](https://docs.python.org/3.14/reference/compound_stmts.html)。

讀取 `height[left]` 會取出元素，但不會移除它。把值指派給 `left_height`，會綁定一個 local name，並不會複製 list。Python integer 是 immutable：`left += 1` 計算新的整數值，再將 `left` 綁定到它，不會改動 `height` 裡儲存的整數。若 assignment 的目標是 `height[left]` 這樣的 item，便會寫入該 item；這裡沒有這種 assignment。呼叫者仍能使用原始輸入。[Python assignments](https://docs.python.org/3.14/reference/simple_stmts.html#assignment-statements)、[numeric types](https://docs.python.org/3.14/library/stdtypes.html#numeric-types-int-float-complex)。

## 每個檢查點都成立的事

面積公式描述的是單一配對。整個搜尋是否正確，還需要另一個 loop invariant：在指定檢查點持續成立的敘述。每次開始檢查 `while` 條件時，`best` 是所有已計算配對的最大面積；若尚未計算任何配對，它就是零。而任何一端位於當前區間之外的配對，面積都不超過 `best`。

起初 `[0, n - 1]` 外沒有任何位置，所以第二項敘述沒有被排除配對需要檢查。第一項也成立，因為 `best` 是零，而且所有合法面積都非負。

每次 iteration 量出兩端面積並更新 `best`，會保住第一項敘述。捨棄用的不等式證明，所有新排除配對的面積，都不超過剛量到的面積，也就不超過更新後的 `best`。由於 `best` 永不減少，先前排除的配對仍然被涵蓋。無論選哪個 branch，包括等高情況，這些事實都會重新建立 invariant。

距離 `right - left` 從 `n - 1` 開始，每次恰好減一。經過 `n - 1` 次 iteration，距離就變成零。此時，已沒有任何配對的兩端都能留在區間內，因此每個合法配對都已計算過，或被 invariant 涵蓋。除了不影響結果的初始零，`best` 也確實來自實際候選，因此它等於要求的最大值。

## 計算操作與儲存的值

令 `n` 表示牆的數量。我們用 bounded-integer、unit-cost model 比較成長：一次整數比較、加法、減法、乘法、local binding 或 indexed list access，都花費有界的工作量；儲存一個這樣的 scalar 或 reference 算一個單位。依題目限制，index 小於 `100000`，牆高至多 `10000`，面積至多為 `99999 * 10000 = 999,990,000`。這些值都能用固定數量、機器大小的整數片段表示。這個 model 計算工作量，並不是說所有 Python expression 的實際耗時相同。Python 能表示更大的整數，但若數字位數可以無限增加，就必須改用另一種 arithmetic cost model。

list access 的假設有具體的實作依據。在 CPython v3.14.0，list 將 element reference 存在以 index 定位的 slot；取得 slot `i` 會存取該 slot，而不是逐一走過前面 `i` 個元素。list 也儲存長度，因此 `len(height)` 不必逐面牆計數。在普通 list、沒有 concurrent mutation 的情況下，這些特性支持這種存取模式的有界工作量。[CPython list 實作](https://github.com/python/cpython/blob/v3.14.0/Objects/listobject.c)、[list 結構與存取 macros](https://github.com/python/cpython/blob/v3.14.0/Include/cpython/listobject.h)。

每次 two-pointer iteration 讀取 list 兩次、執行固定數量的有界算術與比較，並更新一個 index。`min` 與 `max` 各接收兩個 scalar，所以比較工作不會隨 `n` 增加。iteration 恰有 `n - 1` 次，迴圈條件檢查有 `n` 次；初始化與回傳增加固定工作。因此，總工作量可以被「某個常數乘以 `n`，再加上一個常數」限制。我們把這寫成 `O(n)` time。Big O 表示忽略固定乘數後的成長上界；這裡，精確的 iteration 次數也表明是線性成長，不只有上界。

同一時間，只有固定數量的 local name 與暫時 integer result 存活。後續 iteration 取代先前的值，不保存歷史。沒有 recursion、持續長大的 collection，也沒有複製輸入。Auxiliary space 指的是供應的輸入與回傳結果以外新增的儲存量，這裡為 `O(1)`。暫時算術值在同一時間也只占固定數量的有界單位。回傳單一 integer 的 output space 是 `O(1)`；呼叫者原本的 list 已占 `O(n)` 個單位，不計入 auxiliary space。

all-pairs 解法每個候選也使用相同的有界讀取、算術與雙 argument 比較。因此，`n * (n - 1) / 2` 次計算帶來 `O(n²)` time：隨著 `n` 增大，平方項主導成長。它仍然只需要 `O(1)` auxiliary space 與 `O(1)` output space。Python `range` 保留 start、stop、step，而不會把所有 index 都實體化。外層迴圈保留一個 range 與當前位置；每個內層 range 都取代前一個，不會留下配對 list 或面積歷史。即使執行期間建立過很多內層 range，同時存活的數量仍然固定。`n - 1` 次內層 range 初始化只儲存這些固定欄位，每次前進則遞增一個有界 integer index。在前述 elementary model 下，這些初始化增加線性工作量，每個候選的前進增加固定工作量；兩者都不超過平方級總量。[Python range objects](https://docs.python.org/3.14/library/stdtypes.html#ranges)。

對很小的輸入，all-pairs 適合作為檢查用的 oracle：它直接列舉 contract 中的候選，所以容易核對。若新的計分規則破壞較短牆的上界，它也仍可作為起點；但改過的規則需要自己的成本分析與證明。在目前的 contract 與大輸入上限下，two-pointer 解法能避免數十億次計算，也不增加隨輸入成長的儲存量。

## 改變間距，保留理由

假設輸入還提供 strictly increasing 的整數座標 `x`，與 `height` 採相同順序，且 `0 <= x[i] <= 1000000000`。高度與長度限制維持原樣。牆之間不再一律相隔一單位。繼續用 `right - left`，算出的會是間隔數，而不是間隔的總寬度。

將寬度改為 `x[right] - x[left]`。對 `x = [0, 1, 100]` 與 `height = [1, 3, 2]`，外側配對的面積是 `100`；移動較短的左牆後，得到 `99 * 2 = 198`。答案是 `198`。原本用 index 算寬度則會回傳 `2`。

```python
def max_area_at_positions(x: list[int], height: list[int]) -> int:
    left = 0
    right = len(height) - 1
    best = 0
    while left < right:
        left_height = height[left]
        right_height = height[right]
        area = (x[right] - x[left]) * min(left_height, right_height)
        best = max(best, area)
        if left_height <= right_height:
            left += 1
        else:
            right -= 1
    return best
```

Strictly increasing 座標保證，任一端點往內移都會縮小實際寬度。較短牆對水高的上界沒有改變，所以把 index 差替換成座標差後，捨棄用的不等式與 invariant 仍成立。Pointer 每次仍只移動一個位置：座標間距的數值大小，不會增加 iteration 次數。

這項改版每次 iteration 多讀取兩個座標 slot；對座標值做減法，取代原本對 index 的減法。它沒有新增隨輸入成長的迴圈或 collection。座標與面積仍有界，面積至多 `1000000000 * 10000 = 10¹³`，在同一 model 下只需固定數量的 scalar 單位。因此，`n - 1` 次 iteration 仍帶來 `O(n)` time，固定的存活狀態則帶來 `O(1)` auxiliary 與 output space。新增的座標 list 是已提供的輸入，另外占 `O(n)` 單位，並不是函式自行配置的 list。這項推導假定座標已排序且與高度對應；函式不會排序，也不會驗證那個不同的 contract。

## Interview English 與 master map

Why move the shorter wall? Keeping it caps the water height while moving the other endpoint inward reduces width. All such pairs are bounded by the endpoint area already measured.

Does the next pair have to improve? No. `best` remembers earlier candidates, so the current area may decrease.

What happens on equal heights? Either endpoint can be removed safely. This implementation removes the left one.

Why is the time linear? The index distance decreases from `n - 1` to zero, once per constant-work iteration.

What does constant space exclude? It excludes the caller's input list. The function adds a fixed set of scalar locals and returns one integer.

Master map 是一串因果關係：兩個牆的位置決定寬度；較短牆決定水高；兩者相乘得到候選面積。已計算的候選，限制了所有保留較短牆、另一側往內移的配對。移除該牆，會縮小尚未解決的區間，同時由 `best` 涵蓋已排除配對。當區間無法包含兩面牆，`best` 就涵蓋每個合法選擇。
