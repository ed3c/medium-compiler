# LeetCode 文章的推導粒度與通用產文方法

最終版方法的後續兩題首次產文，另見 [holdout 報告](leetcode-final-method-holdout.md)。
它固定本版方法，不沿用下方開發集的修訂結果：Intervals 八題可重建，Islands 保留 `cost` 缺項，未宣稱一般穩定性。

本次修正 complete-article profile 與 Group Anagrams 的 Part 7 完整英繁稿。
目標讀者懂基本 Python syntax，但尚未學過 data structures、Python runtime internals 與 complexity。
使用者提供的完整文章是內容及教學粒度的比較來源，不是正確性權威，也不是固定章節配額。
本次交付止於 PR 與 CI；不包含 merge、部署或 learner mastery 宣稱。

## 原始落差與修改位置

原文章已正確說明 tuple snapshot、key equality／hash collision 與 `O(M + N)`。
實際缺口是 `defaultdict(list)` 的物件生命週期，以及具體 logarithm／換底推導。
原文 Reader 引用了正文並對這兩處回覆 `NOT_STATED`。
這些是已觀察的文章落差；以下規則對歷史產文的影響是來源支持的風險判斷，不能冒充已取得的歷史 Writer trace。

- **把少數 algorithm decisions 推成少量教學步驟。** 一個決策仍可能需要 representation、輸入狀態、操作、回傳或 mutation、下一個 state 等解釋。修正在 [content profile](../.agents/skills/leetcode-mental/references/article-content-profile.md)。
- **把等價實作推成等價教學覆蓋。** 改用顯式 dict branch 不會取消使用者要求的 `defaultdict(list)` 機制。本版保留 `defaultdict(list)` 主實作，完整追蹤 MISS／factory／insert／return／append，以及 HIT 與 `get()` 的差異。
- **把同一術語再出現推成重複贅述。** 機制解釋、具體 trace、code 對照與 interview recall 各有目的。[本機 sloptrim supplement](../.agents/skills/sloptrim/SKILL.md) 的刪文審查必須保留讀者重建下一步所需的橋接；上游 pristine bytes 不變。
- **把標題或名詞覆蓋推成正文已解釋。** 完整比較文已由使用者提供，不能沿用「外部 Medium 不可讀」來忽略它；來源狀態及 [原始比較文](../.agents/skills/leetcode-mental/references/group-anagrams-user-reference.md) 已更新。
- **把 CLI／digest／detector 通過推成內容品質成立。** 原 CLI 仍只負責順序、位元組與已宣告 coverage。技術推導、雙語核對與 Reader evidence 保持各自責任。

工程指引審查沿 [狀態機修改契約](state-machine-change.md)。沒有新增 compiler stage、Writer Manager、學習事件或發布權限。
本機實際讀取 Soodles `review-writing/features/ste-reference.md`，採用 Issue 9 的 1.5–1.13 術語一致、3.6–3.7 動作者、4–6 節的前提及因果順序、9.1／9.3／9.4 原義保存原則；不宣稱正式 STE compliance。

## 新版內容與來源界線

[英文](../articles/leetcode-49-group-anagrams.en.md) 先完成內容與實際 detector／作者語義審查，再產生 [繁中](../articles/leetcode-49-group-anagrams.md)。
繁中保留完整 English Interview Q&A；兩份正文逐段對齊，Python／text fences、圖位及 URL 保持一致。
七張既有 SVG 沒有變更；caption 只描述實際圖義，未渲染的 figure specifications 沒有混進公開正文。

相對於使用者比較文，保留以下必要技術限定：

- 固定 alphabet 的 expected counting time 為 `O(M + N)`；全空字串仍有逐字串工作。舊版 canonical article 原已保留這點。
- Sorting 對不等長字串使用 `O(N + sum(k_i log(k_i + 1)))`；常見 `O(NK log K)` 簡寫明定 `K` 為 maximum length，並處理 0／1 長度。
- `tuple(count)` 建立獨立 snapshot，沒有讓原 list immutable；tuple 的 elements 必須各自 hashable。
- 相等 key 決定同組，hash 協助查找；balanced merge 層數是成本模型，不能冒充 CPython 的 exact trace。

Primary sources 是文章內的 LeetCode 49 contract、Python 3.14 `ord`／hashable／defaultdict 文件，以及 CPython v3.14.0 sorting note。
使用者比較文不是獨立擷取的 Medium body。English author review、翻譯 review 與機械控制亦不是 human learner observation。

