# 有界的獨立 Reader report

我以 elementary Python 讀者身分從四份完整批准 source bodies 重建兩篇文章，再逐一讀完 83 個 complete paragraph annotations（Water 43、Course 40），包含 note、全部 premise/checkpoint、所鏈段落、reading markup、短 cue、Active sentence/cue/oracle。繁中、英文各複製一份，共 166 個展示 instances；兩語同項 annotation fields 完全相同，因此不是 166 個獨立語意案例。

結論：82/83 項為 PASS_BOUNDED；water:p22 有一項 source scope 措辭 FAIL，其限定於展示程式的重建仍通過。發現是「只有 item assignment」的排他語氣，比來源的充分例示更強。合法起始 list [2,5] 可經 height.append(1) 修改而無 item assignment；這只否定一般化，不表示原函式有這項 mutation。完整引文與界限在 findings.json / audit.json，沒有刪去此失敗。

Water 的核心重建是：同一合法 pair 的正寬乘非負短高；在短端分支只界住保留該短端的 inward partners；先把已量 endpoint area 納入 best，才刪這組候選。每次 while 檢查時，best 同時最大化已量候選並涵蓋區間外 pair。距離歸零才覆蓋全域，且 best 來自真實候選。座標版另需 x 嚴增、對齊且已供應。沒有把「內縮」擴成所有內部 pair，也沒有從 safe discard 推下一 area 改善。

Course 的核心重建是：b→a 表示 b 完成才消除 a 的一項義務；counts 必須是數量，初始零由完整 ID scan 納入、後來正值剛達零再納入。checkpoint 僅在前一 completion 的整份 dependent updates 完成後，要求 distinct finished、unfinished counts 正確以及 ready 恰含所有 available unfinished courses 各一次。最終完整 ready 空並且仍有 unfinished 課，才能用有限逆追推出 cycle。FIFO 無 smallest-first 保證；self-loop 包含在 contract。

來源與reading fidelity：四頁 article block 序列（每份 Water 55 blocks、Course 51 blocks）與各自完整 Markdown 在去除 Markdown/HTML 表示層後對應，段落／headings／code 沒有發現內容遺失；外部 source links 的順序和 URL 相同。每項 reading 去除新增的 break、bundle 邊框與重音標記後，逐字內容（僅合併空白）對應同 index 的 English source。完整中文 source 與完整英文 source 也已分別通讀，沒有發現改掉 contract、否定、數量或證明關係。這些逐項比較只是 fidelity 證據，語意判斷另見 83 行 audit。

Chunk/cue：83 reading texts 與全部 bundle/stress attachments 已讀。未發現 bundle 換掉關係子句對象、not/only/either 指向或把 selected object 換成較大的集合。/、// 有些切得很細，例如 Course p15 的「3 stays /out of the queue //because ...」，但後接原因、完整 context 及 source 均仍在；我不把停頓處視為獨立定理。短 cue 明示非獨立結論，判定以 complete annotation 與其明鏈argument為單位。

Active：30 個含Active的paragraph，合計 31 個term/sentence entries。每個展示 sentence 與原段可對照，cue/oracle 的推論均可由該項完整 context 加其明鏈來源重建。重要的限定包括 Water p21 的「這份程式每branch各一次index update」、Water p35 的非負高度／有序對齊座標，以及 Course p6/p18 的完整 dependent updates 檢查點。若將 oracle 單獨抽離，這些短回答不足作無條件 theorem；本 request 的驗收單位沒有要求那樣閱讀。沒有另發現 Active 內容上的FAIL。

界限：我只讀指定 frozen HTML 與source文字，沒有開瀏覽器、取得CSS/JS或執行互動；不判定視覺遮擋、展開/點擊功能、音訊、壓力/斷句的人類效果、或程式測試。像 algorithm 的 al stress markup 只是可觀察的字形標記，批准輸入沒有提供可獨立核對音韻的音源/詞典；發音 evidence 為 partial，不能標總體 pronunciation PASS。批准 bodies 裡的外部 LeetCode/Python/CPython links 只核對保留，依只讀 allowlist 的邊界沒有fetch其內容，因此不把上述教材忠實性說成已另行查證那些上游版本實況。沒有真實學習者、計時、前後測或跨版本抽樣，所以不宣稱速度、學習成效或普遍穩定。

交付：audit.json 含完整83行、全部明鏈中英source引文、展示context、reading、Active及逐行重建；audit.tsv / audit.md 方便掃讀。findings.json 保留全部實際失敗。actual-reads.json 與 CODEX_THREAD_ID.txt 記本reader可觀察身分及讀取。由父代理另跑的code tests沒有混入本判定。
