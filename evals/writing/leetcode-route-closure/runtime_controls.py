"""Execute actual article solutions against independent problem definitions."""
from pathlib import Path
import copy
import itertools
import json
import re

ROOT = Path(__file__).resolve().parent


def complete_codes(text, method):
    blocks = re.findall(r"(?ms)^```python\s*\n(.*?)^```\s*$", text)
    result = []
    for block in blocks:
        if "class Solution:" in block and "def " + method + "(" in block:
            result.append(("Solution", block))
        elif method == "dailyTemperatures" and block.startswith("def daily_temperatures_scan("):
            result.append(("daily_temperatures_scan", block))
        elif method == "subsets" and block.startswith("def subsets_iterative("):
            result.append(("subsets_iterative", block))
        elif method == "subsets" and block.startswith("def subsets_of_size("):
            result.append(("subsets_of_size", block))
    if not result:
        raise AssertionError("No complete article solution for " + method)
    return result


def temperatures_oracle(values):
    return [next((j - i for j in range(i + 1, len(values)) if values[j] > value), 0)
            for i, value in enumerate(values)]


def subsets_oracle(values):
    return sorted(tuple(v) for size in range(len(values) + 1)
                  for v in itertools.combinations(sorted(values), size))


def normalized_subsets(result):
    if not isinstance(result, list) or any(not isinstance(v, list) for v in result):
        raise AssertionError("Expected list of lists")
    normalized = [tuple(sorted(v)) for v in result]
    if len(normalized) != len(set(normalized)):
        raise AssertionError("Duplicate subsets")
    return sorted(normalized)


def check(case):
    method = "dailyTemperatures" if case == "temperatures" else "subsets"
    directory = ROOT / case
    en = (directory / "article.en.md").read_text()
    zh = (directory / "article.zh-TW.md").read_text()
    codes = complete_codes(en, method)
    if codes != complete_codes(zh, method):
        raise AssertionError("Bilingual complete solutions differ")
    results = []
    for index, (entry, code) in enumerate(codes):
        namespace = {}
        exec(compile(code, str(directory / "article.en.md"), "exec"), namespace)
        call = getattr(namespace["Solution"](), method) if entry == "Solution" else namespace[entry]
        failures, checks = [], 0

        def one(values, expected, label, k=None):
            nonlocal checks
            checks += 1
            try:
                supplied = copy.deepcopy(values)
                actual = call(supplied) if k is None else call(supplied, k)
                if supplied != values:
                    raise AssertionError("Article promises unchanged input")
                if case == "subsets":
                    actual = normalized_subsets(actual)
                elif not isinstance(actual, list) or any(type(v) is not int for v in actual):
                    raise AssertionError("Expected integer answer list")
                if actual != expected:
                    failures.append({"label": label, "input": values if len(values) < 20 else "large boundary",
                                     "expected": expected if len(expected) < 20 else "large expected output",
                                     "actual": actual if len(actual) < 20 else "large mismatching output"})
            except Exception as exc:
                failures.append({"label": label, "type": type(exc).__name__, "error": str(exc)})

        if case == "temperatures":
            literals = [([73,74,75,71,69,72,76,73],[1,1,4,2,1,1,0,0]),
                        ([30],[0]),([100,100],[0,0]),([40,40,41],[2,1,0]),
                        ([100,30,99],[0,1,0]),([30,40,50,60],[1,1,1,0])]
            for values, expected in literals:
                one(values, expected, "literal")
            for size in range(1,8):
                for values in itertools.product((30,31,32), repeat=size):
                    one(list(values), temperatures_oracle(values), "first-future-strictly-warmer")
            # The article's complete Solution is the recommended linear method.
            # Its explicitly quadratic scan alternative is checked on small inputs.
            if entry == "Solution":
                size = 100000
                one([70]*size,[0]*size,"max-equal")
                one([30]*(size-1)+[31],list(range(size-1,0,-1))+[0],"max-delayed-warmer")
                one([30,31]*(size//2),[1,0]*(size//2),"max-alternating")
        else:
            literals = [([0],[(),(0,)]),([1,2],[(),(1,),(1,2),(2,)]),
                        ([-1,0,2],[(),(-1,),(-1,0),(-1,0,2),(-1,2),(0,),(0,2),(2,)])]

            def subsets_case(values, expected, label, boundary=False):
                if entry == "subsets_of_size":
                    choices = (0,1,5,10) if boundary else range(len(values)+1)
                    for k in choices:
                        one(values,[row for row in expected if len(row)==k],label+f"-k={k}",k)
                else:
                    one(values,expected,label)

            for values, expected in literals:
                subsets_case(values, sorted(expected), "literal")
            for size in range(1,6):
                for values in itertools.permutations((-2,-1,0,1,2),size):
                    subsets_case(list(values),subsets_oracle(values),"all-combinations-definition")
            for values in (list(range(10)),list(range(-10,0))):
                subsets_case(values,subsets_oracle(values),"max-distinct-input",boundary=True)
        results.append({"code_index":index,"entry":entry,"checks":checks,"passed":checks-len(failures),
                        "failures":failures,"bilingual_solution_identical":True})
    return results


if __name__ == "__main__":
    result = {case:check(case) for case in ("temperatures","subsets")}
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if any(v["failures"] for values in result.values() for v in values):
        raise SystemExit(1)
