# Four-Pass 與文章的組合

本 recipe 接在來源研讀與雙語語意核對之後。**新的 alg-four Lesson 必須涵蓋本篇完整文章的每個工程決策與核心 Runtime 機制**，而非只選一個決策。若來源無法完整讀取，標記未涵蓋部分並拒絕宣稱 Full-article lesson 已完成；不得為了短 lesson 偷偷刪除內容。原已 Frozen 的 CEFR 技術 Lesson 使用歷史來源與其原本單決策契約，不追溯修改。

## 取得完整依賴

**新 Lesson 的 Semantic Owner** 是 [alg-four](../../alg-four/SKILL.md)；依 [完整文章契約](../../alg-four/references/lesson-contract.md)、[Thinking Route](../../alg-four/references/thinking-route.md) 及 [Consumer Migration](../../alg-four/references/migration.md) 取得本次 Scope、全部 Decision Coverage、Passive/Active 雙角色及必要思考操作。

[CEFR skill lock](../../../../references/upstream/cefr-alg-skills-lock.json) 仍精確驗證**歷史 Frozen 來源** `ed3c/cefr-alg-c2-plus` 的 12 個檔案；不得以新 Owner 當作理由修改該 Lock 或 Vendored Bytes。

- [alg-vocab-encounter](../../alg-vocab-encounter/SKILL.md)：沿用原版 Passive lexical encounter 子流程。
- [cefr-alg-four-pass](../../cefr-alg-four-pass/SKILL.md)：**Legacy** frozen lesson、原技術 UI 與原 Oracle Gate 的歷史 Compiler，非新 Lesson 預設 Owner。
- [alg-explainer-video](../../alg-explainer-video/SKILL.md)：原版 Frozen Lesson 影片 Renderer；新格式先需證明其 handoff 相容，不可直接宣稱原 Renderer 接受新的 alg-four package。

沿用當前 host route，Local 讀本次 checkout，Cloud 透過 GitHub 讀本次精確 ref。
不要求安裝全域 skills、切換另一個 repository 或先啟動模型。先執行原 skill 的 doctor；
它核對 vendored bytes，不能證明語意或 Hypit 可用。

完整讀取每個所選入口要求的 references。相對引用以該入口的目錄解析，不能以 shell
cwd 解析。新 alg-four Lesson 必讀其 `SKILL.md`、`references/lesson-contract.md` 和 `references/thinking-route.md`，Legacy Frozen Lesson 使用原 Compiler 的 `references/four-pass-contract.md`、`references/execution-protocol.md` 及 `features/README.md`；有影片要求仍先讀原 Renderer `references/handoff-contract.md` 並判斷新格式是否相容。
需要變更 consumer 時也讀其 feature map 指向的相關內容。保存實際讀取的
repository、revision、path 與 byte hash。只讀入口名稱或搜尋摘要不算載入依賴。
若某個必讀檔案不可取得，列出該檔案與受阻步驟，繼續不依賴它的研讀／文章工作；
不能宣稱該 lesson 或影片已完成。不要建立空 wrapper 或複製上游指令來掩蓋缺件。

## 執行次序

1. 依 [article-assembly](article-assembly.md) 從原始來源建立英文推理稿與繁中稿，
   保存每個決策的 actor、condition、negation、evidence、uncertainty 與 consequence。
   先列實際目錄／symbol tree，再畫決策心智圖與一個具體輸入的 runtime 資料流。
   目錄只表示包含關係；圖中的執行順序須由 code 或來源支持。標明 observed、proposed
   或 source-reported，並區分教學主題的 runtime 與文章／影片製作流程。
2. 執行 compiler，選本次學習目標與有來源支持的最小 lesson。保留 STE-inspired
   clarity 與 C2+ precision 兩種英文表示，再核對繁中；清楚寫法不能刪除限制。
   依 alg-four 覆蓋**所有**工程決策與底層 Runtime，為每個 Decision 設 Passive Context 與至少一個可對照 Oracle 的 Active English reasoning cue；Passive 詞彙可以與 Active reasoning 的核心概念重疊，但不是每個單字都要生成。用 Thinking V2 選必要的 Pass 4 主要操作，僅對會改變教學選擇的可反駁新問題啟動 V3。保留來源 Actor/Conditions/Negation/Invariant，避免筆記漂亮但學習題無法重建 Runtime。
