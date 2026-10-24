# 完整註解 Reader audit

判定：**PASS_BOUNDED**。46 組完整註解逐段閱讀，兩個頁面共 92 組實例；未發現需修改的 entailment 或推導前提問題。

CODEX_THREAD_ID：`01a15cf2-b81e-7323-81ac-2a924a125df0`

只核對給定正文；沒有開啟外部引用。這不是外部技術事實、發音、閱讀速度或學習效益的驗證。完整 English、zh_note、premises/checkpoint、Active sentence/cue/oracle 及每個連結正文的逐字引句保存在 audit.json。

## 實際讀取路徑

- `/var/folders/l6/44bf7nvs64j60f1mpyy88hdm0000gn/T/article-entailment-2x13kv72/intervals/annotation-reader-input/task.json`
- `/var/folders/l6/44bf7nvs64j60f1mpyy88hdm0000gn/T/article-entailment-2x13kv72/intervals/annotation-reader-input/article.en.md`
- `/var/folders/l6/44bf7nvs64j60f1mpyy88hdm0000gn/T/article-entailment-2x13kv72/intervals/annotation-reader-input/article.zh-TW.md`
- `/var/folders/l6/44bf7nvs64j60f1mpyy88hdm0000gn/T/article-entailment-2x13kv72/intervals/annotation-reader-input/page.en.html`
- `/var/folders/l6/44bf7nvs64j60f1mpyy88hdm0000gn/T/article-entailment-2x13kv72/intervals/annotation-reader-input/page.zh-TW.html`

## 內容核對

- 兩頁完整 annotation 可見文字逐組相同。
- 46 組完整 English 只移除 reading markup 後，與 English 正文逐字一致。
- 所有 paragraph links 的正文目標均存在。
- 兩語各五個 fenced/code trace 區塊與 generated HTML 一致；兩語的區塊也相同。
- 所有判定均以完整 annotation 為單位，沒有單獨把縮短 cue 當成定理。

## 逐段判定

### 第 1 段 — PASS_BOUNDED

可見中文：> 依 left endpoints 排序後，遇到 gap 就能讓前一段定案，因為未來 start 不會往回。

可見閱讀提示：> 閱讀提示（非獨立結論）：What makes a gap permanent?

正文支持（English）：> Sort the intervals by their left endpoints. Walk through that order, keeping the merged result in a list. A new interval either extends the result's last interval or starts a new one. The reason this works is stronger than "nearby intervals are easier to compare": once a gap appears, no later start can reach backward across it.

正文支持（繁中）：> 先依左端點排序所有區間，再按照這個順序走訪，用一個 list 保留合併結果。每個新區間不是延伸結果的最後一段，就是另開一段。這個方法成立的理由，比「相鄰區間比較方便」更明確：一旦出現間隙，後面的起點就不可能往回跨過它。

判讀：排序使 future starts 不遞減；第 5、7、8 段給出 gap 定案與只比較最後一段的因果鏈，checkpoint 在取得順序之後。

不授權的鄰近推論：看到任意輸入的 gap 就永久定案；註解明確限於排序後 scan。

已讀正文支援段落：1, 5, 7, 8。全部對應引句見 audit.json。

### 第 2 段 — PASS_BOUNDED

可見中文：> closed interval 包含兩端點；答案要保留 exact coverage，不能為了合成大區間而填滿 gap。

可見閱讀提示：> 閱讀提示（非獨立結論）：Which coverage must the result preserve?

正文支持（English）：> In LeetCode 56, Merge Intervals, each input pair [start, end] describes a closed interval: every position from start through end, including both endpoints. There are between 1 and 10,000 pairs, and their integer endpoints satisfy 0 <= start <= end <= 10000. Return non-overlapping intervals after merging overlaps. The returned intervals must cover exactly the positions covered by the input. Keeping everything inside one large interval would incorrectly fill gaps.

正文支持（繁中）：> 在 LeetCode 56, Merge Intervals 中，每組輸入 [start, end] 表示一個 closed interval：從 start 到 end 的所有位置，包含兩端點。輸入有 1 到 10,000 組區間，整數端點符合 0 <= start <= end <= 10000。將重疊部分合併後，回傳互不重疊的區間。回傳結果覆蓋的位置必須恰好等於輸入覆蓋的位置。若直接用一個大區間包住全部輸入，就會錯誤填滿原本的間隙。

判讀：closed、包含端點、合法範圍與 exact coverage 都保留；中文提醒不能填 gap，提示問的是必須保留的覆蓋。

不授權的鄰近推論：把所有輸入包進單一大區間，或把合法範圍視為 runtime validation。

已讀正文支援段落：2。全部對應引句見 audit.json。

### 第 3 段 — PASS_BOUNDED

可見中文：> 相接的 closed intervals 共享端點而合併；整數端點不代表只覆蓋整數點，[12,12] 也有覆蓋。

可見閱讀提示：> 閱讀提示（非獨立結論）：When does touching count as overlap?

正文支持（English）：> For example, [1,4] and [4,6] share position 4, so their replacement is [1,6]. But [1,4] and [5,6] have a gap between them and remain separate. Integer endpoints do not mean that the interval contains only integer points. A zero-length interval such as [12,12] still covers its endpoint. The problem's examples explicitly count touching endpoints as overlap. Original problem and boundary example.

正文支持（繁中）：> 例如，[1,4] 和 [4,6] 都包含位置 4，所以要合成 [1,6]。但 [1,4] 和 [5,6] 之間有間隙，必須分開。端點是整數，不代表區間只包含整數位置。長度為零的區間，例如 [12,12]，仍然覆蓋它的端點。題目範例明確把端點相接視為重疊。原題與邊界範例。

判讀：英文範例保留 [1,4]/[4,6]、[5,6] 與 [12,12]；premise 指定連續 closed interval，Active 與 oracle 以共享位置解釋 touching。

不授權的鄰近推論：整數端點相鄰就合併，或 zero-length interval 沒有覆蓋。

已讀正文支援段落：2, 3。全部對應引句見 audit.json。

### 第 4 段 — PASS_BOUNDED

可見中文：> 輸入可能晚到連接段；此實作選擇回傳 start order 並保留 caller input，後者不是題目要求。

可見閱讀提示：> 閱讀提示（非獨立結論）：Which guarantees come from the implementation?

正文支持（English）：> Input order carries no useful guarantee. An interval that connects two others may arrive after both. We will return intervals in increasing start order and preserve the caller's input, although preserving it is an implementation choice rather than a requirement stated by the problem.

正文支持（繁中）：> 輸入順序沒有提供可利用的保證。能連接另外兩段的區間，可能在那兩段之後才出現。我們會依起點遞增順序回傳結果，並保留呼叫端的輸入不變；保留輸入是這份實作的選擇，並不是題目明訂的要求。

判讀：沒有輸入順序保證與實作選擇保留 caller input 均明說；label 的 fresh-pair 做法由第 12 段正文供應。

不授權的鄰近推論：題目強制保留輸入，或輸入原順序可以讓 merge 定案。

已讀正文支援段落：2, 4, 12。全部對應引句見 audit.json。

### 第 5 段 — PASS_BOUNDED

可見中文：> start order 給出 left <= start，輸入合法性給出 start <= end；再依 start 與 right 分支。

可見閱讀提示：> 閱讀提示（非獨立結論）：Which inequalities permit the two cases?

正文支持（English）：> Suppose the current merged interval is [left, right], and the next interval is [start, end]. If starts arrive in increasing order, then left <= start. Because each input also satisfies start <= end, two cases remain.

正文支持（繁中）：> 假設目前合併區間是 [left, right]，下一個區間是 [start, end]。如果起點按遞增順序到來，就有 left <= start。每組輸入又都符合 start <= end，因此只剩兩種情況。

判讀：分支之前的 left<=start 來自 nondecreasing starts，start<=end 來自合法 pair；checkpoint 避免用更新後狀態倒推。

不授權的鄰近推論：只有 start<=right 就足以在任意順序保留 left。

已讀正文支援段落：2, 5, 9。全部對應引句見 audit.json。

### 第 6 段 — PASS_BOUNDED

