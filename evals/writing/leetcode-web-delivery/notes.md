# 索引 metadata 交付紀錄

本次依 task.json 的選定範圍，完整讀取三份指定規範及兩篇文章的完整 English、Traditional Chinese editions。交付的是已審正文的 website-ready 索引資料；既有正文的核准前提來自任務，不是本次重新產文、翻譯或獨立文章審查所得。

index-entries.json 採兩筆明確 registry entries，每筆同時包含雙語 title、description、既有 source paths、穩定 slug，以及 bilingual=true、download_markdown=true。四個 title 均逐字取自對應 edition 的唯一 H1；source 與 english_source 均直接保留任務給定值。Metadata 沒有寫入正文。

## 描述的正文依據與核准範圍

- Container With Most Water：雙語描述對應面積公式、較短牆的捨棄不等式、完整狀態追蹤、loop invariant、Python reference code、成本推導，以及 strictly increasing coordinates 的改版。描述只概述這些既有內容，沒有新增測試結果、圖像或狀態。
- Course Schedule：雙語描述對應 after adjacency lists、remaining indegree、unbounded deque、逐步釋放課程、Kahn's topological sort 的 cycle 判定證明，以及 deque/list.append 的成本與 repeated-scan alternative。描述沒有把 Boolean 判定誤寫為回傳完整 schedule。
- 本次已將兩組描述與所讀完整雙語正文逐項比對，核准它們作為本次 metadata handoff。公開描述沒有 evaluation/process 或 learner mastery claims。這項比對不是獨立讀者證據，也不建立新的正文核准歷史。

## 保留的內容限制與證據邊界

Container 的成本推導限於正文聲明的 bounded-integer、unit-cost model；座標改版假定座標已 strictly increasing 且與 heights 對應，不進行排序或 contract validation。Course Schedule 的主解法回傳 Boolean，FIFO 不保證最小編號順序；其成本推導依正文的 bounded-scalar 與 container cost model。這些限制仍保留在完整正文，索引短述不取代它們。

本次僅以四份指定正文支持 metadata，沒有查核外部來源或執行正文程式；沒有新增 sloptrim、translation review、CLI validation、runtime tests、independent reader、images、website build/browser verification 或 Provider publication 的 PASS。既有原稿、修補、review 與 failure evidence 不在本次可讀範圍，不能由 metadata 推定其執行結果。

四份 supplied bodies 均未改寫。尚需 site builder 依既有 bilingual website contract 註冊條目、原樣接入正文，並另行驗證文章清單、雙語 routes、各語 heading navigation、language switch 與 exact source downloads。本交付沒有執行上述網站工作，也不授權 merge 或 deployment。
