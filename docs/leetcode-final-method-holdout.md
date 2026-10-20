# 最終 leetcode-mental 的兩題首次產文驗證

這次沒有證明方法已穩定產出完整 Zero Context 成品。兩份完整英繁文章都產出可執行的正確主解法；
Merge Intervals 的 fresh Reader 能從正文重建全部八題，Number of Islands 的 Reader 仍將 `cost` 列為缺項。
文章、首稿、作者修正及 Reader 原始失敗都保留，沒有事後修文或再抽樣來覆蓋首次結果。

## 固定輸入與執行範圍

使用 [commit 4e5ee4d](https://github.com/ed3c/medium-compiler/commit/4e5ee4dba71b33287be0fd720d35133a8247409a)
的最終 `leetcode-mental` skill、complete-article profile、construction method 及本機 sloptrim 指引。
啟動前以 Git 取出精確 instruction snapshots，固定 [選樣與接受條件](../evals/writing/leetcode-final-method-holdout/selection.md)
及 [八個 Reader 問題](../evals/writing/leetcode-final-method-holdout/reader-questions.json)。
讀者只有基本 Python syntax，不預設 data structures、演算法、runtime internals 或 complexity 知識。

選題是 [LeetCode 200 Number of Islands](https://leetcode.com/problems/number-of-islands/)
與 [LeetCode 56 Merge Intervals](https://leetcode.com/problems/merge-intervals/)，分屬圖搜尋與區間合併。
兩題均不在前次方法開發的 49、20、704、198 集合。
Writer 只獲題目、官方 statement／Python primary sources 的範圍、共同方法與交付要求；
沒有範文、editorial、解法大綱、父代理的題目專屬提示、先前 Reader findings 或對方文章。
搜尋策略、representation、trace、proof、章節與是否需要額外圖檔都由作者選擇。

兩位 Writer 使用 Local Codex 原生 `collaboration.spawn_agent`、`fork_turns=none`，沒有指定替代 model。
它們自行完成英文初稿、實際 detector／來源語義審查、批准英文後完整翻譯及作者英繁覆核。
首份完整草稿與作者定稿分開保存。兩份首次交付都凍結後，才各啟動一個 fresh Reader。
本次沒有改 skill、Part 7、七張 SVG、ALG Four sidecar、API、Sandbox 或 CEFR。

## 四份完整正文與結果

| 首次交付 | 英文 | 繁中 | Reader 重建 | Observer 執行文內解法 |
| --- | --- | --- | --- | --- |
| Number of Islands | [全文](../evals/writing/leetcode-final-method-holdout/islands/article.en.md) | [全文](../evals/writing/leetcode-final-method-holdout/islands/article.zh-TW.md) | 七題完成，`cost` 缺項 | 692/692 |
| Merge Intervals | [全文](../evals/writing/leetcode-final-method-holdout/intervals/article.en.md) | [全文](../evals/writing/leetcode-final-method-holdout/intervals/article.zh-TW.md) | 八題完成 | 1,120/1,120 |

Islands 自行推導四向 path、connected component、scan 與 search 的分工、立即標記與待辦 stack，
區分 discovered／examined；其獨立 row allocation、bounds、完整 trace、兩層 invariant 與主法成本均能重建。
Intervals 自行推導任意順序下的 provisional gap、排序後可定案的 gap、最後一個 output pair 的 frontier，
把 `max`、closed endpoints、shallow copy／fresh output pairs、prefix proof 與 sorting／append 成本接回完整程式。
沒有把 Group Anagrams 的 counters、canonical key、固定章節或圖數套到這兩題。
正文使用具體格網與狀態 blocks，沒有未完成 figure placeholders，也沒有宣稱另有已渲染圖檔。

Reader 只獲各自的兩份正文、共同 audience、固定問題與輸出形狀；不獲 skill、來源、作者 report／tests、答案或其他輸出。
它們各自以新合法輸入手工重建 trace，回答 contract、state、failure、proof、cost、transfer 與 bilingual。
兩位都未報告實質英繁差異；完整解法另經實際機械比對一致。
這是 LLM article-only reconstruction，不能換算成 human learning、mastery 或一般成功率。

## 保留的缺口與判讀

[Islands 原始 Reader](../evals/writing/leetcode-final-method-holdout/islands/reader.raw.json)
能由 `mn` 次 scan、每個 land 一次 push／pop、四次鄰居檢查推導主法 `O(mn)`，
也能區分 Boolean matrix、pending coordinates 與有界整數 output。
缺項集中在文章後段：recursive DFS 只說未完成 call 必須留狀態，沒有明確閉合其 time／space；
最短路變體新增 distance／layer counter，沒有進一步交代該新增 state 的成本。
它另外標記 geometric sum 中 `K` 未明定。

Owner 對照正文後保留這個 scoped 缺項。附近的「final size」可以提示 `K` 的含義，
因此不能只靠沒寫一行定義就斷言整個 amortized argument 錯誤；主法推導也不是失敗。
但固定成本問題要求涵蓋正文引入的 alternatives 與新 state，後段確實沒有像主法一樣交代完整成本。
這至少阻止「全部八題皆能只憑正文重建」與「兩篇都已完成 Zero Context 閉合」的宣稱。
未要求每一個變體另寫完整程式或展開全部 interpreter internals。

逐字核對另發現 Islands Reader 的 64 個引文中，四個漏掉 `"1"`／`"0"` 外的 inline-code backticks。
60 個原始引文直接匹配；另外四個的正文原句由 Owner 定位，另存 [quote audit](../evals/writing/leetcode-final-method-holdout/quote-audit.json)。
Raw Reader 沒有被修改，不能報成 64/64 exact quotes。
這是 consumer 引用格式失敗，與文章的成本缺項分開記錄。
[Intervals Reader](../evals/writing/leetcode-final-method-holdout/intervals/reader.raw.json) 的 62 個引文全部逐字匹配，
其新 trace、嚴格 gap、最大 end、prefix invariant、operation-derived cost 與 changed-contract adaptation 均能對回正文。

另外啟動一位 fresh Reader，只讀從 Intervals 刻意刪去成本段落及其成本 recall 的副本。
變更及預期缺口在啟動前另存，沒有提供給 Reader。它保留可觀察的 loop／allocation 關係，
對缺少的 primitive costs、sorting bound 與空間模型回覆 `NOT_STATED`，18 個引文均匹配。
[此控制結果](../evals/writing/leetcode-final-method-holdout/cost-control/output.json)
支持它在這份缺文上能拒絕補答案；不等於已校準所有缺口，也不算自然 Writer 失敗。

## 實際執行與首稿證據

Observer 從凍結的英文正文擷取完整 `Solution`，確認英繁 code 相同後直接執行。
Islands oracle 使用 land reachability closure；Intervals oracle 使用 pairwise intersection 的 transitive closure，
兩者都沒有重用受測的 DFS／sorted-frontier algorithm。
字面 oracle controls 先獨立核對；小輸入列舉與最大合法輸入比較全部通過，輸入值保持不變。
詳細結果見 [runtime-independent.json](../evals/writing/leetcode-final-method-holdout/runtime-independent.json)。

Islands 的 692 次包括七個 literal、682 個小格網、300×300 全陸／全水／checkerboard；
Intervals 的 1,120 次包括八個 literal、1,110 個小 interval lists、10,000 個 interval 的 chain／分離單點。
作者另有自己的 runtime／trace／negative controls：Islands 20 個 literal／boundary、682 exhaustive、200 random；
Intervals 15 literal、11,110 exhaustive、五個 n=10,000 controls。
作者與 Observer 的數目不混加成獨立樣本，更不能用測試次數抵消 Reader 的缺項。

每題目錄保留英繁 `article.first.*`、作者定稿、`report.md`、review、detector、runtime、當時 stdout／stderr 及驗證程式。
沒有正確主解法的 failing case 或非預期作者 command failure；故意錯誤的演算法 controls 都明確標示。
Islands 的標題／語句清晰度修正與翻譯補充、Intervals 的英文小編輯及繁中「終於／結束於」修正均可從首稿 diff 看到。
作者 instruction 合併讀取曾發生工具輸出截斷，隨後補讀；沒有當成完整未截斷讀取。
Observer 的一次結果檔 existence 檢查也記錄了尚未交付的 `No such file`，沒有反覆啟動 Writer。

## CI 與證據界線

[新增機械控制](../tests/test_final_method_holdout.py) 由既有 unittest discovery 執行：
重跑文內程式、比對 raw Reader 與保存的問題／missing IDs，逐字核對引文並保留具名 quote audit。
它不要求 `unanswered_question_ids=[]`，也不把人工 audit 當成原 Reader 成功。
CI 不啟動模型、不重跑作者驗證器、不為此實驗計算 article／report SHA-256。
作者當時在本機 sidecar 保存的 digest 保留為歷史紀錄；本文沒有增加新的 digest gate。
Matching-head CI 以 PR #81 的實際 Actions readback 為準，先前 head 的綠燈不能覆蓋本次新增檔案。

本機完整 unittest 首輪為 287 tests、8 failures、12 errors、14 skipped，新增的兩項 holdout controls 通過。
所有失敗來自既有 learning-handoff 測試：預設暫存路徑經過 macOS `/var` symlink，觸發 `symlinked source path` 保護。
只把測試程序的 `TMPDIR` 指向相同位置的實體 `/private/var/...` 後，該組測試通過；沒有修改來源拒絕邏輯或測試 assertion。
原始全套失敗 log 保存於 [local-verification](../evals/writing/leetcode-final-method-holdout/local-verification/)。
相同實體暫存路徑下的完整重跑為 287 tests，全部通過、14 skipped；成功 log 也保存在同目錄。

本次只新增 holdout 文章與驗證證據；未對新文章執行 compiler Stage admission、網站發布或 learner episode。
依既有範圍止於 PR 與 CI，不 merge、不部署。
完整原始 task、instruction snapshots、所有 native captures 及 observer records 位於：
`/var/folders/l6/44bf7nvs64j60f1mpyy88hdm0000gn/T/leetcode-final-holdout-m22zvsha`。
可攜式文章與原始結果見 [packet](../evals/writing/leetcode-final-method-holdout/README.md)，
[session manifest](../evals/writing/leetcode-final-method-holdout/session-manifest.json) 列出五個真實 native thread IDs。
App capture 有每項 20,000 字元上限，共享 filesystem 也不提供強制 read isolation。
獨立 context、讀取 allowlist 與可取得的實際 capture 不等於完整隱藏上下文或沙箱隔離證明。

結論限定為：最終方法在兩個新題型都完成英繁首次交付，主解法正確；其中一篇完成本次八題重建，
另一篇暴露後段成本閉合與 consumer 引用格式問題。不能據此宣稱方法已穩定達標。
下一個必要修改應先處理「作者自審為何沒有讓新增變體沿同一成本模型閉合」，
不能只新增 Islands 的專屬詞彙或事後把文章修好當成方法首次成功。