可見中文：> 有 left <= start 且 start <= right 時，union 保留 left 並取 max(right,end)；內含段不能縮短群組。

可見閱讀提示：> 閱讀提示（非獨立結論）：Why keep the farther right endpoint?

正文支持（English）：> If start <= right, the new interval meets the existing coverage. Their union is [left, max(right, end)]: keep the earlier left endpoint and whichever right endpoint reaches farther. An interval contained inside the current one contributes no new positions. Assigning right = end unconditionally would incorrectly shorten coverage.

正文支持（繁中）：> 若 start <= right，新區間接上了目前的覆蓋範圍。兩者的 union 是 [left, max(right, end)]：保留較早的左端點，右端點則取伸得比較遠的那一個。完全內含於目前區間的新區間，不會增加任何覆蓋位置。若一律指定 right = end，就可能錯誤縮短覆蓋範圍。

判讀：中文、premise、Active 與 oracle 共同保留 left<=start、start<=right 及 max 更新；containment 反例解釋為何不能縮短。

不授權的鄰近推論：每次 right=end 都正確，或忽略 left<=start。

已讀正文支援段落：5, 6, 16。全部對應引句見 audit.json。

### 第 7 段 — PASS_BOUNDED

可見中文：> strict gap 後所有 future starts 都在更右側，無法回接目前群組；因此可以另開新段。

可見閱讀提示：> 閱讀提示（非獨立結論）：Why can later intervals not bridge this gap?

正文支持（English）：> If start > right, there is a gap. Every later interval starts at least as far right as start, so none can overlap [left, right] or bridge that gap. The current interval is finished. Start a new interval at [start, end].

正文支持（繁中）：> 若 start > right，兩段之間有間隙。後面所有區間的起點都至少和 start 一樣靠右，因此不可能與 [left, right] 重疊，也無法跨回這個間隙。目前這段已經定案。從 [start, end] 另開一段。

判讀：start>right 加 future starts>=start 才授權 final；Active sentence 把兩個條件直接寫入，oracle 也給出不等式鏈。

不授權的鄰近推論：僅憑不相交就否定任意尚未排序區間回接的可能。

已讀正文支援段落：5, 7, 9。全部對應引句見 audit.json。

### 第 8 段 — PASS_BOUNDED

可見中文：> 只查最後一段，是因為較早各段已被跨過的 gap 隔開；延伸 right 不會讓 left 往回。

可見閱讀提示：> 閱讀提示（非獨立結論）：Why inspect only the last result interval?

正文支持（English）：> This ordering also explains why only the last result interval needs inspection. Earlier result intervals already ended before a gap that the scan crossed. The current start and every future start are beyond those gaps. A growing last interval may reach farther right, but its left endpoint never moves backward to join an earlier result interval.

正文支持（繁中）：> 這個順序也解釋了為什麼只需檢查結果的最後一段。更早的結果區間，早已結束在掃描曾跨過的間隙之前。目前與未來的起點都位於那些間隙之後。最後一段可以繼續往右延伸，但它的左端點不會往回移動，接上更早的結果區間。

判讀：先前 pair 已被 strict gaps 隔開，last 的 left 不往回移動，因此向右延伸不會接回先前答案；checkpoint 在前一分支完成後。

不授權的鄰近推論：只因 list 上相鄰，就可以省略所有其他比較。

已讀正文支援段落：6, 7, 8, 10。全部對應引句見 audit.json。

### 第 9 段 — PASS_BOUNDED

可見中文：> sort 是取得 nondecreasing starts 的一種機制；正確性需要這個順序保證，不要求所有演算法都 sort。

可見閱讀提示：> 閱讀提示（非獨立結論）：Is sorting the only way to obtain order?

正文支持（English）：> Sorting by start is one way to obtain the needed order; it is not a claim that every correct algorithm must sort. The important permission is that future starts cannot be smaller than the start currently being processed.

正文支持（繁中）：> 依起點排序，是取得所需順序的一種方式；這不表示所有正確演算法都必須排序。真正允許我們做決定的條件，是未來的起點不會小於目前正在處理的起點。

判讀：完整註解把順序需求限於本文保留 left 的 scan；Active oracle 指出可靠 sorted-input contract 也能供應前提。

不授權的鄰近推論：所有正確演算法都必須排序；或只要省略 library sort 就失去正確性。

已讀正文支援段落：5, 7, 9, 41。全部對應引句見 audit.json。

### 第 10 段 — PASS_BOUNDED

可見中文：> merged 的 pair 代表整個 connected group；merged[-1][1] 是群組最遠端，不一定是上一個原始 pair 的 end。

可見閱讀提示：> 閱讀提示（非獨立結論）：What does the last pair represent?

正文支持（English）：> Use ordered for a start-sorted list and merged for the partial answer. A pair in merged represents all coverage in one connected group of processed intervals, not necessarily one original input pair. merged[-1] selects its last pair, and merged[-1][1] selects that pair's right endpoint. The earlier pairs are finished; the last pair can still grow.

正文支持（繁中）：> 用 ordered 表示依起點排好的 list，用 merged 表示部分答案。merged 裡的一組端點，代表已處理區間中一整個相連群組的覆蓋範圍，不一定是某個原始輸入區間。merged[-1] 選取最後一組端點，merged[-1][1] 再選取那組的右端點。前面各段已經定案，最後一段還可能繼續長大。

判讀：群組 coverage、last slot 與 end slot 三者分工明確，更新後的 checkpoint 連至完整 invariant；oracle 否定 previous-original-pair 誤讀。

不授權的鄰近推論：merged[-1][1] 必然等於上一個原始 pair 的 end。

已讀正文支援段落：6, 8, 10, 22, 27。全部對應引句見 audit.json。

### 第 11 段 — PASS_BOUNDED

可見中文：> key=lambda interval: interval[0] 取 start；sorted 回傳新 outer list。equal starts 仍可用 max end 得到相同 union。

可見閱讀提示：> 閱讀提示（非獨立結論）：How do keys and equal starts affect the union?

正文支持（English）：> The ordering expression is sorted(intervals, key=lambda interval: interval[0]). The lambda is a small function: give it a pair and it returns that pair's first number. The sort uses those numbers as its comparison keys. Thus [8,10] receives key 8, while [1,4] receives key 1. Python evaluates the key once per input pair and returns a new outer list in ascending key order. Equal starts can appear in either order for this algorithm: retaining the larger end produces the same union. Python sorting documentation.

正文支持（繁中）：> 排序運算式是 sorted(intervals, key=lambda interval: interval[0])。lambda 是一個小函式：給它一組端點，它就回傳第一個數字。排序會把這些數字當作比較用的 key。因此 [8,10] 的 key 是 8，[1,4] 的 key 是 1。Python 對每組輸入只計算一次 key，並回傳依 key 遞增排列的新外層 list。對這個演算法來說，相同起點的區間用哪個順序都可以：保留較大的右端點，就會得到相同的 union。Python sorting 文件。

判讀：lambda 取 start、每對計算一次 key、新 outer list 及 equal-start max-end 規則都與正文一致；並未宣稱 Python 實際打亂 equal keys。

不授權的鄰近推論：新 outer list 等於 deep copy，或這個算法需要 equal starts 的特殊次序。

已讀正文支援段落：6, 11。全部對應引句見 audit.json。

### 第 12 段 — PASS_BOUNDED

可見中文：> 新 outer list 仍共享 input pairs；本文 append fresh pair，讓後續 endpoint mutation 只改答案。

可見閱讀提示：> 閱讀提示（非獨立結論）：Which object receives the endpoint mutation?

正文支持（English）：> A new outer list does not imply new inner pairs. Its elements still refer to the original pair objects. When adding an answer interval, merged.append([start, end]) creates a fresh two-item list and places a reference to it at the end of merged. Later endpoint updates therefore modify an answer pair, not an input pair. Appending an original pair and then modifying it would share that mutation with the caller. Python assignment binds references rather than copying objects; list elements can be changed in place. Python lists and assignment.

