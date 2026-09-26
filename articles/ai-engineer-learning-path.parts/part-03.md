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

