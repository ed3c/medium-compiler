# Cost-inference review: two blind first deliveries

固定方法：`1487e11f5347806ca4a1e218f0a1d61bb6c8e34e`。
[完整原因、方法交互與判讀](../../../docs/leetcode-cost-inference-review.md)。
這是 Native Local Codex 的兩個新題型實例，不是 matched A/B、一般可靠率或 human-learning study。

## 完整正文、首稿與 raw answers

- Container With Most Water：[English](container/article.en.md)／[繁中](container/article.zh-TW.md)；
  [English first](container/article.first.en.md)／[繁中 first](container/article.first.zh-TW.md)；
  [author reconstruction](container/english-review.md)／[translation review](container/translation-review.md)；
  [Reader raw](container/reader.raw.json)。
- Course Schedule：[English](courses/article.en.md)／[繁中](courses/article.zh-TW.md)；
  [English first](courses/article.first.en.md)／[繁中 first](courses/article.first.zh-TW.md)；
  [author report](courses/report.md)／[Reader raw](courses/reader.raw.json)。

Writer 沒有範文、editorial、解法大綱、舊失敗、Reader 問題或另一位 Writer 輸出。
兩份完成交付先 [freeze](freeze.json)，才啟動 fresh Readers。
[八個原問題](reader-questions.json) 不變。
兩位 Reader 均未標缺項或實質英繁 mismatch；原始 limits 亦保留，
包括 Course 替代法沒有直接寫出 done 初始 Boolean 值。
Owner 對此及前向分攤直觀的較窄判讀見 report，沒有重寫 Reader 或修補凍結正文。

## 所有修訂、失敗與真正的 controls

Container [repair](container/repair.md) 保留 [1,3,2] 手算錯誤與實際測例失敗。
首稿與錯誤英繁／review／harness 的 before-runtime-repair 檔保留，
重新批准後才同步翻譯；before-range-bridge 版本亦保存。
runtime-failures.log 中的 Python exception 是失敗，即使外層 shell 最後 cat 讓 exit 為 0。
錯法 negative-control 與正解 tests 分開，不算自然 Writer 成功或失敗的替代品。

Course 保留 finish.failed.py、bilingual-controls.failed.json、failed stdout／stderr；
檢查器把中文語序差異當成錯誤，修正檢查器後沒有改文章。
完整 verified code、verify.py、runtime 與實際 stdout／stderr 都在各自目錄。
來源 C／header 原件及 native tool captures 留在 external evidence，未把巨大 source dumps 複製進本包。

Observer [notes](observer-notes.md) 保留工具包裝錯誤、讀取截斷及 regex 檢查器問題。
[第一次錯誤空清單 equality](bilingual-mechanical.before-regex-repair.json) 不當成有效證據；
[修正後非空 mechanical check](bilingual-mechanical.json) 比較實際 fences、URLs 與 English interview。
機械一致性不是雙語語義判分。

[runtime_controls.py](runtime_controls.py) 從實際正文抽出四個完整程式，
對獨立 problem-definition oracle 比較 3,282／3,285／4,665／3,058 次，
[實際結果](runtime-independent.json) 共 14,290 全過。
不在 quadratic alternative 跑最大長度；不把 Course prose-only methods 冒稱成完整 code replay。
既有 tests/test_final_method_holdout.py 同時重播前三個 packet，沒有 model invocation 或新 digest 計算。
[147 段 quote check](quote-check.json) 全為 exact contiguous passages；
[quote audit](quote-audit.json) 無另補引文。Raw gaps／limits 不會因 CI 需要而刪改。

[cost-control](cost-control/output.json) 是第三位 fresh Reader 的 planted sensitivity：
把英繁各一段 aggregate-cost proof 換成 bound／definition／sequence condition，
其餘 model／程式／頻率／結論／adaptation 保留。
[事先私存的 transformation／expected](cost-control-private.json) 未給 Reader。
Reader 標記 cost 缺項。這不是自然 Writer 樣本、已校準 judge 或效果改善的實驗證明。

## Schema、capture 與續行

[criteria](feedback/criteria-review.json) 先審需求來源，不看文章結果；
[Schema readback](feedback/observed.json) VALID／SUPPORTED／10 fields PASS，
只支持五個 action reports，workflow decisions=null、authorizes_landing=false。
[消費原 next](schema-consumed.json) 沒有授予 merge／deploy、全文品質或學習結論。
工具原本的本機 FileRef 綁定不變成 CI 額外 SHA-256 gate。

[session manifest](session-manifest.json)、[capture audit](capture-audit.json)、
[selection](selection.md)、[cognitive review](cognitive-review.md)、[local checks](local-checks.json)
說明實際條件及範圍。外部位置見 manifest。
App captures 有逐項長度上限，native web observations 亦不保證完整；
不同目錄與 fork_turns=none 並非強制 filesystem read isolation。
repo 是可重播投影，不能冒充完整原生事件流。
沒有正文 Stage admission、publication、merge、provider 或 billing effect。

原 container/runtime-failures.log 與 courses/report.md 的多餘 EOF 空白被 diff check 拒絕；
旁邊的 .raw.gz 保留完整原 bytes，可讀檔只移除末尾空白行。文章、首稿與 Reader 原件未改。
