# Daily Temperatures：讓新的一天回答仍在等待的舊日期

某天的氣溫是 70 度，後來出現的 70 度不會結束等待。72 度才會，即使中間隔著幾個更冷的日子。答案是到第一個符合條件日期的距離，單位是天數，不是度數。

[LeetCode 739，Daily Temperatures](https://leetcode.com/problems/daily-temperatures/) 的 `temperatures` 是整數 list，長度介於 1 到 100,000，每個值介於 30 到 100。請回傳相同長度的 list：位置 `i` 放入滿足 `temperatures[j] > temperatures[i]` 的最小正距離 `j - i`；如果未來沒有這樣的位置，就放入 `0`。位置從零開始編號。題目要求回傳答案；以下解法都保留傳入的 list，另外配置結果。

假設輸入是 `[70, 70, 69, 72, 71]`。第 0 天必須等到第 3 天，所以答案是 `3`。第 1 天到同一個暖日只需 `2` 天。第 2 天等 `1` 天。第 3 天與第 4 天之後都沒有更暖的一天。完整答案為 `[3, 2, 1, 0, 0]`。

## 先用直接搜尋確定必須保留什麼

一個正確方法是分別處理每一天。從下一天開始往右走，在遇到第一個嚴格較高的氣溫時停止。必須在那裡停下：更遠處即使有更熱的一天，也無法縮短題目要求的等待時間。

```python
def daily_temperatures_scan(temperatures: list[int]) -> list[int]:
    n = len(temperatures)
    answer = [0] * n
    for i in range(n):
        for j in range(i + 1, n):
            if temperatures[j] > temperatures[i]:
                answer[i] = j - i
                break
    return answer
```

這裡的 `i` 是正在求答案的日期，`j` 是候選的未來日期。內層搜尋若什麼也沒找到，初始化的零就會保留下來。`break` 結束內層搜尋，下一次外層迭代便處理下一個 `i`。被選中的 `j` 之前，每個候選日期都沒有通過比較；因此第一次成功就能給出正確答案。每次內層搜尋都讓 `j` 朝 `n` 前進，而 `i` 的數量有限，所以方法會結束。

未來始終不變暖時，成本就成了問題。對長度為 `n` 的全同溫 list，各次搜尋依序檢查 `n - 1`、`n - 2`，一直到 `0` 個候選日期。把這個總和的首尾配對，可得 `n(n - 1)/2` 次比較。100,000 天就要比較 4,999,950,000 次。題目的氣溫範圍沒有排除這種輸入：全部都是 70，仍然合法。

Big O 描述成本上界如何隨輸入大小成長，省略固定倍數與較低次項。上述總和的最高次項是二次項，因此 worst-case time 是 `O(n²)`。這裡假設讀取 list 項目、比較這些有界整數、更新 index，都只需要固定時間。除了答案，這個方法只保留 `n`、`i`、`j`，所以 auxiliary space 是 `O(1)`，output space 是 `O(n)`。`range` 描述 index 如何前進，不會建立一份包含所有 index 的 list。輸入很小時，直接搜尋可能更適合，因為不需要一個隨輸入成長的待解日期集合。即使長輸入的重複掃描很昂貴，這項記憶體優勢仍然成立。

重複工作讓我們可以把問題反過來問。第 3 天帶來 72 度時，它能一次回答好幾個舊日期。我們需要保留尚未找到更暖後繼日期的那些天。

## 先推導待解狀態，再命名 stack

每個待解項目必須指出是哪一天，不能只保留氣溫。範例中的兩個 70 度有相同門檻，到第 3 天的距離卻不同。儲存它們的 index，可以同時保留答案要寫入的位置，以及計算答案所需的減法運算元。原始 list 還在，因此可以從儲存的日期讀回其氣溫。

由左往右處理日期，並讓待解 index 保持相同順序。最新的待解日期放在 Python list 的右端。如果今天比那一天暖，就移除該待解 index、填入答案，再檢查新的最右端項目。某天找到第一個更暖的後繼日期後，就不再需要第二個答案，可以永久移除。

為什麼只看右端就夠了？待解日期的氣溫會由左往右維持 non-increasing：每個項目的氣溫都大於或等於下一個。如果今天連最右端、氣溫最低的待解日期都無法回答，就更不可能回答左邊較暖或同溫的日期。如果今天能回答最右端日期，移除它就會露出下一個要檢查的門檻。因此，比較失敗後，演算法不必繼續掃描其餘待解項目。

要維持這個順序，就先移除右端所有比今天冷的項目，再加入今天。移除結束後，list 不是空的，就是最後一個項目的氣溫大於或等於今天。把今天加入右端，便能維持 non-increasing 的順序。同溫日期一起留在待解狀態，因為相等無法回答它們嚴格較暖的問題。這種有順序的 last-in, first-out 集合稱為 monotonic stack；本題的氣溫順序是 non-increasing，允許同溫並存。

stack 這個詞描述存取規則。它的 top 是最右端項目；移除該項目，下面那一個就會露出。Python 的 [list-as-stack 文件](https://docs.python.org/3.14/tutorial/datastructures.html#using-lists-as-stacks) 支持在右端 `append`，也從同一端 `pop()`。過程沒有排序：index 保持日期順序，由有效答案決定哪些 index 可以離開。

## 跟著程式走完一份完整輸入

輸入 `[70, 70, 69, 72, 71]` 一開始對應 `answer = [0, 0, 0, 0, 0]` 與 `pending = []`。以下各個狀態的 `pending` 都存放 index，不是氣溫。

第 0 天，待解 list 是空的，因此沒有舊日期需要回答。加入 `0` 後變成 `[0]`。答案仍然全是零；第 0 天現在開始等待。

第 1 天，top 的 index 是 `0`，對應 70 度。比較 `70 > 70` 為 false。沒有 index 離開，答案也不變。加入 `1` 後得到 `[0, 1]`。這兩個同溫項目代表兩個不同的未解日期。

第 2 天，`69 > temperatures[1]`，也就是 `69 > 70`，為 false。加入 `2` 後得到 `[0, 1, 2]`，對應氣溫 `[70, 70, 69]`。答案仍為 `[0, 0, 0, 0, 0]`。

第 3 天，今天的 72 大於 `temperatures[2]`，也就是 69。`pending.pop()` 回傳 `2`，並將 `[0, 1, 2]` 改成 `[0, 1]`。把回傳的 index 存入 `previous`，接著 `answer[previous] = 3 - 2` 讓答案變成 `[0, 0, 1, 0, 0]`。減法計算的是經過幾天。氣溫差 `72 - 69` 回答的是另一個問題。

迴圈再次檢查。新的 top 是 `1`，對應 70 度。pop 回傳 `1`、留下 `[0]`，寫入 `answer[1] = 3 - 1` 後，答案為 `[0, 2, 1, 0, 0]`。下一次比較發現 `72 > temperatures[0]`。pop 回傳 `0`、清空待解 list，`answer[0] = 3 - 0` 讓答案變成 `[3, 2, 1, 0, 0]`。現在已經沒有 top 可以檢查。加入 `3`，留下 `[3]`。

第 4 天，`71 > temperatures[3]`，也就是 `71 > 72`，為 false。加入 `4` 得到 `[3, 4]`。輸入結束，所以這兩天始終沒有遇到使比較成功的未來日期。回傳現有的 `[3, 2, 1, 0, 0]`；最後兩個零已經表達它們未來沒有更暖的一天。

第 3 天若只用一次 `if` 就不夠：第一次 pop 之後，還有兩天需要今天的答案。`while` 會重複執行，直到今天已回答所有它能回答的待解日期。

## 把狀態變化接到 Python

完整解法用 `enumerate` 同時取得每個 index 與氣溫。預設計數從零開始，因此本例的第一組是 `(0, 70)`。它隨著迴圈推進逐組產生資料，不會另外建立包含全部組合的 list。可參考官方 [`enumerate` 定義](https://docs.python.org/3.14/library/functions.html#enumerate)。

```python
class Solution:
    def dailyTemperatures(self, temperatures: list[int]) -> list[int]:
        answer = [0] * len(temperatures)
        pending = []

        for day, temperature in enumerate(temperatures):
            while pending and temperature > temperatures[pending[-1]]:
                previous = pending.pop()
                answer[previous] = day - previous
            pending.append(day)

        return answer
```

`pending[-1]` 讀取最後一個待解 index。外層的 `temperatures[pending[-1]]` 再讀取那一天的氣溫。例如 `pending` 是 `[0, 1, 2]` 時，這兩次讀取先得到 `2`，再得到 `69`。讀取 top 不會改變待解 list；pop 則會移除並回傳該 index。

guard 有兩部分，因為空 list 沒有最後一個項目。Python 把空 list 視為 false，而 `and` 只有在左運算元為 true 時才會計算右運算元。因此，`pending and ...` 在 `pending` 為空時會略過 indexing，包括剛剛被 pop 清空的情況。這個順序避免了 `IndexError`。這些是 [Python truth-value 與 Boolean-operation 規則](https://docs.python.org/3.14/library/stdtypes.html#truth-value-testing)。

`answer = [0] * len(temperatures)` 預先建立 output 的各個位置。各項目一開始都參照 immutable integer 零。賦值給 `answer[previous]` 只會替換一個位置，不會改變所有零項目。`pending.append(day)` 修改既有 list 並回傳 `None`，所以程式沒有把它的回傳值再賦給 `pending`。兩份 mutable list 有不同用途：`pending` 追蹤未完成工作，`answer` 接收已完成的日距。這些操作都不會修改 `temperatures`。

輸入只有一天時，迴圈只會加入 index 0，回傳 `[0]`。全部同溫時，每個 index 都留在待解狀態，答案全部為零。氣溫遞增時，每個新的一天都會回答前一天。這些情況分別走過沒有 top、同溫，以及連續成功回答的路徑，不需要額外分支。

## 為什麼每個答案都是第一個較暖日期

把 checkpoint 設在準備處理新日期 `d` 之前。loop invariant 是在這個 checkpoint 對整份狀態的敘述：`pending` 恰好包含那些已處理、但尚未在已見日期中找到較暖後繼日期的天；它們的 index 遞增，氣溫為 non-increasing。所有已處理但不在 `pending` 裡的 index，都已在 `answer` 中取得正確的第一個較暖日期之日距。待解位置與尚未處理的位置仍為零。

最初還沒處理任何一天，因此空的待解 list 與全零答案滿足這個敘述。

現在假設處理第 `d` 天之前，敘述成立。如果今天比 top 的待解日期 `p` 暖，就表示 `p` 與 `d` 之間沒有任何一天比 `p` 暖；否則 checkpoint 的敘述不會允許 `p` 仍然待解。今天符合條件，之前所有未來候選日期卻都不符合，所以 `d` 就是 `p` 的第一個較暖日期。寫入 `d - p` 正確，移除 `p` 也只會丟棄已完成的待辦。每次 pop 都適用同樣論證。

如果 top 不比今天冷，所有更早的待解項目都至少和 top 一樣暖。今天無法回答任何一個。其餘項目因此繼續待解。加入 `d`：已處理的日期之中不可能已有 `d` 的未來日期，而停止比較的條件又保證氣溫順序得以維持。於是，處理下一天之前，invariant 再次成立。

外層迴圈恰好處理 `n` 天。內層每次迭代都移除一個待解 index，因此也會結束。在最後的 checkpoint，所有日期都已看過。每個仍待解的日期，在整份輸入中都沒有更暖的未來日期，保留零正確。被移除的日期都已取得第一個較暖日期的日距。因此，回傳的 list 正確。

這份證明談的是 checkpoint 上尚未完成的日期。題目另外規定的結果條件，是每一天各自最早符合條件的未來 index。invariant 將中途進度接到最終條件；兩個敘述各有用途。

把 `>` 改成 `>=` 會破壞原題契約。輸入 `[70, 70]` 時，它會回傳 `[1, 0]`，而不是 `[0, 0]`。這是能暴露此錯誤的最短長度：輸入只有一天時，沒有後來的日期可以比較。另一個看似可行的修改是把 `while` 換成 `if`，但它會在 `[71, 70, 72]` 失敗：只回答第 1 天，第 0 天仍為零，回傳 `[0, 1, 0]`，而不是 `[2, 1, 0]`。

## 把整趟掃描的工作加起來

令 `n` 為天數。`O(n)` time 表示在所述成本假設下，扣除固定開銷，總工作量最多隨 `n` 成正比地成長。光看巢狀迴圈，不能判定工作量是二次；要計算迴圈本體能消耗多少東西。

每個 index 恰好進入 `pending` 一次。它最多離開一次，因為移除後不會再次加入。因此，整趟執行共有 `n` 次 append、最多 `n` 次 pop。每次成功的氣溫比較都會帶來一次 pop。每次外層迭代，最多有一次失敗的氣溫比較讓內層停止；待解 list 為空，也可能在沒有比較氣溫的情況下讓它停止。因此，即使某天觸發很多次 pop，總迴圈檢查次數仍然與 `n` 成正比。每個已解位置只寫入一次，初始化 output 則需要建立 `n` 個位置。

這個操作次數計算假設 list indexing 與有界整數算術需要固定時間。list 成長還需要一項限定。[CPython v3.14.0 的 list 實作](https://github.com/python/cpython/blob/v3.14.0/Objects/listobject.c) 將參照存放在可按 index 存取的 array，成長時會預留額外 capacity。單次 append 偶爾可能複製許多參照，但一長串 append 的總 resizing 工作量是線性的。從尾端 pop 不必搬移其餘項目；偶爾縮小容量也要花費工作。縮容會等到長度低於已配置容量的一半才發生，因此距離下一次同等規模的 resize，仍隔著一段容量差。這些實作事實支持每次尾端操作的 amortized constant time，也就是把成本攤在一串操作上，平均每次為固定成本，而非承諾每次呼叫都花一樣的時間。成長或縮小時的容量呈幾何級數，讓被複製的各次容量總和不超過最大容量的固定倍數；成長、縮小交錯時，必須重新跨過那些容量差，才能再次 resize，因此可以把相關工作攤給中間的更新。

將操作次數與這些成本結合，在這種 CPython-style model 下，總時間為 `O(n)`。演算法的正確性不依賴氣溫維持在 30–100；這個界線讓算術成本假設直接成立。Python 語言文件規定行為，上述 CPython source 則提供實作細節。

最多會同時保留 `n` 個待解 index。全部同溫時，即使只有一種氣溫，也會達到這個最大值。list 預留 capacity，以及 resize 時暫時並存的新舊 array，都只增加這份儲存量的固定倍數。迴圈當前的資料組與 index 變數只保留固定數量的值。因此，worst-case auxiliary space 是 `O(n)`。另外回傳的答案有 `n` 個項目，所以 output space 也是 `O(n)`，合計 additional space 為 `O(n)`。傳入的 input 不計入 additional space；確切 byte 數取決於 Python build，這裡沒有宣稱固定值。

## 如果同溫也應該結束等待

假設另一份契約要求找到未來第一個氣溫大於或等於今天的日期。這時 stack 解法的正確比較就變成 `>=`。保留相同的 index 表示法、全零 output、處理方向、重複 pop，以及日距寫入。輸入 `[70, 70, 71]` 時，第 1 天現在會 pop 第 0 天並寫入 `1`；第 2 天 pop 第 1 天並寫入 `1`，得到 `[1, 1, 0]`。原本嚴格較暖的契約則會得到 `[2, 1, 0]`。

改過的 invariant 表示：在已見日期中，待解日期尚未找到氣溫大於或等於自己的未來日期。它們的氣溫現在是 strictly decreasing：新項目進來前，同溫項目會被移除。如果今天比 top 冷，它就比每個更早的待解日期都冷，因此停止規則仍然有效。被 pop 的日期，在新條件下仍未遇過更早符合條件的後繼日期，所以今天的日距就是它第一個符合條件的答案。原本的終止論證仍然適用。

這項調整沒有增加集合、額外掃描或 output 項目。每個 index 仍然只加入一次、最多 pop 一次，每天失敗檢查的次數仍有固定上限。因此，相同的算術與 list 成本假設仍然給出 `O(n)` time。待解儲存量仍不超過 `n`，暫態狀態數量固定，output 有 `n` 個項目。更精確地說，在原本 30–100 的氣溫範圍下，strictly decreasing 的待解氣溫最多容納 71 個項目。因此，固定這個範圍時，改題版本的 auxiliary space 為 `O(1)`，output 與 total additional space 仍為 `O(n)`。如果允許氣溫範圍隨輸入成長，遞減輸入就能保留全部 `n` 個 index，使 worst-case auxiliary space 回到 `O(n)`。這個較小的界線不適用於原解法，因為原解法會累積同溫日期。

## Interview English 與最後的 Master Map

Why store indices? "Equal temperatures can belong to different days. An index identifies the output position and lets me compute the wait as the current index minus the previous index."

Why can the algorithm stop at the top? "Pending temperatures are non-increasing. If today cannot resolve the coldest pending day at the top, it cannot resolve any earlier pending day."

Why is a pop safe? "That day has remained unresolved through every earlier day we processed. Today is warmer, so today is its first warmer successor."

Why is the nested loop linear? "Every index is pushed once and popped at most once. The total stack work is linear, assuming amortized constant-time end operations."

What changes for warmer-or-equal? "I use `>=`, remove equal pending temperatures, and restate the invariant for the new qualifying condition. The work count stays linear; with a fixed 71-value range, the strictly decreasing stack has at most 71 entries."

Master Map 從題目要求的「未來第一個較暖日期」出發。由左往右處理，讓新出現且符合條件的日期，成為每個被它解決的待解 index 之最早答案。index 同時保留答案目的地與經過天數的計算依據。non-increasing 的待解氣溫，讓 top 成為有效的停止界線。重複 pop 完成待辦，append 建立今天的待辦。每個待辦只進入一次、最多離開一次，因此得到線性的工作量。最後，從未離開的待辦保留零，因為它們的整段未來都已走完。
