# Course Schedule：計算尚未滿足的先修義務

假設課程 3 同時要求先修完課程 1 與課程 2。完成課程 1 有幫助，但課程 3 仍不能開始。解法必須記住還有幾項要求，並察覺這個數量降到零的時刻。

## 完成所有課程代表什麼

在 [LeetCode 207](https://leetcode.com/problems/course-schedule/) 中，課程識別碼從 `0` 到 `numCourses - 1`。一組 `[a, b]` 表示必須先完成 `b`，才能修 `a`。回傳一個 Boolean，表示是否能完成每門課；不需要回傳 schedule 本身。課程數介於 1 到 2000，互不重複的 prerequisite pairs 數量介於 0 到 5000；兩個識別碼都在課程範圍內。題目沒有排除 `[a, a]`，而這會讓該課程無法開始。下面的實作不修改輸入。

沒有先修要求的課程可以立即修讀。即使某門課沒有出現在任何 pair 裡，它仍然存在，也必須計入結果。相反地，`[[1, 0], [0, 1]]` 讓課程 0 與課程 1 彼此等待。無論選哪門當第一門，都無法滿足這些要求。

對每組 `[a, b]` 畫一條 directed edge `b -> a`。一張 directed graph，就是所有課程節點以及這些單向的先修 edges。沿著一條或多條 edges 回到起點，就形成 directed cycle。cycle 上的每門課都必須等待同一個 cycle 裡的另一門課，因此不可能先完成其中任何一門。self-loop 是只含一個節點的 cycle。

對這張有限的 graph，反過來也成立。如果每門尚未完成的課，都還有一門尚未完成的 prerequisite，就從任一門未完成的課出發，不斷往回追它的 prerequisite。課程識別碼的數量有限，因此必定重遇某個識別碼，於是找到 cycle。所以，只要剩餘部分非空而且沒有 cycle，就必定有課程可以開始。不斷選一門可開始的課，能恰好在 graph 沒有 directed cycle 時完成所有課程。這個 equivalence 描述題目的性質；實作則會由隨執行狀態變化的 loop invariant 來描述。

## 保存計數，以及它可以釋放哪些課程

每完成一門課就掃描所有 pairs，會重新找出哪些課依賴剛完成的課。改為建立 `after[b]`，保存直接等待 `b` 的課程清單。對每組 `[a, b]`，把 `a` 存入這個 list。這就是 adjacency list：每個節點擁有一份清單，記錄它所有 outgoing edges 的目的地。

同時建立 `remaining[a]`，初值是進入 `a` 的 prerequisite edges 數量。這個 incoming-edge count 常稱為 indegree。完成一些課程後，我們使用的意義則是：`a` 還有幾門 prerequisite 尚未完成。計數為二，代表還有兩項不同的義務；只記錄課程是否有 prerequisite，會失去第一次完成先修課後所需的資訊。

使用 `after = [[] for _ in range(numCourses)]`。每門課分別求值一次 `[]`，就會得到各自獨立的 inner lists。若寫成 `[[]] * numCourses`，則會重複保存指向同一個 shared list 的 references：為課程 0 加上一門 dependent，其他課程也會看似同時多出那門 dependent。相較之下，這裡的 `[0] * numCourses` 是安全的。integer 是 immutable，而 `remaining[a] += 1` 會替換 slot `a` 裡的值，不會修改一個共用的零。Python 的 [sequence operations](https://docs.python.org/3.14/library/stdtypes.html#common-sequence-operations) 區分重複 references 與複製它們指向的 objects。

把可開始的課程放入 `ready`，一個 queue。queue 保存等待處理的 entries；從一端移除最早進入的 entry，再從另一端加入新 entries，就得到 first-in, first-out 行為。在可開始的課程之間任選一門，不會破壞先修要求：每門被選的課都已經沒有未完成的 prerequisite。FIFO 讓 trace 有明確順序，也不必搜尋最小的課程編號。

使用沒有長度上限的 `collections.deque`。`deque()` 建立 queue，`append(x)` 把 `x` 加在右端並回傳 `None`，`popleft()` 則移除並回傳最左端的 entry。因此，若把 `append` 的回傳值重新指定給 `ready`，queue 就會被換成 `None`。有長度上限的 deque 在滿載時可能丟棄 entries，所以這裡不該設定 `maxlen`。這些行為由 [Python 3.14 deque documentation](https://docs.python.org/3.14/library/collections.html#collections.deque) 規定。

每當一門課從 `ready` 被移除，就在 `finished` 多記一次完成。只走訪 `after[course]` 裡的 dependents。每門 dependent 都恰好少了一項未滿足的義務，所以把其計數減一。恰好在某門 dependent 的計數變成零時，將它 append 進 queue。這個階段的計數只減不增。原本為正的計數只會跨越零一次，初始計數為零的課程則在初始化時入列，因此每門課最多進入 queue 一次，不需要額外的 visited set。

## 一段包含延後釋放的 program movie

考慮以下構造的輸入：

```text
numCourses = 5
prerequisites = [[1, 0], [2, 0], [3, 1], [3, 2]]
```

課程 4 獨立存在。課程 0 會釋放 1 與 2；兩者都完成後，3 才能開始。依照 pairs 列出的順序讀入，得到：

```text
after     = [[1, 2], [3], [3], [], []]
remaining = [0, 1, 1, 2, 0]
ready     = deque([0, 4])
finished  = 0
```

初始化依課程識別碼由小到大檢查，因此 0 比 4 先入列。此時 `popleft()` 回傳 0，並把 `ready` 修改成 `[4]`。增加 `finished` 後，得到 1。第一門 dependent 是 1：其計數從 1 變成 0，因此 `append(1)` 讓 queue 變成 `[4, 1]`。第二門 dependent 是 2：其計數也從 1 變成 0，得到 `[4, 1, 2]`。此時計數為 `[0, 0, 0, 2, 0]`。

下一次移除回傳 4，留下 `[1, 2]`；`finished` 變成 2。它的 dependent list 是空的，所以沒有計數改變。一門 isolated course 即使沒有釋放其他課，也算完成一門課。

移除 1 後留下 `[2]`，`finished` 增為 3。課程 3 的計數從 2 變成 1。零值檢查不成立：3 仍不能進入 queue，因為課程 2 尚未完成。若只用 Boolean 表示 readiness，就容易錯誤處理這個 branch。

移除 2 後 queue 清空，`finished` 增為 4。課程 3 的計數從 1 變成 0。加入 3 後得到 `[3]`，計數為 `[0, 0, 0, 0, 0]`。最後移除 3，queue 清空且 `finished = 5`；它的 dependent list 是空的。loop 結束，`5 == numCourses` 回傳 `True`。概念上的完成順序是 `[0, 4, 1, 2, 3]`；回傳 Boolean 的實作不會保存這個順序。

再看一個拒絕案例：`numCourses = 3`，pairs 是 `[[1, 0], [0, 1]]`。初始計數為 `[1, 1, 0]`，只有課程 2 進入 queue。它完成後沒有釋放其他課。此時 queue 為空，但 `finished = 1`，因此與 3 比較後回傳 `False`。有一門可開始的課並不足夠：另一個 component 仍包含 cycle。

## 完整 Python 解法與它的 checkpoint

```python
from collections import deque


class Solution:
    def canFinish(self, numCourses: int, prerequisites: list[list[int]]) -> bool:
        after = [[] for _ in range(numCourses)]
        remaining = [0] * numCourses

        for course, prerequisite in prerequisites:
            after[prerequisite].append(course)
            remaining[course] += 1

        ready = deque()
        for course in range(numCourses):
            if remaining[course] == 0:
                ready.append(course)

        finished = 0
        while ready:
            course = ready.popleft()
            finished += 1
            for dependent in after[course]:
                remaining[dependent] -= 1
                if remaining[dependent] == 0:
                    ready.append(dependent)

        return finished == numCourses
```

checkpoint 位於每次求值 `while ready` 之前，也就是前一門課完成後的所有更新都已處理完畢之時。此時，`finished` 計算互不相同的已完成課程；每門未完成課程的計數，等於它尚未完成的 prerequisites 數量；queue 恰好包含所有可以開始、尚未完成的課程，而且每門只出現一次。已完成的課程不在 queue 中。queue 內部的排列順序是實作選擇，與這些條件分開。

起初沒有課程完成，因此從所有 pairs 建立的計數具有所需意義。初始化掃描恰好納入計數為零的課程。因此，在第一次 iteration 之前 checkpoint 成立，即使 queue 起初就是空的也一樣。

對 maintenance 而言，移除一門可開始的課是合法的，因為它的 prerequisites 已全部完成。它的 outgoing edges 恰好描述這次完成所滿足的義務。把那些目的地的計數減一，會正確更新計數，而不影響其他課程。每個新降到零的目的地入列一次；其他已可開始的課程繼續留在 queue。增加 `finished` 便記錄了這一次新完成。checkpoint 會在整份 dependent list 處理結束後再次成立，而不是處理到一半時就成立。

對 termination 而言，最多只能移除 `numCourses` 門互不相同的課程。如果全部都被移除，這些合法步驟便構成 schedule。否則，queue 已空，但仍有課未完成。依 checkpoint，每門這樣的課都還有一門未完成的 prerequisite。前面的有限集合往回追蹤論證因此會找到 cycle，所以不可能存在完整 schedule。最後的比較因而涵蓋兩種結果。這個 algorithm 常稱為 Kahn's topological sort；topological order 會把每門 prerequisite 排在其 dependent 前面。

一個誘人的錯誤回傳方式，是只要初始 queue 非空就回傳 `True`。前面的三門課拒絕案例就能推翻它。如果要求案例必須同時含有 two-course cycle 與另一門可開始的課，則它按課程數計算是最小的：兩個課程識別碼形成 cycle，第三個提供誤導性的起點。如果沒有這項要求，更小的 `numCourses = 2, prerequisites = [[0, 0]]` 已能推翻捷徑：課程 1 可開始，但課程 0 在等待自己。

## Running time 從何而來

令 `V = numCourses`、`E = len(prerequisites)`。Big O 描述成長速度的 upper bound，忽略固定倍數；在下面的模型中，`O(V + E)` 表示工作量的成長不超過課程數加 pairs 數再乘上一個常數。讀取或寫入一個 list slot、比較有界的 integers、增加 counter，以及搬移或保存一個 object reference，都是固定大小的 elementary operations。課程識別碼介於 0 到 1999，計數介於 0 到 5000；在這個 contract 下，把這些 scalars 當成有界的單位是適當的。這是 operation-count model，不是說每個 Python instruction 的實際執行時間完全一樣。配置或複製 `k` 個 slots 的成本與 `k` 成正比。

queue 的選擇會影響這項計算。Python list 把 references 放在連續、有索引的 slots 裡。移除第一項後，必須把後面的 references 向左移，才能讓 indexing 繼續從零開始。如果初始有 `V` 門可開始的課，用 `pop(0)` 逐一取空 list，總共會搬移 `(V - 1) + (V - 2) + ... + 1` 個 references。將各項配對可得 `V(V - 1)/2`；即使完全沒有 prerequisite edges，仍是 quadratic growth。[Python tutorial](https://docs.python.org/3.14/tutorial/datastructures.html#using-lists-as-queues) 說明了這種搬移成本。

CPython v3.14.0 的 [deque implementation](https://github.com/python/cpython/blob/v3.14.0/Modules/_collectionsmodule.c) 使用以 links 串接的固定長度 blocks。endpoint operation 會改變端點位置；遇到 block boundary 時，會改變固定大小 block 的連接，而不會把所有已入列的 references 搬移。如果把固定大小的 block allocation 視為有界工作，那麼在此模型中，每次 queue endpoint operation 都有 constant cost，與文件所述約為 `O(1)` 的行為相符。queue 大小可以增加，但單次 endpoint update 的工作量不會隨其長度增加。

adjacency lists 使用 `list.append`，需要另一個論證。list 有時會用完已配置的 slots。CPython v3.14.0 的 [list resize policy](https://github.com/python/cpython/blob/v3.14.0/Objects/listobject.c) 在單項增加時預留 spare capacity；預留部分約為所要求大小的八分之一，另有少量 rounding 與 padding。一次成長可能複製原有 references，所以單次 append 並不保證都是 constant work。

為什麼整段 append-only sequence 仍是 linear？一個夠大的 list 在大小為 `m` 時成長後，會有與 `m` 成正比的 spare room，因此至少還能做某個固定比例乘上 `m` 次的單項 appends，才需要再次成長。把這次與 `m` 成正比的成長成本分攤給接下來那些 appends，每次只需分到 constant charge。也可以從最終 capacity `C` 往回看：除去小尺寸的情況，歷次成長的大小會按某個小於一的固定比例縮小。其複製工作有 upper bound：`C + rC + r²C + ... = C/(1-r)`，其中 `r < 1` 是某個固定值。要理解這個界，把整個和乘上 `r`，就得到原本的和扣掉第一項；兩式相減便是 `(1-r)S = C`。初期的小 capacities 只增加固定工作。最終 capacity 與最終 length 成正比，因此 `d` 次單項 appends，連同一般的寫入，總共花費 `O(d)` 工作。這個 aggregate guarantee 稱為每次 append 的 amortized constant time。這裡可以使用它，因為每個 adjacency list 都只靠每次 append 一項來成長；論證並未暗中混入交替刪除或 bulk update。

建立 `V` 個獨立 lists 與 `V` 個計數的成本是 `O(V)`。讀取 `E` 組 pairs 會做 `E` 次 counter updates 與 `E` 次 appends。如果課程 `b` 有 `d_b` 門 dependents，它的 append sequence 成本是 `O(d_b)`；把所有課程的 `d_b` 相加，恰好得到 `E`。小 lists 的 overhead 最多再貢獻 `O(V)`。因此建立 representation 的成本為 `O(V + E)`。

readiness scan 檢查 `V` 個 slots，並將最多 `V` 門課入列。在處理階段，每門課最多入列與移除一次。每條 edge 恰好出現在一份 dependent list，而那份 list 最多被走訪一次。因此，雖然程式把 inner loop 放在 `while` 裡面，inner loop 的所有執行次數加起來仍最多為 `E`。setup、queue operations 與 edge updates 合計得到 worst-case `O(V + E)` time，其中 list construction 是針對整段 append sequences 分析。cycle 可能讓處理提早停止，但無法省去最初讀取 pairs 的工作。

就 auxiliary space 而言，外層 adjacency list 與 inner-list headers 使用 `O(V)` 個 slots 或固定大小的 records。inner lists 保存 `E` 個 references，再加上 spare capacity；依同一套 growth policy，這些 capacity 與 `V + E` 成正比。計數使用 `V` 個 scalar slots；queue 最多保存 `V` 個 entries，加上與該 capacity 成正比的固定大小 block overhead。scalar loop variables 使用 constant space。resize 期間，舊 storage 與新 storage 可能暫時同時存在，但兩者大小都與正在成長的 list 成正比，因此 peak bound 仍是 `O(V + E)`。auxiliary space 不計既有輸入，回傳的 Boolean 則是 `O(1)` output space。此實作沒有 recursion stack。

## 用重複掃描換取少存一些 edges

如果無法接受額外保存 `E` 個 references，但可以反覆掃描原有 pair list，就有一個較慢的替代方案。保存 `done[V]` Booleans。每一輪都重新配置一個全部為 false 的 `blocked[V]` array。掃描每組 `[a, b]`；若 `a` 與 `b` 都未完成，就把 `blocked[a]` 設為 true。接著找出所有未完成且未被 blocked 的課程，等掃描結束後才把整組標為 done。這些課恰好就是該輪開始時，沒有未完成 prerequisite 的課程。全部完成就成功停止；若某輪沒有增加任何完成課程，就失敗停止。

同一套合法性與有限 cycle 論證也適用於這些群組。群組成員不可能互相要求先修，因為這樣的 edge 會把目的地標成 blocked。每個成功的 round 至少新完成一門課，因此最多有 `V` 個成功 rounds，再加上最多一個最後失敗的 round。每輪初始化 flags 與檢查課程花費 `O(V)`；檢查每組 pair 花費 `O(E)`。因此 bound 為 `O(V(V + E))`。一條長度為 `V` 的 prerequisite chain 每輪只釋放一門課，說明為何規模增加時，重複工作仍可能持續。`done`、`blocked` 與可選的 group buffer 各自最多保存 `V` 個 entries，因此 peak auxiliary storage 為 `O(V)`；舊的 round buffers 在下一輪之前釋放。Boolean output 仍為 `O(1)`。輸入的 `E` 組 pairs 持續存在，並依相同計算慣例排除在 auxiliary space 之外。只有當額外 adjacency storage 的負擔比重複掃描更重要時，才選擇這個 trade-off。

另一項需求會改變主解法必須保留的內容：回傳一個合法課程順序；若不可能，則回傳 `[]`。先建立空的 `order` list，每次移除課程後立即 append `course`。如果長度等於 `V` 就回傳 `order`，否則回傳 `[]`。每筆保留下來的 entry 都記錄一次合法完成，因此先前的 proof 可以證明回傳順序正確。FIFO 不保證編號由小到大；在 program movie 中，4 排在 1 前面。

這個 adaptation 最多增加對同一個 growing list 的 `V` 次單項 appends。append-only 論證仍然適用，所以額外工作為 `O(V)`，整個 algorithm 仍是 `O(V + E)`。adjacency representation、計數與 queue 都還在，因此不含成功回傳 order 的 auxiliary storage 仍是 `O(V + E)`。成功時的 output 恰好含有 `V` 個 references，需要 `O(V)` output space。失敗時，partial order 是最多含有 `V` 個 entries 的暫時 auxiliary storage，回傳的 empty list 則是 constant size。保存 order 會改變 storage accounting，卻不改變每條 edge 的走訪成本。

## Interview English 與 master map

Why use indegree? "It counts unfinished prerequisites. A course becomes available exactly when its count reaches zero."

Why can each edge be handled once? "I store each dependent under its prerequisite. When that prerequisite finishes once, I visit that edge once and remove one obligation."

Why does an empty queue sometimes mean failure? "If unfinished courses remain, each still waits for an unfinished prerequisite. Following those prerequisites in a finite graph must reach a cycle."

What are the bounds? "Construction and traversal take `O(V + E)` time under the stated bounded-scalar and container cost model. Adjacency storage, counts and the queue use `O(V + E)` auxiliary space. The result is one Boolean."

master map 串起整個論證：`[a, b]` 建立 `b -> a`；outgoing lists 找出一次完成會移除哪些義務；remaining counts 決定 availability；queue 在處理前保存這些可開始的課程；checkpoint 讓計數持續對應未完成的 prerequisites；已完成課程數則區分全部完成的 graph 與受阻的剩餘部分。只有先說明 queue 與 append-sequence costs，才能由每門課及每條 edge 各走訪一次，推出 time bound。
