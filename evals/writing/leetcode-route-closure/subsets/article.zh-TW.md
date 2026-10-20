# LeetCode 78：撤回選擇，同時保留 subset

對 `nums = [2, 5]`，要求的結果包含 `[]`、`[2]`、`[5]` 與 `[2, 5]`。空 list 記錄「什麼都不選」這個選擇。`[5, 2]` 與 `[2, 5]` 描述的是同一個 subset；按照輸入順序選取元素，就能讓每個 subset 只有一種 list 表示方式。

[LeetCode 78](https://leetcode.com/problems/subsets/) 要求找出一個由互異整數組成的 array 的所有 subset，而且不能有重複的 subset。所有 subset 的集合稱為 power set。結果順序不限。輸入有 1 到 10 個元素，每個值介於 -10 與 10 之間。負數也只是一般候選值；正負號與數值大小都不影響它能否被選入。

題目沒有要求改動 `nums`。以下實作會保留輸入，回傳一個新的外層 list，其中包含新建立的 subset list。對空輸入，它們也會回傳 `[[]]`，但空輸入不在題目給定的限制內。重複的輸入值同樣不在 contract 內：`[2, 2]` 需要另一套 uniqueness 論證。

## 每個位置各做一次選擇

只找連續片段，會漏掉 `[2, 5, 7]` 中的 `[2, 7]`。Subset 可以跳過元素。允許任意選取順序，則會造成相反的問題：先選 2 再選 5，與先選 5 再選 2，會重複同一個 membership 選擇。

從左到右處理位置。每個位置恰好有兩種選擇：exclude 它的值，或 include 它一次。兩種選擇之後都前進到下一個位置，就不會重複使用同一位置。因為所有值互異，兩串不同的 yes/no 決策，必定對某個值的 membership 有不同決定，因此會產生不同的 subset。反過來說，任何一個要求的 subset，也會精確指定哪些位置應該 include，因此這個流程一定能走到它。

這是 decision sequence 與 subset 之間的對應關係。它說明為什麼不需要另外去除重複，並且不同於稍後用來維持程式正確性的 checkpoint 規則。

我們要記住下一個尚未決定的位置 `i`，以及已選取的值 `path`。進入 `visit(i)` 時，`path` 恰好包含 `nums[0:i]` 中已決定 include 的值，並維持輸入順序。在這次呼叫中，從 `i` 開始的所有位置都還沒有決定。外層 list `result` 則保留已完成的答案。

為了探索兩種選擇，函式可以用 `i + 1` 再次呼叫自己。這就是 recursion：caller 會暫停，等該次呼叫結束後，才從下一個 statement 繼續。每個尚未結束的呼叫各自保留自己的 `i`，以及稍後要恢復執行的位置。所有呼叫共用外層函式中的同一份 `path` 與 `result` list，並沒有各自取得 private copy。Python 的 [function 教學](https://docs.python.org/3.14/tutorial/controlflow.html#defining-functions) 說明了函式的 local state 與 recursive call。

Exclude branch 不需要改動 list。Include branch 則先 append `nums[i]`，探索剩下的位置，再移除剛才加入的值。這種復原稱為 backtracking，能讓後續 branch 從目前呼叫原先收到的選擇狀態開始。Checkpoint 也包含 return condition：`visit(i)` 結束時，必須把 `path` 留在進入時的狀態，同時將新增的完整 subset 保留在 `result` 中。

## 為什麼答案需要自己的 list

Python 的 `append` 會改動現有的 list，並回傳 `None`。`pop()` 會移除並回傳最後一個 item。`copy()` 會回傳 shallow copy：建立新的 list，但裡面仍是指向相同元素的 reference。這些行為記載在 [Python 的 list methods](https://docs.python.org/3.14/tutorial/datastructures.html#more-on-lists)。

這裡的元素都是整數。複製它們的 reference 就足夠，因為演算法改動的是 list membership，而非整數本身。即使 `path` 後來移除一個 entry，新的 subset list 仍能保留自己的 entry。這份獨立性，就是在答案完成時必須 copy 的原因。

一個看似可行的替換，是把 `result.append(path.copy())` 改成 `result.append(path)`。這時 `append` 儲存的是指向工作用 list 本身的 reference，不會凍結當下的內容。[Python 的 assignment semantics](https://docs.python.org/3.14/reference/simple_stmts.html#assignment-statements) 區分了把名稱 bind 到 object，與複製該 object 這兩件事。

最小的合法輸入就能使這個替換失敗。對 `[2]`，exclude leaf 會把空的 `path` append 進去。Include branch 再把同一個 list 改成 `[2]`，並再次 append 它。這時兩個 result entry 都指向 `[2]`。最後的 `pop()` 清空了唯一的共用 list，所以回傳結果變成 `[[], []]`，而且兩個 entry 指向同一個 object。要求中的 `[2]` 消失了。由於最小輸入長度是 1，不存在更小的合法輸入。

只在儲存答案時 copy，就能維持工作路徑更新的低成本，並讓每個答案的 membership 保持穩定。`path.copy()` 的回傳值會交給 `result.append(...)`；`append` 自己的回傳值則被忽略。

## 完整搜尋程式

```python
class Solution:
    def subsets(self, nums: list[int]) -> list[list[int]]:
        n = len(nums)
        result = []
        path = []

        def visit(i: int) -> None:
            if i == n:
                result.append(path.copy())
                return

            visit(i + 1)
            path.append(nums[i])
            visit(i + 1)
            path.pop()

        visit(0)
        return result
```

當 `i == n`，代表已沒有剩餘位置。即使 `path` 是空的，也已經是一個完整答案，所以程式先儲存再 return。在尚未到終點的呼叫中，第一個 child 處理 exclusion；第二個 child 則在 appended value 仍存在時處理 inclusion。第二個 child 會先復原它自己的選擇，最後的 `pop()` 才撤回目前呼叫自己的 inclusion。

`visit` 透過 `result` 傳遞答案，自己回傳的是 `None`。`subsets` 等 `visit(0)` 結束後，回傳累積完成的外層 list。`append` 與 `pop` 都不會碰到 `nums`。

## 跟著 `[2, 5]` 走過每個 branch

從 `result = []`、`path = []` 與 `visit(0)` 開始。位置 0 放的是 2。它的 exclude call 以 `path = []` 進入 `visit(1)`；位置 1 放的是 5。

這個呼叫先 exclude 5，以 `path = []` 進入 `visit(2)`。因為 `2 == n`，它配置一個空 snapshot 並 append 進去，得到 `result = [[]]`。然後它回到 `visit(1)`，沒有改動 `path`。

回到這次 `visit(1)`，`path.append(5)` 把 `path` 從 `[]` 改成 `[5]`。它的 include call 進入 `visit(2)`，copy `[5]` 並 append 該 copy，得到 `result = [[], [5]]`。這個 child 回來後，`path.pop()` 回傳 5，將路徑復原為 `path = []`。整個 exclude-2 subtree 到此結束，執行回到最初的 `visit(0)`。

最初的呼叫現在 append 2，得到 `path = [2]`。它的第二個 child 進入 `visit(1)`。Exclude 5 會抵達一個帶著 `[2]` 的 leaf，使 `result = [[], [5], [2]]`。這個 child 回來時保留 `[2]`。

目前的 `visit(1)` 接著 append 5，使 `path = [2, 5]`。Leaf copy 這個 list 並加入答案，得到 `result = [[], [5], [2], [2, 5]]`。回到 `visit(1)` 後，`pop()` 移除 5，復原為 `[2]`；再回到 `visit(0)`，另一個 `pop()` 移除 2，復原為 `[]`。

`visit(0)` 結束，`subsets` 回傳 `[[], [5], [2], [2, 5]]`。清空 `path` 並沒有清空任何已儲存的 snapshot。輸出順序來自先 exclude、再 include，符合題目要求。這是手動推演的 execution trace，並非 interpreter 執行時間的量測。

## 為什麼搜尋結束時，答案恰好正確

一開始，`visit(0)` 的 `path` 是空的，因為前面沒有任何位置可供 include。它符合 entry checkpoint。

假設某個尚未到終點的 `visit(i)` 符合 checkpoint。Exclude call 保持先前的選擇不變，並跨過位置 `i`，所以也符合它自己的 entry checkpoint。當它 return，return condition 會交回原本的 `path`。接著 append `nums[i]`，便建立了 include child 所需的 checkpoint。這個 child return 時會復原這條較長的 path；parent 的 `pop()` 再精確移除自己加入的 entry。因此 parent 的 return condition 也成立。

在 leaf，checkpoint 表示 `path` 是一份完整的 membership 選擇。Copy 會儲存這個選擇，並保持工作 list 不變。從 leaf 向最初呼叫進行 induction，可以證明每次呼叫都符合 restoration condition。因此，對 sibling 的推理並沒有偷用尚未證明的 cleanup 步驟。

每次 recursive call 都把 `i` 增加 1，並在 `n` 停下，所以最多只有 `n + 1` 個同時未結束的呼叫，也沒有 branch 能無限延伸。每個位置都會走過兩種決策。前面建立的對應關係，證明所有 subset 都會恰好出現一次。復原 `path` 維護 checkpoint；製作 snapshot 保護答案。兩項責任缺一不可。

## 把 copy 也算進成本

令 `n` 為輸入長度。為了比較成長趨勢，把位置數當作可變數量，同時保留相同演算法與值互異的假設。官方上限仍然是 10。我們計算 list-reference operation 與尚未結束的 function call，假設有足夠的 memory 與 recursion capacity，並忽略各平台的 byte 大小。若輸入大得多，Python 的 recursion limit 與指數成長的輸出會成為實際限制。

做完一個決策，有 2 個 branch；做完兩個，有 4 個。每增加一個位置，數量就翻倍，所以共有 `2**n` 個 leaf。所有層合計的呼叫數是 `1 + 2 + 4 + ... + 2**n = 2**(n + 1) - 1`：把這個總和乘以 2 再減去原總和，中間的項就會互相抵消。因此，單是走訪呼叫的成本就與 `2**n` 成正比。

Copy 長度為 `r` 的 path，需要把 `r` 個 element reference 寫入新的 list，另加固定的 list 建立成本。對 `n >= 1`，每個指定的輸入值都會出現在一半的 subset 中：把每個不含它的 subset，與加入它之後的 subset 配成一對。合計 `n` 個值，輸出中恰好有 `n * 2**(n - 1)` 個 element entry。這些 entry 正是 leaf 進行 copy 時寫入的項目。空 subset 仍然需要自己的一個 list。

因此，對 `n >= 1`，總時間為 `Theta(n * 2**n)`。`Theta` 表示，忽略固定倍數後，成長同時有這個形式的 upper bound 與 lower bound；`O` 則只給出 upper bound。這裡的 lower bound 來自必須寫入那麼多 output entry；列舉所有明確的 list，不可能只花與 `n` 成線性關係的時間。

主要的 live working state，是一條長度最多為 `n` 的 path，以及最多 `n + 1` 個尚未結束的呼叫。其 auxiliary space，也就是 input 與已保留 output 以外的 storage，是 `O(n)`。在 append 之前正在建立的 snapshot，長度也最多為 `n`，所以即使把這個 transient list 另外計算，上界仍然不變。Returned output 使用 `Theta(n * 2**n)` space，計入外層 reference、內層 list object，以及 element-reference slot。Integer object 不必重複建立。當 `n = 10`，共有 1,024 個 subset list，合計包含 5,120 個 element entry。

這些成本採用 end append 的一般 aggregate cost，沒有假設每次 append 都耗時相同。CPython 3.14 會在增加 list capacity 時保留一些空間，讓偶爾發生的 resize 成本分攤到許多次 append。這裡的 `m` 是一串持續增加長度的操作中的 append 次數；把 resize 工作分攤到這串操作，稱為 amortized analysis。一串 `m` 次 append 的 aggregate cost 是 `O(m)`。Copy 與 concatenation 則會明確走訪它們輸入中的 reference。相關實作位於 [CPython v3.14.0 的 `listobject.c`](https://raw.githubusercontent.com/python/cpython/v3.14.0/Objects/listobject.c)，尤其是 `list_resize`、`list_slice_lock_held` 與 `list_concat_lock_held`。這是 implementation cost model，並非對每個 Python implementation 的精確 allocation time 所作的承諾。

## Iterative alternative：保留舊的那一半

若不適合使用 recursion，可以改為建立逐漸擴大的 prefix 的所有完整 subset。從 `[[]]` 開始。當下一個值是 `x`，保留每個 old row 來表示 exclude `x`，再加入一個新建立的 `old_row + [x]`，表示 include `x`。

```python
def subsets_iterative(nums: list[int]) -> list[list[int]]:
    result = [[]]
    for x in nums:
        old_count = len(result)
        for j in range(old_count):
            result.append(result[j] + [x])
    return result
```

對 `[2, 5]`，處理 2 會把 `[[]]` 改成 `[[], [2]]`。處理 5 時，先固定 `old_count = 2`。當 `j = 0`，`[] + [5]` 建立 `[5]`；當 `j = 1`，`[2] + [5]` 建立 `[2, 5]`。最後得到 `[[], [2], [5], [2, 5]]`。

Python 的 list concatenation 會產生新的 list，不會把值 append 到 old row 裡。`range(old_count)` 提供從 0 到 `old_count - 1` 的 index，所以本次 iteration 新 append 的 row 不會再被處理。即使外層 list 變長，儲存的 count 仍然是 2。Python 文件說明了 [sequence concatenation 與 mutable-sequence iteration](https://docs.python.org/3.14/library/stdtypes.html#common-sequence-operations)，以及 [range endpoint](https://docs.python.org/3.14/tutorial/controlflow.html#the-range-function)。

Loop checkpoint 是：在處理 `x` 之前，`result` 恰好包含已處理 prefix 的所有 subset，各一次。舊的一半不含 `x`；新增的一半包含 `x`，而移除 `x` 就能還原出唯一的 old row。輸入值互異，使這兩半沒有交集。一開始，空 prefix 只有空 subset。每次外層 iteration 完成，都會把 checkpoint 延伸到下一個位置；處理完所有位置，就是要求的結果。

新增 row 的數量是 `1 + 2 + ... + 2**(n - 1) = 2**n - 1`。每個非空的最終 subset 都只建立一次，做法是 copy 它先前的 entry，再加上它的最後一個值。因此，所有 concatenation 恰好寫入前面算出的 `n * 2**(n - 1)` 個 output entry。時間與 returned output space 同樣都是 `Theta(n * 2**n)`。除了 output，loop 只保留少量 control value。它從不 copy 外層 list；old row 仍是最終 output 的一部分。暫時建立的 `[x]` 只有一個 entry，新 concatenated row 在 append 之前則最多有 `n` 個 entry。若把新 row 在 append 之前算作 transient state，peak auxiliary space 為 `O(n)`；若從建立時就把它算入 output，control state 與 singleton-list scratch space 則是 `O(1)`。

這個 alternative 避開了 recursive call 與可變的共用 path，所以當 recursion depth 或禁止 recursion 的要求決定選擇時，它較合適。若未來的限制能在建立全部 completion 之前，就否決一個 partial choice，backtracking 就派得上用場。

## 改變要求：只要大小為 `k` 的 subset

假設值仍互異，但 caller 現在只要恰好包含 `k` 個值的 subset，其中 `0 <= k <= n`。若先產生完整 power set 再 filter，仍會建立全部 `2**n` 個 row。搜尋可以改為在值的數量足夠時停下，或拒絕已不可能達標的 path。

```python
def subsets_of_size(nums: list[int], k: int) -> list[list[int]]:
    n = len(nums)
    result = []
    path = []

    def visit(i: int) -> None:
        if len(path) == k:
            result.append(path.copy())
            return
        if len(path) + (n - i) < k:
            return

        visit(i + 1)
        path.append(nums[i])
        visit(i + 1)
        path.pop()

    visit(0)
    return result
```

Path 與 position 保留原本的意義。現在，`n - i` 是尚未決定的位置數量。當 `len(path) + (n - i) < k`，即使把它們全部 include 也無法成功，因此拒絕這次呼叫不會丟失任何合法答案。當 `len(path) == k`，所有剩餘位置都必須 exclude。儲存一次後停下，就代表了這個唯一的 completion，而不必繼續探索更多 inclusion。兩個 early return 都不改動 `path`，所以 restoration proof 仍適用。程式假設 `k` 符合前述範圍。

對 `[2, 5, 7]` 與 `k = 2`，先 exclude 2 再 exclude 5，會抵達 `i = 2`、`path = []`。只剩一個值尚未決定，所以 `0 + 1 < 2`，這次呼叫被拒絕。若 exclude 2、改為 include 5，則留下 `[5]`；include 7 就會完成 `[5, 7]`。Include 2 的路線最後產生 `[2, 7]` 與 `[2, 5]`。提前成功的條件會阻止三元素的結果。每個大小為 `k` 的 subset 仍然有唯一的 decision route：該 route 的任何 prefix 都不會是不可能的狀態，而一旦選滿 `k` 個值，剩下的 exclusion 就都是確定的。因此，兩個 early return 都保留了 completeness 與 uniqueness。當 `i == n`，必定已成功或已不可能成功，所以不會有程式讀取 `nums[n]`。

令 `C(n, k)` 表示從 `n` 個互異位置中選出 `k` 個的方法數，每個不分順序的選擇只計一次。這就是這裡儲存的 leaf 數量。只有在原本 include/exclude 搜尋也會呼叫 `visit` 的地方，才會發生這裡的呼叫，因此最多有 `2**(n + 1) - 1` 次。Copy 寫入 `k * C(n, k)` 個 entry，建立 list 本身另需 `C(n, k)` 個成本單位。一個合法的 upper bound 是 `O(2**n + (k + 1) * C(n, k))`；這裡刻意不把它稱為對所有 `k` 都 tight 的 bound。計入 active call、path 與 temporary snapshot，auxiliary space 仍是 `O(n)`。Output space 為 `Theta((k + 1) * C(n, k))`，即使 row 為空，也要計入一個 object 與一個外層 reference。當 `k = 0`，第一次呼叫就儲存 `[]` 並停下，只需 constant work。當 `k = n`，唯一能繼續的 route 是 include 每個值；被 exclude 的 sibling 會立刻失敗，因此只有 `O(n)` 次呼叫，以及一次長度為 `n` 的 copy。這些 boundary 說明了提前拒絕 partial path 為什麼可能有用。

## Interview English 與 master map

Why are there no duplicate subsets? Each distinct input value receives one include/exclude decision, and positions are processed in one fixed order. Different decisions change membership of some value.

Why copy the path? The working list is mutated after a leaf returns. A shallow copy gives the saved answer an independent list while safely sharing integer elements.

What does backtracking restore? Every `visit(i)` leaves `path` with exactly its entry contents. Its final `pop()` reverses its own inclusion after its children finish.

Why is time `Theta(n * 2**n)`? There are `2**n` subsets and exactly `n * 2**(n - 1)` element entries in their explicit lists. Saving those entries dominates the call overhead.

When would you choose the iterative version? When recursive calls are unsuitable and all subsets are still required. Its old-prefix checkpoint replaces the recursive path-restoration checkpoint.

這個任務要求每一種 membership 選擇。互異的值與固定的位置順序，讓每個選擇只有一種表示方式。Recursive position 標記尚未完成的決策，path 保留已選取的值，兩個 branch 涵蓋下一個決策。復原 path 保護 sibling search，在完成時 copy 則保護已儲存的答案。Output 數量解釋了指數成本。大小限制改變了哪些 partial choice 仍可能成功，因此允許安全的 early return。
