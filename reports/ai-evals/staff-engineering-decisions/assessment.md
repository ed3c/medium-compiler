# Staff Evals 工程評估：這次測試修補，哪些判斷值得保留？

這次 coding agent 做對的關鍵，是找出測試已過時的假設，再修正那個假設，同時保留原有證據檢查。網站原本只有一份報告，測試便把數量寫死為一；新增第二份報告後，程式正常產生兩份結果，測試卻失敗。Agent 改為依報告目錄（catalog）檢查應交付的路由、數量及內容，讓測試重新對應產品需求。

這個案例可支持局部的 Engineering judgment 與 Debugging quality 判斷。證據包括失敗重現、Agent 當時寫出的理由、patch、局部測試結果及同一 commit 的 CI 結果。它仍不足以判定整段 agent workflow 的品質，也沒有重新驗證先前 Soodles 報告引用的全部實作。

本報告採 `combined` 模式：同時檢查所提供的程式變更，以及部分有紀錄的 Agent 決策。主案例是 `ed3c/medium-compiler@e30508d0f78a98a225e72f8c9e13273ae0582b25`。被觀察的執行者為 AI assistant `/root`，使用 ChatGPT Work、GitHub connector 與 shell tools；精確 model 未知。另一份 Soodles 原始碼審查見下方附件。

這是既有英文評估的繁體中文語意改寫：技術識別保留 English terms，並展開判斷成立的條件。英文原始輸出、case records 與當時的 capture 均保留。本次改寫沒有新增 coding-agent 實驗、人類校準（Human calibration）或職級認證。

## 發現一：修正數量假設，保留真正需要防止的退步

原測試使用 `len(provenance) == 1`。這裡的 provenance 是每份報告交付後留下的來源識別紀錄。新增第二份報告後，局部重現得到 `2 != 1`，也就是實際回傳兩筆，測試卻只接受一筆。證據位置是 `before-test.py:28` 與 `observations.json` 的 e3。

Agent 在改動前說明：要逐份驗證 catalog 中的報告，並保留歷史報告原有的檢查（e4）。這個理由與 renderer 的實作相符：`render_reports` 本來就會走訪 `catalog['reports']`，為每份有效報告產生一筆 provenance（`ai_evals_site.py:44–89`）。因此，只有一份報告是早期測試資料（fixture）的狀態；它不是 renderer 必須維持的產品契約。

修補後，測試以 `/ai-evals/<id>/` 為索引建立 `expected`，同時比較路由集合與數量，再核對交付的 report、assessment 雜湊及首頁連結（`after-test.py:28–40`）。只比較集合會漏掉重複項目，因此仍須檢查數量；renderer 自己也會拒絕重複 ID（第 55–57 行）。這些檢查的用途，是找出漏交、重複交付或內容與宣告來源不符。

測試與產品使用同一個 `checked_file` helper 讀取來源。這能支持交付位元組與宣告雜湊的一致性，卻不能當成對整套 hashing 實作的獨立驗證。共享 helper 可能共享缺陷，判斷時應保留這個限制。

原歷史報告的專屬 assertions 仍在第 41–53 行：沒有新的 coding-model 執行、沒有完整平台 transcript、保留六筆 observations、人類校準為 `NOT_PERFORMED`、assessment 與 provenance 的雜湊一致、當時的英文 article 標記、證據涵蓋文字及歷史報告連結。provenance 的查找方式由陣列第零筆改成指定路由，移除了不必要的順序依賴。第 15–22 行的 stale-source 與 path escape 拒絕檢查也未變動。

當時的靜態 AST 比較找到：原版 12 個 assertion calls，新版 16 個，其中 10 個原有 calls 完全相同；兩個改動分別是取代「只有一份」的假設，以及改用路由選取歷史報告後比對雜湊。因此 `original_report_checks_preserved = true` 指的是保留原報告的實質檢查，不包括那個本來就該替換的數量假設。

