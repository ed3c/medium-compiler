# 把實作證據寫成完整文章

文章讓沒有前文的讀者理解原因、步驟與結果，保留原課的要求與限制。

## Sub-features

- 寫作：依 `medium-writing` 把研讀與實作轉成自然的繁體中文解釋。
- 編譯：新作 Stage 0–7；既有稿依合法修訂流程；保存同一版本的原文与結果。
- 交付：完整文章、context、可重跑範例與去敏證據；receipt 只證明機械條件。

## How to get to it (user POV)

從「按上一課完成方式新增下一篇」或修訂既有課程文章進入。
讀 `README.md`、`.agents/skills/medium-writing/SKILL.md` 及其完整 writing contract，
使用 `prompts/medium-article.md` 既有輸入，不新增另一套寫作 pipeline。

## Driving it with medium-compiler

Preconditions: skill doctor 成功，lesson-practice 筆記、來源與執行證據已備妥；若有未完成
實作，在文章與 context 如實保留。文章用途由任務決定，不能為逃避 handoff 改名。

- **寫作**：先給章節目錄。原課理論逐章解释「為什麼、怎麼做、何時失效」，Exercises
  給實際答案、推理與驗證結果，不增加等待學員回答的附加門檻。第一課的具體問題不是
  所有文章的固定問卷。補充／替代章節標明來源與有效範圍，正文不放内部流程狀態或表格。
- **編譯**：先讀 `python3 medium_compiler.py --help`。新稿 `init --spec ... --run-dir ...`
  並依 `next` 逐階段 submit。純文字修訂先留真實 before，用 `init --draft` 及 Stage 6–7；
  來源追加依 medium-writing 走 lossless_batch 的 preflight → boot → next → drill-down →
  review → finish，保留來源佇列與 batch proof。單一來源連結更正依現有 source_correction
  coverage；尚無支援的技術替換明示缺口，不能假裝 prose copyedit 或改 accepted state。
  實際全文經 assemble、verify、
  check-receipt 後比對輸出 bytes，按現有路由保存 proof，不虛构 Stage 0–5 或 Issue ID。
- **上下文**：沿用 `articles/application-engineering-colab.context.json` 的用途、sources、
  review、assembly 與 unresolved 慣例，填本課真實 ref、執行與 article hash，不照抄 PASS。
  保存可公开程式與 evidence；讀者連結指向完整開放教材或具體 code，不只連首頁。
- **維護 live drive**：用保留的第一課全文做一次 **無改動重新編譯控制**。在 `$LESSON_RUN`
  建立 spec（topic 說明此控制、claims/terms 為空）與 coverage
  `{"elements":["copyedit"],"claims":[],"terms":[]}`，用第一課檔案 init --draft，next
  必須為 Stage 6，再 submit 同一檔、assemble、verify、check-receipt。比對 canonical 與
  原稿 bytes 完全相同，保存 commands / receipt；無變動控制不呼叫 prove-update。
  這不是新寫作、語意獨立審視或重發文章。
- **拒絕控制**：執行
  `python3 .agents/skills/verify-medium/scripts/verify.py --feature bounded-revision --out "$LESSON_RUN/revision-control"`。
  既有 driver 檢查受保護內容改動與過期 receipt 被拒絕；其 Ops 範例不冒充本課內容驗證。

## Gotchas

原課有多少章就審多少章；medium-writing 的教學責任不是固定標題數。自動編譯 VALID、
作者審視及獨立語意審視分開，保留未測的學習效果。對於正式 learning-episode 仍由
上游 owner 提供 acceptance、人的 checkpoint 與進度；本文工作不寫 LEARNING.md。
文章裡的下一課連結與網站導航要一致，尤其舊稿可能仍連原課而網站已發表本站下一篇。
