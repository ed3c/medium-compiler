# LeetCode 56 Merge Intervals：作者交付紀錄

已完成一份完整英文文章與忠實繁中版本。先保存首份完整英文，再完成英文 editorial supplement 與 primary-source semantic review，最後才開始翻譯。首份完整繁中與作者定稿分別保存。沒有讀取範文、repository 文章、歷史實驗或其他 agent/observer 材料。

## 交付檔案與版本順序

1. `article.first.en.md`：首份完整英文，未覆寫。
2. `sloptrim.first.json`／`.stderr`：snapshot detector 的實際初次 stdout／stderr。
3. `article.en.md`：英文作者定稿；只將 additionally 改為 also，並移除五個 interview question 的粗體。
4. `sloptrim.final.json`／`.stderr`：定稿實際 detector 輸出。
5. `english-source-review.json`：英文來源覆核內容、定稿 SHA-256 與覆核時間；當時 translation_started=false。
6. `translation-start.json`：翻譯開始時間與已核准英文 SHA-256。
7. `article.first.zh-TW.md`：首份完整翻譯，未覆寫。
8. `article.zh-TW.md`：繁中作者定稿；只修正「component 終於 a」為「component 結束於 a」的語意歧義。
9. `translation-review.json`：雙語逐項作者覆核與 deterministic matching 結果。
10. `verify.py`、`extracted-solution.py`、`runtime.json`、`runtime.stdout`、`runtime.stderr`：可重跑的抽取與驗證程式及實際結果。
11. `output.json`：指定的四項布林值。
12. `author-notes.md`、`author-repairs.md`、`failures.md`：推導、作者修改與失敗紀錄。

SHA-256 用於此任務 sidecar 比對，不是 compiler receipt、Stage admission 或語意真實性證明。

## 實際來源覆核

依序讀完 task 明列的四份最終 instruction snapshots，未跟讀其中的本地範文連結。來源僅限允許的官方頁面：

- LeetCode `https://leetcode.com/problems/merge-intervals/`：實際讀取 statement、三個 examples、constraints；未開 editorial 或 community solutions。
- Python 3.14 `library/functions.html#sorted` 與 `howto/sorting.html`：new sorted list、key function、一次 key evaluation、stable sort。
- Python 3.14 `tutorial/datastructures.html`：append、sort、None、shallow copy。
- Python 3.14 `library/stdtypes.html`：empty-list truth value、short-circuit、list sequence semantics。
- 官方 CPython `v3.14.0/Objects/listobject.c`：list_resize 的 proportional spare capacity 與 amortized sequence；list_sort_impl 的 key allocation。
- 官方 CPython `v3.14.0/Objects/listsort.txt`：adaptive natural merge sort、runs、merge scheduling、temporary storage。

以上均實際透過 web source reads 取得。線上 Python 3.14 文件當次標示 3.14.8；實作來源固定於 v3.14.0，執行環境為 CPython 3.14.6。文章明確把等長 run 的 rounds 標為 conceptual cost explanation，沒有冒稱 interpreter 的精確執行順序或當次 allocator trace。

英文覆核檢查了 constraints、continuous closed coverage、相接端點、max 對 nesting 的必要性、sorted frontier 的前提與證明、pair ownership、None return、short-circuit、worst-case／amortized 成本、output／auxiliary／peak space，以及 presorted stream 的 final flush。這是作者自審，不是獨立 Reader 證據。

## Editorial 與翻譯

實際執行 snapshot 的 `sloptrim/scripts/detect.py`，兩次命令均 exit 0，stderr 為空。首稿 score=14，band=clean；英文定稿 score=6，band=clean。最後保留一個 copula-avoidance heuristic 命中：`represents a whole connected component` 正在定義 state 的含義，作者選擇保留其技術作用。character-layer 指標沒有 invisible chars、homoglyphs、nonstandard spaces 或 trailing-space 問題。未對繁中執行 detector。

另依 snapshot reader-article supplement 逐句檢視 actor、condition、causal relation 與 decision boundary，保留了新手重建所需的 key→order、shared pair→fresh output pair、short-circuit→安全 indexing、具體 branch→新 state、invariant→exact union、growth→amortized cost、doubling→logarithm 等橋接。沒有以 detector score 代替語意判斷。

英文全篇來源覆核先完成，才建立 translation-start 記錄並撰寫繁中。翻譯後逐節核對條件、否定、數值、程式、ownership 與成本限定。定稿的 9 個 fenced code／state blocks、9 個 source URLs（含出現順序），以及完整 English interview 段落，均與英文逐字相同。繁中保留 English technical terms。

## Runtime 驗證

實際命令為 `python3 verify.py`（在本目錄以絕對路徑執行）。命令 exit 0。程式先從最終英文擷取唯一完整 Python solution，再編譯並呼叫其 `Solution().merge`；不是另寫一份解答來測。

- 15 個 literal cases 通過：包含官方三例、完整 Program Movie、nesting、touching、integer gap、unsorted bridge、chain、duplicate、equal start 的反向 end、合法單點與兩端上限，以及額外的空輸入。空輸入明列為超出 statement 的補充行為。
- 11,110 個獨立小輸入通過：endpoint 0..3 的所有合法 interval，列舉長度 1..4 的所有有序序列。oracle 先依原始 pairwise closed intersection 建圖，再求 connected components 的 min start／max end，沒有重用受測的 sorted-frontier scan。
- 5 個 statement-boundary controls 通過：每例 n=10,000，涵蓋互不 overlap 的單點、反向 touching chain、全範圍 duplicate、nested intervals、固定 seed 的 random intervals 加全覆蓋 pair。完整 labels、n、k 與當次時間在 runtime.json。時間不是 complexity 證明或 benchmark 結論。
- 每個 case 也核對 input 值與 pair identity 不變、output 不 alias input、output pairs 彼此獨立、輸出有 strict gaps；實際修改已回傳 output endpoint 後再次確認 input 不變。
- 三個 intentional negative controls 都重現錯誤：overwrite-end 產生 `[[1,3]]` 而非 `[[1,5]]`；把 equality 當 gap 產生兩段而非 `[[1,3]]`；unsorted frontier 產生 `[[5,6]]` 而非 `[[1,6]]`。原始輸入、錯誤結果與要求結果保存在 runtime.json。

非預期 command/case failure 為 0。沒有因 runtime failure 修補 article code；所有作者 editorial／translation 修改保存在 author-repairs.md。沒有 rerun 掩蓋失敗的紀錄。

## 證據界線

- CONTENT_REVIEWED：作者已完成。
- SLOPTRIM_RUN：實際完成；supplement 是作者人工覆核，並非另一個 detector。
- TRANSLATION_REVIEWED：作者完成，另有 blocks／links／English interview 的精確比對。
- RUNTIME_TESTED：完成上述 cases，未聲稱完全證明所有輸入。
- CLI_VALIDATED：NOT_RUN；未操作 repository compiler 或 Stage。
- INDEPENDENT_READER：NOT_RUN。
- IMAGES_RENDERED：NOT_RUN；本文的 literal state blocks 足以呈現各轉移，未需要 figure asset。
- PUBLISHED：NOT_RUN；沒有 Git、CI、provider、發布或其他 model／agent 操作。
- HUMAN_LEARNING：UNOBSERVED；沒有 learner mastery 或 learning-effect 主張。

這是本次允許來源下的一次作者完整交付。只在指定 output_directory 寫入；未宣稱 filesystem 強制隔離，亦未將共享 native-agent 環境誤當成隔離證據。交付後停止，不接受 Reader 提示來修補本次 generation。
