# 架構師不再贏辯論的那一天：一張付款流程圖如何改變團隊的決策

假設一個產品團隊即將迎接大型促銷。結帳系統仍是 Monolith，付款偶爾 Timeout，每次修改都讓工程師擔心牽動其他功能。下一波流量會增加多少，沒有人能確定。

會議上，一位工程師提議拆成 Microservices，另一位認為 Monolith 比較容易部署，有人希望直接導入 Kubernetes。三個人談的是架構，擔心的卻是不同的失敗。

## 先問會發生什麼事，再談要用什麼技術

主張拆分的人說，每次更新付款功能都得協調全站發版。支持單體的人怕的是服務間交易、監控與重試變得更難。營運工程師最擔心 Timeout 之後的重試風暴。產品經理只問一件事：促銷前能不能安全上線？

架構師沒有立刻選邊。他請每個人講出一個最想避免的故障，並拿實際的 Code、Release 記錄和 Logs 對照。修改折扣規則會不會影響付款模組？目前是否真的每次都得共同部署？Retry 是否可能對外產生第二次扣款？

這些問題指向不同的工作。模組互相修改內部狀態，需要檢查 Design-time Boundaries；共同發版拖慢交付，需要衡量 Release Coupling；付款結果不明，則要追查 Payment Attempt 與 Provider 的執行語意。把它們全叫作「Monolith 的問題」，只會讓方案比問題更早定型。

Gregor Hohpe 把這種架構師稱為 Amplifier：不替所有人保管答案，而是讓團隊有能力辨認自己在爭什麼。

## 白板畫錯了，反而看見一個缺少的狀態

架構師畫出最簡單的結帳流程：Checkout 呼叫 Payment Provider，成功便把訂單設為 Paid。他問營運工程師：「真的只有成功和失敗兩種結果嗎？」

對方補上一種情況：Provider 可能已扣款，回應卻在網路上遺失。Checkout 只收到 Timeout；Webhook 也可能稍後才到。另一名工程師指出，如果 Retry 沒有綁定同一筆邏輯付款，系統還可能送出第二個扣款請求。

白板被改成：

```text
Customer → Checkout → Payment Attempt
                           ↓
                     Payment Provider
                           ↓
                 success / failure / unknown
                           ↓
                   Reconciliation / Readback
                           ↓
                       Order State
```

圖中的 Payment Attempt 與 Reconciliation 尚須對照現有程式與 Provider Contract：程式是否在呼叫前保存付款身分？Provider 是否提供 Idempotency Key、有效期限與可查詢的最終結果？

有件事不需要等到拆服務才知道：**Timeout 不是 Payment Failure**。若把 Timeout 當成確定失敗而直接重送，可能重複扣款；若當成確定成功，則可能把未付款訂單標成 Paid。在結果可信以前，訂單狀態不能假裝已經確定。

這是 Hohpe 所說的 Phantom Sketch Artist：先畫出一張能被修正的圖，讓第一線工程師補上藏在工作經驗裡的關係。有人說「這條線不對」時，會議終於有了可以共同檢查的對象。

## Monolith 與 Microservices 原來不是兩個互斥選項

團隊回到最初的架構爭論，發現「要不要拆」其實混合了兩個問題。

一個是 **Design-time Modularity**：付款、折扣、訂單之間是否有清楚的程式碼與領域邊界？另一個是 **Runtime Modularity**：它們是否需要獨立部署、獨立隔離故障或分別 Scale-out？

這樣就有四種組合。邊界不清、一起部署的是 Spaghetti Monolith；邊界清楚、一起部署的是 Modular Monolith；拆成多個服務卻彼此緊密依賴的是 Distributed Spaghetti；邊界與部署都相對獨立，才接近團隊希望得到的 Microservices。

Distributed Spaghetti 可能同時承受跨服務追蹤、網路延遲與資料一致性成本，卻無法獨立發版。Modular Monolith 免去了部分分散式成本，但仍須靠模組 API、測試與 Code Review 維護邊界。

於是問題變成：**付款功能目前有哪些約束，非得讓它成為另一個 Process 才能滿足？**

