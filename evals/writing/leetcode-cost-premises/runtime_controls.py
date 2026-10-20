"""Replay complete article code against problem-definition controls."""
from pathlib import Path
import ast
import copy
import itertools
import json
import re

ROOT = Path(__file__).resolve().parent


def water(height):
    return max((j - i) * min(height[i], height[j])
               for i in range(len(height)) for j in range(i + 1, len(height)))


def finish(n, prerequisites):
    reach = [[False] * n for _ in range(n)]
    for a, b in prerequisites:
        reach[b][a] = True
    for k in range(n):
        for i in range(n):
            for j in range(n):
                reach[i][j] = reach[i][j] or (reach[i][k] and reach[k][j])
    return not any(reach[i][i] for i in range(n))


def complete_codes(text, method):
    result = []
    fence = chr(96) * 3
    for block in re.findall(r"(?ms)^" + fence + r"python\s*\n(.*?)^" + fence + r"\s*$", text):
        try:
            tree = ast.parse(block)
        except SyntaxError:
            continue
        if any(isinstance(node, ast.ClassDef) and node.name == "Solution"
               and any(isinstance(f, ast.FunctionDef) and f.name == method for f in node.body)
               for node in tree.body):
            result.append(("Solution." + method, block))
        elif method == "maxArea":
            for node in tree.body:
                if isinstance(node, ast.FunctionDef) and node.name in (
                        "max_area_all_pairs", "max_area_at_positions"):
                    result.append((node.name, block))
    if not result:
        raise AssertionError("No complete body solution for " + method)
    return result


def check(case):
    directory = ROOT / case
    method = "maxArea" if case == "container" else "canFinish"
    codes = complete_codes((directory / "article.en.md").read_text(), method)
    if codes != complete_codes((directory / "article.zh-TW.md").read_text(), method):
        raise AssertionError("Bilingual solution blocks differ")
    results = []
    for index, (entry, code) in enumerate(codes):
        ns = {}
        exec(compile(code, str(directory / "article.en.md"), "exec"), ns)
        call = getattr(ns["Solution"](), method) if entry.startswith("Solution.") else ns[entry]
        checks, failures = 0, []

        def one(args, expected, label):
            nonlocal checks
            checks += 1
            try:
                supplied = copy.deepcopy(args)
                actual = call(*supplied)
                if type(actual) is not type(expected) or actual != expected:
                    raise AssertionError("Expected " + str(expected) + ", got " + str(actual))
                if supplied != args:
                    raise AssertionError("Input changed")
            except Exception as exc:
                failures.append({"label": label, "type": type(exc).__name__, "error": str(exc)})

        if case == "container" and entry == "max_area_at_positions":
            one([[0,1,100],[1,3,2]],198,"literal-coordinate")
            for n in range(2,6):
                for gaps in itertools.product((1,7),repeat=n-1):
                    x=[0]
                    for gap in gaps:x.append(x[-1]+gap)
                    for h in itertools.product((0,1,4),repeat=n):
                        expected=max((x[j]-x[i])*min(h[i],h[j])
                                     for i in range(n) for j in range(i+1,n))
                        one([x,list(h)],expected,"all-pairs-coordinate-definition")
            x=[i*1000000000//99999 for i in range(100000)]
            one([x,[10000]*100000],10000000000000,"max-coordinate-span")
            one([list(range(100000)),[0]*100000],0,"max-coordinate-zero")
        elif case == "container":
            for values, expected in [
                ([1,8,6,2,5,4,8,3,7],49), ([1,1],1), ([0,0],0),
                ([4,0,0,4],12), ([1,2,4,3],4), ([2,3,4,5,18,17,6],17)]:
                one([values], expected, "literal")
            for n in range(2,8):
                for values in itertools.product((0,1,4), repeat=n):
                    one([list(values)], water(values), "all-pairs-definition")
            # Large boundaries are for the main recommended Solution, not a
            # separately declared quadratic comparison, if one appears later.
            if entry == "Solution.maxArea":
                one([[10000]*100000],999990000,"max-equal")
                one([[0]*100000],0,"max-zero")
                one([[10000]+[0]*99998+[10000]],999990000,"max-endpoints")
        else:
            for n, edges, expected in [
                (2,[[1,0]],True), (2,[[1,0],[0,1]],False),
                (1,[],True), (1,[[0,0]],False),
                (4,[[1,0],[3,2]],True), (4,[[2,1],[1,2]],False)]:
                one([n,edges],expected,"literal")
            for n in range(1,4):
                pairs = list(itertools.product(range(n), repeat=2))
                for bits in range(1 << len(pairs)):
                    edges = [list(pair) for i,pair in enumerate(pairs) if bits & (1 << i)]
                    one([n,edges],finish(n,edges),"transitive-closure-definition")
            pairs = list(itertools.product(range(4), repeat=2))
            for size in range(5):
                for selected in itertools.combinations(pairs,size):
                    edges = [list(pair) for pair in selected]
                    one([4,edges],finish(4,edges),"four-node-sparse")
            n = 2000
            chain = [[i+1,i] for i in range(n-1)]
            one([n,[]],True,"max-isolated")
            one([n,chain],True,"max-chain")
            one([n,chain+[[0,n-1]]],False,"max-cycle")
            dag = [list(p) for p in itertools.islice(
                ((a,b) for a in range(1,n) for b in range(a)),5000)]
            one([n,dag],True,"max-edges-dag")
            one([n,dag[:-1]+[[1999,1999]]],False,"max-edges-cycle")
        results.append({"code_index":index,"entry":entry,"checks":checks,
                        "passed":checks-len(failures),"failures":failures,
                        "bilingual_solution_identical":True})
    return results


if __name__ == "__main__":
    result = {case:check(case) for case in ("container","courses")}
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if any(item["failures"] for rows in result.values() for item in rows):
        raise SystemExit(1)
