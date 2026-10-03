# 原課要求、實作與直接解答

讀者能理解本課解決什麼問題、為何如此操作，以及實際得到什麼結果。

## Sub-features

- 路線：從已選 manifest 找到目前及下一課，保留 lesson path 與來源 commit / blob。
- 章節：逐一讀取原課、連結的 code / outputs / exercises；保留可選、條件與版本要求。
- 實作：以真實輸入執行要求，保留輸出、副作用、失敗修正與重驗。
- 解釋：直接回答有價值的理論與操作問題；替代方法另章記錄判準及尚未等效部分。
- 成果：每課 examples/<lesson>/ 保存必要材料、固定版本與使用／重跑方式，區分當次本機能力及尚未驗證範圍。

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
- **選擇與判準**：依 [因果解釋與語意驗收](article-assembly.md#因果解釋與語意驗收)
  保存每個選擇的需求、限制、前提與來源。追出執行者、輸入、檢查、狀態變更、效果及失敗路徑。
  先從原要求推導接受／拒絕／未知條件，再判讀結果；不能為配合已得到的答案改判準。
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

文章寫好、安裝過套件、GitHub 上有檔案，都不是完整 replay 的判準。執行下列契約，
再決定能宣稱哪一項成果；既有課程不因 skill 更新就自動通過新的要求。

## 成果取得與 replay 契約

新增或修訂課程文章時，沿用 [examples/](../../../../examples/) 的既有結構，在
`examples/<lesson>/` 交付這一課的最小可用成果。先讀 2–3 個相關既有實作；目前
`examples/dev-environment/` 展示多語言與計算驗收，`examples/python-environments/`
展示 pyproject、lock 與環境驗收。不要把它們各自尚未具備的能力當作通用模板保證。

1. **先定義成果能力。** 用一個具體輸入與預期輸出說明學完這課可以做什麼；列出
   支援的 OS／架構、工具與 Python 等 runtime 版本、硬體、網路及外部授權條件。
   SDK 匯入、API 成功請求、GPU 運算、LLM 工作負載各自驗收；不能互相代替。
2. **保存足夠材料。** README、必要程式／notebook／小型輸入、依賴宣告與 lock、
   已知答案及驗收入口必須進 GitHub。工具鏈不能由 lock 完整固定時，明列版本與取得方式；
   大資料／模型記錄公開取得位置、版本／checksum 及授權條件，不入庫 secrets 或 venv。
   不需 runtime 的理論課也保留可核對的推導／例子，明示本機環境不適用，不硬造安裝需求。
3. **提供兩條可操作路徑。** README 分開寫「取得並使用成果」與「重播學習實驗」：
   前者讓讀者從乾淨目錄取得指定 ref、安裝、執行最小成果並驗收；後者對照原課實作，
   包含必要輸入、操作、預期結果、失敗修復、可用反例與清理。允許沿用少量明確命令，
   不強迫新增 launcher；若宣稱一鍵 replay，必須有實際受測入口且涵蓋其宣稱的步驟。
   重建一個雙套件環境不能冒稱重播了原課全部四題。
4. **交付持久本機入口。** 使用既有學習根目錄，在新課程／版本子目錄準備環境，
   保留各課相容性邊界；不以全域升級、覆寫前課環境或切換共享 checkout 代替隔離。
   記錄可複製的進入、使用、再驗收指令與輸出位置。既有目錄身分不符就另建版本目錄；
   不能刪除他人資料。不要移動 venv；在目標位置重建。未能持久交付就明示此項未完成。
5. **固定來源再驗收。** 成果取得用完整 commit SHA 或其他已核對不可變 ref，
   配合相對目錄／檔案 hash；不能用會漂移的 main 當作重播身分。文章、範例與驗收
   context 記錄版本關係。避免自指 commit：文章可連固定的前置成果 commit；若同一
   commit 新增文章與範例，將發布後讀回的完整 SHA 記於交付收據，README 使用明確的
   `<verified-commit>` 取得方式。branch URL 只是瀏覽入口，不是驗證 pin。
6. **真的重跑。** 用未帶入既有 venv 的乾淨副本依宣告／lock 重建並檢查已知結果；
   快取可以使用，但須註明，不能把使用快取說成無快取安裝；只有實際採用離線模式
   並成功時才宣稱該次離線重建，不能由此推論首次取得套件不需網路。再在保留的持久環境重新
   啟動使用入口及驗收，確認重複使用不破壞成果。負例只在自有副本；變更依賴或
   來源後重驗，不消除失敗斷言。記錄來源 SHA、lock hash、cwd、命令、版本、時間、
   stdout／stderr／exit、實際結果與清理；敏感路徑只留本機，公開紀錄去敏。

驗收要回答「材料可取回」「乾淨重建能運作」「現有持久環境現在能運作」
及「哪些原課實驗能 replay」。缺少 credentials、平台或輸入時，標明受阻的能力及
精確缺件；在授權內繼續其他項，不以 CPU 結果宣稱 GPU、以替代結果宣稱原環境。
執行成功不等於人已理解；不代寫測驗答案作為人的成績或更新 LEARNING.md。

### 此契約的維護 live drive

沿用上方計算 drive，另外從本次精確 repository ref 的
`examples/python-environments/` 取 README、pyproject.toml、uv.lock 與
`verify_environment.py` 到本次專用的持久維護目錄；記錄其用途為維護控制，
不能冒稱已補齊所有既有課程成果。先確認 Python 3.12 與 uv 可用，讀程式，再執行：

```sh
uv sync --locked --all-extras --python <已核對的-Python-3.12-絕對路徑>
.venv/bin/python verify_environment.py
```

在另一個沒有 venv 的副本重建，核對 lock 未變、installed 版本清單與
NumPy／PyTorch CPU 矩陣皆一致；再從持久目錄重跑同一驗收。可重用已驗證來源的
package cache，記錄實際網路／cache 選擇；不為維護安裝全部工具鏈或開新雲端 session。
README 的 lock 漂移負例可在副本實跑並還原，確認拒絕後原持久環境仍可用。
保留兩次獨立環境的結果與命令，停止本次程序，留下持久入口與證據。
缺少 runtime／套件來源時只阻塞這個控制，不捏造重建成功。

## 其他範圍限制

首頁 lessons 數量及預設語言都可能變；先即時核對，不將 20 phases / 523 lessons 固化為
驗證門檻。工具 preflight 的 route 和網站 learningPath 可能不同，不能因此換路線。
套件已安裝、API 能呼叫、session 列表為空、CPU 指定計算相同，各自只支持自己的窄結論。
保持原課要求／文章補充／agent 執行／學員回答四者清楚；缺少必要成果就說未完成。
