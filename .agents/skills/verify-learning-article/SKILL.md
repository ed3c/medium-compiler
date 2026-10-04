---
name: verify-learning-article
description: 依 AI Engineering from Scratch 的已選學習路徑逐課研讀、實作並直接回答理論與實務問題，結合 medium-compiler 寫作與網站發布驗收。用於新增下一課文章、修訂課程文章或維護這條驗證流程。
---

# AI Engineering 學習文章：從原課到可驗證的網頁

以 [AI Engineering from Scratch 中文入口](https://aiengineeringfromscratch.com/?lang=zh)
為教材入口，以 [開發環境設定文章](../../../articles/application-engineering-colab.md)
及其 context / evidence 為完成方式的實例。沿用「逐章讀懂 → 實跑 → 解釋原因與結果 →
保存可用成果與重跑入口 → 編譯文章 → 驗證網站」，不複製第一課的工具清單、題數、
Colab 實驗或硬體結論到每一課。

文章發布與歷史綠燈不代表本機永久就緒。每課以 repository 的
[examples/](../../../examples/) 保存可取得的成果，並完成
[成果取得與 replay 契約](features/lesson-practice.md#成果取得與-replay-契約)。
使用者指定的 [examples 基準版本](https://github.com/ed3c/medium-compiler/tree/d71300ac12bd26857baf06799ddb4d5c7bd4427f/examples)
是既有實作參考，不是所有課都已支援完整 replay 的證明；新成果必須綁定自己的精確 ref。

目前網站實作的是 `software-engineering-fundamentals`；順序由
[已釘選的路線](../../../references/upstream/software-engineering-fundamentals.json) 決定。
`?lang=zh` 是顯示語言，不是學習路徑。保留使用者已選路線；若明確改選其他路線，先讀取
其 manifest 並處理網站現有的單一路線限制，不能默默換課或沿用錯誤導航。

讀 [features/README.md](features/README.md)，只載入本次需要的 recipe。新增一課通常依序
完成三項；「下一課」預設只前進一課，不自動撰寫整套課程。

## Zero context 的寫作要求

Zero context 的定義是：
> It must expose why each algorithm or design choice follows from the problem constraints and what actually happens at runtime.

作者須解釋每個演算法或設計選擇如何來自問題限制，並交代執行時實際發生什麼。
只讓文章不依賴聊天前文，仍不足以符合此要求。
依 [因果解釋與語意驗收](features/article-assembly.md#因果解釋與語意驗收) 撰寫與審視。
從原需求和證據推導接受、拒絕及未知條件。清楚的文字不能補足缺少的證據，
也不能把取捨直接標成主觀問題，再交回使用者決定。

## Launch

沿用 AGENTS.md 已選的 GitHub / Local route；取得本次精確 ref 的完整來源。
本機驗證使用 Python 3.10+、標準函式庫及專案既有 CLI，不需要 Vercel、Colab 或模型金鑰
才能開始研讀與編譯。課程本身的依賴另按原課與實際工作負載判定。

在選定 repository 根目錄建立全新的外部證據目錄，後續 shell 共用此實際路徑：

```sh
LESSON_RUN=$(python3 -c 'import pathlib,tempfile; print(pathlib.Path(tempfile.mkdtemp(prefix="learning-article.")).resolve())')
python3 .agents/skills/verify-medium/scripts/verify.py --feature doctor --out "$LESSON_RUN/doctor"
```

短命 CLI 每次執行完即結束；網站 build 與 server 的啟停由網站 recipe 說明。
不同執行不能共用寫作 run、build 輸出或 Colab session；已存在的使用者環境可讀取，
需要實作時使用隔離目錄，不在共享主 tree 切 branch。暫存目錄用於證據與破壞性反例；
交付可直接使用的本機能力時，另選使用者既有學習根目錄下的持久課程目錄，記錄真實路徑。
不要把本次暫存 venv 當成交付入口，也不要搬動已建立的 venv；在最終位置依 lock 重建。

## Doctor

上面的既有 doctor 必須成功。它只證明 CLI、skill 檔案與來源鎖定可用，並不證明課程
工具、Google 授權、瀏覽器、GitHub 寫入或部署可用。先查看所選課程的真實先決條件，
再探測必要工具；第一課的 beginner preflight 不是所有工具的驗收。
出現意外後重做對應檢查，連續同一問題最多三次嘗試，保留失敗並重新評估。

macOS 的 `/var`、`/tmp` 可能是符號連結，現有 source 防護會拒絕這種來源路徑。
使用上面 resolve 後的實體路徑；完整測試若受預設暫存路徑影響，可建立
`mkdir "$LESSON_RUN/tmp"`，以單次命令的 `TMPDIR="$LESSON_RUN/tmp"` 執行測試與
mechanical drive。不改防護或停用測試，也不全域修改使用者環境。

## Drive

1. [逐章研讀與實作](features/lesson-practice.md)：保存完整原課與所引用程式，從課程
   真正要求推導成功條件。直接尋找值得解釋的問題並給出答案、推理及實測證據；
   在 examples/<lesson>/ 交付成果使用與 replay 入口，實跑重建及既有環境重新驗收。
2. [寫作與編譯](features/article-assembly.md)：載入 `medium-writing`，新文章走既有
   Stage 0–7，既有文章用實際支援的修訂路徑，不能倒填虛構的寫作階段。完成後自動
   執行 recipe 的 `verify.py --feature learning-article --article <本篇>` 實際入口，
   核對本篇與 context 並保留無改動重編譯收據；既有 Ops drives 不能替代本篇驗收。
3. [導航與網站交付](features/website-delivery.md)：build、點擊前後課、核對文章雜湊，
   在現有授權範圍內提交與發布，最後讀回精確 commit 的 deployment 及公開頁面。

使用者要的是「代為實作、研究並寫出教學」時，記錄為 agent 操作與 source-explanation；
不等待附加考題答案，也不宣稱學員已掌握。若使用者另要求已接受的 learning-episode，
則遵循 medium-writing 的上游 handoff 與 preflight；缺少學員／learning-owner 資料時
保留該阻塞，不改 purpose 以繞過它。本站發布不等於發布到 Medium 平台。

## Evidence

證據保存在 `$LESSON_RUN`，不要放進讀者正文。記錄來源 ref / blob、已讀章節、要求與
結果對照、實際命令與 cwd / stdout / stderr / exit、修正前後、寫作 receipt、文章 SHA、
GitHub head / CI、deployment 身分與瀏覽器動作及結果。密鑰、token、私有使用者資料不入庫。
只把必要且可公開的範例、去敏證據與 context 放入文章 repository。

分別報告：原課要求覆蓋、指定實作結果、替代方法的有效範圍、編譯機械檢查、作者語意
審視、獨立審視、網站發布、成果材料可取得、本機當次可用、重建／replay 範圍、學員理解。
本機能力須附最近驗收時間與版本，不能承諾永久可用。沒有執行就寫未執行；舊證據標示其 ref / 日期，
不能重新標為本次執行。來源不完整或工具受阻時交付可確認部分及具體缺口，不能宣称全課完成。

## Cleanup

只停止本次啟動的 server / runtime，Colab 先下載並確認結果才停止，最後讀回 session。
清理本次 disposable 工作目錄前先保留證據；保留 `$LESSON_RUN`，確認輸出與 receipt
仍存在。保留已交付的持久環境、成果與使用入口；只清理自己的反例／暫存副本。
失敗也要清理自身資源；不停止他人的程序、不刪除使用者課程環境。

## Helpers

重用 `verify-medium/scripts/verify.py`、`medium_compiler.py`、`scripts/build_site.py`
及課程已有的程式。實際命令在 feature recipes 中；不新增學習進度 writer、發布器、
排程器或另一套驗證引擎。

## 維護此 skill

使用既有 [pstack maintenance](../verify-medium/references/maintain-verification.md)，
target 僅為本 skill 目錄：核對 index → 每 feature 一位唯讀 source reviewer → coordinator
逐項實跑 → 修正 drift 並重跑 → 保留證據。使用載體的原生 subagent，獨立上下文、明確
來源 ref、不同證據目錄；讀者不操作網站或寫檔。無此能力則明示 source-wave 阻塞。

維護不為了製造驗證而發布重複文章、推送練習分支、開 Colab 或重新部署。使用各 recipe
的保留文章／read-only drive；它不證明新的外部寫入。嚴格結果為 clean / changed / blocked，
未執行的必要 feature 不能算 clean。changed 只在此目錄提交一個已實跑修正的 PR；產品
缺陷另報，不改正文或產品程式來掩飾。建立標準見
[pstack creation](../verify-medium/references/create-verification.md)；`.cursor` 放置慣例在本 repo
適配為 `.agents`。這是工作方法，不自行授權部署或證明人的學習成效。
