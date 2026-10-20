# 從支持句到可重建的成本推導

本輪依 [狀態機修改契約](state-machine-change.md) 修正通用產文方法。
舊 Daily Temperatures／Subsets 正文及 Reader 原始缺項不變；
不以修補兩篇案例取代方法，也不把後續產文結果倒填成舊版成功。
新版方法固定於 `1487e11f5347806ca4a1e218f0a1d61bb6c8e34e`。

## 來源支持的原因與未知

前輪方法已要求逐一重建各方法，並在私有自審定位正文支持段落。
因此再加「必須有引文」不能解釋或修正本次問題。
[Daily Temperatures 自審](../evals/writing/leetcode-route-closure/temperatures/report.md)
引用了 index 入列／移除次數與最終 O(n)，接著在筆記中補充 CPython resize 細節，
並判定 geometric 與 capacity-gap 敘述足以支持 amortized cost。
但 [正文](../evals/writing/leetcode-route-closure/temperatures/article.en.md)
沒有展開容量序列及其和的界線；[Reader](../evals/writing/leetcode-route-closure/temperatures/reader.raw.json)
能重述結果，仍須外補該推導。

[Subsets 自審](../evals/writing/leetcode-route-closure/subsets/english-review.md)
逐方法列出 nodes、copies、retained／transient／output 成本，
卻未查明 growing-run append 性質如何適用於 shared path 的交錯 append/pop。
兩例可觀察的共同失效，是將「存在支持句」當成「句子間必要推論已閉合」。
來源事實、作者知道的知識、正文讓讀者獲得的解釋是不同證據。
這不足以判斷作者內在注意力、意圖或心理原因；也未證明最終公式或程式錯誤。

成本模型可以明示 elementary units，不必把每個算術／index 操作展開到硬體。
前輪 Reader 另外列舉的所有 primitive-cost 疑問，並未自動全部採為新要求。
真正要補的，是在文章宣告的讀者與模型下，仍須從外部取得的必要關係。

## Thinking 與 Ambitious 的往返及融合

