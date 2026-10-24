# 最新兩篇文章的雙語網站交付

以下保留 `04cbab1` 網站接入輪的歷史範圍與觀察；後續使用者明確要求的收合目錄、
逐段註解與 speed-reading Owner 交付見[閱讀介面審查](reading-interface-review.md)。

使用者兩輪釐清均選 A：收錄 Container With Most Water 與 Course Schedule 的完整英繁稿；
加入首頁／Articles 列表、各語言標題目錄與切換；同步修正未來產文交付契約。
交付止於可部署產物、真實 browser、原 PR81／CI，不 merge、不部署。
沒有擴張成全站翻譯、CMS、ALG Four annotations 或所有 eval 文章自動發布。

## 第一個斷點及方法交互

新文章原本只存在 evals evidence，build_site.py 的 ARTICLES 是明確登錄的另一個集合。
因此完整 Markdown／Reader 結果不會自動變成網站路由與列表。
現有 english_source 只輸出英文 Markdown，並未生成英文 HTML。
Thinking Route 區分「可部署產物」與真正 Provider 發布，將文章集合、索引含義及授權終點交給使用者選擇。
Ambitious Route Depth／Range 借用明確 catalog handoff：同一組已審雙語正文及列表資料，
供既有 builder 生成可發現、可分享及可跳轉的頁面。
Thinking 的反例是掃描 evals 將未完成／失敗稿或私有 notes 一起曝光；
另一個反例是把可部署誤解為默許 merge 或發布。
所以保留明確 registry、選定文章、原責任與使用者明示的 effect boundary。
沒有新問題會改變範圍後退出往返，不再重問樣式等可由既有實作決定的細節。

本輪沿既有固定 Soodles Thinking／Ambitious source 與
[狀態機修改契約](state-machine-change.md) 手動套用方法，不宣稱原生 Skill invocation、
Loop admission 或新 Manager。review-writing 保留術語、actor、前提、因果及效果界線；
工程指引未跑文章 humanization，也不宣稱正式 STE compliance。

## 實際變更與原責任

[通用網站交付契約](bilingual-articles.md) 接入 leetcode-mental complete-article profile
及 medium-writing formatter。Content Owner 交付完整已審英繁稿、各語精確 H1、
短摘要與既有 source paths／slug；formatter 與網站 builder 只負責路由、列表、目錄及呈現。
沒有新增 compiler Stage、學習狀態或 publication authority。
既有文章可以原樣接入，不用重跑產文來虛構另一段核准歷史。

一個 fresh metadata consumer 實際讀取三份固定指引與四份完整正文，
產出兩筆 index entries 並記錄摘要依據與核准範圍。
父 Session 讀回後將同一資料加入 ARTICLES；四份 public article Markdown
與前輪凍結 final editions 逐 byte 相同。首稿、失敗與 Readers 留在原 eval evidence。
這不是新盲寫、正文語義重新驗收或 instruction-only improvement 實驗。

兩篇各有以下相對路由：

- /articles/leetcode-11-container-with-most-water/ 與其 en/。
- /articles/leetcode-207-course-schedule/ 與其 en/。

首頁與 /articles/ 提供兩語入口。每頁正確設定自己的 document language、
title／description；顯示該版 H2–H4 目錄、另一語頁面連結及原始 Markdown 下載。
重複 heading 仍有唯一錨點，code fence 中的 heading 不加入目錄。
語言切換回另一完整頁面，不宣稱 paragraph alignment 或等價 scroll position。
Desktop 目錄在右側，mobile 預設收起；header 實際高度決定 heading scroll margin。
Code 可在自己的區塊捲動，不讓整份文件橫向溢出。

既有 page helper 的預設語言／metadata 不變，新版呈現只對 bilingual=True entries 啟用。
四份頁面以外的語言呈現與 ALG Four projection 不改動。
新頁透過來源 paths、實際下載 bytes／code 比對及 Git revision 驗證；
沒有加額外 article/report SHA-256。既有部署 manifest 預設仍由原 build target 負責，
content/browser CI 使用 --no-deployment-manifest。

## 驗證與失敗

本機 full-site build 成功，使用完整網站 config 的 pinned Wrangler dry-run exit0，
僅 ASSETS binding；沒有發布 Worker、登入變更或 payment Sandbox 操作。
dry-run 不是 Provider URL 或 active version 驗收。

- 四個新 focused tests 通過：列表／雙語來源下載、重複／nested／fenced headings、
  缺少 metadata 及 private eval source 的診斷拒絕。
- 原 full-site transport 三個 tests 及 ALG Four 七個 tests 通過；
  source、七張圖、139 段／14 Active 的原資料沒有重綁。
- verify-medium doctor mechanical_pass 只表示來源／註冊檢查。
- 真實 Chromium 在 desktop 1440×900、mobile 390×844，驅動兩篇×兩語共八個頁面觀察。
  每個從首頁及 Articles 列表實際點入，核對 document language、完整 code blocks、
  TOC click／keyboard focus、heading 未被 header 遮擋、無 document overflow、
  語言切換與 exact Markdown downloads。JS page errors 為空。
  Desktop／mobile 截圖已實際查看代表樣本。

第一次 browser drive 是真實失敗：測試以 get_attribute("open") 得到空字串，
錯當成未開啟而關閉 mobile TOC，導致 click timeout。
其 screenshot error handler 又在 Playwright context 關閉後呼叫 screenshot，產生第二個錯誤。
保留初版 harness 與 result；修成讀取 details.open Boolean、在 context 關閉前擷取失敗圖。
第二次 drive 八個 observations PASS。沒有跳過測試、force click 或改正文。
[可重讀證據](../evals/writing/leetcode-web-delivery/README.md) 保留前後結果。

Schema2 的三個 action fields 實際 VALID／SUPPORTED／PASS，原 next
consume_verified_behavior 已由父 Session 消費。它只支持 metadata 交付回報；
workflow_decisions=null、authorizes_landing=false，與 browser／Provider 結果分開。
Native session IDs／captures 與 fixed instructions 在 external evidence，
fork_turns=none、共享 filesystem 及逐項 capture 限制不能證明強制讀取隔離。

External evidence:
/private/var/folders/l6/44bf7nvs64j60f1mpyy88hdm0000gn/T/leetcode-web-delivery-kihz_m16。
正常 matching-head CI 亦包含同一 browser drive，沒有模型生成或非必要 SHA-256 gate。
CI、local preview 與可部署 dist 都不代表正式 Cloudflare 網址已更新。