## Writer／Reader 的實際結果

使用 Local Codex 原生 `collaboration.spawn_agent`，`fork_turns=none`，未指定替代 model。
所有實驗使用外部 task evidence directory，各 Agent 只獲指定輸入；共享 filesystem 並不提供強制 read isolation。
Parent 另用 native `read_thread` 保存可取得的實際 request／commands／output capture；單項輸出上限及截斷仍是限制。

第一對 Writer 因未在起稿前讀取 hidden `.agents` instructions，均為 comparison-invalid，失敗稿與 capture 保留。
新的 fresh pair 在起稿前讀取明列路徑；共用 task 與完整 reference 相同。啟動訊息的路徑列舉不同，不宣稱整份 launch prompt 位元組相同。

- Fresh baseline Reader 七題可由正文重建，沒有未答題；它另註明正文未明寫 `__getitem__` 名稱，但有 subscript／get 的行為差異。
- Raw treatment Reader 同樣找到完整 factory 與 sorting 推導，但將 `__getitem__` 命名橋接列為一題未完整回答。這是保留的 raw 結果，不改寫成零缺口。
- Content Owner 對照 Python 官方文件，明補 `groups[key] → __getitem__ → __missing__`。另一個 fresh Reader 僅複驗此變更邊界，回答完整；引文全部能逐字對回實際 article。
- Schema Manager 的原始欄位比較為 `VALID / FAIL`；具名修正後的單題比較為 `VALID / PASS`，已消費 `consume_verified_behavior`。這是 schema 1 的 consumer-report 欄位比對，`criteria.status=NOT_REVIEWED`，不建立語義自動評分或一般改善結論。語義條件由本次 owner source review 審查，不能將其混成 Schema 的認證。
- Transfer Writer 對 LeetCode 20 從 bracket nesting 推導 stack、pop、guard、prefix invariant 與成本，沒有套入 26 counters 或 canonical-key 演算法。執行了從實際文章抽出的解法與 grammar oracle；它仍是單一 transfer draft，未做發布、獨立 learner 或一般化效果驗證。

因此這次 matched comparison **不支持 instruction-only improvement，也不宣稱整體 scoped nonregression**。
可支持的是：舊 canonical 的具體缺口被補齊；raw treatment 的剩餘邊界被發現及修正；完整參考文與讀者前提不可省略。
沒有 Issue #12 closure、calibrated judge 或人類學習效益證據。

Native Writer IDs：baseline `01a159f9-a00c-7491-a16e-e91250b02598`；treatment `01a159fb-c118-7cb2-99f8-72d51f7754c6`。
Reader IDs：baseline `01a15a01-bd94-7250-81f3-9993caff168e`；raw treatment `01a15a04-fae3-7a60-9109-05ae7eaffb5b`；修正邊界 `01a15a09-7570-75d3-b3ec-66c218383770`。
原始任務、所有 attempts、實際 capture、detector、runtime、翻譯審查與 Schema snapshots 保存於本機外部 evidence directory：
`/var/folders/l6/44bf7nvs64j60f1mpyy88hdm0000gn/T/leetcode-depth-g7c93nxy`。
此本機路徑不是可攜式遠端 artifact；PR CI 自行產出它所執行的 mechanical／browser artifacts。

## ALG Four 與必要驗證

[新 sidecar](../references/learning/alg-four-group-anagrams.json) 綁定 139 個 source paragraphs、29 個 headings、七張圖與原有 14 個 Active IDs。
八個 source-derived concepts 分開 equivalence、alphabet、ord、dictionary/factory、snapshot、sorting、cost 與 correctness，不把五個舊 decision IDs 當成通用配額。
只加入八個有實際來源的 optional skeleton cues；沒有為每一段製造同一句摘要。
所有 notes 經作者與 owner 逐段核對；learner evidence 維持 `NOT_OBSERVED`，既有 CEFR 12-file lock 不變。

新文暴露了 Mode C 原本將原文括號／斜線與新增標記混在一起的問題。
`scan_reading` 現在只從原文匹配範圍產生標記，並 escape 原文；原文 `strs[:i]`、`M / N`、路徑或 HTML-like literals 不會被當成新增符號。
測試移除具名 markup 後，逐一核對全部 source paragraphs 及 concepts，保留真正的原文 punctuation。

