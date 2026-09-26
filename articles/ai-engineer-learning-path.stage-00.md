# Stage 0｜Medium-native 格式、Ops Reconciliation Copilot 與決策地圖

## Medium 最終正文格式

Medium 官方 story editor 公開的原生格式包含 headings、subheadings、粗體、斜體、連結、quote、lists、code blocks、inline code、images 與 embeds；沒有原生 table block。

因此 final Medium body：

- 不使用 Markdown table 或 HTML table；
- 需要矩陣資訊時改用小標題 + **粗體欄位** + 短段落／列表；
- 二選一比較使用 Option A / Option B；
- runtime、目錄、資料流只有在固定寬度本身有價值時才用 `text` code block；
- 以 headings / subheadings 作為導航；Medium web 會自動產生 table of contents；
- Stage 0 可以列規劃目錄，但 final article 不需要重複一份人工 TOC。

## 主線案例

主線固定為公開的 [Ops Reconciliation Copilot](https://github.com/ed3c/ops-reconciliation-copilot)，來源 commit：

`24a56d18661630b0dba97dcb0b057dce07b0ab32`

核心資料流：

```text
兩份 CSV
    ↓
headers only
    ↓
LLM mapping proposal
    ↓
application validation
    ↓
separate confirmed mapping
    ↓
deterministic Decimal reconciliation
    ↓
findings + evidence
```

它同時暴露 model boundary、structured output、evals、workflow / Agent boundary、persistence、concurrency、provider latency、AI Infra 與 fine-tuning decision。

## 這篇文章的 10 個主要讀者決策

### A01｜先做 application，還是先從零訓練模型？
**選擇條件**：目標是能交付的 AI product。  
**文章選擇**：先建立可測試的 model boundary 與 deterministic execution；model internals 平行深化。

### A02｜模型 output 可以直接觸發 reconciliation 嗎？
**選擇條件**：mapping 是 probabilistic output，但金額結果要求可重算。  
**文章選擇**：模型只產生 `mapping_proposal`；可執行的 `mapping` 另外確認。

### A03｜為什麼 sources、mapping_proposal、mapping、findings 要分開？
**選擇條件**：它們具有不同 authority 與重播需求。  
**文章選擇**：分開保存，不讓 conversation history 成為唯一 state。

### A04｜JSON schema 通過是否等於欄位語意正確？
**選擇條件**：合法 JSON 仍可能選錯業務欄位。  
**文章選擇**：schema validation 與 semantic / task validation 分層。

### A05｜固定 workflow 還是 full Agent？
**選擇條件**：upload → proposal → confirm → reconcile 的主流程已知。  
**文章選擇**：保留 workflow；只有出現真正動態 decision 才增加 agentic control。

### A06｜現在需要 RAG 嗎？
**選擇條件**：當前問題是 CSV schema ambiguity，不是缺少外部知識。  
**文章選擇**：不加入 RAG；等 mapping 真的依賴資料字典或 policy evidence 再比較。

### A07｜4/4 eval case 能證明什麼？
**選擇條件**：只有四個固定案例與一個記錄 checkout。  
**文章選擇**：只聲稱 smoke coverage，不外推企業準確率或 p95。

### A08｜慢 model request 回來時，還能直接寫 state 嗎？
**選擇條件**：等待 provider 時 run state 可能已改變。  
**文章選擇**：provider call 不長時間持有 transaction；回應後重新讀 current state。

### A09｜什麼時候該深入 AI Infra？
**選擇條件**：已有真實 request、token usage、latency 或 memory / capacity bottleneck。  
**文章選擇**：先量測，再追 inference / serving 機制。

### A10｜什麼時候才值得 Fine-tuning？
**選擇條件**：failure taxonomy 已穩定，prompt、model selection、deterministic rule 仍無法合理解決，且有合法資料。  
**文章選擇**：此時才評估 fine-tuning；不是預設必修步驟。

## Runtime 心智圖

```text
CSV inputs
│
├─ source rows + headers
│
└─ headers
    ↓
LLM proposal
    │
    ├─ malformed / invalid → reject / manual mapping
    ├─ clarify            → ask for missing meaning
    └─ proposed
        ↓
application validates
        ↓
separate confirmed mapping
        ↓
normalize
        ↓
Decimal reconciliation
        ↓
findings
        ↓
persist / review / export
```

## 學習路徑心智圖

```text
Model boundary
    ↓
Structured output + validation
    ↓
Deterministic execution
    ↓
Evals
    ↓
State / persistence / concurrency
    ↓
Workflow vs Agent decision
    ↓
Measurement
    ↓
AI Infra when needed

Parallel:
tokenization → attention → LLM internals

Conditional:
external knowledge need → RAG
stable adaptation failure → Fine-tuning
```

## Open-access link policy

Reader-facing Medium links必須：

1. 不要求購買書籍或訂閱後才能閱讀正文；
2. 不連到商店、O'Reilly preview、Amazon 或其他付費預覽頁；
3. 不連到 owner-only workspace、private repo 或登入後才有內容的頁面；
4. 優先 public GitHub source、官方 public docs、完整公開文章或開源書；
5. provider / cloud docs 可以公開閱讀，即使真正執行服務時需要 API key 或帳號；
6. 主例程式碼使用 pinned public commit URL，避免文章描述隨 `main` 漂移。

完整 allowlist：`references/open-access-resources.json`。
