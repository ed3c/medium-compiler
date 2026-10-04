本案支持保留「成本觀察、必要性判斷、狀態轉移權限分離」的設計。`cost_telemetry.project` 先整理觀察，再交給 `test_manager.review_cost`，最後由 `schema_manager.project_cost` 投影資料。失敗或重複測試不直接觸發修復或完整測試。這符合所附 `AGENTS.md` 的成本與權限要求。但本案只能判斷實作機制；產品的端到端成果仍為 `unobserved`（未觀察）。沒有原始 Issue、patch（變更差異）、執行紀錄或 owner readback（狀態負責者的最新回讀）。

審查模式為 `implementation_review`（實作審查）。目標標示為 `ed3c/soodles@d58c4e7ba0685c367da5c3060e06e6c5fc38f85f`。本文由 AI Codex 撰寫，實際模型版本未知。所審實作的作者、模型與執行框架均未知。以下行號指任務提供的 `source-only` 檔案；完整路徑及 SHA-256（位元組摘要）保留在 `case.json`。14 個選定 instruction/evidence 檔案均符合任務列出的摘要。這驗證副本身分，未獨立驗證 Git commit 與副本的對應。

可重建的產品要求是：Soodles 在正常執行時保留有來源的成本，讓 Test Manager 說明觀察與缺口，讓 Schema Manager 提供現有 owner 的下一步。未知成本不得補成零；時間長不得直接判定浪費；成本報告不得取得新的執行權限。這些要求來自所附 `AGENTS.md` 的「Cost and decision principles」與「Current boundary」。原始實作任務及完整交付邊界未提供，因此不能宣稱原工程任務已完成。本次授權只涵蓋來源審查與五份紀錄，不包含產品測試、來源修改或發佈。

第一個重要設計是避免把重疊時間相加。`cost_telemetry.py:163–172,175–277` 先驗證每筆 observation（觀察紀錄），再以來源摘要、span（被量測的區段）及特定 native session（原生工作階段）鍵去重。相同鍵而內容矛盾會在 `conflicting_replay` 拒絕。`intervals` 排序並合併重疊區間；`observed_wall_seconds` 使用 foreground 與 wait 的聯集。worker 時間另依 worker 分組，phase 的 inclusive_seconds 保留為含子區段的時間，不宣稱可加總。假設 foreground 是 [10,20]、wait 是 [15,25]，聯集代表 15 秒；相加會是 20 秒。此數字是紙上例子，並非執行結果。沒有區間時回傳 null；有來源仍只標示 partial。這讓使用者看見量測範圍，而不把局部記錄冒充完整生命週期。

較簡單的替代方案是只累加 seconds。它適合已證明互斥且完整的區段；目前資料允許巢狀與平行活動，因此不符合這裡的前提。現有方案增加了區間與來源處理的複雜度，但保留 wall time（經過時間）與 worker time（各工作者時間）的不同意義。反證限制是：來源驗證不能證明時間戳真的準確。`begin/finish` 用 `time.time()` 產生邊界，用 `time.monotonic()` 算 seconds（668–718 行）。若系統時鐘跳動，兩者可能不同；這是來源顯示的量測限制，未觀察到實際故障。最小後續證據是現有正常紀錄中相同 span 的邊界與秒數，以及針對重疊、缺失、矛盾重播的既有控制結果。這不要求新增基準測試或完整測試。

第二個重要設計是保留必要性判斷與權限的 owner。具體路徑從 `cost_telemetry.report:416–503` 開始。它讀取 authorization（授權資料）、state（狀態資料）及成本紀錄，透過 `read_ref:280–286` 比對來源摘要，再呼叫 `project`。`project` 只建立區域彙總資料；`review_cost:463–503` 逐一讀取 phase。若 failed/refused 次數大於零，回傳 `needs_owner_readback`。若同一 `test.module` worker 有多筆觀察，也要求 owner 比較每次輸入與必要行為。缺少秒數另列 unknowns。回傳的 `effects=[]`、`test_demand=null`、`authorizes_landing=false` 明確保留權限邊界。

