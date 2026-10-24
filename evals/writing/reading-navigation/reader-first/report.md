# 獨立 speed-reading 語義審讀

結論：NEEDS_REVISION。83 筆完整閱讀投影已逐段讀過；3 筆 skeleton 有必要條件遺失（Water P12 為 INCOMPLETE；Water P13、Course P33 為 FAIL）。此結論不是學習效益實驗。

## 範圍與獨立條件

先寫 conditions.json，之後才讀允許輸入。只讀 speed-reading SKILL、兩份 manifest、其指向的四份完整英繁正文；為實際 rendered HTML 另提取 render_speed_reading 函式。未讀其他 agent 自審、舊 evidence 或預期答案。只寫本 /tmp 證據目錄；未修改 manifest、文章、skill，也未發布。

實際 carrier CODEX_THREAD_ID：01a15c79-7344-7bd1-84bb-6817ee643567

## Findings

### R1 INCOMPLETE: articles/leetcode-11-container-with-most-water.en.md paragraph_index=12

原始 skeleton：Nonnegative heights and smaller width → bound → every retained-left candidate.

骨架留下 nonnegative 與 smaller width，卻沒有保留這是 shorter-left 分支。原式最後一項之所以是已量到的 endpoint area，依賴 height[left] <= height[right]。省略它後，骨架只說 retained-left candidate 受界，沒有交代是以哪個已記錄值作界；若按章節用途反向展開為「每個較窄的 retained-left pair 都不超過剛量的 endpoint area」，條件就不足。

- P11：Suppose height[left] <= height[right].
- P11：Its width k - left is smaller, and its water height cannot exceed height[left], even if the new wall is much taller. Because heights are nonnegative,
- P12：area(left, k) <= (k - left) * height[left] <= (right - left) * height[left].

來源內交叉檢查：P14 明寫 right 較短時要保留 right 作同一個界並減少 right；P15 的 taller-wall 反例證明不能把任一端點當成可排除端點。這裡不以正文前段默補被骨架省去的必要條件。

### R2 FAIL: articles/leetcode-11-container-with-most-water.en.md paragraph_index=13

原始 skeleton：The recorded endpoint area → bounds → every remaining candidate involving left.

骨架把帶有 such pair 前文限定的結論，改成 recorded endpoint area 對所有 remaining candidate involving left 的無條件界。left 必須是較短或等高端點才有這個結論。正文與 Active A0004 保留 P11/P12 的條件，無法替這筆骨架消除條件遺失。

- P11：Suppose height[left] <= height[right].
- P13：So no such pair can beat the endpoint area we already recorded.
- P13：Every remaining candidate involving left can be discarded together by increasing left by one.
- P15：Always moving the taller wall lacks that proof.

來源內交叉檢查：只把 left 從 shorter 改成 taller，就離開 P11 證明分支；P14 指定此時要反向處理，P15 另給 taller-wall 路徑漏掉 optimum 的完整反例。

### R3 FAIL: articles/leetcode-207-course-schedule.en.md paragraph_index=33

原始 skeleton：Retaining legal completions → produces → one valid order without a smallest-first guarantee.

保留每一次合法完成，只能保證保留下來的 entries 各自合法；產生可回傳的完整 course order 還需要 length == V。骨架省略成功條件與失敗分支，因此把可能只有 partial order 的狀態寫成會產生 one valid order。

- P33：Return order if its length equals V, otherwise return [].
- P33：Each retained entry records a legal completion, so the earlier proof establishes the returned ordering.
- P34：On failure, the partial order is temporary auxiliary storage of at most V entries and the returned empty list has constant size.

來源內交叉檢查：P17 本文拒絕案例只完成 course 2，finished = 1，與 3 比較後回傳 False；依 P33 的改版，所保留的單一合法完成不能成為三門課的完整 order。P34 明確把 failure 的 partial order 記作 temporary auxiliary storage。

## 其餘觀察與限制

- 對全部 83 筆逐段檢查語塊、major break、bundle，未找到另一個已具體證成的條件或修飾範圍改變。if/since/because/only/negation 等仍保留在完整投影中。major break 的 render 會加 br。
- 110 個 stress spans 僅涵蓋 wall、width、course、queue、algorithm（含開頭大寫）；逐筆未找到 function word 或 code identifier 誤標。algorithm 標 al；其餘四詞為單音節 content words。每筆都有 Cambridge URL／pronunciation。因本次輸入 allowlist，不另開外部字典頁，故 authoritative-page verification 為 NOT_RUN，不能聲稱獨立完成外部 pronunciation 查證。
- 31 個 Active items 已逐項讀 primary paragraph 和全部 supporting_sources。20 筆 supporting quote 全部存在於其指向段落。就當前 oracle 的實際主張，未找到需靠私人知識補上的實質缺漏。尤其 Water A0004 綁 P11/P12，Course A0013 綁 P27 的攤還與 append-only 限制；A0014 同時保留個別 append 可能 resize 的 P26。此為有範圍的 Agent 語義判讀，不是通用正確性證明。
- 機械輔助：83/83 token text 串接等於完整 english_source；4/4 本地文章 blob 等於 manifest 宣告值；83/83 可由現有 render_speed_reading 產生 HTML。這些結果不推翻上述 skeleton 失敗，也不證明語義正確。
- skeleton 僅為正文補充，仍須保留會改變 technical claim 的必要條件；本報告沒有把每個未重述上下文都當成失敗，只列出涉及已證明分支或成功條件的具體問題。
- 實際人類閱讀：NOT_OBSERVED；速度：NOT_OBSERVED；理解／記憶／學習效益：NOT_OBSERVED。未做 browser 像素排版檢視。

## 實際證據檔

- conditions.json：先行條件與 carrier。
- source-receipts.json：四份完整正文的來源身份。
- paragraph-audit.json：83 筆逐段審讀結果。
- active-audit.json：31 項 oracle 的來源判讀及 20 筆 quote 檢查。
- findings.json：3 筆完整 finding、原始 skeleton 和來源 quote。
- mechanical-checks.json：lossless 輔助及 stress spans。
- container-with-most-water-rendered-review.txt、course-schedule-rendered-review.txt：獨立審讀用文本。
- rendered-review.html：以現有 render_speed_reading 函式產生的實際 HTML。
- 四份完整正文與兩份 manifest 的當次 snapshot。