在同一 Session 手動讀取／應用 Soodles commit
`1f5bfbe19d553304ca2f60138fe2c22519d655dd` 的
[Thinking Router](https://github.com/ed3c/soodles/blob/1f5bfbe19d553304ca2f60138fe2c22519d655dd/.agents/skills/thinking-router/SKILL.md)
與 [Ambitious Route](https://github.com/ed3c/soodles/blob/1f5bfbe19d553304ca2f60138fe2c22519d655dd/.agents/skills/ambitious-route/SKILL.md)。
沒有原生 Skill-tool invocation、另一個 Thinking Agent、Loop admission 或新核准流程。

Thinking V2／Adversarial 用已存在的規則與真實自審反駁「規則不存在」。
Ambitious Depth／Range 借用 backward proof checking：由結論追到操作次數、
單次／aggregate work 與條件，分辨已解釋的論證、明示基本模型及未解決主張。
Thinking 反例是無限追到物理，或把陌生資料結構的效能性質全部宣告為原子成本；
前者過度擴張，後者逃避文章用來選法的關鍵比較。
所以停止點是已解釋的 elementary work／storage model 與宣告的讀者前提。
Ambitious 再指出小數值例不等於一般上界，因此還要解釋關係如何隨 size 持續，
並核對 aggregate bound 的合法操作序列，不能只引用 theorem 名稱或循環支持。

融合成一個最小變更：保留逐方法 scope 與 exact passages，
但自審須實際連接成本推論、指出自己從記憶／來源筆記補入的部分；
有缺口就在正文修正後重審，或維持 incomplete。
不新增 schema、compiler stage、公開 checklist、固定圖數、各 CPU 操作清單或語義 linter。
案例中的 API、演算法與公式未寫入通用指引。
沒有新的可驗證區別會改變實作後，停止認知往返，固定方法再讓新 consumer 使用。

review-writing 使用原 STE Issue9 的術語、actor、前提、因果及原義保存規則；
工程指引不跑 sloptrim，不宣稱正式 STE compliance。
原 Content Owner、formatter、CLI／annotation／publication owner 不變。
Test Manager 沿 target 既有驗證入口；沒有把 Soodles 自身 full suite 套到本 repo。

## 新的固定盲寫設計

選擇 11 Container With Most Water 與 207 Course Schedule。
兩者均未用於先前 49、20、704、198、200、56、739、78 的開發或 holdout。
Writer 只收到固定 general instructions、題目、同一基本 Python syntax audience、
允許的官方 statement／Python／CPython primary sources 與一般交付要求。
沒有範文、editorial、解法大綱、先前失敗、Reader 問題、預期答案或另一位 Writer 的輸出。
各自從零選解法、trace、proof、alternative、pivot、成本與文章結構。

兩份作者首次完整英繁交付先凍結，才交給各自 fresh Reader。
Reader 只讀正文、audience、原八個一般問題及輸出格式。
不給作者筆記、skill、來源、程式測試或預期答案；不得從背景知識補上缺項。
保留首份完整英／繁、作者內部修訂及所有失敗，不做 Reader 後補稿或重抽成功題。
使用原生 Local Codex、fork_turns=none、預設 model；共享 filesystem 不證明強制 read isolation。
這不是六次 retained-runner 比較、instruction-only gain、一般可靠率或 human-learning measurement。

Schema 2 在 Writer 前固定，只比對五個 action-report fields。
獨立 reviewer 審查 exact requirement quotes；不觀察文章結果後修改 expected。
工具來源綁定由原 producer 計算，本機回饋不變成新的 CI hashing gate。
父 Session 的 problem-definition oracle 與 literal controls 也在閱讀新文章前固定。
程式 correctness、Reader 重建與來源真偽仍分開判斷。

external evidence：
`/private/var/folders/l6/44bf7nvs64j60f1mpyy88hdm0000gn/T/leetcode-cost-premises-0pm97zkf`。
本機 registration 13 tests、ordinary v4 5 tests 通過；verify-medium doctor 為 mechanical_pass，
只支持來源／註冊。以下是實際首次交付與 Reader readback。

## 新文章與首次 Reader 重建

- Container With Most Water：[英文](../evals/writing/leetcode-cost-premises/container/article.en.md)、
  [繁中](../evals/writing/leetcode-cost-premises/container/article.zh-TW.md)、
  [Reader 原始回覆](../evals/writing/leetcode-cost-premises/container/reader.raw.json)。
- Course Schedule：[英文](../evals/writing/leetcode-cost-premises/courses/article.en.md)、
  [繁中](../evals/writing/leetcode-cost-premises/courses/article.zh-TW.md)、
  [Reader 原始回覆](../evals/writing/leetcode-cost-premises/courses/reader.raw.json)。

兩位 fresh Reader 都回答八題，`unanswered_question_ids=[]`，未回報實質英繁不一致。
這是本輪兩個樣本在固定問題下的重建結果，不是文章品質分數或一般穩定性證明。
Reader 沒有收到作者報告、source notes 或原失敗；正文沒有收到 Reader 後修補。

Container 作者在私有 review 實際連接 pair count、range setups 與每候選固定工作，
以及 index distance、iteration count 與 fixed live state；座標 adaptation 分開計算新增讀取與有界算術。
這些關係也位於正文。Reader 能用新輸入 [1,4,2,3] 重建三次迭代及答案 6，
並重建錯誤 taller-wall discard 在 [1,3,3] 的第一個失效狀態。
成本重建分開原輸入、output、auxiliary、累計建立與同時存活的 range，不靠固定公式記憶。

Course 作者把 list.append 的 aggregate bound 與 deque 的端點機制分開；
正文明示 elementary model、size-dependent copying、比例容量與後向級數，
再由各 adjacency list 的長度總和導出 E，並限定 append-only sequence。
這個相同前提在 order-output adaptation 中被明確保留。
Reader 能重建新四課輸入的 delayed release，以及主法、重掃替代法、order-output 的成本，
沒有把 nested loops 直接乘成 V×E，也沒有把 append 的回傳或費用視為語法常識。

Owner 的獨立來源核對讀了官方題目與 CPython v3.14.0 的 deque blocks／list resize 部分；
端點不整段搬移、單項成長比例 over-allocation 與本文限定相符。
Container 的兩端排除 inequality、main trace、counterexample、座標範例；
Course 的 obligations checkpoint、self-loop、finite-cycle argument 與新 trace，皆另核對具體狀態。
runtime controls 不充當這些 proof 的證據。

仍保留兩個較窄的閱讀限制。Course Reader 指出替代重掃法未直接寫出 done 初始 Boolean 值；
主實作 checkpoint 與其成本問題可回答，不代表替代法每個初始化細節都明列了。
正文主證明說明起初沒有 completed courses，done 又代表已完成狀態，
但把它明寫為全 false 會更直接。保留此限制，不改寫 raw answer 或在看過答案後補稿。
Owner 另指出 append 的前向分攤直觀若單獨閱讀，沒有處理最後一次 resize 之後可能沒有更多 append；
正文接著的後向容量和包含最終 C，可獨立支持整段 upper bound。
因此不把前向一句單獨視為完整證明，也不因有後向論證就宣稱每句表述無可改善。

## 真實失敗及控制組

[evidence packet](../evals/writing/leetcode-cost-premises/README.md) 保留全部英繁首稿、作者內部修訂、原始失敗及完成交付。
Container 首稿錯把 [1,3,2] 的相鄰 pair 面積當成 3，實際 min 為 2。
真實程式測試發現 literal／反例手算錯誤；主程式無需修改。
作者保存當時英繁與 review／harness，修成 [1,3,3] 的合法錯法反例，
也修正座標段落的 index-width 對照值，重新審英文後才同步繁中。
最後另把私有 review 的 range-setup 成本橋接移到正文。
這些是首次完整交付內的作者修訂，不能算 Reader 後改善或首次首稿全正確。
首次 runtime command 最後的 cat 為 exit0，但內部 Python exception 保留；
父 Session 按實際錯誤判讀，沒有把 shell exit0 當成正解通過。

Course 的首次雙語檢查因 inline-code 順序不同而 AssertionError，
原失敗程式／JSON／stderr 保留。作者查明中文語序調換，未缺英文 inline tokens，
才修檢查器；沒有改正文迎合 sequence equality。
父 Session 的首個 code／URL equality 檢查也因 regex 過度跳脫，錯把兩份空清單當相同；
零計數暴露問題，保留錯誤輸出後修正，加入非空條件重跑。
不得拿這兩個檢查器結果當語義真值。

另由第三位 fresh Reader 讀 Course 的雙語刪除控制：
只把 append-only aggregate proof 段換成原有 bound、definition 與適用條件，
保留 primitive model、程式、頻率、公式、其他機制及 output adaptation。
預期在 Reader 看不到的 observer material 先固定。
Reader 實際標記 `cost`：resize policy 到 O(d) 總成本之間的必要轉換未展示。
這支持本次對該缺口的敏感性，不能作自然 Writer 失敗、已校準 judge、因果改善或人類測量。

## 驗證、原 next 與未觀察範圍

Observer 執行實際正文的四段完整程式；英繁 code 相同：

- Container all-pairs：3,282／3,282；
  main two-pointer：3,285／3,285；
  coordinate adaptation：4,665／4,665。
- Course main solution：3,058／3,058。

總計 14,290 個比較；包含合法最小／最大、全零／全高、座標跨度、self-loops、
小型有向圖窮舉、2000-course chain／cycle 及 5000-edge boundaries。
不對 quadratic all-pairs 執行 n=100000。
Course 文字替代法與 output adaptation 的重建、proof／cost review，
沒有冒稱額外完整 body-code runtime。
三份 Reader 的 147 段引文皆可逐字定位；英繁各三段 fences 一致，
來源 URL 順序及 English interview（Container 五段／Course 四段）保留。
既有 packet replay 與引文控制兩個 tests 通過；CI 沒有新增 model judge 或非必要 SHA-256 計算。

Schema 2 實際 readback：VALID、criteria SUPPORTED、10／10 reported fields PASS，
`workflow_decisions=null`、`authorizes_landing=false`。
父 Session 已消費原 `consume_verified_behavior`，只接受五項操作回報相符；
不把它轉成全文語義、讀者理解或 landing 權限。
這輪 criteria 未被拒絕；前輪的拒絕與自然 Writer 失敗都保留，不重寫歷史。

Native captures 與 task/source snapshots 保存在外部 evidence，repo 保存可重播投影。
逐項 20,000-character capture 限制截斷了部分 command output；
這和模型當時看到的工具輸出是否截斷、原生 web 事件是否完整可見，是不同問題。
共享 filesystem、未強制讀取隔離、未做 matched A/B 或 human study 的限制不變。
本輪支持的是兩個新樣本的正文成本重建可行；不能外推一般可靠率、方法的單獨因果效果或真人完全理解。
交付仍止於原 PR 與 matching-head CI，不 merge、不部署。
