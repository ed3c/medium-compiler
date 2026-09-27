# 開發環境設定：逐章理解、本機實作與 Colab 操作紀錄

這篇文章依 [Dev Environment 原課](https://aiengineeringfromscratch.com/lesson?path=phases/00-setup-and-tooling/01-dev-environment&learningPath=software-engineering-fundamentals) 的章節，回答每一步為什麼存在、如何操作，以及這次實際驗證了什麼。原網站的 Ship It 應理解為「交付成果」，Exercises 是「練習」，不是運送或運動。

核對日期為 2026-09-27。[AI Engineering from Scratch](https://aiengineeringfromscratch.com/) 首頁標示 20 個 phases、523 lessons；目前選的是 Software Engineering Fundamentals 路線。課程規模不等於本次已安裝所有後續依賴。本篇處理第一課，並保留從 Colab 起步、再回頭完成本機環境的操作歷程。

## Act on this lesson：把閱讀變成證據

**理論。** 原頁提供閱讀、構建、運行、驗證、繼續五個自行勾選的檢查點，並把測驗結果分開顯示。這個設計提醒我們：看懂指令、建立檔案、成功執行、保存證據，是不同的動作。

**實務。** 這次以三份成果回應：可使用的本機課程環境、真正執行過的程式，以及保存下來的檢查結果。原頁行動區還提供 Rust 驗證程式的編譯與執行指令，因此除了 Python preflight，也要實際編譯它。學員自評與測驗仍由學員完成；本文不替你勾選「已完成」。

## 學習目標

第一個目標是能使用 Python、Node.js 與 Rust，而非只看到安裝器成功。對應證據應包含執行檔位置、版本，以及能編譯或執行的小程式。

第二個目標是隔離依賴。Python 虛擬環境讓這門課的 PyTorch 與 Jupyter 不必與其他專案共用；依賴版本紀錄則讓別人知道這次成功使用了哪些組合。

第三個目標是確認運算裝置。GPU 被偵測到只是開始，還要把張量放到裝置上執行，再與 CPU 的預期值比對。這次針對 M1 Pro 使用 MPS；CUDA 不適用於這台 Mac。

第四個目標是能沿著系統、套件管理器、語言執行環境、AI 函式庫四層排錯。本文會用真正發生的 Python 選錯版本與 Node／pnpm 衝突說明，而非假設電腦壞了就全部重裝。

## 問題

最容易混淆的是「安裝過」和「現在這個程序能用」。同一台電腦可以有多個 Python、Node.js 與套件目錄；終端機按 PATH 順序找到的版本，不一定是你以為的那一個。

第一次安裝 Colab CLI 時，雖然系統有 Python 3.14.6，uv 卻選到 3.11.11，而當前 CLI 需要 Python 3.12+。後來檢查 pnpm，指令確實存在，卻由 Node.js 22.11.0 啟動；pnpm 11.7.0 要求至少 22.13，因而拒絕執行。這兩個問題都與 LLM 大小或 GPU 容量無關。

修正方式是讓「工具、執行它的 runtime、安裝依賴的位置」一致，並用原本失敗的命令重新確認。單看另一個終端機曾顯示成功，不能代替目前環境的驗證。

## 概念

**系統層**提供作業系統、shell、Git、編輯器與編譯工具。**套件管理層**負責取得、選擇和記錄依賴，例如 uv、pnpm、cargo、juliaup。**runtime 層**是真正執行程式的 Python、Node.js、Rust 產物與 Julia。**函式庫層**才是 NumPy、PyTorch 等被程式匯入的功能。

這是排錯模型，不是四個永不重疊的盒子。例如 uv 同時能管理 Python 版本與 Python 套件；cargo 也負責建置。實務上要問的是「哪個程序用了哪個路徑，以及失敗發生在哪一步」。

```text
輸入：原始碼 + 明確的 runtime + 該環境的依賴
  → shell 根據 PATH 找到工具
  → runtime 匯入套件或編譯程式
  → CPU / MPS / 遠端 Colab 執行
  → assert 比對預期結果
  → 保存 stdout、結束碼與結果檔
```

本機、雲端 API 與 Colab 也要分開。應用程式可以在本機開發，模型由遠端 API 供應商執行；這條路不需要 Colab。若想自己載入模型權重，再評估模型大小、量化、上下文長度、可用記憶體與速度，必要時改用雲端 GPU。Colab CLI 是操作遠端 runtime 的工具，不會增加本機的顯示記憶體。

這台是 M1 Pro、16 GB 統一記憶體。它能執行本課的工程練習；尚未選模型就不能斷言所有本地 LLM 都跑不了。Apple Silicon 有 [MLX LM](https://github.com/ml-explore/mlx-lm) 等本地推論路徑，但本次沒有做模型 benchmark。以 30 億參數、4-bit 粗估，原始權重約 1.5 GB；還要另計 KV cache、量化附加資料、框架和系統用量，不能把 16 GB 全部當成模型額度。

## 建立它（Build It）

### 步驟 1：系統基礎

**理論。** shell 要能找到工具，編譯器要能產生這台機器可執行的程式。Apple Silicon 應先確認目前程序的架構，避免把 Rosetta 的 x86 環境和 arm64 套件混在一起。

**實務與結果。** 本機讀回為 arm64，已有 Xcode developer directory、Apple clang 21.0.0、Git 2.50.1、curl 與 unzip；補上 wget 1.25.0。Git 不因課文使用 Homebrew 安裝示例就需要再裝一份。Rust 程式後續能編譯並執行，也是系統編譯鏈可用的證據。

```sh
arch
xcode-select -p
xcrun clang --version
git --version
command -v curl wget unzip
```

編輯器沿用現有 Codex。Docker CLI 雖然存在，但 Docker 屬於這條路線後面的獨立課程；本篇不以 CLI 存在宣稱容器服務或 Docker 課程已驗收。

### 步驟 2：使用 uv 管理 Python

**理論。** 安裝 Python 只解決 runtime；虛擬環境決定套件裝到哪裡。啟用環境後要再次確認執行檔與匯入結果，才能避免把另一個專案的套件誤認為本課已準備好。

**實務。** 建立 `~/ai-engineering-learning/.venv`，明確使用本機已有的 Python 3.12.4。原課示範用 uv 下載 Python；這裡沿用已安裝、符合版本條件的 runtime，再由 uv 建立獨立環境，達成同一個隔離目標。

```sh
uv venv --python /opt/homebrew/opt/python@3.12/bin/python3.12 ~/ai-engineering-learning/.venv
uv pip install --python ~/ai-engineering-learning/.venv/bin/python numpy matplotlib jupyter torch torchvision torchaudio
```

以上路徑是這台 Mac 的實際位置，別台機器要先確認自己的 Python 路徑。此次結果：Python 3.12.4、NumPy 2.5.3、Matplotlib 3.11.2、Jupyter 1.1.1。除匯入套件外，已執行 NumPy 內積、產生 Matplotlib PNG，並透過 Jupyter kernel 執行含斷言的 Notebook；kernel 中的 Python 環境也有檢查，避免暗中用了系統 Python。

```python
import numpy as np
vector = np.array([1, 2, 3])
assert int(vector @ vector) == 14
```

### 步驟 3：Node.js 與 pnpm

**理論。** Node.js 是 runtime，pnpm 是套件管理工具；pnpm 自己也需要相容的 Node.js 啟動。工具有安裝而且路徑存在，仍可能因版本不合而不能使用。

**這次失敗與修正。** 預設 PATH 先找到 Node.js 22.11.0，pnpm 11.7.0 則要求至少 22.13。本機另有 nvm 管理的 Node.js 22.17.1；把它放到課程 shell 的 PATH 前面後，pnpm 可以正常執行。沿用 nvm，不再增加 fnm；這是版本管理方法的替代，而非刪掉 Node 的驗收。

課程內安裝 tsx 4.23.15。pnpm 首次擋下 esbuild 0.28.2 的安裝腳本，後續只允許這個已選定依賴的建置，再實際執行 TypeScript。結果為 `Hello, TypeScript!`，不只是 `pnpm --version`。

```sh
source ~/ai-engineering-learning/activate.sh
node --version
pnpm --version
pnpm exec tsx exercises/hello.ts
```

這個修正限定在啟用後的課程 shell，不會宣稱所有終端機的預設 Node 都已改變。

### 步驟 4：Rust

**理論。** rustc 把原始碼編譯成原生程式；cargo 管理 Rust 專案、依賴與建置。顯示版本只能確認入口存在，必須編譯後執行，才知道完整路徑可用。

**實務與結果。** 沿用 rustc 1.93.0、cargo 1.93.0，建立四語言練習中的 Rust Hello World，以 2021 edition 編譯，執行結果為 `Hello, Rust!`。另外也編譯、執行原課行動區指定的 `main.rs`，保存完整輸出。

```sh
rustc --edition 2021 exercises/hello.rs -o evidence/hello-rust
./evidence/hello-rust
```

### 步驟 5：Julia（可選）

**理論。** Julia 在原課安裝步驟中是可選，但課末練習要求四語言 Hello World。若要完成那一道練習，就不能以「可選」把 Julia 的執行結果略過。

**實務與結果。** 本機原先沒有 Julia，這次透過 Homebrew 安裝 juliaup 1.22.7，再由 juliaup 安裝 release channel。讀回版本為 Julia 1.13.1，實際執行 `hello.jl` 得到 `Hello, Julia!`。使用 Homebrew 取得版本管理器，是官方來源的一種安裝選擇；成果仍以 Julia 真正執行為準。

```sh
juliaup status
julia --version
julia exercises/hello.jl
```

### 步驟 6：GPU 設定

**理論。** CUDA 是 NVIDIA 生態系；Apple Silicon 使用 MPS。Mac 上 `CUDA available: False` 不是本課失敗，不能照抄 NVIDIA wheel 的下載來源。

**實務與結果。** 安裝一般 macOS PyTorch 套件後，本機 PyTorch 2.14.0 讀回 MPS 可用。程式把二乘二張量送到 `mps` 上做矩陣乘法，等待裝置完成，再送回 CPU 與預期值比較。結果為 `[[7, 10], [15, 22]]`，裝置為 `mps:0`，比對通過。

```python
import torch
assert torch.backends.mps.is_available()
x = torch.tensor([[1., 2.], [3., 4.]], device="mps")
y = x @ x
torch.mps.synchronize()
torch.testing.assert_close(y.cpu(), torch.tensor([[7., 10.], [15., 22.]]))
```

這證明小型張量可以走 MPS，不證明某個大型 LLM 的容量、速度或訓練可行性。裝置選擇和模型大小仍要在後續實驗另外量測。

### 步驟 7：驗證準備開始的路線

**理論。** preflight 的通過只涵蓋它實際檢查的條件。Python 版的 `--route beginner` 只要求 Python 與 Git；`--show-later` 才展開後續工具。網站的 `learningPath=software-engineering-fundamentals` 不是可直接搬到 `--route` 的參數。

**實務。** 本次保留上游第一課的有界來源快照，位於 `~/ai-engineering-learning/source`，以檔案 Git blob 雜湊核對原始位元組。它含 README 與本課來源，不是假裝已下載全部課程。以下命令從這份來源的根目錄執行：

```sh
source ~/ai-engineering-learning/activate.sh
cd source
python phases/00-setup-and-tooling/01-dev-environment/code/verify.py --route beginner --show-later
```

**結果。** Python preflight 的 2/2 必要檢查通過，列出的 9 個後續項目也全部通過。原課 Rust 版為 5/5 必要、3/3 可選通過；TypeScript 版為 3/3 必要通過。Deno 只在 TypeScript 版被列為可選；本次未額外安裝，不把它當成原課必需工具。

這三份程式沒有完全相同的門檻：Rust／TypeScript 版仍標示 Python 3.10，而課文與 Python 版要求 3.11+。本次使用 3.12.4，同時滿足較嚴格條件；文章保留這個來源差異，不以較寬鬆的 PASS 取代課文目標。

## 替代實作與等效驗證：哪些結果可以相同

本章是原課之外的實作補充。替代方法必須先說明替代哪個目標，再拿相同輸入與判準比較，不能只因為兩邊都有成功訊息就稱為等效。

本機 Python 沿用 Homebrew 提供的 3.12.4，Node 沿用 nvm 的 22.17.1，Juliaup 由 Homebrew 安裝。它們與原課示例的安裝方法不同；版本條件、環境隔離、程式執行和輸出仍接受相同檢查。這次沒有因硬體限制而無法安裝或執行 Python。

### Colab CLI 替代的是遠端計算位置

第一次操作已安裝 Google 官方 `google-colab-cli 0.7.4`。最初 uv 選到 Python 3.11.11 而安裝失敗，指定已存在的 Homebrew Python 3.14.6 後成功。這是 CLI 自己的 runtime，與課程 `.venv` 的 Python、Colab 遠端 Python 是三個不同環境。

```sh
uv tool install --python /opt/homebrew/bin/python3 google-colab-cli
colab version
colab sessions
```

首次 sessions 查詢停在 OAuth 授權，當時先取消；使用者後來在自己的終端機完成 Google 授權，再查詢得到沒有 active sessions。之後才建立 CPU runtime，執行文章的四格練習，下載 JSON 並停止 session。這段歷程證明雲端操作實際發生，不再只是安裝說明。

首次登入時，請開啟 CLI 顯示的 Google 網址，核對帳號與權限，再把授權碼直接貼回同一個終端機，不要貼到文章、版本庫或聊天。Colab 網頁已登入，不等於 CLI 已完成授權。

### 同一份程式，兩個 runtime

為驗證替代結果，這次新增 `verify_compute.py`，原封不動在本機與 Colab CPU 執行。它不用模型 API、不靠隨機回應，而以手算結果當作共同判準：

- NumPy 對 `[1, 2, 3]` 計算內積，預期為 14。
- PyTorch 對 `[[1, 2], [3, 4]]` 做矩陣自乘，預期為 `[[7, 10], [15, 22]]`。
- 平方和測試正常輸入、空輸入、負數輸入，預期依序為 `[14, 0, 13]`。

矩陣第一格是 1×1＋2×3＝7；第二格是 1×2＋2×4＝10。這個預期值不依賴其中一個 runtime 的輸出，所以不是拿兩份可能同錯的結果互相背書。程式還檢查斷言狀態；負向對照把結果故意改錯時，比對必須拒絕。

**實測環境。** 本機為 Python 3.12.4／NumPy 2.5.3／PyTorch 2.14.0，使用 MPS；Colab 為 Python 3.13.15／NumPy 2.1.3／PyTorch 2.11.0+cpu，使用 CPU。版本與裝置不同，指定輸入、向量結果、矩陣結果、邊界測試與斷言狀態逐欄比對相同。

**成立的替代範圍。** 這證明本課所選 Python、NumPy 和小型 PyTorch 計算可以在兩邊得到相同結果。它不證明所有函式、所有數值精度或大型模型都等效，也不證明 Colab CPU 完成了本機 MPS 設定。

**仍然不同的部分。** 本機 `.venv` 留在磁碟上，Colab runtime 有生命週期；本機 Node、Rust 編譯器與四語言練習需各自驗證。若後續改用 Colab GPU，還要另外驗證實際 GPU 型號、記憶體與目標模型，不能沿用這次 CPU 的收據。

## 用它（Use It）

### 回到同一個本機課程環境

下次開新終端機，先進入課程環境，再重跑檢查：

```sh
source ~/ai-engineering-learning/activate.sh
python verify-all.py
```

啟用腳本選擇課程 Node.js 和 Python `.venv`；檢查程式逐項執行，遇到失敗就留下輸出並停止，不靜默跳過。後續課程要加依賴時，在這個環境中明確安裝並更新版本紀錄。

### 從瀏覽器使用 Colab Notebook

開啟 [Google Colab 繁體中文入口](https://colab.research.google.com/?hl=zh-tw)，新增筆記本；或開啟[本文的可重跑 Notebook](https://colab.research.google.com/github/ed3c/medium-compiler/blob/main/notebooks/application-engineering-colab.ipynb)。選 Python 3、CPU／None，按需要保存自己的 Drive 副本，再從上到下執行。

Notebook 是程式、說明與輸出的文件；runtime 是執行它的程序和虛擬機。Notebook 保存了，不代表 runtime 中的每個檔案都保存了。[Colab 官方 FAQ](https://research.google.com/colaboratory/faq.html) 說明這個生命週期差異，因此結果 JSON 要另外下載。

以下保留實際執行的四個程式格。第一格確認 Python，第二格定義函式，第三格測試，第四格輸出 JSON。若先跑第三格而沒有執行第二格，會得到 `NameError`；修正方法是按依賴順序執行，而非重新安裝 Python。

```python
import json
import platform
import sys

print("Python:", platform.python_version())
print("Executable:", sys.executable)
assert sys.version_info >= (3, 11), "需要 Python 3.11+；先檢查執行階段版本"
print("環境檢查通過")
```

```python
def sum_of_squares(values):
    return sum(value * value for value in values)

values = [1, 2, 3]
result = sum_of_squares(values)
print(result)
```

```python
assert sum_of_squares([1, 2, 3]) == 14
assert sum_of_squares([]) == 0
assert sum_of_squares([-2, 3]) == 13
print("3 tests passed")
```

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

第一次雲端執行結果為 Python 3.13.15、14、`3 tests passed`；[下載的原始結果](https://github.com/ed3c/medium-compiler/blob/main/articles/evidence/colab-dev-environment.json) 已保存。執行結束後，重啟 kernel 並從頭跑，才能檢查有沒有依賴隱藏的記憶體狀態。三個整數的平方和只需 CPU；時間是 O(n)，切換 GPU 不會讓 Python 的 `sum` 自動加速。

### 從終端機操作 Colab

在含有本文 Notebook 的 medium-compiler repository 根目錄，可以依序執行：

```sh
colab new -s application-engineering-first-lesson
colab exec -s application-engineering-first-lesson -f notebooks/application-engineering-colab.ipynb
colab download -s application-engineering-first-lesson /content/environment-check.json ./environment-check-colab.json
colab stop -s application-engineering-first-lesson
colab sessions
```

每一步完成後再執行下一步，確認下載成功才停止 session。這次第一次練習與後續等效對照各自建立、使用並停止 CPU session；最後讀回均無 active sessions。若錯誤中止，先確認哪一步成功、哪個 session 還存在，再清理，不能把下載尚未完成的檔案當成果。

## 交付它（Ship It）：留下可重用的成果

原課交付的是環境診斷能力，不是部署一個 LLM 服務。官方 `outputs/prompt-env-check.md` 也先要求辨識失敗所在的層，再給具體修正方法。這次 pnpm 問題就是實例：指令存在，但啟動它的 Node 太舊；修正 PATH 後還要執行 TypeScript 才收尾。

本次成果保存在 `~/ai-engineering-learning/`：啟用腳本、獨立 Python 環境、四語言 Hello World、MPS 測試、共同計算程式、版本鎖定紀錄，以及含 stdout／stderr／結束碼的驗收紀錄。來源快照的版本與檔案雜湊也一併保留。

公開文章另附[實作檔案](https://github.com/ed3c/medium-compiler/tree/main/examples/dev-environment)與[本機／Colab 驗收摘要](https://github.com/ed3c/medium-compiler/blob/main/articles/evidence/dev-environment-local.json)。程式與測試結果可以交付，登入憑證與 runtime token 不屬於學習成果。

## 練習（Exercises）

### 練習 1：執行驗證程式並修正失敗

實作答案是保存「失敗、原因、修正、重驗」的完整鏈。本次包含 Colab CLI 的 Python 選擇、pnpm 與 Node.js 的相容性，以及 tsx 依賴的建置腳本確認。原課 Python、Rust 與 TypeScript 驗證程式均已實跑；比較判準時仍以課文較嚴格的 Python 3.11+ 為準。

### 練習 2：建立 Python 虛擬環境並安裝 PyTorch

課程 `.venv` 已與其他專案分開；除了匯入 PyTorch，還把張量實際送到 MPS，計算、同步、搬回 CPU 並比對。這回答「GPU 是否真的參與本次運算」，比只顯示可用裝置更完整。

### 練習 3：四語言 Hello World

Python、TypeScript、Rust、Julia 的檔案都已建立並執行。Rust 經過編譯才執行，TypeScript 透過課程內的 tsx 執行；結果都留下來。Julia 原先是可選安裝項目，但這一道題目要四種語言，因此這次也完成它。

### 理論練習與參考推理

1. 為什麼 `command -v pnpm` 有結果，執行 pnpm 還是可能失敗？請說明 PATH、Node.js 與套件管理器的關係。
2. 為什麼 Mac 上 CUDA 是 False、MPS 是 True 可以是正確狀態？什麼證據才能說本次運算確實使用 MPS？
3. 本機和 Colab 都算出 14，能否據此說兩套環境完全等效？請指出還沒驗證的範圍，以及應另外保存的檔案。
4. `--route beginner` 顯示 2/2，為什麼還不能宣稱四語言練習都完成？

參考推理一：PATH 先決定啟動哪一個 Node，pnpm 再檢查該版本是否符合自己的需求；存在 pnpm 檔案不代表這組搭配可執行。

參考推理二：CUDA 與 MPS 是不同的 GPU 後端。Mac 應檢查 MPS，再把張量移到裝置、執行並等待完成，最後比對結果；單純 import torch 或顯示裝置可用都不足以證明這次運算用了 GPU。

參考推理三：14 只是一個範例的結果。還應比較其他輸入、矩陣結果、錯誤情況與程式版本；效能、可用記憶體、完整工具鏈和 runtime 檔案持久性不在這次相等的主張中。Notebook 與輸出 JSON 都要保存。

參考推理四：beginner 的兩項是 Python 與 Git，沒有執行四種語言的 Hello World。必須另跑那些程式，再以輸出與結束碼驗收。

以上是文章提供的參考答案，不是學員本人作答。本文提供了工程檢查的實作結果與解釋，但尚未收到學員自己的回答，也未代做原網站測驗。所以「本課環境與練習由代理實作驗證」和「學員已掌握並完成本課」仍是兩個不同狀態。

準備好後，沿所選 Software Engineering Fundamentals 的 13 課順序前進，[下一課是 Git & Collaboration](https://aiengineeringfromscratch.com/lesson?path=phases/00-setup-and-tooling/02-git-and-collaboration&learningPath=software-engineering-fundamentals)。Python preflight 輸出的 Beginner 數學課入口屬於另一條路線，不能因工具提示而悄悄替換你選的課程順序。

本次逐章核對的[原課版本](https://github.com/rohitg00/ai-engineering-from-scratch/blob/968da0791b83917c9d8a5ba197ff190fa0b24093/phases/00-setup-and-tooling/01-dev-environment/docs/en.md)為 `968da0791b83917c9d8a5ba197ff190fa0b24093`。課文與 Python 驗證程式的檔案雜湊仍與前次參考版本相同。後續課程更新時，應依新版本重新檢查，不能沿用舊結果宣稱新要求也通過。
