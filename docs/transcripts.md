# 第三方逐字稿 → Medium 文章

先保存來源，再寫成自己的文章。原始 HTML、擷取文字與文章各自保存，重新取材使用新目錄，舊快照不會被覆寫。

目前支援 **PodScripts 公開節目搜尋與逐字稿頁面**。上方輸入主題、來賓或 YouTube 連結，選擇節目，即可自動搜尋並讀取第一個候選的時間戳與固定短摘錄。也可以逐一確認其他候選。

每次使用一個節目的免費公開搜尋，最多顯示第一頁的 5 集，不使用付費跨節目搜尋。內建 The a16z Show、a16z Podcast、Latent Space、Dwarkesh、No Priors、Lenny's Podcast、Lex Fridman。中文 AI 關鍵字採有限詞彙對照，不是通用語意搜尋；未命中時改用較短的英文關鍵字。

一般 YouTube 連結先讀取公開影片標題，再於選定節目搜尋。這次的影片沿用既有來源對應紀錄搜尋 The a16z Show；這份對應原本由取材者指定，並未核對音訊。搜尋結果、標題相似與已讀到時間戳都不代表確認了同一集或原話。

## 先自動尋找來源

```sh
python3 scripts/transcript.py search \
  --query 'https://youtu.be/ekK8urKHPMQ'
python3 scripts/transcript.py search \
  --query 'Agent 記憶' --podcast latent-space
python3 scripts/transcript.py inspect \
  --url 'https://podscripts.co/podcasts/the-a16z-show/beyond-the-god-model-alex-atallah-amjad-masad'
```

`search` 回傳實際搜尋詞、節目、原站搜尋網址與候選來源；`inspect` 實際讀取來源，回傳段落數、起訖時間戳、SHA-256 與固定短摘錄。網站和 CLI 共用這兩個流程。沒有结果與來源讀取失敗會分開顯示；不會用搜尋摘要冒充逐字稿。

完整第三方逐字稿由「閱讀原站逐字稿全文」開啟。本站不重新發布全文。確認來源後，若要保存本機取材快照，可使用下方原有的 `fetch`；網頁不會自動提交搜尋結果到 Git、生成文章或改動既有來源。

## 取得來源

在 medium-compiler repository 根目錄執行，Python 3.10+ 即可，不需 API key：

```sh
python3 scripts/transcript.py fetch \
  --url 'https://podscripts.co/podcasts/the-a16z-show/beyond-the-god-model-alex-atallah-amjad-masad' \
  --video-url 'https://youtu.be/ekK8urKHPMQ' \
  --out .transcripts/openrouter-agent-primitives
```

`fetch` 在你的終端執行。網站提供公開來源的搜尋與短預覽，不代理下載任意網址，也不要求你提供登入資料。

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

在此 repository 的 Agent 工作階段使用 **`podcast-to-medium`**：輸入 Podcast、影片網址或想討論的問題，skill 會串接 CLI 搜尋、來源保存、段落定位、`medium-writing` 與已要求的網站部署。這是 Agent 的工作流程；網頁搜尋按鈕本身不會呼叫寫作模型或自動發布文章。

```sh
python3 scripts/transcript.py locate \
  --snapshot .transcripts/openrouter-agent-primitives \
  --term '2005' --term 'table stakes' --term 'agent loop'
python3 scripts/transcript.py passage \
  --snapshot .transcripts/openrouter-agent-primitives \
  --start 00:14:05 --through 00:15:18 --context 1 \
  --out .transcripts/openrouter-agent-primitives/selected-passage.json
python3 scripts/transcript.py verify-passage \
  --snapshot .transcripts/openrouter-agent-primitives \
  --packet .transcripts/openrouter-agent-primitives/selected-passage.json
```

`locate` 回傳關鍵詞命中的時間戳；`passage` 保存完整時間戳段落與前後文，不改寫文字。`through` 指最後一組段落的起始時間，不代表原話結束時間。寫作前仍須閱讀前後文，確認哪些內容回答使用者的問題；`verify-passage` 只核對來源與選段的一致性。若沒有已知影片，`fetch` 可省略 `--video-url`。

使用 repository 的 `medium-writing`，先列目錄、讀者決策與來源範圍，再依現有 Stage 0–7 CLI 完成新文章。原始來源與既有文章保持不變，文章另存於 `articles/`。保留原文的條件與不確定性；自己的分析、假設案例與來源觀點必須可區分。公開頁面只使用必要短引文、來源連結與獨立論述。

本次範例聚焦訪談 14:05–15:40 的 Agent 基本元件類比，不宣稱改寫整集。可在本站 Articles 閱讀「每個人都在做 Agent，為什麼產品仍然可以不同？」。文章提供 Markdown 下載與來源紀錄，發布到本網站不等於發布到 Medium.com。

程式與完整使用方式：[medium-compiler repository](https://github.com/ed3c/medium-compiler)。
