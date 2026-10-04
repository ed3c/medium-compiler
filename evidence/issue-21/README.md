# Issue #21：指定文章驗收，不借用 Ops 範例的綠燈

本 atom 修補一個機械盲點：學習文章與自己的 context 不一致時，Ops mechanical drives
仍可通過。既有 driver 新增 opt-in `learning-article --article`，讀相鄰 context 的
assembly.article_sha256，沿用 compiler 做無改動 Stage 6–7 與 receipt 驗證。
verify-learning-article recipe 要求執行這個入口，CI 也實跑真實 Git 文章。

## 本次實證（2026-09-28）

基線為 `4ad35ef8fb0caac94fe1f613f766f99ac1c2ba70`。完整 Git 文章的 SHA256 是
`14da88f545a69fe6a84024456802c545d6d0ada8ff07cb33c4677de48d62b17d`。

1. 從基線 git archive 建立外部來源副本，只在其 Git 文章附加
   `\n這是故意植入的未編譯變更。\n`；舊版 mechanical 仍 exit 0。
2. 新入口讀取同一變動文章與原 context，exit 2，明示 article/context hash mismatch。
3. 恢復該副本文章，只將 context hash 改為 64 個 0；新入口仍 exit 2。
4. 新入口驗證未改動的真實 Git 文章，exit 0；canonical bytes 與來源相同，搬移與
   scratch 清理後再次 check-receipt 成功。全篇 articles 檔案與 LEARNING.md 前後相同。
5. 完整 159 項 unittest 通過，包含 7 項新增測試；既有四項 mechanical drives 通過。
   behavior-evals 保持 BLOCKED / exit 3。

這是刻意植入漂移的機械敏感度控制，不是自然 writer 行為改善或人類學習成效。
未修改文章內容、課程 fork、本機課程環境或學習狀態；沒有執行發布命令。

`proof.json` 保存基線、前後檔案 hash、外層命令實錄及本篇 compiler 命令實錄。
僅將本機絕對路徑替換成 `<checkout>`／`<run>`，退出碼與內容結果保持原樣。
PR 的 Writing verification artifact 另外保留 exact-head 的 tests、git-article 輸入、
article-run receipt 與 commands。CI artifact 有既有的 7 天保存期限。

## 重跑

從 repository root，先選新的外部實體證據目錄：

```sh
PROOF_RUN=$(python3 -c 'import pathlib,tempfile; print(pathlib.Path(tempfile.mkdtemp(prefix="selected-article.")).resolve())')
python3 .agents/skills/verify-medium/scripts/verify.py --feature learning-article --article articles/git-collaboration.md --out "$PROOF_RUN/git-article"
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_selected_article_verification.py -v
```

完整 suite／mechanical 的 macOS TMPDIR 注意事項沿用 verify-learning-article Doctor。
測試只改外部副本，覆蓋缺少 context、過期 hash、本文漂移、匹配 hash 但未閉合 fence，
以及必填／禁止參數；不把只有 hash 一致誤作 compiler 通過。

## 明確邊界

不新增決策 sidecar、語意評分器或 renderer。Context 是一致性宣告，不是權威審核；
一起改正文與 hash 仍須作者／獨立語意審視。此 PASS 不證明 24 個決策完整、runtime
解釋正確、網站已發布或學員理解，這些不被本 atom 的驗收結果覆蓋。