**工程判斷：保留這個修補。** 假設只把條件改成 `len(provenance) == 2`，這次雖會通過，下次新增報告仍會失敗；若直接刪掉數量檢查，又會減少對遺漏與重複交付的保護。依 catalog 推導期望值增加了少量測試邏輯，但符合此處以 catalog 定義交付集合的責任分工。反例是產品真的要求「永遠只有一份報告」；在那種需求下，固定數量才有意義。另外，catalog 比對本身也不能證明 catalog 已收錄所有使用者想要的內容。

封存的局部測試成功（e6）與相同 head 的 provider 成功結果（e7、`passed-ci-jobs.json`）支持這次修補。完整測試輸出未包含在此案例內，因此沒有逐條 assertion 的獨立執行證據。現有資料不支持再修改產品程式。

## 發現二：局部重現能區分原因；CI 綠燈要按實際範圍解讀

失敗的 provider 紀錄只指出 `Tests and real article drives` 步驟失敗，job 為 111437885547，沒有直接指出哪個 assertion 出錯。工作流程把 unittest 輸出導向 `tests.txt`（`writing-verification.yml:21`），所以只看到 exit 1，還不能判斷是 renderer 壞了，或測試的假設過時。

Agent 執行 `python3 -B -m unittest discover -s tests -p test_ai_evals_site.py -v`，得到數量 assertion 失敗、stale/path 測試通過的結果（e2–e3）。這個 focused check 提供了能區分原因的資訊；之後的 source inspection 與 patch 也相互支持。修改了測試假設後再跑同一個命令（e5–e6），是在確認修補結果，與沒有新前提的重複重跑不同。

接著，Agent 讀到 `e30508d0f78a98a225e72f8c9e13273ae0582b25` 的 CI 成功，才進行紀錄中的 expected-head merge（e7–e8）。這種 exact-head readback 把結果對回真正要合併的版本；更早版本的綠燈無法做到這一點。provider job JSON 可核對失敗與成功各自的 job/head；merge 與部署回讀在此仍只有協調者轉錄，沒有獨立原始平台紀錄。

另一個可行選擇是取得原 CI 上傳的 `tests.txt`，保留雲端執行脈絡來定位失敗。此案例沒有記錄那個 artifact 當時是否可取得、是否曾嘗試，因此不能把沒有採取這條路徑直接判為錯誤。在尚未找到 assertion 前反覆重跑完整 suite，則很可能增加工作量，卻沒有改善診斷；這是替代方案分析，沒有實際 A/B 成本比較。

工作流程還有一個容易誤讀的地方：它刻意接受 behavior-evals 的 exit status 3，並寫出 `BLOCKED: no fresh writer/reader experiment performed by this job`（第 23–28 行）。所以這裡的 CI success 支持機械驗證完成，不表示已做新的 writer/reader 行為實驗，也不表示 Staff-level 品質已通過。

**工程判斷：保留局部診斷與 exact-head readback，完成聲明則維持相同證據範圍。** 現有紀錄沒有出現相反的最終聲明可供指正。若還需要更精確地核對是哪個版本執行了哪些 assertions，最小補件是既有 run 的 `checkout.txt` 與 `tests.txt`，不需要先重跑整套測試。

## 發現三：Soodles 報告有具體取捨，但文字推理與實作查證要分開

先前的需求是審視 Soodles 的 Schema Manager、Test Manager、測試必要性、Code quality 與回饋路徑（`observations.json:7–8`）。已交付報告確實談到這些問題。例如，它說明修改 shared fixture 為何可能影響沒有改動的 consumers，也指出九個 refusal cases 不能只因 setup 很花時間就刪掉（`delivered-assessment.md:40–48`）。

這個分析區分了兩件事：成本集中在哪裡，以及那些成本是否可避免。它提出先拆開 fixture preparation 與能區分行為的操作，再判斷是否能共享 immutable setup。這是可以讓工程師決定下一步的 Architecture 與 verification 取捨。

報告也分清協調者提交 data feedback 與原 owner 在實際流程中接續執行的差異，並區分已知狀態的 projection 與未來 coding 成功的預測（第 19–23、58–72 行）。若把 `reviewed`、很快的 projection，或八個欄位符合期望，直接當成修復授權或優化成功，會跨越證據實際支持的範圍。

