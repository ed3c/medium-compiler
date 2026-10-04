# Soodles 原始碼審查：成本資料如何回到 owner，而不自行觸發修復？

在這次讀到的程式邊界內，Soodles 把「觀察到成本」與「決定修復」分開處理。`cost_telemetry.project` 驗證、整理 observations；Test Manager 判斷哪些情況需要進一步回讀；Schema Manager 將這些資訊放在原 owner 的 continuation 旁。單次耗時很長，不會直接選擇 repair 或要求再跑測試。這個 ownership 分工值得保留。

這是 `implementation_review`，目標版本為 `ed3c/soodles@d58c4e7ba0685c367da5c3060e06e6c5fc38f85f`。原 reviewer 是 Codex AI review consumer，精確 model 未知；原實作者的 coding agent、model 與 execution harness 都未知。這份繁中版改寫原有評估，不是使用者獨立完成的作品證明。

原任務提供 `AGENTS.md` 及三份 Python source，雜湊均與 task manifest 相符。沒有提供 patch、原始實作過程、tests、runtime logs 或 owner receipt。repository/revision 的歸屬來自 task manifest，reviewer 沒有檢查目標 Git checkout；九份 staff-evals 指令也符合 task 對 skill revision `bc68aa025a26124ccbf6a0afc94c380dad4af0be` 宣告的雜湊。因此以下結論是 source review，沒有證明實際速度、成本下降、完整生命週期或實作者的工程行為。

## 要解決的問題與責任界線

`AGENTS.md` 的 Cost and decision principles 要求從正常執行取得量測、保留 unknown，並分開計算 projection 與外部工作的時間。修復需要觀察到缺陷或設計風險，由既有 owner 在既定 controls 與 budget 內處理；寫入結果未知時須向 owner 回讀。這些是需求，不能因文件寫了就當成 runtime 已實現。

此處的設計問題是：如何把既有 timing evidence 整理成可用回饋，又不讓報告自己觸發副作用？使用者需要知道哪些工作昂貴、哪些仍不確定，原 owner 則保留判斷「這個工作是否必要」的責任。原 reviewer 的授權只到 assessment 與 case record，沒有修改產品、執行 suite、新跑模型或發布網站；本次網站上的繁中交付由協調者另行處理。

## 發現一：資料路徑保留了「量到成本」與「發現可修缺陷」的差別

資料生產端是 `test_manager._run_suite`（448–452 行）。module log 帶有 `operation`、模組識別、elapsed seconds、exit status 及執行是否完整。讀到函式內容，不代表已觀察它實際執行。

`cost_telemetry.timing_log`（302–334 行）讀取符合格式的 stderr lines，將 `test.module` 轉成 verification-family 的 worker observation，保留 module、source digest、span、status 與秒數。`status`（67–79 行）把未完整執行或非零 exit 視為 failed，也保留 pending、refused。舊 log 若沒有 timestamp，不會被補上虛構的時間邊界。

`project`（175–277 行）先驗證 observation，再依 source digest、span，以及 native writer evidence 的 session 去重（deduplication）。接受同一筆 evidence 的 replay 前，還會比較其餘內容；若矛盾，會拋出 `CostRefusal`，不產生部分數值摘要。因此相同 evidence 的不同 path aliases 不會灌大計數。不過，不同 logs 仍可能記錄重複工作；去重不等於證明剩下每次執行都有必要。

接著，程式產生各 phase 的摘要，呼叫 `test_manager.review_cost`（463–503 行）。單筆成功 module observation 即使 `inclusive_seconds` 很大，也只代表觀察到成本，這裡沒有固定的慢速門檻。failed 或 refused phases 會要求 owner readback；同名 `test.module` 有多筆 observations 時也會回讀，並把 `repeat_necessity` 留為 unknown。若輸入已改變，重跑驗證就可能必要，所以不能只看「重複」便宣稱浪費。

`schema_manager.project_cost`（247–276 行）檢查傳入 review 的 subject 與 source list 是否一致，以及是否夾帶 effects、test demand 或 landing authority；同時保留原 owner gate。`cost_telemetry.report`（502–503 行）呼叫 `project_owner_feedback`，保留 owner 的 `next`，透過 `owner_transition` 驗證宣告的 continuation state，並把 effectiveness 留為 unknown（`schema_manager.py:279–367`）。所讀到的 projection functions 產生回傳物件，沒有進行 provider write 或發出 repair request。

**工程判斷：保留這個 ownership 邊界。** 假設改用「超過固定秒數便修復」，程式較簡單，也能立即自動化，但可能把必要驗證或 provider waiting 當成缺陷。目前設計需要 owner 解讀任務脈絡，代價是多一步判斷；當必要性取決於輸入時，這個代價合理。若別處已確定存在 deterministic defect，成本審查也不應成為延誤已授權修復的新關卡。

