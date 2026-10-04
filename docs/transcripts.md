# 第三方逐字稿 → Medium 文章

先保存來源，再寫成自己的文章。原始 HTML、擷取文字與文章各自保存，重新取材使用新目錄，舊快照不會被覆寫。

目前支援 **PodScripts 公開節目頁面**。你需要先找到對應節目的逐字稿 URL；YouTube URL 只記錄你指定的影片對應，不會自動搜尋逐字稿或確認兩者相同。先核對節目名稱與內容。

## 取得來源

在 medium-compiler repository 根目錄執行，Python 3.10+ 即可，不需 API key：

```sh
python3 scripts/transcript.py fetch \
  --url 'https://podscripts.co/podcasts/the-a16z-show/beyond-the-god-model-alex-atallah-amjad-masad' \
  --video-url 'https://youtu.be/ekK8urKHPMQ' \
  --out .transcripts/openrouter-agent-primitives
```

網頁只提供操作說明與已完成文章；命令在你的終端執行。本站不會代理下載任意網址，也不要求你提供登入資料。

成功後，目錄包含四個檔案：

- `source.html`：HTTP 回應的原始 bytes，未經改寫。
- `transcript.json`：依來源時間戳分段的文字；只解碼 HTML entities 與正規化空白。
- `transcript.md`：可閱讀的時間戳逐字稿，保留來源的重複與疑似辨識錯誤。
- `manifest.json`：URL、實際取得時間、來源與輸出 SHA-256，以及核對限制。

`.transcripts/` 已被 Git 忽略。原始逐字稿不會被網站 builder 複製或發布。若需長期保存，請保留自己的來源目錄；Git 中的 metadata 不能重建完整快照。

## 核對快照與匯出來源紀錄

```sh
python3 scripts/transcript.py verify \
  --snapshot .transcripts/openrouter-agent-primitives
python3 scripts/transcript.py receipt \
  --snapshot .transcripts/openrouter-agent-primitives \
  --out /tmp/openrouter-source.json
```

`verify` 檢查 bytes，並從保存的 HTML 重新解析後比較輸出。`receipt` 只匯出 metadata 與雜湊，不包含逐字稿正文。兩個命令都不確認原話真偽、音訊、發言者或整集是否完整；metadata 是取得紀錄，不是第三方簽章。

下載逾時、非 HTML、頁面沒有時間戳或來源版型改變時，命令以 exit 2 拒絕，不會把搜尋摘要當成完整逐字稿。已存在的輸出目錄也會拒絕。需要重抓時換一個目錄；不要修改舊快照來讓驗證通過。

如果已經另行保存完整 HTML，可用以下匯入路徑。紀錄會明確標示 `imported_html`，不虛構 HTTP 取得時間。

```sh
python3 scripts/transcript.py import-html \
  --url 'https://podscripts.co/podcasts/the-a16z-show/beyond-the-god-model-alex-atallah-amjad-masad' \
  --video-url 'https://youtu.be/ekK8urKHPMQ' \
  --html /tmp/saved-episode.html \
  --out .transcripts/openrouter-imported
```

## 寫成獨立文章

使用 repository 的 `medium-writing`，先列目錄、讀者決策與來源範圍，再依現有 Stage 0–7 CLI 完成新文章。原始來源與既有文章保持不變，文章另存於 `articles/`。保留原文的條件與不確定性；自己的分析、假設案例與來源觀點必須可區分。公開頁面只使用必要短引文、來源連結與獨立論述。

本次範例聚焦訪談 14:05–15:40 的 Agent 基本元件類比，不宣稱改寫整集。可在本站 Articles 閱讀「每個人都在做 Agent，為什麼產品仍然可以不同？」。文章提供 Markdown 下載與來源紀錄，發布到本網站不等於發布到 Medium.com。

程式與完整使用方式：[medium-compiler repository](https://github.com/ed3c/medium-compiler)。
