# 作者首次完整交付報告

本次依 task.json 明列的四份 final instruction snapshots，從 LeetCode 200 statement 自行構建完整英文與繁中文章。未讀任何範文、editorial、community solution、repository article、其他作者或 observer 材料。這是作者的操作紀錄，並非強制檔案隔離或獨立 Reader 的證明。

## 實際檔案

- `article.first.en.md`：首次完整英文，保留原始標題及 detector 可見的格式。
- `article.en.md`：英文作者定稿。
- `article.first.zh-TW.md`：英文完成來源核對與作者批准後，才開始的首次完整繁中翻譯。
- `article.zh-TW.md`：繁中作者定稿；English interview Q&A 依指定 construction instructions 保留英文。
- `verify.py`：抽出英文完整 `Solution` 後執行的實際驗證器。
- `extracted_solution.py`：從本次英文定稿抽出的完整程式，未重寫成驗證專用解法。
- `runtime.json`、`runtime.stdout.log`、`runtime.stderr.log`：對最終英文檔案的實際執行結果。
- `initial.runtime.json`、`initial.runtime.stdout.log`、`initial.runtime.stderr.log`：標題修正前的首輪實際執行，完整保留。
- `sloptrim.first.json`、`sloptrim.final.json`、`sloptrim.approved.json`：實際 snapshot detector 的原稿、編輯後與批准版輸出。
- `editorial-review.json`：草稿／定稿 SHA-256、英文批准時間、翻譯開始時間、作者語意審查與修正。
- `output.json`：task 要求的四個真實 Boolean 欄位。

## 由問題推導的內容

目標是數四向 land path 的 connected components。先以底部橋接的 `101 / 111` 排除「只看上方與左方就決定新島」的捷徑，再推導完成一次 region search 的必要性。程式採 iterative DFS、獨立 Boolean matrix 與 mark-before-push；保留輸入，因此不必推定題目授權消耗地圖。主例 `1100 / 1101 / 0011` 同時涵蓋越界、水、已發現但尚未 examined 的 pending cell、避免重複 push，以及兩座島的完整 return。

本文分別證明 path-based grouping 與 inner/outer loop checkpoints，並從 `mn` 次 scan、`L` 次 pop、`4L` 次 neighbor tests 導出成本。Python runtime 解釋涵蓋獨立 row allocation、reference alias、tuple unpacking、append 的 `None`、pop 的回傳與 mutation、truth testing、negative indexing、short-circuit bounds。CPython list capacity／amortization 明確限定在 implementation。替代方法包括 recursive DFS、BFS、授權 mutation；改動條件包括 shortest land path 及 diagonal connectivity。

文章的 coordinate grids 與逐步 stack 值已直接給出完整狀態，本次未選擇額外圖檔，也未要求 image generation。沒有不存在的圖檔、figure slot 或 render 成功聲明。

## 來源與邊界

實際透過 Web 工具只開啟以下允許的 primary sources；未點 editorial 或 community solutions。以下 locator 支持原題與語言原語，搜尋策略、反例、proof 與 operation counting 為作者自行推導。

