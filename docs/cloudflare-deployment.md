# medium-compiler 的 Cloudflare 部署與負載成本

本次選擇 Workers Static Assets 承載公開網站，既有 Remote Sandbox 繼續使用
Access + Worker + Queues + 兩個 SQLite Durable Objects。帳號維持 Workers Free、
Zero Trust Free；不新增 R2、Containers、付費 Load Balancer 或 Workers Paid。
這是 US$0 約束下的實驗部署，不是持續大流量付款服務的容量承諾。

## 網站與付款系統分別計量

網站的 HTML、CSS、JS、Wasm、音檔與影片由 Static Assets 直接回傳。根目錄
`wrangler.jsonc` 只讓 `/api/*` 先進 Worker，避免每次閱讀網頁都消耗動態請求。
逐字稿搜尋 `/api/transcripts` 移到 Workers 原生 HTMLRewriter，保留七個節目、
URL allowlist、15 秒來源 timeout、8 MiB HTML 上限、固定短摘錄與來源 SHA-256。
第三方拒絕或格式改變時回傳 502，不宣稱找不到逐字稿或已驗證音訊。
網站 Worker 沒有 Queue／DO binding，也不代理 Remote Sandbox 的 Access 身分。

Cloudflare [Static Assets](https://developers.cloudflare.com/workers/static-assets/billing-and-limitations/)
的直接資產請求免費且不限次數；Free 每次部署上限 20,000 個檔案、每檔 25 MiB。
本次遷移前 build 為 149 個檔案、11,553,174 bytes，最大檔案 1,323,541 bytes。
不存在「移到 Cloudflare 後每筆付款也不限量」這項推論。

2026-10-11 核對的官方額度：

| 路徑 | Free 額度 | 實驗含義 |
| --- | --- | --- |
| [Worker 動態請求](https://developers.cloudflare.com/workers/platform/pricing/) | 100,000/day；10 ms CPU/invocation | API、Queue Consumer 等依平台計量，不是只計訪客 Create |
| [Queues](https://developers.cloudflare.com/queues/platform/pricing/) | 10,000 operations/day；24 小時保留 | 通常一則訊息至少 write/read/delete 三次；Retry／DLQ 額外消耗 |
| [SQLite DO compute](https://developers.cloudflare.com/durable-objects/platform/pricing/) | 100,000 requests/day；13,000 GB-s/day | 每個身分的一組 DO 仍有熱點；增加邊緣 Worker 不會分拆其帳本 |
| [SQLite DO storage](https://developers.cloudflare.com/durable-objects/platform/pricing/) | 5 million rows read/day；100,000 rows written/day；5 GB | 完整帳本輪詢會放大 rows read；不是「一筆 Order 一次 read」 |
| [Workers Builds](https://developers.cloudflare.com/workers/ci-cd/builds/limits-and-pricing/) | 3,000 build minutes/month | 本機 build/deploy 不消耗雲端 build minutes；Git integration 另有用量 |

在沒有其他使用者、Retry 或其他服務消耗時，10,000 / 3 約 3,333 是 Queue
訊息的理論每日上限，並非實測付款上限或安全測試預算。
100 intents/s × 300 s 已有 30,000 intents，最低約 90,000 Queue operations，
超過 Free。1,000/s × 600 s 最低約 1.8 million operations，也不符合 US$0。
Free 額度用盡時接受拒絕／服務中斷，不自動升級。Budget Alert 不能停止計費。

若 Owner 日後另行授權付費，Workers Paid 基本費目前為 US$5/month，超出包含額度
後 Worker requests 為 US$0.30/million、CPU 為 US$0.02/million ms；Queues 為
US$0.40/million operations。DO requests、duration、SQL、其他帳戶使用量另計。
這些單價只提供成本模型，沒有啟用 Paid，也不能據此保證高流量 SLO。

## 部署與來源

```sh
npm ci --ignore-scripts
npm run build
npm run test:site
npx wrangler deploy --dry-run
# Owner 先在指定帳號 Billing 讀回 Workers Free，才執行遠端部署。
npm run deploy -- --message 'Source <verified Git SHA>'
```

`npm run deploy` 重建原有 Python static site，然後使用 pinned Wrangler 4.149.0。
Public Worker 名稱為 `medium-compiler`，與 `checkout-reliability-sandbox` 分開。
原 `vercel.json` 保留作為回退路徑，不刪除 Vercel 專案；不在遷移中購買網域。
GitHub Actions 對 PR 執行原本的 Python／Node／mechanical drives，另加入本機
workerd 的網站 API controls。CI 不能代替遠端 Browser 或第三方來源驗收。
Workers Builds 只有真正完成 Git 連接後才算自動部署；一份 config 不構成連接證明。

`site/_headers` 隨 build 複製，保留 Lab 的 COOP same-origin／COEP require-corp。
原網站路由、Markdown downloads、notebook、provenance 與 ALG assets 原樣生成。
Static Assets 使用 auto-trailing-slash，未知 API 回傳 404，不回傳假成功的首頁。
持久化 Workers Logs 保持關閉；操作員用平台 Usage、有限的 Tail 與實驗 JSON
保存證據。這會限制歷史 Log 查詢，不把內部計數當成 Cloudflare 帳單。

## 驗收與獨立 Load Runner

新網址的 P0 需實際 Browser Create → Provider Commit + Lost Reply → Readback
PAID + 單一 Charge → Reload 保存狀態，並檢查錯金額拒絕、Export、Reset。
遷移到新 Origin 不會搬移舊 OPFS；舊 Vercel Lab 仍可回讀與匯出 evidence。
JSON evidence 是執行紀錄，並不是已實作的資料 Import／Restore。

`examples/cloudflare-site-load.js` 只對公開網站的固定靜態路由執行有界測試，
不查逐字稿第三方、不執行付款。它量測 CDN 的 requests/s、latency、errors 與
dropped iterations。Remote 付款使用既有 `examples/cloudflare-checkout-sandbox/load-bounded.js`，
需要 application-scoped Access JWT，保留原 Payment Key 與 unknown outcome readback。
不要將 Token 寫入檔案、Git 或回報。

```sh
# 200 個靜態請求 baseline；不能作為付款容量證據。
TEST_URL=https://medium-compiler.ga874199.workers.dev \
RUN_ID=site-baseline-unique EVIDENCE_FILE=/absolute/new/site-load.json \
k6 run examples/cloudflare-site-load.js
```

付款 baseline 仍是 1／2 arrivals/s × 4／8 s。先觀察 Accepted、PAID、
settlement p50/p95/p99、Error Rate、Dropped Iterations、Pending Age 與平台 Queue
Backlog，再選擇下一輪。完整 State 每個 VU 反覆輪詢及建立時重掃 Pending Outbox
是現有 Source 的工作量放大點；大幅加載前需依實測結果做單一因果修正。
負載測試不能移除 Idempotency、Unknown Effect Preservation 或 Access。
不同 DO partitions 的容量需在真實授權身分／隔離 workload 中另行驗證；本次不
冒用第二身分或把同一 Owner 的多個 Worker isolate 宣稱為獨立 partition。

PITR Bookmark 不等於 Restore。既有 DR 演練的版本與單一 RTO observation
維持其原範圍，不能因網站遷移而升格為新版本的 Disaster Recovery PASS。
