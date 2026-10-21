# 文章閱讀介面與註解 Owner 修正

本輪使用者選 A：兩篇新文章英繁頁與既有 ALG Four 共用右側收合目錄；
每個頂層章節一條 bar，長度代表章節正文量；展開後包含段落、目前位置與註解。
交付仍止於原 PR81／CI，不 merge、不部署，不變更 Sandbox、API 或 billing。
後續明示 `speed-reading` 必須負責索引註解內容，已取代最初只當格式工具的提案。

## 來源觀察與最小修正

上一輪網站交付只登錄標題目錄。這不足以滿足本輪要求的逐段閱讀輔助：
兩篇新頁沒有註解，ALG Four 的常駐側欄則擠壓正文。實際 1440px viewport 中，
舊 ALG Four 正文約603px寬；新頁正文760px，但另常駐240px目錄。
直接開 `/alg-four/#alg-heading-4` 時，標題在125px，header底部約63px，
索引卻選了上一節第33段（零起算32），而非新節首段（零起算33）。
這是位置選擇的程式落差，不能以增加註解文字修好。

手動套用固定 Soodles Thinking Router／Ambitious Route 的方法，沒有原生 Skill
invocation、另一個 Router、Manager 或新 admission stage。Thinking 查原DOM與來源，
Ambitious Depth 借用漸進揭露：正文置中，導航先退到背景，需求出現才展開註解。
反例是把139個段落直接壓成139條細線，仍難以掃讀；使用者選章節bar，段落留在展開層。
另一個反例是只改善外觀，仍沒有來源對應的完整英文與解釋。
[Medium 官方說明](https://medium.com/blog/long-reads-on-medium-just-got-easier-to-read-and-enjoy-2a9f8fa135f8)
支持桌面右側 hover 目錄；段落註解、長度bar與手機操作是本案實作，不冒稱Medium原功能。

## 原責任與通用交付

- leetcode-mental 保留完整文章語義，medium-writing 保留 assembly。
- speed-reading 產出索引內的繁中解釋、完整英文衍生閱讀、骨架與有來源支持的 Active 句／cue／oracle。
- alg-four 維持 source Git blob、英繁對齊、逐段覆蓋、admission validation、導航與呈現。

沿[狀態機修改契約](state-machine-change.md)同步修正上述P-class、既有builder／validator與
[網站交付契約](bilingual-articles.md)。兩篇新文章分別43／40個正文段落，
有14／17個Active contexts，並非31個跨篇去重詞，也沒有湊2,000項。
83個英文原段落全部保留，既有四份文章bytes不變。Part7保留139段、14個Active與七張SVG；
只修Markdown emphasis的呈現，並同步13則原manifest的渲染英文文字，原source blobs未變。
ALG Four 的說明收進可展開區，原Markdown下載改由同一build提供，避免連到不同版本的main。

speed-reading以語法決定切分，不能把3–5個word當作一次眼球注視的證據。
本輪110個重音spans只用Cambridge核對的wall／width／queue／course／algorithm；
其餘保留plain。原文字、重音證據與衍生標記分開保存；模型與字典不在browser／CI執行。
目前沒有真人理解、眼動、閱讀速度或學習成效觀察。

## 真實失敗與修正

最初annotation Reader指出兩筆oracle需要其他段落的條件與成本推導。
新版Owner重審後，14筆Active明確綁定20則supporting quotes，頁面提供對應段落跳轉。
精確quote存在只證明文字位置，完整支持鏈仍由Owner與Reader判讀。

第一輪speed-reading Reader審完83段、110個stress spans與31個Active後，仍判NEEDS_REVISION：
Water P12／P13骨架省略較短left條件，Course P33省略完成V門課才回傳order的條件。
父Session另記Course P26的「despite spare capacity」觸發條件歧義。完整段落有條件，
不能替獨立骨架補上被壓縮掉的條件。所有首稿與失敗保留；沒有把首次結果改成PASS。
方法增加「骨架反向展開一句主張、改變一個前提找最小反例」的自審，並重審全部83段。

工程失敗同樣保存：抽出共用loader後的items變數漏接導致NameError；窄螢幕的滑鼠hover
提前開啟modal而攔截click；舊測試預期完全無重音與後續新增核對重音的要求衝突；
Schema criteria多一個非schema欄位遭原工具拒絕。分別修正原接線、hover範圍、
核對實際reviewed spans的assertion及保留原review的四欄投影，沒有停用測試或force click。

## 驗證與限制

真實Chromium覆蓋兩篇×兩語×desktop/mobile共8頁觀察與ALG Four的2個viewport：
預設收合、hover／touch／keyboard、章節與段落跳轉、直接hash、scroll跟隨、
panel獨立捲動、Escape與focus返回、正文／code無整頁橫向溢出、語言切換及原稿下載。
關閉控制留在panel頂部；從rail移入panel不應讓hover視窗消失。
Unit controls涵蓋來源漂移、缺段、空Active quote、錯誤supporting quote、缺reading view、
原字元與既有slash/bracket還原、function-word粗體及無發音證據的拒絕。
這些不是語義或閱讀效益的機械判定。

P-class分別保存format-only提案、使用者指定Owner後的完整註解交付，以及骨架修正後的
fresh consumer。最後consumer沒有範文、舊註解或Reader答案，從完整原文產出三則完整註解。
Schema2的三個reported-action fields VALID／SUPPORTED／PASS，原
consume_verified_behavior已由父Session消費；不等於所有骨架語義通過、真人理解或發布。
所有consumer使用fork_turns=none；共享filesystem不構成強制讀取隔離。
App read_thread取得原生capture，每項最多20,000字元，有截斷／摘要限制，未偽造完整event stream。

[可重讀首稿與失敗](../evals/writing/reading-navigation/README.md)留在原PR；完整原生capture、
commands、screenshots與實際工具輸出在external evidence：
`/var/folders/l6/44bf7nvs64j60f1mpyy88hdm0000gn/T/reading-navigation-mtgts0x3`。
必要Schema FileRefs由原工具產生，沒有新增CI報告hash；既有部署manifest在正常部署build保留。
Build／Wrangler dry-run不是Cloudflare發布。最新matching-head CI以原PR實際run為準。

## 三次停止與使用者選定的新驗收單位

第二輪仍找到 Water P11 的集合範圍遺失、P39 未保留先記錄面積再丟棄端點的順序。
第三輪仍找到 Course P21 沒有終止／完成所有 dependent updates 的判讀時點。
同一無環執行在迴圈內也會短暫 `ready=[]` 且尚未完成全部課程；不能因此推斷 cycle。
Reader 明認第二輪展開時自行補入「At termination」，這個漏判保留在原報告。
三輪原 verdict 均為 NEEDS_REVISION，沒有用最後82筆未找到新錯誤抵銷第83筆。

依三次停止紀律，停止繼續修短定理骨架。使用者選 A：完整註解為驗收單位，
明確顯示前提／檢查點，短骨架改為閱讀提示，不獨立斷言結論。
這是原需求選定的表示與驗收調整，不把前三輪改寫成新標準下的PASS。

Thinking 定位的早期斷點是本輪先前方法把15字骨架提升為獨立技術主張；
這是Session的驗證設計，並非使用者要求15字取代全文。作者與Reader又把自己能補回的
條件誤當成輸出已提供。Ambitious 換成漸進揭露的
完整註解：短問題引導注意，原文保留完整，前提與時點有可見且無15字限制的欄位。
其可推翻條件是完整註解仍無法讓Reader指出結論成立／不成立的差別；
引用存在、欄位齊全與問題句形式都不能當作通過證據。
原producer負責內容，原validator檢查欄位／exact quote，原consumer呈現並跳轉；
沒有新增Runtime stage或泛用Manager。

新 A 契約另有一個 fork_turns=none consumer，僅給凍結指引與完整英繁正文，
產出兩則完整註解。其原生thread為 `01a15c99-e7d1-70f2-b473-7a7dfdf5f9a3`。
Schema 回饋只支持 annotation_content_created=true、source_body_changed=false、
publication_performed=false 三欄，原 consume_verified_behavior 已消費。
父Session第一次把包裝report當raw output輸入，得到INCONCLUSIVE；保留該結果，
改交未更動的實際output.json後才取得VALID／SUPPORTED／reported-field PASS。
這不是語義驗收，也不是完全隔離、因果改善或真人效果證據。

## A 方案目前實測

A第一次候選的首稿與自審後候選各自凍結，14筆自審變更及原因保留；新資料有83份完整註解、
126則解釋性premises、59個checkpoint與24個null，464則exact supporting quote bindings。
每個閱讀提示為7–13詞問題；來源正文、既有zh note、tokens／重音與31個Active contexts未變。
數量只表達覆蓋，不是語義真實性指標；該候選之後交給新的fresh Reader（判定見下）。
既有ALG Four 139段註解保留為legacy approved projection，不冒稱由新Owner重新產製。

A版真實Chromium八個雙語viewport／page observations與ALG Four兩viewport已通過，
代表desktop closed／note與mobile note截圖已檢視。手機bar改為以可用寬度縮放，
避免CSS cap把不同章節截成同長；檢查實際bounding widths，非只檢查inline style。
相同完整站config的本機workerd API七個controls全過；provider頁面是synthetic fixture，
不能當成Cloudflare已部署或已訪問真實上游。全套Python與matching-head CI結果另讀回。

A第一次fresh Reader完成全部83份註解後，82項PASS_BOUNDED、Water P22（零起算）一項FAIL：
保留的zh_note與新增premise把原文「item assignment會寫入」提升成「只有item assignment能寫入」。
合法list也能用append修改；這否定排他措辭，不否定展示程式保留輸入。
Owner原自審只反駁「local binding會修改list」及「item assignment是讀取」，
未反駁反方向的唯一機制主張；既有註解被保留，錯誤也被帶進新context。
因此通用speed-reading自審改為逐一核對可見斷言（含retained note與Active）的方向與強度，
以另一合法機制檢查only／must／cannot；來源例示或充分條件不能直接變必要條件。
這是原有來源忠實性驗收的執行修正，沒有降低A的標準或重寫第一次verdict。
新的instruction bytes另綁fresh consumer；修正後仍須交回同一Reader讀回。

## 修稿後的有界讀回

完整限定語重審又找到Course P7的「每次[]才有獨立lists」可能把此comprehension的效果
升格成唯一必要建構；改為描述本實作分別求值[]會建立獨立lists。只改Water P22、
Course P7各自zh_note及premise，共四欄；原反例以實際Python執行保存。
83段、558可見欄位的Owner自審是本次輸出，不是決策數或完整語義真實性的機械度量。

同一fresh Reader在第二份凍結頁面核對actual delta：四正文與正文HTML完全不變，
81則完整註解exact unchanged並重用原有audit，兩則變動註解完整重新判讀。
現行83項PASS_BOUNDED，原F1已解決；首輪FAIL未改，Reader也保留Course P7首輪未單列
必要條件歧義的漏檢。這不是第二個獨立Reader或兩次全新83項觀察。
發音覆蓋仍partial，真人速度／理解／學習效果仍NOT_OBSERVED，不宣稱通用穩定性或措辭因果增益。
原生thread為 `01a15ca8-1d91-77a3-b89a-d1fe2c75e710`，其完整報告在
[portable evidence](../evals/writing/reading-navigation/representation-a/reader-second/report.md)。

全套Python296項完成，14項既有SCOPE_*上游缺件skip；未新增skip。
第一次8 failures／12 errors同源於macOS暫存根路徑經/var symlink；僅將fixture root resolve，
原production symlink拒絕不變。該檔21項通過後重跑全套OK，原失敗log保留。
最後四欄修稿後53項focused controls與八個雙語Chromium observations又通過。
既有ALG Four兩viewport、七SVG實載、exact Markdown及本機API七controls覆蓋未變輸入。
最後generic assertion-direction方法另有fresh source-only consumer與獨立criteria；
Schema VALID／SUPPORTED／三reported-action fields PASS的原next已消費，仍不認證語義或發布。

Reader後僅更新manifest的有界review metadata與兩則legacy note修正例外，未再改可見註解。
正式commit後的完整build／Wrangler dry-run及原PR新head CI以實際Provider讀回為準；不merge、不部署。
