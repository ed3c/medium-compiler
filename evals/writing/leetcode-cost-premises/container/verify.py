"""Execute code extracted from the final article. Writes only beside this file."""
from pathlib import Path
import ast
import itertools
import json
import platform
import re
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parent

def oracle(height, x=None):
    # Independent candidate specification: enumerate index combinations.
    areas = []
    for i, j in itertools.combinations(range(len(height)), 2):
        level = height[i] if height[i] < height[j] else height[j]
        width = j - i if x is None else x[j] - x[i]
        areas.append(width * level)
    return sorted(areas)[-1]

class ReadOnlyCountedList(list):
    def __init__(self, values):
        super().__init__(values)
        self.reads = 0
        self.length_reads = 0
    def __getitem__(self, item):
        assert isinstance(item, int), 'Article introduced slicing'
        self.reads += 1
        return super().__getitem__(item)
    def __len__(self):
        self.length_reads += 1
        return super().__len__()
    def __setitem__(self, item, value):
        raise AssertionError('Article attempted input mutation')

class CountLoops(ast.NodeTransformer):
    def tick(self, node, label):
        self.generic_visit(node)
        tick = ast.parse(f"counts['{label}'] += 1").body[0]
        node.body.insert(0, tick)
        return node
    def visit_While(self, node):
        return self.tick(node, 'while')
    def visit_For(self, node):
        label = 'pairs' if isinstance(node.target, ast.Name) and node.target.id == 'j' else 'outer'
        return self.tick(node, label)


def main():
    start = time.perf_counter()
    english = (ROOT / 'article.en.md').read_text()
    chinese = (ROOT / 'article.zh-TW.md').read_text()
    blocks = re.findall(r'```python\n(.*?)```', english, re.S)
    assert len(blocks) == 3
    assert blocks == re.findall(r'```python\n(.*?)```', chinese, re.S)
    source = '\n\n'.join(blocks)
    (ROOT / 'extracted.py').write_text(source)
    scope = {}
    exec(compile(source, str(ROOT / 'extracted.py'), 'exec'), scope)
    direct = scope['max_area_all_pairs']
    fast = scope['Solution']().maxArea
    positions = scope['max_area_at_positions']
    literals = [
        ([1,8,6,2,5,4,8,3,7], 49), ([1,1],1),
        ([2,5,1,4],8), ([3,3,3],6), ([1,3,2],2), ([1,3,3],3),
        ([4,1,3,2],6), ([0,0],0), ([0,10000],0),
        ([10000,10000],10000), ([0,0,0,0],0),
        ([1,2,3,4],4), ([4,3,2,1],4),
    ]
    literal_results = []
    for h, expected in literals:
        before = h.copy()
        actual = (direct(h), fast(h))
        assert actual == (expected, expected), (h, actual, expected)
        assert h == before
        literal_results.append({'height':h,'expected':expected,'all_pairs':actual[0],'two_pointer':actual[1]})
    exhaustive = 0
    for n in range(2,8):
        for values in itertools.product(range(4), repeat=n):
            h = list(values)
            expected = oracle(h)
            assert direct(h) == expected
            assert fast(h) == expected
            assert h == list(values)
            exhaustive += 1
    coordinate_cases = 0
    for n in range(2,6):
        for heights in itertools.product(range(4), repeat=n):
            for gaps in itertools.product((1,3), repeat=n-1):
                x = [0]
                for gap in gaps:
                    x.append(x[-1]+gap)
                h = list(heights)
                before_x = x.copy()
                assert positions(x,h) == oracle(h,x), (x,h)
                assert h == list(heights) and x == before_x
                coordinate_cases += 1
    assert positions([0,1,100],[1,3,2]) == 198
    assert positions([0,1000000000],[10000,10000]) == 10000000000000
    # Practical boundary controls using the unmodified extracted functions.
    boundary = [10000]*100000
    assert fast(boundary) == 999990000
    assert fast([0]*100000) == 0
    assert direct([10000]*300) == 2990000
    assert positions(list(range(100000)),boundary) == 999990000
    # Count the actual article's loops after inserting counter increments only.
    tree = CountLoops().visit(ast.parse(source))
    ast.fix_missing_locations(tree)
    instrumented = {'counts':{'while':0,'pairs':0,'outer':0}}
    exec(compile(tree, '<article with loop counters>', 'exec'), instrumented)
    c = instrumented['counts']
    h = ReadOnlyCountedList([10000]*100000)
    assert instrumented['Solution']().maxArea(h) == 999990000
    assert c['while'] == 99999 and h.reads == 199998 and h.length_reads == 1
    fast_counts = {'iterations':c['while'],'height_reads':h.reads,'length_reads':h.length_reads}
    c['while'] = 0
    h = ReadOnlyCountedList([10000]*300)
    assert instrumented['max_area_all_pairs'](h) == 2990000
    assert c['pairs'] == 44850 and c['outer'] == 299 and h.reads == 89700
    direct_counts = {'pair_evaluations':c['pairs'],'outer_iterations':c['outer'],'height_reads':h.reads,'length_reads':h.length_reads}
    h = ReadOnlyCountedList([1,3,2])
    x = ReadOnlyCountedList([0,1,100])
    assert instrumented['max_area_at_positions'](x,h) == 198
    assert c['while'] == 2 and h.reads == 4 and x.reads == 4
    position_counts = {'iterations':c['while'],'height_reads':h.reads,'coordinate_reads':x.reads}
    # An intentionally wrong rule is a negative control, not a failed correct solution.
    wrong_trace = []
    h = [1,3,3]
    left, right, best = 0,2,0
    while left < right:
        area = (right-left)*min(h[left],h[right])
        best = max(best,area)
        wrong_trace.append({'left':left,'right':right,'area':area,'best':best})
        if h[left] > h[right]:
            left += 1
        else:
            right -= 1
    assert best == 2 and oracle(h) == 3
    (ROOT/'negative-control.json').write_text(json.dumps({'expected_incorrect_result':best,'required_result':3,'trace':wrong_trace},indent=2))
    result = {
        'status':'PASS','python':sys.version,'implementation':platform.python_implementation(),
        'article_code_blocks':len(blocks),'bilingual_code_identical':True,
        'literal_results':literal_results,'exhaustive_height_cases':exhaustive,
        'exhaustive_coordinate_cases':coordinate_cases,
        'statement_boundaries':{'n_max':100000,'height_max':10000,'max_area':999990000,'coordinate_max_area':10000000000000,'zero_case':0,'all_pairs_practical_n':300},
        'counted_controls':{'two_pointer':fast_counts,'all_pairs':direct_counts,'coordinate_adaptation':position_counts},
        'unexpected_failures':[], 'negative_control_expected_failure':'negative-control.json',
        'outside_contract':'Empty/one-wall inputs, negative heights, unordered/mismatched coordinates and non-integer elements are not claimed supported; no invented validation requirement.',
        'elapsed_seconds':time.perf_counter()-start,
    }
    (ROOT/'runtime.json').write_text(json.dumps(result,indent=2))
    print(json.dumps({k:result[k] for k in ('status','python','exhaustive_height_cases','exhaustive_coordinate_cases','counted_controls','elapsed_seconds')},indent=2))

if __name__ == '__main__':
    try:
        main()
    except BaseException:
        failure = traceback.format_exc()
        # Append rather than overwrite to retain every unsuccessful execution.
        with (ROOT/'runtime-failures.log').open('a') as handle:
            handle.write(failure+'\n')
        raise