3. 回到完整來源對照逐項 Decision Coverage 與相反解讀，產出獨立於 Medium 文章的英文學習 Lesson／網站 Preview；記錄 Source Identity、全部 Decisions、跨語言 Claim Fidelity、四遍來源對應、Active Cues、Oracles 及未完成的人類嘗試狀態。將必要的 Source Claims、英文 scripts、原始 Code、visual anchors 與輸入來源固定版本。**僅文件型 Preview** 可以使用自我展開的 Oracle，不以此宣稱既有原生 CEFR Attempt Gate 已接受或執行。
4. 任務要求影片時，執行 renderer。使用使用者指定的 Hypit checkout 或該 host 可用的
   既有 Hypit skill/runtime，先讀其實際 contract 與版本。
   將 frozen package、supplied narration 及 anchors 交給 Hypit。Renderer 發現語意問題
   就回交 compiler，不在 animation 或字幕中私改。保存 editable project、render 與
   claim → narration → visual change → consequence 對應；實際播放、暫停、seek，
   檢查否定、條件與 uncertainty 是否仍可見。缺 word timing 時只稱 semantic timing。
5. 完成原文章編譯與 [verify-medium](../../verify-medium/SKILL.md) 的 matching drives。
   接入既有網站時按 [website-delivery](website-delivery.md) 驗收實際頁面與版本。
   來源 snapshot 匯入與 skill 讀取是兩件事；更新網站 lock 不等於載入了 compiler。

已有同版 frozen lesson 或已驗影片時，先核對其來源、revision、bytes 與 correspondence，
直接消費仍符合本次需求的成果，不重編 claims 或重 render。若缺 narration，先指出
所缺 exact script／audio 與對應 owner；renderer 不自行生成新詞句或假裝音訊已存在。
有 script 而沒有 audio 時，依任務授權與 Hypit 實際能力處理，分開記錄 planned 與 rendered。

## Acquisition runtime 驗收

沿用 compiler execution protocol，不另建 LMS。Passes 1–3 保持 receptive，Pass 3 的
English transcript 預設可見，隱藏是選項。**既有 Frozen CEFR Runtime** 的 Pass 4 必須先有 oral-or-written attempt
acknowledgment 才能 reveal oracle。新的 alg-four 文字版是獨立的非追蹤 worksheet，無 Session Receipt；若要進入 Native Runtime，必須提供 versioned compatible consumer 與實際 Attempt/Reveal/Comparison Readback，不能冒用舊 runtime。文字輸入存在不等於 acknowledgment。
Reveal 與 comparison 是不同事件；看到 oracle 不證明 learner 已比較。
只有另外的 comparison report 才能進入 COMPARED，productive semantic practice 加上
comparison 才能進入 ACTIVE_PRACTICED。Shadowing 或 recognition 本身都不足以升級。

若任務修改 runtime，實際操作既有 UI 驗證拒絕、接受與 reload 路徑，保存下載 receipt
的真實 bytes。Receipt 記錄 session 事件與 learner reports，不能證明認知、retention、
pronunciation、mastery 或 CEFR。無真實 learner 時，把自動 UI 控制標為測試操作。

## 維護與證據

先固定依賴版本，再用保留的同一來源與 frozen package 做唯讀 correspondence review。
檢查所有相對引用能由該 revision 取得，並用一位 fresh consumer 實際讀此 recipe 決定
路由。提供原需求及來源，不提供預期答案；保存實際 request、讀取紀錄與輸出，另做比較。
至少涵蓋普通雙語 lesson、要求影片但缺少 narration、既有文稿的純連結修正。
不為 maintenance 重新 render、呼叫付費模型或發布內容。

分開報告 dependency read、source/bilingual review、semantic freeze、Hypit render、
UI event evidence、compiler mechanical results、independent review 與 learner evidence。
`verify-medium` 的綠燈不能代替其餘項目；本 recipe 也不新增語意 PASS 分數。
