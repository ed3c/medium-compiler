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

