from pathlib import Path
import ast
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
ARTICLE = ROOT / 'article.en.md'
records = []
started = time.perf_counter()
result = {
    'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'python': sys.version,
    'implementation': platform.python_implementation(),
    'source_documentation_version': 'Python 3.14 / CPython v3.14.0',
    'runtime_version_matches_documentation': sys.version_info[:2] == (3, 14),
    'cases': records,
    'failures': [],
}


def load_solution(text, filename):
    namespace = {}
    exec(compile(text, filename, 'exec'), namespace)
    return namespace['Solution']().numIslands


def check(label, grid, expected, fn):
    before = [row[:] for row in grid]
    actual = fn(grid)
    if type(actual) is not int or actual != expected:
        raise AssertionError((label, grid, expected, actual))
    if grid != before:
        raise AssertionError((label, 'input mutated', before, grid))
    records.append({'name': label, 'rows': len(grid), 'cols': len(grid[0]),
                    'expected': expected, 'actual': actual, 'input_preserved': True})


def oracle(grid):
    # Independent definition: all-pairs path closure, then distinct reachability groups.
    land = [(r, c) for r in range(len(grid)) for c in range(len(grid[0]))
            if grid[r][c] == '1']
    size = len(land)
    reach = [[i == j or abs(land[i][0] - land[j][0]) +
              abs(land[i][1] - land[j][1]) == 1
              for j in range(size)] for i in range(size)]
    for k in range(size):
        for i in range(size):
            for j in range(size):
                reach[i][j] = reach[i][j] or (reach[i][k] and reach[k][j])
    return len({tuple(row) for row in reach})


