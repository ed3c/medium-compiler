"""Extract final article code; compare independent order enumeration and inspect checkpoints."""
from pathlib import Path
import ast
import collections
import copy
import itertools
import json
import platform
import random
import re
import sys

ROOT = Path(__file__).parent
source = (ROOT / 'article.en.md').read_text()
blocks = re.findall(r'```python\n(.*?)```', source, re.S)
assert len(blocks) == 1
code = blocks[0]
(ROOT / 'extracted_solution.py').write_text(code)
namespace = {}
exec(compile(code, str(ROOT / 'extracted_solution.py'), 'exec'), namespace)
solution = namespace['Solution']()

# Independently enumerate complete candidate schedules. No graph traversal in this oracle.
def oracle(n, pairs):
    for order in itertools.permutations(range(n)):
        position = {v: i for i, v in enumerate(order)}
        if all(position[b] < position[a] for a, b in pairs):
            return True
    return False

checks = 0
failures = []
def run(n, pairs, expected):
    global checks
    before = copy.deepcopy(pairs)
    actual = solution.canFinish(n, pairs)
    assert actual is expected, (n, pairs, expected, actual)
    assert pairs == before, 'input mutation'
    checks += 1

literal = [
    (2, [[1, 0]], True),
    (2, [[1, 0], [0, 1]], False),
    (5, [[1, 0], [2, 0], [3, 1], [3, 2]], True),
    (3, [[1, 0], [0, 1]], False),
    (1, [], True), (1, [[0, 0]], False),
    (2, [[0, 0]], False),
    (4, [[3, 2], [1, 0]], True),
]
for item in literal:
    run(*item)
for n in range(1, 4):
    choices = [(a, b) for a in range(n) for b in range(n)]
    for mask in range(1 << len(choices)):
        pairs = [list(pair) for bit, pair in enumerate(choices) if mask & (1 << bit)]
        run(n, pairs, oracle(n, pairs))
exhaustive_count = checks - len(literal)
rng = random.Random(207)
for n in (4, 5, 6):
    for _ in range(70):
        pairs = [[a, b] for a in range(n) for b in range(n) if rng.random() < .18]
        run(n, pairs, oracle(n, pairs))

# Legal statement boundaries: maximum nodes, zero edges, and exactly 5000 distinct edges.
run(2000, [], True)
chain = [[i, i-1] for i in range(1, 2000)]
run(2000, chain, True)
run(2000, chain + [[0, 1999]], False)
dense = [[a, b] for a in range(2000) for b in range(max(0, a-4), a)][:5000]
assert len(dense) == len(set(map(tuple, dense))) == 5000
run(2000, dense, True)
cycle_dense = dense[:-1] + [[0, 1]]
run(2000, cycle_dense, False)

# Read exact locals in the extracted function at its actual while checkpoint.
tree = ast.parse(code)
while_line = next(node.lineno for node in ast.walk(tree) if isinstance(node, ast.While))
records = []
completed = []
checkpoint_count = 0
class ObservedDeque(collections.deque):
    def popleft(self):
        value = super().popleft()
        assert value not in completed
        completed.append(value)
        return value
namespace['deque'] = ObservedDeque

def trace(frame, event, arg):
    global checkpoint_count
    if frame.f_code.co_filename == str(ROOT / 'extracted_solution.py') and event == 'line' and frame.f_lineno == while_line:
        data = frame.f_locals
        n = data['numCourses']
        pairs = data['prerequisites']
        left = [v for v in range(n) if v not in completed]
        expected_counts = {v: sum(a == v and b not in completed for a, b in pairs) for v in left}
        assert data['finished'] == len(completed)
        assert all(data['remaining'][v] == expected_counts[v] for v in left)
        queue = list(data['ready'])
        assert len(queue) == len(set(queue))
        assert set(queue) == {v for v in left if expected_counts[v] == 0}
        assert not (set(queue) & set(completed))
        assert sum(map(len, data['after'])) == len(pairs)
        checkpoint_count += 1
        records.append({'completed': list(completed), 'remaining': list(data['remaining']), 'ready': queue, 'finished': data['finished']})
    return trace

try:
    sys.settrace(trace)
    for n, pairs, expected in literal:
        completed.clear()
        run(n, pairs, expected)
finally:
    sys.settrace(None)
namespace['deque'] = collections.deque

# A deliberately wrong rule must be rejected by an actual distinguishing case.
def wrong_start_rule(n, pairs):
    return any(not any(a == v for a, b in pairs) for v in range(n))
assert wrong_start_rule(2, [[0, 0]]) is True
assert solution.canFinish(2, [[0, 0]]) is False

# Practical cost controls: all-ready queue, endpoint block crossings, append-only growth.
queue = collections.deque(range(2000))
assert [queue.popleft() for _ in range(2000)] == list(range(2000))
queue = collections.deque([4])
assert queue.append(1) is None and list(queue) == [4, 1]
assert queue.popleft() == 4 and list(queue) == [1]
shared = [[]] * 2
shared[0].append(1)
assert shared == [[1], [1]] and shared[0] is shared[1]
independent = [[] for _ in range(2)]
independent[0].append(1)
assert independent == [[1], []] and independent[0] is not independent[1]
# Observe capacity-related size jumps; this is evidence of this host, not proof of asymptotics.
growth, values, previous = [], [], sys.getsizeof([])
for i in range(2000):
    values.append(i)
    size = sys.getsizeof(values)
    if size != previous:
        growth.append({'length': len(values), 'bytes': size})
        previous = size
# Count reference shifts implied by repeated front removal and the article's literal formula.
assert sum(range(2000)) == 2000 * 1999 // 2 == 1999000

result = {'python': platform.python_version(), 'implementation': platform.python_implementation(),
          'extracted_complete_solutions': len(blocks), 'checks_passed': checks,
          'literal_cases': len(literal), 'exhaustive_graphs_n_1_to_3': exhaustive_count,
          'random_graphs_n_4_to_6': 210, 'statement_boundary_cases': 5,
          'checkpoint_observations': checkpoint_count, 'checkpoint_states': records,
          'container_controls': 'PASS', 'wrong_rule_distinguished': True,
          'append_capacity_observations': growth, 'failures': failures,
          'limits': 'Finite controls establish sampled behavior, not asymptotic proof or learner understanding. CPython source analysis is pinned to v3.14.0; runtime version is reported separately.'}
(ROOT / 'runtime.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('checkpoint_states','append_capacity_observations')}, indent=2))
