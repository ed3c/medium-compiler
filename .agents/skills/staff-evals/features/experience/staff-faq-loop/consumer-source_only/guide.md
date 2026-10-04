先讀 assessment.md 的設計判斷，再開 case.json 的 evidence 查到來源。這是一份 implementation_review（實作審查），沒有執行產品。檔案摘要吻合只能證明讀到指定副本，不能證明工程成果已交付。

核心閱讀順序是 `cost_telemetry.report → project → test_manager.review_cost → schema_manager.project_cost → project_owner_feedback`。前三個步驟整理來源與成本；後兩個步驟保留成本觀察及原 owner（狀態負責者）的接續動作。報告中列出函式與行號，方便檢查輸入、分支、缺口及權限。`case.json` 保存本案判斷、反例與下一個觀察，`consumer-report.json` 保存四個有限範圍判斷及 instruction 摘要，`capture.md` 記錄本次實際操作範圍。

閱讀數值時，先問量測對象。wall time 是經過時間；worker time 是各工作者累積時間；inclusive phase time 包含子區段，不能直接全部相加。null 代表未知。partial 代表僅有部分來源。elapsed_ms 代表本地投影耗時，不預測外部執行成功，也不衡量工程判斷品質。

閱讀失敗或重複時，先問原 owner 現在知道什麼。兩次 test.module 紀錄可能是必要的修正後驗證。`needs_owner_readback` 要求查證必要性，不是新的測試或修復指令。舊的 resolved/null 結果可被保留為歷史，但沒有 continuation_state 時不等於新的完成證據。

若要延伸成 Agent（實作者）工作流程評估，最少補上同一決策前的輸入、實際行動、結果與後續調整，以及可辨識的 actor。理由未記錄就維持 null。若要驗證產品，補上既有針對性控制與實際 caller 對拒絕、缺口、重複資料的回讀。應由現有 Test Manager 選必要控制；本案沒有要求完整測試或新的 benchmark（基準測試）。

若要練習真人工程判斷，下次先讓真人在尚未看到評語與結果前保留自己的預測、理由和可推翻條件，再保留原始答案、後續觀察與分歧。本案已讀來源，不能倒填為前瞻預測。真人未回答時繼續可支持的 AI 審查，human_review 保持 null。

若要宣稱 evaluator（評估器）可靠，還需真實專家標註、準則版本、相關重試成組的 train/dev/test（訓練／開發／測試）分配與未受污染的保留測試結果。紀錄各類錯誤及未解分歧。本案只有 case_review（個案審查）用途；保存案例、JSON 格式正確或四個欄位吻合，均不會自動取得這些資格。
