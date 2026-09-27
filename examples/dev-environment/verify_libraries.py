import json
import sys
from pathlib import Path
import importlib.metadata
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import torchvision, torchaudio
import nbformat
from nbclient import NotebookClient

plt.plot([1, 2, 3], [1, 4, 9])
plt.savefig("evidence/squares.png")
plt.close()
assert Path("evidence/squares.png").stat().st_size > 0
notebook = nbformat.v4.new_notebook(cells=[nbformat.v4.new_code_cell(
    f"import sys\nimport numpy as np\nassert sys.prefix == {sys.prefix!r}\nassert int(np.dot([1,2,3],[1,2,3])) == 14\nprint(sys.executable)\nprint('Jupyter kernel verified')")])
executed = NotebookClient(notebook, timeout=60, kernel_name="python3").execute()
nbformat.write(executed, "evidence/local-jupyter.ipynb")
versions = {p:importlib.metadata.version(p) for p in
            ("numpy", "matplotlib", "jupyter", "torch", "torchvision", "torchaudio")}
versions["matplotlib_render"] = "PASS"
versions["jupyter_kernel"] = "PASS"
Path("evidence/local-libraries.json").write_text(json.dumps(versions,indent=2)+"\n")
print(json.dumps(versions,indent=2))