正文支持（繁中）：> 外層 list 是新的，不代表內層的端點組也是新的。新 list 的元素仍然參照原本的端點組物件。加入答案區間時，merged.append([start, end]) 會建立一個新的兩元素 list，並把指向它的 reference 放到 merged 尾端。因此，之後更新端點時，改的是答案中的端點組，並不是輸入中的端點組。若直接 append 原始端點組再修改，呼叫端也會看到這個變動。Python assignment 綁定的是 reference，並不會複製物件；list 的元素可以原地修改。Python lists 與 assignment。

判讀：先共享 input pairs、再建立 fresh answer pair、最後寫 answer end slot 的物件鏈完整；Active 與 oracle 的 mutation 只針對後續 endpoint writes。

不授權的鄰近推論：sorted 自動複製 inner pairs，或 fresh outer list 就隔離了所有 mutation。

已讀正文支援段落：4, 11, 12。全部對應引句見 audit.json。

### 第 13 段 — PASS_BOUNDED

可見中文：> 這句引入 constructed input；它是待追蹤的例子，並不是實際執行證據。

可見閱讀提示：> 閱讀提示（非獨立結論）：Which constructed input will the trace follow?

正文支持（English）：> Consider this constructed input:

正文支持（繁中）：> 考慮這組自行構造的輸入：

判讀：constructed input 的定性與引句一致；只引入 trace，沒有把 constructed movie 當實際執行紀錄。

不授權的鄰近推論：文章中的 constructed trace 本身證明某次 runtime 實際發生。

已讀正文支援段落：13。全部對應引句見 audit.json。

### 第 14 段 — PASS_BOUNDED

可見中文：> sorted 產生 ordered 而不重排 intervals；scan 逐 pair 把兩個數字綁給 start、end。

可見閱讀提示：> 閱讀提示（非獨立結論）：What is produced before scanning begins?

正文支持（English）：> The call to sorted produces ordered; it does not rearrange intervals. The scan visits each pair in ordered, binding its two numbers to start and end.

正文支持（繁中）：> 呼叫 sorted 會產生 ordered，不會重新排列 intervals。掃描依序走訪 ordered 裡的每組端點，把兩個數字分別綁定到 start 與 end。

判讀：sorted 完成後才解包 ordered，且不重排 intervals；共享 inner objects 的 premise 並未被誤寫為新 pair。

不授權的鄰近推論：sorted 保留 outer list 原地順序只是因為它複製了所有 inner pairs。

已讀正文支援段落：11, 12, 14。全部對應引句見 audit.json。

### 第 15 段 — PASS_BOUNDED

可見中文：> 空答案先 append fresh [1,4]，得到 [[1,4]]；此分支不需要讀取既有 last endpoint。

可見閱讀提示：> 閱讀提示（非獨立結論）：How is the first pair stored safely?

正文支持（English）：> For [1,4], there is no last answer pair. Create [1,4] and append it. The answer is now [[1,4]]. No endpoint lookup is needed while the answer is empty.

正文支持（繁中）：> 處理 [1,4] 時，答案還沒有最後一組端點。建立 [1,4] 並 append，答案就成為 [[1,4]]。答案是空的時候，不需要讀取任何既有端點。

判讀：前態為空，先判空再建立 [1,4]，結果 [[1,4]]；第 20 段與程式的 or 次序說明為何沒有空 last lookup。

不授權的鄰近推論：先讀 merged[-1][1] 再決定是否為空。

已讀正文支援段落：15, 20。全部對應引句見 audit.json。

### 第 16 段 — PASS_BOUNDED

可見中文：> containment 時 max(4,3)=4，所以 merged 維持 [[1,4]]；改成 3 會縮掉原本覆蓋。

可見閱讀提示：> 閱讀提示（非獨立結論）：Why does containment leave the answer unchanged?

正文支持（English）：> For [2,3], compare 2 with the last right endpoint 4. They overlap, but max(4,3) is 4. Writing that value back leaves merged equal to [[1,4]]. This is the containment case; moving the endpoint to 3 would lose coverage between 3 and 4.

正文支持（繁中）：> 處理 [2,3] 時，把 2 和最後一段的右端點 4 比較。兩段重疊，但 max(4,3) 是 4。把這個值寫回後，merged 仍然是 [[1,4]]。這是內含情況；若把右端點改成 3，就會失去 3 到 4 之間的覆蓋範圍。

判讀：前態 [1,4] 與新 [2,3] 明示，max(4,3)=4 保留覆蓋；丟失 (3,4] 的反事實有正文數值支撐。

不授權的鄰近推論：內含段的 end 可以直接覆蓋群組 end。

已讀正文支援段落：6, 15, 16。全部對應引句見 audit.json。

### 第 17 段 — PASS_BOUNDED

可見中文：> 處理 [3,6] 時 max(4,6)=6，得到 [[1,6]]；排序前提讓 left 保持 1。

可見閱讀提示：> 閱讀提示（非獨立結論）：Which slot changes during extension?

正文支持（English）：> For [3,6], 3 <= 4, so write max(4,6), which is 6, into the last pair's end slot. merged becomes [[1,6]]. The stored left endpoint stays 1 because sorting already established that no new left endpoint is smaller.

正文支持（繁中）：> 處理 [3,6] 時，因為 3 <= 4，所以把 max(4,6)，也就是 6，寫入最後一組端點的結束位置。merged 變成 [[1,6]]。儲存的左端點仍然是 1，因為排序已經確保新區間的左端點不會更小。

判讀：前態、3<=4、max(4,6)=6、end slot 與 [[1,6]] 相互一致；left 保持 1 的理由是排序順序。

不授權的鄰近推論：extend 分支也應把 left 改成 incoming start 3。

已讀正文支援段落：5, 6, 16, 17。全部對應引句見 audit.json。

### 第 18 段 — PASS_BOUNDED

可見中文：> closed intervals 的 equality 也 overlap：[6,8] 與 [8,10] 連續把答案延伸至 [[1,10]]。

可見閱讀提示：> 閱讀提示（非獨立結論）：Why do both touching intervals extend the group?

正文支持（English）：> For [6,8], the start equals the stored end. The closed intervals share 6; write max(6,8) = 8. The answer becomes [[1,8]]. For [8,10], the same touching rule extends it to [[1,10]].

正文支持（繁中）：> 處理 [6,8] 時，起點恰好等於已儲存的終點。這兩個 closed intervals 共有位置 6，所以寫入 max(6,8) = 8，答案變成 [[1,8]]。處理 [8,10] 時，同樣的相接規則會把它延伸成 [[1,10]]。

判讀：先 [[1,6]] 再 [[1,8]] 再 [[1,10]] 的時序明確；equality 因 closed endpoints 共享位置而 overlap。

不授權的鄰近推論：6==6 或 8==8 屬於 strict gap。

已讀正文支援段落：3, 17, 18。全部對應引句見 audit.json。

### 第 19 段 — PASS_BOUNDED

可見中文：> 12 > 10 形成 gap，append [12,12] 後得到兩段；最後一段早已存在 merged，不需額外 flush。

可見閱讀提示：> 閱讀提示（非獨立結論）：Why is no final flush needed?

正文支持（English）：> For [12,12], 12 > 10. There is a gap, so append a fresh [12,12] without changing [1,10]. merged becomes [[1,10], [12,12]]. The loop then runs out of input and returns that list. The last interval is already stored, so no final flush is needed.

正文支持（繁中）：> 處理 [12,12] 時，12 > 10。兩者有間隙，因此 append 新建的 [12,12]，而不修改 [1,10]。merged 變成 [[1,10], [12,12]]。迴圈接著耗盡輸入，回傳這個 list。最後一段已經存在答案中，因此不必在最後再做一次 flush。

判讀：12>10、fresh [12,12]、兩段結果及耗盡後 return 的順序一致；Active oracle 以最後一段已儲存解釋無 final flush。

不授權的鄰近推論：尚未定案表示最後一段還沒放進 merged，必須再 append 一次。

已讀正文支援段落：3, 7, 18, 19。全部對應引句見 audit.json。

### 第 20 段 — PASS_BOUNDED

可見中文：> or 的 short-circuit 先保護空 list；非空時用 start > last end 分 gap，因此 else 包含 equality。

