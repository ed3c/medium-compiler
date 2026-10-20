# 作者英繁語意核對

核對者是文章作者；沒有獨立 Reader、翻譯 reviewer 或真實學習者。首份完整繁中 article.first.zh-TW.md 原樣保留。定稿 article.zh-TW.md 已完整讀回，code 三個完整 block 與英文逐 byte 相同，來源 URL 順序相同。

## 英文先審、再翻譯的實際時序

1. 完整英文首稿保存，執行 snapshot detector、閱讀 pattern 51/56 與 reader-article supplement，作者完成全文來源與 reconstruction 核對。
2. 第一份英文 approved edition 保存為 article.en.md；在 english-review.md 記錄 approval 後，才開始寫第一份完整繁中。
3. 英繁對照發現英文 exact-size 成本用了錯誤術語 binary search tree；未掩蓋這個作者錯誤，將該英文版本另存 article.before-translation-repair.en.md。
4. 英文改成具體 include/exclude 呼叫包含關係，並在首次接觸定義 power set。作者重新核對改動及其前提／成本，記錄再 approval，然後才修改對應繁中成為 final edition。這不是 Reader 回饋修補。其餘英文全文與已完成的翻譯不變。
5. 完整讀回繁中定稿，依以下三方法重新核對，而非只比較主程式。

## 方法與重要限制的實際支持段落

Recursive enumeration：英文 "All calls use the same `path` and `result` lists from their enclosing function." 對應繁中「所有呼叫共用外層函式中的同一份 `path` 與 `result` list，並沒有各自取得 private copy。」保留 object identity 邊界，沒有把共享的 path 說成每層私有。

Checkpoint 與復原：英文 "when `visit(i)` finishes, it must leave `path` as it found it" 對應「`visit(i)` 結束時，必須把 `path` 留在進入時的狀態」。Exclude 不動 path、include append、child return、parent pop 的順序相同。Leaf shallow copy 是新 list、相同整數 reference；兩版都說明不改 integer，不能把 shallow copy 誤譯為 deep copy。

失敗：兩版 [2] 最小合法案例均回傳 [[],[]]，兩 entry 同一 object；繁中「要求中的 `[2]` 消失了」與英文 "The required `[2]` has disappeared." 一致。Code runtime 確認這是實際可觀察結果。

主成本：英文 "The returned output uses `Theta(n * 2**n)` space, counting its outer references, inner list objects and element-reference slots." 對應「Returned output 使用 `Theta(n * 2**n)` space，計入外層 reference、內層 list object，以及 element-reference slot。」O(n) auxiliary 包括 path、active calls、transient snapshot，沒有翻成總空間 O(n)。n>=1 的公式條件、官方 n<=10、n=0 為額外防禦行為、大輸入 recursion/memory 假設都保留。

Iterative alternative：英文 "The stored count remains 2 even after the outer list grows." 對應「即使外層 list 變長，儲存的 count 仍然是 2。」保持 old_count 固定、concat 新 row、舊半不含 x／新半含 x 的 disjointness。英文 "It never copies the outer list: the old rows remain part of the final output." 對應「它從不 copy 外層 list；old row 仍是最終 output 的一部分。」兩版都分開 transient row O(n) 與把新 row 從建立起算作 output 時 O(1) control/singleton scratch 的 convention，沒有丟掉其條件。

Exact-size pivot：英文 "Even including all of them cannot succeed when `len(path) + (n - i) < k`" 對應「當 `len(path) + (n - i) < k`，即使把它們全部 include 也無法成功」。英文 "When `len(path) == k`, every remaining position must be excluded." 對應「當 `len(path) == k`，所有剩餘位置都必須 exclude。」保留兩個不同 early return 的原因與不改 path 的 restoration 前提。完整性重用句「每個大小為 `k` 的 subset 仍然有唯一的 decision route」及其 prefix 不可能性／強制剩餘 exclusion 推理均在兩版。

Pivot 成本：O(2**n+(k+1)*C(n,k)) 是 upper bound，並未宣稱每個 k 都 tight；C(n,k) 定義、snapshot-copy entry 數、empty-row object/outer-reference、O(n) auxiliary、k=0 constant work 及 k=n O(n) calls 均有對應繁中。新術語錯誤已在兩版改成原始 include/exclude 呼叫包含關係。

Interview English 五組問答逐字保留英文；closing master map 只連接已解釋的 membership、state、restoration、snapshot、output 成本與 pruning。無新增方案或代價主張。

## 機械核對與限制

完整 code blocks 及 URLs 相同。Inline-code sequence 比較為 false，已保留 bilingual-controls.json 原始差異。原因是自然中文語序、相同 x 加上 backticks；Counter 比較顯示英文 inline expression 沒有缺失，繁中多出兩個 x 格式標記。這個機械核對不是語意 PASS；上方才是作者實際核對的支持段落。

TRANSLATION_REVIEWED=author。沒有剩餘已知的雙語語意缺口；兩語一致本身不證明教學完整或讀者理解。