若折扣規則直接存取付款內部狀態，先整理模組邊界也許就足夠。若有證據顯示付款功能必須獨立發版、承受不同工作負載，或滿足共同部署無法提供的隔離需求，拆分才有明確理由。

拆分也未必帶來自治。兩個 Service 如果繼續共用可任意修改的資料表，或每次都要協調同時上線，只是把原本的耦合搬到網路上。相反地，維持 Monolith 也得承擔共同發版與資源隔離的限制。成本要從實際部署、Network Hop、Observability、Versioning、Retry 和 On-call 工作算起，不能從架構名稱推導。

## 一張圖發現問題，Contract 和 Test 才能回答問題

白板上出現了兩條指向 Payment Provider 的箭頭：第一次呼叫和 Retry。有人問，Provider 會不會把它們當成兩筆扣款？

這個懷疑要回到程式與契約。相同邏輯付款是否保留同一個 Payment Attempt ID？身分在外部呼叫前就已持久化嗎？Provider 對重複請求的承諾是什麼？Webhook 與主動查詢發生衝突時，誰擁有最後的狀態判定權？

團隊把答案和缺口畫回圖中，再設計兩個關鍵測試。第一個重送同一筆邏輯付款，確認沒有發生不允許的重複 Side Effect。第二個模擬 Provider 已處理付款、回應卻遺失，檢查 Checkout 是否保留 Unknown Outcome，並由可信 Readback 決定下一次 State Transition。

這些測試還需要實際執行與結果證據，不能僅憑白板認定系統安全。但它們已經讓團隊知道該觀察什麼：視覺化把可疑關係暴露出來，Contract 把懷疑化為可反駁的條件，Test 和 Readback 再把結果帶回共享模型。

Hohpe 將這種在結構化推理與視覺表徵之間切換的做法稱為 Left-Right Brain Ping-Pong。它適合作為工作隱喻，不意味著大腦真的依左右半球分別處理這些工程任務。

## 向主管解釋的是客戶風險，不是架構標籤

預算會議上，有人寫下「全面導入 Cloud-native Microservices，提升系統韌性」。主管問：「它避免了哪一種客戶損失？為什麼拆開就能避免？」

架構師改從付款結果不明說起。可能的傷害包括重複扣款、客服處置成本與訂單狀態錯誤。近期應先查明 Payment Attempt Identity、Unknown Outcome 的處置、模組責任與 Failure Tests。若之後獨立部署和故障隔離確實成為必要條件，再比較拆分的收益與新增的操作成本。

從底層 Retry、State Transition 說到客戶風險、交付時間與預算，是 Hohpe 的 Architect Elevator 所要連接的兩層對話。主管不必理解每條程式碼，仍可以追問技術選擇與商業結果之間缺了哪個因果環節。

架構師也不必為每個命名風格都爭取勝利。把影響力留給重複扣款、難以回復的部署變更和重大成本風險，往往比贏得所有 Code Review 更有價值。Hohpe 所談的 Political Capital，指的正是這種取捨，而不是架構師擁有代替原 Owner 核准上線的權力。

## 讓決策能被下一個人重新檢查

會議最後若選擇 Modular Monolith，Architecture Decision Record（ADR）不該只有結論。它還要留下：當時要解決的問題、觀察到的證據、排除其他方案的原因，以及哪些新事實會推翻這次選擇。

例如，日後若付款模組的工作負載需要獨立 Scale-out，或發版協調已成為可測量的瓶頸，就重新評估 Service Extraction。ADR 應連到對應的 Metrics、Provider Contract、Payment State Machine Tests 與責任邊界，不能只留下「微服務比較現代」這種會過期的判斷。

這些記錄讓後來接手的工程師有機會重走推理，而不必猜測前任架構師的想法。下次付款 Timeout 發生時，他們知道哪些狀態不能擅自推進、去哪裡找證據，也知道在什麼條件下值得重新拆分系統。

*來源：Gregor Hohpe 與 Patrick Akil 的 Beyond Coding 對談，涵蓋 Amplifier、Solution Space、Phantom Sketch Artist、Left-Right Brain Ping-Pong、Architect Elevator 與 Political Capital。結帳案例是假設情境，不是已記錄的客戶事故；本文描述的付款測試尚無執行結果。*