假設採用「刪掉慢測試」或「超過固定秒數就修復」，可能損失 refusal coverage，卻仍沒有證明原成本不必要。原報告主張回到 owner 與具體輸入做比較，並指出下一筆需要的觀察。這個可見的推理值得保留。

不過，這位 fresh reviewer 的輸入沒有包含原報告所引用的 Soodles source、原始 logs、projection payloads 及 frozen prediction。因此，它可以判斷論證是否清楚、前後是否一致，不能獨立確認那些實作、耗時、feedback 是否已被消費，或 prediction 是否真的先於結果固定。

原報告自己揭露沒有完整 implementer transcript，也沒有 Human calibration（第 5、80 行）。其中八項期望符合的敘述（第 64 行）屬於讀過原始碼後設計的局部 oracle check。即使這項結果經核對，也只支持那些欄位；所以 `matched_field_checks_establish_staff_quality = false`。

**工程判斷：保留具體的 fixture、測試必要性及 ownership 分析，對實作結論要求對應證據。** 若要讓另一位 reviewer 獨立確認其中一個重要主張，應提供那個 source branch、綁定同一版本的 runtime input/output，以及 owner 實際消費回覆的紀錄。原本沒有捕捉到的操作，不能回填成已觀察事實。

## 發現四：空白輪詢有改善空間，目前不能量化為浪費

事件 e9 記錄同一個部署回讀 session 的連續 `write_stdin` 回覆沒有新輸出，最後得到 `matched_files=10` 與 `provenance_matches=true`。這表示等待中的工作最終有提供有用的交付證據，等待本身合理。

短間隔 polling 若沒有帶回新資訊，可以考慮改成較長、仍有上限的等待，以減少空白呼叫；代價是較晚知道工作完成。這是尚未執行比較的改善方向。

此紀錄缺少精確呼叫次數、完整 timestamps、process command 與 token 用量，不能據此聲稱有大量不必要成本、stuck loop，或整段任務的速度改善。

**工程判斷：保留有限的效率建議，不把觀察缺口升級成缺陷。** 若這個等待真的成為成本問題，再取得該 session 的呼叫與時間區間，判斷哪些等待可避免。本次沒有修改 polling 或 production 行為。

## 實際執行路徑：測試到底驗證到哪裡？

這份測試呼叫 `render_reports(ROOT, out, page_stub, markdown_stub)`。renderer 先讀取 `reports/ai-evals/catalog.json`，透過 `checked_file` 檢查檔案是否留在 repository 內、SHA-256 是否符合宣告，再檢查 report ID 及 assessment、guide、audit 的來源。無效或重複 ID 會被拒絕；report 與 audit 的 repository/revision 不同時，也會在建立該報告輸出目錄前拋出錯誤（`ai_evals_site.py:51–65`）。

通過的報告會在暫存輸出目錄寫入 report JSON、archive audit、assessment、選用附件與 HTML，加入一筆 provenance，最後產生 index。這段函式的副作用是寫本地輸出檔，沒有發布網站，也沒有修改 Soodles。若中途發生 exception，可能留下先前已寫出的檔案；此測試用 `TemporaryDirectory` 限制其生命週期。整個 builder 如何復原，超出這段程式的檢查範圍。

本次失敗發生在 renderer 已回傳兩筆 provenance 之後：過時的數量 assertion 把結果拒絕。依 `patch-commit.json`，修補只改 `tests/test_ai_evals_site.py`，沒有改 renderer。新的 oracle 改為檢查 catalog 中每筆交付，並保留歷史報告的證據契約。由於 page 與 markdown callbacks 是 stubs，這個測試沒有操作真實瀏覽器、production Markdown renderer 或部署流程。

## 評估者本身也需要被檢查：一次來源推論的更正

原 reviewer 核對了九份 instruction files 與十一份 raw evidence files，全部符合 task 宣告的 SHA-256。實際 paths 與 digests 存在 `case.json`，instruction map 存在 `consumer-report.json`；task digest 為 `2af1b599b0321950a94b76f2b727f26eab27a318454f48c5dbe3f88ececdc135`。

