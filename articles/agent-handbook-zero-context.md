# Agent 不是一段 Prompt：安全修補背後的七個工程決策

支付服務依賴套件出現高危漏洞。團隊希望快速更新，又不能造成付款中斷。AI Agent 可以讀取 Repository、修改依賴、執行測試並準備發布；真正困難的問題是：**誰持有權威狀態？誰有權讓外部系統發生改變？什麼證據能證明修補真的完成？**

本文以 [AI Agent Handbook](https://github.com/aliyun/ai-agent-handbook/blob/a5028af381306fd0f65c11f56a18fcbbb814d4f8/02-build/README.md) 第 3–6、22–23 章為主要教材。這是**教學用的假設案例**，沒有聲稱已修復真實漏洞或完成部署。無須閱讀先前對話，就能理解每個技術選擇的限制、機制、Runtime 後果和反例。

## 先定義任務，而不是先選模型

假設支付服務的 Dependency Manifest 記錄了有漏洞的套件。使用者要求選出安全且相容的版本、維持既有付款功能、執行相關 Regression Test 與 Security Scan，並準備變更單。**Production Deployment 必須另有人工核准。** Model 可以提出 Upgrade Plan，但不能自行授權正式發布。若發布請求逾時，未知結果也不等於可以重送。

要理解這個任務，需要分開表示：`goal`、`source_revision`、`selected_dependency`、`constraints`、`stage`、`observations`、`effect_authorization`、`unknown_effects`。這些只是解釋用的 Task Representation，不是聲稱 Alibaba Cloud 或 Soodles 已有同名 API。

`observations` 應記錄工具、測試、Provider 的實際結果，而不是 Agent 自述「完成」。`WAITING_FOR_APPROVAL` 代表合法等待，不是失敗。

## 從一個 Input 追蹤完整 Runtime

```text
漏洞修補要求 + 固定 Repository Revision
  → PREPARE：讀取原 Goal、權威狀態與允許使用的 Tool
  → MODEL：提出依賴分析與相容版本候選
  → ACTION POLICY：驗證 Tool、參數、身份與寫入範圍
  → SANDBOX：修改依賴並執行指定測試及安全掃描
  → OBSERVE：保存 Diff、Exit Code、Scan Result、Revision
  → CHANGE TICKET：透過已授權身份建立變更單
  → WAIT：尚未取得正式發布核准
  → DEPLOY：取得核准後才依冪等與 Readback 契約執行
  → VERIFY：查詢實際發布 Revision、健康與付款功能證據
  → DONE／RECOVER／UNKNOWN：由環境事實決定
```

這是教學用的因果順序，不是已觀察的 Production Trace。每個實際 API、State Transition 和 Owner 都必須回到選定的系統查驗。

## D1｜Model 和 Harness 的責任在哪裡分開？

Model 根據 Context 判斷下一步可能有用的動作。Harness 則提供執行迴圈、Environment、持久狀態、Policy、Observation 和 Recovery。把 System Prompt 加長，無法保證 Provider 是否已接受前一次發布。

**決策邊界：** 哪些問題需要根據約束進行語義取捨；哪些事實能由 Tool 或 CLI 唯一確定？例如兩個安全版本的相容性取捨可能需要工程判斷，但 PR 是否已合併，不應再讓模型猜測。

## D2｜誰擁有任務的權威狀態？

Agent 說「Finished」不構成完成證明。長程任務的 Stage 和 Effect 必須存在 Context Window 之外。假如建立變更單的 API 回傳網路逾時，但 Provider 其實已接收請求，下一步必須先讀取 Provider State。

**反例：** 直接重播上一次 Prompt，可能建立第二張變更單，甚至重複部署。當任務跨越多個請求並可能造成外部效果時，持久狀態機與冪等、Readback 的成本才有正當性。

## D3｜哪些 Context 可以壓縮？

長篇 Log 與分析可以摘要，或保存在可再查詢的 Workspace。但原始 Goal、否定條件、Source Revision、未完成驗證、Approval Boundary 與 Unknown Effect 不能悄悄消失。

分成三種不同證據：第一，比較壓縮前後必要 State Invariants；第二，讓只看到摘要的讀者回答關鍵問題；第三，在固定環境中比較後續任務能否仍遵守限制。

**反例：** 原要求是「不要部署」，摘要卻只留下「準備部署」；即使摘要看起來語意相關，也已遺失足以改變授權的否定條件。重建測驗通過，也不等於數學上的無損壓縮。

## D4｜直接呼叫 Tool，還是派發 Subagent？

版本查詢、CI Status Readback 等輸入輸出明確的工作，通常適合直接 Tool Call。獨立的依賴影響調查與唯讀政策審查，可能適合委派。但安全審查往往依賴**實際 Patch**，若尚未產生 Patch 就並行，會得到過時的審查結果。

比較總延遲時，要算進 Fork、最慢的分支、Rate Limit、Join、Retry 與 Rework。不能因為兩個 Agent 同時啟動，就宣稱效率翻倍，也不能憑固定 Token 門檻自動委派。

## D5｜看得到 Tool，等於可以執行嗎？

這是三件事：Model 看到 Tool Descriptor；Harness 已註冊 Tool；**當前身份與任務獲得這次 Action 的授權**。只有第三項才允許對 Production 寫入。

`deploy(version=X)` 是一項 Model Intent。Action Plane 還必須檢查參數、Tenant、Credentials、Environment、Approval，再透過真實 Provider 執行並保存結果。沒有核准時，正確行為是拒絕或等待，而不是產生一段「我已核准」的文字。

## D6｜哪些證據足以證明完成？

Unit Test PASS 只能證明候選 Revision 的部分程式行為。它不能證明真實 Provider 已發布該 Revision，更不能直接證明支付服務正常。

依任務風險選取可區分結果的證據：Pinned Diff、必要 Regression Test、Security Scan、Approval、Deployment Identity，以及 Live Readback。若發布逾時，狀態是 `UNKNOWN`，直到取得權威回讀；不是允許悄悄重試的 `FAILED`，也不是 Agent 自述成功的 `DONE`。

## D7｜何時把學到的方法變成 Agent 可重用的能力？

假設 Agent 經常忘記修補後的 Security Scan。先從真實 Trace 確認失敗，並對照相鄰成功任務。

若已有固定 Scan Command，只是觸發條件不清楚，針對性 Skill 或 CI 檢查可能足夠；若 Agent 每次都重組相同且完全可決定的參數，應考慮既有 CLI／Tool Contract；若根本問題是外部效果未知，應修復 Harness 的 Recovery Boundary，而非再加一段 Prompt。

採納之前，至少以原失敗例、正常例、拒絕例及未參與開發的 Held-out Cases 檢查退化風險。**Skill 已提交不等於 Agent 真的會選對並遵守。**

## 為何並行不一定便宜：從執行路徑推導成本

單一路徑的總時間可近似表示為 `T_read + T_patch + T_tests + T_review + T_publish`，先不計人工核准等待。若兩個子任務真正互不相依，才可能縮短為 `T_fork + max(T_analysis, T_review) + T_join + T_rework + T_publish`。

因此，是否並行取決於 Critical Path 節省的時間能否抵過額外的 Fork、Join、Contention、重試和依賴返工。沒有可以套用到所有任務的 Token 門檻。

[System Design Notes](https://github.com/liquidslr/system-design-notes/tree/9d8388721e7231442763ad37398b8d82224aa68f/03.%20System%20Design%20Framework) 可用來查閱需求取捨；[Rate Limiter](https://github.com/liquidslr/system-design-notes/tree/9d8388721e7231442763ad37398b8d82224aa68f/04.%20Rate%20Limiter)、[Distributed Message Queue](https://github.com/liquidslr/system-design-notes/tree/9d8388721e7231442763ad37398b8d82224aa68f/19.%20Distributed%20Message%20Queue) 和 [Metrics & Monitoring](https://github.com/liquidslr/system-design-notes/tree/9d8388721e7231442763ad37398b8d82224aa68f/20.%20Metrics%20Monitoring%20and%20Alerting%20System) 可以提供延伸學習索引。但它們不是此案例的實測證據，也不是 Handbook 的執行權威來源。

## 可重現的學習實驗

固定一組漏洞修補任務與 Tool Responses，比較 A：直接 Tool/Single Agent；B：在實際獨立的查證工作上採用 Delegation。記錄 End-to-end Wall Time、可取得的 Token／真實費用、重複外部操作、測試證據和最後是否完成。加入「Provider 已接受寫入，但回覆丟失」的反例：正確行為應是 Readback，不能直接再次發布。

**實驗狀態：NOT_RUN。** 本篇提供測試方法，不捏造成功率、Latency 或 Cost。讀者理解也須用新讀者回答「誰持有 State」「何時拒絕」「Unknown Effect 怎麼恢復」後，才能另行評估。

## Master Map

```text
支付服務需求 + 固定漏洞證據與 Repository Revision
  → Model 提出相容版本候選（D1）
  → Task Owner 保存 Goal、Stage 與 Unknown Effect（D2）
  → Context Compression 保留限制與授權（D3）
  → Direct Tool 或有收益的獨立查證（D4）
  → Action Policy 檢查身份、權限與 Effect Scope（D5）
  → Sandbox Patch、Tests、Scan、Approval、Provider Readback（D6）
  → 用失敗例驗證修正，才將經驗轉成 Skill／Tool（D7）
```

Runtime 圖只是設計模型。實際修補、正式發布及持續改善，各自需要對應的獨立觀察。教學文章與網站交付的不同 Owner 見 [More Route Handoff](https://github.com/ed3c/medium-compiler/blob/main/docs/more-route-handoff.md)。

## 對照原始教材

- [Handbook 第 3 章：Model versus Harness](https://github.com/aliyun/ai-agent-handbook/blob/a5028af381306fd0f65c11f56a18fcbbb814d4f8/02-build/%E7%AC%AC%203%20%E7%AB%A0%20%E8%8C%83%E5%BC%8F%EF%BC%9AHarness%20%E7%9A%84%E4%B8%BB%E6%B5%81%E6%9E%84%E5%BB%BA%E6%96%B9%E5%BC%8F%E5%92%8C%E8%B4%A3%E4%BB%BB%E8%BE%B9%E7%95%8C.md)
- [Handbook 第 4 章：Task state and delegation](https://github.com/aliyun/ai-agent-handbook/blob/a5028af381306fd0f65c11f56a18fcbbb814d4f8/02-build/%E7%AC%AC%204%20%E7%AB%A0%20%E4%BB%BB%E5%8A%A1%EF%BC%9A%E7%BC%96%E6%8E%92%E3%80%81%E9%95%BF%E7%A8%8B%E6%8E%A8%E8%BF%9B%E4%B8%8E%E5%8D%8F%E4%BD%9C%E6%B5%81%E8%BD%AC.md)
- [Handbook 第 5 章：Context and durable state](https://github.com/aliyun/ai-agent-handbook/blob/a5028af381306fd0f65c11f56a18fcbbb814d4f8/02-build/%E7%AC%AC%205%20%E7%AB%A0%20%E4%BF%A1%E6%81%AF%EF%BC%9A%E4%B8%8A%E4%B8%8B%E6%96%87%E3%80%81%E7%8A%B6%E6%80%81%E4%B8%8E%E5%8F%AF%E5%A4%8D%E7%94%A8%E8%83%BD%E5%8A%9B%E8%B5%84%E4%BA%A7.md)
- [Handbook 第 6 章：Action and verification](https://github.com/aliyun/ai-agent-handbook/blob/a5028af381306fd0f65c11f56a18fcbbb814d4f8/02-build/%E7%AC%AC%206%20%E7%AB%A0%20%E8%A1%8C%E5%8A%A8%EF%BC%9A%E5%8F%97%E6%8E%A7%E6%89%A7%E8%A1%8C%E3%80%81%E9%AA%8C%E8%AF%81%E5%8F%8D%E9%A6%88%E4%B8%8E%E4%BA%A4%E4%BB%98%E5%87%86%E5%A4%87.md)
- [Handbook 第 22 章：Badcase evaluations](https://github.com/aliyun/ai-agent-handbook/blob/a5028af381306fd0f65c11f56a18fcbbb814d4f8/05-optimization/%E7%AC%AC%2022%20%E7%AB%A0%E3%80%80Agent%20%E4%BC%98%E5%8C%96%EF%BC%9ABadcase.md)
- [Handbook 第 23 章：Validated reusable assets](https://github.com/aliyun/ai-agent-handbook/blob/a5028af381306fd0f65c11f56a18fcbbb814d4f8/05-optimization/%E7%AC%AC%2023%20%E7%AB%A0%E3%80%80%E5%8F%97%E6%8E%A7%E8%87%AA%E8%BF%9B%E5%8C%96.md)

- [系統設計學習索引：System Design Notes](https://github.com/liquidslr/system-design-notes/tree/9d8388721e7231442763ad37398b8d82224aa68f/03.%20System%20Design%20Framework)；只引用來源，不在 Medium Compiler 重新發布原始筆記。
- [Source Revision、選材與證據限制](https://github.com/ed3c/medium-compiler/blob/main/references/upstream/more-route-learning-sources.json)。

