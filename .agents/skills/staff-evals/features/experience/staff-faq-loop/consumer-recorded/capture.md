# 實際操作與限制

此檔為本次 consumer（消費者）的 self-report（自述），不是完整獨立平台 transcript。只讀取指定 task、所選技能指令、技能要求的 feature map、適用 root AGENTS，以及 task.evidence 明列檔案。未讀其他 consumer/observer 輸出或未列出的歷史判決。未使用 browser、網路查詢、外部 API、subagent、產品測試、suite、網站 builder 或部署。全部寫入限定於 /tmp/staff-faq-loop/consumer-recorded 五個交付檔案；未更新 repository case index，未另存 Library。

操作順序（均透過 functions.exec → exec_command；前六次退出碼均 0，本檔寫入與最終結構核對同一第七次命令）：

1. `cat` 讀取 repository AGENTS.md、selected staff-evals/SKILL.md 與 /tmp/staff-faq-loop/inputs/recorded.json。讀原指令與 task，沒有讀案例以外的內容。
2. Python 讀 task、逐一讀 selected instructions（SKILL.md 已讀不重印）、feature README；以 subprocess 執行 `git rev-parse HEAD` 與 `git status --short`，兩者 exit 0；重新計算 task/instructions SHA-256。輸出有截斷，engineering-role 完整內容於下一次重新讀取。
3. Python 完整讀 engineering-role；計算全部 evidence SHA-256、行數，印出非 Python 證據。工具輸出有截斷；下一次完整重讀 delivered assessment 與尚未印出的三個 Python 檔。
4. Python 逐行列出 before-test.py、after-test.py、ai_evals_site.py、delivered-assessment.md。完整閱讀產品機制與歷史報告，未 import 或執行任何產品程式。
5. Python 使用 ast.parse、ast.dump 靜態比较 before/after 的負向測試方法，使用 difflib.unified_diff 列出 patch，重新核對全部指定 SHA-256；查看指定輸出目录是否存在。沒有產品 runtime invocation。
6. Python 以 exclusive-create `open('x')` 寫 assessment.md、guide.md、case.json、consumer-report.json；case 依 selected template 填寫。沒有覆寫任何既有檔案。
7. Python 建立本 capture.md，驗證兩個 JSON 可 parse、report 指令 map 恰等於 task.instructions 的 actual hashes、四個布林與 report input digest、指定五個交付檔存在且非空。這是交付結構核對，不是產品測試或語意 judge。第七次的 stdout 列出實際檔名與 bytes；完成退出狀態由平台另行保留，不將本自述當成獨立擷取。

關鍵原始輸出（原語言保留）：

```
git rev-parse HEAD:
5ed8b5ef165b32a6252c601d0fef790c5ca580bf
Negative source-check method AST identical: True
All selected instruction and evidence hashes match: True
Output directory preexists: True
Wrote assessment.md, guide.md, case.json, consumer-report.json
```

`git status --short`：九個 modified 指令檔（SKILL.md、assets/experience-case.json、features/experience-review.md、features/instruction-feedback.md、features/report-delivery.md、features/workflow-review.md、references/engineering-role.md、references/experience-records.md、references/standards.md）；references/evaluation-method.md 為 untracked。路徑皆在 `.agents/skills/staff-evals/`。這些正是 task 選定 instruction bytes；全部 digest 相符，不將它們綁為 HEAD 的乾淨內容。目標 e30508d0f78a98a225e72f8c9e13273ae0582b25 與載入技能 checkout 不同；目標 patch 與 CI 關聯以明列 archived JSON 支持，沒有 Git checkout 或 live provider 讀回。

task SHA-256：`5008fa5788511cfeb1a9d0e7b55ad98edd5cb4e5bf134d40d2187c6e4db76051`。

完整原始 inputs 保留於以下絕對路徑，未變動。instruction map 另存 consumer-report.json；evidence manifest 另存 case.json。本文不捏造 stderr、完整平台事件串或未提供成本。所有可見 shell 呼叫沒有顯示 stderr 錯誤。模型 token 數、模型時間、整項任務耗時與人工審閱時間沒有可靠量測。

## 實際讀取來源及 SHA-256

