"""Independent code controls; no prose-quality or human-learning verdict."""
from pathlib import Path
import copy
import itertools
import json
import re

ROOT = Path(__file__).resolve().parent

def codes(path, method):
    blocks = re.findall(r"(?ms)^```python\s*\n(.*?)^```\s*$", path.read_text())
    result = [s for s in blocks if "class Solution:" in s and "def " + method + "(" in s]
    if not result:
        raise AssertionError(f"No standalone complete {method} implementation: {path}")
    return result

def islands_oracle(grid):
    rows, cols = len(grid), len(grid[0])
    land = {r * cols + c for r in range(rows) for c in range(cols) if grid[r][c] == "1"}
    remaining = set(land)
    count = 0
    while remaining:
        closure = {min(remaining)}
        while True:
            enlarged = closure | {v for v in land if any(
                abs(v // cols - u // cols) + abs(v % cols - u % cols) == 1
                for u in closure)}
            if enlarged == closure:
                break
            closure = enlarged
        remaining -= closure
        count += 1
    return count

def intervals_oracle(intervals):
    n = len(intervals)
    reach = [[max(intervals[i][0], intervals[j][0]) <= min(intervals[i][1], intervals[j][1])
              for j in range(n)] for i in range(n)]
    for k in range(n):
        for i in range(n):
            for j in range(n):
                reach[i][j] = reach[i][j] or (reach[i][k] and reach[k][j])
    remaining = set(range(n))
    result = []
    while remaining:
        i = min(remaining)
        component = {j for j in remaining if reach[i][j]}
        result.append((min(intervals[j][0] for j in component), max(intervals[j][1] for j in component)))
        remaining -= component
    return sorted(result)

def normalize(intervals):
    return sorted(tuple(v) for v in intervals)

def check(case):
    method = "numIslands" if case == "islands" else "merge"
    en = ROOT / case / "article.en.md"
    zh = ROOT / case / "article.zh-TW.md"
    english_codes, chinese_codes = codes(en, method), codes(zh, method)
    if english_codes != chinese_codes:
        raise AssertionError(case + ": bilingual standalone code differs")
    results = []
    for code_index, code in enumerate(english_codes):
        namespace = {}
        exec(compile(code, str(en), "exec"), namespace)
        call = getattr(namespace["Solution"](), method)
        failures = []
        passed = total = 0
        def one(data, expected, label):
            nonlocal passed, total
            total += 1
            try:
                supplied = copy.deepcopy(data)
                actual = call(supplied)
                if supplied != data:
                    raise AssertionError("Article promises to preserve input, but changed it")
                actual = actual if case == "islands" else normalize(actual)
                if actual != expected:
                    failures.append({"label": label, "input": data if len(data) < 20 else "large boundary", "expected": expected, "actual": actual})
                else:
                    passed += 1
            except Exception as exc:
                failures.append({"label": label, "error_type": type(exc).__name__, "error": str(exc)})
        if case == "islands":
            literals = [(list(map(list,["1"])),1),(list(map(list,["0"])),0),
                (list(map(list,["10","01"])),2),(list(map(list,["11","11"])),1),
                (list(map(list,["10101"])),3),(list(map(list,["101","010","101"])),5),
                (list(map(list,["110","101","011"])),2)]
            for grid, expected in literals:
                one(grid,expected,"literal")
            for rows in range(1,4):
                for cols in range(1,4):
                    for bits in itertools.product("01",repeat=rows*cols):
                        grid=[list(bits[r*cols:(r+1)*cols]) for r in range(rows)]
                        one(grid,islands_oracle(grid),"small-map-closure")
            one([["1"]*300 for _ in range(300)],1,"max-all-land")
            one([["0"]*300 for _ in range(300)],0,"max-all-water")
            one([["1" if (r+c)%2 == 0 else "0" for c in range(300)] for r in range(300)],45000,"max-checkerboard")
        else:
            literals=[([[1,3],[2,6],[8,10],[15,18]],[(1,6),(8,10),(15,18)]),
                ([[1,4],[4,5]],[(1,5)]),([[4,7],[1,4]],[(1,7)]),
                ([[1,10],[2,3],[4,8]],[(1,10)]),([[1,2],[3,4]],[(1,2),(3,4)]),
                ([[1,4],[2,5],[5,9]],[(1,9)]),([[1,1],[1,1]],[(1,1)]),([[0,0]],[(0,0)])]
            for data,expected in literals:
                one(data,expected,"literal")
            options=[(a,b) for a in range(4) for b in range(a,4)]
            for length in range(1,4):
                for values in itertools.product(options,repeat=length):
                    data=[list(v) for v in values]
                    one(data,intervals_oracle(data),"pairwise-overlap-closure")
            one([[i,i+1] for i in range(9999,-1,-1)],[(0,10000)],"max-touching-chain")
            one([[i,i] for i in range(9999,-1,-1)],[(i,i) for i in range(10000)],"max-disjoint-points")
        results.append({"code_index":code_index,"checks":total,"passed":passed,"failures":failures,"standalone_code_identical_in_both_languages":True})
    return results

if __name__ == "__main__":
    result={case:check(case) for case in ["islands","intervals"]}
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if any(item["failures"] for items in result.values() for item in items):
        raise SystemExit(1)
