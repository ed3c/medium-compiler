# Python 環境：讓套件彼此隔離，也讓專案能重新建立

## 學習目標：從「裝好了」走到「知道裝在哪裡」

同一部電腦可以同時執行需要不同套件版本的專案。前提是每個專案使用自己的 Python 環境，而且執行程式與安裝套件時，選到的是同一個環境。本課接續 [Git 與協作](https://medium-compiler.vercel.app/articles/git-collaboration/)，依 [Python Environments 原課](https://aiengineeringfromscratch.com/lesson?path=phases%2F00-setup-and-tooling%2F06-python-environments&learningPath=software-engineering-fundamentals) 完成隔離、依賴宣告、鎖定與錯誤診斷。

原課先決條件是開發環境設定，預估時間約 30 分鐘；實際時間還受套件下載影響。完成操作後，要能指出 Python 與套件的位置、讓兩個 NumPy 版本共存、由宣告和 lockfile 重建 PyTorch 加 Anthropic SDK 的環境，並說明哪些限制沒有因此消失。

這些工作不需要跑大型語言模型。本機記憶體不足以容納某個 LLM，不能推出本機 Python 不能用；本次採用 Mac 的本機 Python。Colab 是需要遠端運算資源時的選項，換成 Colab 仍須管理套件與 runtime，不能代替依賴隔離的概念。

## 問題與概念：每個專案需要自己的套件位置

假設專案 A 要求 PyTorch 2.4，專案 B 因既有程式或相容性限制要求 2.1。若兩者都從同一個 site-packages 讀取同名套件，修改它會同時改變兩個專案的執行條件。Git 能保存程式版本，卻不會自動隔離 Python 套件。

virtual environment，簡稱 venv，是以一個 Python 安裝為基礎建立的環境目錄。它有自己的套件安裝位置；通常保留對基礎 interpreter 的關係，而不是把整個作業系統複製一份。因此兩個環境能各裝一版 NumPy，但仍共用主機的 OS 與硬體。它不是安全沙箱，也不能自己補上不存在的 GPU driver。

需要維持的條件是：專案的安裝工具與執行工具都指向它自己的環境。只看套件名稱或終端提示符無法證明這件事。[Python 的 venv 文件](https://docs.python.org/3/library/venv.html) 提供更可靠的辨識方式：在 venv 內，`sys.prefix` 與 `sys.base_prefix` 不同；也可直接使用環境內 interpreter，不必先 activate。

```text
版本能共用 → 小型基礎環境
版本有衝突 → 每專案分開環境
要重新建立 → pyproject.toml + lockfile
需要 GPU   → 另查硬體、driver 與套件 build
```

上圖的選擇處理不同問題：隔離避免相互覆寫，lockfile 保留一次解析結果，GPU 相容性則仍由執行平台決定。

## 套件從哪裡來：跟著一次安裝追到 import

建立 `.venv` 後，activate 主要調整目前 shell 的環境與命令搜尋順序，讓輸入 `python` 時優先找到環境內執行檔。但工具也能接受明確的 Python 選擇；兩者不一致時，提示符就不足以判斷結果。

本次第一次跑原課腳本時，我在執行器指定了 `UV_PYTHON`，指向 Homebrew 的基礎 Python。腳本成功建立並啟用 `.venv`，但後面的 uv 安裝仍使用那個明確指定的基礎 interpreter，因 externally managed 保護而拒絕。失敗來自我加的選擇覆寫，不能歸咎原課程式，也不能用解除系統保護來修。

正確修復是移除不合適的覆寫，讓安裝使用專案環境；需要精確選擇時，把 `--python` 直接指向該環境的 Python。這個例子可用以下路徑追查：

```text
建立 .venv → 啟用 shell → 工具選擇安裝目標
  指向 Homebrew 基礎 Python → 保護拒絕
  指向專案 .venv           → 安裝到專案套件目錄
專案 Python → import numpy → 讀回 numpy.__file__
```

日常診斷先看實際執行檔，再看 prefix，最後看載入的檔案：

```bash
.venv/bin/python -c 'import sys; print(sys.executable); print(sys.prefix); print(sys.base_prefix)'
.venv/bin/python -c 'import numpy; print(numpy.__version__); print(numpy.__file__)'
```

`which python` 能回答 shell 現在會找哪個命令；`sys.executable` 能回答目前執行中的 Python 是誰；`numpy.__file__` 則把「匯入了哪份套件」落到實際檔案。若環境附有 pip，可用 `python -m pip --version` 檢查它的位置。uv 建立的環境不一定內含 pip，因此沒有 `.venv/bin/pip` 並不等於建置失敗。

原課腳本也有驗證範圍。它先找到 Python 3.11 以上的命令，再交給 uv 建環境；兩個選擇未必是同一 interpreter。它會重用既有根目錄 `.venv`，安裝五項核心套件，檢查 import、版本與一次矩陣乘法。PyTorch 缺少時只警告，是允許的結果。它沒有鎖定版本，也沒有驗證所有平台，更不會判定學員理解。

## 建立它：選一條符合需求的路線

### uv、標準 venv 與 conda

本機已有 uv，所以沿用它建立環境及解析套件。原課推薦 uv，也列出速度宣稱；本次沒有與 pip 做效能比較，不把教材的倍數當成本機實測。

若機器沒有 uv，Python 標準庫的 `venv` 也能提供相同的套件隔離目標：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install numpy
```

執行前先確認 `python3` 是專案支援的版本。有些系統需要另外安裝 venv 支援。這條路線能建立環境，但依賴解析與鎖定仍須另行管理；本次主要實測 uv 路線，沒有宣稱每個工具都實跑。

conda 適合團隊既有 conda 規範，或需要一併管理特定非 Python library 的情境。它不是本課必裝工具。原課示範的 Miniconda 安裝器是 Linux x86_64 版本，不能直接拿到 Apple Silicon Mac 執行；也不能假設舊版 PyTorch conda 指令永遠適用。

「conda 環境完全不能使用 pip」過於絕對。真正風險是兩個管理器看見的狀態不同。依 [conda 官方環境管理說明](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html)，應先安裝 conda 套件，再處理只有 pip 提供的依賴；之後若還要改 conda 依賴，重新建立環境比交替修改容易掌握。這是有條件的做法，並非保證混用不會出錯。

### 按階段拆環境，也衡量成本

原課建議 phases 0–3 共用輕量環境，神經網路課另用 PyTorch 環境，transformers 課依相容性另拆；只呼叫 LLM API 的課可以只裝 SDK。課程編號不能取代相容性判斷：相容需求可以共用，有衝突就分開。

假設有 k 個環境，每個需要安裝一組套件，就有 k 份環境需要建立、驗證與更新。快取能減少重複下載，但不能把所有安裝與維護成本變成零；也不宜把 `.venv` 大小硬套成固定範圍。大型框架及選用平台套件才是容量的重要來源。這次將基本環境、不同 NumPy 版本、雙套件專案與重建環境分開，是為了觀察隔離；日常工作不需要為每個練習都永久保留一份。

### pyproject.toml 表達需求，lockfile 保存解析結果

`pyproject.toml` 是專案設定與依賴宣告的標準位置。例如「需要 NumPy 2.2.6」、「支援 Python 3.12」是條件；resolver 還要選出依賴所需的其他套件。套件 A 需要 B，而 B 又需要 C，C 就是 A 的 transitive dependency。

本課範例把 PyTorch 與 Anthropic SDK 放在兩個 optional dependency extras。extras 可以按需求安裝，並不是「寫在檔案裡就全部已安裝」。同時需要兩者時，必須一起選入。

`uv.lock` 保留套件版本、來源及相關條件。以 `uv sync --locked` 重建時，如果宣告與 lock 不一致，應拒絕而不是偷偷改鎖定結果。不同 OS、CPU、Python 版本或 extras 可能選到不同 wheel 與依賴分支；lockfile 不承諾任何機器都得到逐位元相同的環境。細節見 [uv 的鎖定與同步說明](https://docs.astral.sh/uv/concepts/projects/sync/)。

原課還列出 `uv pip compile pyproject.toml -o requirements.lock` 再安裝 requirements 的路線。它與 uv project 的 `uv.lock` 是不同工作方式；requirements 檔仍有用途，不能說 pyproject 已讓它全面消失。這次選 uv project 路線，提交宣告、lock 與驗證程式，忽略 `.venv/`。虛擬環境含本機路徑，重新建立比把整個環境目錄交給別人可靠。

## 用它：原課程式與四個 Exercises 的操作結果

### 練習一：在獨立目錄執行原始 setup

原程式會依自身位置找到 repository 根目錄，並重用那裡既有的 `.venv`。因此先讀程式，再在本次專用目錄保留相同路徑，執行未修改的 [env_setup.sh](https://github.com/rohitg00/ai-engineering-from-scratch/blob/968da0791b83917c9d8a5ba197ff190fa0b24093/phases/00-setup-and-tooling/06-python-environments/code/env_setup.sh)。沒有拿使用者原本的學習環境試裝新版本。

```bash
bash phases/00-setup-and-tooling/06-python-environments/code/env_setup.sh
```

本機使用 uv 0.5.7。首次建立的是 Python 3.12.4 環境，移除前述錯誤覆寫後，重新使用該環境完成安裝。腳本開頭找到的主機 Python 是 3.14.6，最後實際執行的 venv Python 是 3.12.4；所以應以環境內讀回的版本為準。

結果是 NumPy 2.5.3、matplotlib 3.11.2、scikit-learn 1.9.1、pandas 3.0.6 與 jupyter_core 5.9.1 均可匯入，矩陣乘法執行成功，腳本回報 All checks passed。基礎環境未裝 PyTorch，腳本依原設計發出可選安裝警告。這不代表「所有機器的所有工具都安裝好了」；只證明本課根環境的指定檢查通過。

### 練習二：兩個 NumPy 版本真的互不干擾嗎？

另建第二個環境，指定不同版本；以下的 `python3.12` 必須先解析到可用的 Python 3.12：

```bash
uv venv --python python3.12 second
uv pip install --python second/bin/python numpy==1.26.4
second/bin/python -c 'import numpy; print(numpy.__version__); print(numpy.__file__)'
```

第二個環境載入 NumPy 1.26.4，原環境仍載入 2.5.3。兩者的 `numpy.__file__` 分別落在自己的 site-packages，prefix 也不同；再次檢查原環境，版本並沒有被覆寫。對同一輸入 `[1,2,3]` 求和，兩者都得到 6。

不同版本、不同套件路徑，加上原環境未變，支持「依賴已隔離」；相同的小計算則檢查環境可以工作。它不證明兩版 NumPy 的每個 API 完全等效，也不代表共用主機資源已被隔離。

### 練習三：同一專案使用 PyTorch 與 Anthropic SDK

下面是本次實際使用的宣告。選擇 Python 3.12、固定 NumPy 與 PyTorch，是為了讓範例有明確範圍；不是推薦所有新專案都永遠停在這些版本。

```toml
[project]
name = "python-environments-lesson"
version = "0.1.0"
requires-python = ">=3.12,<3.13"
dependencies = ["numpy==2.2.6"]

[project.optional-dependencies]
torch = ["torch==2.6.0"]
llm = ["anthropic>=0.39,<1"]
```

本範例是直接執行腳本的環境專案，沒有宣告可安裝的 Python package 或 build-system。這裡用 uv 同步依賴，不把它假裝成已完成封裝的 editable package。

```bash
uv lock --python python3.12
uv sync --locked --all-extras --python python3.12
.venv/bin/python verify_environment.py
```

解析結果安裝 NumPy 2.2.6、PyTorch 2.6.0、Anthropic SDK 0.125.0。驗證程式檢查三者都從專案環境載入，再分別用 NumPy 與 PyTorch CPU 計算同一矩陣的平方：

```python
import numpy as np
import torch
import anthropic

a = [[1, 2], [3, 4]]
expected = [[7, 10], [15, 22]]
assert (np.array(a) @ np.array(a)).tolist() == expected
assert (torch.tensor(a) @ torch.tensor(a)).tolist() == expected
assert hasattr(anthropic, "Anthropic")
```

兩種計算都得到 `[[7,10],[15,22]]`。Anthropic SDK 可以匯入並提供客戶端類別；本課不需要 API key，也沒有發出模型請求，因此沒有宣稱雲端推論已驗證。這台 Mac 的 CUDA available 為 false，CUDA build 為 null；這與 Apple Silicon 平台相符，不是本練習失敗。

把宣告、`uv.lock` 和驗證程式複製到全新目錄，再用相同 Python 與 extras 重建。兩份環境安裝的 26 個套件版本完全一致，兩種矩陣結果也一致。這是同一主機條件下的重建實驗，沒有擴張為跨 Linux、Windows 或 NVIDIA GPU 的結果。

接著故意把複本宣告的 NumPy 改成 1.26.4，保留舊 lock。`uv sync --locked --all-extras` 以 exit 2 拒絕，說明 lockfile 需要更新；lock bytes 保持不變。還原宣告後再同步成功。這個反例重要，因為「能安裝」不足以證明實際遵守鎖定檔。

可重跑的 [專案範例](https://github.com/ed3c/medium-compiler/tree/main/examples/python-environments) 包含宣告、lockfile 與完整路徑／計算檢查。讀者應在新的練習目錄使用它，並把 `.venv/` 留在版本控制之外。

### 練習四的替代章節：保留全域保護，仍看見安裝與卸載

原課要求不啟用 venv，故意全域安裝一個套件、觀察落點，再卸載。這一步的學習價值是認識「安裝目標是誰」及清理副作用，不需要故意破壞已有專案。

本次先在專用目錄用 uv 安裝 Python 3.12.8，確認 `sys.prefix == sys.base_prefix`，因此它不是 venv。它帶有 externally-managed 標記；嘗試一般全域安裝 colorama 0.4.6，以 exit 1 被拒絕。這是 [externally managed 環境規範](https://packaging.python.org/en/latest/specifications/externally-managed-environments/) 保護管理器所持有環境的行為，不是要求我們解除保護。

改用 pip 的明確 target，把同一個套件裝進本次專用的外部目錄。以下 `LAB_PY` 代表該非 venv Python 的絕對路徑，且指令在新的練習目錄執行：

```bash
"$LAB_PY" -m pip --isolated install --target ./external-packages colorama==0.4.6
PYTHONPATH="$PWD/external-packages" "$LAB_PY" -c 'import colorama; print(colorama.__version__); print(colorama.__file__)'
uv pip uninstall --python "$LAB_PY" --target ./external-packages colorama
PYTHONPATH="$PWD/external-packages" "$LAB_PY" -c 'import importlib.util; assert importlib.util.find_spec("colorama") is None'
```

實際讀回 colorama 0.4.6 的檔案落在 external-packages，程序仍是非 venv；卸載後同樣的搜尋條件找不到套件，目錄內的 colorama 也消失。`PYTHONPATH` 只傳給單次檢查程序，沒有改 shell 啟動設定。`--target` 的語意可查 [pip 官方安裝選項](https://pip.pypa.io/en/stable/cli/pip_install/#cmdoption-t)。

卸載第一次省略 interpreter 時，uv 0.5.7 仍尋找 venv 並拒絕；補上 `--python` 指向同一個專用 Python，便成功只從指定 target 移除。這再次顯示，目標目錄與工具使用哪個 interpreter 是兩個都要明確的選擇。

這個替代已驗證原題中的目標辨識、實際安裝、載入路徑、卸載與事後不存在；沒有成功寫入 OS 管理的 global site-packages，也沒有實際污染其他使用者專案。因此不能宣稱逐字完成「全域安裝成功」，只能說以受控替代完成這部分的可觀察學習目標。前三題依原要求執行，第四題保留原嘗試的拒絕與替代的實測結果。

本次觀察到的目錄關係如下；這是包含關係，不是執行順序：

```text
practice/
  course/.venv/      NumPy 2.5.3 與課程核心套件
  second/           NumPy 1.26.4
  project/          宣告、lock、雙套件環境
  rebuilt/          相同條件重建的環境
  standalone/       Python 3.12.8，非 venv
  external-packages/ 安裝落點；練習後已卸載
```

完整去敏 [操作結果與失敗修復紀錄](https://github.com/ed3c/medium-compiler/blob/main/articles/evidence/python-environments.json) 保留版本、路徑關係與命令回傳。依賴隔離、lock 重建與安裝落點都在本機完成，沒有理由為這一課增加 Colab 或雲端 LLM 費用。

## 常見錯誤與五道原課測驗的直接答案

**virtual environment 解決什麼？** 它讓專案各自持有套件版本，避免同一套件位置被另一個專案覆寫。它不會讓 Python 自動變快，也不是自動升級工具。原課第一題的正確概念是依賴隔離。

**lockfile 記錄什麼？** 它記錄解析出的直接與間接依賴，以及工具所需的來源與條件資訊。第二題要選固定套件版本供重建的答案；不能把它解讀成鎖住程式碼不讓人修改，或保證所有硬體與 OS 都相同。

**怎樣確認使用正確環境？** 第三題給的選項中，`which python` 指向 `.venv/bin/python` 是正確起點。不過它只能回答 Python 命令的選擇，不能單獨證明另一個 pip 命令的身分。完整操作還要看 `sys.prefix`、`sys.base_prefix`、套件檔案位置，以及安裝工具的目標。首次實跑遇到的覆寫正好說明這個差別。

**pip 與 conda 混用為何可能出錯？** 第四題的重點是 pip 的修改繞過 conda 的依賴管理狀態，而非所有 pip 套件都與 conda Python 不相容。需要混用時先 conda 後 pip，並保留完整需求，後續優先重建。

**有 NVIDIA GPU 卻顯示 CUDA unavailable，應判定什麼？** 第五題的預設答案是 PyTorch CUDA build 與 driver 不相容。但真實診斷不能只靠這一行：也可能裝到 CPU-only build、裝置未暴露給程序，或 driver 有問題。先確認實際 NVIDIA 裝置與 driver，再看 `torch.version.cuda` 及 `torch.cuda.is_available()`；原課的 `nvidia-smi` 是 NVIDIA 平台的診斷命令，不是 Mac 本課的必裝工具。

原課有一個需要更正的簡化：新版 NVIDIA driver 可以向後支援較舊 CUDA runtime，不是 CUDA 11.8 和標示 12.x 的 driver 一定互斥。同一主版本的 minor compatibility，以及另外的 forward compatibility，都有適用條件，應查 [NVIDIA 官方相容性說明](https://docs.nvidia.com/deploy/cuda-compatibility/latest/why-cuda-compatibility.html)。單純要求兩個顯示數字相同會導致錯誤排查。本次使用 Apple Silicon，CUDA 的實際相容性沒有在 NVIDIA 主機上驗證。

還有兩個常見誤會。未 activate 並不必然錯；直接指定 `.venv/bin/python` 也能正確執行。反過來，看到提示符也不必然對。另一個是把 `.venv/` 提交進 Git：環境有本機路徑與平台相依內容，應忽略它，提交宣告與 lockfile。若它早已被追蹤，新增忽略規則也不會自動取消追蹤，這與上一課的 Git 規則相同。

用英文簡答可以濃縮成：

- A virtual environment isolates a project's Python packages; it does not isolate the operating system or GPU driver.
- A lockfile records resolved dependencies. Rebuilding still depends on the selected Python, platform and extras.
- Inspect the interpreter and package paths. An activated prompt alone does not prove the install target.

## Master Map 與下一課

```text
專案需求衝突 → 分開 venv → 各自的 site-packages
需求宣告     → pyproject.toml + extras
解析結果     → uv.lock
新環境重建   → sync --locked → 版本與結果讀回
宣告漂移     → 拒絕 → 修復宣告或正式更新 lock
載入錯套件   → 查 interpreter、prefix、package path
GPU 問題     → 另查平台、build、driver
```

本課的結果是 agent 執行並記錄的操作與教學，沒有代填個人的課程測驗，也沒有宣稱學員已掌握。原課沒有獨立 Ship It 章節；保留可重跑範例與公開文章，是這條學習路線的補充成果。教材完整原文與程式可讀 [釘選來源目錄](https://github.com/rohitg00/ai-engineering-from-scratch/tree/968da0791b83917c9d8a5ba197ff190fa0b24093/phases/00-setup-and-tooling/06-python-environments)。

下一課是 [Docker for AI](https://aiengineeringfromscratch.com/lesson?path=phases%2F00-setup-and-tooling%2F07-docker-for-ai&learningPath=software-engineering-fundamentals)。本站下一篇實作文章尚未發布，先連到原課；本篇的工作停在 Python 環境，不把下一課算成已完成。
