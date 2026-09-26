更精確地說，這裡要分開三層 authority。課程可以觸發 **EXPERIMENT**：即使 canonical product 目前沒有缺陷，Ops 作為實驗環境仍可以用隔離路徑研究 Agent、Fine-tuning 或新的 eval 方法；如果連實驗價值都不足，才記錄 **NO_CHANGE**。這兩種結果都只回答「現在要不要研究這項能力」，不直接改 production runtime。

```text
lesson
  ↓
EXPERIMENT ──→ tests / evals / runtime evidence
  │                         │
  │                         └─ 沒有真實產品需求 → 保留實驗，不升格
  │
  └─ evidence + real product need
                  ↓
              PROMOTE candidate
                  ↓
          product owner decides
```

因此 **PROMOTE** 是第二個獨立決策，不是 `EXPERIMENT` 的自動下一步。即使實驗數據很好，只要沒有真實 product need，也可以保留成實驗能力而不改 canonical path；反過來，課程教到某個主題也不能單獨構成升格理由。這讓 Ops 可以快速擴展實驗面，同時避免 syllabus 直接變成 production backlog。

