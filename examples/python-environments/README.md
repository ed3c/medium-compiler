# Python Environments：可重跑範例

這是 source-explanation 的 agent 實作範例，不登記學員進度。原課來源是 rohitg00/ai-engineering-from-scratch@968da0791b83917c9d8a5ba197ff190fa0b24093，lesson `06-python-environments`。

## 雙套件專案與 lockfile 重建

已在 macOS arm64、Python 3.12.4、uv 0.5.7 執行。把此目錄複製到新的練習目錄，避免覆寫已有環境。先確認 `python3.12` 指向你選定的 Python，再執行：

```sh
uv sync --locked --all-extras --python python3.12
.venv/bin/python verify_environment.py
```

程式檢查 interpreter/prefix、三個套件路徑、NumPy 和 PyTorch CPU 的矩陣結果，輸出所有 installed versions；不使用 API key、不呼叫 Anthropic API、不下載模型。MPS/CUDA 欄位只是可用性讀回，未做 GPU 計算驗收。

重新複製 `pyproject.toml`、`uv.lock`、`verify_environment.py` 到另一個空目錄，使用相同 Python 和 extras 重跑。比對輸出的 `installed` 與矩陣結果，兩份路徑應不同。

反例只在複本操作：保留 uv.lock，把 NumPy 宣告改為 1.26.4，執行 `uv sync --locked --all-extras` 應拒絕且 lock 不變。還原宣告再同步。日常若確實想改版本，則應重新解析 lock、審查差異並重測；不可把本反例的還原當作每次升級的做法。

## 原始 setup 與 NumPy 隔離

先讀 [原始 setup](https://github.com/rohitg00/ai-engineering-from-scratch/blob/968da0791b83917c9d8a5ba197ff190fa0b24093/phases/00-setup-and-tooling/06-python-environments/code/env_setup.sh)。它依檔案所在位置找根目錄並重用 `.venv`，請在專用課程副本執行。腳本沒有 lock，未來下載版本可能不同。

第二環境：`uv venv --python python3.12 second`，再執行 `uv pip install --python second/bin/python numpy==1.26.4`。各自執行 Python，讀回 NumPy version、`__file__` 和 `sys.prefix`。不要只看終端提示符。

## 全域安裝練習的安全替代

原要求：不啟用 venv，安裝、觀察套件落點，再移除。本次獨立 Python 3.12.8 仍有 externally-managed 保護，預設全域安裝被拒絕；保留此結果，沒有移除標記或使用 `--break-system-packages`。

改用非 venv Python + 明確外部 target，驗證安裝位置、import 與卸載。下例只在新目錄執行；`LAB_PY` 請設定為本次專用 Python 的絕對路徑：

```sh
"$LAB_PY" -c 'import sys; assert sys.prefix == sys.base_prefix'
"$LAB_PY" -m pip --isolated install --target ./external-packages colorama==0.4.6
PYTHONPATH="$PWD/external-packages" "$LAB_PY" -c 'import colorama; print(colorama.__version__); print(colorama.__file__)'
uv pip uninstall --python "$LAB_PY" --target ./external-packages colorama
PYTHONPATH="$PWD/external-packages" "$LAB_PY" -c 'import importlib.util; assert importlib.util.find_spec("colorama") is None'
```

這驗證了 venv 以外的安裝落點與移除；沒有成功寫入 OS 管理的 global site-packages，也沒有模擬污染其他真實專案。詳見 `articles/evidence/python-environments.json`。`.venv`、套件 cache 和私人路徑不入庫。
