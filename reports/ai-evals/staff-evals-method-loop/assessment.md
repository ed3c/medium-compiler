# Staff Evals 方法修正：從任務結果回到工程判斷

這次修正的核心，是讓 Staff Evals 先回答使用者的任務是否完成，再解釋 coding agent 的工程選擇。測試通過、局部修補合理與整個交付完成，是不同的判斷。若只挑一段成功的除錯片段，報告可能正確描述 patch，卻沒有回答使用者最在意的結果。

原版 skill 已有 decision episodes（有證據的決策片段）、角色要求對照與成本責任分工。缺口在於流程第一步就選局部決策，case template 也沒有獨立欄位承載任務結果與資料用途。另外，網站正文已改用繁體中文，skill 和部分 recipe 仍要求英文。這些矛盾會讓下一位 reviewer 產出不一致的報告。

## 讓任務結果成為診斷起點

新版 Drive 先要求列明原始需求、允許的副作用、完成界線，以及結果是已達成、未達成或尚未觀察。之後才沿具體輸入追查 caller、條件、state mutation（狀態變更）、外部效果及失敗後的處理。這保留原本微觀的程式分析，也讓每項分析都能連回使用者的任務。

本次使用既有測試修補紀錄與 Soodles 原始碼，沒有重跑當時的 coding agent。前者能檢查「新增報告後如何修正測試」，後者能檢查成本資料如何被分類及呈現。兩者可回答的問題不同，因此各自保留 case record（案例紀錄），不合併為模型能力分數。

## 先區分資料用途，才談累積經驗

`experience-case.json` 新增可選的 `evaluation` object。`task_outcome` 保存完成條件、結果與證據；`first_observed_divergence` 保存第一個看見的偏差；`dataset_use` 說明資料目前用於單案審查、錯誤探索，或評估器驗證。歷史資料仍可讀，不會因缺少新欄位就被補成成功。

`case_review` 是可供回顧的工程案例。`error_discovery` 是用來探索可能失敗模式的樣本與原始筆記。`evaluator_validation` 則要有特定判斷準則、真實標記及適當分組的驗證資料。改一個名稱不能完成資料用途的轉換。`human_review`、`split` 與 `evaluator_validation` 預設保留空值，避免 Agent 自行填出不存在的人類審閱或 train/dev/test 分組。

這項設計直接服務經驗累積：下一次遇到相似問題，可以找回原始條件、自己的預測、實際結果與反例。但本次只有 AI reviewers，使用者的獨立預測仍未收集。回顧已知結果有學習價值，不能計入事前預測正確率。繁體中文報告也不能證明職缺要求的 English fluency；英文溝通必須用真實英文作品另外觀察。

## FAQ 如何連到現有方法

方法來源是 [Hamel Husain 與 Shreya Shankar 的 AI Evals FAQ](https://hamel.dev/blog/posts/evals-faq/)。Skill 的 reference 按原頁七個目錄保留導航，重點依序是目標、錯誤探索、評估設計、人工審閱、工具、上線及 coding-agent 應用。這是閱讀入口；實際 case schema 與 Soodles 分工是本專案的適配。

已知 contract（行為契約）由現有 code 或 owner oracle（判定依據）驗證。尚未釐清的工程品質問題才進入案例分析；真正的人類互動標記工作使用 `error-discovery`。若需要 model judge（模型評分器），再使用 `write-judge-prompt` 與 `validate-evaluator`，保留真實專家標記和未參與調整的資料。本次沒有建立新的 model judge，也不以文章中的樣本數建議作為每次 review 的固定門檻。

## 成本、抽象與自動修復仍由原 owner 負責

對 Soodles 的審查仍需指出是哪個操作發生成本，以及哪個任務需要它的結果。Test Manager 負責量測與必要性判斷；Schema Manager 依有效資料呈現狀態、依賴與下一步；真正改變狀態的 owner 保留執行責任。`elapsed_ms` 與 `projection_ms` 是本次讀取、檢查與投影的時間，不是未來外部行為的預測準確率。

抽象加上 lint 規則可以排除已知錯誤選項，但必須能指出它排除了什麼，並保留合理的合法替代方案。行數減少不足以證明設計品質，成本很高也不足以證明某項驗證多餘。只有觀察到缺陷或有證據的設計風險，才由既有 repair owner 在其權限內處理；這次沒有修改 Soodles runtime。

## 本輪驗證

兩位 reviewer 使用固定版本的十份指引，各自完成一份 assessment、guide、case、consumer-report 與 capture。兩份正文都先辨認任務完成的證據範圍，再說明程式機制和替代方案。測試修補案例保留了原報告的 assertions（斷言）；source-only 案例則把產品結果維持為 unobserved，沒有倒推出實作者的行為。

Schema Manager 先對缺少觀察的 selection 回覆 `INCONCLUSIVE`。補入實際報告與 capture 後，它回覆 `VALID`、`behavior.classification=PASS`，八個欄位檢查通過。協調者已消費 `consume_verified_behavior`，並另讀兩份正文檢查因果與反例。這八項是人工審閱、評估器驗證、事前預測資格，以及各案例的一項來源事實；它們不是八道 Staff 能力測驗。

這次正常回饋的 `elapsed_ms` 約 1.79 ms，`projection_ms` 約 0.043 ms。數值不包含模型產文或 subprocess 啟動，更不表示未來工作能在毫秒內完成。協調者的讀取程式起初把 behavior 當成字串，因而在 CLI 已成功後出現 assertion error；修正為讀取實際的 `behavior.classification`，直接沿用原回覆，沒有重跑同一提交。

捕捉範圍仍有限：capture 是 reviewer 自述，沒有完整獨立平台 transcript。source reviewer 初始搜尋曾看見其他目錄檔名；它回報沒有閱讀其他 reviewer 或 observer 內容。因此保留這項暴露，不宣稱檔案系統隔離。原始正文也保留少量文字瑕疵，沒有為了漂亮結果改寫 raw output。兩次使用只能支持這些案例上的觀察，不足以證明新版文字造成普遍改善。

## 如何繼續累積可檢驗的經驗

下一個尚未揭露結果的實際任務，可以先讓使用者記下預測、成立條件與能推翻它的證據，再比較實際結果與 reviewer 的理由。若涉及自己尚不熟悉的架構，先保留程式與替代方案，交由具備該領域經驗的人判斷有爭議的部分。每次只補足改變結論的證據，保留失敗和更正，而不是持續增加測試數量。

本輪交付的是方法修正、兩次 fresh reviewer 使用觀察及可查閱的原始資料。它不證明 wording 造成改善、不估計母體失敗率，也不宣稱使用者已達 Staff-level 能力。這些限制與案例一起進入 feature map，讓後續判斷可以修正它們。
