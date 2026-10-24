"""Run exactly the complete solution extracted from the final English article."""
from pathlib import Path
import copy
import datetime
import hashlib
import itertools
import json
import platform
import random
import re
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parent
report = {
    'started_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'python': sys.version,
    'implementation': platform.python_implementation(),
    'unexpected_failures': [],
    'intentional_bad_algorithm_witnesses': [],
}
start_time = time.perf_counter()


def oracle(intervals):
    """Connected components of the original pairwise-intersection graph.

    This does not depend on input order, a sorted frontier, or the tested scan.
    """
    unseen = set(range(len(intervals)))
    result = []
    while unseen:
        first = unseen.pop()
        component = [first]
        pending = [first]
        while pending:
            i = pending.pop()
            a, b = intervals[i]
            neighbors = []
            for j in unseen:
                c, d = intervals[j]
                if max(a, c) <= min(b, d):
                    neighbors.append(j)
            for j in neighbors:
                unseen.remove(j)
                component.append(j)
                pending.append(j)
        result.append([
            min(intervals[i][0] for i in component),
            max(intervals[i][1] for i in component),
        ])
    return sorted(result)


def run_case(label, intervals, expected):
    original = copy.deepcopy(intervals)
    outer_id = id(intervals)
    pair_ids = [id(x) for x in intervals]
    got = merge(intervals)
    assert got == expected, (label, intervals, expected, got)
    assert intervals == original, ('input value mutation', label)
    assert id(intervals) == outer_id and [id(x) for x in intervals] == pair_ids
    assert got is not intervals, ('outer alias', label)
    assert not ({id(x) for x in got} & set(pair_ids)), ('inner alias', label)
    assert len({id(x) for x in got}) == len(got), ('shared result pair', label)
    assert all(a <= b for a, b in got), ('invalid pair', label)
    assert all(got[i-1][1] < got[i][0] for i in range(1, len(got))), ('unmerged output', label)
    if got:
        got[0][1] = -1
        assert intervals == original, ('post-return alias', label)