可見閱讀提示：> 閱讀提示（非獨立結論）：Which operand prevents an empty-list lookup?

正文支持（English）：> not merged is true for an empty list. Python's or stops once its left side is true, so the first iteration never evaluates merged[-1][1] on an empty list. After that first append, the second condition tests for a strict gap. The else therefore includes equality, and max returns the larger of the existing end and the incoming end. Python truth testing and short-circuit evaluation.

正文支持（繁中）：> 當 list 是空的，not merged 就是 true。Python 的 or 一旦左邊成立就會停止求值，所以第一次迭代不會對空 list 執行 merged[-1][1]。第一次 append 之後，第二個條件負責檢查嚴格間隙。因此 else 包含端點相等的情況，max 則回傳目前終點與新終點中較大的值。Python truth testing 與 short-circuit evaluation。

判讀：or 左側 not merged 與右側 endpoint lookup 的求值順序明確；非空時 strict > 的補集保留 equality，Active 受此確切 expression 限定。

不授權的鄰近推論：任意調換 or operands 仍可避免空 lookup，或 else 排除 touching。

已讀正文支援段落：3, 6, 15, 20。全部對應引句見 audit.json。

### 第 21 段 — PASS_BOUNDED

可見中文：> type hints 不驗證每組長度；兩端點來自 problem contract。[] 回傳可行，但 empty input 不在題目限制內。

可見閱讀提示：> 閱讀提示（非獨立結論）：What do type hints leave unenforced?

正文支持（English）：> The type hints describe nested integer lists; they do not validate input at runtime or specify that each inner list has exactly two items. That two-endpoint requirement comes from the problem contract. It also returns [] for an empty input, although that input lies outside LeetCode's stated constraints.

正文支持（繁中）：> type hints 描述的是巢狀整數 lists；它們不會在執行時驗證輸入，也沒有規定每個內層 list 必須剛好有兩個元素。兩端點要求來自題目契約。對空輸入，這個方法也會回傳 []，不過空輸入不在 LeetCode 明訂的限制範圍內。

判讀：type hints 不做 runtime validation、也不表達每對長度；空輸入位於題目限制外，但初始化加零次迭代解釋回傳 []。

不授權的鄰近推論：List[List[int]] 驗證每一 inner list 正好長度二，或 empty input 是題目合法案例。

已讀正文支援段落：2, 21, 23, 26。全部對應引句見 audit.json。

### 第 22 段 — PASS_BOUNDED

可見中文：> loop invariant 在每次 iteration 結束後成立：merged 是 processed union，start-ordered 且不重疊，只有最後一段仍可能變。

可見閱讀提示：> 閱讀提示（非獨立結論）：When does the invariant describe the partial answer?

正文支持（English）：> Use this English loop invariant at the checkpoint immediately after each iteration: "merged contains the exact union of the processed intervals as start-ordered, non-overlapping intervals; all but its last interval are final against every unprocessed interval." Here, union means all positions covered by at least one interval. The union property describes the required coverage; the invariant also states when the partial answer is valid and which pieces can no longer change.

正文支持（繁中）：> 在每次迭代剛結束的檢查點，使用這個 English loop invariant："merged contains the exact union of the processed intervals as start-ordered, non-overlapping intervals; all but its last interval are final against every unprocessed interval." 這裡的 union，表示至少被一個區間覆蓋的所有位置。union 性質描述結果必須保留的覆蓋範圍；loop invariant 還進一步指明，部分答案在哪個時點成立，以及哪些部分不會再改變。

判讀：立即 post-iteration 的 checkpoint、processed 前綴、exact union、start order、non-overlap 及除 last 外 final 全部保留；Active oracle 補齊短句未單列的性質。

不授權的鄰近推論：只有 coverage 相等就等於完整 invariant，或在更新中途任意狀態套用。

已讀正文支援段落：5, 7, 10, 22, 24, 25。全部對應引句見 audit.json。

### 第 23 段 — PASS_BOUNDED

可見中文：> 初始化時 empty result 精確覆蓋 empty processed set；第一輪存入一段後，它本身就是 exact union。

可見閱讀提示：> 閱讀提示（非獨立結論）：How does initialization establish the invariant?

正文支持（English）：> Before processing anything, the empty result covers exactly the empty set of processed intervals. There are no finalized pairs to contradict the invariant. The first iteration creates the initial interval, which is its own exact union.

正文支持（繁中）：> 還沒處理任何區間時，空答案恰好覆蓋空的已處理集合。此時沒有任何已定案的端點組會違反 loop invariant。第一次迭代建立初始區間，而單一區間本身就是它的完整 union。

判讀：loop 前空集合與第一輪 append 後分別說明，沒有假稱 loop 前真的完成過 iteration；第 15 段供應初次存入機制。

不授權的鄰近推論：空狀態需要不存在的 last pair 才能建立 base case。

已讀正文支援段落：15, 22, 23。全部對應引句見 audit.json。

### 第 24 段 — PASS_BOUNDED

可見中文：> overlap 分支以保留 left、取 max end 維持 exact union；start <= right 排除新增內部 gap，舊 gap 也仍分隔較早結果。

可見閱讀提示：> 閱讀提示（非獨立結論）：Which boundaries preserve the invariant during overlap?

正文支持（English）：> For an overlap, replacing [left,right] with [left,max(right,end)] adds exactly the new interval's positions. There is no gap inside that replacement because start <= right. Its left boundary is unchanged, so it remains separated from all earlier answer pairs. No earlier pair becomes reachable by a later start. The invariant survives.

正文支持（繁中）：> 遇到重疊時，把 [left,right] 換成 [left,max(right,end)]，增加的恰好是新區間帶來的位置。因為 start <= right，替換後的區間內部不會出現間隙。它的左邊界不變，所以仍然和更早的所有答案區間分離。較晚到來的起點也不可能回頭接上更早的端點組。因此 loop invariant 仍然成立。

判讀：沿用已排序與分支前 invariant，overlap 更新維持 exact union；left 不變配合先前 gap 保留 earlier separation。

不授權的鄰近推論：start<=right 單獨在任意順序就保證 replacement 無缺失。

已讀正文支援段落：5, 6, 8, 22, 24。全部對應引句見 audit.json。

### 第 25 段 — PASS_BOUNDED

可見中文：> strict gap 時 append 只加入新段；future starts >= start 使舊 last pair 定案，新 pair 接手未定案角色。

可見閱讀提示：> 閱讀提示（非獨立結論）：Which pair becomes final after a gap?

正文支持（English）：> For a strict gap, appending [start,end] preserves all previous coverage and adds exactly the new interval. It is separate from the last pair, hence also from the pairs farther left. Future starts are at least start, so the old last pair is now final. The newly appended pair becomes the only unfinished pair.

正文支持（繁中）：> 遇到嚴格間隙時，append [start,end] 會保留所有既有覆蓋，再加入恰好等於新區間的範圍。新區間和原本最後一組端點分離，因此也和更左邊的端點組分離。未來起點都至少是 start，所以原本最後一組端點現在已經定案。新加入的端點組成為唯一尚未定案的一段。

判讀：strict gap 在已排序、non-overlapping merged 前態下成立；append 保存舊 coverage，新段與 farther-left pairs 分離，future-start 界使舊 last final。

不授權的鄰近推論：只從兩段分離就可在無順序保證時定案。

已讀正文支援段落：7, 22, 25。全部對應引句見 audit.json。

### 第 26 段 — PASS_BOUNDED

可見中文：> 每輪消耗一對有限輸入，終止時 processed 等於全部輸入；因此 exact union 與 non-overlap 變成完整答案性質。

可見閱讀提示：> 閱讀提示（非獨立結論）：What changes at termination?

正文支持（English）：> Each iteration consumes one of the finite n input pairs. At termination every pair has been processed. Exact coverage and pairwise non-overlap now apply to the whole input, so merged is the required result. "Unfinished" describes possible future extension, not missing output data.

正文支持（繁中）：> 每次迭代會消耗有限 n 組輸入中的一組。迴圈終止時，所有端點組都已處理，因此精確覆蓋與兩兩不重疊的性質適用於完整輸入，merged 就是所需答案。「尚未定案」指的是未來還可能延伸，並不是輸出資料還沒存入。

