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

