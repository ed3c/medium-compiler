# 開發環境設定：練習檔案

配合[逐章學習文章](https://medium-compiler.vercel.app/articles/application-engineering-colab/)使用。這些是本次實作檔案，不取代上游原課的 preflight。

在本資料夾操作，先建立獨立 Python 3.11+ 環境並安裝 numpy、matplotlib、jupyter、torch、torchvision、torchaudio；Node.js 需符合你選用 pnpm 的最低版本，本次是 Node 22.17.1、pnpm 11.7.0、tsx 4.23.15。

```sh
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip install numpy matplotlib jupyter torch torchvision torchaudio
pnpm install --frozen-lockfile
mkdir -p evidence
python hello.py
pnpm exec tsx hello.ts
rustc --edition 2021 hello.rs -o evidence/hello-rust
./evidence/hello-rust
julia hello.jl
python verify_tensor.py
python verify_libraries.py
python verify_compute.py
```

`verify_tensor.py` 是本次 Mac 的 MPS 裝置測試，其他平台不應刪除斷言來冒充同一項驗收。`verify_compute.py` 則會在有 MPS 時使用 MPS，否則使用 CPU，用同一組明確結果檢查計算。

`verify_libraries.py` 會要求 Jupyter kernel 的 Python 環境與啟動檢查程式的環境一致，避免使用到另一份系統 Python。

遠端 Colab 可執行同一個 `verify_compute.py`，但需要下載 `compute-parity.json`，再停止 session。本次結果相同只涵蓋文章列出的運算，不證明硬體、套件全域行為、效能或 LLM 工作負載等效。

套件清單與 pnpm lockfile 保存本次 TypeScript 依賴；工作區只允許 esbuild 的必要建置腳本。Python 套件的實測版本見文章與驗收摘要；未宣稱未來重新安裝會取得完全相同版本。Rust、Julia、uv 與相容的 Node／pnpm 需先依文章準備。
