# 課程導航與真實網站交付

讀者從文章連到正確下一課，線上內容能追溯到已驗證的文章及部署 commit。

## Sub-features

- 導航：依已選路線排序；已發表下一篇連本站，未發表則明示並連原課，最後一課明示終點。
- 建置：沿用 repository build、靜態路徑、provenance 與原有測試。
- 本機預覽：每次文章更新先開啟 localhost 頁面，提供使用者檢視的網址與結果。
- 發布：僅限本次明確授權；辨識既有 Provider、scope、Git / commit / 環境並讀回公開頁面。
- 成果取得：文章的 examples 連結可公開讀取，實際程式／lock 與交付記錄的 ref 一致。

## How to get to it (user POV)

網站 `/learning/` → `/articles/application-engineering-colab/` →「下一課」。
文章清單在 `/articles/`；來源讀回在 `/provenance.json`。
遵循 [本機預覽先於發布](../../../../writing-contract.md#article-updates-local-preview-before-deployment)。
Provider 沿 AGENTS.md 的本次所選路線；歷史 Vercel Project `noodles8/medium-compiler`
及 `https://medium-compiler.vercel.app` 只作既有來源參考，不強制重選 Vercel。

## Driving it with the site builder, HTTP and Chrome

Preconditions: skill doctor 成功；具備當前文章/context、`scripts/build_site.py`、
路線 manifest、所選 Provider config、Ops snapshot 及 curriculum lock。要發布才需要現有 GitHub / Provider
權限；有 URL 或 Preview build 成功不等於 Production 已更新。

- **接入**：新課沿用 ARTICLES 項目的 source、slug、title、description、lesson、
  lesson_title、next_lesson_title。核對 lesson 存在於路線且不重複。每篇課程文章有下一課；
  非課程 overview 不硬塞課次。更新前一篇正文的下一课連結，避免與生成導航互相矛盾。
- **建置**：`python3 scripts/build_site.py --out "$LESSON_RUN/site"`，输出必須屬於本次
  執行（builder 會先刪除此輸出目錄）。執行既有 site 與 course navigation 測試，PR 前跑
  完整 unittest suite 及 verify-medium mechanical drives；不關閉失敗測試。
- **本機頁面**：

  ```sh
  python3 -u -m http.server 0 --bind 127.0.0.1 --directory "$LESSON_RUN/site" > "$LESSON_RUN/server.log" 2>&1 &
  LESSON_SERVER_PID=$!
  ```

  從 log 讀取實際分配的 port，HTTP 讀取 provenance 核對本次 source hashes 才開始使用。
  用可用瀏覽器開該 URL，實際點「下一課」、上一課，保存 URL / 可見標題 / 導航與截圖。
  若瀏覽器無法連本機，記錄限制，不把 HTTP 檢查宣稱為畫面驗收。
- **內容讀回**：检查 `/`、`/learning/`、`/experiments/`、`/articles/`、本次文章、相鄰
  課程及 `/provenance.json`。200 之外還核對可見標題、code、重要來源链接、navigation
  目的地與 article SHA256。provenance 的 Ops revision 要等於
  `references/ops-experiment-catalog.json.provider_revision`；curriculum revision 要等於
  `references/upstream/ai-engineering-skills-lock.json.revision`；
  不因更新教材就默默修改 Ops provider。沿用當前快照，不把範本或歷史實驗寫成本次執行。
- **成果連結**：由實際文章找 examples 入口，確認讀者可取得 README、必要程式、lock
  與輸入，核對交付收據的完整 Git SHA／hash，並確認文件有從該 ref 取得的步驟。
  連到 GitHub main 可以導覽，但不能證明重播的是本次成果。單純打開 repo 首頁不算
  取得成果驗收。本站目前不把 examples 複製成下載路由，不虛構 `/examples/` 網站功能。
  網站 200、deployment Ready 或 provenance 的文章 hash，只證明各自項目；
  本機持久能力與 replay 必須另消費 lesson-practice 的實跑結果。
- **本機交付**：提供以上實際開啟的 localhost URL、檢查結果與來源版本。沒有本次發布要求就
  停在此處；使用者要求先看再上線時等其檢視。Agent 開啟不代表使用者已看過。
- **授權發布**：本機預覽完成後，依本次授權建立／更新同一 PR，讀回當前 head、diff、CI。
  先查 Git push／merge 是否觸發 Vercel Preview 或 Workers Builds；不以遠端 Preview 取代本機。
  未知 trigger 時保留本機成果，不逕行推送。head 改變就檢查變更及其證據。
  沿 AGENTS.md 所選 Provider；Vercel 路線先查現有獨立 Project，避免重複建立或連到 Ops。
  Vercel provider readback 核對 Root Directory 為 repo 根目錄；`vercel.json` 核對
  `python3 scripts/build_site.py`、`dist`、cleanUrls。
  靜態站不複製資料庫、Google OAuth 或模型 secrets。維持使用者指定 Preview / Production；
  合併與 Production 需有本任務授權，skill 自己不授權。
- **上線驗收**：保存 Project ID、scope、repo、branch、精確 SHA、deployment ID、環境、
  狀態與 URL。正式域名可能已指向別的 commit，必須與 provider readback 及 provenance
  一起核對。重做上面的實際頁面與導航檢查；不要拿 main 部署驗收 PR head，也不要拿
  Preview 當 Production。受登入保護的頁面不得宣稱匿名公開可讀。
- **維護 live drive**：以目前文章 build、本機 HTTP/瀏覽器點擊、正式站唯讀驗收即可；
  不為維護製造新 deployment。明示「既有部署讀回」，不宣稱演練了新的 provider 寫入。
- **清理**：`kill "$LESSON_SERVER_PID"` 並 `wait "$LESSON_SERVER_PID"` 回收本次 server；
  保留 log、site/provenance、HTTP 與瀏覽器證據，確認其仍在 `$LESSON_RUN`。不要用程序名稱
  殺 server，也不要在此流程刪 Project 或停止他人的服務。

## Gotchas

当前 builder 只支援已釘選的 Software Engineering Fundamentals route；新路線是另一次
明確產品修改，不是改 URL 的 lang 就完成。Git 後一課是 Python Environments，不能因
資料夾編號把 GPU 當下一課。部署 ID 或舊綠燈不證明本次文章；比對內容、commit 與時間。
網站發布成功不證明學員理解，也不會補齊沒有執行的原課要求。
