# Subsets 首次完整交付報告

交付目錄：本 report 所在目錄。只使用 task.json、四份指定 instructions、snapshot sloptrim pattern/detector、自己的 output，以及允許的官方線上來源。沒有讀 repository/history、範文、其他 Writer、Observer、Reader、feedback；沒有啟動 model/subagent；沒有 Git/CI/provider 或 publishing 寫入。

## 已交付

- article.first.en.md：第一份完整英文，未覆蓋。
- article.en.md：作者審核的英文定稿，2,894 個 whitespace-separated words（此量是文件描述，非內容品質指標）。
- article.first.zh-TW.md：第一份完整繁中，未覆蓋。
- article.zh-TW.md：作者審核的繁中定稿，11,899 characters。保留 exact English technical terms、identifiers、數值與三份完整 code。
- verify.py／runtime.json：由英文定稿抽取完整 code 後實際執行；stdout/stderr、三個 extracted solution、alias negative control 與其真實 AssertionError traceback 都保留。
- english-review.md：final-body reconstruction，逐方法列條件、state、更新、結果、工作／storage、具體支持原文，新輸入重建及失敗例。
- author-revisions.md／translation-review.md：實際作者修訂與完整英繁核對，含翻譯階段發現的英文錯誤及其修正時序。
- sloptrim.first.json／sloptrim.final.json／bilingual-controls.json：實際執行的診斷，與語意判斷分開。
- output.json：指定的平坦 boolean 物件。

## 推導與 final-body review

從 [2,5] 的四種 membership 出發，[2,5,7] 的非連續 [2,7] 排除 contiguous shortcut；固定位置的 include/exclude 讓每個 distinct-value subset 有唯一 decision route。這導出下一位置 i、共享 selected path、獨立 saved snapshot。因為所有呼叫共用 path，必須證明 return restoration，再配合葉節點 copy。選 backtracking 讓 exact-size pivot 能解釋 safe early return；另提供無 recursion 的 iterative doubling 作實質比較。

因果脊椎：所有 membership 選擇 → distinct values 與固定位置 → next position + selected path → exclude / append-include / pop → i=n → independent snapshot result。反向檢查：要安全 pop，child 必須恢復 entry path；要讓 sibling 不互相污染，parent 必須撤回自己的 inclusion；要使 answer 不被後續 pop 清空，保存時必須 copy。

實際 final body 提出三方法，非由舊 outline 重建：main recursive enumeration、iterative prefix doubling、exact-size pruned recursion。所有方法的完整 state/work/storage reconstruction 與精確 body passages 均在 english-review.md；三者的繁中支持 passages 亦在 translation-review.md。這些都是作者自審，不是獨立 Reader 或學習效果證據。

一個代表性的 final-body 支持鏈："At entry to a call `visit(i)`, `path` contains exactly the included values among `nums[0:i]`, in input order." → "when `visit(i)` finishes, it must leave `path` as it found it" → "A new subset list can keep its entries even when `path` later loses an entry." 新輸入 [0,-1] 從 body 可推出 recursive [[],[-1],[0],[0,-1]]、iterative [[],[0],[-1],[0,-1]]，以及 k=1 [[-1],[0]]；均另在 runtime assertion 執行。

## Primary sources 與實際來源讀取

- https://leetcode.com/problems/subsets/ ：description、examples、constraints。Unique values；每個 subset 一次；any order；1<=n<=10；-10<=value<=10。沒有開 editorial/community solution。
- https://docs.python.org/3.14/tutorial/datastructures.html ：More on Lists，append／pop／copy 的行為與 shallow copy。
- https://docs.python.org/3.14/reference/simple_stmts.html#assignment-statements ：binding 與 object assignment，不是假設 assignment 自動複製。
- https://docs.python.org/3.14/tutorial/controlflow.html#defining-functions ：local state、recursive call；同頁 range 段落支援不含終點。
- https://docs.python.org/3.14/library/stdtypes.html ：sequence concat、range 與 mutable-sequence iterator 行為。另檢視 integer bitwise 文件，但沒有採用或撰寫 bitmask 方法。
- https://docs.python.org/3.14/library/functions.html#func-range 及 https://docs.python.org/3.14/reference/compound_stmts.html#the-for-statement ：range／for 的官方頁面讀取。
- https://raw.githubusercontent.com/python/cpython/v3.14.0/Objects/listobject.c ：list_resize 約 lines 97–174 的 proportional spare capacity；list_slice_lock_held 約 649–668 的 reference-copy loop；list_concat_lock_held 約 696–724 的兩段 copy loop；list_copy_impl 約 1097–1100。Exact v3.14.0 tag。

當時文件頁面標為 Python 3.14.8；實際執行為 CPython 3.14.6。文章把 CPython v3.14.0 作 cost-model implementation source，沒有冒稱實際 runtime 是該 tag 或 exact allocation measurement。手推 Program Movie 與實測是不同證據。

