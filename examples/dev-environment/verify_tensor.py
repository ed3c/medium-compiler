import json
import platform
from pathlib import Path
import numpy as np
import torch

vector = np.array([1, 2, 3])
assert int(np.dot(vector, vector)) == 14
assert torch.backends.mps.is_available(), "This Mac must expose MPS for this device-specific test"
cpu = torch.tensor([[1., 2.], [3., 4.]])
expected = cpu @ cpu
gpu = cpu.to("mps")
actual = gpu @ gpu
torch.mps.synchronize()
torch.testing.assert_close(actual.cpu(), expected)
receipt = {"python": platform.python_version(), "numpy": np.__version__,
           "torch": torch.__version__, "numpy_dot": 14,
           "cuda_available": torch.cuda.is_available(), "mps_available": True,
           "actual_device": str(actual.device), "tensor_result": actual.cpu().tolist(),
           "cpu_mps_match": True, "scope": "environment-and-small-tensor-only"}
Path("evidence/local-tensor.json").write_text(json.dumps(receipt, indent=2)+"\n")
print(json.dumps(receipt, indent=2))
