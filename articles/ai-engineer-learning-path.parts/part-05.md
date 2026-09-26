## 14. 作品集不是 README 截圖，而是一條 evidence chain

AI Engineer portfolio 最有價值的不是技術名詞數量，而是讀者能不能從 repository 重建你的工程判斷。

Ops Reconciliation Copilot 已經示範了一個很好的 evidence layout：

```text
repository
├─ app/
│  ├─ llm.py
│  ├─ main.py
│  └─ storage.py
│
├─ evals/
│  ├─ cases.jsonl
│  └─ run.py
│
├─ scripts/
│  └─ verify_runtime.py
│
├─ tests/
│  └─ contract / runtime tests
│
└─ docs/evidence/
   └─ retained evaluation artifacts
```

你要能回答：

**Code** — 哪個 function 實作這個 decision？

**Test** — 哪個 failure 被拒絕？

**Eval** — 哪種 model behavior 被量測？

**Receipt** — 這個結果綁在哪個 checkout、dataset、prompt 或 model？

**Unknown** — 哪些事情仍沒有證據？

這種作品集比「我會 LangChain / RAG / Agent」更容易讓面試者判斷你的工程深度。

## 15. 面試時怎麼用英文壓縮這個系統？

**Why doesn't the LLM reconcile transactions directly?**

> The model only proposes column mappings. The application validates the proposal, a separate mapping is confirmed, and deterministic Python code owns transaction matching and Decimal arithmetic.

**What does structured output solve?**

> It makes malformed responses rejectable. It does not prove that a valid mapping is semantically correct.

**Why keep `mapping_proposal` separate from `mapping`?**

> They have different authority. A proposal is probabilistic advice; the mapping is the validated input to deterministic execution.

**Why isn't this a full agent?**

> The workflow is already known. Giving the model control over the next step would add state and failure modes without solving the current ambiguity problem.

**What does the 4/4 evaluation prove?**

> It proves that four fixed cases matched expectations on one recorded checkout and model configuration. It does not establish representative accuracy or latency percentiles.

## 16. Master Map：從真實 failure 決定下一段學習

```text
兩份交易 CSV 欄位不同
        ↓
模型只看 headers
        ↓
mapping proposal
        │
        ├─ malformed / unknown field
        │      → structured-output / contract problem
        │
        ├─ ambiguous
        │      → clarify / task-design problem
        │
        └─ valid proposal
               ↓
        separate confirmed mapping
               ↓
        deterministic normalize + reconcile
               │
               ├─ arithmetic / matching error
               │      → software correctness problem
               │
               └─ findings
                      ↓
               eval + persistence + review
                      │
                      ├─ model behavior unstable
                      │      → eval / model / adaptation
                      │
                      ├─ workflow needs dynamic choices
                      │      → evaluate Agent design
                      │
                      ├─ needs external policy evidence
                      │      → evaluate RAG
                      │
                      └─ latency / capacity bottleneck
                             → AI Infra
```

這就是整條學習路徑的核心：

> 不要照技術名詞的順序學下一章；看你現在的 failure 屬於哪一層。

資料問題不要用 Fine-tuning 修。

deterministic calculation 不要重新交給 LLM。

固定 workflow 沒有必要為了履歷改造成 Agent。

四個 eval case 也不要包裝成企業準確率。

當你可以從一個真實產品，把 problem、decision、representation、runtime、eval、failure boundary 和 evidence 串起來時，你已經不是只在「學 LLM」；你正在做 AI Engineering。