try:
    blocks = re.findall(r'```python\n(.*?)```', ARTICLE.read_text(), re.S)
    complete = [block for block in blocks if any(isinstance(n, ast.ClassDef)
                and n.name == 'Solution' for n in ast.parse(block).body)]
    if len(complete) != 1:
        raise AssertionError(('expected exactly one complete solution', len(complete)))
    code = complete[0]
    (ROOT / 'extracted_solution.py').write_text(code)
    result['english_sha256'] = hashlib.sha256(ARTICLE.read_bytes()).hexdigest()
    result['solution_sha256'] = hashlib.sha256(code.encode()).hexdigest()
    fn = load_solution(code, 'article_solution.py')
    literal = [
        ('single_water', ['0'], 0), ('single_land', ['1'], 1),
        ('diagonal', ['10', '01'], 2),
        ('horizontal_pair', ['11'], 1), ('vertical_pair', ['1', '1'], 1),
        ('bridge_below_scan', ['101', '111'], 1),
        ('movie', ['1100', '1101', '0011'], 2),
        ('shared_row_discriminator', ['10', '11'], 1),
        ('no_vertical_wrap', ['1', '0', '1'], 2),
        ('no_horizontal_wrap', ['101'], 2),
        ('closed_ring', ['111', '101', '111'], 1),
        ('separate_edges', ['1001', '0000', '1001'], 4),
        ('statement_example_1', ['11110', '11010', '11000', '00000'], 1),
        ('statement_example_2', ['11000', '11000', '00100', '00011'], 3),
    ]
    for label, rows, expected in literal:
        check(label, [list(row) for row in rows], expected, fn)
    exhaustive = 0
    for rows in range(1, 4):
        for cols in range(1, 4):
            for values in itertools.product('01', repeat=rows * cols):
                grid = [list(values[r * cols:(r + 1) * cols]) for r in range(rows)]
                before = [row[:] for row in grid]
                expected = oracle(grid)
                actual = fn(grid)
                if actual != expected or grid != before:
                    raise AssertionError(('exhaustive', grid, expected, actual))
                exhaustive += 1
    result['exhaustive_small_inputs'] = {'count': exhaustive,
        'shapes': 'every rectangle from 1x1 through 3x3',
        'oracle': 'all-pairs reachability closure; distinct Boolean reachability rows',
        'mismatches': 0, 'all_inputs_preserved': True}
    rng = random.Random(200)
    for i in range(200):
        rows, cols = rng.randrange(1, 6), rng.randrange(1, 6)
        grid = [[rng.choice('01') for _ in range(cols)] for _ in range(rows)]
        before = [row[:] for row in grid]
        expected, actual = oracle(grid), fn(grid)
        if expected != actual or grid != before:
            raise AssertionError(('random', i, grid, expected, actual))
    result['seeded_random'] = {'seed': 200, 'count': 200,
        'max_shape': [5, 5], 'mismatches': 0, 'all_inputs_preserved': True}
    check('maximum_all_water', [['0'] * 300 for _ in range(300)], 0, fn)
    check('maximum_all_land', [['1'] * 300 for _ in range(300)], 1, fn)
    check('maximum_checkerboard', [[str((r + c) % 2) for c in range(300)]
                                  for r in range(300)], 45000, fn)
    check('maximum_single_row', [['1'] * 300], 1, fn)
    check('maximum_single_column', [['1'] for _ in range(300)], 1, fn)
    snake = [['1' if r % 2 == 0 or c == (299 if (r // 2) % 2 == 0 else 0)
              else '0' for c in range(300)] for r in range(300)]
    check('maximum_snake', snake, 1, fn)
    # Capture the real extracted solution's locals at its while checkpoint.
    tree = ast.parse(code)
    while_line = next(n.lineno for n in ast.walk(tree) if isinstance(n, ast.While))
    events = []
    def tracer(frame, event, arg):
        if frame.f_code.co_filename == 'article_solution.py':
            if event == 'line' and frame.f_lineno == while_line:
                state = frame.f_locals
                events.append({'count': state['count'], 'stack': list(state['stack']),
                               'seen': [row[:] for row in state['seen']]})
            return tracer
        return None
    sys.settrace(tracer)
    try:
        movie_result = fn([list(row) for row in ['1100', '1101', '0011']])
    finally:
        sys.settrace(None)
    expected_stacks = [[(0, 0)], [(0, 1), (1, 0)], [(0, 1), (1, 1)],
                       [(0, 1)], [], [(1, 3)], [(2, 3)], [(2, 2)], []]
    if [e['stack'] for e in events] != expected_stacks or movie_result != 2:
        raise AssertionError(('movie trace', events))
    if events[1]['seen'] != [[True, True, False, False],
                            [True, False, False, False], [False] * 4]:
        raise AssertionError(('movie first discovery state', events[1]))
    if events[-1]['seen'] != [[True, True, False, False],
                             [True, True, False, True], [False, False, True, True]]:
        raise AssertionError(('movie final state', events[-1]))
    result['actual_movie_trace'] = events
    # Controls deliberately violate claims; failures are expected, separately labeled.
    controls = []
    for name, mutated, rows, correct in [
        ('shared_row_lists', code.replace('[[False] * cols for _ in range(rows)]',
                                         '[[False] * cols] * rows'), ['10', '11'], 1),
        ('compare_to_integer', code.replace('"1"', '1'), ['1'], 1),
        ('missing_lower_bounds', code.replace('0 <= nr < rows and 0 <= nc < cols',
                                             'nr < rows and nc < cols'), ['1', '0', '1'], 2),
        ('diagonal_connectivity', code.replace(
            '((-1, 0), (0, 1), (1, 0), (0, -1))',
            '((-1, 0), (0, 1), (1, 0), (0, -1), (-1, -1), (-1, 1), (1, -1), (1, 1))'),
         ['10', '01'], 2),
    ]:
        actual = load_solution(mutated, name + '.py')([list(row) for row in rows])
        if actual == correct:
            raise AssertionError(('control failed to discriminate', name, actual))
        controls.append({'name': name, 'grid': rows, 'correct_under_statement': correct,
                         'mutant_result': actual, 'expected_incorrect_result_observed': True})
    # Execute the prose shortcut without repairing it.
    bad_grid = ['101', '111']
    shortcut = sum(v == '1' and (r == 0 or bad_grid[r - 1][c] != '1')
                   and (c == 0 or bad_grid[r][c - 1] != '1')
                   for r, row in enumerate(bad_grid) for c, v in enumerate(row))
    if shortcut != 2 or fn([list(row) for row in bad_grid]) != 1:
        raise AssertionError(('shortcut witness', shortcut))
    result['expected_wrong_approach_controls'] = controls + [
        {'name': 'upper_left_shortcut', 'grid': bad_grid,
         'correct_under_statement': 1, 'wrong_result': shortcut}]
    # Runtime semantics asserted with literal values.
    stack = [(0, 1), (1, 0)]
    assert stack.pop() == (1, 0) and stack == [(0, 1)]
    assert stack.append((1, 1)) is None and stack == [(0, 1), (1, 1)]
    good = [[False] * 2 for _ in range(2)]
    good[0][0] = True
    bad = [[False] * 2] * 2
    bad[0][0] = True
    assert good == [[True, False], [False, False]]
    assert bad == [[True, False], [True, False]]
    result['primitive_controls'] = ['pop return and mutation', 'append return None',
                                    'independent rows', 'shared-row falsifier']
    result['status'] = 'passed'
except BaseException as exc:
    result['status'] = 'failed'
    result['failures'].append({'type': type(exc).__name__, 'error': str(exc),
                               'traceback': traceback.format_exc()})
    raise
finally:
    result['elapsed_seconds'] = time.perf_counter() - started
    result['finished_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    (ROOT / 'runtime.json').write_text(json.dumps(result, indent=2))
    print(json.dumps({'status': result.get('status'), 'literal_and_boundary_cases': len(records),
                      'small_exhaustive_cases': result.get('exhaustive_small_inputs', {}).get('count'),
                      'seeded_random_cases': result.get('seeded_random', {}).get('count'),
                      'failures': len(result['failures']), 'python': sys.version.split()[0]}))