## English editorial 與時序

完整首稿後才實際執行 snapshot scripts/detect.py。首稿 score 15 / clean，flags 為 pattern 51 與 56；讀取其 pattern 定義後局部修改。Reader-article supplement 亦逐句實際檢查：保留具不同教學功能的 worked state、copy causal bridge、歸納證明、cost derivation、alternate storage convention、pivot witnesses 與 English interview recall。

作者於翻譯前完整讀回英文、完成 primary-source semantic review 與 reconstruction，記錄在 english-review.md。第一次完整繁中寫成後，英繁核對發現英文用錯 binary search tree；英文前一版已另存 article.before-translation-repair.en.md，作者先修正與重新 approval，才改對應繁中定稿。另把 power set 的定義補到首次出現處。完整時序透明保留於 author-revisions.md 與 translation-review.md。english_reviewed_before_translation=true 表示每個實際翻譯內容採用其先經作者來源審核的英文 edition；此值不宣稱作者第一次審核沒有漏錯。

最後一次 detector 實際執行是修正後 final English；score 0 / clean，character-layer counters 為 0。沒有對繁中跑 sloptrim。首稿到定稿 2,808→2,894 words，低於 1.25x；score 不是 semantic truth 或 authorship verdict。

## Runtime 實際結果

指令：python3 verify.py（以 absolute path 執行），exit code 0，CPython 3.14.6。

- 英文三份完整 solution code 實際抽出、parse／compile／exec；與繁中完整 code blocks 完全一致。
- 10 次 literal checks，包括 [2,5]、[0]、[-10,10]、[1,2,3] 與超出題目下限但明述支援的 []。
- 從 [-2,-1,0,1,2] 取長度 0..5 所有無重複 permutations，共 326 組 array；兩種 power-set 方法與每個合法 k 合計 2,283 次 oracle 比對。Oracle 用 itertools.combinations，未重用文章的 include/exclude 或 prefix doubling。
- 13 次 statement-boundary checks：兩種 power-set 方法的 n=10 且含 -10/10；exact-size 的 k=0..10。1,024 rows／5,120 entries 實際確認。
- 6 次文章與新增 reconstruction 的 exact-order checks。
- 每次比對檢查 output 類型、membership、無重複 subset、無共享 row object、input order、輸入未變。
- sys.settrace 實際觀察 [2,5] 的 7 次 visit entry／return，逐次斷言 return path 與 entry 相同，完整紀錄在 runtime.json。
- 刻意移除 copy 的 alias negative control，實際回傳 [[],[]]、兩 row 同 object；對正確 expected set 的 AssertionError 是預期失敗，traceback 獨立保留。未把負向控制失敗記成 production solution 通過。
- 對 [2,2] 額外實跑可見 duplicate membership，明標 out-of-contract；不聲稱支援 duplicate inputs。Repeated-call control 確認新呼叫不帶舊 result。

沒有 unexpected runtime failure。沒有因失敗修改 solution code 或重跑測試來覆蓋首輪。

## 真實失敗、診斷與限制

- 第一次把四份 instructions 合併輸出時工具顯示 truncation；沒有把截斷內容當作完整讀取，隨後單獨完整重讀 construction 與 sloptrim。
- 讀取 patterns 時一次 sed 使用 1180..1280，得到空輸出；rg 已找出正確位置，隨後改讀 503..575，完整讀到兩個 flags。該命令 exit 0、沒有可用段落，不冒稱第一次讀到。
- 作者自審移除泛稱 path=path.append 的 warning：在實際 nested function 中還涉及 local binding，原本聲稱的失敗次序沒有成立。首稿保留錯誤、修訂紀錄保留移除理由。
- 翻譯階段抓到 binary search tree 術語錯誤，首稿與修前 approved English 皆保留。
- Bilingual inline-code-sequence check 為 false，因中文語序及兩個額外 backticked x；英語 inline expressions 無缺失，完整 code 與 URL 相同。診斷原值與人工判斷皆保留，不捏造全項 PASS。
- 唯一真正被執行並失敗的 assert 是設計中的 alias negative control，完整 traceback 未刪除。

CONTENT_REVIEWED=author；SLOPTRIM_RUN=actual；TRANSLATION_REVIEWED=author；RUNTIME_TESTED=actual；CLI_VALIDATED=NOT_RUN；INDEPENDENT_READER=NOT_RUN；LEARNER_MASTERY=UNOBSERVED；IMAGES_RENDERED=NOT_RUN；PUBLISHED=NOT_RUN。

沒有要求 image assets，文章的具體 sequential trace 足以表達狀態轉移，未使用 figure slots。沒有使用 medium-writing compiler/assembly 或對外網站；本任務授權是完成指定文章檔案與證據。首次完整交付後停止，不接受 Reader 提示來覆寫這次交付。
