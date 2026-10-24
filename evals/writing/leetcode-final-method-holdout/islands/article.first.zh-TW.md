# Number of Islands：標記每個格子，每個區域只計數一次

兩個陸地格子即使沒有直接接觸，也可能屬於同一座島。只要能沿著陸地走到彼此即可，而且路線可以轉彎。因此，數格子、數橫向連續的陸地，或數看得見的角落，都不能直接回答有幾座島。

可以先找一個陸地格子，記錄從它出發能到達的所有陸地，再把整個區域算成一座島。接著繼續尋找先前搜尋尚未記錄的陸地。這份發現紀錄必須能防止同一個區域被重複計數。

## 地圖允許怎麼走

在 [LeetCode 200](https://leetcode.com/problems/number-of-islands/) 中，`grid` 是由多個 row 組成的長方形地圖。每個格子包含字串 `"1"`，代表陸地，或字串 `"0"`，代表水。row 數與 column 數都介於 1 到 300。答案是一個整數：地圖上有幾座分離的島。陸地格子必須共用水平或垂直的邊才會相連；只在角落接觸不算相連。長方形外面都視為水。

用 `(r, c)` 表示一個格子的 row 與 column，兩者都從零開始。例如，`(1, 3)` 是第二個 row 的第四個格子。land path 是一串陸地格子，其中每一對前後相鄰的格子都共用一條邊。兩個格子屬於同一座島，若且唯若有這樣的 path 連接它們。一個格子可以透過零次移動的 path 連到自己；反轉 path 仍然相連，把兩條 path 接起來也能延伸連接關係。因此，陸地會分成不同的群組，群組之間沒有 land path。這些群組也叫做 connected components。

全部是水時回傳 0；只有一個陸地格子時回傳 1。整個長方形都是陸地時，不論有多少格也只回傳 1。`[["1", "0"], ["0", "1"]]` 中的兩個陸地格子回傳 2，因為它們只有對角接觸。empty grid 不在題目的輸入契約內，因此下方解法直接讀取 `grid[0]`，沒有先檢查是否為空。

這個解法保留呼叫端傳入的地圖。它另外記錄已發現的格子，因此不必要求呼叫端允許覆寫陸地。解法不回傳面積、座標或每座島的標籤。

## Scan 找起點，search 標記整座島

依照 row 的順序讀取地圖，每個 row 都從左向右。水不能作為島的起點。已發現的陸地也不能作為新島的起點，因為先前的 search 已經標記過它。當 scan 找到尚未發現的陸地，就把 `count` 加一，再從那裡搜尋，直到沒有可到達但尚未發現的陸地。

為什麼一定要完成這次 search，才能繼續 scan？考慮以下自訂地圖，為了閱讀方便，把字串簡寫成數字：

```text
1 0 1
1 1 1
```

這裡只有一座島：下方的 row 把上方兩個格子連在一起。一個容易想到的規則是：「若某個陸地格子的上方和左方都不是陸地，就把島數加一。」這個規則會把上方的兩個格子分別計數，回傳 2。連接它們的陸地，要到 scan 稍後才會出現。只查看已掃描的鄰居，不足以斷定這一定是一座新島，除非 algorithm 還知道如何合併先前的群組。直接搜尋整個可到達區域，就能省下這套合併機制。

發現紀錄使用 Boolean `seen[r][c]`：`True` 表示這個格子已被某次 search 標記。它不代表這個格子的所有鄰居都已檢查完。這個區別讓尚未完成的工作有了明確的位置。

尚未完成的工作放在 `stack`，這是一個 list，裡面是等待檢查鄰居的座標。stack 採取 last-in, first-out：最後加入的座標最先被處理。這種搜尋稱為 iterative depth-first search，簡稱 DFS。它通常先沿著新發現的分支往下走，之後才回來處理較早等待的格子。只要最終會檢查每個已發現的格子，任何 pending-cell order 都能用來計算這個數量。

發現一個陸地格子時，立即把它的 `seen` 設為 `True`，再把座標放進 stack。在發現當下標記，可以避免其他鄰居趁它還在等待時，再次把它排進 stack。從 stack 取出一個座標後，檢查它周圍的四個位置。只有位於長方形內、是陸地，而且尚未發現的鄰居，才需要排進 stack。

## Python objects 分別保存哪些狀態

發現紀錄需要讓每個格子都有一個可獨立寫入的 Boolean entry：

```python
seen = [[False] * cols for _ in range(rows)]
```

`[False] * cols` 建立一個包含 `cols` 個 entry 的 row，初值全部是 `False`。comprehension 會為每個 row 重新執行一次建立 row 的 expression，因此得到彼此分離的 row lists。變數 `_` 的值不會被使用。若有兩個 row、三個 column，初值看起來會是 `[[False, False, False], [False, False, False]]`。

row lists 必須彼此分離。看起來更短的 `[[False] * cols] * rows`，會重複保存指向同一個 row 的 references。這時修改 `seen[0][0]`，也會改變 `seen[1][0]` 讀到的值。我們採用的寫法只共用不可修改的 Boolean values，沒有共用可修改的 row lists。Python 文件說明了這項 [sequence repetition 行為](https://docs.python.org/3.14/library/stdtypes.html#common-sequence-operations)。

`seen[nr][nc] = True` 會替換某個 row 裡的一個 entry。它不會改變 `grid`，也不是去修改 `False` object 本身。`(0, 1)` 這樣的座標是一個 two-item tuple，保存 row number 與 column number。把這兩個數字存成一對，就能讓它們共同代表一項等待中的工作。稍後的 `r, c = stack.pop()`，會把這一對的第一個 item 放進 `r`，第二個放進 `c`；這叫做 [assignment unpacking](https://docs.python.org/3.14/reference/simple_stmts.html#assignment-statements)。

若 stack 是 `[(0, 1), (1, 0)]`，`stack.pop()` 會回傳 `(1, 0)`，並讓 list 剩下 `[(0, 1)]`。接著執行 `stack.append((1, 1))`，list 就會變成 `[(0, 1), (1, 1)]`。`append` 回傳 `None`，所以應該單獨執行這個 statement；若把它的回傳值重新指定給 `stack`，就會失去原本的 list reference。這兩個操作都不會複製 grid。這些行為都有記錄在 [Python list stack operations](https://docs.python.org/3.14/tutorial/datastructures.html#using-lists-as-stacks) 文件中。

`while stack:` 會在還有等待中的座標時繼續執行。empty list 在條件判斷中為 false，因此 loop 會在對 empty stack 呼叫 `pop()` 之前停止。檢查鄰居時，先確認 bounds，再使用 index。Python 接受負的 list index，因此若沒有檢查 row `-1`，它會讀取最後一個 row，而不是表示地圖外的水。在 `and` expression 中，Python 遇到第一個 false 條件就會停止求值；把 bounds 放在前面，可以避免用無效位置讀取 grid。這些規則來自 Python 的 [truth-value 與 Boolean operation semantics](https://docs.python.org/3.14/library/stdtypes.html#boolean-operations-and-or-not)。

## 跟完一次完整的搜尋

假設輸入如下：

```text
       c=0 1 2 3
r=0     1 1 0 0
r=1     1 1 0 1
r=2     0 0 1 1
```

左上角的正方形是一座島。右下角附近的三個格子組成另一座島；`(1, 1)` 與 `(2, 2)` 不會因為對角接觸而相連。預期答案是 2。

一開始 `count = 0`，每個 `seen` entry 都是 `False`，也還沒有使用中的 stack。scan 到達 `(0, 0)`，看到尚未發現的陸地，便把 `count` 改成 1，標記 `(0, 0)`，並初始化 `stack = [(0, 0)]`。

這份 trace 與程式都固定依照上、右、下、左的順序檢查鄰居。pop 出 `(0, 0)` 後，stack 剩下 `[]`。上方 `(-1, 0)` 不在 bounds 內。右方 `(0, 1)` 是尚未發現的陸地，因此標記並 append。下方 `(1, 0)` 也是尚未發現的陸地，同樣標記並 append。左方 `(0, -1)` 不在 bounds 內。現在 `stack = [(0, 1), (1, 0)]`；被標記的格子恰好是 `(0, 0)`、`(0, 1)` 與 `(1, 0)`。

下一次 `pop()` 回傳 `(1, 0)`，stack 剩下 `[(0, 1)]`。它的上方鄰居 `(0, 0)` 已被標記。右方鄰居 `(1, 1)` 是新的陸地，因此標記並 append。下方 `(2, 0)` 是水，左方 `(1, -1)` 在地圖外。stack 變成 `[(0, 1), (1, 1)]`，正方形的四個格子現在都已標記。

pop 出 `(1, 1)` 後，stack 剩下 `[(0, 1)]`。上方 `(0, 1)` 已被標記，雖然它本身還沒有開始檢查鄰居。右方 `(1, 2)` 與下方 `(2, 1)` 是水；左方 `(1, 0)` 已被標記。這次不會 append 任何座標。最後 pop 出 `(0, 1)`：上方在地圖外，右方是水，下方與左方都已標記。stack 變空。這次 search 恰好標記整個正方形，`count` 仍然是 1。

這個正方形也顯示了為什麼要在排程時標記。若延後到 pop 時才標記，當 `(1, 1)` 檢查上方鄰居時，`(0, 1)` 仍然看起來像尚未發現。stack 就可能變成 `[(0, 1), (0, 1)]`。設計周全的 delayed-marking algorithm 可以稍後拒絕重複的 entry，但需要額外規則。這個解法直接防止重複 entry 進入 stack。

row scan 繼續。它略過已標記的 `(0, 1)`、是水的 `(0, 2)` 與 `(0, 3)`、已標記的 `(1, 0)` 與 `(1, 1)`，以及是水的 `(1, 2)`。到達 `(1, 3)` 時，它找到新的陸地，便把 `count` 改成 2。標記並 push `(1, 3)`。pop 出它時，只會發現 `(2, 3)`；pop 出 `(2, 3)` 時，只會發現 `(2, 2)`；pop 出 `(2, 2)` 時，不會發現任何新格子。每次都是先移除被 pop 的座標，才 append 新座標，因此每輪檢查完鄰居之後，stack 依序是 `[(2, 3)]`、`[(2, 2)]`、`[]`。

剩下的 scan 位置中，`(2, 0)` 與 `(2, 1)` 是水，`(2, 2)` 與 `(2, 3)` 已被標記。回傳 2。最終的 `seen` 值如下：

```text
True  True  False False
True  True  False True
False False True  True
```

水仍然沒有被標記。輸入的 grid 保留原本的字串。

## 完整解法

```python
class Solution:
    def numIslands(self, grid: list[list[str]]) -> int:
        rows = len(grid)
        cols = len(grid[0])
        seen = [[False] * cols for _ in range(rows)]
        count = 0
        directions = ((-1, 0), (0, 1), (1, 0), (0, -1))

        for row in range(rows):
            for col in range(cols):
                if grid[row][col] != "1" or seen[row][col]:
                    continue

                count += 1
                seen[row][col] = True
                stack = [(row, col)]

                while stack:
                    r, c = stack.pop()
                    for dr, dc in directions:
                        nr, nc = r + dr, c + dc
                        if (0 <= nr < rows and 0 <= nc < cols
                                and grid[nr][nc] == "1"
                                and not seen[nr][nc]):
                            seen[nr][nc] = True
                            stack.append((nr, nc))

        return count
```

`directions` 保存四種座標變化。例如，加上 `(0, 1)` 會讓 row 不變、column 加一，也就是向右移動。`row, col` 屬於外層 scan；`r, c` 屬於目前的 search。使用不同名稱，可以避免 pop 出的座標覆寫 scan 目前選到的起點。當某個格子不能作為新島的起點時，`continue` 會略過內層 scan iteration 剩下的程式。

程式使用字串 `"1"` 進行比較；若拿格子與整數 `1` 比較，所有合法的陸地格子都會被排除。它假設每個 row 長度相同，而且包含題目指定的字串。它不會驗證長短不一的 rows，也不會把整數 grid 轉換成符合這份契約的輸入。

## 為什麼每座島恰好貢獻一次計數

以 path 定義群組，是在描述什麼是一座島，與程式如何執行無關。loop invariant 則是在描述程式到達某個 checkpoint 時，已經完成了什麼。這是兩項不同的主張。

在一次 search 期間，考慮每次測試 `while stack` 之前的 checkpoint。stack 裡每個座標都是已標記的陸地，都屬於起點原本所在的島，而且沒有重複的座標。這次 search 標記的每個格子，不是在 stack 中等待，就是已經檢查完四個鄰居。任何已檢查格子的陸地鄰居，也都已經被標記。

一開始這個 checkpoint 成立：這次 search 唯一標記的格子就是起點，而且它正在等待檢查。pop 會移除一個等待中的座標。對每個鄰居而言，bounds 與陸地檢查確保新排程的格子，都透過一條合法的邊連到剛 pop 的格子。`seen` 檢查搭配立即標記，能防止重複排程。四個鄰居全部檢查完後，被 pop 的格子就已完整檢查，invariant 因此再次成立。

每個陸地格子最多被 push 一次，而每個 loop iteration 都會 pop 一個 item。grid 有限，因此 search 一定會終止。stack 變空時，這次 search 發現的所有格子都已檢查完。假設同一座島裡還有某個尚未發現的陸地格子，沿著起點到它的一條 land path，找出第一個尚未發現的格子。它前面的格子必定已經被發現。那個前驅格子已經檢查完，理應發現它，形成矛盾。因此 search 會到達整座島，而且無法到達另一座島。

外層 scan 的 checkpoint，設在即將檢查下一個格子、且先前的 search 已結束之時。所有已計數的島都已完整標記，`count` 就是它們的數量，而先前所有已掃描位置中的陸地都已標記。初始時沒有更早的掃描位置，`count` 也是零。遇到水或已標記的陸地，不增加 count，這項主張仍然成立。尚未發現的陸地屬於還沒計數的島，因此 count 加一並完成它的 search 後，checkpoint 依然成立。最後一個 scan 位置結束後，每個陸地格子都屬於一座已計數的島。任何島都不會貢獻兩次，因為第一次 search 就已標記整座島。

## 把等待中的工作也算進成本

令 `m` 為 row 數，`n` 為 column 數，`L` 為陸地格子數，因此 `L <= mn`。Big O 描述成本如何隨輸入大小成長，忽略固定倍數。這裡的 `O(mn)` 表示，在下述操作假設下，成本有一個上界，等於格子數乘上某個固定常數；它不是執行時間的預測值。

建立 `seen` 要寫入 `mn` 個 Boolean references。外層 scan 檢查 `mn` 個格子。把所有 search 加起來看，每個陸地格子各被 push 與 pop 一次，因此共有 `L` 次 pop 與 `4L` 次鄰居檢查。search 寫在 scan 裡面，不代表會執行 `mn` 次完整的 grid search：已完成的發現紀錄會保留，不能重複。因此總時間是 `O(mn + L) = O(mn)`。

這個計算把大小有界的整數運算、座標存取、Boolean 存取與單一字元比較視為固定成本。list 尾端操作需要補上一個條件。CPython v3.14 的 list 使用 object references array，並保留額外 capacity；擴充時可能配置空間並複製 references，因此某一次 append 不一定是 constant time。反覆做小幅擴充時，capacity 會按比例增加。若 capacity 以大於一的倍率成長，每次複製的大小便形成 geometric sum，總和不超過最終大小的某個固定倍數：倒過來看就是 `K + K/q + K/q² + ...`，其中 `q > 1` 是固定值。把多次 append 合起來計算，就能將 resizing 成本分攤到這些操作上。「Amortized constant time」指的是這種總成本換算成每次操作的上界，而不是保證每一次呼叫都有相同成本。縮減時也會保留一段 capacity 餘裕，之後才再次 resize，因此交替執行尾端 push 與 pop，不會每次都被迫複製。[CPython v3.14 list implementation](https://github.com/python/cpython/blob/v3.14.0/Objects/listobject.c) 記載了這些 growth 與 shrink policies；它們是 implementation details，不是 Python language 對執行時間的保證。

`seen` matrix 保留 `mn` 個 entry。同時等待中的座標最多有 `L` 個，每個座標含有兩個大小有界的整數。因此 auxiliary space，也就是輸入以外額外使用的儲存空間，在 worst case 下是 `O(mn)`。使用 explicit stack，不會讓 DFS 變成 constant-space。directions 與目前處理的座標只需要固定的額外空間。回傳的整數是一個值，在這份有界輸入的模型下，output space 計為 `O(1)`。若允許維度無限增加，並計算整數需要多少位數，就必須採用不同的 numeric model。

## 什麼情況值得換方法

Recursive DFS 會以一個對鄰居呼叫自己的 function，取代 explicit stack。每個尚未結束的 function call 都必須保存足夠狀態，才能在 child call 回傳後繼續檢查鄰居。狹長的 land path 可能需要同時保留很多層 calls，因此 recursion 並沒有消除儲存成本。Python 有 [recursion limit](https://docs.python.org/3.14/library/sys.html#sys.getrecursionlimit)；一座合法的大島，可能需要超過目前設定上限的深度。iterative 版本明確保存等待中的工作，不必依賴這麼深的 call depth。

Breadth-first search，簡稱 BFS，會優先處理最早等待的格子。`collections.deque` 支援從一端 append，並透過 `popleft()` 從另一端移除。採用相同的 discovery marking，BFS 也能以 `O(mn)` time 與 `O(mn)` worst-case auxiliary space 算出相同的島數。不要直接把 `pop()` 換成 list 的 `pop(0)`：移除 list 前端的 item，會搬動後面的 entries。Python 將 [deque operations](https://docs.python.org/3.14/library/collections.html#collections.deque) 在兩端的成本記為約略 constant time。

若題目改成尋找從一個陸地格子到另一個陸地格子，最少需要沿著邊移動幾次，BFS 就更合適。把起點以 distance zero 放入 queue。它的鄰居得到 distance one，這些鄰居再新發現的鄰居得到 distance two，依此類推。優先處理最早等待的格子，會讓每個 distance layer 都在下一層之前處理完，因此第一次發現終點時，move count 就是最小值。我們的 DFS stack 不維持這個順序，所以第一條找到的 route 不一定最短。這項調整也需要保存 distance 或 queue-layer counter；只回傳島數，無法回答這個問題。

若記憶體是考量，而且呼叫端明確允許覆寫地圖，可以在發現陸地時，把它從 `"1"` 改成 `"0"`。稍後的檢查就會把已標記陸地當作水，不再需要獨立的 `seen` matrix。stack 仍可能需要 `O(mn)` space，而且呼叫端會失去原始地圖。若先複製以保留原圖，便又需要 `O(mn)` 的 copy storage；只複製外層 list，仍然共用原來的 row lists，無法保護 row 裡的 entries。

連接規則的改變，會帶來不同的調整。若對角接觸也算相連，就加入四種 diagonal coordinate changes，並讓 proof 一致採用這個規則。先前只有兩個對角陸地的例子，答案就會從 2 座島變成 1 座。每個被 pop 的格子會檢查八個位置，而不是四個，但仍然是固定數量，因此 `O(mn)` bounds 不變。

## English interview answers 與 reconstruction map

Why increase the count before the search? An undiscovered land start identifies one previously uncounted island. The search records that entire island before scanning resumes.

Why mark before pushing? A waiting cell is already discovered. Immediate marking prevents another neighbor from placing the same coordinate on the stack again.

Why examine four directions? The statement connects cells by shared horizontal or vertical edges. Diagonal contact does not establish a legal path.

Why is the time linear in the number of cells? The scan checks every cell once, and each land cell causes one pop and four neighbor tests across all searches.

What does preserving the input cost? The Boolean matrix uses `O(mn)` auxiliary space. Even if permitted mutation removes it, the explicit stack still has an `O(mn)` worst-case bound.

重建這個解法的關係鏈是：由邊相連的陸地定義一個區域；scan 選出尚未發現的代表格子；discovery marks 防止重複排程；stack 保留檢查鄰居的工作；耗盡這些工作，就會記錄整個區域；下一個尚未發現的代表，必定屬於另一座島。回傳值計算的，就是這些已完成搜尋的區域。
