# recorded：保留歷史證據契約的 catalog 測試修補

最關鍵的工程選擇是：CI 揭露第二份報告使固定數量斷言失效後，Agent 改為逐份核對 catalog（報告目錄），並保留第一份報告的證據限制斷言。這是合理且有證據支持的修補；單純把 `1` 改成 `2` 會留下相同的擴充故障。`after-test.py:28–53` 與 `observations.json:e3–e7` 支持此判斷。這不等於整份 Soodles 工程評估經過獨立驗證。

本次採 `combined`（實作與可見 Agent 工作流程合併審查），只涵蓋所選片段。審閱者為本次 AI assistant，模型身分未提供；不是人工認證。原任務是審視 Soodles Schema/Test Manager 的 P-class、CLI 資料驅動與測試成本必要性，回饋 Schema Manager，並在 medium-compiler 網站交付評估。完整任務結果只能判為部分有支持：交付報告存在，網站測試修補通過的歷史紀錄存在；Soodles 回饋的實際 payload、原始 API 回應與完整來源不在本次允許範圍，不能重驗其整體工程結論。

## 決策一：從失敗症狀縮小到錯誤的測試前提

`observations.json:e1–e2` 記錄 head `0ade998252db9d254dd107dce832a9c5ed35b9ca` 的 mechanical-writing 失敗，job log 只有退出 1，unittest 輸出另存 artifact。當時尚不能從失敗狀態判定產品有錯。Agent 執行既有的單一測試模組（e3），得到 `AssertionError: 2 != 1`，定位 `before-test.py:28`。這個檢查能區分「renderer 無法產生報告」與「renderer 產生兩份而測試寫死一份」；在 `render_reports` 已遍歷目錄的實作下，後者有直接依據。

e4 的明示理由是新增第二份報告讓原數量假設失效，會核對每份報告的路由與內容雜湊，保留舊證據檢查。e5 的 patch 符合此說法。這支持局部除錯品質與說明可信度；它不揭露此前全部探索，也不能推論隱藏思考。假設性替代方案是先取回完整 tests.txt；其優點是保留 CI 環境錯誤的完整背景，但當下的局部重現已提供可定位原因，因此沒有證据顯示必須再跑全套才可修改此斷言。本次沒有重跑任何產品測試。

## 決策二：把數量假設換成多報告契約，而非刪除驗證

具体路徑如下。測試 `test_published_report_preserves_scope_and_download_identities` 呼叫 `render_reports(ROOT,out,page,markdown)`；`ai_evals_site.py:44–53` 讀取 `catalog['reports']`，經 `checked_file` 取得來源 bytes。`checked_file:9–16` 先解析路徑並拒絕逃出 repository，再核對 SHA-256（檔案內容身分雜湊），失敗拋 `ValueError`。`render_reports:54–63` 拒絕不合法或重複 slug（路由識別字），讀入 assessment、guide、audit，檢查 audit 與 report 的 repository/revision 一致。

通過後，它建立輸出目錄，寫 report.json、archive-audit.json、assessment.md、補充附件與 index.html，累加 cards 與 provenance（來源與交付身分紀錄），最後產生總索引。輸出有檔案系統副作用，但測試使用 TemporaryDirectory，離開測試後清理。中途失敗沒有完整 rollback（復原已写檔案）的程式路徑；本次沒有證據顯示此修補需要解決部署原子性，不能把此特性直接定為本案新缺陷。

原先 renderer 支援多份，測試卻要求 `len(provenance)==1`。新測試從 catalog 建立 `route -> (entry,source)`，核對實際路由集合與數量，再核對每份已輸出 report.json 與 assessment.md 的雜湊以及索引路由。它會拒絕缺少或多出路由、重複 provenance 項目、內容身分錯誤及缺少索引連結。原 renderer 的 duplicate-ID guard 在產生 provenance 前執行；不能僅以測試的 dict 會合併重複 key 就宣稱實際重複輸出被放行。

歷史報告 `soodles-claim-refusal` 原有斷言全部保留其意思：fresh coding model runs 為 0、非完整 platform transcript、六筆觀察、`human_calibration == 'NOT_PERFORMED'`、assessment 雜湊、Evidence coverage、`lang="en"`、索引連結。原 `provenance[0]` 改為以 route 找回 `original`，消除排序相依。過期來源與逃逸路徑的負向測試在 AST（抽象語法樹）比較中完全相同。因此 `original_report_checks_preserved=true` 有直接原始碼證據，不只是採信 Agent 的宣稱。

更簡單的 `len==2` 改法維護成本低，但第三份報告會重犯，且無法確認新增報告的 bytes。另一個假設性替代是複製舊報告全部 assertions 到每一份；那會錯把歷史報告特有的六筆觀察、English 語言及未校準狀態當成通用契約。現行拆分「所有報告交付身分」與「特定報告歷史事實」較符合需求。

反證與限制：測試以 identity markdown/page callback 執行，沒有瀏覽器或完整樣式；新通用 assertions 未逐份檢查 guide、audit、附件的交付雜湊，也未證明每個 HTML finding 的意義保存。renderer 的 `checked_file` 保護來源身分，但共用 helper 不是完全獨立 oracle（判定正確與否的檢查）。這些限制不推翻本次修補，卻限制「所有交付完整性都驗過」的說法。若未來需求包含完整下載契約，最小補充是在既有測試逐份核對 audit/附件 bytes，並以既有網站驗證流程檢查一項工程 finding 的呈現；不需要新測試框架或現在另跑 suite。

