# 公開 Snapshot 與 artifact 讀回：OMM 架構候選

此候選解釋 medium-compiler 如何產生公開圖套件，以及 Panorama 如何讀取其中的文字。
分析來源固定在 `5994e2b998f8baabf998c9a07e12211907ec67d3`。
這是八個來源檔的靜態分析，沒有涵蓋完整 repository。
Registry 保持 `candidate`，`review_receipt=null`。

## 為何選這個範圍

第一份架構候選必須連到實際 Consumer，也必須區分資料與執行權限。
這條路徑包含 Python Publisher、TanStack route、保留原碼的 Noodle renderer，以及 Browser reader。
直接畫出 callback 與檔案存取已足夠；此分析沒有新增 runtime adapter 或 Graph Owner。

圖檔是 [public-artifact.mmd](public-artifact.mmd)。
[來源索引](public-artifact-sources.json) 保存每個檔案的 Git blob、SHA-256 與 bytes。
箭頭表示其標籤指名的呼叫、callback 綁定或檔案存取。
箭頭不是已觀察的 Native handoff。

## 原碼中的路徑

下列連結均固定在同一來源版本。

| Producer → Consumer | 原碼依據與限制 |
| --- | --- |
| `loop_site` → `loop_graph_site` | [validate_snapshot:105](https://github.com/ed3c/medium-compiler/blob/5994e2b998f8baabf998c9a07e12211907ec67d3/scripts/loop_site.py#L105) 驗證 v2 公開圖；[render_loops:185](https://github.com/ed3c/medium-compiler/blob/5994e2b998f8baabf998c9a07e12211907ec67d3/scripts/loop_site.py#L185) 建置套件。兩者是不同階段，不是圖上一次原子轉移。 |
| `loop_graph_site` → 靜態套件 | [build_graph_package:55](https://github.com/ed3c/medium-compiler/blob/5994e2b998f8baabf998c9a07e12211907ec67d3/scripts/loop_graph_site.py#L55) 複製 graph，移除 `public_content`，寫入獨立文字檔，再寫出含 `content_urls` 的 `graph.json`。公開審查不是這個建置函式自行作出的判斷。 |
| Panorama route → 靜態套件 | [route:38](https://github.com/ed3c/medium-compiler/blob/5994e2b998f8baabf998c9a07e12211907ec67d3/apps/loop-workbench/src/routes/panorama.tsx#L38) 經 `safeManifest` 後 fetch JSON，再檢查 Graph v2 shape。此路徑沒有重新計算整份 `graph.json` 的 SHA-256。 |
| Panorama route → `mountPanorama` | [route:58](https://github.com/ed3c/medium-compiler/blob/5994e2b998f8baabf998c9a07e12211907ec67d3/apps/loop-workbench/src/routes/panorama.tsx#L58) 傳入 graph 與 `readArtifact` callback；callback 在 route:64 呼叫 `readReviewedArtifact`。 |
| `mountPanorama` → `mountIsometric` | [renderer:310](https://github.com/ed3c/medium-compiler/blob/5994e2b998f8baabf998c9a07e12211907ec67d3/apps/loop-workbench/vendor/noodle/loop-panorama.mjs#L310) 傳遞同一 callback。Panorama 模組沒有直接匯入或呼叫 `readReviewedArtifact`。 |
| Isometric → artifact reader | [principle 讀回:573](https://github.com/ed3c/medium-compiler/blob/5994e2b998f8baabf998c9a07e12211907ec67d3/apps/loop-workbench/vendor/noodle/loop-isometric.mjs#L573) 與[本次原要求:1489](https://github.com/ed3c/medium-compiler/blob/5994e2b998f8baabf998c9a07e12211907ec67d3/apps/loop-workbench/vendor/noodle/loop-isometric.mjs#L1489) 使用 `readArtifact`。一般原始來源按鈕走 `onSelect`；不能把所有來源選取都解讀為 fetch。 |
| Artifact reader → 靜態文字檔 | [reader:34](https://github.com/ed3c/medium-compiler/blob/5994e2b998f8baabf998c9a07e12211907ec67d3/apps/loop-workbench/src/public-artifact.mjs#L34) 先核對引用，再 fetch 綁定路徑，拒絕 redirect，核對 bytes、SHA-256，最後使用 fatal UTF-8 decode。 |

## 接受、拒絕與未知

`reviewedArtifactRef` 要求同源 manifest 路徑、相符的 snapshot identity、唯一 artifact、`available` 狀態，以及精確的 `content_urls`。
它拒絕原始 inline content、不可公開狀態、過大的宣告 bytes 與未綁定 URL。
讀回函式在 HTTP、bytes、digest 或 UTF-8 不符時拋出錯誤。
Isometric 會保存部分讀回錯誤並顯示失敗；圖沒有宣稱錯誤會變成已驗證文字。

來源命名中的 reviewed 不證明這次真的完成內容公開審查。
路徑與摘要相符也不證明原 Native event、Agent 行為或完整 Goal 已驗收。
這些狀態仍須各自原 Owner 的證據。

## 方法與觀察

本次使用原 `omm-scan` Skill 的 perspective／leaf 流程。
CLI 從 lock 所列 OMM revision `38ccdb69298adec949177c92c88d6e3ddfb5bab7` 建置，僅在任務暫存目錄執行。
先讀取 Python AST 和 TypeScript AST，再讀取呼叫位置與相關分支。
TypeScript parser 為 OMM 工具依賴中的 `5.9.3`；這只是語法分析，不是 TS7 編譯器等價測試。
Session 完成來源判讀；CLI 的 `write` 保存 7 個節點與 7 條關係，`validate` 檢查圖形慣例。
CLI 沒有自主理解原碼，也沒有執行另一個 Native Agent。

獨立來源 reviewer 核對了八個檔案綁定與七條關係。
初稿把 callback 觸發寫成一般「選取來源」；reviewer 指出實際分支更窄。
候選已改成 mechanism principle／本次原要求讀回。
負向對照把 callback forwarding 改成 Panorama 直接呼叫 reader；原碼不支持這個版本，應拒絕。
這份審查是靜態語義審查，沒有批准 Registry promotion、文章發布或 Production。

## Loss report 與後續邊界

- 圖省略版面、快取、comparison consumer 與其他 UI 分支。
- 圖沒有完整展開 Python Graph validator；來源索引保留該依賴。
- Registry checker 綁定來源索引本身；索引中的八個原檔仍需逐一比對。
- 沒有完整 repository OMM 掃描、獨立 Browser 視覺驗收、Native Soodles／Noodle Acceptance 或人類理解實驗。
- 候選先供原 Owner 審查；此結果不授權 merge、Cloud Push 或部署。
