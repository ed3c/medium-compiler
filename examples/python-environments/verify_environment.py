import importlib.metadata as md
import json
import sys
from pathlib import Path
import numpy as np
import torch
import anthropic

assert sys.prefix != sys.base_prefix, "Expected an isolated virtual environment"
prefix = Path(sys.prefix).resolve()
modules = (np, torch, anthropic)
for module in modules:
    assert Path(module.__file__).resolve().is_relative_to(prefix), module.__file__
a = [[1, 2], [3, 4]]
expected = [[7, 10], [15, 22]]
numpy_result = (np.array(a) @ np.array(a)).tolist()
torch_result = (torch.tensor(a) @ torch.tensor(a)).tolist()
assert numpy_result == expected == torch_result
assert hasattr(anthropic, "Anthropic")
print(json.dumps({
    "python": sys.version.split()[0],
    "executable": sys.executable,
    "prefix": sys.prefix,
    "base_prefix": sys.base_prefix,
    "versions": {name: md.version(name) for name in ("numpy", "torch", "anthropic")},
    "package_paths": {m.__name__: m.__file__ for m in modules},
    "numpy_matrix": numpy_result,
    "torch_cpu_matrix": torch_result,
    "cuda_available": torch.cuda.is_available(),
    "torch_cuda_build": torch.version.cuda,
    "mps_available": torch.backends.mps.is_available(),
    "anthropic_api_call": "NOT_RUN",
    "installed": sorted((d.metadata["Name"].lower(), d.version) for d in md.distributions()),
}, indent=2))
