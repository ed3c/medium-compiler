import json
import platform
from pathlib import Path
import numpy as np
import torch

device = "mps" if torch.backends.mps.is_available() else "cpu"
values = np.array([1, 2, 3], dtype=np.int64)
dot = int(values @ values)
assert dot == 14
left = torch.tensor([[1., 2.], [3., 4.]], device=device)
product = (left @ left).cpu()
expected = torch.tensor([[7., 10.], [15., 22.]])
torch.testing.assert_close(product, expected, rtol=0, atol=0)
checks = [sum(v*v for v in values.tolist()), sum(v*v for v in []), sum(v*v for v in [-2,3])]
assert checks == [14, 0, 13]
receipt = {"python":platform.python_version(),"numpy":np.__version__,"torch":torch.__version__,
           "device":device,"input":[1,2,3],"dot":dot,"matrix_input":[[1.,2.],[3.,4.]],
           "matrix_result":product.tolist(),"boundary_results":checks,
           "assertions":"PASS","scope":"specified-python-numpy-tensor-computation-only"}
Path("compute-parity.json").write_text(json.dumps(receipt,indent=2)+"\n")
print(json.dumps(receipt,indent=2))
