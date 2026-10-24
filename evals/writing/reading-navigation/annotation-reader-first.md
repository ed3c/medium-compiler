# 獨立 Reader／annotation consumer 報告

結論：完整閱讀兩組 manifests 對應的四份英繁正文，逐段核對 83 則 notes 與 31 個 Active。沒有觀察到 notes 改變原段落的技術結論、條件、否定或變體成本，也沒有發現 article-wide unsupported Active 技術主張。以下另記兩個 paragraph-local 支援限制；它們不是程式或技術真偽錯誤，不能被改寫成「每個 oracle 的完整推導都只存在於綁定單段」。

## 先行條件

獨立條件見 criteria.md，寫於完整讀文與完整 notes/Active 檢視之前。審查先核對實際 blob／段落身份，後做人工語義判斷。quote／sentence 的字面存在不替代語義審查。未讀作者 evidence、自審或其他 Reader；沒有期望答案。沒有修改 repository 檔案、branch 或 commit。

## 機械觀察（不等於語義 PASS）

- Container With Most Water：英繁各 43 prose paragraphs、9 headings；annotations 0..42 無缺漏／重複；14 Active。
- Course Schedule：英繁各 40 prose paragraphs、8 headings；annotations 0..39 無缺漏／重複；17 Active。
- 四份 source 的 git hash-object 全部等於 manifest git_blob；83 個 english_source 等於對應完整英文 paragraph 去除 Markdown inline/link 標記後的文字。
- 31 個 Active 的 quote（忽略大小寫）及完整 english_sentence 均在其綁定段落出現。這僅證明來源字面身份；語義仍按 criteria.md 分開評估。

## 逐篇判斷與具體來源

### Container With Most Water

83-row 詳細紀錄中的本篇 43 rows 均已讀。條件、算式、trace、移較高牆的最小反例、checkpoint、bounded arithmetic、list／range機制、peak-live space、非等距座標變體均保留。未觀察到誤導 note 或技術上 unsupported Active。

具體風險點核對：p11 原句 “Suppose height[left] <= height[right].” 及 “Because heights are nonnegative,” 的短牆與非負前提在 note 保留；p13 的 Active 句 “This is a bound on all its possible partners, not a prediction that the next wall is taller or that the next area will improve.” 沒有被 oracle 改成下一面積必改善。p27 原句 “This model counts work, not equal physical time for all Python expressions.” 與有界整數前提在 note／cue／oracle 相符。p36 原句 “This argument assumes coordinates arrive ordered and matched to heights; the function neither sorts nor verifies that different contract.” 的契約限制、O(n)／O(1)以及supplied input歸屬皆未被改錯。

局部支援觀察 L1（非技術錯誤）：Active container-with-most-water-A0014 綁 p35。p35 的原句是 “Strictly increasing coordinates ensure that moving either endpoint inward decreases physical width.” oracle 另說 “ordered and matched to the heights”。ordered 可由 strictly increasing 重建，但 matched to heights 的明示來源在 p33：“Suppose the input supplies strictly increasing integer coordinates x, in the same order as height, with 0 <= x[i] <= 1000000000.” 因而這個 oracle 保留了全文正確限制，但不是所有前提都在 p35 單段明寫。它沒有擴張成立範圍，也沒有不當省略配對前提。

### Course Schedule

本篇 40 rows 均已讀。edge direction、isolated course、自迴圈、finite-cycle converse、獨立inner lists、mutable references／immutable counters、無maxlen deque、at-most-once、完整dependent-list checkpoint、deque與append不同成本、O(V+E)、重掃描與回傳order變體均保留。未觀察到誤導 note 或 article-wide unsupported Active 技術主張。

具體風險點核對：p18 原句 “The checkpoint is just before each evaluation of while ready, after all updates for the preceding completion.” 與 p20 “The checkpoint holds again after the whole dependent list is processed, rather than midway through it.” 對應 note／Active 沒有把半輪狀態當 invariant。p25 的 constant endpoint cost 保留 fixed-size block allocation 被視為 bounded work 的模型前提。p27 原句 “It applies here because each adjacency list only grows by one appended item at a time; no alternating deletion or bulk update is being smuggled into the argument.” 保留 append-only 限制。p32 的 O(V(V+E)) time／O(V) peak auxiliary 與既有 E input 排除、p34 成功output／失敗partial-order temporary storage，均與繁中對齊。

局部支援觀察 L2（非技術錯誤）：course-schedule-A0013 綁 p26；其完整 Active 句精確來自 p26：“CPython v3.14.0's list resize policy reserves spare capacity on single-item growth, roughly one eighth of the requested size beyond the items, with small rounding and padding.” p26 也說 “A growth may copy the old references, so one append is not always constant work.” oracle 的 “It spreads occasional resize-and-copy work over an append-only sequence” 與來源機制相容，但完整分攤推導是在 p27，原句 “Charge the cost proportional to m of that growth across those following appends; each receives only a constant charge.” 因而 term／quote／sentence 的 p26 身份成立，不能據此宣稱完整攤銷推導已在該單段給出。這不是宣稱每次 append 都 worst-case constant；oracle 保留單次可copy的限制。

## 限制與實際讀檔

本報告判斷 notes／Active 對指定原文的忠實度，未外查 CPython 或 LeetCode 版本真偽；未測瀏覽器呈現、可用性、scrolling 或頁面顯示出的全部字串；未觀察人類理解、回憶、發音或學習成效。純全文來源忠實度與段落來源身份不能替代這些證據。沒有 Provider 或其他發布動作。L1／L2 表示相鄰段落提供明示前提／完整推導；若要求所有 oracle 僅用一段且禁止任何上下文，這兩項不能被當成單段自足證據。

實際讀檔：
- .agents/skills/alg-four/SKILL.md
- .agents/skills/alg-four/references/lesson-contract.md
- docs/bilingual-articles.md
- references/learning/alg-four-container-with-most-water.json
- references/learning/alg-four-course-schedule.json
- articles/leetcode-11-container-with-most-water.en.md
- articles/leetcode-11-container-with-most-water.md
- articles/leetcode-207-course-schedule.en.md
- articles/leetcode-207-course-schedule.md

產物位於 /tmp/reading-notes-reader-h1a34smn/：criteria.md、mechanical-and-source-record.json（完整逐段來源／notes／Active與機械檢查）、semantic-review.json（83個逐段人工判斷及31個Active判斷）、report.md、outcome.json。初始 criteria 的 tempfile 另留在 /var/folders/l6/44bf7nvs64j60f1mpyy88hdm0000gn/T/reading-notes-reader-h1a34smn/criteria.md；內容相同，正式交付副本位於 /tmp。
