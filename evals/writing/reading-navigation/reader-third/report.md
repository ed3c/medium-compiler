# 第三輪獨立 skeleton 審讀

**結論：FAIL / NEEDS_REVISION。** 全部83筆完整核對後，82筆未找到新的具體失敗，Course P21有1筆FAIL_CHECKPOINT。原R1/R2/R3、父Session的Course P26、第二輪Water P11/P39，在第三候選均已解決；不能因此忽略這筆新失敗。

這是同一Reader、同一方法的第三輪，未修改條件或候選，未讀作者第三輪check/repair或新probe答案。前兩輪原候選與失敗報告保留。

## Actual scope／candidate

- Water P0–42，共43筆；Course P0–39，共40筆。逐筆候選、獨立展開、scope/state/順序判讀見paragraph-audit.json。
- 凍結第三候選與兩完整manifest、四正文、current skill於本目錄；四正文與前兩輪完整讀過的版本逐位元相同，skill與第二輪相同。
- 實際6筆骨架變更，全部為Water：P10、P11、P14、P26、P39、P42。其餘整份manifest除骨架外全不變，包含全部tokens／stress／zh／31個Active。未把不變當語義通過證明。
- 本輪審讀83筆骨架全部，而非只看6筆diff。Course P21這次沒有改動，仍被檢出。
- actual CODEX_THREAD_ID：`01a15c79-7344-7bd1-84bb-6817ee643567`。
- 第三輪目錄：`/tmp/speed-layout-reader-third-k24_sv84`；第二輪：`/tmp/speed-layout-reader-second-t753q3cx`；第一輪：`/tmp/speed-layout-reader-2wkbm24d`。

## Prior findings

- R1 / container-with-most-water P12：RESOLVED_IN_THIRD_CANDIDATE；目前骨架：With 0≤height[left]≤height[right], endpoint area → bounds → inward pairs retaining left.
- R2 / container-with-most-water P13：RESOLVED_IN_THIRD_CANDIDATE；目前骨架：With 0≤height[left]≤height[right], recorded endpoint area → bounds → inward retained-left pairs.
- R3 / course-schedule P33：RESOLVED_IN_THIRD_CANDIDATE；目前骨架：All courses completed legally once → form → a valid order without smallest-first guarantees.
- PARENT-R4 / course-schedule P26：RESOLVED_IN_THIRD_CANDIDATE；目前骨架：When allocated slots run out, an append → may require → resizing and copying.
- SECOND-N1 / container-with-most-water P11：RESOLVED_IN_THIRD_CANDIDATE；目前骨架：The shorter left wall → caps → the height of inward pairs retaining left.
- SECOND-N2 / container-with-most-water P39：RESOLVED_IN_THIRD_CANDIDATE；目前骨架：After saving equal-height endpoint area → remove → either endpoint; this code removes left.

## THIRD-N1 FAIL_CHECKPOINT — Course P21

候選骨架：The empty queue plus completion count → distinguishes → a schedule from a cyclic remainder.

不補前提的展開：The empty queue plus completed-course count distinguishes a completed schedule from a cyclic remainder.

骨架只有 empty queue 與 completion count，沒有最終／完成所有更新的 checkpoint。把同一合法執行的觀測時點改為迴圈內取出 course 2 後、更新 dependent 前，就得到 empty queue、finished=4、unfinished course 3，但 graph 仍無 cycle。不能由骨架目前保留的兩個條件直接區分 cyclic remainder。

- P16：Removing 2 empties the queue and raises finished to 4.
- P16：Course 3 changes from 1 to 0. Appending 3 gives [3], with counts [0, 0, 0, 0, 0].
- P18：The checkpoint is just before each evaluation of while ready, after all updates for the preceding completion.
- P21：For termination, at most numCourses distinct courses can be removed.
- P21：Otherwise the queue is empty with some courses unfinished. The checkpoint says each such course still has an unfinished prerequisite.

最小條件改變：保留原文同一輸入與程式，只把觀測時點從更新完的while checkpoint改為取出course 2並遞增finished後、尚未完成dependent更新時。此時ready=[]、finished=4；之後course 3由1降0並入列，最後完成5門並回傳True。這是合法無環執行中的中間狀態，反駁不帶checkpoint的廣義骨架。這個反例不是宣稱實際implementation在終止時判錯。

第二輪我的展開曾寫「At termination the empty queue and completed count distinguish a full schedule from a cyclic remainder.」，其中At termination並不在候選骨架內。這是前輪漏檢，沒有把舊報告改成事後已知結果，也沒有另加一套規則。

## Limits

- 這是獨立Agent對此凍結候選的具體審讀；不構成形式語義證明、不推論普遍穩定性或所有可能錯誤都已找出。
- 從來源正文找出遺失checkpoint，是指出骨架缺失，不是用正文把缺失默補回骨架後宣告通過。
- 第三輪原有兩筆Water問題已解決，但仍有新的同類狀態漏項；本輪不修文、不重抽Reader、不啟動第四輪。
- 第一輪Active causal-chain觀察保留為其原範圍結果。本輪未重新宣稱完整Active證明，也未把quote存在或來源byte identity當語義證明。
- Course P8沿用不施加最小優先規則的讀法；不宣稱輸出永遠不可能碰巧升序。Course P35沿用remaining indegree為runtime零值觸發criterion的讀法，reaches zero包含初始化設定零；不把它當任意construction／中途更新狀態都滿足完整checkpoint invariant的宣稱。
- 例子數值骨架按其特定movie fact cue審讀，沒有把它們擴張成所有輸入都回傳8／198等普遍定理。
- 沒有外部字典頁新增查證、browser像素檢視、runtime重跑或真人測量。本輪反例是來源內的symbolic state-order countercheck。
- 實際人類閱讀：NOT_OBSERVED；速度：NOT_OBSERVED；理解／記憶／學習效益：NOT_OBSERVED。

## Evidence files

- paragraph-audit.json：83筆逐項結果（82筆NO_NEW_FAILURE_IDENTIFIED；1筆FAIL_CHECKPOINT）。
- new-findings.json：第三輪完整finding、source quotes、反例狀態與前輪漏檢記錄。
- prior-findings-status.json：先前三輪指定6個finding的第三候選狀態。
- candidate-delta.json：6筆diff、全manifest其餘欄位相同性、skill identity。
- conditions.json：沿用條件與actual carrier。
- source-receipts.json、snapshot-identities.json：四正文identity與本輪frozen inputs身份。
- current skill、兩manifest與四正文snapshot。