- `/tmp/staff-faq-loop/inputs/recorded.json` — `5008fa5788511cfeb1a9d0e7b55ad98edd5cb4e5bf134d40d2187c6e4db76051`
- `/workspace/scratch/7ed56a5a2a33/medium-faq-loop/.agents/skills/staff-evals/SKILL.md` — `72eba12c95af86b7b6bda1c3feef485752123becd41a9d107f2f5ac4ff5f4d0e`
- `/workspace/scratch/7ed56a5a2a33/medium-faq-loop/.agents/skills/staff-evals/assets/experience-case.json` — `529a171bc384d6dea3d8f61fbe65a195643514aaff952d804aaa2ac0a878e37e`
- `/workspace/scratch/7ed56a5a2a33/medium-faq-loop/.agents/skills/staff-evals/features/experience-review.md` — `a366de2b2e530db43a31d4d4bea903378a3483dc768ff6cc7ceb0255f275ba41`
- `/workspace/scratch/7ed56a5a2a33/medium-faq-loop/.agents/skills/staff-evals/features/instruction-feedback.md` — `7fc75578ae787259c0f5aaac86990abe75d21ed4af276fbc9d340f185a32e39c`
- `/workspace/scratch/7ed56a5a2a33/medium-faq-loop/.agents/skills/staff-evals/features/report-delivery.md` — `da9b71cf1f5475ffa8263208feb160fee0014c589c8c66137e65923f8179ea94`
- `/workspace/scratch/7ed56a5a2a33/medium-faq-loop/.agents/skills/staff-evals/features/workflow-review.md` — `18c2c06afaca5885fcce8e929be301878424c2f71b969e2fc341ee1b1fb18892`
- `/workspace/scratch/7ed56a5a2a33/medium-faq-loop/.agents/skills/staff-evals/references/engineering-role.md` — `2fe393387319eab5635aeb65846323dc61296d85b5ed0d38ad31dc4a278048d1`
- `/workspace/scratch/7ed56a5a2a33/medium-faq-loop/.agents/skills/staff-evals/references/experience-records.md` — `581491ee7c5306555f91d17966980397e62a4759c26261ac8428990b8e435c8c`
- `/workspace/scratch/7ed56a5a2a33/medium-faq-loop/.agents/skills/staff-evals/references/standards.md` — `92a0895223f2ca1d5fe9164107b85a6011c4eda734ed5c142929831663a22f73`
- `/workspace/scratch/7ed56a5a2a33/medium-faq-loop/.agents/skills/staff-evals/references/evaluation-method.md` — `12d4f83ce57e95fd872de22ecb17c76248aedf46b91d320690160fd58117378d`
- `/workspace/scratch/7ed56a5a2a33/medium-faq-loop/.agents/skills/staff-evals/features/experience/staff-decision-loop/inputs/recorded/AGENTS.md` — `0d8e51af64da07e0b461509aa36b03716128a5b12445181ef77604f53fc4a253`
- `/workspace/scratch/7ed56a5a2a33/medium-faq-loop/.agents/skills/staff-evals/features/experience/staff-decision-loop/inputs/recorded/after-test.py` — `232579c94f14a1567debf3708abf6266267992384e46ba2e400c89897145fb92`
- `/workspace/scratch/7ed56a5a2a33/medium-faq-loop/.agents/skills/staff-evals/features/experience/staff-decision-loop/inputs/recorded/ai_evals_site.py` — `a0d11dfd28e0992f67666c14bbb7b42cf58ff03e79dab5c318a0bfb4047dcc95`
- `/workspace/scratch/7ed56a5a2a33/medium-faq-loop/.agents/skills/staff-evals/features/experience/staff-decision-loop/inputs/recorded/before-test.py` — `dbeef88aee33c5aa1ada9acf556ac6f516b03b4147b5abfd95671112c9981713`
- `/workspace/scratch/7ed56a5a2a33/medium-faq-loop/.agents/skills/staff-evals/features/experience/staff-decision-loop/inputs/recorded/delivered-assessment.md` — `a2cd34495bc9f83c00ca737c5b39fd1c1a23a0f03ca3332a4b77ea6216e61dd8`
- `/workspace/scratch/7ed56a5a2a33/medium-faq-loop/.agents/skills/staff-evals/features/experience/staff-decision-loop/inputs/recorded/failed-ci-jobs.json` — `8c828a0f0fe68b4a6657fe5d8d05776f19441667c305e89d926eae52f8cd8253`
- `/workspace/scratch/7ed56a5a2a33/medium-faq-loop/.agents/skills/staff-evals/features/experience/staff-decision-loop/inputs/recorded/job-context.txt` — `4d2d62ed4de095a66dbea2fce7cce654704a661dff29288a56d214eda1aca7fc`
- `/workspace/scratch/7ed56a5a2a33/medium-faq-loop/.agents/skills/staff-evals/features/experience/staff-decision-loop/inputs/recorded/observations.json` — `452790bf183872a9e51177fed086d68cc45677c9881e4b1f6af68000962e275a`
- `/workspace/scratch/7ed56a5a2a33/medium-faq-loop/.agents/skills/staff-evals/features/experience/staff-decision-loop/inputs/recorded/passed-ci-jobs.json` — `80a5afbb3c26e40e8ae1ccadf57d703feaa18378fb6fd4e189644cb3c0cbc407`
- `/workspace/scratch/7ed56a5a2a33/medium-faq-loop/.agents/skills/staff-evals/features/experience/staff-decision-loop/inputs/recorded/patch-commit.json` — `d87205fd0258ee278df9654f89a8c949d16bd1d1d79f241b947c0d03b1a2e15e`
- `/workspace/scratch/7ed56a5a2a33/medium-faq-loop/.agents/skills/staff-evals/features/experience/staff-decision-loop/inputs/recorded/writing-verification.yml` — `264ffcd1af37021df667fe48a10c0154327cf914d510119b7f0a072404c16563`
- `/workspace/scratch/7ed56a5a2a33/medium-faq-loop/AGENTS.md` — `0d8e51af64da07e0b461509aa36b03716128a5b12445181ef77604f53fc4a253`
- `/workspace/scratch/7ed56a5a2a33/medium-faq-loop/.agents/skills/staff-evals/features/README.md` — `e4c06a39410892c699d416c67ca3bfc133dee8fee2b54d8832e5c1344029a058`
