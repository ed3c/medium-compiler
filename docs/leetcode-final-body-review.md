# 從最終正文檢查每個方法的作者自審

這次修正 `leetcode-mental` 的通用產文方法，沒有修補舊 Islands 文章。
原因與新版首次產文結果分開記錄；作者的自審、fresh Reader 重建、文內程式執行與 Schema 回饋也各有界線。
新版方法固定於 `589ee4332275f2d6042f1039331e12a33f0f9b56`。

## 最早失效的交接

舊 [construction method](https://github.com/ed3c/medium-compiler/blob/ada0f01c6dfc6582b259318e46588b6db702ad5e/.agents/skills/leetcode-mental/references/article-construction.md)
已要求重算 alternative、reconstruction 與 output builder 的操作，並檢查 caveat 中的新前提。
所以「再加一條要分析變體成本」不是充分修正。
[Islands 的作者自審](../evals/writing/leetcode-final-method-holdout/islands/editorial-review.json)
列出全篇語義檢查並批准英文後翻譯；但 [首稿](../evals/writing/leetcode-final-method-holdout/islands/article.first.en.md)
與定稿的 recursive DFS／最短路段落，都沒有像主解法一樣閉合新 state 與操作的成本。
[fresh Reader](../evals/writing/leetcode-final-method-holdout/islands/reader.raw.json) 保留該缺項。

直接可觀察的是：全篇 approval 沒有要求指出各個已提出方法的正文依據，主解法的完整推導因而不足以保護後段。
我們沒有作者當時注意力或知識狀態的可靠量測，不能把「偷懶」「忘記」「不知道」當成已證明原因。
`K` 的局部符號疑點也不足以判定整個主法成本錯誤；真正需要修的是 scope 到自審證據的交接。

## Thinking 與 Ambitious 的必要往返

依 [狀態機修改契約](state-machine-change.md)，保留 Content Owner、formatter、CLI、annotation 與 publication 的原責任。
手動讀取 Soodles commit `1f5bfbe19d553304ca2f60138fe2c22519d655dd` 的
[Thinking Router](https://github.com/ed3c/soodles/blob/1f5bfbe19d553304ca2f60138fe2c22519d655dd/.agents/skills/thinking-router/SKILL.md)
與 [Ambitious Route](https://github.com/ed3c/soodles/blob/1f5bfbe19d553304ca2f60138fe2c22519d655dd/.agents/skills/ambitious-route/SKILL.md)。
這是同一 Session 應用方法，不宣稱原生 Skill invocation、Loop admission 或兩個思考 Agent。

Thinking V2／Adversarial 先排除「規則完全不存在」的解釋。
Ambitious Depth／Range 提出從最終產物反向追溯每項主張：從實際正文找出方法，而不是從原 outline 想起自己寫過什麼。
Thinking 再提出反例：若所有錯誤示例都要另寫完整 solution／cost，就會產生無關擴張。
因此核對範圍是實際提出的可用 approach／conditional adaptation，以及簡短比較所宣稱的具體 trade-off。
錯誤示例仍要解釋其失效前提，不強迫無關的完整成本推導。

Ambitious 再指出一份新的 checklist 也可能被直接標 PASS。
融合結果因此要求作者在原私有 review 中定位正文支持段落，從其 condition、state、操作與 primitive assumptions 重建結果及成本。
沒有依據時，該部分保持 incomplete；不能用主程式執行成功、全篇「已核對」或相同 Big O 取代它。
英文編輯新增／改動了前提，就在最終 edition 重開受影響的核對；繁中沿同一段落檢查。
不增加必填 schema、public checklist、compiler stage 或語義自動判分器。

未採納固定圖數、固定變體數、全面 internals 展開與新的 SHA-256 gate。
不因沒有 Big O 公式就豁免取捨主張，也不藉刪掉必要 alternative／pivot 逃避核對。
沒有新的可判別問題會改變方案後，停止認知往返，固定方法再產文。

## 審查與驗證範圍

依 Soodles review-writing，實際讀取 `features/ste-reference.md`，採用 Issue 9 的 1.5–1.13、3.6–3.7、4–6、9.1／9.3／9.4：
保留術語、actor、前置條件、因果與原義；不宣稱正式 STE compliance。
local 舊 `writing-review.md` 的七點上限，已對照固定遠端版本同檔確認為過時；沒有將它新增為本 repo gate。
P-class 只改 [construction](../.agents/skills/leetcode-mental/references/article-construction.md)
及 [content profile](../.agents/skills/leetcode-mental/references/article-content-profile.md)，ordinary v4、formatter、CLI 與 canonical source 不變。

Test Manager 保留 target 的既有 `writing-verification` 驗收；Soodles 自身的測試命令不套用到 medium-compiler。
本機先跑既有 registration／v4 controls，13＋5 tests 通過。接著對新文章實跑本文解法及獨立 oracle，並核對 Reader 引文。
普通 matching-head CI 保留原有 mechanical／Chromium jobs，不新增模型產文、額外 full-suite dispatch 或非必要 SHA-256。

P-class feedback 使用既有 Schema 2 standalone 工具，並由 fresh reviewer 先審查五個 reported-action fields。
首輪引文錯引 task 而非綁定的 requirements，Schema 實際拒絕；原 review 及拒絕保存。
同一 reviewer 只更正來源定位，十項條件維持 supported；未改 expected，也沒有將拒絕改稱 PASS。
後續欄位結果只表示操作回報相符，不認證全文語義、一般穩定性或 human learning。

## 新版盲寫的固定設計

兩題為 LeetCode 739 Daily Temperatures 與 LeetCode 78 Subsets，均未出現在既有 49、20、704、198、200、56 的開發／holdout 集合。
使用相同新版 instruction snapshots、基本 Python syntax audience、官方 statement／Python primary sources 範圍及一般交付要求。
不給範文、editorial、題目解法大綱、舊失敗、Reader 問題、預期答案或另一位 Writer 的結果。
兩份首次交付先凍結，再由各自的 fresh Reader 只讀英繁正文回答原八題；不向作者回傳修補提示。
作者依方法自審的修訂與 first complete drafts 分開保存。

Native Local Codex consumers 使用 `fork_turns=none`，未指定 model override。
共享 filesystem 不構成強制 read isolation；原生 capture 的截斷與可見範圍必須保留。
這不是六次 matched comparison、instruction-only gain、雲端證據或人類學習實驗。
兩個新樣本可以暴露新版方法的具體行為，不能估計一般可靠率。

本次 external task evidence：
`/private/var/folders/l6/44bf7nvs64j60f1mpyy88hdm0000gn/T/leetcode-route-closure-136buj7l`。
其中保存原指引、固定方法、任務／問題、首稿／定稿、實際失敗、native captures 與 Schema readback。
既有 Islands 缺項維持原貌。以下是新版兩份首次交付的實際結果。

## 首次交付與 Reader 結果

完整英繁正文：

- Daily Temperatures：[英文](../evals/writing/leetcode-route-closure/temperatures/article.en.md)、
  [繁中](../evals/writing/leetcode-route-closure/temperatures/article.zh-TW.md)。
- Subsets：[英文](../evals/writing/leetcode-route-closure/subsets/article.en.md)、
  [繁中](../evals/writing/leetcode-route-closure/subsets/article.zh-TW.md)。

兩位 Writer 都在私有 review 從最終正文列出實際提出的方法，定位條件、state、操作、正確性及各自成本的支持段落。
Daily Temperatures 包含 direct scan、pending-index stack 及改成至少同溫的 adaptation；
Subsets 包含 recursive enumeration、iterative doubling 及 exact-size pruning。
這是本次可觀察到的作者動作；不是與舊文的受控因果比較，也不保證重建已完整。

兩位 fresh Reader 各回答同一組八題，均保留 `cost` 缺項，其餘七題未標缺失，未回報實質英繁不一致。
這個「七項未標缺失」是 Reader 的回報，沒有換算成文章品質分數。
兩個新題型仍未達到完全 Zero Context 的驗收；不可把它們算成兩次成功或宣稱方法已穩定。

Daily Temperatures 的正文說明了每個 index 入列一次、最多移除一次，以及 resizing 的 spare capacity／shrink gap。
Reader 能重建主法、比較法與改題後 71 個 pending 上限，但正文把「geometric sizes 的總和為最大容量固定倍數」當成前提。
它沒有用容量序列或界線解釋該級數，讓只有基本 Python syntax 的讀者仍須從外部補知識。
這是新的成本先備知識缺口，與舊 Islands 完全缺少變體成本鏈不同；相同的整篇理解目的仍未達成。

Subsets 的正文推導了葉節點、呼叫數、總複製 entries、三個方法與 output／auxiliary／transient conventions。
Reader 的具體疑點是：正文對 growing sequence 的 append 分攤，沒有說明如何涵蓋 shared path 的 append/pop 交錯。
它另列出 pop、len、index 等 primitive cost 未明說。Owner 不將這些全部擴張成必要的 CPython internals 課程：
文章已有 list-reference-operation 與 call-state 計數模型，採明確模型本身可以成立。
但 append-only 到 mixed end operations 的前提重用，沒有可定位的本文橋接，這個較窄的缺項成立。
也可以另給足以支持最終上界的較粗成本論證；本文沒有提供那條替代推導。
目前證據沒有證明程式或 Theta 結論錯誤；它證明本次作者核准仍早於目標讀者可從正文補齊成本前提。

兩例共同指出下一個待解問題：支持段落的存在，仍可能只是被引用的結論，未必能從宣告的讀者前提推導。
現有方法已要求推導 amortized 等新成本，不宜把本輪失敗再簡化為「缺少一句規則」。
本次不在看到 Reader 答案後改動固定方法、偷偷補稿或抽新題重算首次成功。
後續若修改自審如何驗證這種先備推導，須保留本輪版本並綁定新的 consumer，不能沿用本輪結果認證新版。

## 首稿、修訂與失敗

[完整 evidence packet](../evals/writing/leetcode-route-closure/README.md) 保留兩篇 first complete English／Traditional Chinese、
作者修訂、實際 runtime、原始 Reader 回覆與引文核對。
Subsets 作者在翻譯對照時發現英文把 include/exclude call tree 錯稱 binary search tree；
保存當時已審核英文，修正術語與包含關係、重新審核英文，再修對應繁中。
所以實際時序是每個被翻譯 edition 都先經作者核對，不能宣稱最後英文早於任何繁中產生。
這是作者交付內修訂，不是收到 fresh Reader 後修稿。

Subsets 的共享 mutable list 錯誤示例有真實 AssertionError；兩題的刻意錯解 controls 與正解 controls 分開。
來源定位失敗、讀取輸出截斷後補讀、錯誤 sed range 的空輸出，以及 inline-expression sequence 不同的機械觀察都保留。
後者源自中文語序與兩個額外 backtick 標記，不等於語意缺失。
Schema 首輪錯引文與真實拒絕也保存，沒有刪除後只留 PASS。
根觀察者的無效 script interpolation 未執行檔案寫入，修正後重跑；摘要見 packet 的 observer notes。

另做一個刻意刪除控制：從 Daily Temperatures 英繁各刪除一段 list end-operation cost model，
保留程式、操作次數、公式與 adaptation；預期放在 Reader 看不到的位置。
第三位 fresh Reader 只讀被修改的正文與同一 cost 問題，也標記成本前提缺失。
這是 planted sensitivity control，不能計為自然 Writer 失敗、已校準 evaluator 或可靠率。

## 可重播的驗證與界線

父 Session 從實際英繁正文抽出五段完整程式，兩語相同，執行獨立 problem-definition oracle：

- Daily Temperatures direct scan：3,285／3,285；
  stack solution：3,288／3,288，包含三個 100,000-day 邊界。
- Subsets recursive 與 iterative：各 330／330；
  exact-size：1,647／1,647，包含合法 k 與 n=10 邊界。

共 8,880 個程式比對通過；quadratic scan 沒有跑 100,000-day 控制。
這些是程式測例數，不是模型 run 數。
共 115 段 Reader 引文均為指定正文的逐字連續片段；原始缺項維持原樣。
code blocks、來源 URL 順序及五組 English interview recall 在兩語保留。
verify-medium doctor 只驗來源／註冊，不能充當全文 behavior 或網站發布驗收。

Schema 2 的實際 readback 為 VALID、SUPPORTED、10／10 reported fields PASS，
已按原 next `consume_verified_behavior` 消費；沒有 argv 就不發明命令。
它只檢查兩個 Writer 的五項操作回報，workflow decisions 明確為 null，且 `authorizes_landing=false`。
因此不能抵銷兩個 fresh Reader 的成本缺項，也沒有取得 merge／deploy 授權。

native requests、thread IDs、tool responses 與 capture audit 留在外部 evidence；repo 保存可重播內容與 session manifest。
App capture 有每項 20,000-character 上限，部分 Writer／Reader 項目被截斷；
不能由 capture 截斷推論當時模型收到的工具輸出一定被截斷。
各 Writer 自己記錄的讀取截斷及補讀，與 observer capture 限制分開。
共享 filesystem、不可見 web event 與未強制隔離讀取是本輪限制。

本輪結果是「通用自審動作已有實例；完整 Zero Context 仍不通過」。
保留 P-class 的語義決定、formatter 的排版與 CLI 的 bytes／順序責任；
CI 只重播程式與證據結構，不做新模型裁判、不計算非必要 SHA-256，也不把缺項強制改成 PASS。
