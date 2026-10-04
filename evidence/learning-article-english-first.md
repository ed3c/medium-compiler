# 英文先行與繁中翻譯：一個 Git 決策的實證

本次只更新 verify-learning-article 的語言流程。文章及網站沒有改動。
這是作者執行的一個決策點檢查，不是完整課程、獨立 reader 測試或完整 skill maintenance。

## 既有文章抽查

基準為 `af7f53b56ab452983d911920bb45f0d8d318a17b`。抽查範圍如下，不能外推為全部文章合規。

- [Git](../articles/git-collaboration.md#概念一份內容經過四個位置)：保留 add 當下內容、後續修改與 commit 的差別，並說明 fast-forward 的祖先條件。
- [Python environments](../articles/python-environments.md#套件從哪裡來跟著一次安裝追到-import)：說明 interpreter 選擇覆寫造成的拒絕，保留原課檢查範圍。
- [開發環境](../articles/application-engineering-colab.md)：Node.js 與 pnpm 段落交代版本條件、PATH 修正及只影響課程 shell 的範圍。

這些段落具備明確操作、原因及邊界，但仍有一個長句包含多項條件的情況。
三篇 context 都將 independent_semantic_review 標為 NOT_RUN。
沒有英文本稿與繁中譯稿的對照紀錄，不能倒推既有文章採英文先行，也不能宣稱零語意損失。
[ASD-STE100](https://www.asd-ste100.org/about_STE.html) 包含寫作規則及受控字典。
本次只採 STE-inspired 寫法，沒有做完整標準合規檢查。

## 決策與 runtime

問題：修改已 add 的檔案後，要讓下一個普通 commit 保存新內容，是否需要再次 add？
範圍：不帶 path argument 或自動 staging 選項的 git commit。
來源：基準 Git 文章的「概念：一份內容經過四個位置」，以及下面新執行的隔離本機案例。
此英文稿是本次重建的解釋，不是既有文章遺失的歷史英文原稿。

本次實際建立的目錄，僅列與此決策有關的檔案；目錄包含關係不代表執行順序：

```text
git-lab/
├── snapshot.txt       working tree 的檔案
└── .git/
    ├── index          下次 commit 所選的內容
    └── objects/       Git objects
```

一個決策的心智圖：

```text
下一個普通 commit 要保存後續修改
├── 限制：修改 working tree 不會同步更新 index
├── 再次 git add → index 選入新內容 → commit 保存新內容
└── 沒有再次 git add → index 仍是舊內容 → commit 保存舊內容
```

實際資料流及讀回：

```text
snapshot.txt = snapshot=1
  → git add snapshot.txt
  → git show :snapshot.txt = snapshot=1
snapshot.txt 改成 snapshot=2
  → 普通 git commit
  → git show HEAD:snapshot.txt = snapshot=1
  → working tree 仍為 snapshot=2
  → git add snapshot.txt，再普通 git commit
  → git show HEAD:snapshot.txt = snapshot=2
```

使用 `git version 2.50.1 (Apple Git-155)`，新建無 remote 的本機 repository。
首次 commit 為 `2807c0ff9b560ec35a5e24f38ca2cb4709e0ce83`；第二次為 `fb24762eb8b4d0fe252106a3b39fef860f98d8f8`。
兩次 commit 使用 command-scoped 本機測試身分，沒有修改全域 Git 設定。
沒有 push、帳號操作、文章發布或學習進度寫入。

## English draft

### Which version does a commit save?

The goal is to save the edited file in a local commit. The working tree contains the current files. The index contains the content selected for the next commit. Because editing the file does not update the index, run `git add` again after the edit if the next commit must contain that edit.

In this isolated local check, `snapshot.txt` first contained `snapshot=1`. After `git add snapshot.txt`, the index contained `snapshot=1`. The file then changed to `snapshot=2`. Without another `git add`, a plain `git commit` did not include the later edit: the first commit contained `snapshot=1`, while the working tree still contained `snapshot=2`. After another `git add snapshot.txt` and a second commit, that commit contained `snapshot=2`.

This check used plain `git commit`, with no path argument or automatic staging option. It did not test every commit mode. The local commits do not prove remote backup. No remote was configured or contacted in this check.

## 繁體中文譯稿

### commit 會保存哪一版？

目標是把編輯後的檔案存入本機 commit（提交）。working tree（工作目錄）保存目前的檔案。index（暫存區）保存選入下一次 commit 的內容。編輯檔案不會更新 index，所以若下一次 commit 必須包含這次修改，就要在修改後再次執行 `git add`。

這次隔離的本機檢查中，`snapshot.txt` 最初是 `snapshot=1`。執行 `git add snapshot.txt` 後，index 保存 `snapshot=1`。接著把檔案改成 `snapshot=2`。若未再次執行 `git add`，一般的 `git commit` 不會包含後續修改：第一個 commit 保存 `snapshot=1`，working tree 仍是 `snapshot=2`。再次執行 `git add snapshot.txt` 並建立第二個 commit 後，該 commit 才保存 `snapshot=2`。

這次使用一般的 `git commit`，沒有指定檔案路徑或自動加入 index 的選項。這次沒有測試所有 commit 模式。本機 commit 不能證明遠端備份已完成。這次檢查沒有設定或連線到 remote（遠端 repository）。

## 作者語意核對與反例

- 條件：下一次 commit 必須包含修改；兩稿都要求修改後再 add。
- 原因：working tree 的修改不會更新 index；兩稿都保留此因果。
- 狀態：第一次 commit 是 1、working tree 是 2；再 add 後第二次 commit 是 2。兩稿與本次讀回一致。
- 術語：working tree／工作目錄、index／暫存區、commit／提交、remote／遠端 repository。命令、檔名及 snapshot 值保持一致。
- 邊界：普通 commit、非所有模式、未驗 remote backup；沒有把本機結果提升為 GitHub 備份成功。

受控錯譯只將 `git commit` 後的「不會包含後續修改」改為「會包含後續修改」。
原譯稿與錯譯都經 init --draft → next → submit 6 → assemble → verify → check-receipt。
兩者的 receipt 均為 VALID，semantic_correctness 均為 NOT_ASSESSED。
這是以已完成的短稿做 Stage 6–7 機械控制，不虛構原文章的 Stage 0–5。

作者拒絕錯譯：它反轉否定，且與 index 及第一次 commit 的讀回矛盾。
修正版本保留「不會」。接受只涵蓋本次單一決策；不能據此保證未來所有翻譯沒有遺漏。
錯譯由作者刻意建構，判定也是作者核對，不能冒充盲測或獨立 reviewer 成功。
編譯器只檢查機械條件；不增加否定詞 regex 或語意評分引擎。

## 可重查的版本與驗證

以下 SHA-256 對應外部保留的獨立檔案，不是本報告中調整過 heading 層級的節錄：

- `draft.en.md`: `557a187931b72876018d40759c51b284faa3b9a226ff98c145022f4776c6f819`
- `draft.zh-Hant.md`: `6ff8bb5d844b460f0f84158692347e9971721fe2089f37f49f6d2d2eb62b5977`
- `negative.zh-Hant.md`: `88e6e357f90c7709fd85c23f9adbcde09521affd308d6d4a22f7d440e97ee3a4`
- `git-collaboration.md`: `14da88f545a69fe6a84024456802c545d6d0ada8ff07cb33c4677de48d62b17d`

原稿與錯譯的 canonical bytes 分別與送入的譯稿完全一致。
外部保留 commands.json、result.json、兩稿、錯譯、兩份 compiler run 和 verification logs。

- skill-creator quick_validate：通過，僅 metadata／結構檢查。
- verify-medium doctor：通過。
- unittest：153 項通過。
- verify-medium mechanical：staged-authoring、bounded-revision、lossless-drilldown、delivery 四項通過。
- 第一次本機 suite／mechanical 因 macOS 預設 TMPDIR 的符號連結被 source guard 拒絕。
  依既有 skill 指示，以單次命令指定 resolve 後的 TMPDIR 重跑成功；保留原失敗紀錄，未停用防護。
- 證據腳本第一次讀錯 canonical 輸出路徑；依 assemble 的實際回傳路徑修正後續讀取。
  已成功的 compiler run 保留，沒有重寫 state 或 receipt。
- 獨立語意審視：NOT_RUN。人的理解、心流、taste 改善：NOT_MEASURED。

此改動沒有將現有全文重譯，也沒有部署。未來每個單元仍須對來源、英稿及譯稿重新核對。