判讀：有限 n 每輪消耗一對，加維持 invariant，到 input 耗盡才把 processed properties 升為全體答案；unfinished 明確非 missing output。

不授權的鄰近推論：loop 一定結束就足夠證明答案正確，無需 invariant preservation。

已讀正文支援段落：22, 23, 24, 25, 26。全部對應引句見 audit.json。

### 第 27 段 — PASS_BOUNDED

可見中文：> 不能拿 previous original end 當群組 end；[[1,10],[2,3],[4,5]] 中，群組早已到 10，不應在 4 與 3 間判 gap。

可見閱讀提示：> 閱讀提示（非獨立結論）：Which endpoint prevents the false gap?

正文支持（English）：> A tempting mistake is comparing each new start with the previous original interval's end. With [[1,10], [2,3], [4,5]], that compares 4 with 3 and invents a gap. The current group actually reaches 10, so all three belong to [1,10]. The answer must retain the largest reached endpoint of the whole group, which the max update maintains.

正文支持（繁中）：> 一個容易犯的錯，是把新起點和前一個原始區間的終點比較。對 [[1,10], [2,3], [4,5]] 而言，這樣會拿 4 和 3 比較，憑空認定有間隙。目前群組其實已經覆蓋到 10，所以三段都屬於 [1,10]。答案必須記住整個群組已到達的最大右端點，而 max 更新正是維護這個資訊。

判讀：[[1,10],[2,3],[4,5]] 的錯誤比較 4 與 3、正確 group end 10 都精確；Active sentence 與 oracle 用整群最大端點解釋。

不授權的鄰近推論：前一 original end 就代表整個群組可達的最遠位置。

已讀正文支援段落：6, 10, 16, 27。全部對應引句見 audit.json。

### 第 28 段 — PASS_BOUNDED

可見中文：> 對任意輸入直接套同一 scan 會失去左側覆蓋；[[5,6],[1,2]] 違反 stored left 較早的前提。

可見閱讀提示：> 閱讀提示（非獨立結論）：Which missing order premise loses coverage?

正文支持（English）：> Dropping the sort also breaks the reasoning. For [[5,6], [1,2]], the same code sees 1 <= 6 and keeps [5,6], losing [1,2]. Its merge formula assumed that the stored left endpoint came first. Neither the formula nor the invariant authorizes using it in arbitrary input order.

正文支持（繁中）：> 省略排序也會破壞推理。對 [[5,6], [1,2]]，同一份程式會看到 1 <= 6，保留 [5,6]，因而遺失 [1,2]。合併公式原本假設已儲存的左端點比較早。無論公式或 loop invariant，都沒有允許在任意輸入順序下這樣使用。

判讀：反例精確限於相同保留 left 的 scan 且缺少其他順序保證；數值 1<=6 造成遺失 [1,2]，並未否定所有免排序法。

不授權的鄰近推論：任意 no-sort algorithm 都不可能正確。

已讀正文支援段落：5, 6, 9, 28。全部對應引句見 audit.json。

### 第 29 段 — PASS_BOUNDED

可見中文：> 成本模型定義 n、k，並將有界端點比較、reference 讀寫、固定 pair 建立視為常數；Big O 描述上界成長。

可見閱讀提示：> 閱讀提示（非獨立結論）：Which operations are constant in this cost model?

正文支持（English）：> Let n be the input interval count and k the returned interval count, with k <= n. Count a bounded endpoint comparison, a reference read/write, and a fixed two-slot pair creation as constant work. Endpoints are bounded integers here, so arbitrary-length integer arithmetic is not part of this model. Big O gives an upper growth bound up to a constant factor; O(n) means that doubling the input increases that bound by a factor of two.

正文支持（繁中）：> 令 n 為輸入區間數量，k 為回傳區間數量，且 k <= n。把有界端點的一次比較、一次 reference 讀寫，以及建立固定兩個位置的端點組，都視為常數工作。這裡的端點是有界整數，因此模型不包含任意長度整數的運算成本。Big O 描述忽略常數倍後的成長上界；O(n) 表示輸入加倍時，這個上界也按兩倍成長。

判讀：n/k、k<=n 與 bounded endpoints/reference/fixed-pair 常數模型齊備；加倍說的是線性上界函數，未聲稱每次實測時間恰好加倍。

不授權的鄰近推論：O(n) 是固定 runtime 值，或 arbitrary-length integer 操作都無條件常數。

已讀正文支援段落：2, 29。全部對應引句見 audit.json。

### 第 30 段 — PASS_BOUNDED

可見中文：> scan 每輪固定上限次數操作，不搜尋 merged；直接選 last slot，最多建立 n 對，結果留 k 對。

可見閱讀提示：> 閱讀提示（非獨立結論）：What work repeats once per input pair?

正文支持（English）：> The scan visits n pairs. Each iteration performs a bounded number of endpoint reads, comparisons and writes. It never searches through merged; selecting its last slot uses the stored position directly. At most n new pairs are created, and exactly k remain in the result.

正文支持（繁中）：> 掃描會走訪 n 組端點。每次迭代都只做固定上限次數的端點讀取、比較與寫入。它從不搜尋整個 merged；選取最後一個位置，直接使用的是已知位置。最多建立 n 組新端點，最後有恰好 k 組留在結果中。

判讀：n visits、bounded endpoint 操作與 direct last-slot access 分開列計；premise 明確保留下一段 append aggregate，沒有把 resize 偷算為單次常數。

不授權的鄰近推論：每輪含 append 的 worst-case 成本都固定常數，或需搜尋 merged 才找到 last。

已讀正文支援段落：29, 30, 31。全部對應引句見 audit.json。

### 第 31 段 — PASS_BOUNDED

可見中文：> append 的擴容複製要合計：固定 r<1 使幾何和 <= C/(1-r)，再用 C=O(k) 加上 k 次寫入得 O(k)；單次仍可能昂貴。

可見閱讀提示：> 閱讀提示（非獨立結論）：Why is total append work linear?

正文支持（English）：> List append needs an aggregate argument. A Python list stores references in an array with some spare slots. Most appends fill one spare slot. When full, growth may allocate a larger array and copy its references. CPython reserves extra capacity proportional to the size, rather than copying on every append. Looking backward from a final capacity C, earlier large capacities are bounded by a fixed ratio r < 1 of the next capacity. For a doubling illustration, r = 1/2. The total copied references are bounded by a sum S = C + rC + r^2 C + ... + r^m C. Subtract rS: all middle terms cancel, leaving S - rS = C - r^(m+1) C <= C. Therefore S <= C/(1-r). The fixed ratio contributes a constant multiplier, and proportional spare capacity makes C = O(k) for k appends. The few smallest allocations add only fixed work. Adding the k ordinary slot writes gives O(k) total append work, though one particular append can cost more than constant time. This is the meaning of amortized cost. CPython's actual growth is milder than doubling. CPython 3.14 list growth implementation.

正文支持（繁中）：> list append 的成本需要合計來看。Python list 把 references 放在帶有備用位置的 array 中。大部分 append 只需填入一個備用位置。容量用完時，擴容可能配置更大的 array，並複製既有 references。CPython 會依大小比例預留額外容量，不會每次 append 都複製。從最後容量 C 往回看，較早的大容量都有一個上界：不超過下一次容量的固定比例 r < 1。以每次加倍為示意，r = 1/2。總複製 reference 數量不超過 S = C + rC + r^2 C + ... + r^m C。減去 rS 後，中間項全部消去，得到 S - rS = C - r^(m+1) C <= C。因此 S <= C/(1-r)。固定比例只貢獻常數倍，而按比例預留容量，讓最後容量符合 C = O(k)，其中 k 是 append 次數。最初幾次小配置只增加固定工作。再加上 k 次一般位置寫入，總 append 工作就是 O(k)，即使某一次 append 可能超過常數時間。這就是 amortized cost 的意思。CPython 實際擴容的幅度比每次加倍小。CPython 3.14 list 擴容實作。