本機實際控制涵蓋：從英繁文章抽出完整解法執行、literal grouping／multiplicity／input nonmutation、獨立 sorting oracle、main implementation 的 MISS factory object identity；ALG Four 的來源拒絕與 HTML recoverability；原 compiler 的 legal Stage 6 import／Stage 7 exact assembly／verify／check-receipt；真實 Chromium desktop／mobile 的 scroll、anchor、keyboard、七圖載入、outline 及 mobile overflow。
Compiler import 是對已新作成的核准 edition 做 exact admission，沒有把舊 code 改成新 code 偽裝成 prose-only copyedit，也沒有補造先前 Stage 0–5 的作者歷史。

PR 首輪 head `466a4b8` 的 run `39456225837` 在 Linux 的 mobile keyboard target 可見性檢查失敗；build、compiler 與 Chromium 安裝步驟通過，失敗 log／artifact 保留。
原 CSS 使用固定 `125px` scroll margin，沒有反映 sticky header 的實際高度。
現由 layout 繼承實測 header offset，scroll observer 使用相同的 header 邊界；原文 article DOM 不因此新增 style。
本機實跑一般 header 與加高 header 控制：header bottom 分別約 129.6／161.6px，target top 分別約 146.1／178.1px，均完整露出目標段落。
這是本機觀察；後續 head `86539e2c13ae1310e83620ec714a4a1d6bf4b617` 的 [run 39456908161](https://github.com/ed3c/medium-compiler/actions/runs/39456908161) 已讀回 mechanical-writing 與 browser-alg-four 均 success，沒有放寬可見性 assertion。這個 run 只涵蓋該 head。

## CI 的 SHA-256 範圍

文章與 browser CI 使用 `--no-deployment-manifest`，不計算部署專用全站 asset hashes。
Verifier 刪除沒有 consumer 的報告用 compiler／article／packet digest，並在同一唯讀 drive 重用完整性檢查。
Build 也移除未被消費的 ALG Four manifest／English report digest；transcript provenance 重用已由 context 驗證的 article digest。
Article import 直接比較 bytes，再重用原 compiler 已驗證的 receipt digest。
原來源鎖、真正被比較的 source bindings 與 stale-receipt 保護保留；deploy 預設仍可產生供遠端逐檔讀回的 manifest。
只有小型 literal `abc` fixture 驗證 deployment manifest 演算法，CI 不為此重新 hash 整站。

本次沒有執行正式部署。Matching-head CI 的實際結論與 artifacts 以該 PR 的 GitHub Actions readback 為準，不能從本文件或本機 PASS 推論遠端已通過。


## 從近成品反查通用產文方法

本次續修以目前接近成品的英繁文為觀察材料，保留其正文、七張 SVG 與 sidecar bytes。
文章的有效教學關係可遷移；題目的概念及章節順序不能直接變成所有題目的模板。
例如，character-to-index 的逐值推演說明「如何把陌生操作接到下一個 state」；tuple snapshot 的限定說明「representation 與 mutation 的差別」；factory 的完整路徑說明「expression 如何取得下一步使用的物件」；空字串的成本說明「如何用 boundary 揪出公式遺漏的工作」。
新的方法遷移這些動作，不要求下一篇也使用 counters、tuple、factory 或 logarithm。

最早的落差在原需求到 P-class：舊 profile 已列出成品應覆蓋的內容，但尚未交代沒有範文時如何建立連續推導。
先前 Writer pair 又同時得到完整參考文與題目專屬提示，之後另有人工作修補。它不能證明 profile 本身能產生同等成果。
因此本次補的是 [article construction method](../.agents/skills/leetcode-mental/references/article-construction.md)，並讓原 skill、profile 與 thin prompt 指向同一方法。
coverage list 保持驗收用途，沒有改成新的 compiler stage。

本機先讀取 repo 固定的狀態機修改契約，再從 Soodles Git main 讀回 commit `1f5bfbe19d553304ca2f60138fe2c22519d655dd` 的 [Thinking Router](https://github.com/ed3c/soodles/blob/1f5bfbe19d553304ca2f60138fe2c22519d655dd/.agents/skills/thinking-router/SKILL.md) 與 [Ambitious Route](https://github.com/ed3c/soodles/blob/1f5bfbe19d553304ca2f60138fe2c22519d655dd/.agents/skills/ambitious-route/SKILL.md)。
原本 Soodles 本機 checkout 較舊；沒有把它找不到 Ambitious 當成產品不存在，也沒有改動其 working tree。
這是手動讀取原文並套用方法，不宣稱原生 Skill-tool invocation、Loop admission 或另一個執行模式。

Thinking 指出「成品 coverage 不等於產生 reasoning 的方法」；Ambitious Depth 提議從 primary problem/runtime material 與讀者需要的依賴關係建立教學流程。
Thinking 再反駁「所有題目都應展開同一組 internals」：必須只展開會影響選擇、狀態、正確性或成本的機制。
Ambitious 接著指出單一異題 draft 仍不足以檢查範文依賴及雙語交付，於是選兩種演算法家族與一次同題重複產文。
兩條路由形成一份必要 delta，沒有把兩份完整 prompt 或五種方法清單加到 Writer task。

通用方法要求 Content Owner：

- 從成功條件及能分離錯誤捷徑的 input，推導需要保留和可以忘記的資訊，再選 representation。
- 往前追 input 到 return，往後追每個 operation 的必要前提，把缺口轉成先於使用的讀者問題。
- 用具體 operands、before/after states、return／mutation／allocation 解釋 material transitions，並讓完整 code、proof 與圖義一致。
- 從實際 operation 次數及保留物件推導成本，交代 assumptions、boundary、auxiliary/output 與替代方案。
- 只憑完整正文重建推導，先修最早缺失的前提，再進 English editorial review 與完整繁中翻譯；保留英文 interview practice。

這些是原 Content Owner 的 authoring actions。`medium-writing` 仍只格式化及沿原 CLI admission/assembly，`alg-four` 仍只讀 accepted source，沒有新增 Manager、schema、發布權或學習狀態。

## 沒有範文的實際產文與反例

三個 fresh 原生 Writer 都使用 `fork_turns=none`，只有明列的 instruction snapshots、官方 problem statement 與 Python 3.14 primary sources。
它們沒有 Group Anagrams 參考文、題目專屬解法大綱或其他 Writer output；所有首份英文、作者修訂、定稿、翻譯、detector、執行與失敗紀錄均保留。
第二次 Binary Search 與第一次使用同一語義 task、instructions、sources/tools，只改 output directory，避免共享寫入。
這是本機原生 consumer 觀察，不是 retained local runner 的六次 matched study，也不重標為雲端證據。

每篇英繁完成後，另給 fresh Reader 兩份正文與事前固定的八個 reconstruction questions；沒有提供 skill、作者 report、測試、答案或另一篇文章。
問題涵蓋 contract、state/checkpoint、新 input trace、錯誤路徑、proof/termination、operation-derived cost、changed constraint 及 bilingual relations。
Reader 必須提供 exact quotes，沒有前提就標 `NOT_STATED`。它是文章消費者，不是已校準的品質 judge 或 human learner。

| 首輪產文 | 實際推導 | Article-only Reader |
| --- | --- | --- |
| Binary Search | 從 sorted order 推導 inclusive candidate interval、排除中點、進展及 halving bound | 八題均可由正文重建，50 個引文逐字核對成立 |
| House Robber | 從合法 take/skip 推導 prefix optima、兩個保存值、覆寫順序及線性成本 | `cost` 有前提缺口；其他七題可重建，50 個引文逐字核對成立 |
| Binary Search 同題重複 | 自行產出 interval invariant、完整 trace、rounding/log 定義及 duplicate-boundary pivot | 八題均可由正文重建，66 個引文逐字核對成立 |

三個主解法另由 observer 從實際英文文章擷取，對照獨立 linear-index search／nonadjacent-subset oracle；比較次數依序為 1,148／5,461／1,148，包含合法 boundary controls。
input 不被修改，英繁 Python blocks 與 source links 也直接比對相同。作者另執行自己的 literal/exhaustive controls 與 runtime frame capture，不能與 observer 計數混加為不同樣本。
兩位原 Writer 的翻譯 inline-code 比對曾失敗：英文與繁中的句構改變了全域 span 順序。
保留原失敗後，作者改為核對 spans/multiplicity、完整 code fences、links 及 material passages；沒有把自然語序差異當成技術內容遺失，也沒有刪除 code 保護。

House Robber 的主要 bounded-integer 成本可以重建，但 caveat 引入未解釋的 bit length／bit-space，output 分析又使用未定義的 `ceil`。
這是正文仍有未交代的前提，不能拿解法執行通過抵消。
方法的修正因此要求：prerequisite check 同樣涵蓋 caveats、alternatives 與 output notation；新引入的符號或 technical qualification 也要先解釋，或用保留條件的平白文字表達。
這項修正不把 House Robber 的詞彙清單寫成下一篇的必備內容。

原方法與三份首輪產文保持不變。另有 fresh revision Writer 只收到原 House Robber 英文、修正後的方法及原 primary sources，沒有 Reader findings 或預期改寫。
修訂觀察與後續 article-only reconstruction 的結果獨立保存，不能覆寫首輪缺口或當成沒有提示的首次產文。
它自行補上 iterator、數值上界及 binary digits、回溯 `k == 1`、rounding/output 等四處橋接；主解法 code 逐字未變，先前 observer 的 5,461 次比較可按相同 code 重用。
新的 fresh Reader 八題複驗仍將 `cost` 列為缺口，67 個引文均能逐字對回文章：核心成本與新增符號已可理解，但回傳 indices 的替代方案引入 list indexing、配置／填格及 append，沒有交代這些新操作的成本假設。
因此方法再補上通用的 operation audit：alternative、reconstruction 與 output builder 新增的操作要重新清點，只有確實涵蓋那些操作時才能重用原假設。
後續只選定 cost prose unit 修訂與定點 reconstruction，不重跑未變主解法來冒充文字修訂驗證。
該 fresh unit Writer 依最終方法與 primary sources 自行補出 indexed read/write、配置、逐格填值、append 的 amortized 序列界、反轉與 peak/output space 的成本。observer 核對這是唯一 contiguous English section replacement，其餘英文與主解法未變，英繁 code 及 source links 相同。
另一個 fresh Reader 沿原問題中的 `cost` 與 `bilingual` 定點複驗，`unanswered_question_ids=[]`，未發現具體英繁落差；引文另由 observer 逐字核對。
它也明記 append 的整段成本是正文採用的 CPython 操作成本事實，並未推導 resize strategy；amortized 的序列意義已有解釋。不能把這項 reconstruction 當成完整 interpreter 實作證明。
兩次 `cost` 缺口不刪除，三次首次產文與兩次修訂不混成五個 first-pass samples。最終方法的新增規則經限定修訂 consumer 觀察，沒有重新宣稱三份首輪產文已載入最後一版。

## 回饋範圍與仍未證明的主張

本次沿 `review-writing` 與 `eval-audit` 對照實際文章、舊 task、原生 traces 與既有 criteria；STE 使用前述同一份 Issue 9 reference，保留動作者、必要前提、語義及執行狀態，不作正式 compliance 宣稱。
Schema 2 的 requirements 與 task output shape 先保存，再由沒有 Writer outputs 的獨立 native criteria reviewer 核對 exact requirement quotes。
原兩個 task 回饋為 `VALID / criteria SUPPORTED / consumer-report PASS`，已消費 `consume_verified_behavior`。
四欄只核對英文 review 先於翻譯、實際執行、是否讀 polished exemplar、是否 publication；不是文章品質分數。
文章重建、runtime oracle 與引文核對各自有證據，沒有從四欄 PASS 推論它們也通過。
修訂與最終 cost unit 另綁定各自實際 instructions、task、獨立 criteria review 及原生 capture，Schema 2 均為 `VALID / criteria SUPPORTED / consumer-report PASS`，返回的 `consume_verified_behavior` 均已消費。
cost unit 只比對三個適用欄位；未增加 runtime 欄位，也未為未改 code 重跑演算法。這些回饋同樣不認證文章語義或一般穩定性。

三次首輪產文橫跨兩個 family，並含一次重複生成，能暴露範文依賴及部分不穩定處，不能估計一般成功率或保證任意讀者完全理解。
目前沒有 matched improvement study、calibrated semantic judge 或人類學習觀測。
所有結果仍區分作者審查、獨立 consumer reconstruction、程式正確性、機械 CLI/CI 與發布。
沒有新資料能改變當前修正或驗證方案時，停止認知往返；沒有用「全部未知消失」當成無限遞迴的退出門檻。

本次 external evidence directory：`/var/folders/l6/44bf7nvs64j60f1mpyy88hdm0000gn/T/leetcode-method-y83v2dgo`。
其中保留各版 instruction snapshots、三份首輪產文、revision／cost unit、Reader outputs、實際 native captures、criteria/Schema snapshots 與 observer controls。
native capture 仍有單項 truncation，shared filesystem 沒有強制 read isolation；本機目錄不是遠端可攜 artifact。
CI 只執行既有指定 workflow，不啟動這些模型產文，也沒有為新方法加入任何 SHA-256 計算。
