# Final-body author review: first-delivery observations

固定方法：`589ee4332275f2d6042f1039331e12a33f0f9b56`。
完整因果分析、Soodles 契約套用及結果界線見
[review](../../../docs/leetcode-final-body-review.md)。
這是兩個 Native Local Codex 盲寫實例，沒有 instruction-only gain、一般可靠率或 human-learning 結論。

## 正文與原始回覆

- Daily Temperatures：[English](temperatures/article.en.md)、
  [繁中](temperatures/article.zh-TW.md)、
  [English first](temperatures/article.first.en.md)、
  [繁中 first](temperatures/article.first.zh-TW.md)、
  [author review](temperatures/report.md)、
  [fresh Reader raw](temperatures/reader.raw.json)。
- Subsets：[English](subsets/article.en.md)、
  [繁中](subsets/article.zh-TW.md)、
  [English first](subsets/article.first.en.md)、
  [繁中 first](subsets/article.first.zh-TW.md)、
  [author revisions](subsets/author-revisions.md)、
  [English review](subsets/english-review.md)、
  [translation review](subsets/translation-review.md)、
  [fresh Reader raw](subsets/reader.raw.json)。

兩篇都是完整文章，不是解法大綱。沒有範文或解法提示交給 Writer。
先凍結兩份作者首次交付，才啟動 Readers；之後沒有正文修訂、抽新題或回傳修補提示。
作者內部修訂不是 fresh Reader feedback，first complete drafts 與完成交付都保存。
Subsets 的 [已審英文中間版本](subsets/article.before-translation-repair.en.md)
保留翻譯對照發現的錯誤術語；重新審核英文後才修改最終繁中。

兩位 Reader 均保留 `cost` 缺項。其他七個問題未標缺失，並未回報實質英繁不一致；
這不是品質分數，不能稱為完整 Zero Context 通過。
Daily Temperatures 的幾何容量級數缺少從讀者前提開始的推導；
Subsets 的 append-only 分攤沒有橋接到 shared path 的 append/pop 交錯。
Owner 對 Reader 其他 primitive-cost 意見的較窄判讀，見 review；原始回答未修改。

## 控制、可重播部分與失敗

[固定 Reader 問題](reader-questions.json) 與前輪相同；
[selection](selection.md)、[session manifest](session-manifest.json) 記錄選題、角色與限制。
[quote-check](quote-check.json) 記錄 115 段 exact quotes，沒有另補引文；
[quote-audit](quote-audit.json) 為空。
Readers 的 `missing` 是保留證據，不是 CI 必須消滅的紅燈。

[獨立 runtime](runtime-independent.json) 由正文五段程式實際執行：
3,285 + 3,288 + 330 + 330 + 1,647 = 8,880 comparisons。
[runtime_controls.py](runtime_controls.py) 可直接重播，及由既有
`tests/test_final_method_holdout.py` 同時檢查前輪與本輪。
Python tests 不產文、不做語義判分、不計算 SHA-256。
這個 replay 不代替 fresh Reader、來源真偽或題型泛化驗證。
[bilingual-mechanical](bilingual-mechanical.json) 也只比較可確定的 blocks／links／recall。

各作者目錄保留自己的 task、output、report、抽出程式、verify、stdout／stderr、
刻意錯解、AssertionError、detector 結果及修訂記錄。
author-edits 是 observer 的零 context diff。Daily Temperatures 作者原始
author-revisions.en.diff.gz／author-revisions.zh-TW.diff.gz 保存原 bytes：
原 diff 的空白 context 被 git diff --check 判為 trailing whitespace，故只用 gzip 封裝；
沒有刪改原文或原 diff。
無意外的正解 runtime failure；deliberate wrong examples 不算自然失敗。
實際來源／讀取失敗、修復與 bilingual mechanical false 均保留在作者 notes／external native captures。

[cost-control](cost-control/output.json) 是獨立 fresh Reader 的 planted deletion control：
英繁各刪掉一個成本模型段落，保留程式及成本結論。
[預先保存的 transformation／expected](cost-control-private.json) 未提供給該 Reader。
它也標記 `cost` 缺項；這是敏感性觀察，不是新自然 Writer 樣本或 evaluator calibration。

## Schema 與外部 capture

[feedback](feedback/observed.json) 只涵蓋五個 reported-action fields；
VALID／SUPPORTED／10 fields PASS 不代表文章完整、所有 workflow decisions 已觀察或批准發布。
[原 criteria](feedback/criteria-review.first.json)、[實際拒絕](feedback/criteria-refusal.json)、
[修正說明](feedback/criteria-correction.md)、
[修正 criteria](feedback/criteria-review.corrected.json) 及
[消費原 next](feedback/consumed.json) 均保留。
工具本身產生的來源綁定 SHA 屬該次本機回饋；CI 沒有重新計算或新增 digest gate。

external evidence 路徑在 session manifest。固定 instructions、原始工具 responses、
native captures、source files 及完整 failure/readback 留在該路徑。
repo 的檔案是可重播投影，不冒充完整原生 trace。
capture 有逐項長度上限、filesystem 未強制讀取隔離；child self-report 與 observer capture 分開。
沒有 CLI Stage admission、publication、merge、Cloudflare／Vercel 或 Sandbox effect。
