# LeetCode 文章的推導粒度修正

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
這是本機觀察；Linux 修正結果仍須讀回新 head 的 CI，沒有放寬可見性 assertion。

## CI 的 SHA-256 範圍

文章與 browser CI 使用 `--no-deployment-manifest`，不計算部署專用全站 asset hashes。
Verifier 刪除沒有 consumer 的報告用 compiler／article／packet digest，並在同一唯讀 drive 重用完整性檢查。
Build 也移除未被消費的 ALG Four manifest／English report digest；transcript provenance 重用已由 context 驗證的 article digest。
Article import 直接比較 bytes，再重用原 compiler 已驗證的 receipt digest。
原來源鎖、真正被比較的 source bindings 與 stale-receipt 保護保留；deploy 預設仍可產生供遠端逐檔讀回的 manifest。
只有小型 literal `abc` fixture 驗證 deployment manifest 演算法，CI 不為此重新 hash 整站。

本次沒有執行正式部署。Matching-head CI 的實際結論與 artifacts 以該 PR 的 GitHub Actions readback 為準，不能從本文件或本機 PASS 推論遠端已通過。