例如一個 phase 有兩筆 test.module 觀察，其中一筆 failed 且未量測時間，來源分支會同時保留成本觀察、失敗回讀需求、重複必要性疑問與未量測缺口。這仍是未執行的輸入推演。它不等於兩次執行必有一次浪費：第一次失敗後，修正輸入或程式再驗證可能完全必要。以次數或秒數閾值自動刪除測試，雖較簡單，卻缺少這項因果資訊，還會把資料投影變成第二個調度者。應保留現有設計。最小可用檢查是同一 module 兩次正常執行的輸入身分、第一次結果、修正與當前 owner 回讀，判斷重跑是否必要。

後續 `schema_manager.project_cost:247–276` 再檢查數值為有限且非負，並核對 review 的 owner、subject、sources 與無副作用宣告。它保留 hard_gate（由原 owner 提供的必要條件），不從成本推導新命令。`project_owner_feedback:341–367` 接著使用 `owner_transition:279–338` 檢查 continuation（接續動作）的狀態、required、argv 與 environment 形狀，原樣保留 next。ready、waiting、input_required、complete 各有不同 disposition。elapsed_ms 只量測這次本地投影，不是網路、模型、測試或使用者的全程時間。DAG（有向無環依賴圖）中的 effectiveness 明確仍為 unknown。

此處有需要消費者理解的相容分支：舊結果若只有 `status=resolved,next=null` 而沒有 continuation_state，`legacy_terminal` 會把 review_disposition 標為 history_retained，但 owner_transition 仍可是 unknown。這可保留歷史紀錄，卻不能讀成目前已驗證完成。相容分支也不會產生效果。最小後續觀察是實際 CLI 消費者對這種結果的顯示與處理。沒有該 caller 或執行紀錄，不能把可能的誤讀判成已發生缺陷。

失敗路徑同樣有邊界。摘要不符或矛盾觀察會透過 `require` 丟出 `CostRefusal`。`failure:723–725` 提供 refused 的成本投影，文字說明原 continuation 不變。但所附來源沒有 `issue_atom` 呼叫端，故不能證明實際例外一定被攔截、回復後仍能合法接續。`begin` 透過傳入的 save 保留未完成 intent（意圖紀錄）；`finish` 更新量測並保存，報告後再保存 telemetry overhead（量測本身的開銷），該開銷要下一次投影才可見。這是來源可見的恢復與可見性設計，並非本案觀察到的執行。本次沒有觸發任何 save 或產品函式。

接受條件是：正常紀錄身分一致、重疊時間不重算、缺口保留 unknown、owner 的現行 continuation 被保留，且沒有因成本自行新增測試或修復。拒絕條件是來源身分矛盾、成本數值非法或消費者將觀察擅自轉為效果權限。來源支援部分判斷；實際 caller、既有測試與 owner 回讀缺席的部分維持 unknown。`test_manager.select:179–246` 顯示 full 只在明確 full 參數成立時選完整範圍；未知變更進 unresolved。這是另一個來源層的反證，避免把未知視為全套測試需求；它不是本次執行的測試結果。

這些紀錄能支援什麼？工程架構與細節有可爭辯的來源判斷。Agent（被評實作者）的工程判斷、debugging（除錯）、理由表達、書面溝通與可信度沒有過程證據，不能從正確程式倒推。第一個實際偏離沒有被觀察到，故 `first_observed_divergence=null`。沒有 A/B（兩方案實測比較）；替代方案均為假設。沒有專家標註、準則版本與分組保留測試集的結果，所以 `evaluator_validated=false`。沒有真人判斷或回饋，所以 `human_review_performed=false`、`human_review=null`；這不是使用者的獨立 Staff 經驗或任職資格證明。沒有先凍結預測再揭露結果的順序證據，故 `prospective_prediction_eligible=false`、`prediction=null`。沒有實作者 trace（行動與觀察紀錄），故 `agent_behavior_observed=false`、decision_episodes 為空。這四個 false 表示本案沒有建立相應主張，不代表人或模型失敗。

本案用途為 `case_review`（個案審查），split 為 null。保留此案可供下一次比較前提與反例，但不會自動訓練模型或驗證評估器。本次審查交付完成；產品交付、行為改善、成本降低、真人學習、評估可靠度及 owner 消費回饋均未建立。成本、token 與人工作業時間沒有量測，保持 null。
