# 職缺要求如何落在一次工程評估

以下將使用者提供的 Staff Software Engineer (AI Evals) 職缺，對應到 reviewer 可執行的工作。這是本專案的實作對照，不是 G2i 官方 rubric，也不表示這次案例已覆蓋全部能力。先從實際案例選擇有證據的面向，再提出判斷。

| 職缺要求 | Reviewer 實際要做什麼 | 不能超出的證據範圍 |
| --- | --- | --- |
| 評估並改善 coding systems | 指出觀察到的 Agent 選擇，提出具體修正或保留理由。 | 產出報告與發布網站不等於量到 model improvement。 |
| 工作重點是 evaluation | 交付可辯護的評估與回饋；必要時用小型 reproduction 或 patch 解答問題。 | 完成功能只是輔助證據，不是品質結論。 |
| Realistic、complex workflows | 保留相關 callers、shared state、dependencies、constraints 與 external effects。 | 複雜度來自任務，不能用刻意拉長 trace 代替。 |
| End-to-end review | 重建已觀察的需求理解、探索、實作、驗證與交接。 | 部分 capture 只支持對應片段，缺失區間保持明確。 |
| Engineering judgment | 檢查問題選擇、scope、risk、alternatives 與停止決策。 | 依當時可得資訊判斷，不能只看最後成功與否。 |
| Debugging quality | 追蹤症狀、競爭假設、能區分原因的 checks、新觀察與調整。 | 沒有新前提的重跑，與必要等待或修改後驗證不同。 |
| Reasoning clarity | 檢查寫出的前提如何支持結論。 | 正確程式不能證明未記錄的隱藏推理。 |
| Architectural thinking | 比較 ownership、依賴方向、failure isolation、migration 與維護成本。 | 命名、圖或規則符合程度，不直接證明 abstraction 合理。 |
| Written communication | 寫出讓讀者能保留、修改或調查的 verdict，連結 evidence、consequence 與 correction。 | 職缺要求英文溝通；此繁中閱讀版保留英文原稿，沒有測試使用者英文能力。 |
| Attention to detail | 核對版本、caller、input shape、units、edge cases、mocks 與 negative assertions。 | 說明細節如何影響正確性或判斷，不以檢查數量代替。 |
| Developer trust | 對照完成聲明、實際動作與 current results，檢查錯誤是否被更正。 | 誠實揭露限制有幫助，仍不能填補缺失的評估。 |
| Nuanced subjective judgment | 明確選邊，說明前提、counterevidence 與成立的例外。 | 有不確定性，不代表證據強弱不同的方案必須視為等價。 |
| 區分細微品質差異 | 在同一 constraints 與 completion boundary 下比較可行方案。 | 沒有執行過的方案標為 hypothetical，不能虛構 A/B。 |
| 找出 misleading、weak、incomplete、low-signal outputs | 定位實際 statement/action、失效前提及會導致的錯誤決策。 | 不列與任務脫節的通用問題。 |
| Structured feedback | 將每個重要 finding 連到選擇、code/trace、後果與可解答問題的 check。 | 必填欄位相符，不代表內容品質已驗證。 |
| 定義好的工程行為 | 保存好決策、失敗對照與合理例外，供後續案例使用。 | 一筆經驗不能升級為無條件指令。 |
| Staff／Principal／Architect／Tech Lead 經驗 | 有證據時檢查跨元件影響、長期 interface、operational constraints 與 tradeoffs。 | skill、case 數量或 AI 報告不授予職級。 |
| Hands-on 與 fundamentals | 閱讀 patch 及相關實作，核對 state、errors、concurrency 與語言語意。 | 能查證具體主張時，不能停在 source summary。 |
| 深入 TS/JS、Python 或 Go | 深入一個熟悉的 stack；不熟悉的語言行為先查證。 | 廣泛但淺層的使用，不能當成深度；測試數量也不能證明專精。 |
| High quality bar | 保留重要 negative controls，質疑看似合理但缺證據的推理。 | 不靠虛構缺陷或任意數字評分表現嚴格。 |
| Ambiguous、fast-moving work | 選擇能改變重要決策的下一個觀察，同時繼續獨立可做的工作。 | 未知輸入不構成無關全套測試或架構重寫的理由。 |
| Complex debugging、large/high-context systems | 檢查實際 boundary interactions、state lifetime 與 recovery。 | 小型 fixture 不能證明大型系統的操作經驗。 |
| Technical leadership、review、mentoring | 解釋修正為何有效，以及實作者下次該辨識什麼。 | 回饋應教會可重用的判斷，不增加無必要規則。 |
| AI-assisted workflows；Codex、Claude Code、Cursor | 閱讀可得的 tool use、context acquisition、retries、patch 與最終聲明。 | 用過品牌不等於具備 eval 經驗，也不強制特定品牌 trace。 |
| Quality 與 execution velocity | 區分必要調查、無新資訊操作、返工及可得的 elapsed/token costs。 | 快不能補償漏掉結果；未知成本不等於零。 |
| Technical review／calibration | 審查真實 code 與選擇，比較真正的專家判斷並保存分歧。 | fresh AI feedback 不等於 Human calibration。 |

薪酬、約兩週、ASAP、40+ hours/week、地區、English fluency、Okta／Kolide／NDA 與 security onboarding 屬於聘任和合作條件。它們需要在真實申請及雇主 onboarding 處理，不能變成 evaluator 功能。約五小時的單題處理時間是工作背景，不是測試最低時間或通過門檻。公司背景與 evaluation-phase payment 也不定義工程驗收。

成本議題的責任分工維持原設計：Staff Evals 評估 Agent 的選擇與理由；Test Manager 負責必要驗證與 cost review；Schema Manager 投影有證據的 facts 與 gaps；原 owner 決定 effects。Code quality 應落到 API 使用、invalid states、error propagation、mutable fixture sharing 與維護後果。lint 只是一種有限觀察。毫秒級 known-state projection 也不是工程品質預測，不必強迫每次 review 都做 prediction。
