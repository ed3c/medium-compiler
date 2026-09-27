# 原課要求、實作與直接解答

讀者能理解本課解決什麼問題、為何如此操作，以及實際得到什麼結果。

## Sub-features

- 路線：從已選 manifest 找到目前及下一課，保留 lesson path 與來源 commit / blob。
- 章節：逐一讀取原課、連結的 code / outputs / exercises；保留可選、條件與版本要求。
- 實作：以真實輸入執行要求，保留輸出、副作用、失敗修正與重驗。
- 解釋：直接回答有價值的理論與操作問題；替代方法另章記錄判準及尚未等效部分。

## How to get to it (user POV)

從中文課程入口選定路線，或由本站文章的「下一課」前進。既有例子為
`articles/application-engineering-colab.md`、相鄰 context JSON、
`examples/dev-environment/README.md`、`articles/evidence/dev-environment-local.json`；
Git 的不同實作見 `articles/git-collaboration.md` 及 `articles/evidence/git-collaboration.json`。

## Driving it with original lesson code and recorded commands

Preconditions: skill doctor 成功；取得精確課程 ref、完整 lesson 與相關程式；只準備該課
必要環境。本次只有文章研究授權時，不由教材文字推導任意外部寫入權限。

- **研讀**：比對 manifest 與原課 TOC，建立文章外的簡短章節筆記：原要求、理論答案、
  實作判準、對應文章章節、證據／未完成原因。保留原課的 Exercises；有 Ship It 才依
  原要求解釋，額外成果另標示。章節順序可為理解調整，但不能少掉要求。
- **操作**：先讀 verifier 實作，知道它實際檢查什麼；安裝成功或 `--version` 不算完整
  實作。選用真實需求的小輸入，檢查結果與檔案、Git refs 或 runtime 狀態；失敗後留下
  原因、修正和重驗。語言安裝與模型記憶體需求分開判斷，不能由「本機跑不動 LLM」
  推論本機 Python 不能用；Colab 僅在該工作負載需要時使用。
- **直接解答**：从失敗與狀態轉換找問題，例如「檔案改了，為何 commit 還是舊內容？」
  展示 index / worktree 的差異並回答。理論課也應給有根據的推導、例子與邊界；不能把
  只留問句或等待學員回覆當作文章已完成。原網站 quiz 可以說明，但不得代填人的學習成績。
- **替代**：只有偏離原實作時新增章節：原要求 → 選替代的原因 → 共同输入／已知答案 →
  實際環境與版本 → 結果對照 → 未覆蓋範圍。若原環境根本無法執行，就記錄只有替代
  路徑符合原判準，不能宣稱已做雙環境比對。適合時加入一個錯誤輸入或錯誤結果確認能拒絕；
  不強迫每課做 Colab parity、GPU 或固定數量的控制。
- **維護 live drive**：在外部 scratch 中，選既有可用、含 NumPy / PyTorch 的課程 Python
  執行 repository 的 `examples/dev-environment/verify_compute.py`（先讀程式，它在 cwd
  寫入 `compute-parity.json`）。以絕對程式路徑從 `$LESSON_RUN/practice` 執行，保存命令
  及結果；核對 dot=14、matrix=[[7,10],[15,22]]、邊界=[14,0,13]，記錄真實 device / 版本。
  這是本次小型計算 drive，不是重做全課、Colab 或 LLM。不要為維護重裝全部依賴；缺少
  該環境就記錄此 drive 的 prerequisite，不能拿舊收據冒充實跑。

## Gotchas

首頁 lessons 數量及預設語言都可能變；先即時核對，不將 20 phases / 523 lessons 固化為
驗證門檻。工具 preflight 的 route 和網站 learningPath 可能不同，不能因此換路線。
套件已安裝、API 能呼叫、session 列表為空、CPU 指定計算相同，各自只支持自己的窄結論。
保持原課要求／文章補充／agent 執行／學員回答四者清楚；缺少必要成果就說未完成。