判讀：append-only、fixed r<1、C=O(k)、小配置固定成本與 k slot writes 共同封閉幾何和推導；doubling 被標成示意，Active 不把 aggregate 換成每次 worst-case。

不授權的鄰近推論：每一次 append 都 worst-case O(1)，或 CPython 每次擴容恰好加倍。

已讀正文支援段落：29, 31。全部對應引句見 audit.json。

### 第 32 段 — PASS_BOUNDED

可見中文：> 概念 balanced merge 中，兩個指標只前進使 merge 為 O(a+b)；每層 O(n)、約 log n 層，得到 O(n log n)。

可見閱讀提示：> 閱讀提示（非獨立結論）：How do merge work and level count combine?

正文支持（English）：> Ordering dominates the worst-case time. For this analysis, use CPython's adaptive merge-based sort; it recognizes already ordered stretches, called runs, and combines neighboring runs. To understand the n log n scale, consider a conceptual balanced merge plan. Combining sorted stretches of lengths a and b takes O(a+b) work: compare their front items, move the smaller, and advance its position until both are exhausted. Neither position moves backward. Across one level, each input item belongs to one merge, giving O(n) work. Stretch sizes grow as 1,2,4,8,...; after h doublings they reach 2^h. The number needed to reach n is about log2(n), so O(n) work across O(log n) levels gives O(n log n).

正文支持（繁中）：> 最壞時間成本主要來自排序。這裡分析 CPython 的 adaptive merge-based sort；它會辨識已排序的連續片段，也就是 runs，再合併相鄰 runs。要理解 n log n 的尺度，可以先看一個概念性的平衡合併計畫。合併長度為 a 與 b 的已排序片段，需要 O(a+b) 工作：比較兩邊最前面的元素，移動較小者，然後往前推進那一邊的位置，直到兩邊都耗盡。兩個位置都不會往回走。同一層中，每個輸入元素只屬於一次合併，因此整層工作是 O(n)。片段大小按 1,2,4,8,... 成長；加倍 h 次後，大小會到 2^h。要達到 n，大約需要 log2(n) 次，所以每層 O(n)，乘上 O(log n) 層，就得到 O(n log n)。

判讀：指標只前進解釋 O(a+b)，每層元素一次與 doubling 解釋兩個成本因子；premise/Active oracle 明確是 conceptual balanced plan。

不授權的鄰近推論：實際 CPython 恰好每層等分，或一個 O(n) merge 就推出整個 sort 線性。

已讀正文支援段落：29, 32。全部對應引句見 audit.json。

### 第 33 段 — PASS_BOUNDED

可見中文：> Powersort 的細分層級約以 log n 為界，路徑層級下降避免同層重複計費；按參與 items 分攤 merge work 得總界。

可見閱讀提示：> 閱讀提示（非獨立結論）：Why can an item avoid repeated charges at one level?

正文支持（English）：> The balanced picture is conceptual; CPython 3.14 actually uses natural runs and a Powersort merge schedule. Its schedule also has logarithmically many levels. Picture the n input positions split into halves, then quarters, then eighths. Assign each boundary between adjacent runs the first subdivision level that separates their midpoints. Nonempty neighboring runs have midpoints at least one position apart. Once cell width n/2^h reaches one, those midpoints must be separated, so boundary levels are bounded by about log2(n). The schedule merges deeper boundaries before crossing a shallower one. Along an item's path through these merges, levels decrease; the item cannot be charged repeatedly at one level. The final cleanup has only logarithmically many pending levels left. Charging each merge's O(a+b) work to its participating items therefore gives O(n log n) total merge work. This is cost accounting, not a claim that the Program Movie ran these internal merges.

正文支持（繁中）：> 平衡圖像只是概念模型；CPython 3.14 實際使用 natural runs 與 Powersort merge schedule。這個排程的層數同樣按對數成長。想像把 n 個輸入位置先切成兩半，再切成四份、八份。每個相鄰 run 之間的邊界，都指定為「第一次把兩個 run 中點分開」的細分層級。非空相鄰 runs 的中點至少相隔一個位置。一旦每格寬度 n/2^h 降到一，這些中點必定已經分開，因此邊界層級大約以 log2(n) 為上界。排程會先合併較深的邊界，再跨越較淺的邊界。沿著某個元素經歷的合併路徑，層級會下降，不會在同一層反覆計費。最後清理時，也只剩對數數量的待處理層級。因此，把每次合併的 O(a+b) 工作分攤到參與元素，就得到 O(n log n) 的總合併工作。這是成本計算，並不是聲稱 Program Movie 執行了這些內部合併。

判讀：實際 schedule 與 conceptual picture 分開；中點至少距一、單位 cell 後已分開、路徑層級下降及 cleanup 的界共同支持 item charging。

不授權的鄰近推論：Program Movie 觀察到 CPython 內部這些 merge，或每個 item 在同一 level 可無限重複計費。

已讀正文支援段落：29, 32, 33。全部對應引句見 audit.json。

### 第 34 段 — PASS_BOUNDED

可見中文：> keys、runs 與有界短 run insertion 加線性工作；至多 n 邊界各用 log n 細分，與 merge、scan 合計仍為 O(n log n)。

可見閱讀提示：> 閱讀提示（非獨立結論）：Which extra sorting operations preserve the bound?

正文支持（English）：> Key extraction and identifying runs add linear work. CPython also extends short runs by insertion, but the target run length is bounded by 64, so each inserted item crosses only a fixed number of positions; this adds linear work too. Calculating each boundary level uses at most the same logarithmic number of subdivisions, on at most n boundaries. Thus the ordering step remains O(n log n) in the worst case; existing order can reduce work. Adding the O(n) interval scan preserves that bound. CPython sorting design, including its merge strategy.

正文支持（繁中）：> 計算 keys 與辨識 runs 另外增加線性工作。CPython 也會用 insertion 延長過短的 runs，但目標 run 長度最多是 64，所以每個插入元素只會跨過固定上限的位置數，這部分也只增加線性工作。每個邊界層級的計算，最多使用相同的對數次細分，而邊界數量不超過 n。因此排序步驟的最壞成本仍為 O(n log n)；既有順序可能減少工作。再加上 O(n) 的區間掃描，上界維持不變。CPython sorting 設計與 merge strategy。

判讀：keys/runs 線性、bounded <=64 insertion、至多 n boundaries 各 logarithmic subdivisions，加既有 merge/scan 上界，合計保留 worst-case 而允許已有順序較便宜。

不授權的鄰近推論：短 run insertion 沒有固定長度前提也可直接當線性，或任何輸入一定花同樣 n log n 工作。

已讀正文支援段落：29, 30, 31, 32, 33, 34。全部對應引句見 audit.json。

### 第 35 段 — PASS_BOUNDED

可見中文：> output 有 k 個 fresh two-slot pairs 與 outer list，為 O(k)；ordered 只持有 n 個 input references，不是另建 n 組 input pairs。

可見閱讀提示：> 閱讀提示（非獨立結論）：Which objects are new and which references are shared?

正文支持（English）：> The returned output occupies O(k) space: one outer list and k fresh two-slot pairs, including proportional spare capacity. ordered holds n references to input pairs. Those shared objects do not become n new pair allocations merely because ordered is new.

正文支持（繁中）：> 回傳輸出占用 O(k) 空間：一個外層 list，以及 k 個新建的兩元素端點組，包含按比例預留的容量。ordered 持有指向輸入端點組的 n 個 references。這些共用物件不會變成另外配置的 n 組端點，即使 ordered 是新建的也是如此。

判讀：O(k) output 明確含 outer list、fresh two-slot pairs 與 spare capacity；ordered 的 n references 沒被當成 n new inner allocations。

不授權的鄰近推論：ordered 是新 list 就意味它 deep-copies n pairs，或 output 是 O(1)。

已讀正文支援段落：12, 29, 31, 35。全部對應引句見 audit.json。

### 第 36 段 — PASS_BOUNDED

可見中文：> n 個 key slots 加上較短 run 的至多 2m 暫存；2m<=a+b<=n，合併逐次重用 buffer，所以按最大一次估 peak，而非累加每次配置。

可見閱讀提示：> 閱讀提示（非獨立結論）：Why does peak workspace follow one merge rather than their sum?

