# 第二輪獨立 skeleton 審讀

**結論：NEEDS_REVISION。** 全部83筆已逐項審讀，81筆未找到新的具體失敗；Water P11 是 INCOMPLETE_SCOPE，Water P39 是 FAIL_PRECONDITION。原R1、R2、R3及父Session指定的Course P26問題在目前候選中已解決。第一次NEEDS_REVISION與frozen snapshots保持原樣。

## 實際輸入與carrier

- current speed-reading SKILL 已讀，包括獨立展開／最小條件改變的方法。
- 兩份當次manifest與四份完整正文已另存snapshot；四份正文與第一輪已完整讀過的版本逐位元相同。
- 沒有讀作者reaudit、自審、新probe或其答案；沒有提供期望修法；只寫本/tmp目錄。
- 實際 CODEX_THREAD_ID：`01a15c79-7344-7bd1-84bb-6817ee643567`。
- 第二輪目錄：`/tmp/speed-layout-reader-second-t753q3cx`。第一輪保留在 `/tmp/speed-layout-reader-2wkbm24d`。

## 83筆範圍與改動核對

- Water paragraph_index 0–42：43筆；Course paragraph_index 0–39：40筆。每筆的候選、獨立展開句、語義判讀與理由保存在paragraph-audit.json。
- 實際17筆skeleton變更：Water 7,12,13,25,26,29,31,37,42；Course 8,24,26,28,33,34,37,38。
- 83筆其餘paragraph annotation欄位都與第一候選相同，包含tokens、stress、zh note等；31個Active items也不變。這個相同結果不作語義PASS。
- 本輪主範圍為83筆skeleton；Active causal-chain判讀沿用明確標示為第一輪結果，沒有把20筆quote存在重新宣告為全鏈證明。

## 原findings目前狀態

- R1 / container-with-most-water P12：RESOLVED_IN_CURRENT_CANDIDATE。目前骨架：With 0≤height[left]≤height[right], endpoint area → bounds → inward pairs retaining left.。判據：explicit 0≤height[left]≤height[right] plus inward retained-left selection。
- R2 / container-with-most-water P13：RESOLVED_IN_CURRENT_CANDIDATE。目前骨架：With 0≤height[left]≤height[right], recorded endpoint area → bounds → inward retained-left pairs.。判據：explicit nonnegative shorter-left premise, recorded endpoint area and inward retained-left selection。
- R3 / course-schedule P33：RESOLVED_IN_CURRENT_CANDIDATE。目前骨架：All courses completed legally once → form → a valid order without smallest-first guarantees.。判據：all courses completed legally once。
- PARENT-R4 / course-schedule P26：RESOLVED_IN_CURRENT_CANDIDATE。目前骨架：When allocated slots run out, an append → may require → resizing and copying.。判據：capacity-exhaustion condition and may resize/copy are explicit。

## 新findings

### SECOND-N1 INCOMPLETE_SCOPE — articles/leetcode-11-container-with-most-water.en.md P11

實際骨架：Keeping the shorter left wall → bounds → every narrower pair's height.

獨立展開：Keeping the shorter left wall bounds every narrower pair height.

every narrower pair 的量詞對象應當受 retaining-left 限定；目前的主語 Keeping the shorter left wall 可以暗示這種讀法，但賓語沒有明示，較廣讀法會宣稱它限制所有較窄配對。此處記範圍不完整，不把唯一讀法直接定成錯誤。

- P11：Consider any pair that keeps left and replaces right with an inner position k.
- P11：Its width k - left is smaller, and its water height cannot exceed height[left], even if the new wall is much taller.
- P15：On [1, 3, 3], the outer pair gives area 2.
- P15：it misses positions 1 and 2, whose area is 3.

最小來源內反例：使用原文 [1,3,3]：left=0 的短牆高為1，right=2。內側 pair (1,2) 的寬為1，小於外側寬2，但其水高為3，大於短左牆高1。這反駁 every narrower pair 的廣義讀法；pair (1,2) 不保留 left。保留 left 的狹義讀法則成立。

### SECOND-N2 FAIL_PRECONDITION — articles/leetcode-11-container-with-most-water.en.md P39

實際骨架：Equal heights → permit → either endpoint's safe removal; this code removes left.

獨立展開：Equal heights permit either endpoint to be removed safely.

equal heights 不足以單獨授權 safe removal；答案先由當前 endpoint area 計算／記錄所覆蓋，是移除前的必要狀態。骨架沒有這個狀態。

- P39：What happens on equal heights? Either endpoint can be removed safely. This implementation removes the left one.
- P10：Evaluate its endpoint pair before discarding anything.
- P15：It removes a wall only after proving that the lost pairs are already covered by a recorded value.
- P20：A separate tie witness, [3, 3, 3], starts with area 6, moves left, measures area 3, moves left again and returns 6.

最小來源內反例：原文等高 witness [3,3,3] 的外側面積6。若只滿足骨架的 equal heights，在尚未計算／保存6時先移除任一外側端點，剩下唯一 pair 面積3，先前的6已不能由該次後續搜尋取得。因此 equal heights 與相同合法輸入並未單獨保證 safe。實際程式先記錄面積，並沒有這個錯誤；這是骨架省去順序／記錄狀態的反例。

## Limits

- 這是獨立Agent的具體閱讀判讀，不是形式語義證明或語義完備性保證。
- P11保留兩種語法讀法的差異，記為scope不完整；沒有把狹義成立讀法隱藏。P39則有明確先後狀態反例。
- 新findings包含我第一輪未列出的地方；第一輪原判讀未重寫成事後已知結果。
- 語義展開以source中的算法／資料模型為domain；沒有任意更改程式、破壞queue invariant、改成非法輸入再聲稱現有implementation失敗。P39反例特別只用來檢查骨架沒有帶入的記錄狀態。
- Course P8的without smallest-first ordering按不施加最小優先規則解讀；不宣稱FIFO的實際輸出永遠不可能碰巧升序。Course P35 reaches zero按包含初始化設定零解讀。這些自然語句的讀法界線已寫入逐筆紀錄。
- 沒有新增外部字典查證、browser像素檢查或runtime測試；未借機械checks斷言語義正確。
- 實際人類閱讀：NOT_OBSERVED；閱讀速度：NOT_OBSERVED；理解／記憶／學習效益：NOT_OBSERVED。

## 檔案

- conditions.json：第二輪先行條件及actual carrier。
- paragraph-audit.json：完整83筆逐項展開與判讀。
- new-findings.json：新兩筆完整source quote與反例。
- old-findings-status.json：原findings當前狀態。
- candidate-delta.json：實際17筆diff與未改欄位control。
- source-receipts.json：四正文實際sha256及第一輪identity對照。
- speed-reading-SKILL.md、兩份manifest與四份正文：當次snapshot。
