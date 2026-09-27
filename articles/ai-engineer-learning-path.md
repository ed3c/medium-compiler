# 從軟體工程師到 AI Engineer：用 Ops Reconciliation Copilot 串起 LLM、Evals、Agent 邊界與 AI Infra

中文優先、實作優先的學習路徑：不是把 LLM、RAG、Agent、Fine-tuning 和 AI Infra 當成一串必修名詞，而是沿著一個可以公開檢查的產品，理解每個技術決策在什麼問題出現時才值得加入。

這篇文章的主例是公開的 [Ops Reconciliation Copilot](https://github.com/ed3c/ops-reconciliation-copilot)。它處理一個很適合 AI Engineer 學習的問題：兩份交易 CSV 使用不同欄位名稱，模型可以提議欄位對應，但真正的交易配對與金額差異由 Python 執行。

這個案例有一條清楚的工程邊界：

```text
LLM proposes
    ↓
application validates
    ↓
human confirms mapping
    ↓
deterministic Python reconciles
    ↓
findings + evidence are persisted
```

這比「做一個 chatbot」更適合拿來練 AI Engineering。模型不是整個產品；你必須同時處理 input contract、structured output、deterministic logic、evals、persistence、runtime、failure handling 和 deployment。

本文引用的學習資源全部可以直接在公開網頁或公開 GitHub repository 閱讀。沒有 O'Reilly 預覽頁、書店頁或需要購買才能繼續閱讀的連結。部分 API 或部署服務在你實際執行時仍可能需要帳號或 API key，但閱讀本文連結不需要付費訂閱。

## 1. 先把「成為 AI Engineer」換成一個可以交付的問題

如果目標只是「學 LLM」，學習路徑很容易變成：

```text
Transformer
→ Prompt
→ RAG
→ Agent
→ Fine-tuning
→ Infra
```

這個順序的問題是：它沒有說明為什麼現在需要下一項技術。

Ops Reconciliation Copilot 把目標改成一個更具體的問題：

> 兩份欄位名稱不同的交易 CSV，怎麼讓模型幫忙辨識 schema，又不把交易計算交給模型？

[公開 README](https://github.com/ed3c/ops-reconciliation-copilot/blob/24a56d18661630b0dba97dcb0b057dce07b0ab32/README.md) 已把產品邊界寫得很清楚：只把左右 CSV 的 headers 傳給模型；模型產生 `mapping_proposal`；實際 `mapping` 要另外提交；金額差異由 `Decimal` 計算。

因此第一個 AI Engineer 能力不是「會呼叫模型」，而是能回答：

**模型應該負責什麼？**

**什麼結果必須由程式或人決定？**

**模型錯了時，系統怎麼停在安全狀態？**

如果想先走一條完整的 application engineering 路線，可以用 [AI Engineering from Scratch](https://aiengineeringfromscratch.com/)；它公開 20 個 phases、523 lessons，每課都把問題接到數學、程式與測試。需要補 LLM 本體時，不再連到只有摘要的 companion repo：中文直接讀 Happy-LLM 的[第五章〈動手搭建大模型〉](https://github.com/datawhalechina/happy-llm/blob/main/docs/chapter5/%E7%AC%AC%E4%BA%94%E7%AB%A0%20%E5%8A%A8%E6%89%8B%E6%90%AD%E5%BB%BA%E5%A4%A7%E6%A8%A1%E5%9E%8B.md)，英文理論直接讀 Jurafsky 與 Martin 免費公開的 [Chapter 7: Transformers and Pretraining](https://web.stanford.edu/~jurafsky/slp3/7.pdf)。

## 2. 第一個核心決策：LLM 可以提議，但不能直接執行對帳

Ops Reconciliation Copilot 最值得學的不是 prompt，而是它把模型輸出放在哪個 authority level。

[模型介面 `app/llm.py`](https://github.com/ed3c/ops-reconciliation-copilot/blob/24a56d18661630b0dba97dcb0b057dce07b0ab32/app/llm.py) 接收欄位名稱，要求模型回傳結構化結果。回應可以是：

```text
proposed
    → 模型認為欄位對應足夠明確

clarify
    → 模型認為資料不足，需要人補充
```

但 `proposed` 仍然只是 proposal。

真正的 runtime 邊界在 [主流程 `app/main.py`](https://github.com/ed3c/ops-reconciliation-copilot/blob/24a56d18661630b0dba97dcb0b057dce07b0ab32/app/main.py)：

```text
mapping_proposal
    ≠
mapping
```

模型成功回應，不會直接觸發 reconcile。

這是一個可以帶到其他 AI 產品的規則：

> Probabilistic output should not silently become deterministic authority.

如果你之後做的是採購、財務、客服退款、資料庫操作或 deployment Agent，同一個問題都會再次出現：模型可以提出 action，但哪個 owner 有權讓 action 生效？

這就是 AI Engineer 與「把 API 接起來」之間的差異。

## 3. Representation：為什麼要把 `sources`、`mapping_proposal`、`mapping` 和 `findings` 分開？

如果所有資訊都塞在一個 conversation history 裡，系統很難回答：

- 哪兩份資料是原始輸入？
- 模型建議過什麼？
- 人最後確認了什麼？
- 實際計算使用哪份 mapping？
- 結果之後能不能重新計算？

Ops Reconciliation Copilot 把這些概念拆開。可以把 runtime 心智模型寫成：

```text
Run
├─ sources
│  ├─ left CSV rows + headers
│  └─ right CSV rows + headers
│
├─ mapping_proposal
│  └─ LLM suggestion + model metadata
│
├─ mapping
│  └─ confirmed executable column mapping
│
├─ findings
│  └─ deterministic reconciliation output
│
└─ reviews
   └─ later review decisions
```

持久化實作可以直接看 [`app/storage.py`](https://github.com/ed3c/ops-reconciliation-copilot/blob/24a56d18661630b0dba97dcb0b057dce07b0ab32/app/storage.py)。

這個 representation 的價值不是「JSON 比較漂亮」。它讓每個 state 有不同責任：

```text
proposal
    → 可以錯，但不能直接改結果

mapping
    → 已經通過應用層檢查，可以進 deterministic calculation

findings
    → 應該可以由 sources + mapping 重算
```

當你開始設計 Agent memory、tool results、RAG citations 或 durable workflow state，先問相同問題：**不同類型的資訊是否被放在同一個權限層？**

## 4. 跟著一筆 T100，看完整 runtime 怎麼走

公開 fixture 裡有一筆很適合當 runtime witness 的資料。

左側交易：

```text
transaction: T100
amount:      100.00
currency:    USD
```

右側交易：

```text
transaction: T100
amount:      98.00
currency:    USD
```

流程不是「LLM 看完兩筆交易，回答差 2 美元」。

實際設計更接近：

```text
兩份 CSV 上傳
    ↓
只取 headers 給模型
    ↓
模型提議：
左 txn_ref       ↔ 右 reference_id
左 amount        ↔ 右 paid
左 currency      ↔ 右 ccy
    ↓
應用驗證 proposal
    ↓
mapping 被另外確認與提交
    ↓
normalize()
建立 transaction_id → rows
    ↓
reconcile()
以相同 transaction ID 比較
    ↓
Decimal("100.00") - Decimal("98.00")
    ↓
amount_mismatch
delta = 2.00
```

完整可重現流程與測試入口在公開的 [`docs/demo.md`](https://github.com/ed3c/ops-reconciliation-copilot/blob/24a56d18661630b0dba97dcb0b057dce07b0ab32/docs/demo.md) 與 [`scripts/verify_runtime.py`](https://github.com/ed3c/ops-reconciliation-copilot/blob/24a56d18661630b0dba97dcb0b057dce07b0ab32/scripts/verify_runtime.py)。

金額使用 `Decimal` 不是 AI 技巧，而是一般軟體工程 correctness。Python 官方的 [`decimal` 文件](https://docs.python.org/3/library/decimal.html) 可以直接閱讀。

這是一個很重要的學習訊號：

> AI Engineer 仍然必須是 Software Engineer。

模型只處理它擅長的歧義；可精確計算的部分留在確定性程式。

### 同一個交易 ID，為什麼保存成一個 list？

前面的箭頭把 normalize 縮成了一個步驟。實際上，它先檢查 mapping 是否包含 transaction_id、amount、currency，而且三個欄位必須存在、不能重複使用。接著逐列建立索引。transaction_id 是 CSV 裡的交易識別值；一次上傳工作的 run ID 則識別整個工作，兩者不是同一個 key。

normalize 對交易 ID 做 strip，移除首尾空白；幣別另做 strip 和 upper。它沒有把交易 ID 轉成同一種大小寫，因此 T100 與 t100 仍是不同交易 ID。每一筆正規化結果還保留 row：enumerate 從 2 開始，因為第一列是欄名，這個數字讓檢查者能回到 CSV 的原始資料列。

索引的 value 是 list，不是單筆資料。下面刻意讓左側 T100 出現兩次，作為程式的診斷輸入；它不是歷史模型報告裡的一次真實業務操作。

```text
left CSV
  row 2: T100, 100.00, USD
  row 3: T100, 100.00, USD
             |
             | normalize：相同 key 持續 append
             v
left index
  T100 -> [row 2, row 3]

right CSV
  row 2: T100, 98.00, USD
             |
             v
right index
  T100 -> [row 2]
```

若把索引改成 transaction_id 對到單筆 row，後一筆可能覆蓋前一筆，對帳時就看不見重複。保留 list，才有足夠資料區分「同一筆交易金額不同」和「交易 ID 本身就不唯一」。這段表示方式的選擇，直接決定下一步能檢查哪種錯誤。

### 有重複資料時，為什麼不能先算 2.00？

reconcile 不是看到同一個 key，就立刻把左右第一筆金額相減。它走訪左右 ID 的聯集，排序後依固定優先序分類。下面的符號目錄對應 app/main.py 的實際函式；目錄表示責任歸屬，箭頭才表示資料怎麼流動。

```text
app/main.py
├─ normalize(source, mapping)
│  ├─ 檢查欄位與資料
│  └─ transaction_id -> list of normalized rows
└─ reconcile(left, right)
   ├─ 走訪 sorted(set(left) | set(right))
   ├─ 依序分類
   └─ findings：保留左右 row 與差額
```

```text
同一個 ID 的左右 lists
  |
  +-- 任一側超過一筆？
  |     yes -> duplicate_key，delta = null
  |     no
  v
任一側沒有資料？
  |     yes -> missing_left 或 missing_right，delta = null
  |     no
  v
幣別不同？
  |     yes -> currency_mismatch，delta = null
  |     no
  v
金額不同？
  |     yes -> amount_mismatch，delta = left - right
  |     no
  v
不產生 finding
```

所以剛才的重複 T100 會得到 duplicate_key，左右的 row 仍保留在 finding 中，但 delta 是 null。即使兩側各取第一筆可以算出 100.00 − 98.00 = 2.00，程式也不會把它當成可信的金額差異。只有兩側都恰好一筆、幣別相同且金額不同，才產生 amount_mismatch 並計算 delta。

同樣地，若一側重複、另一側缺列，最先成立的仍是 duplicate_key；幣別不同時，也不會把兩個不同貨幣的數字直接相減。這些保證只涵蓋程式採用的分類規則，不證明來源 CSV 或已提交 mapping 的業務含義正確。完整條件可以回到前面連結的 app/main.py，對照 normalize 與 reconcile 逐行檢查。

## 5. Structured output：JSON 合法，不代表 mapping 語意正確

LLM 回傳 JSON 後，至少有兩種完全不同的問題。

第一種是**結構錯誤**：

```text
invalid JSON
unknown field
duplicate field choice
missing required mapping
invalid clarify response
```

這些可以由程式拒絕。

第二種是**語意錯誤**：

```text
JSON 完全合法
但 amount 被對到 tax
```

這不是 JSON parser 能證明的事情。

所以 `app/llm.py` 的 validation 只是其中一層。真正系統需要的是：

```text
provider response
    ↓
syntax / schema validation
    ↓
domain constraint validation
    ↓
human or independent task validation
    ↓
only then executable state
```

OpenRouter 的 [公開文件](https://openrouter.ai/docs) 可以直接查看 API、structured outputs、routing 與 logging 等能力。讀文件不需要訂閱；真正送出 provider request 時則需要相應的 API access。

這一節要留下的不是某個 framework API，而是一個 mental model：

> Structured output reduces one failure class; it does not remove semantic uncertainty.

## 6. Evals：先問「系統會在哪裡錯」，不要先追一個總分

Ops Reconciliation Copilot 保存了一組固定模型案例與歷史 eval。

案例定義在 [`evals/cases.jsonl`](https://github.com/ed3c/ops-reconciliation-copilot/blob/24a56d18661630b0dba97dcb0b057dce07b0ab32/evals/cases.jsonl)，runner 在 [`evals/run.py`](https://github.com/ed3c/ops-reconciliation-copilot/blob/24a56d18661630b0dba97dcb0b057dce07b0ab32/evals/run.py)。

目前公開保存的歷史報告包含四種 case：

**canonical** — 標準欄名可以直接提出 mapping。

**aliases** — `txn_ref` / `reference_id`、`amount` / `paid` 這類別名需要正確配對。

**opaque** — 欄名太模糊，預期回傳 `clarify`。

**missing_currency** — 缺少 currency 欄，預期要求補充資訊。

保存的 [歷史 JSON 報告](https://github.com/ed3c/ops-reconciliation-copilot/blob/24a56d18661630b0dba97dcb0b057dce07b0ab32/docs/evidence/2026-09-15-luna-medium.json) 記錄當次四個固定案例通過。

但 4/4 只能回答：

> 這四個固定案例在那次 checkout 上符合預期。

它不能回答：

> 企業資料準確率是 100%。

也不能推出 p95 latency、使用者節省多少時間，或模型換版後仍然相同。

這正是 eval 的用途：讓「通過了什麼」和「還不知道什麼」同時變清楚。

如果要建立更完整的 eval 方法，可以讀公開的 [Hamel 與 Shreya AI Evals FAQ](https://hamel.dev/blog/posts/evals-faq/)。實作練習則可以配合 [AI Engineering from Scratch 的 Learning Paths](https://aiengineeringfromscratch.com/learning-paths.html)，把 eval 當成產品迭代的一部分，而不是文章最後才補的 benchmark。

### 把「擋住錯誤」與「選對下一步」分開評估

假設 writer 嘗試在學習結果尚未被接納時開始文章增量，而 CLI 拒絕了操作。這裡有兩個不同的結果：護欄成功擋住寫入；writer 仍然選錯了一次。只看最後的文章沒有改變，會漏掉這次錯誤嘗試。

```text
writer 選擇操作
    │
    ├─ 操作不符合目前狀態 → 記錄一次錯誤嘗試
    │                         ↓
    │                      CLI 拒絕
    │                         ↓
    │                      沒有文章修改
    │
    └─ 操作符合目前狀態 → 檢查執行結果與交付內容
```

要比較兩版寫作指引與 CLI，兩個新 session 必須拿到相同的任務、原稿與 evidence snapshot。舊版不能讀到新版的文章或評分報告；模型、工具權限與觀察方式也要固定。記錄由 writer 以外的程序保存，至少包括工具請求、結果、exit code，以及工作目錄的修改前後差異。

這份紀錄還需要判讀。相同檔案讀了兩次，不一定是不必要的重讀；回報文章組裝 `DONE`，也不一定是在宣稱 learning episode 已完成。必須查看當時的問題、狀態與實際用語。事件被截斷、缺少工具結果或尚未 review 時，應保留「無法判定」，不能填成零次錯誤。

測試程式可以刻意製造缺少接納、過期收據或錯誤寫入，確認 observer 能否辨識。這些是控制案例，不是模型自然犯錯的紀錄。只有真正的新 session 比較，才可能支持「這次修改讓 writer 少走錯路」；文章是否讓人更容易理解，仍要另外從成稿做讀者檢查。

## 7. 為什麼這個專案現在不需要做成 full Agent？

很多 AI 學習路徑會把 Agent 當成 RAG 後面的下一章。

實務上不應該這樣決定。

Ops Reconciliation Copilot 已知的工作流是：

```text
upload
→ proposal
→ confirm
→ reconcile
→ review
→ export
```

這條路徑本身很清楚。

模型目前只需要回答：

```text
這幾個欄名可能對應什麼？
```

所以沒有理由為了「比較像 Agent」加入：

```text
while True:
    model decides next tool
```

固定 workflow 的好處是：

- 可測試的 state transition 較少；
- 可精確定義什麼時候允許 reconcile；
- provider failure 不會自動變成另一個 side effect；
- deterministic calculation 不需要經過模型重新解釋。

Anthropic 的公開文章 [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) 就把 workflow 與 agentic control 分開討論。

如果你要系統化理解 `LLM + Context + Tools`、ReAct、evaluation 與 Agent engineering，可以直接閱讀開源繁中版[《深入理解 AI Agent》](https://github.com/bojieli/ai-agent-book/blob/main/docs/zh-TW/README.md)。

學完後應該得到的不是「每個產品都要 Agent」，而是：

> 知道什麼決策值得交給模型，什麼決策應該從模型手上拿走。

## 8. RAG 不是這個產品目前的必修功能

這個案例還能修正另一個常見學習誤區：AI application 不等於一定需要 RAG。

目前的核心問題是：

```text
CSV schema ambiguity
```

不是：

```text
模型缺少外部知識文件
```

因此把向量資料庫塞進現有流程，不會自然改善 `txn_ref` 到 `reference_id` 的 mapping。

RAG 會在問題改變時變得合理，例如：

- mapping 必須遵循公司資料字典；
- 欄位語意來自多份 schema 文件；
- reviewer 需要引用 reconciliation policy；
- model suggestion 必須附可追溯的 policy evidence。

到了那個時候，再加入 retrieval，並用 eval 比較：

```text
沒有 retrieval
vs
有 retrieval
```

而不是因為「AI Engineer 路線圖下一章是 RAG」。

如果需求真的走到 retrieval，先讀完整內容而不是 resource index：Jurafsky 與 Martin 的 [Chapter 11: Information Retrieval and RAG](https://web.stanford.edu/~jurafsky/slp3/11.pdf) 從 IR 到 RAG 建立完整脈絡；中文實作可直接進 Happy-LLM 的[第七章〈大模型應用〉](https://github.com/datawhalechina/happy-llm/blob/main/docs/chapter7/%E7%AC%AC%E4%B8%83%E7%AB%A0%20%E5%A4%A7%E6%A8%A1%E5%9E%8B%E5%BA%94%E7%94%A8.md)，其中包含 evaluation、RAG 與 Agent。

## 9. Persistence 與 concurrency：AI request 也會遇到一般 backend 問題

只要模型請求可能花幾秒，runtime state 就可能在等待期間改變。

Ops Reconciliation Copilot 的一個重要設計是：模型呼叫不包在資料庫 transaction 裡。回應回來後，系統重新讀取 run state；如果 run 已經完成 reconcile，就不能再把過期 proposal 寫回去。

持久化實作在 [`app/storage.py`](https://github.com/ed3c/ops-reconciliation-copilot/blob/24a56d18661630b0dba97dcb0b057dce07b0ab32/app/storage.py)。PostgreSQL 路徑使用 `FOR UPDATE` 處理同一 run 的 read-modify-write 邊界。

這裡值得學的不是 PostgreSQL 語法本身，而是一個時序問題：

```text
read state
    ↓
call slow external model
    ↓
state may change
    ↓
response returns
    ↓
must re-check current truth
```

這也是 Agent 系統、background job、tool execution、approval flow 常見的 race condition。

API service 使用 FastAPI；[FastAPI 官方文件](https://fastapi.tiangolo.com/)可以直接閱讀。專案自己的部署與 database 設定則在公開 repo 的 [`docs/supabase.md`](https://github.com/ed3c/ops-reconciliation-copilot/blob/24a56d18661630b0dba97dcb0b057dce07b0ab32/docs/supabase.md) 與 [`docs/vercel.md`](https://github.com/ed3c/ops-reconciliation-copilot/blob/24a56d18661630b0dba97dcb0b057dce07b0ab32/docs/vercel.md)。

## 10. AI Infra：先量測一次 request，再學 serving

歷史模型報告還留下兩個很實用的數字：

```text
4 次呼叫合計：
prompt tokens     = 830
completion tokens = 208
total             = 1,038
```

client-observed latency 落在：

```text
1,184–2,131 ms
```

這些數字可以拿來問：

- latency 花在哪裡？
- prompt 長度成長會怎樣？
- provider routing 會怎樣影響 tail latency？
- request timeout 應設在哪裡？
- 什麼指標是 client-observed，什麼是 server-side？
- 模型 inference cost 和整個產品 cost 是否是同一件事？

但四次呼叫不能產生 p95。這是最重要的限定。

要往下理解 inference、KV cache、batching、memory bandwidth 與 distributed serving，可以直接讀開源的[《深入理解 AI Infra》](https://github.com/bojieli/ai-infra-book)。

先有實際 request 與 measurement，再讀 infra，術語會開始對應到真實工程問題。

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

更精確地說，這裡要分開三層 authority。課程可以觸發 **EXPERIMENT**：即使 canonical product 目前沒有缺陷，Ops 作為實驗環境仍可以用隔離路徑研究 Agent、Fine-tuning 或新的 eval 方法；如果連實驗價值都不足，才記錄 **NO_CHANGE**。這兩種結果都只回答「現在要不要研究這項能力」，不直接改 production runtime。

```text
lesson
  ↓
EXPERIMENT ──→ tests / evals / runtime evidence
  │                         │
  │                         └─ 沒有真實產品需求 → 保留實驗，不升格
  │
  └─ evidence + real product need
                  ↓
              PROMOTE candidate
                  ↓
          product owner decides
```

因此 **PROMOTE** 是第二個獨立決策，不是 `EXPERIMENT` 的自動下一步。即使實驗數據很好，只要沒有真實 product need，也可以保留成實驗能力而不改 canonical path；反過來，課程教到某個主題也不能單獨構成升格理由。這讓 Ops 可以快速擴展實驗面，同時避免 syllabus 直接變成 production backlog。

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