正文支持（English）：> During sorting, the key function's one result per input needs n key-reference slots. Our key is an existing bounded endpoint integer. To merge runs of lengths a and b, CPython copies the smaller remaining run into a buffer while writing the merged order back into the main array; it may first skip portions already in place. With m = min(a,b), this needs at most m key slots and m matching pair-reference slots: 2m <= a+b <= n. For eight items split into runs of four and four, that is at most four temporary keys and four matching references. Merges execute one at a time and reuse this buffer; when more space is needed, CPython releases the old dynamic buffer before allocating the larger one. Peak scratch storage therefore follows the largest individual merge, not the sum of all merges. Pending-run records contain fixed-size positions, lengths and levels; the logarithmic pending count derived above is also bounded by O(n). Together with the n key slots, these live arrays and records use O(n) sorting workspace. CPython key storage, merge-buffer reuse and smaller-run selection.

正文支持（繁中）：> 排序期間，key function 對每組輸入產生一個結果，需要 n 個 key-reference 位置。這裡的 key 是已存在的有界整數端點。合併長度為 a 與 b 的 runs 時，CPython 會把剩餘部分中較短的 run 複製到 buffer，同時將合併順序寫回主要 array；它可能先略過已經就定位的部分。令 m = min(a,b)，這最多需要 m 個 key 位置與 m 個對應的端點組 reference 位置：2m <= a+b <= n。例如八個元素分成長度四與四的 runs，最多暫存四個 keys 與四個對應 references。各次合併逐一執行，並重用這個 buffer；需要更多空間時，CPython 會先釋放舊的動態 buffer，再配置較大的 buffer。因此，scratch storage 的峰值取決於最大的一次合併，而不是所有合併的總和。待合併 run 的每筆紀錄只含固定大小的位置、長度與層級；前面推導的對數數量待處理紀錄，也在 O(n) 上界內。加上 n 個 key 位置後，同時存活的這些 arrays 與紀錄使用 O(n) sorting workspace。CPython key storage、merge-buffer reuse 與 smaller-run selection。

判讀：n keys、m=min(a,b) 與 2m<=n 的同時 slots 界，sequential reused buffer、先釋舊再擴與 pending-record 界，構成 O(n) live workspace 論證。

不授權的鄰近推論：每個 merge buffer 永久累加，或 key slots 可以從工作空間帳中消失。

已讀正文支援段落：11, 29, 32, 33, 36。全部對應引句見 audit.json。

### 第 37 段 — PASS_BOUNDED

可見中文：> sort 的 dynamic arrays 在 scan 前釋放；scan 留 ordered 並增長 O(k) output。auxiliary peak O(n)，含 output 為 O(n+k)=O(n)。

可見閱讀提示：> 閱讀提示（非獨立結論）：Which allocations remain live when the interval scan begins?

正文支持（English）：> The sort releases its dynamic key-reference array and merge buffer before the interval scan begins. During the scan, ordered remains live while the O(k) result grows; loop variables occupy constant space. Excluding the output, peak auxiliary space is O(n). Including the output, peak extra storage is O(n+k), hence O(n) because k <= n. Sorting workspace and answer growth occur in different phases, so their allocation totals must not be multiplied by the number of merges. CPython sort cleanup.

正文支持（繁中）：> 排序會在區間掃描開始前，釋放動態 key-reference array 與 merge buffer。掃描期間，ordered 仍然存活，而 O(k) 結果逐步成長；迴圈變數只占常數空間。不計輸出時，auxiliary space 的峰值是 O(n)。計入輸出時，額外儲存峰值是 O(n+k)，也就是 O(n)，因為 k <= n。Sorting workspace 與答案成長發生在不同階段，因此不能把配置總量乘上合併次數。CPython sort cleanup。

判讀：sort cleanup 先於 scan、ordered 與 growing output 同時存活、k<=n 與兩種空間邊界均明示；兩組 Active 與 oracle 都保留 live/phase accounting。

不授權的鄰近推論：把每次配置總量乘 merge 次數當 peak，或 O(n) auxiliary 已包含且可刪去 O(k) output。

已讀正文支援段落：12, 29, 31, 35, 36, 37。全部對應引句見 audit.json。

### 第 38 段 — PASS_BOUNDED

可見中文：> intervals.sort 省掉 sorted outer list 但會重排 caller list；sort workspace 仍可能成長，不能推成 constant auxiliary。

可見閱讀提示：> 閱讀提示（非獨立結論）：Does in-place sorting remove all auxiliary storage?

正文支持（English）：> Calling intervals.sort(...) instead would remove the separate sorted outer list but rearrange the caller's list. It would not establish constant auxiliary space: Python's sorting workspace can still grow with n. Changing mutation permission alone does not remove that cost. Python sorting behavior, CPython sorting memory.

正文支持（繁中）：> 若改呼叫 intervals.sort(...)，可以省下獨立的已排序外層 list，但會重排呼叫端的 list。這並不能證明 auxiliary space 是常數：Python 排序需要的 workspace 仍可能隨 n 成長。只改變是否允許修改輸入，不會消除這個成本。Python sorting 行為、CPython sorting 記憶體。

判讀：只換 intervals.sort 省 outer copy、改 caller order，sorting workspace 未被消除；Active oracle 精確否定 constant-space 的不當推論。

不授權的鄰近推論：in-place sorting 這個名稱本身就保證整體 O(1) auxiliary。

已讀正文支援段落：35, 36, 37, 38。全部對應引句見 audit.json。

### 第 39 段 — PASS_BOUNDED

可見中文：> repeated selection 用 used markers 反覆選最小剩餘 start，再送入相同 merge rule；同起點仍由 max end 處理。

可見閱讀提示：> 閱讀提示（非獨立結論）：How can selection construct the required order?

正文支持（English）：> A simpler way to construct the required order is repeated selection. Keep the input and a Boolean "used" marker for each pair. Scan all unused pairs to find a smallest remaining start, mark that pair used, then feed its endpoints into the same merge rule. Retain only the selected index and best start during each search. Choosing equal starts in any order remains valid because the end update keeps the maximum.

正文支持（繁中）：> 另一種較直觀的排序建構方法，是 repeated selection。保留輸入，並為每組端點準備一個 Boolean「是否已使用」標記。每次掃描所有尚未使用的端點組，找出剩餘起點最小的一組，將它標記為已使用，再把它的端點送入同一套合併規則。每次搜尋過程只需保留目前選中的索引與最佳起點。遇到相同起點，選擇順序仍然不影響正確性，因為終點更新會保留最大值。

判讀：每對 used marker、重掃 smallest unused start、selected index/best start 及 mark 後 merge 的時序完整；同起點仍依 max end。

不授權的鄰近推論：只保留 selected index 就能跳過 marker 儲存，或不標 used 仍能逐對消耗。

已讀正文支援段落：6, 9, 39。全部對應引句見 audit.json。

### 第 40 段 — PASS_BOUNDED

可見中文：> repeated selection 保留順序正確性，但 n 次選擇各查 n 標記為 n²；即使只掃剩餘也有 n(n+1)/2。markers O(n)，output O(k)。

可見閱讀提示：> 閱讀提示（非獨立結論）：Why does repeated selection cost quadratic work?

正文支持（English）：> This also produces nondecreasing starts, so the earlier correctness proof applies to the merge step. But finding the next pair repeatedly costs more. With n markers checked on each of n selections, there are n*n marker checks. Even a version that scans only the remaining candidates must inspect n + (n-1) + ... + 1 candidates. Pair the first and last counts: each pair totals n+1, yielding n(n+1)/2, which grows quadratically. This alternative takes O(n^2) time, O(n) auxiliary marker space, and O(k) output space with the same fresh-pair and append argument. It avoids relying on a sorting library, but does not improve this problem's worst-case resource bounds.