- [LeetCode statement](https://leetcode.com/problems/number-of-islands/)：Description 與 Constraints，四向連接、字串值、rectangle、兩個維度各 1 到 300。頁面亦提供兩個 official examples，驗證器使用其輸入與字面預期結果。
- [Python 3.14 data structures](https://docs.python.org/3.14/tutorial/datastructures.html#using-lists-as-stacks)：list append／pop、LIFO、front removal 的搬移成本。
- [Python 3.14 built-in types](https://docs.python.org/3.14/library/stdtypes.html#common-sequence-operations)：sequence repetition 只重複 references、mutable item assignment、negative indexing、空 list 的 truth value。
- [Python 3.14 Boolean operations](https://docs.python.org/3.14/library/stdtypes.html#boolean-operations-and-or-not)：`and` 的 short-circuit，支撐先測 bounds。
- [Python 3.14 assignment](https://docs.python.org/3.14/reference/simple_stmts.html#assignment-statements)：tuple pair unpacking 與 mutable item assignment。
- [Python 3.14 sys](https://docs.python.org/3.14/library/sys.html#sys.getrecursionlimit)：interpreter recursion limit；本文未宣稱所有環境都是同一固定上限。
- [Python 3.14 collections](https://docs.python.org/3.14/library/collections.html#collections.deque)：deque 兩端 append／pop 的約略 constant-time 性質與 list front removal 對照。
- [CPython v3.14.0 listobject.c](https://github.com/python/cpython/blob/v3.14.0/Objects/listobject.c)：`list_resize` proportional over-allocation、低於一半 capacity 才走 shrink，與 amortized append behavior。文章未聲稱此 allocation policy 是 Python language 保證。

官方 documentation 本次回傳標題為 Python 3.14.8；實際執行器為 CPython 3.14.6。兩者同為 Python 3.14；對內部政策的引用另外固定到 CPython v3.14.0。這不等同在 v3.14.0 binary 上執行，也沒有以本次執行測量所有 Python implementations 的 timing。

## 實際編輯及來源審查

CONTENT_REVIEWED：作者逐段比對 statement 與上述語言機制，並手動重建 witness、code、兩層 invariant 與成本推導。不是獨立 Reader review。

SLOPTRIM_RUN：實際執行所指定 snapshot 的 `scripts/detect.py`。首次 score 14，最後批准版 score 0；兩者均為 clean。這只是 style diagnostic，不作語意、作者身份或學習成效判決。對首次標記的 vocabulary、boldface、curly quotes、fragmented header，實際讀了同 snapshot 的 pattern reference。人工套用 reader-article supplement，保留有獨立教學用途的 worked states、API-to-state mapping、proof、成本推導及 interview recall。

保留的作者修正：移除 vague difficulty sentence；將 `_` 改以實際 identifier 描述；移除 interview questions 的粗體；替換 curly quotes；明確說明 pending-cell order 的條件；將標題從可能暗示「搜尋完才 increment」的文字改為「claim every cell, count each region once」。正文與 code 始終是在發現 seed 時 increment，outer proof checkpoint 是 search 結束後。標題修正發生於翻譯開始前。

英文批准時間與翻譯開始時間存於 `editorial-review.json`；四份 article 的實際 SHA-256 也存於同檔。已完成整份英文審查後，才產生繁中翻譯。

TRANSLATION_REVIEWED：作者按英文與同批來源核對條件、否定、四向與對角差異、discovery/examination、mark order、每個 trace state、bounds、complexity 與 mutation permission。實際 assertions 證明所有 Python fences、文字格線 fences 與來源 URL 順序一致。繁中定稿只補充 cell 的 English term 與 queue-layer counter 的中文機制說明；沒有改變演算法或數值。

## 實際驗證

RUNTIME_TESTED：`verify.py` 從英文定稿讀取唯一完整 `Solution` class，再 compile／exec。CPython 3.14.6 實際結果為 passed。

- 20 個字面與 practical statement-boundary cases：最小 land／water、水平與垂直 pair、對角、晚出現的 bridge、主 movie、row-alias discriminator、邊界不 wrap、ring、分離角落、兩個 statement examples，以及 300×300 全水、全陸地、checkerboard、合法長 snake、1×300、300×1。輸入逐次核對未被修改。
- 682 個 exhaustive 小輸入：所有 row、column 各 1 到 3 的 rectangles，全部 binary assignments。獨立 oracle 使用 all-pairs reachability closure，再數不同 reachable groups；沒有重用 DFS 解法。
- 200 個 seed 200 的 random 小輸入，最大 5×5，使用相同獨立定義 oracle；無 mismatch、無輸入 mutation。
- 透過 `sys.settrace` 擷取抽出程式的真實 locals，在每次 while checkpoint 斷言九個 stack states，並核對首輪 discovery matrix 與最後 matrix。
- 用故意錯誤的 control versions 檢查 statements 的區別：shared row lists 得 2 而非 1；整數比較得 0 而非 1；少了負數 bounds 時垂直 wrap 得 1 而非 2；對角鄰居得 1 而非 2。另執行 upper/left shortcut，bridge witness 得 2 而正確解為 1。這些是預先標明的 wrong-approach controls，沒有冒充正確解法的失敗。
- 實際核對 list pop return／mutation、append returns None、獨立 rows 與 shared-row 反例。

兩輪實際完整程式執行均成功，沒有執行失敗或 failing correct-solution case。兩輪 stdout/stderr 與 JSON 都保留；第二輪只為使英文 artifact SHA 與已修正標題一致，完整 Solution bytes 沒有改變。原始 instruction 四檔的合併讀取有工具輸出 truncation，因此另行完整重讀被截斷的 construction 與 sloptrim；不是省略 instruction，也不是 runtime 失敗。

## 未觀察或未執行

INDEPENDENT_READER/NOT_RUN；CLI_VALIDATED/NOT_RUN；IMAGES_RENDERED/NOT_RUN；PUBLISHED/NOT_RUN。未執行 repository／Git／CI／provider／model／其他 agent 操作，沒有外部發布，也沒有修改 instruction snapshots 或 user-global skill。未啟動 recursion failure 示範，未把改動條件的 BFS 說明宣稱為獨立完成並執行的第二份 solution。

本次只交付作者首次完整文章與上述驗證證據。沒有觀察人類讀者重建解法，不能宣稱 mastery、learning effect 或此方法在其他題目上可靠。native agent 可能共用 filesystem；依讀取 allowlist 工作不構成強制隔離證明。
