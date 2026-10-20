# Merge Intervals：何時才能確定 gap 不會再被填補

假設輸入是 `[[8,10],[1,7],[3,4],[7,8],[12,12],[12,14]]`，正確答案是 `[[1,10],[12,14]]`。幾個短 interval 連成第一段，第二段則從一個 gap 之後開始。要可靠地產生這個答案，程式必須能區分：眼前的 gap 已經確定存在，還是後面某個 interval 仍可能把它填起來。

## 什麼才算相同的 coverage？

一個 interval `[start, end]` 包含兩個 endpoint，以及它們之間的每個點。因此 `[1,2]` 和 `[2,3]` 共享 `2` 這個點，必須合併成 `[1,3]`。`[1,2]` 和 `[3,4]` 之間有 gap，應維持分開。endpoint 是整數，不代表 interval 只是一組整數；`2` 到 `3` 之間的 gap 仍然重要。`[12,12]` 這樣的單點 interval 也是合法輸入。

LeetCode 56 接受 `1` 到 `10^4` 個 interval。每個 interval 恰有兩個整數 endpoint，滿足 `0 <= start <= end <= 10^4`，而且不保證輸入順序。結果中的 interval 不能互相 overlap，coverage 又必須與輸入完全相同；把 gap 裡原本未涵蓋的點加進來，就是錯誤。共享 endpoint 也算 overlap，這項規則明列於[題目敘述](https://leetcode.com/problems/merge-intervals/)。

可以把 coverage 理解成「至少被一個 interval 包含的所有點」；數學上稱為 union。對這個任務而言，只要兩份輸入的 union 相同，它們就是等價的。原本的排列順序或重複次數都不影響 union。這是正確答案必須滿足的性質，在選擇 algorithm 之前就已成立。

題目沒有承諾呼叫端希望輸入被重新排列或修改。因此，以下實作會保留輸入 list 的順序與內層 pair，並回傳新的 pair。若輸入為空，它也會回傳 `[]`；不過，空輸入不在題目的 constraints 之內。

## 先排序，才能判定一段 coverage 已經結束

最初可能會想到：每讀到一個 interval，就拿它與最後儲存的 interval 比較。若輸入順序是 `[[5,6],[1,2],[2,5]]`，前兩個看起來彼此分開，第三個卻會把它們連成 `[1,6]`。任意輸入順序下看到的 gap，還不足以證明一個 component 可以定案。這裡的 component 是一整段連續 coverage，由彼此相連的 interval 合併而成；連接也可能透過其他 interval 間接完成。

改成依 start 遞增排序。同一份輸入便成為 `[[1,2],[2,5],[5,6]]`。當 start 只會向右移動時，如果新 interval 的起點已超過目前這段的終點，就能確定後面所有 interval 也都起步太晚，無法再碰到這一段。

設目前這段是 `[left, right]`，下一個排序後的 interval 是 `[start, end]`。排序保證 `left <= start`。若 `start <= right`，兩者相接或 overlap，union 中沒有洞，起點是 `left`，終點是 `max(right, end)`。若 `start > right`，`right` 與 `start` 之間有未被涵蓋的點。此時應保留目前這段，再開啟新的一段。

right endpoint 必須表示整個當前 component 能抵達的最遠位置，不能只記住上一個輸入 interval 的 end。對 `[[1,5],[2,3]]` 而言，若把 `right` 改成 `3`，就會丟掉 `3` 到 `5` 的 coverage。以 interval 數量計算，這是該錯誤的最小 counterexample：只有一個 interval 時，根本不會觸發 merge update。取 maximum 才能避免內含的 interval 把外層 interval 縮短。

兩個 interval 是否 overlap，本身不是 equivalence relation：`[1,2]` overlap `[2,3]`，`[2,3]` overlap `[3,4]`，但 `[1,2]` 並不 overlap `[3,4]`。允許合併成單一 interval `[1,4]` 的原因，是它們能透過一條連接鏈串起來。即使忘記原本有哪些成員，保留 component 的最遠 endpoint，仍保有判斷下一次連接所需的資訊。

## 用最後一個輸出 pair 保存 frontier

以名為 `merged` 的 list，保存目前找到的 component。當中的 pair 依 start 排序，彼此以嚴格的 gap 分隔。最後一個 pair 就是 frontier：下一個 interval 到來時，它還可能延伸。更前面的 pair 則已定案。

為何只需與最後一個 pair 比較？假設較早的 component 結束於 `a`，最後一個 component 始於 `b`，且 `a < b`。後續每個 start 都至少是 `b`，所以不可能向左跨過這個 gap，碰到較早的 component。新 interval 若能碰到任何已存的 component，就只可能是最後一個。因此，不必在每讀一個 interval 後，重新掃描整份輸出。

在 Python 中，`sorted(intervals, key=lambda pair: pair[0])` 會回傳一個新的外層 list。小函式 `lambda pair: pair[0]` 接收一個 pair，回傳它的 start；排序時用來決定先後的值就是這些 start。每個輸入 pair 只會呼叫一次 key function。例如 `[8,10]` 產生 key `8`，`[1,7]` 產生 key `1`，因此 `[1,7]` 會排在前面。這個 algorithm 不需要在 start 相同時再按照 end 排序：無論先處理哪一個，都會透過 maximum 合併。Python 的 stable sort 會保留相同 key 原本的相對順序。[Python sorting 文件](https://docs.python.org/3.14/howto/sorting.html#key-functions)

外層 list 是新的，不代表內層 pair 也是新的。新 list 的 entry 仍指向輸入的 pair object。若程式直接保存其中一個 pair，再修改它的 end，呼叫端也會看見變更。因此，`merged.append([start, end])` 會為每個新 component 建立全新的雙元素 list。整數可以安全共享，因為程式不會修改 integer object，而是替換輸出 pair 中的一個 entry。輸入 pair 全程只被讀取。Python 的 [shallow list copy](https://docs.python.org/3.14/tutorial/datastructures.html#more-on-lists) 並不代表巢狀 object 也各自獨立。

完整的 Python 3 解答如下：

```python
class Solution:
    def merge(self, intervals: list[list[int]]) -> list[list[int]]:
        ordered = sorted(intervals, key=lambda pair: pair[0])
        merged = []

        for start, end in ordered:
            if not merged or start > merged[-1][1]:
                merged.append([start, end])
            else:
                merged[-1][1] = max(merged[-1][1], end)

        return merged
```

`for start, end in ordered` 讀取一個 pair，將它的兩個值分別綁定到區域名稱 `start` 和 `end`。`merged[-1]` 選取最後一個輸出 pair，後面的 `[1]` 再選取該 pair 的 end。對 `merged[-1][1]` 賦值，會替換既有 pair 裡的那個位置；它不會 append 另一個 component，也不會替換整份輸出 list。

處理第一個 interval 時，`merged` 是空的，所以 `not merged` 為 true。Python 的 `or` 在左側 operand 為 true 時就停止，因此不會嘗試 index 尚不存在的最後一個 pair。後續 iteration 才會檢查 gap。這些行為來自[文件中的 truth-value 與 short-circuit 規則](https://docs.python.org/3.14/library/stdtypes.html#boolean-operations-and-or-not)。

`append` 會修改輸出 list，並回傳 `None`；程式使用的是它的效果，而非 return value。若寫成 `merged = merged.append(...)`，變數就會被改成 `None`，導致下一次 iteration 失敗。同樣地，`intervals.sort(...)` 會原地排序呼叫端的 list，並回傳 `None`；它不能直接替換此處使用的 `sorted(...)` expression。[Python list methods](https://docs.python.org/3.14/tutorial/datastructures.html#more-on-lists)

## 跟著一份輸入走完整個程式

以下是推演的 state trace，並非對 interpreter instruction 的量測。從這份輸入開始：

```text
intervals = [[8,10],[1,7],[3,4],[7,8],[12,12],[12,14]]
```

sorting call 會在 loop 開始前執行完畢，回傳：

```text
ordered = [[1,7],[3,4],[7,8],[8,10],[12,12],[12,14]]
merged = []
```

輸入仍維持原本順序。start 相同的 `[12,12]` 和 `[12,14]` 保留原有相對順序。掃描期間，沒有任何 assignment 會修改 `ordered` 或輸入 pair。

第一個 pair 提供 `start = 1`、`end = 7`。由於 `merged` 為空，第一個 branch 會 append 一個新配置的 `[1,7]`：

```text
merged: [] -> [[1,7]]
```

下一個 pair 是 `[3,4]`，最後一個輸出 end 是 `7`。gap test `3 > 7` 為 false，因此進入 `else` branch，計算 `max(7,4)`，回傳 `7`。把這個值寫回後，可見的結果不變：

```text
merged: [[1,7]] -> [[1,7]]
```

這個不變的 state 是必要的：`[3,4]` 沒有增加任何尚未涵蓋的點。

處理 `[7,8]` 時，`7 > 7` 為 false。共享 endpoint 會進入 merge branch。`max(7,8)` 回傳 `8`，既有輸出 pair 因而改變：

```text
merged: [[1,7]] -> [[1,8]]
```

處理 `[8,10]` 時，`8 > 8` 也為 false。下一個 maximum 是 `10`：

```text
merged: [[1,8]] -> [[1,10]]
```

處理 `[12,12]` 時，`12 > 10` 為 true。這裡存在實際的 gap，因此程式 append 一個新 pair，而不是延伸第一個 pair：

```text
merged: [[1,10]] -> [[1,10],[12,12]]
```

後面的 start 都不可能小於 `12`。第一個 component `[1,10]` 現在已不可能再被剩餘 interval 碰到。

最後的 `[12,14]` 與最後一個 component 相接，因為 `12 > 12` 為 false。只有最後的 pair 改變：

```text
merged: [[1,10],[12,12]] -> [[1,10],[12,14]]
```

loop 已讀完所有 pair。`return merged` 回傳 `[[1,10],[12,14]]`；不需要最後再做一次 flush，因為掃描全程中，frontier 一直就在輸出裡。return value 的外層 list 與內層 pair 都不與輸入共享。因此，之後修改輸出的 endpoint，也不會改變輸入。

一個相近的 boundary test 能區分此解答與常見錯誤。對 `[[1,2],[2,3]]` 而言，若將 `start >= last_end` 視為 gap，就會回傳兩個相接的 interval。正確答案卻是 `[[1,3]]`。程式中的嚴格 `>`，正是 closed-endpoint contract 改變 branch 選擇的位置。

## 為何掃描不會遺失或憑空增加 coverage

loop invariant 是在每次 iteration 的同一個 checkpoint 都成立的敘述。這裡的 checkpoint 位於處理下一個排序後的 pair 之前。此時，`merged` 已精確且完全合併地表示 processed prefix：兩者 union 相同，start 遞增，每兩個相鄰輸出 pair 之間都有嚴格 gap。除了最後一個 pair 之外，其他 pair 即使考慮尚未讀取的輸入，也都已定案。

這與前面談到的 task-equivalence property 不同。union 相等是在描述什麼答案可被接受；invariant 還描述了中途的 state，以及未來工作能改變哪些部分。

初始化時，processed prefix 與 `merged` 都是空的。兩者都不涵蓋任何點，也沒有 pair 會違反順序或 gap 條件。

要證明 maintenance，假設下一個 pair `[start,end]` 到來。若輸出為空，加入一份新 copy 就能精確表示第一個 pair。否則，排序保證 `start` 不早於最後一個 component 的起點。若 `start` 不大於其終點，兩個 interval 就有交集。將該終點替換為兩者的 maximum，便精確表示它們的 union：只增加新涵蓋的點，不留下洞。左側 endpoint 不變，因此不會破壞它與更早 component 之間的 gap。

若 `start` 大於最後一個 end，append 會同時保留精確 coverage 與嚴格 gap。所有尚未讀取的 interval，其 start 都至少等於 `start`，無法再從左邊填補這個剛確立的 gap。原本最後的 component 現在也能歸入已定案的 component。這些情況都保留 invariant。

termination 時，processed prefix 已是整份輸入。invariant 保證 coverage 完全相同，而且輸出 component 之間有嚴格 gap。因此，任兩個輸出 interval 都不會 overlap，也沒有任何 covered point 被遺失或憑空加入。loop 會結束，因為它只會逐一走訪有限 sorted list 中的每個元素一次。

## 算進 sorting 與 append 隱藏的工作

令 `n` 為輸入 interval 數量，`k` 為輸出 component 數量，因此 `k <= n`。Big O 描述成長上界，忽略固定倍數與少量固定開銷。`O(n)` 表示工作量不超過輸入大小的某個固定倍數；`O(n log n)` 則多乘上一個隨 logarithm 成長的因子。這些敘述描述 operation count，並非經過多少秒。

在這裡，把 endpoint comparison、indexing 與替換 list entry 都視為 constant work。題目把 endpoint 限制在 `10^4` 以內，所以 integer 大小有界。sorting key 每個 pair 讀取一個 endpoint，帶來 `O(n)` 工作。掃描走訪 `n` 個 pair，每次進行固定數量的 test、read 與 maximum comparison，最多再做一次 append。

append 偶爾可能需要較大的 storage area，並複製既有 reference。因此，不能說每一次 append 都只花 constant time。在 CPython v3.14.0 中，list storage 會預留與目前大小成比例的額外 capacity。多次擴充所複製的 capacity 形成 geometric progression：從後往前看，較早的 capacity 會按固定比例縮小。總和便不超過最終 capacity 的某個固定倍數。因此，全部 `k` 次 append 合計花費 `O(k)`，稱為每次 append 的 amortized constant cost。這是對整段操作序列的上界，並不是假設偶爾昂貴的 append 不會發生。[CPython list growth 實作](https://github.com/python/cpython/blob/v3.14.0/Objects/listobject.c#L111-L121)

sorting 決定 worst-case time 的主要成長。CPython v3.14.0 採用 adaptive merge sort：先找出已排序的片段，稱為 run，再把它們合併。要理解 logarithm 的來源，可以先看合併等長 run 的概念情況。每一輪讓 run size 加倍：`1, 2, 4, 8, ...`。到達 `n` 大約需要 `log2(n)` 輪；`log2(8) = 3`，因為從 `1` 加倍三次就得到 `8`。每一輪合併 run，合計最多檢查線性數量的 item，因此工作量是 `O(n log n)`。CPython 使用更複雜的 merge schedule，而非完全照這幾輪進行，但仍保有 worst-case `O(n log n)` 上界。原有的 ordered run 可以減少工作量。這是在解釋成本，並不是說實作真的會把每份輸入拆成單一 item。[CPython sorting 設計](https://github.com/python/cpython/blob/v3.14.0/Objects/listsort.txt)

將 sorting 與掃描相加，隨著 `n` 成長，worst-case time 為 `O(n log n)`；`n = 1` 時則只需 constant work。畫面上只有一個 loop，不代表整個函式就是 linear：`sorted` 在該 loop 之前已經執行了自己的工作。

回傳結果占 `O(k)` space：一個外層 list，加上 `k` 個新 pair，每個 pair 都固定只有兩個元素。扣除輸入與回傳結果，auxiliary space 仍為 `O(n)`。`ordered` 包含 `n` 個 reference，sorting 還可能保存數量與 `n` 成比例的 key 及 temporary merge storage。sorting 結束後，這些 temporary structure 就不再需要，但 `ordered` 會一直存留到掃描期間。掃描本身除了輸出以外，只需固定數量的 local reference。包含回傳結果的 peak extra space 為 `O(n + k) = O(n)`。改用 in-place `list.sort` 可以省去外層 list 的 copy，但這不足以支持「CPython sorting 的 auxiliary space 一般是 `O(1)`」這種主張。[CPython key allocation](https://github.com/python/cpython/blob/v3.14.0/Objects/listobject.c#L2770-L2793) 與 [merge storage](https://github.com/python/cpython/blob/v3.14.0/Objects/listsort.txt#L14-L18)

## 輸入本來就有順序時

若改變後的 contract 保證 start 不遞減，就可以移除 sorting call，直接依該順序掃描。同一份 proof 仍成立，因為所需的順序前提現在由呼叫端提供。在相同的 primitive-cost assumption 下，time 變成 `O(n)`。

這也允許 streaming：只保留一個 pending `[left,right]` pair，相接時延伸它，出現嚴格 gap 時就 emit。輸入結束時，再 emit 最後一個 pending pair。emit 是把已完成的 pair 交給 consumer，而不是將全部已完成 pair 保存在 list 裡。這個版本除了 input stream 與 consumer 自己儲存的資料之外，只需 `O(1)` working state。若 API 仍要求回傳 list，保存 `k` 個結果依然需要 `O(k)` space。

這項保證不可省略。unsorted stream 可能在某個 component 已經 emit 之後，才送來用於連接的 interval；`[[5,6],[1,2],[2,5]]` 就已展示這個問題。原始 contract 允許任意輸入順序，因此這裡選擇先 sorting，以免反覆回頭檢查已保存的 component。排列 interval 的成本，換來的是每個 component 只需定案一次。

## English interview rehearsal

Why sort by start? Sorting makes future starts nondecreasing. Once a new start exceeds the current end, no later interval can bridge the gap.

Why keep the maximum end? The last output pair represents a whole connected component. A contained interval must not shorten its furthest reach.

Why does equality merge? The intervals are closed. Two intervals with a shared endpoint intersect at that point.

What is your invariant? Before each iteration, the output is the fully merged union of the processed prefix, ordered with strict gaps. Earlier components are final; only the last may grow.

What are the costs and mutation effects? Worst-case time is `O(n log n)`, auxiliary space is `O(n)`, and returned output uses `O(k)` space. The implementation preserves the input and creates new output pairs.

## Master Map

closed endpoint 讓相等邊界也成為 overlap。任意輸入順序，讓眼前的 gap 只能暫定；依 start sorting 之後，未來 start 只會向右，嚴格 gap 才能確定不會再被填補。最後一個輸出 pair 因而保存唯一還可能延伸的 component，取 maximum end 則保留它的完整 coverage。新的輸出 pair 讓這些 update 不會碰到呼叫端的輸入。prefix invariant 把每一步 local update 連到所需的最終 union。sorting 的成本換來這個 one-pass decision rule；若輸入原本已有順序，就能直接取得這項規則，省下 sorting 成本。