這項發現沒有支持新的產品修補。若要判斷某次重跑是否必要，最小補件是兩次 input identities、各次檢查的 required behavior，以及原 owner 的 current readback。若要證明 feedback 真正在正常流程被使用，還需一筆綁定版本的 owner response 與後續 continuation observation。本案例沒有 owner/caller 的完整實作，因此副作用邊界只確認到所提供程式內。

## 發現二：分開時間單位，才能看出真正的成本

`cost_telemetry.intervals`（163–172 行）將有時間邊界的 intervals 排序並合併，`project` 使用區間聯集計算 observed wall time，另保留 worker time。wall time 是觀察區間經過的時間；worker time 是執行單位投入的時間，兩者可能因平行工作而不同。

依 source 推導的例子：前景工作 `[100,110]` 與等待 `[105,115]` 重疊，合併後涵蓋 100 到 115，所以 observed wall time 是 15 秒，不是直接相加的 20 秒。這個例子沒有執行。nested phases 的總數標示為 inclusive、non-additive（254–271 行），因為父 phase 可能已包含子 phase，不能再次相加。

沒有證據的 CPU time、price、API calls 與 human wait 保持 null。只觀察到部分 spans 時，coverage 是 partial；某 family 完全沒有證據時是 unknown（190–205 行）。舊 log 即使沒有時間邊界，仍可提供量到的 worker duration，但 wall time 可能未知。`external` 也不會把多個 native turns 的 tokens 直接加總，因為尚未釐清數字是 cumulative 還是 incremental（630–658 行）。

簡單加總較容易實作，也可能適合表示累積資源工作量，但不能在這裡代表經過時間。區間聯集需要 timestamp 與排序，換來對重疊執行較正確的表達。

observation 的生命週期也保留缺口：`begin` 透過 caller 提供的 writer 保存未完成的 invocation intent（668–685 行）；`finish` 更新 observation 並先保存，再產生 report（688–714 行）。report overhead 之後才附加，下次 projection 才看得到，最後一次 flush 不列入（715–719 行）。若 intent 保存後中斷，會留下明確 incomplete span。所提供程式沒有證明 caller 真的持有承諾的 lock 或處理 telemetry errors；`failure` 雖提供不具授權效果的 refusal object（723–725 行），也不能單憑其存在就認定 caller recovery 有效。

**工程判斷：下游顯示應維持這些單位與涵蓋限制。** 不要把 wall、worker、inclusive phase totals 加成一個總秒數。`project_owner_feedback` 的 `elapsed_ms` 只量本機 projection function，不能變成 model latency 或整段 task-handling time。此 reviewer 沒有取得任何能證明毫秒級效能的實測。

若要做有限的 latency 主張，應補此版本正常使用時的 exact inputs、projection duration 與 receipt。若要聲稱整體工作變少，還需要在相同任務、完成邊界及 required controls 下，取得可比較的正常執行 observations。

## 驗證範圍與下一筆有用資料

檢視到的 source 支持以下設計判斷：validated observations 交給 Test Manager review；未知量測仍可見；失敗與重複訊號要求回讀；cost projection 不自行選擇 effects 或 test demand。若慢一次就授權 repair、把重疊 wall intervals 重複計算，或把缺測量轉成成功，便違反這些條件；目前檢視的 branches 沒有建立這類行為。這不等於所有 input shapes 或完整 lifecycle 都已正確。

既有 test mapping 列出 `test_cost_telemetry` 與 `test_schema_manager`（`test_manager.py:39–47`），但沒有提供它們的實作與結果。下一個有用觀察是這些既有測試對 overlap、conflicting replay、missing duration 及 owner continuation 不變的相關 controls 與綁定結果。本次沒有執行 suite，也沒有認證這些 test oracles。

三個結構化判斷保留原值：

- `agent_behavior_observed = false`：source 說明程式允許什麼，沒有說明 coding agent 當時知道什麼、如何選擇與除錯。因此 `decision_episodes` 保持空白，缺 trace 是涵蓋缺口，不是 agent failure。
- `slow_cost_alone_authorizes_repair = false`：需求與所讀到的 data-only path 都不支持只憑耗時便修復。
- `source_review_possible = true`：即使沒有 agent trace，這條 caller/callee chain 仍能支持具體機制與 tradeoff 分析。

若要進一步評估 Agent，只需先補一段有實質後果的決策：動作前的任務與證據、實際動作、tool result、當時有記錄的理由，以及之後的調整或停止決定。不能從程式碼倒推實作者的隱藏推理。

這份審查完成了指定來源範圍內的 Architecture 與單位／coverage 分析。實作者的 Debugging、Reasoning clarity、Communication、Attention to detail 與 Developer trust 沒有被評分；也沒有 A/B、prediction score、Human calibration、Staff-level 認證或 measured savings。產品 runtime 閉環與 agent 行為評估仍待對應證據。
