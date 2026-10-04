# 這次改了什麼

staff-evals 現在先評估實際工程決策：當時可得的證據、採取的動作、可見理由、結果、替代方案及下一個必要觀察。英文報告以一次真實的測試失敗修補為例，指出哪些判斷應保留、哪些結論仍缺證據。

案例一涵蓋 medium-compiler 前次 Soodles 報告交付中的部分決策；案例二只審視 Soodles 的 Schema／Test Manager 原始碼。第二個案例沒有實作者操作紀錄，因此不評分 agent 行為。兩個案例都已存入 feature map 的 experience index，保留適用條件、反例、未知成本與下一步；沒有把事後分析計入預測準確率。

版本查證有一項更正：原始評估者無法在本機讀取指定 commit，進而寫成「該 commit 不包含指令」。協調者後續讀取 GitHub commit/tree，已確認九份指令存在且內容一致。英文頁首附更正，原始輸出與分歧記錄仍保留，不回填成評估者當時已知。

Schema Manager 先回覆缺資料的 INCONCLUSIVE；提交兩份實際評估後，六個指定欄位得到 VALID／PASS，並已消費其 consume_verified_behavior。這只確認這六個欄位及檔案身分。報告內容另經逐項審閱，保留上述更正，沒有宣稱通過人類專家校準。

下方附件包含職缺逐項要求與 reviewer 動作對照、source-only 報告、原始案例、分歧處理與 Schema feedback。主要英文報告先呈現具體 finding，之後才列證據涵蓋範圍。完整 agent 紀錄、人類校準與真正的事前預測仍待後續正常工程任務累積。
