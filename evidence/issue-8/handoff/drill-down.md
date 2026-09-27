### 先留下學習證據，再決定文章要增加什麼

閱讀地圖與學習進度是兩份不同的紀錄。[課程的 learn 工作流程](https://github.com/rohitg00/ai-engineering-from-scratch/blob/8bc378c2e07777899322ae77cd0dde94cb12fab3/.claude/skills/learn/SKILL.md) 從 LEARNING.md 取得下一課，教學與測驗後再保存 Progress log；沒有這份檔案時也允許先上課。文章章節的順序因此不應被拿來填寫課程進度，更不能因為本文已經寫到 RAG，就推定讀者已學會檢索。

這條學習路線採用下面的交接順序。這是教學安排，不是聲稱本專案已經完成 placement 或讀者測驗。

```text
課程／學習 owner 選定本輪能力
        ↓
觀察 Ops 的目前實作與需求
        ├─ 有相交的產品缺口 → 小範圍修改＋測試
        └─ 不需要改產品     → NO_CHANGE＋理由
        ↓
實驗結果＋實際的人類回答
        ↓
學習 owner 記錄本次結果與待複習項目
        ↓
medium-compiler 讀取已接納的證據
        ↓
文章增量；下一課仍由學習 owner 決定
```

以 RAG 為例，目前只靠 headers 就能描述的欄位對應問題，不會因課程開始教 retrieval 而突然需要向量資料庫。NO_CHANGE 記錄的是「這次不改 Ops」；是否理解 RAG，仍要看讀者能否完成相關練習、解釋檢索失敗，或處理一個不同的例子。必要時在隔離的練習中驗證概念，不把課綱直接變成產品 backlog。

這裡也有兩種不同的 checkpoint。學習 checkpoint 保存讀者在實驗中的預測、解釋與修正判斷；文章的 reader checkpoint 則檢查成稿能否支持讀者回答。後者即使已收到答案，也不能替前者補寫完成紀錄。缺少學習 owner 接納時，文章工具應指出缺少哪份交接資料，停在原稿，不代答、不推進 LEARNING.md。一般的來源解釋或文章修訂仍可獨立進行，但不能改名成「純寫作」來繞過一個尚未完成的學習任務。

