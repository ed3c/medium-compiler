# A 完整註解限定語修稿紀錄

本輪沿用 Representation A，不是舊短骨架第四輪，也未清除先前三輪 NEEDS_REVISION。第一組 A candidate 與 Reader FAIL 完整保存在本目錄根部兩份 manifest 與 first-A-reader-report/；舊 evidence 位置見 entry.json。

實際讀回目前 speed-reading 方法、第一輪 A Reader 全報告與 findings，以及全部 83 段的完整 English、zh_note、premises/checkpoint、reading cue 和相關 31 項 Active sentence/cue/oracle。qualifier-audit-all-83.json 保存 558 個可見欄位及每段方向／強度判讀。這是 Owner 自審，不是獨立 Reader PASS。

Reader F1：Water zero-based p22 把 item assignment 這個寫入例子升格為唯一必要機制。實跑 append 可在相同合法 list 上改值且沒有 item assignment；原函式這一案例仍保留輸入。修正 zh_note 與 premise0，限回來源程式的讀取、綁定、更新操作，保留 item assignment 是寫入例子而非所有 mutation 必要條件。

Owner 重審另發現：Course zero-based p7 的「求值 [] 才有」也把充分做法升格為必要機制。實跑 list() comprehension 同樣取得獨立 inner lists；list repetition 對照仍共享。修正 zh_note 與 premise0 為此 comprehension 的效果，不宣稱唯一配置語法。完整前後理由見 repair-delta-four-fields.json。

本輪僅兩段、四個文字欄位改動；還原這四欄後，每份 JSON 物件與凍結首 A candidate 完全相同。四份來源正文、全部 83 份完整 English/tokens/stress/cues、31 個 Active 和所有其餘欄位保持不變。464 處 context supporting quote 維持精確來源且 unchanged。stress 無新查證或新增，保留既有 PARTIAL；learner NOT_OBSERVED。兩則 retained zh_note 修改是本輪明確授權修正例外，沒有回溯宣稱首 A 正確。

實跑反例僅反駁排他措辭，不是對所有合法輸入的 runtime 證明。全83自審沒有再找到需修的充分→必要／範圍升級；未把此判讀當客觀語義 PASS。metadata 保持 PENDING_INDEPENDENT_READER。新修稿已安裝並逐 byte readback，見 installed-readback.json；尚待同一 Reader 復核。未更動 code/docs/skills/branch，未 commit/deploy。