try:
    english = (ROOT / 'article.en.md').read_text()
    blocks = re.findall(r'^```python\n(.*?)^```', english, re.M | re.S)
    assert len(blocks) == 1, ('complete solution count', len(blocks))
    extracted = blocks[0]
    (ROOT / 'extracted-solution.py').write_text(extracted)
    report['english_sha256'] = hashlib.sha256(english.encode()).hexdigest()
    report['solution_sha256'] = hashlib.sha256(extracted.encode()).hexdigest()
    namespace = {}
    exec(compile(extracted, str(ROOT / 'extracted-solution.py'), 'exec'), namespace)
    merge = namespace['Solution']().merge

    literals = [
        ('statement_1', [[1,3],[2,6],[8,10],[15,18]], [[1,6],[8,10],[15,18]]),
        ('statement_2', [[1,4],[4,5]], [[1,5]]),
        ('statement_3', [[4,7],[1,4]], [[1,7]]),
        ('movie', [[8,10],[1,7],[3,4],[7,8],[12,12],[12,14]], [[1,10],[12,14]]),
        ('contained', [[1,5],[2,3]], [[1,5]]),
        ('equality', [[1,2],[2,3]], [[1,3]]),
        ('integer_gap', [[1,2],[3,4]], [[1,2],[3,4]]),
        ('unsorted_bridge', [[5,6],[1,2],[2,5]], [[1,6]]),
        ('chain', [[1,2],[2,3],[3,4]], [[1,4]]),
        ('duplicate', [[2,2],[2,2]], [[2,2]]),
        ('same_start_reverse_ends', [[1,5],[1,2]], [[1,5]]),
        ('min_singleton', [[0,0]], [[0,0]]),
        ('max_singleton', [[10000,10000]], [[10000,10000]]),
        ('full_bounds', [[0,10000]], [[0,10000]]),
        ('extra_empty_outside_statement', [], []),
    ]
    for label, intervals, expected in literals:
        run_case(label, intervals, expected)
    report['literal_cases'] = [{'label': label, 'input': data, 'expected': expected, 'pass': True}
                               for label, data, expected in literals]

    domain = [(a,b) for a in range(4) for b in range(a,4)]
    exhaustive_count = 0
    for n in range(1,5):
        for sequence in itertools.product(domain, repeat=n):
            intervals = [list(pair) for pair in sequence]
            run_case('exhaustive_graph', intervals, oracle(intervals))
            exhaustive_count += 1
    report['independent_small_input'] = {
        'oracle': 'pairwise closed-intersection graph connected components',
        'domain': 'all valid endpoints 0..3, all ordered sequences of 1..4 intervals',
        'cases': exhaustive_count,
        'pass': True,
    }

    boundary = [
        ('n10000_disjoint_points', [[i,i] for i in range(10000)], [[i,i] for i in range(10000)]),
        ('n10000_reverse_touch_chain', [[i,i+1] for i in reversed(range(10000))], [[0,10000]]),
        ('n10000_duplicates_full', [[0,10000] for _ in range(10000)], [[0,10000]]),
        ('n10000_nested', [[i%5001,10000-i%5001] for i in reversed(range(10000))], [[0,10000]]),
    ]
    rng = random.Random(56)
    random_full = [[0,10000]]
    for _ in range(9999):
        a, b = sorted([rng.randrange(10001), rng.randrange(10001)])
        random_full.append([a,b])
    rng.shuffle(random_full)
    boundary.append(('n10000_random_plus_full_cover', random_full, [[0,10000]]))
    report['statement_boundary_controls'] = []
    for label, intervals, expected in boundary:
        began = time.perf_counter()
        run_case(label, intervals, expected)
        report['statement_boundary_controls'].append({
            'label': label, 'n': len(intervals), 'k': len(expected),
            'pass': True, 'elapsed_seconds': time.perf_counter()-began,
        })

    # Intentional negative controls; these are expected rejections, not repaired article code.
    def overwrite_end(intervals):
        result = []
        for a,b in sorted(intervals):
            if not result or a > result[-1][1]:
                result.append([a,b])
            else:
                result[-1][1] = b
        return result

    def equality_gap(intervals):
        result = []
        for a,b in sorted(intervals):
            if not result or a >= result[-1][1]:
                result.append([a,b])
            else:
                result[-1][1] = max(result[-1][1],b)
        return result

    def unsorted_frontier(intervals):
        result = []
        for a,b in intervals:
            if not result or a > result[-1][1]:
                result.append([a,b])
            else:
                result[-1][1] = max(result[-1][1],b)
        return result

    negative_controls = [
        ('overwrite_end', overwrite_end, [[1,5],[2,3]], [[1,5]]),
        ('equality_gap', equality_gap, [[1,2],[2,3]], [[1,3]]),
        ('unsorted_frontier', unsorted_frontier, [[5,6],[1,2],[2,5]], [[1,6]]),
    ]
    for label, bad, data, expected in negative_controls:
        observed = bad(data)
        assert observed != expected, ('negative control did not discriminate', label)
        report['intentional_bad_algorithm_witnesses'].append({
            'algorithm': label, 'input': data, 'required': expected, 'observed_wrong': observed,
            'expected_failure_observed': True,
        })
    report['pass'] = True
except BaseException as exc:
    report['pass'] = False
    report['unexpected_failures'].append({
        'exception': repr(exc), 'traceback': traceback.format_exc(),
    })
    raise
finally:
    report['elapsed_seconds'] = time.perf_counter()-start_time
    report['finished_at_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    (ROOT/'runtime.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({
        'pass': report.get('pass',False),
        'literal_cases': len(report.get('literal_cases',[])),
        'independent_cases': report.get('independent_small_input',{}).get('cases',0),
        'boundary_cases': len(report.get('statement_boundary_controls',[])),
        'unexpected_failures': len(report['unexpected_failures']),
    }))
