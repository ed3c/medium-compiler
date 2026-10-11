# 一場促銷揭露了付款系統的未知狀態：從故障實驗學會可靠的分散式系統

[上一篇文章](https://medium-compiler.vercel.app/articles/architect-amplifier-payment-decisions/)中，結帳團隊暫時放下 Monolith 與 Microservices 的爭論，先檢查付款狀態。現在假設促銷只剩六週。產品經理希望更快發版，營運人員希望結帳失敗減少，財務部門則想知道：為什麼有些顧客明明被扣款，訂單卻沒有完成？

工程師很快就能寫出一個新的 API。真正困難的是：顧客重新整理頁面、Worker 重啟、網路弄丟回覆，或行銷活動帶來超出平常的請求量時，哪些事情絕對不能改變？

團隊決定先建立一個付款故障實驗，再考慮調整正式系統。實驗使用開源 Python 程式、獨立的模擬金流帳本，不需要 API Key，也不會扣到真實款項。本機測試可以檢查指定的 State Machine 性質，但無法據此保證正式金流整合正確，也不能證明叢集能承受某個 Requests per Second（RPS）。

## 先確認商業損失，再畫系統架構

產品經理問，能不能在星期五前部署新的 Checkout Service。財務部門提出另一個問題：付款已成功、訂單卻還是 Pending，會造成多少客服案件和人工對帳？有人提議增加 Worker。這或許能縮短佇列等待時間，卻不能修好有缺陷的 Retry 協定。

團隊先用所有人都能理解的文字寫下承諾：同一位顧客的一次購買，不應因為系統 Retry 變成兩次扣款；已扣款的購買，必須保有可找回的訂單身分；系統不能因為「請求已送出」便聲稱「付款已完成」。

這些承諾要轉成可驗證的 **Invariants（不變量）**，而不是某個 Framework 的名字。

- Identity：同一筆邏輯付款，在 Provider 定義的適用範圍和保留期限內使用穩定的 `Idempotency-Key`。相同 Key 若搭配不同金額，必須拒絕。
- No invented success：網路 `Timeout` 代表 `UNKNOWN`，不等於 `FAILED`，也不等於 `PAID`。只有可信的 Provider Evidence 能確定外部付款效果。
- No lost intent：Order 和待處理的 `Outbox` Event 必須在同一筆本地 Database Transaction 中寫入。提交後即使程序崩潰，待處理工作也不能消失。
- Safe redelivery：Event 重送或 Worker 重啟，不應造成第二筆邏輯扣款。這項保證依賴 Provider 的 Idempotency Contract 或可信 Readback。
- Recovery：未完成的工作必須能被找到，維運人員不需要猜測外部操作是否發生，就能接續對帳。

「Exactly Once」在這裡有兩個完全不同的意思。Database 的 `UNIQUE` Constraint 可以讓同一個 Request Key 只建立一筆本地 Order；卻無法單靠這個 Constraint 保證另一家金流 Provider 只執行一次外部扣款。後者需要 Provider 端相容的身分契約，以及發生模糊結果後可查詢的 Readback。兩項都不存在，就不能承諾外部付款 Exactly Once。

## 兩次 Commit 之間，可能剛好發生故障

顧客送出訂單時，Checkout 在同一筆交易中保存 Order 與 Pending Outbox Event。Worker 之後才向 Payment Provider 發出扣款請求，而 Provider 有自己的 Transaction。這不是一筆橫跨兩個資料庫的 ACID Transaction；兩邊無法直接一起 Rollback。

```text
Customer → Checkout DB [Order + Outbox]  COMMIT A
                            │
                            ▼
                        Worker
                            │  stable Idempotency-Key
                            ▼
                Mock Provider Ledger       COMMIT B
                            │
                    reply or lost reply
                            ▼
            Checkout reads provider evidence
                            │
                     PAID / PENDING
```

Worker 可能在 `COMMIT B` 後、尚未把結果寫回 Checkout 前就停止。此時 Order 還是 `PENDING`，但 Provider 已經記錄扣款。如果把 Pending 當成付款失敗，Retry 又重新產生 Key，顧客就可能再被扣一次。

**Transactional Outbox** 解決的是比較窄的問題：確保本地 Order 和待發事件的意圖在 `COMMIT A` 同時保存。它不會讓後續的 Provider 扣款與 `COMMIT A` 變成同一筆原子交易。Outbox Relay 若在 Publish 成功後遺失確認訊息，可能再次 Publish 同一個 Event；Consumer 必須能安全處理 Redelivery。RabbitMQ 的 Reliability 文件也明確指出 Consumer 故障後可能重送，而 Publisher 恢復時可能出現重複訊息。

比較可靠的 Worker 會先用穩定的邏輯付款 Key 查詢 Provider 既有結果。若確實沒有外部效果，才用**同一個 Key**要求付款；回覆若遺失，就保留未知並重新查詢。只有 Provider 記錄的扣款金額及幣別與原訂單一致，才能將 Order 標記為 `PAID`。Unknown 並不是可以省略的錯誤狀態，它讓系統不必在證據不足時做出不可逆的猜測。

## 先用最小實驗重現故障

配套的 [Checkout Reliability Lab 開源程式](https://github.com/ed3c/medium-compiler/tree/main/examples/checkout-reliability-lab) 只依賴 Python Standard Library。兩個 SQLite 檔案分別模擬 Checkout 與 Provider 的持久化帳本。`checkout_lab.py` 實作 Order、Outbox、模擬扣款、Readback 和受限制的 State Transition；`test_checkout_lab.py` 注入回覆遺失、重複請求和 Worker Crash。實驗不儲存信用卡資訊，也不連接真實付款機構。

```bash
git clone https://github.com/ed3c/medium-compiler.git
cd medium-compiler/examples/checkout-reliability-lab
python3 -m unittest discover -v
```

第一階段不需要帳號、金流 API Key 或 Docker。但測試通過只代表以下幾種指定情境成立，不代表涵蓋完整金流業務。

**重複結帳請求。** 60 個並行呼叫使用相同的 Business Key。Order Table 的 `UNIQUE` Constraint 與 Transaction 讓建立工作序列化，預期只得到一筆 Order 和一筆 Outbox Event。若相同 Key 換成另一個金額，則必須回報 Conflict，而不是假裝第二筆需求成功。

**Provider 已扣款，回覆卻遺失。** 模擬 Provider 先把 Charge 寫入自己的 Ledger，再丟出 `LostReply`。Checkout 仍然是 `PENDING`，Provider Ledger 卻已有一筆 Charge。重新處理時，Worker 透過 Readback 取得原本的 Charge，再將 Order 變成 `PAID`，不得新增第二筆 Charge。這個實驗的反例是 Retry 擅自換新 Key：那代表不同的外部操作，不能拿來當同一筆購買的重試策略。

**Worker 停在兩個效果之間。** Provider Commit 已完成，Checkout State Commit 尚未完成時注入 Crash，Outbox Event 仍然 Pending。下一次處理讀回原本的 Provider Charge，再完成本地 Order State。

**兩個 Worker 同時執行。** 兩個本地 Worker Attempt 可能都看到尚未完成的付款；模擬 Provider Ledger 的 Unique Key 確保只有一筆 Charge。這驗證的是實驗內指定的 Constraint，不表示所有真實金流 Provider 都提供相同語意。

可以親自重現一次「已扣款但失去回覆」：

```bash
python3 checkout_lab.py --data .demo create cart-42 1250
# Copy order_id from the JSON response.
python3 checkout_lab.py --data .demo process ORDER_ID --lost-reply
python3 checkout_lab.py --data .demo counts
python3 checkout_lab.py --data .demo process ORDER_ID
python3 checkout_lab.py --data .demo counts
```

第一次 `process` 在 Provider Commit 之後回傳非零 Exit Code。第一份 Counts 應出現一筆 Provider Charge、一筆 Pending Event、零筆 Paid Order；第二次 `process` 才透過 Reconciliation 完成本地狀態，並將 Pending Event 消耗掉。這條可追蹤的狀態轉移，比只證明 Happy Path 回傳 `200 OK` 更能解釋系統是否可靠。

## 正確性和大流量，是兩種不同的測量

付款邏輯能容忍重送，不代表能承受促銷流量。**Correctness** 檢查同一筆邏輯操作重試後，Invariants 是否保持成立；**Capacity** 則觀察需求提高時，Throughput、Latency 和 Error Rate 如何改變。Correctness Test 全綠不能直接推導出 Capacity。

實驗另有一個只綁定 Loopback 的 HTTP Adapter，可以拿來練習負載測試：

```bash
python3 http_api.py --data .load --port 8080
# In another terminal, with Grafana k6 installed:
k6 run -e RUN_ID=campaign-a load.js
```

隨附的 k6 腳本將 Target 設定為**每秒 20 次 Arrival、持續 20 秒**。這只是設定值，不是測到的處理能力。腳本檢查 HTTP Status 和 Order ID，並設定 `http_req_failed < 1%`、`p95 < 500 ms`、`dropped_iterations == 0` 等 Threshold。重跑時使用新的 `RUN_ID`，避免把新的購買和既有 Request Key 混為一談。如果測試失敗，就保存原始結果，判斷瓶頸是 CPU、SQLite Write Contention、I/O，還是 Load Generator；不要只是刪掉 Threshold 讓結果變綠。

一般負載測試用不同 Key 建立新訂單；另做一輪多個 Caller 刻意重用**同一個** Key 的 Burst。兩個測試在回答不同問題：前者量測寫入容量，後者確認 Duplicate Suppression。需要保留實際 RPS、p50／p95／p99、Error Rate、Dropped Iterations、Pending Outbox Age、Conflict 數量，以及尚未完成對帳的付款數量。

這個 HTTP Adapter 沒有 Authentication，只監聽 `127.0.0.1`，不能公開部署。SQLite 足以支援這個局部實驗，卻不是正式 PostgreSQL、Replication、Broker、Provider Rate Limit 或分散式容錯的替代品。本次已執行 Python 測試；Docker-based 元件與 k6 的實際 Load Run 仍屬下一階段，必須以執行環境的原始結果為準。

## 換成 PostgreSQL、RabbitMQ 和多個 Replica 後，難題在哪裡？

下一個實驗要把雙 SQLite 模擬替換成真實 Service Boundary。PostgreSQL 在同一筆 Transaction 中保存 Orders 與 Outbox Events。Outbox Relay Polling 待處理資料，例如使用 `SELECT ... FOR UPDATE SKIP LOCKED`，再 Publish 到 RabbitMQ。Consumer 只有在安全處理訊息後才 Acknowledge。每個 Event 都攜帶穩定的 Order ID、Event ID，不在重新投遞時產生新的 Payment Key。

這時需要進一步注入跨程序故障。API 在 DB Commit 後崩潰，Outbox 必須留下；RabbitMQ 停止時仍有新訂單，Pending Events 應累積，恢復後可安全排空；Relay 在 Publish 後、記錄 Sent Marker 前崩潰，重複事件不能造成第二次扣款；Consumer 在 Provider 已完成付款後被殺掉，必須靠 Readback 恢復 Order；Provider Idempotency Window 過期，也不能繼續假設同 Key 永遠受到保護。若從 Backup 還原 PostgreSQL，重新開放寫入之前還需要對照 Provider Evidence 做 Reconciliation。

真正分散後，多了成本與新故障面。PostgreSQL 的 Row Lock、Index、Isolation Level 與 Connection Pool 都可能成為 Contention；RabbitMQ 帶來 Publisher Confirms、Consumer Acknowledgement 和 Queue Backpressure；Outbox Relay 需要監控。HTTP API 即使一直回傳 `202 Accepted`，Broker 的 Pending Age 仍可能持續增加。若瓶頸在下游 Provider 或共用資料庫，增加 Worker 未必提高實際完成率。

可用已有實作的開源 Repository 做比較，但不能把別人的 README 當成自己的測試結果：[Microsoft eShop](https://github.com/dotnet/eShop)（MIT）展示多服務電商架構；[Temporal Python Samples](https://github.com/temporalio/samples-python)（MIT）提供 Durable Workflow 與 Retry 實例；[PostgreSQL 官方文件](https://www.postgresql.org/docs/current/transaction-iso.html) 解釋 Transaction Isolation；[RabbitMQ Reliability](https://www.rabbitmq.com/docs/reliability) 解釋訊息傳遞語意；[Grafana k6](https://grafana.com/docs/k6/latest/using-k6/thresholds/) 提供 Load Test Threshold 做法。k6 Repository 採 AGPL-3.0，本實驗只呼叫外部 CLI，沒有複製其原始碼；實際重用各專案程式時應核對各自 License。

第二階段真正的完成條件，不是「Docker Compose 能啟動」，而是能重播一筆故障的完整證據：確切輸入、Source Revision、注入位置、Provider 端 Side Effect 數量、恢復後的 Order State、Broker Backlog，以及觀察到的 Load Metrics。目前尚未宣稱這些跨 Service 實驗已經執行。

## 讓 Product 與 Finance 聽懂工程選擇

AI 可以讓團隊更快完成 Endpoint。但 Finance 要負擔退款或人工調帳，客服需要找回消失的訂單，Operations 在 Backlog 增加時必須處理警報。工程師應提出的是：哪個技術改動能降低這些成本，卻不引入更大的故障面？

假設有人提出「把 Payment 拆成五個 Microservices」。另一個提案可以是：「先持久化 Payment Identity、建立 Reconciliation，量測重複扣款與 Pending Age。如果 Release Coupling 或 Independent Scaling 仍是有證據的限制，再考慮 Service Extraction。」這是一個以商業結果檢驗技術方案的討論，而不是單純反對新架構。

團隊可以把需要的數據留在一份決策紀錄中：

```text
Monthly investigation cost = incidents × support minutes × cost per minute
Potential business benefit = avoidable losses + recovered customer value
Engineering cost           = build + infrastructure + on-call + tests
Decision                   = compare benefit, risk, and cost on the same scope
```

在事故數量、工時與受影響顧客尚未測量前，任何精確的 ROI 百分比都只是猜測。API 即使更快，如果人工對帳工作倍增，整體商業結果仍可能變差。反過來說，一項優雅但昂貴的 Migration，若錯過促銷時程又沒有降低風險，也不必然值得做。

這場會議可能要和新加坡、曼谷或其他地區的同事一起開。英文能力在這裡不只是讀技術文件，而是讓工程師能直接參與跨國商業決策，向對方說明風險、未知證據、可選方案和下一個測試。實際可以這樣表達：

> We have confirmed that a lost payment reply can leave an order pending while the mock provider has recorded a charge. We have not tested that failure against the production provider. Before we scale the workers, we need to verify the provider's idempotency window and readback API. I recommend a scoped failure test and an alert for unresolved payments older than our agreed recovery target.

這段英文沒有把本機測試包裝成正式 Provider 的執行證據。Product 能知道現在可以決定什麼，Finance 能看到尚未解決的風險，Operations 也知道需要觀測的訊號。面試時同樣可以從商業目標開始，說明一個 Invariant、追蹤一條失敗路徑、展示測試與結果，最後交代證據目前尚不能支持哪些結論。

## 下一次促銷來臨前，怎樣才算準備好？

七項本機測試成功，離正式 Production Readiness 還有距離。團隊仍須取得真實 Provider Contract，完成付款狀態 Reconciliation、Backup Restore、Recovery Point Objective（RPO）、Recovery Time Objective（RTO）、Alerting、Operational Ownership，並在量測過的 Peak Traffic 下驗收。這些不能靠 Python Unit Tests 或單台電腦上的負載測試自動證明。

練習可以依序進行：重送同一筆請求、模擬扣款成功但回覆遺失、在 Worker Crash 後恢復、驗證本地 Outbox 的 Atomic Intent、加入 Broker 觀察重複訊息、施加 Load 追蹤 Pending Age、還原 Backup，再用英文向真正負責商業決策的人解釋風險。每一步都有可保存的實際 Artifact，也清楚顯示還沒被證明的部分。

能把需求寫成 Code 的工程師，仍然是團隊需要的人。若還能清楚說明系統承受哪些故障、哪些風險仍未處理，以及每條技術邊界保護了哪項商業承諾，就有能力參與更大的決策，而不必靠猜測。
