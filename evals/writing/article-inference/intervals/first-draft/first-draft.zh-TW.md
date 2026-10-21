# Merge Intervals：為什麼排序後只剩最後一段尚未定案

先依左端點排序所有區間，再按照這個順序走訪，用一個 list 保留合併結果。每個新區間不是延伸結果的最後一段，就是另開一段。這個方法成立的理由，比「相鄰區間比較方便」更明確：一旦出現間隙，後面的起點就不可能往回跨過它。

## 結果必須保留什麼？

在 [LeetCode 56, Merge Intervals](https://leetcode.com/problems/merge-intervals/) 中，每組輸入 `[start, end]` 表示一個 closed interval：從 `start` 到 `end` 的所有位置，包含兩端點。輸入有 1 到 10,000 組區間，整數端點符合 `0 <= start <= end <= 10000`。將重疊部分合併後，回傳互不重疊的區間。回傳結果覆蓋的位置必須恰好等於輸入覆蓋的位置。若直接用一個大區間包住全部輸入，就會錯誤填滿原本的間隙。

例如，`[1,4]` 和 `[4,6]` 都包含位置 `4`，所以要合成 `[1,6]`。但 `[1,4]` 和 `[5,6]` 之間有間隙，必須分開。端點是整數，不代表區間只包含整數位置。長度為零的區間，例如 `[12,12]`，仍然覆蓋它的端點。題目範例明確把端點相接視為重疊。[原題與邊界範例](https://leetcode.com/problems/merge-intervals/)。

輸入順序沒有提供可利用的保證。能連接另外兩段的區間，可能在那兩段之後才出現。我們會依起點遞增順序回傳結果，並保留呼叫端的輸入不變；保留輸入是這份實作的選擇，並不是題目明訂的要求。

## 哪一種順序能讓決策定案？

假設目前合併區間是 `[left, right]`，下一個區間是 `[start, end]`。如果起點按遞增順序到來，就有 `left <= start`。每組輸入又都符合 `start <= end`，因此只剩兩種情況。

若 `start <= right`，新區間接上了目前的覆蓋範圍。兩者的 union 是 `[left, max(right, end)]`：保留較早的左端點，右端點則取伸得比較遠的那一個。完全內含於目前區間的新區間，不會增加任何覆蓋位置。若一律指定 `right = end`，就可能錯誤縮短覆蓋範圍。

若 `start > right`，兩段之間有間隙。後面所有區間的起點都至少和 `start` 一樣靠右，因此不可能與 `[left, right]` 重疊，也無法跨回這個間隙。目前這段已經定案。從 `[start, end]` 另開一段。

這個順序也解釋了為什麼只需檢查結果的最後一段。更早的結果區間，早已結束在掃描曾跨過的間隙之前。目前與未來的起點都位於那些間隙之後。最後一段可以繼續往右延伸，但它的左端點不會往回移動，接上更早的結果區間。

```text
Unordered input
    -> order by start
    -> inspect the last merged interval
         start <= last end -> keep left, extend right if needed
         start >  last end -> finish last, append a new interval
    -> return the merged list
```

依起點排序，是取得所需順序的一種方式；這不表示所有正確演算法都必須排序。真正允許我們做決定的條件，是未來的起點不會小於目前正在處理的起點。

## Python 狀態各自代表什麼？

用 `ordered` 表示依起點排好的 list，用 `merged` 表示部分答案。`merged` 裡的一組端點，代表已處理區間中一整個相連群組的覆蓋範圍，不一定是某個原始輸入區間。`merged[-1]` 選取最後一組端點，`merged[-1][1]` 再選取那組的右端點。前面各段已經定案，最後一段還可能繼續長大。

排序運算式是 `sorted(intervals, key=lambda interval: interval[0])`。`lambda` 是一個小函式：給它一組端點，它就回傳第一個數字。排序會把這些數字當作比較用的 key。因此 `[8,10]` 的 key 是 `8`，`[1,4]` 的 key 是 `1`。Python 對每組輸入只計算一次 key，並回傳依 key 遞增排列的新外層 list。對這個演算法來說，相同起點的區間用哪個順序都可以：保留較大的右端點，就會得到相同的 union。[Python sorting 文件](https://docs.python.org/3/howto/sorting.html#key-functions)。

外層 list 是新的，不代表內層的端點組也是新的。新 list 的元素仍然參照原本的端點組物件。加入答案區間時，`merged.append([start, end])` 會建立一個新的兩元素 list，並把指向它的 reference 放到 `merged` 尾端。因此，之後更新端點時，改的是答案中的端點組，並不是輸入中的端點組。若直接 append 原始端點組再修改，呼叫端也會看到這個變動。Python assignment 綁定的是 reference，並不會複製物件；list 的元素可以原地修改。[Python lists 與 assignment](https://docs.python.org/3.14/tutorial/introduction.html#lists)。

## Program Movie：內含、延伸、相接與間隙

考慮這組自行構造的輸入：

```text
intervals = [[8,10], [1,4], [2,3], [3,6], [6,8], [12,12]]
ordered   = [[1,4], [2,3], [3,6], [6,8], [8,10], [12,12]]
merged    = []
```

呼叫 `sorted` 會產生 `ordered`，不會重新排列 `intervals`。掃描依序走訪 `ordered` 裡的每組端點，把兩個數字分別綁定到 `start` 與 `end`。

處理 `[1,4]` 時，答案還沒有最後一組端點。建立 `[1,4]` 並 append，答案就成為 `[[1,4]]`。答案是空的時候，不需要讀取任何既有端點。

處理 `[2,3]` 時，把 `2` 和最後一段的右端點 `4` 比較。兩段重疊，但 `max(4,3)` 是 `4`。把這個值寫回後，`merged` 仍然是 `[[1,4]]`。這是內含情況；若把右端點改成 `3`，就會失去 `3` 到 `4` 之間的覆蓋範圍。

處理 `[3,6]` 時，因為 `3 <= 4`，所以把 `max(4,6)`，也就是 `6`，寫入最後一組端點的結束位置。`merged` 變成 `[[1,6]]`。儲存的左端點仍然是 `1`，因為排序已經確保新區間的左端點不會更小。

處理 `[6,8]` 時，起點恰好等於已儲存的終點。這兩個 closed intervals 共有位置 `6`，所以寫入 `max(6,8) = 8`，答案變成 `[[1,8]]`。處理 `[8,10]` 時，同樣的相接規則會把它延伸成 `[[1,10]]`。

處理 `[12,12]` 時，`12 > 10`。兩者有間隙，因此 append 新建的 `[12,12]`，而不修改 `[1,10]`。`merged` 變成 `[[1,10], [12,12]]`。迴圈接著耗盡輸入，回傳這個 list。最後一段已經存在答案中，因此不必在最後再做一次 flush。

```text
[]
  -- [1,4]: first pair --> [[1,4]]
  -- [2,3]: contained --> [[1,4]]
  -- [3,6]: extends   --> [[1,6]]
  -- [6,8]: touches   --> [[1,8]]
  -- [8,10]: touches  --> [[1,10]]
  -- [12,12]: gap     --> [[1,10], [12,12]]
```

## 完整 Python 實作

```python
from typing import List


class Solution:
    def merge(self, intervals: List[List[int]]) -> List[List[int]]:
        ordered = sorted(intervals, key=lambda interval: interval[0])
        merged: List[List[int]] = []

        for start, end in ordered:
            if not merged or start > merged[-1][1]:
                merged.append([start, end])
            else:
                merged[-1][1] = max(merged[-1][1], end)

        return merged
```

當 list 是空的，`not merged` 就是 true。Python 的 `or` 一旦左邊成立就會停止求值，所以第一次迭代不會對空 list 執行 `merged[-1][1]`。第一次 append 之後，第二個條件負責檢查嚴格間隙。因此 `else` 包含端點相等的情況，`max` 則回傳目前終點與新終點中較大的值。[Python truth testing 與 short-circuit evaluation](https://docs.python.org/3.14/library/stdtypes.html#boolean-operations-and-or-not)。

type hints 描述的是巢狀整數 lists；它們不會在執行時驗證輸入，也沒有規定每個內層 list 必須剛好有兩個元素。兩端點要求來自題目契約。對空輸入，這個方法也會回傳 `[]`，不過空輸入不在 LeetCode 明訂的限制範圍內。

## 為什麼部分答案一直正確？

在每次迭代剛結束的檢查點，使用這個 English loop invariant："`merged` contains the exact union of the processed intervals as start-ordered, non-overlapping intervals; all but its last interval are final against every unprocessed interval." 這裡的 union，表示至少被一個區間覆蓋的所有位置。union 性質描述結果必須保留的覆蓋範圍；loop invariant 還進一步指明，部分答案在哪個時點成立，以及哪些部分不會再改變。

還沒處理任何區間時，空答案恰好覆蓋空的已處理集合。此時沒有任何已定案的端點組會違反 loop invariant。第一次迭代建立初始區間，而單一區間本身就是它的完整 union。

遇到重疊時，把 `[left,right]` 換成 `[left,max(right,end)]`，增加的恰好是新區間帶來的位置。因為 `start <= right`，替換後的區間內部不會出現間隙。它的左邊界不變，所以仍然和更早的所有答案區間分離。較晚到來的起點也不可能回頭接上更早的端點組。因此 loop invariant 仍然成立。

遇到嚴格間隙時，append `[start,end]` 會保留所有既有覆蓋，再加入恰好等於新區間的範圍。新區間和原本最後一組端點分離，因此也和更左邊的端點組分離。未來起點都至少是 `start`，所以原本最後一組端點現在已經定案。新加入的端點組成為唯一尚未定案的一段。

每次迭代會消耗有限 `n` 組輸入中的一組。迴圈終止時，所有端點組都已處理，因此精確覆蓋與兩兩不重疊的性質適用於完整輸入，`merged` 就是所需答案。「尚未定案」指的是未來還可能延伸，並不是輸出資料還沒存入。

一個容易犯的錯，是把新起點和前一個原始區間的終點比較。對 `[[1,10], [2,3], [4,5]]` 而言，這樣會拿 `4` 和 `3` 比較，憑空認定有間隙。目前群組其實已經覆蓋到 `10`，所以三段都屬於 `[1,10]`。答案必須記住整個群組已到達的最大右端點，而 `max` 更新正是維護這個資訊。

省略排序也會破壞推理。對 `[[5,6], [1,2]]`，同一份程式會看到 `1 <= 6`，保留 `[5,6]`，因而遺失 `[1,2]`。合併公式原本假設已儲存的左端點比較早。無論公式或 loop invariant，都沒有允許在任意輸入順序下這樣使用。

## 時間與記憶體成本從哪裡來？

令 `n` 為輸入區間數量，`k` 為回傳區間數量，且 `k <= n`。把有界端點的一次比較、一次 reference 讀寫，以及建立固定兩個位置的端點組，都視為常數工作。這裡的端點是有界整數，因此模型不包含任意長度整數的運算成本。Big O 描述忽略常數倍後的成長上界；`O(n)` 表示輸入加倍時，這個上界也按兩倍成長。

掃描會走訪 `n` 組端點。每次迭代都只做固定上限次數的端點讀取、比較與寫入。它從不搜尋整個 `merged`；選取最後一個位置，直接使用的是已知位置。最多建立 `n` 組新端點，最後有恰好 `k` 組留在結果中。

list append 的成本需要合計來看。Python list 把 references 放在帶有備用位置的 array 中。大部分 append 只需填入一個備用位置。容量用完時，擴容可能配置更大的 array，並複製既有 references。CPython 會依大小比例預留額外容量，不會每次 append 都複製。從最後容量 `C` 往回看，較早的大容量都有一個上界：不超過下一次容量的固定比例 `r < 1`。以每次加倍為示意，`r = 1/2`。總複製 reference 數量不超過 `S = C + rC + r^2 C + ... + r^m C`。減去 `rS` 後，中間項全部消去，得到 `S - rS = C - r^(m+1) C <= C`。因此 `S <= C/(1-r)`。固定比例只貢獻常數倍，而按比例預留容量，讓 `k` 次 append 的最後容量符合 `C = O(k)`。最初幾次小配置只增加固定工作。再加上 `k` 次一般位置寫入，總 append 工作就是 `O(k)`，即使某一次 append 可能超過常數時間。這就是 amortized cost 的意思。CPython 實際擴容的幅度比每次加倍小。[CPython 3.14 list 擴容實作](https://github.com/python/cpython/blob/v3.14.0/Objects/listobject.c#L98-L126)。

最壞時間成本主要來自排序。這裡分析 CPython 的 adaptive merge-based sort；它會辨識已排序的連續片段，也就是 runs，再合併相鄰 runs。要理解 `n log n` 的尺度，可以先看一個概念性的平衡合併計畫。合併長度為 `a` 與 `b` 的已排序片段，需要 `O(a+b)` 工作：比較兩邊最前面的元素，移動較小者，然後往前推進那一邊的位置，直到兩邊都耗盡。兩個位置都不會往回走。同一層中，每個輸入元素只屬於一次合併，因此整層工作是 `O(n)`。片段大小按 `1,2,4,8,...` 成長；加倍 `h` 次後，大小會到 `2^h`。要達到 `n`，大約需要 `log2(n)` 次，所以每層 `O(n)`，乘上 `O(log n)` 層，就得到 `O(n log n)`。

平衡圖像只是概念模型；CPython 3.14 實際使用 natural runs 與 Powersort merge schedule。這個排程的層數同樣按對數成長。想像把 `n` 個輸入位置先切成兩半，再切成四份、八份。每個相鄰 run 之間的邊界，都指定為「第一次把兩個 run 中點分開」的細分層級。非空相鄰 runs 的中點至少相隔一個位置。一旦每格寬度 `n/2^h` 降到一，這些中點必定已經分開，因此邊界層級大約以 `log2(n)` 為上界。排程會先合併較深的邊界，再跨越較淺的邊界。沿著某個元素經歷的合併路徑，層級會下降，不會在同一層反覆計費。最後清理時，也只剩對數數量的待處理層級。因此，把每次合併的 `O(a+b)` 工作分攤到參與元素，就得到 `O(n log n)` 的總合併工作。這是成本計算，並不是聲稱 Program Movie 執行了這些內部合併。

計算 keys 與辨識 runs 另外增加線性工作。CPython 也會用 insertion 延長過短的 runs，但目標 run 長度最多是 64，所以每個插入元素只會跨過固定上限的位置數，這部分也只增加線性工作。每個邊界層級的計算，最多使用相同的對數次細分，而邊界數量不超過 `n`。因此排序步驟的最壞成本仍為 `O(n log n)`；既有順序可能減少工作。再加上 `O(n)` 的區間掃描，上界維持不變。[CPython sorting 設計與 merge strategy](https://github.com/python/cpython/blob/v3.14.0/Objects/listsort.txt#L327-L428)。

回傳輸出占用 `O(k)` 空間：一個外層 list，以及 `k` 個新建的兩元素端點組，包含按比例預留的容量。即使不計輸出，所選實作仍使用 `O(n)` auxiliary space。`ordered` 持有 `n` 個 references，排序還可能保留與 `n` 成比例的 keys 與暫存 reference 空間。迴圈變數只占常數空間。與輸入共用的物件，不會因為 `ordered` 是新的，就變成另外配置的 `n` 組端點。包含輸出在內的額外儲存峰值是 `O(n+k)`；由於 `k <= n`，也就是 `O(n)`。

若改呼叫 `intervals.sort(...)`，可以省下獨立的已排序外層 list，但會重排呼叫端的 list。這並不能證明 auxiliary space 是常數：Python 排序需要的 workspace 仍可能隨 `n` 成長。只改變是否允許修改輸入，不會消除這個成本。[Python sorting 行為](https://docs.python.org/3/howto/sorting.html#sorting-basics)、[CPython sorting 記憶體](https://github.com/python/cpython/blob/v3.14.0/Objects/listsort.txt#L12-L25)。

## 替代方案，以及會改變選擇的條件

另一種較直觀的排序建構方法，是 repeated selection。保留輸入，並為每組端點準備一個 Boolean「是否已使用」標記。每次掃描所有尚未使用的端點組，找出剩餘起點最小的一組，將它標記為已使用，再把它的端點送入同一套合併規則。每次搜尋過程只需保留目前選中的索引與最佳起點。遇到相同起點，選擇順序仍然不影響正確性，因為終點更新會保留最大值。

這個方法產生的起點順序同樣不遞減，因此前面的正確性證明仍適用於合併步驟。但反覆尋找下一組端點，成本較高。若每次選取都檢查 `n` 個標記，共選取 `n` 次，就有 `n*n` 次標記檢查。即使某個版本只掃描剩餘候選，也仍要檢查 `n + (n-1) + ... + 1` 組。把第一項與最後一項配對，每組總和都是 `n+1`，因此得到 `n(n+1)/2`，按平方成長。這個替代方案需要 `O(n^2)` 時間、`O(n)` 的標記 auxiliary space，以及 `O(k)` output space；新建端點組與 append 的推導沿用前面相同的論證。它可以不依賴 sorting library，但不會改善這題的最壞資源上界。

如果改變輸入契約，保證區間本來就按起點不遞減的順序到來，實用的調整就是完全省略排序。把每組到來的端點直接送入同一套合併規則。此時排序前提改由輸入提供者保證；間隙證明與最大右端點更新都不變。仍然只有 `n` 次走訪與最多 `n` 次 append，所以掃描時間是 `O(n)`。沒有 `ordered` list，也沒有 sort workspace，因此保留 `O(k)` 結果之外，只需要 `O(1)` auxiliary state。要保留呼叫端的端點組不變，仍然必須建立新的答案端點組。當已排序輸入的保證可靠時，這個版本比較合適；只看到幾組已排序範例還不夠。

## English interview practice

Why sort by the start? "It makes future starts nondecreasing. After a strict gap, no future interval can connect to the interval we just finished."

Why keep the maximum end? "The last answer pair represents an entire overlapping group. A contained interval must not shorten that group's coverage."

Why is equality overlap? "The intervals are closed. If a start equals the current end, both intervals contain that endpoint."

What are the costs? "For this Python implementation, sorting costs worst-case O(n log n), and the scan costs O(n) including amortized appends. Auxiliary space is O(n), plus O(k) output space."

What would change for sorted input? "I would remove the ordering step, keep the same merge rule, and obtain O(n) time with O(1) auxiliary state excluding the output."

## Master Map

```text
Closed intervals -> equality shares coverage -> merge at start <= last end
Unordered starts -> sort by start -> future starts never move backward
Processed coverage -> merged pairs -> only the last pair can still extend
Overlap -> preserve left and max end -> exact union without shrinking
Strict gap -> append fresh pair -> previous pair becomes final
Fresh answer pairs -> mutate output endpoints -> preserve input pairs
Sort + one scan -> O(n log n) worst-case time
Ordered references + sort workspace -> O(n) auxiliary space
k answer pairs -> O(k) output space
Guaranteed sorted input -> omit ordering -> O(n) time, O(1) auxiliary state
```
