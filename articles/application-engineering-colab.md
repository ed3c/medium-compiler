# 開發環境設定：從本機判讀到 Colab CLI 與第一份 Python 練習

想走完整的 Application Engineering 路線，可以把 [AI Engineering from Scratch](https://aiengineeringfromscratch.com/) 當作課程骨架。首頁在 2026-09-27 標示 **20 個 phases、523 lessons**，描述的學習循環是從問題走向數學、程式、測試與可保留的成果。這是整份課程的規模，不是入門者必須先上完的課數，也不是本文逐課驗證過的完成保證。

你指定的 [Dev Environment 第一課](https://aiengineeringfromscratch.com/lesson?path=phases/00-setup-and-tooling/01-dev-environment&learningPath=software-engineering-fundamentals) 位於 **Software Engineering Fundamentals** 路線。它先處理開發環境，後面才接 Git、除錯、介面、驗證與發佈。若目標是能做出 AI 應用，這些基礎可以與網站另列的 [Building and Deploying AI Applications](https://aiengineeringfromscratch.com/lesson?path=phases/11-llm-engineering/01-prompt-engineering&learningPath=building-and-deploying-ai-applications) 路線接起來；兩個名稱代表不同的課程選擇。

第一個成果很小：打開 Colab，執行一段 Python，讓測試確認結果，然後把程式與結果帶走。暫時不需要模型 API、資料庫或 GPU。

## 先分清 Notebook 和 runtime

Notebook 是保存說明、程式格與輸出的文件；runtime 是執行程式的環境。按下執行後，Python 定義的變數留在該次程序記憶體中。光是把程式碼寫在格子裡，還沒有定義變數。

這個區別決定了操作方式：一份可重跑的練習，應讓後面的格子只依賴前面明確執行過的格子。不要依賴昨天留在記憶體裡、今天已刪掉的設定。

[Google Colab 官方 FAQ](https://research.google.com/colaboratory/faq.html) 說明，Notebook 可以保存在 Drive 或從 GitHub 開啟；執行用的虛擬機有生命週期限制。保存 Notebook 不等於保存 runtime 的全部檔案。本篇因此保留兩個東西：可重跑的 `.ipynb` 與執行後另外下載的 `environment-check.json`。

## 一筆輸入怎麼變成可檢查的成果

練習使用平方和：把 `[1, 2, 3]` 的每個值平方，再加總。手算是 1 × 1 + 2 × 2 + 3 × 3 = 14。選這個小例子，是為了把「程式是否正確」和「環境是否可用」先分開；不用網路模型回應當判準。

```text
Notebook 中的程式格
    ↓ 按執行，交給目前 Python runtime
values = [1, 2, 3]
    ↓ sum_of_squares(values)
產生 1、4、9，逐項累加
    ↓
result = 14
    ↓ 三個 assert 都成立
environment-check.json
    ↓ 另外下載保存
可讀取的本次測試紀錄
```

`print(14)` 只會顯示一個值，無法證明函式曾計算。`assert sum_of_squares([1, 2, 3]) == 14` 才會實際呼叫函式並檢查條件；不成立時，Python 會以 `AssertionError` 中止該格。再加上空輸入與含負數的測試，可以檢查目前定義的邊界。

執行順序也是輸入條件。若先跑測試格而沒有跑函式定義，會得到 `NameError`。這時應回到前面的格子，從上往下重跑；不必先重裝套件。

本文附的 Notebook 結構如下。最後的 JSON 由第四格執行後產生，不是事先放好的成功報告。

```text
application-engineering-colab.ipynb
├─ 1. Python 版本與執行位置
├─ 2. sum_of_squares 與範例輸入
├─ 3. 正常、空集合、負數測試
└─ 4. 寫出 environment-check.json
```

## 本機、雲端 API 與 Colab，要分成三個問題

這次學習從一台 M1 Pro、16 GB 統一記憶體的 MacBook Pro 出發。本機讀回確認了晶片與記憶體規格；尚未選定模型，也沒有執行 LLM 效能測試。因此「本機無法跑任何 LLM」不是這次已驗證的結論。

第一個問題是應用程式在哪裡開發。Python、Git、測試與呼叫模型 API 的程式，可以在本機完成；第一課的環境設定不以載入大型模型為前提。Node.js、Rust、Docker 等工具仍依後續課程需求準備，Colab 不會自動取代整套開發環境。

第二個問題是模型由誰執行。呼叫雲端 LLM API 時，模型由供應商執行，本機負責送出請求、處理結果與測試應用。這條路需要該服務的存取權與網路，並不需要 Colab CLI。

第三個問題是要不要自己載入模型權重。這才需要評估模型大小、量化、上下文長度、可用記憶體與速度。Apple Silicon 有 [MLX LM](https://github.com/ml-explore/mlx-lm) 這類本地推論工具；這說明存在本機路徑，不代表本篇已測出某個模型能在這台機器順暢執行。若指定模型或實驗超出本機資源，再選雲端 GPU，Colab 是其中一種實驗環境。

粗估權重記憶體可以先用「參數量 × 每個參數的位元數 ÷ 8」。例如 30 億參數以 4-bit 表示，原始權重約 1.5 GB；這只是下限估算，還沒算量化附加資料、KV cache、框架、作業系統與其他應用。16 GB 統一記憶體也不是可以全部交給模型的獨立顯示記憶體。實際決策仍要指定模型與工作負載，再測量。

因此這次採用的方向是：**本機保留工程工具與程式，雲端按需要提供模型服務或 GPU 運算**。Colab CLI 的作用是從終端機建立、執行和結束 Colab runtime；它不會讓本機 GPU 變大，也不保證雲端一定分配到想要的 GPU。

## 用最小 CPU 練習，先確認可重跑性

這四格只用 Python 標準函式庫。CPU 足以完成三個數字的計算；把硬體切成 GPU 不會讓一般 Python 的 `sum` 自動使用 GPU。等課程確實需要張量運算與加速框架時，再檢查框架是否把資料和運算放在對應裝置。

若輸入有 n 個數字，這個函式逐項做一次乘法與累加，需走過 n 項；對本例的小整數，把單次算術視為固定成本，時間為 O(n)。產生式沒有建立完整平方陣列，除輸入外只保留累加過程所需的少量狀態。這裡值得優先改善的是可重跑性，GPU 傳輸或排程反而不符合這個練習的需要。

Colab 適合這種短程 Python 練習。需要長期執行的服務、完整 Node.js／Rust 工具鏈、Docker 或正式應用部署時，回到原課的本機環境路線。不要把 Notebook 連線當作網站的正式主機。

[原課完整內容](https://github.com/rohitg00/ai-engineering-from-scratch/blob/c257687012e3b0ae7cf55f7f467e4b703652b3cc/phases/00-setup-and-tooling/01-dev-environment/docs/en.md) 包含 Python 3.11+、Node.js 20+、Rust、套件管理，以及依硬體檢查 CUDA／MPS；它也說明可先準備所選路線需要的工具。這篇 Colab 指南只承接 Python 入門部分，並不等於已完成所有本機、多語言或 GPU 練習。

## 把第一課放回完整路線

接續時以[官方 Software Engineering Fundamentals 路徑](https://github.com/rohitg00/ai-engineering-from-scratch/blob/c257687012e3b0ae7cf55f7f467e4b703652b3cc/learning-paths/software-engineering-fundamentals.json) 為準。該版本列出 13 個必修節點，順序是：

1. 開發環境。
2. Git 與協作。
3. Python environments。
4. Docker for AI。
5. 資料管理。
6. Terminal 與 Shell。
7. Debugging 與 Profiling。
8. Tool interface。
9. Tool schema design。
10. Verification gates。
11. Shadow／Canary／Progressive release。
12. Security／Secrets／Audit。
13. SRE for AI。

這條線先建立「能執行、能改動、能驗證、能交付」的工程能力。之後再沿 AI 應用路線練習 Prompt、結構化輸出、檢索、評估與服務化。這是把兩條官方路線連起來的閱讀建議，不是官方另發的一條名為 Application Engineering 的認證路徑。

## 在 Colab 建立第一份筆記本

開啟 [Google Colab 繁體中文入口](https://colab.research.google.com/?hl=zh-tw)，使用你自己的 Google 帳號登入。選擇新增筆記本（New notebook），把檔名改成 `application-engineering-colab.ipynb`。如果介面語言不同，可對照括號內的英文名稱。

在「執行階段 → 變更執行階段類型」（Runtime → Change runtime type）選 Python 3，硬體加速器選 CPU 或 None，再連線。這裡的 Python 3 是系列名稱；實際小版本要以第一格輸出為準。免費資源的可用性與使用限額可能變動，第一次練習不需要購買 GPU。

你也可以直接開啟[本文的 Colab 練習筆記本](https://colab.research.google.com/github/ed3c/medium-compiler/blob/main/notebooks/application-engineering-colab.ipynb)，再選「在雲端硬碟中儲存副本」（Save a copy in Drive）保留自己的版本。需要執行的部分仍要登入 Colab；文章與 [Notebook 原始內容](https://github.com/ed3c/medium-compiler/blob/main/notebooks/application-engineering-colab.ipynb) 可公開閱讀。

### 第一格：觀察你真正使用的 Python

貼上以下程式，按格子左邊的執行按鈕，或用 Shift+Enter：

```python
import json
import platform
import sys

print("Python:", platform.python_version())
print("Executable:", sys.executable)
assert sys.version_info >= (3, 11), "需要 Python 3.11+；先檢查執行階段版本"
print("環境檢查通過")
```

看到版本、執行檔位置和「環境檢查通過」，表示這次 runtime 的 Python 符合本練習要求。這不是套件安裝清單，更不是課程完成證明。若版本太舊，先檢查所選執行階段，不要把版本條件刪掉來取得通過。

### 第二格：先讓輸入走過函式

```python
def sum_of_squares(values):
    return sum(value * value for value in values)

values = [1, 2, 3]
result = sum_of_squares(values)
print(result)
```

預期顯示 `14`。函式收到列表，產生式逐項平方，`sum` 加總後回傳結果。改成其他整數列表之前，可以先手算，再比較程式輸出。

### 第三格：用測試區分「有輸出」與「符合條件」

```python
assert sum_of_squares([1, 2, 3]) == 14
assert sum_of_squares([]) == 0
assert sum_of_squares([-2, 3]) == 13
print("3 tests passed")
```

三項都成立才會印出 `3 tests passed`。空列表的平方和定義為 0；負數平方仍為正數。本例的輸入契約是整數序列，不在這一課延伸為字串轉型、浮點誤差或大型資料系統。

### 第四格：保存這一次實際產生的結果

```python
from pathlib import Path

receipt = {
    "exercise": "colab-dev-environment",
    "python": platform.python_version(),
    "input": values,
    "result": result,
    "tests": 3,
    "scope": "environment-and-example-only",
}
receipt_path = Path("environment-check.json")
receipt_path.write_text(
    json.dumps(receipt, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
print(receipt_path.resolve())
print(receipt_path.read_text(encoding="utf-8"))
```

這格會寫入 runtime 的工作目錄。從左側「檔案」（Files）找到 `environment-check.json`，使用檔案選單下載；它不會因為 Notebook 存在 Drive 就自動保存到 Drive。Notebook 自己也要儲存，或用「檔案 → 下載 → .ipynb」（File → Download → .ipynb）保留副本。

JSON 記錄了 Python 版本、輸入與結果，方便回看；它不是不可偽造的證書。是否可重現仍要重新執行四格，而不是只閱讀最後一行文字。

## 從乾淨狀態重跑，才知道漏了什麼

先保存並下載需要的檔案，再重新啟動工作階段，從第一格順序執行到第四格。這次若仍得到 `14` 和三個測試通過，代表練習沒有依賴重啟前遺留的 Python 變數。重啟 Python 工作階段不一定等於刪除整台虛擬機或全部檔案，兩種操作不要混為一談。

常見錯誤可按發生位置處理：

- `NameError`：前面定義函式、匯入套件或建立變數的格子還沒跑，先從第一格重跑。
- `AssertionError`：先檢查是否改過函式或預期值，用手算的 14、0、13 找出第一個不符案例。
- 斷線或連不上：確認登入與 runtime 連線狀態，再看服務當下是否有資源可用。
- 後續課程遇到 `ModuleNotFoundError`：確認錯誤是哪個套件，再在目前 Notebook 使用 `%pip install 套件名稱`；本篇四格不需要安裝第三方套件。
- 找不到 JSON：先確認第四格是否成功，再看目前工作目錄；若原 runtime 已被刪除，應重新跑程式或使用先前下載的副本。

原課的[環境驗證程式](https://github.com/rohitg00/ai-engineering-from-scratch/blob/c257687012e3b0ae7cf55f7f467e4b703652b3cc/phases/00-setup-and-tooling/01-dev-environment/code/verify.py) 也能作為之後的檢查入口。將課程 repository 下載到所選環境後，在含有 README.md 與 phases/ 的根目錄執行：

```bash
python3 phases/00-setup-and-tooling/01-dev-environment/code/verify.py --route beginner
```

這個版本的 beginner 檢查要求 Python 與 Git，其他工具預設留待後續。網頁網址的 `learningPath=software-engineering-fundamentals` 是網頁導覽參數，不是這支程式接受的 `--route` 值；不要直接照抄成 CLI 參數。以上命令供你在已取得課程 repository 後操作，本文沒有替你宣告該命令已在你的 Colab 執行。

## 實際操作紀錄：從安裝失敗到完成第一次雲端執行

以下紀錄截至 2026-09-27。它記錄本次環境操作，不代表讀者已完成課程，也不代表已完成任何 LLM 訓練或推論。

1. **讀回本機硬體。** 確認 M1 Pro、16 GB 記憶體；未執行模型 benchmark。不能從硬體名稱直接推導所有模型都能跑或都不能跑。
2. **檢查現有工具。** 本機已有 uv，Homebrew Python 為 3.14.6，原先沒有 `colab` 指令。
3. **第一次安裝失敗。** 執行官方建議的 `uv tool install google-colab-cli`，但 uv 這次選用 Python 3.11.11，低於當前套件要求的 Python 3.12。這是 CLI 本身的執行環境問題，與 GPU 或 LLM 容量無關。原課的 Python 3.11+ 與新工具的 Python 3.12+ 是兩個不同條件。
4. **指定已存在的 Python 後安裝成功。** 使用下方指令，得到 `google-colab-cli 0.7.4`。這個 Python 路徑來自本機檢查；其他電腦應改成自己實際安裝的 Python 3.12+，不要盲抄路徑。
5. **驗證命令可啟動。** `colab version` 回傳 `Version: 0.7.4`，`colab --help` 列出 session、執行、檔案下載等命令。這只能確認本地 CLI 已可用。
6. **首次查詢停在授權。** `colab sessions` 最初進入 Google OAuth 流程，在輸入授權碼前取消。這個時間點只完成 CLI 安裝，還沒有建立 runtime。
7. **由使用者完成 Google 授權。** 使用者在自己的終端機登入後，得到 `No active sessions found on server`；再次讀回得到相同結果與成功結束狀態。這表示可查詢伺服器，只是當時沒有執行中的 session。
8. **建立 CPU session 並執行四格 Notebook。** 新 session 回傳 `Session READY`；硬體讀回為 CPU、Standard。遠端 Python 為 3.13.15，執行檔為 `/usr/bin/python3`。四格依序執行，輸出 14 與 `3 tests passed`，並寫出 `/content/environment-check.json`。
9. **下載結果並結束運算。** CLI 確認 JSON 已下載；讀取本機檔案，核對結果為 14、測試數為 3。停止 session 後回傳 `Session terminated`，再次查詢為 `No active sessions found on server`。這次的雲端資源已釋放。

```sh
uv tool install --python /opt/homebrew/bin/python3 google-colab-cli
colab version
colab --help
```

[Google 官方 CLI 專案](https://github.com/googlecolab/google-colab-cli) 提供操作命令；本文核對了已安裝 0.7.4 的實際說明。首次登入可在自己的終端機執行：

```sh
colab sessions
```

依 CLI 顯示的網址進入 Google，核對帳號與要求的權限，完成授權後，把授權碼直接貼回自己的終端機。不要把授權碼、token 或憑證檔放進文章、版本庫或聊天。CLI 的登入狀態與瀏覽器已登入 Google 是不同的狀態；能打開 Colab 網頁，不代表 CLI 已取得授權。

完成授權後，可在本文 repository 根目錄重現這個流程。以下下載目的地使用目前資料夾，讀者可依自己的目錄調整；每一步成功後再往下執行，下載完成後才停止 session：

```sh
colab new -s application-engineering-first-lesson
colab exec -s application-engineering-first-lesson -f notebooks/application-engineering-colab.ipynb
colab download -s application-engineering-first-lesson /content/environment-check.json ./environment-check-colab.json
colab stop -s application-engineering-first-lesson
```

第一行未指定 GPU 或 TPU，依 0.7.4 的命令說明會要求 CPU runtime。先用它驗證連線、執行、下載與釋放資源；等課程需要 GPU 時，再根據模型需求、配額與可用機型選擇。若中間任一步失敗，記錄該錯誤並確認 session 狀態，已建立的 runtime 在不再使用時仍應停止。

本文四格程式先在本機乾淨的 Python 程序驗證，再於真實 Colab CPU runtime 執行。下載回來的 [環境測試紀錄](https://github.com/ed3c/medium-compiler/blob/main/articles/evidence/colab-dev-environment.json) 內容如下：

```json
{
  "exercise": "colab-dev-environment",
  "python": "3.13.15",
  "input": [
    1,
    2,
    3
  ],
  "result": 14,
  "tests": 3,
  "scope": "environment-and-example-only"
}
```

這份紀錄確認 Python 環境、函式結果與檔案下載流程；它沒有測試 LLM、GPU 推論或訓練，也不代表學員已掌握課程。原始 Notebook 保留未執行的乾淨版本，方便下一次從頭重跑。

## 留下能解釋的成果，再進下一課

完成四格後，可以用自己的話回答三個問題：只存 Notebook 為何可能找不回 JSON？先跑測試格為何會出現 NameError？本例為何不需要 GPU？若只能記得按鈕位置，回到資料流圖，把每一步的輸入、記憶體狀態與保存位置對上。

用英文向同事說明，也只需要兩句有邊界的描述：

**What did you verify?** I checked the Python version and three cases of a small function.

**What can be reproduced?** The notebook defines its inputs and tests in execution order; rerunning those cells recreates the result file.

```text
學習目標：能建立可重跑的第一個練習
  ↓ 選擇 Software Engineering Fundamentals 的環境課
Colab Notebook 保存說明與程式
  ↓ CPU runtime 執行四格
版本檢查 → 平方和 → 三個測試 → JSON 檔
  ↓ 保存 Notebook，另存結果，再順序重跑
確認環境與本例；學習理解由你解釋
  ↓
Git 與協作 → Python environments → 後續工程課
```

[下一課：Git & Collaboration](https://aiengineeringfromscratch.com/lesson?path=phases/00-setup-and-tooling/02-git-and-collaboration&learningPath=software-engineering-fundamentals) 會讓這份可執行成果開始有版本、差異與協作歷史。先把第一份 Notebook 保留下來，它就是接續練習的素材。

課程路徑與原課內容在此以 2026-09-27 核對的公開版本為準；Colab 的介面和 runtime 版本可能更新。這篇文章提供操作指南與可測試範例，不代填學員回答、不更新課程進度，也不把環境測試結果稱為已掌握 Application Engineering。
