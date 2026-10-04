# 閱讀指南

先讀 assessment.md 的第一段與「決策二」。這個案例評估一個具體修補：多份報告加入後，測試應核對目錄內每份交付，並保持歷史報告原有的限制聲明。

1. 用 case.json 找到 before-test.py、after-test.py、ai_evals_site.py 的絕對路徑與 SHA-256；對照測試第28行的固定數量，和新版本第28–53行。SHA-256 是 bytes 身分，不是語意正確性評分。
2. 用 observations.json 的 e1–e7 還原症狀、局部重現、明示理由、修補與後續結果。這是協調者轉錄，並非完整平台逐事件擷取。用 failed/passed-ci-jobs.json 與 patch-commit.json 核對各 head。
3. 把 e8/e9 的部署說法當成有範圍的歷史支持；沒有完整讀回檔案就不要聲稱自己驗過目前網站。也不要把空輸出輪詢當成多次產品執行。
4. 閱讀已列入輸入的 delivered-assessment.md，但其 Soodles 數值與原 API 行為需原證據才能獨立驗證。保留英文歷史報告是事實保存，本次中文評估不是改寫歷史。
5. 查看 consumer-report.json 的四個布林結論與 assessment.md 的解釋；結構正確不能替代工程判斷。capture.md 記錄本次實際操作，屬消費者自述，不能冒稱獨立 transcript。

本 case 的用途是 case_review（個案審查）。human_review 為 null，prediction 為 null，split 為 null；沒有人工標籤、未見測試集或前瞻評分。若用於練習，請選新案例，在揭露結果前留下人的判斷，再保存專家回饋和歧見。不能把 AI 記錄數量換算成人的 Staff 年資或 evaluator（評估器）可靠度。

本次未執行產品測試、網站 build、部署、外部回饋或 repository 寫入。case.json 是此指定輸出目录內的案例保存；依任務範圍沒有修改產品 experience/index.json。