正文支持（繁中）：> 這個方法產生的起點順序同樣不遞減，因此前面的正確性證明仍適用於合併步驟。但反覆尋找下一組端點，成本較高。若每次選取都檢查 n 個標記，共選取 n 次，就有 n*n 次標記檢查。即使某個版本只掃描剩餘候選，也仍要檢查 n + (n-1) + ... + 1 組。把第一項與最後一項配對，每組總和都是 n+1，因此得到 n(n+1)/2，按平方成長。這個替代方案需要 O(n^2) 時間、O(n) 的標記 auxiliary space，以及 O(k) output space；新建端點組與 append 的推導沿用前面相同的論證。它可以不依賴 sorting library，但不會改善這題的最壞資源上界。

判讀：n 次選擇各查 n markers 或 triangular candidate sum 兩種界明確，搭 marker O(n)、fresh-pair O(k) 與 aggregate append；Active 的 quadratic 限於此反覆線性搜尋機制。

不授權的鄰近推論：只做 n selections 就是 O(n) total，或 O(n²) 時間會自動導致 O(n²) peak space。

已讀正文支援段落：29, 31, 35, 36, 37, 39, 40。全部對應引句見 audit.json。

### 第 41 段 — PASS_BOUNDED

可見中文：> 可靠的 nondecreasing starts 保證允許省略 ordering；本文保留 fresh answer pairs，使原地 end 更新不改 caller。scan O(n)，output 外 state O(1)。

可見閱讀提示：> 閱讀提示（非獨立結論）：What guarantee permits removing the ordering step?

正文支持（English）：> If a different input contract guarantees that intervals already arrive in nondecreasing start order, the useful adaptation is to skip ordering entirely. Feed each arriving pair directly into the same merge rule. The ordering premise now comes from the input producer; the gap proof and largest-end update remain unchanged. There are still n visits and at most n appends, so the scan takes O(n) time. With no ordered list and no sort workspace, it needs O(1) auxiliary state beyond the retained O(k) result. This adaptation keeps the shown implementation's fresh answer pairs, so its in-place endpoint updates cannot change the caller's pairs. This is preferable when the sorted-input guarantee is reliable; merely observing a few sorted examples is insufficient.

正文支持（繁中）：> 如果改變輸入契約，保證區間本來就按起點不遞減的順序到來，實用的調整就是完全省略排序。把每組到來的端點直接送入同一套合併規則。此時排序前提改由輸入提供者保證；間隙證明與最大右端點更新都不變。仍然只有 n 次走訪與最多 n 次 append，所以掃描時間是 O(n)。沒有 ordered list，也沒有 sort workspace，因此只需要 O(1) auxiliary state，另加保留的 O(k) 結果。這個調整保留所示實作新建答案端點組的做法，讓原地更新答案終點時不會改到呼叫端的端點組。當已排序輸入的保證可靠時，這個版本比較合適；只看到幾組已排序範例還不夠。

判讀：producer 可靠 nondecreasing contract 取代 sorting，保留 same merge/fresh pairs，n visits 加 aggregate appends 才得 O(n)；O(1) state 排除 O(k) retained output。

不授權的鄰近推論：幾組 sorted examples 等於輸入契約，或免排序就不需要 output 空間/可直接改 caller pairs。

已讀正文支援段落：6, 7, 12, 29, 30, 31, 35, 36, 37, 41。全部對應引句見 audit.json。

### 第 42 段 — PASS_BOUNDED

可見中文：> 面試回答把 sort 連到 future starts 不遞減；strict gap 後的定案來自這個前提。

可見閱讀提示：> 閱讀提示（非獨立結論）：Which premise should the sorting answer mention?

正文支持（English）：> Why sort by the start? "It makes future starts nondecreasing. After a strict gap, no future interval can connect to the interval we just finished."

正文支持（繁中）：> Why sort by the start? "It makes future starts nondecreasing. After a strict gap, no future interval can connect to the interval we just finished."

判讀：面試短答的 future-start 與 strict-gap 因果由第 5、7、9 段明確限定，沒有把 sort 提升為所有算法必要。

不授權的鄰近推論：面試回答只說比較方便就已說明永久定案。

已讀正文支援段落：5, 7, 9, 42。全部對應引句見 audit.json。

### 第 43 段 — PASS_BOUNDED

可見中文：> maximum end 保留整個 overlapping group 的覆蓋；contained interval 不能把群組終點往回拉。

可見閱讀提示：> 閱讀提示（非獨立結論）：What group information must an interview answer retain?

正文支持（English）：> Why keep the maximum end? "The last answer pair represents an entire overlapping group. A contained interval must not shorten that group's coverage."

正文支持（繁中）：> Why keep the maximum end? "The last answer pair represents an entire overlapping group. A contained interval must not shorten that group's coverage."

判讀：整個 overlapping group 與 contained interval 不縮 coverage 的關係，連至第 6、10、27 段；checkpoint 是每次 overlap 更新後。

不授權的鄰近推論：max 只是在比較前一 pair 與 current pair，無需保存群組狀態。

已讀正文支援段落：5, 6, 10, 27, 43。全部對應引句見 audit.json。

### 第 44 段 — PASS_BOUNDED

可見中文：> equality overlap 的原因是 closed intervals 同時包含共享端點。

可見閱讀提示：> 閱讀提示（非獨立結論）：What makes equality count as overlap?

正文支持（English）：> Why is equality overlap? "The intervals are closed. If a start equals the current end, both intervals contain that endpoint."

正文支持（繁中）：> Why is equality overlap? "The intervals are closed. If a start equals the current end, both intervals contain that endpoint."

判讀：equality 的共享 endpoint 機制明確限於 closed contract；reading cue 是提問而非脫離契約的定理。

不授權的鄰近推論：start==end 在任何半開/開區間表示法都自動 overlap。

已讀正文支援段落：2, 3, 44。全部對應引句見 audit.json。

### 第 45 段 — PASS_BOUNDED

可見中文：> 成本回答要同時保留 worst-case sort、含 amortized appends 的 scan，以及 O(n) auxiliary 加 O(k) output 的區別。

可見閱讀提示：> 閱讀提示（非獨立結論）：Which qualifications belong in the cost answer?

正文支持（English）：> What are the costs? "For this Python implementation, sorting costs worst-case O(n log n), and the scan costs O(n) including amortized appends. Auxiliary space is O(n), plus O(k) output space."

正文支持（繁中）：> What are the costs? "For this Python implementation, sorting costs worst-case O(n log n), and the scan costs O(n) including amortized appends. Auxiliary space is O(n), plus O(k) output space."

判讀：短答保留 this implementation、worst-case sort、amortized scan、auxiliary/output 分界；premise 連到 CPython、有界端點及整串推導。

不授權的鄰近推論：所有 Python 程式的排序或每次 append 都有同一無條件成本，或 auxiliary/output 可以混為常數。

已讀正文支援段落：29, 30, 31, 32, 33, 34, 35, 36, 37, 45。全部對應引句見 audit.json。

### 第 46 段 — PASS_BOUNDED

可見中文：> sorted-input 回答需以契約保證為前提；去掉 ordering 後保留同一 merge，O(1) 僅指 output 外 state。

可見閱讀提示：> 閱讀提示（非獨立結論）：Which sorted-input guarantee and space exclusion matter?

正文支持（English）：> What would change for sorted input? "I would remove the ordering step, keep the same merge rule, and obtain O(n) time with O(1) auxiliary state excluding the output."

正文支持（繁中）：> What would change for sorted input? "I would remove the ordering step, keep the same merge rule, and obtain O(n) time with O(1) auxiliary state excluding the output."

判讀：sorted input 的簡答由 premise 指定可靠 producer 保證，checkpoint 連至 n visits/append aggregate，且 O(1) 排除 retained O(k) result。

不授權的鄰近推論：看到已排序範例就可省略 ordering，或 O(1) state 等於整體 O(1) extra storage。

已讀正文支援段落：29, 30, 31, 41, 46。全部對應引句見 audit.json。

## 範圍限制

- No external references were opened; external factual provenance, CPython implementation conformance and source-document truth were not independently reverified.
- No repository, Owner/author review, previous Reader output or manifest was read.
- No learning benefit, reading speed, semantic score, authorship or pronunciation verdict is made. The repeated styling note about checked stress is not independently established by this packet.
- Local HTML parsing verifies supplied static content and links, not browser execution, CSS legibility or deployment state.
