# Repository Loop 入口

`scripts/loop.py` 把已選定的語義 request 交給原 Soodles
`loop enter --request-file`。它只核對 request version 與本 repository 綁定，
再原樣傳遞檔案。原 CLI 驗證完整語義、固定來源 bytes，並回傳原 owner next。

呼叫形式：

```text
python3 scripts/loop.py --soodles /path/to/installed/soodles --request-file /path/to/request.json
```

`--soodles` 省略時使用 PATH 中的 `soodles`。範例路徑是佔位值，
不證明該機器已安裝 CLI。啟動失敗會回傳具名錯誤；adapter 不安裝替代 runner。

Request 使用 `schema: 1`。`repository` 是此 worktree 的絕對路徑。
`mode` 使用 `outer-inner`、`inner-only` 或 `outer-only`。
`goal`、`selected_skill`、`model` 是原 caller 選定的字串。
`write_paths`、`acceptance`、`source_refs` 是字串陣列。
`source_refs` 指向原 CLI 要讀取的實際檔案。原 caller 明確指定 Host 模型。
選用欄位是 `intent_selection`、`authorization`、`noodle`、`output`。
其有效性及所需條件由原 CLI 判定；adapter 不補造 identity、digest 或 receipt。

Adapter 不重選 mode、Skill、模型或測試，不建立 scheduler、重試或執行狀態。
原 CLI 的 stdout、stderr 與 exit code 直接保留。語義 request 不是執行成功證據；
native consumer、scope 驗收與 Provider readback 仍各自保留原結果。
