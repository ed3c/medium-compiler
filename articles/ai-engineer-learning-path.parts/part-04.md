## 11. 模型內部：平行學，不需要先學完才能做產品

應用主線進行時，可以另外建立一條 model-internals 路線。

英文理論先讀 Jurafsky 與 Martin 的 [Chapter 7: Transformers and Pretraining](https://web.stanford.edu/~jurafsky/slp3/7.pdf)，它直接推導 attention、Transformer、decoding 與 pretraining。要把概念落成模型，再使用 Sebastian Raschka 的公開 [LLMs from Scratch](https://github.com/rasbt/LLMs-from-scratch)。中文則直接讀 Happy-LLM 的[第五章〈動手搭建大模型〉](https://github.com/datawhalechina/happy-llm/blob/main/docs/chapter5/%E7%AC%AC%E4%BA%94%E7%AB%A0%20%E5%8A%A8%E6%89%8B%E6%90%AD%E5%BB%BA%E5%A4%A7%E6%A8%A1%E5%9E%8B.md)，不要只停在 README。

這條路線適合回答：

- tokenization 實際產生什麼？
- attention 怎麼改變表示？
- causal mask 限制什麼？
- pretraining 與 instruction tuning 改的是哪一層？
- LoRA 到底更新哪些參數？

但 Ops Reconciliation Copilot 的第一個產品問題，不需要你先從零訓練 GPT。

所以兩條線應該並行：

```text
Application Engineering
structured output
→ evals
→ runtime boundary
→ persistence
→ deployment

Model Internals
tokenization
→ attention
→ GPT implementation
→ training / fine-tuning
```

它們會在 inference、adaptation、cost 與 debugging 再次交會。

## 12. Fine-tuning：只有觀察到穩定行為缺口，才值得進場

目前四個 smoke cases 不是 fine-tuning dataset。

如果 aliases case 偶爾失敗，第一步也不是立刻做 LoRA。

先問：

- prompt 是否把 output contract 說清楚？
- ambiguous input 是否應該回 `clarify`？
- 失敗是不是來自某一類 header？
- 換 model 是否改善？
- deterministic rule 能不能直接解掉？
- 有沒有足夠且合法的 examples？

只有當 failure taxonomy 穩定，而且 prompt、model selection、deterministic rule 都不能合理解決時，fine-tuning 才開始變成候選方案。

如果真的走到這一步，先讀免費完整的 [Chapter 8: Post-training](https://web.stanford.edu/~jurafsky/slp3/8.pdf) 理解 fine-tuning 與 alignment，再做 Happy-LLM [第六章〈大模型訓練流程實踐〉](https://github.com/datawhalechina/happy-llm/blob/main/docs/chapter6/%E7%AC%AC%E5%85%AD%E7%AB%A0%20%E5%A4%A7%E6%A8%A1%E5%9E%8B%E8%AE%AD%E7%BB%83%E6%B5%81%E7%A8%8B%E5%AE%9E%E8%B7%B5.md) 的 SFT / LoRA / QLoRA；要看現代 library 流程，再進 Hugging Face LLM Course 的 [Supervised Fine-Tuning](https://huggingface.co/learn/llm-course/chapter11/1) 與 [Evaluation](https://huggingface.co/learn/llm-course/chapter11/5)。

Fine-tuning 是 adaptation branch，不是 AI Engineer 身分認證。

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

## 13. 把學習路徑壓成五個可交付里程碑

### Milestone 1 — Model boundary

**要做的事**

讓模型只接收必要資料，定義可解析的 response contract，並保留 manual fallback。

**直接讀**

[Ops `app/llm.py`](https://github.com/ed3c/ops-reconciliation-copilot/blob/24a56d18661630b0dba97dcb0b057dce07b0ab32/app/llm.py)

[OpenRouter docs](https://openrouter.ai/docs)

[AI Engineering from Scratch](https://aiengineeringfromscratch.com/)

**通過條件**

你能說清楚 schema validation 能證明什麼、不能證明什麼。

### Milestone 2 — Deterministic execution

**要做的事**

把真正需要 correctness 的計算留在可測試的程式裡。

**直接讀**

[Ops `app/main.py`](https://github.com/ed3c/ops-reconciliation-copilot/blob/24a56d18661630b0dba97dcb0b057dce07b0ab32/app/main.py)

[Python Decimal](https://docs.python.org/3/library/decimal.html)

**通過條件**

給定 sources + mapping，你能重算 findings，而且不需要模型。

### Milestone 3 — Evals

**要做的事**

保存固定 cases、預期行為、逐筆結果與版本身分。

**直接讀**

[Ops eval cases](https://github.com/ed3c/ops-reconciliation-copilot/blob/24a56d18661630b0dba97dcb0b057dce07b0ab32/evals/cases.jsonl)

[Ops eval runner](https://github.com/ed3c/ops-reconciliation-copilot/blob/24a56d18661630b0dba97dcb0b057dce07b0ab32/evals/run.py)

[AI Evals FAQ](https://hamel.dev/blog/posts/evals-faq/)

**通過條件**

你能把「這個 case 通過」和「產品整體準確」分開。

### Milestone 4 — Runtime and state

**要做的事**

處理 slow provider、persistent state、concurrency、error recovery 與 access boundary。

**直接讀**

[Ops `app/storage.py`](https://github.com/ed3c/ops-reconciliation-copilot/blob/24a56d18661630b0dba97dcb0b057dce07b0ab32/app/storage.py)

[FastAPI docs](https://fastapi.tiangolo.com/)

[Ops runtime verifier](https://github.com/ed3c/ops-reconciliation-copilot/blob/24a56d18661630b0dba97dcb0b057dce07b0ab32/scripts/verify_runtime.py)

**通過條件**

你能解釋為什麼 provider request 不應長時間持有 DB transaction，以及 response 回來後為什麼要重新讀 state。

### Milestone 5 — Agent and Infra decisions

**要做的事**

知道何時保留 workflow、何時增加 agentic choice，以及何時深入 inference system。

**直接讀**

[Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)

[深入理解 AI Agent（繁中）](https://github.com/bojieli/ai-agent-book/blob/main/docs/zh-TW/README.md)

[深入理解 AI Infra](https://github.com/bojieli/ai-infra-book)

**通過條件**

你可以指出一個「不應該交給模型的 decision」，以及一個只有量測後才值得做的 infra optimization。

