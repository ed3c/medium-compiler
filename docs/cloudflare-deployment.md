# medium-compiler 的 Cloudflare 部署與負載成本

本次使用者明確選用 Local Codex + pinned Wrangler，將完整網站部署至獨立的
`medium-compiler-full-site` Worker。新設定 `wrangler.full-site.jsonc` 使用完整 `dist/`；
既有 `medium-compiler` Worker 仍只承載 Reliability Lab，Vercel 保留為回退參考。
既有 Remote Sandbox 繼續使用 Access + Worker + Queues + 兩個 SQLite Durable Objects。
帳號維持 Workers Free、
Zero Trust Free；不新增 R2、Containers、付費 Load Balancer 或 Workers Paid。
這是 US$0 約束下的實驗部署，不是持續大流量付款服務的容量承諾。

| 方案 | 網站成本／限制 | 付款測試 | 選擇 |
| --- | --- | --- | --- |
| [Vercel Hobby](https://vercel.com/docs/plans/hobby) + Cloudflare Free | US$0；100 GB Fast Data Transfer、1 million CDN requests 的 included usage；限個人非商業用途 | 仍受 Cloudflare Queue／DO 額度 | 回退參考；本次不重新部署 |
| Workers Static Assets + Cloudflare Free | US$0；直接資產請求免費、不限次數；動態 API 另計 | 有界故障／恢復與 baseline | 新完整網站與既有獨立 Lab |
| Workers Static Assets + Workers Paid | 基本 US$5/month，加超額操作成本 | 可擴大 native load window，仍需處理熱 DO 與量測 SLO | 尚未獲授權，不啟用 |

只升級 Vercel 不能擴大 Cloudflare Queues 額度。若未來的要求是持續大流量付款，
最小付費升級候選在 Cloudflare dynamic runtime；公開靜態網站仍可維持免費。

## 網站與付款系統分別計量

完整網站包含文章、Learning、ALG Four、CEFR、逐字稿介面與 read-only API。
新 build 沿用 `scripts/build_site.py`，只將產出 HTML 中指向既有 Vercel 的
`href`／`src` 映射為同源路徑；Markdown、雙語 source blob、註解 manifest、七張圖與
下載檔案保持原始 bytes。完整目標不帶 Lab-only `_redirects`。
導覽仍直接開啟既有 Lab Origin，保留其 OPFS；完整網站也包含 `/reliability/`，
但新 Origin 的 OPFS 是獨立資料，並不搬移原狀態。
兩個公開網站 Worker 均沒有 Queue／DO binding，也不代理 Sandbox Access 身分。
`/api/transcripts` 共用既有 Worker handler，保留 search／inspect、限制及拒絕語義。
未知 API 回 JSON 404；未知網站路由不回首頁假成功。

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
npm run build:cloudflare:full
python3 -m unittest discover -s tests -p test_cloudflare_full_site.py -v
npm run test:site:full
npx --no-install wrangler deploy --dry-run --config wrangler.full-site.jsonc
# 在帳號、Workers Free、現有用量與匹配 HEAD 的 PR／CI／main 均讀回後：
npm run deploy:cloudflare:full -- --message 'Source <verified main SHA>'
npx --no-install wrangler deployments list --config wrangler.full-site.jsonc
# URL 必須採用 Wrangler／Provider 實際回傳，不自行猜測 canonical origin。
python3 scripts/verify_cloudflare_site.py --url <provider URL> --site dist --revision <main SHA> --out <external evidence.json>
python3 tests/browser_e2e_alg_four.py --url <provider URL> --out <external browser evidence directory>
```

`deployment.json` 保存 Git revision、dirty 狀態與公開產物 SHA-256。Runtime verifier
要求乾淨且 revision 相同的本機 build，再逐檔讀回 HTTP bytes、MIME、主要路由、
Lab isolation headers 與 API 拒絕。Manifest 不包含自身 digest，也不是 Provider version
證明；active version 仍由 Wrangler 另讀。部署前先確認 `git status --short` 為空。
文章／Browser CI 使用 `npm run build:cloudflare:full -- --no-deployment-manifest`，
不計算部署專用的全站資產 SHA-256。來源鎖定與 compiler receipt 保留原本實際消費的
完整性檢查；品質驗收檢查文章推導與實際 Reader 回答，不以 digest 數量代替。
本機正式部署仍使用預設 build，產生供遠端逐檔讀回使用的 manifest。
相容日沿用共用 API 的 `2026-10-11`：pinned Wrangler 4.149.0 的本機 workerd
最高支援 `2026-10-13`，不能將今天日期寫入後只用 dry-run 宣稱 runtime 可用。

`npm run deploy`／`wrangler.jsonc` 繼續只生成 `dist-cloudflare` 的 Lab assets。
本次不改既有 Workers Builds trigger、不連接新 Git 自動部署、不變更 Sandbox config。
PR CI 執行原 controls、新完整資產及 API controls、dry-run、Chromium desktop／mobile；
CI 不代替遠端部署或第三方逐字稿來源 readback。
`site/_headers` 保留 Lab COOP／COEP。持久化 Workers Logs 沿用關閉的成本策略；
平台 Usage、有限 Tail 與外部 evidence 保留觀察，不把內部計數當帳單。

回退只作用於新 Worker：先記錄 active version，再使用 pinned Wrangler 的 rollback
指令（以當前 `rollback --help` 為準）。首次部署若尚無可回退版本，讀者仍可使用既有
Vercel／Lab URL。不得以回退名義覆蓋 Lab、Sandbox、Queue、DO 或 Access Policy。

## 驗收與獨立 Load Runner

既有 Lab／付款系統的 P0 需實際 Browser Create → Provider Commit + Lost Reply → Readback
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
Backlog，再選擇下一輪。完整 State 每個 VU 反覆輪詢仍是 rows-read 放大點。Outbox 修正保存 Queue ACK，
Create 只送自己的 key；PENDING 不再等同於尚未 Publish。Unknown ACK 的恢复先
讀 Provider，再沿用原 key；lease 到期不代表舊 send 已終止，不能聲稱零重複訊息。
負載測試不能移除 Idempotency、Unknown Effect Preservation 或 Access。
不同 DO partitions 的容量需在真實授權身分／隔離 workload 中另行驗證；本次不
冒用第二身分或把同一 Owner 的多個 Worker isolate 宣稱為獨立 partition。

PITR Bookmark 不等於 Restore。既有 DR 演練的版本與單一 RTO observation
維持其原範圍，不能因網站遷移而升格為新版本的 Disaster Recovery PASS。

## Native Git 自動部署契約

官方 Cloudflare Workers and Pages GitHub App 只選 `ed3c/medium-compiler`。
兩個既有 Worker 都選 production `main`、repository root `/`、Preview builds 關閉。
Public Lab build command 為 `npm run build:cloudflare`，deploy 為 `npx wrangler deploy`。
Remote build command 為 `node --experimental-sqlite --test tests/cloudflare_interface.test.mjs`，
deploy 為 `npx wrangler deploy --config examples/cloudflare-checkout-sandbox/wrangler.jsonc`。
沿用既有 Queue、DO migration 和 Access Policy，不建立 preview bindings 或第二個 Scheduler。
沿用單一 `medium-compiler Git Builds` user token，限定目前帳號的 Workers Scripts
Edit、Queues Edit、Account Settings Read；不使用預設 R2／Containers 等廣泛權限。
Cloudflare 平台保存 build credential；不把 Token 值放入 Git、回報或聊天。

Local Codex 是配置 Owner；Workers Builds 是 Git 執行 Host。App Installed、Repo Connected、
Build Triggered、Build Succeeded、Deployment Active、Runtime Verified 要分別讀回。
Git connection 不證明已發布修正，部署成功不證明付款或 Restore 正確。
單次 Git build 不會把 medium compiler 的 VALIDATED 提升為 Runtime PASS；外部錯誤
不重設 article stages。來源變動後以 matching-head CI 與新版本 Runtime evidence 驗證。