但 reviewer 對指定 skill revision `bc68aa025a26124ccbf6a0afc94c380dad4af0be` 執行本機 `git show` 時失敗，exit 為 128。當時 checkout 的 HEAD 是 `ce5ed482e16917debb1f944c97d16b8afd0761bc`，選定的 skill files 是修改後的工作目錄檔案。它正確保留了「本機未能確認 commit binding」這個缺口，卻在部分輸出中進一步寫成「指定 commit 不包含這些路徑」。

**需要更正的是這一步推論。** 本機查找失敗，不能單獨證明遠端 commit 缺少檔案。協調者之後讀取 GitHub commit/tree，確認九個路徑都存在，而且 Git blob identities 與選定內容一致。這個後續證據解決了遠端版本歸屬的疑點；它不是 reviewer 當時已知的資訊。

英文原始 assessment、case、capture 與 `disagreements.json` 仍保留，另由 `candidate-provider-readback.json` 記錄後續查證。本繁中版本將當時觀察、過度推論與更正放在同一處，避免讀者只看到一個過時的結論。這也說明為何 evaluator 自己的輸出不能因為欄位通過就免於內容審閱。

## 如何閱讀證據與成本

這個案例的 trace 是協調者轉錄的部分事件 e1–e10，沒有完整平台輸出、所有工具呼叫或全部副作用紀錄。因此 `complete_trace_available = false`。可追查的局部決策仍然能被評估；缺失的段落不能用推測補齊。

Before/after tests、renderer 與 patch metadata 支持修補機制及 assertions 保留的判斷，但 reviewer 沒有新跑產品 suite。provider job JSON 支持 job/head 結果及時間，屬於封存 metadata，沒有完整 logs。先前 Soodles assessment 支持對可見文字推理的審查；它的底層證據不在該 reviewer 的輸入內。hash 與 AST 檢查確認檔案身分、語法及 assertion 差異，沒有衡量人類是否同意評估結論。

provider timestamps 對應失敗 job 11 秒、成功 job 20 秒；因為成功與失敗走過的路徑不同，不能當成效能比較。局部命令的歷史結果是 0.010 秒與 0.006 秒，並非本次新量測。model tokens、model time、整體 task-handling time、human review time 與 repair time 仍未知。

七個職缺面向各有不同涵蓋程度：前兩項 findings 支持局部 Engineering judgment 與 Debugging quality；patch 與報告的可見取捨支持部分 Architectural thinking、Reasoning clarity；第三項可用來討論 Communication quality；保留負向檢查與 exact-head readback 支持 Attention to detail。Developer trust 還需要更完整的流程與實際使用者回饋，不能由這個片段直接給整體評等。

## 參考 Hamel／Shreya FAQ，下一筆資料應如何累積？

Hamel Husain 與 Shreya Shankar 的 [AI Evals FAQ](https://hamel.dev/blog/posts/evals-faq/) 建議從真實失敗做 Error analysis，再選擇值得建立的評估；可確定判斷的條件使用 code assertions，需要主觀判斷的 evaluator 則與人類標註比較，並以未參與調整的資料檢查泛化。這是本報告採用的方法參考，不是他們對此案例的認證。

套用到這個案例，下一筆有用資料是 reviewer 的一項具體判斷與對應證據。例如先保留上述 provenance 推論錯誤：看到了什麼、原本下了什麼結論、哪個 provider 回覆推翻了它，以及修正適用的條件。不要把這一筆直接擴張成「Agent 經常搞錯 Git」，也不要在沒有代表性樣本前報一個錯誤率。

後續若出現相同類型的真實案例，才值得檢查能否用現有 provider 查詢消除這個判斷，或是否仍需要 evaluator。客觀的檔案身分檢查與需要工程經驗的 tradeoff review，應各自保留結果，避免六個欄位的 PASS 蓋過一個實際發生的推論錯誤。

目前已有兩個 retrospective cases 可供回顧，但沒有事前固定並在未知結果上驗證的新 prediction，不能計算 prospective prediction accuracy；也沒有 human labels 可計算 evaluator 的 TPR／TNR。完整 coding-agent trace、人類對重要 findings 的接受或否決，以及後續正常任務的結果，仍是下一階段需要累積的資料。
