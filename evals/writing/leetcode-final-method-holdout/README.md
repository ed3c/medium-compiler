# 最終方法的兩題盲寫與正文重建

固定方法 commit：`4e5ee4dba71b33287be0fd720d35133a8247409a`。
這是兩份全新題型的 first-delivery holdout，不是 baseline/treatment improvement study。
完整判讀見 [報告](../../../docs/leetcode-final-method-holdout.md)。

| 文章 | English | 繁中 | fresh Reader 原始結果 |
| --- | --- | --- | --- |
| LeetCode 200 Number of Islands | [全文](islands/article.en.md) | [全文](islands/article.zh-TW.md) | [cost 缺項](islands/reader.raw.json) |
| LeetCode 56 Merge Intervals | [全文](intervals/article.en.md) | [全文](intervals/article.zh-TW.md) | [八題完整重建](intervals/reader.raw.json) |

每個題目目錄保存 `article.first.*` 首份完整草稿、`article.*` 作者首次定稿、
作者 `report.md`／review／runtime／detector，以及實際作者驗證程式。
作者報告中的 `INDEPENDENT_READER/NOT_RUN` 描述其交付時點；Reader 結果另存，不回填作者歷史。
兩份定稿先凍結才啟動 Reader；沒有 Reader 後文章修訂或補做成功樣本。

`selection.md` 與 `reader-questions.json` 在 Writer 啟動前保存。
`session-manifest.json` 列出原生 thread IDs、實際 capture 限制與路徑。
原始 task 中的本機路徑是當次紀錄，不能直接拿來重啟另一個實驗。
完整 native captures 留在 manifest 指定的外部目錄；此處是可攜式文章與結果，並非全部原始執行事件。

`quote-check.json` 保留原始逐字比對：Intervals 62/62、Islands 60/64、控制副本 18/18。
Islands 的四處漏掉 inline-code backticks；`quote-audit.json` 另存正文原句與定位，沒有改寫 raw Reader。
`cost-control/` 是從 Intervals 刻意刪除成本說明的副本；`cost-control-private.json`
記錄啟動該 Reader 前保存的變更與預期缺口。它只測 proxy 敏感度，不算自然 Writer 失敗。
現在公開了該控制與預期，往後不能把重用它的 consumer 當作未接觸答案的新盲測。

可離線重跑實際文章解法及機械證據檢查：

```sh
python3 evals/writing/leetcode-final-method-holdout/runtime_controls.py
python3 -m unittest discover -s tests -p 'test_final_method_holdout.py' -v
```

這兩條命令不啟動模型、不計算 SHA-256、不評文章語義，也不要求缺項清單為空。
CI 透過原有 unittest discovery 執行它們；不重跑作者 `verify.py`。
作者在當次本機 sidecar 留下的 digests 是歷史紀錄，不能當成內容正確性或發布 receipt。
首稿、失敗與 raw 結果都保持原貌，CI 綠燈不會把 Islands 的成本缺項變成通過。