## 決策三：使用已有 CI 與部署 readback，但等待記錄不夠完整

e6 記錄同一局部模組兩項測試通過，0.006 秒；e7 與 `passed-ci-jobs.json` 對應修補 head `e30508d0f78a98a225e72f8c9e13273ae0582b25`、run `37202934016`、job `111438144045` 的 success。`patch-commit.json` 記錄父 commit、單一變更檔與同一 diff，支持這是該修補的歷史 CI。`writing-verification.yml:17–27` 同時顯示普通測試與 drives，以及 behavior-evals 預期 exit 3 後明記沒有 fresh writer/reader experiment。CI 綠燈不能轉述為模型效果已證明。

e8 有 merge 結果；e9 有部署 readback 最後 `matched_files=10`、`provenance_matches=true` 的轉錄，支持當時做過檔案與 provenance 比對。原始部署命令、十個檔名與完整回應未提供，所以本次把「網站交付」保留為轉錄支持而非獨立完整驗證。這比只依 CI 判定已上線更謹慎且具體。

e9 同時顯示對同一 running session 多次空輸出輪詢。這不是重跑產品測試，也没有證據顯示製造重複外部寫入。若要改善互動效率，可在同一部署程序上選擇較合適的等待窗口並持續讀回；不要另起 launcher。完整次數、超時策略和程序內容缺失，不能計算浪費成本，亦不能直接判定所有等待不必要。

## 交付文字、評估器與人的經驗

`delivered-assessment.md:40–78` 提供可行的架構取捨：測試 module 粒度選擇不證明每個 case 必要、共用 fixture 改變會擴大受影響 consumers、duration 本身不足以授權刪除負向控制、owner feedback 保留原 next。這些說明具有可行動的機制與反例；但本次只有報告文字，沒有它所引用的 Soodles 原始碼、654 條 timing logs、projection 回應及 owner-consumption。因此其數值、API 行為與「已回饋 Schema Manager」仍屬作者報告，不能冒稱本次重新證實。最小補件是所選 input、實際 response、owner-consumption 及對應來源 bytes，並沿該一條回饋路徑核對，無須發動另一輪無關完整 suite。

報告明說沒有獨立 human calibration（人工校準），測試也保留 `NOT_PERFORMED`。commit author 名稱不是人工審閱紀錄；本次審查同樣由 AI 完成。因此 `human_review_performed=false`。`evaluator_validated=false`：沒有實際專家標籤、版本化判準、依關聯任務分組的 train/dev/test（訓練／開發／測試）配置、未接觸測試集结果、每類錯誤或歧見處理。通過內容雜湊與 CI 只驗证其確定性契約，不校準評估文字的可靠度。

`prospective_prediction_eligible=false`：這是已看過失敗、patch、成功和報告的 retrospective（回顧性）案例。舊報告第64行說曾事先儲存八項 API 預期，也明確排除其為 population prediction accuracy；原 freeze 與獨立觀察順序不在本次輸入。不能藉保存本 case 將其變成前瞻評測。合格前瞻案例 0、已解析合格案例 0、未解析合格案例 0、排除 1；不計算準確率。

本資料用途為 `case_review`，不是 `evaluator_validation`。人的原始預測、判讀、回饋與歧見皆不存在，故 case 的 human_review 保持 null。它可以支援練習與下一次對照，不能證明使用者獨立取得 Staff 經驗、任職能力、English fluency、模型排名或模型權重學習。沒有 A/B；上述替代方案均未執行。下一次若要觀察人的進展，應在揭露新的 outcome 或 AI 判斷前取得人的原始預測，再保留真正的專家回饋；本次不補造。

## 證據與覆蓋範圍

| 類別 | 本次可支持 | 不能推出 |
| --- | --- | --- |
| 原始碼 | before/after、renderer 及負向控制 AST 差異 | 重新執行的結果 |
| 歷史執行 | 轉錄 e3/e6、綁定 head 的 jobs JSON | 完整 Agent transcript、所有此前選擇 |
| 部署 | e8/e9 轉錄的合併與比對結果 | 目前網站狀態、逐檔獨立複驗 |
| 新確定性檢查 | 21 個指定 instructions/evidence 雜湊吻合、來源 diff/AST | 產品 suite、judge 語意準確度 |
| 評估 prose | 已交付文件的工程說明與自述界線 | 原 Soodles 實作與回饋的完整重驗 |

目標 repository 為 `ed3c/medium-compiler`，目標 revision 為 `e30508d0f78a98a225e72f8c9e13273ae0582b25`。目前載入 instructions 的 checkout HEAD 是 `5ed8b5ef165b32a6252c601d0fef790c5ca580bf`，且有九個 modified 指令檔、一個 untracked 方法檔；它不是目標 commit。每個指定輸入的實際 SHA-256 均吻合 task 清單，所以評估綁定選定 bytes 與 archived patch/CI，沒有將髒檔冒綁到 HEAD 或聲稱直接驗證目標 Git tree。完整來源路徑與雜湊在 case.json；input 身分與精確指令 map 在 consumer-report.json。

七個面向只用於查漏：工程判斷、除錯、架構及細節有上述局部支持；推理清晰度僅限 e4 和交付文字；溝通與開發者信任以說法是否吻合 patch 和已知界線判讀。完整工作流程、人的能力與 evaluator reliability 仍未評估完成。tokens、model time、整體 task-handling time、人的 review time 均未知；0.010/0.006 秒是轉錄中的局部 unittest 時間，不能作為整項任務成本或效能改善基準。
