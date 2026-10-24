"""Execute code extracted from the delivered article; retain failures verbatim."""
from pathlib import Path
import ast
import itertools
import json
import platform
import re
import sys
import traceback

ROOT = Path(__file__).resolve().parent
record = {
    'python_version': sys.version,
    'implementation': platform.python_implementation(),
    'executable': sys.executable,
    'commands': ['python3 verify.py'],
    'extracted_complete_solutions': [],
    'literal_checks': [],
    'small_input_checks': 0,
    'small_input_arrays': 0,
    'boundary_checks': [],
    'negative_controls': [],
    'failures': [],
}

def normalized(rows):
    return {tuple(sorted(row)) for row in rows}

def oracle(nums, k=None):
    sizes = range(len(nums) + 1) if k is None else [k]
    return {tuple(sorted(row)) for r in sizes for row in itertools.combinations(nums, r)}

def validate(fn, nums, expected, k=None):
    original = list(nums)
    rows = fn(nums) if k is None else fn(nums, k)
    assert nums == original, ('input mutated', original, nums)
    assert isinstance(rows, list) and all(isinstance(row, list) for row in rows)
    assert normalized(rows) == expected, (fn.__name__, nums, k, rows, expected)
    assert len(rows) == len(expected), ('duplicate rows', fn.__name__, nums, k)
    assert len({id(row) for row in rows}) == len(rows), ('shared row objects', fn.__name__)
    for row in rows:
        assert len(row) == len(set(row)), ('repeated element', row)
        positions = [nums.index(x) for x in row]
        assert positions == sorted(positions), ('input order changed', nums, row)
    return rows

try:
    english = (ROOT / 'article.en.md').read_text()
    chinese = (ROOT / 'article.zh-TW.md').read_text()
    blocks = re.findall(r'```python\n(.*?)```', english, re.S)
    zh_blocks = re.findall(r'```python\n(.*?)```', chinese, re.S)
    assert len(blocks) == 3 and blocks == zh_blocks, 'Complete bilingual code blocks differ'
    namespace = {}
    for index, block in enumerate(blocks):
        ast.parse(block)
        (ROOT / f'extracted-solution-{index + 1}.py').write_text(block)
        exec(compile(block, f'<article-code-{index + 1}>', 'exec'), namespace)
        record['extracted_complete_solutions'].append(f'extracted-solution-{index + 1}.py')
    recursive = namespace['Solution']().subsets
    iterative = namespace['subsets_iterative']
    exact = namespace['subsets_of_size']
    literal = [
        ([2, 5], {(), (2,), (5,), (2, 5)}),
        ([0], {(), (0,)}),
        ([-10, 10], {(), (-10,), (10,), (-10, 10)}),
        ([1, 2, 3], {(), (1,), (2,), (3,), (1, 2), (1, 3), (2, 3), (1, 2, 3)}),
        ([], {()}),
    ]
    for fn in [recursive, iterative]:
        for nums, expected in literal:
            rows = validate(fn, list(nums), expected)
            record['literal_checks'].append({'method': fn.__name__, 'input': nums, 'output': rows})
    assert recursive([2, 5]) == [[], [5], [2], [2, 5]]
    assert iterative([2, 5]) == [[], [2], [5], [2, 5]]
    assert exact([2, 5, 7], 2) == [[5, 7], [2, 7], [2, 5]]
    assert recursive([0, -1]) == [[], [-1], [0], [0, -1]]
    assert iterative([0, -1]) == [[], [0], [-1], [0, -1]]
    assert exact([0, -1], 1) == [[-1], [0]]
    record['article_and_new_reconstruction_order_checks'] = 6
    alphabet = [-2, -1, 0, 1, 2]
    for n in range(6):
        for values in itertools.permutations(alphabet, n):
            nums = list(values)
            record['small_input_arrays'] += 1
            for fn in [recursive, iterative]:
                validate(fn, nums, oracle(nums))
                record['small_input_checks'] += 1
            for k in range(n + 1):
                validate(exact, nums, oracle(nums, k), k)
                record['small_input_checks'] += 1
    boundary = [-10, -8, -6, -4, -2, 0, 2, 4, 6, 10]
    for fn in [recursive, iterative]:
        rows = validate(fn, list(boundary), oracle(boundary))
        assert len(rows) == 1024 and sum(map(len, rows)) == 5120
        record['boundary_checks'].append({'method': fn.__name__, 'n': 10, 'min': -10, 'max': 10, 'rows': len(rows), 'entries': sum(map(len, rows))})
    for k in range(11):
        rows = validate(exact, list(boundary), oracle(boundary, k), k)
        record['boundary_checks'].append({'method': exact.__name__, 'k': k, 'rows': len(rows)})

    # Capture the actual path-return invariant at every recursive call.
    entries = {}
    visits = []
    restores = []
    def tracer(frame, event, arg):
        if frame.f_code.co_name == 'visit' and frame.f_code.co_filename == '<article-code-1>':
            if event == 'call':
                entries[id(frame)] = list(frame.f_locals['path'])
                visits.append({'i': frame.f_locals['i'], 'path_at_entry': list(frame.f_locals['path'])})
            elif event == 'return':
                before = entries.pop(id(frame))
                after = list(frame.f_locals['path'])
                assert before == after, ('restoration failed', before, after)
                restores.append({'i': frame.f_locals['i'], 'path_at_return': after})
        return tracer
    sys.settrace(tracer)
    try:
        traced = recursive([2, 5])
    finally:
        sys.settrace(None)
    assert len(visits) == len(restores) == 7
    record['actual_program_trace'] = {'input': [2, 5], 'entries': visits, 'returns': restores, 'output': traced}

    # The advertised incorrect approach is run as a deliberately failing control.
    mutant = blocks[0].replace('path.copy()', 'path')
    (ROOT / 'negative-control-alias.py').write_text(mutant)
    bad_ns = {}
    exec(compile(mutant, '<negative-control-alias>', 'exec'), bad_ns)
    bad = bad_ns['Solution']().subsets([2])
    assert bad == [[], []] and bad[0] is bad[1]
    try:
        assert normalized(bad) == {(), (2,)}
    except AssertionError:
        expected_failure = traceback.format_exc()
        (ROOT / 'negative-control-alias.failure.txt').write_text(expected_failure)
        record['negative_controls'].append({'kind': 'advertised aliasing bug', 'input': [2], 'actual': bad, 'same_object': True, 'expected_rejected': True, 'failure_file': 'negative-control-alias.failure.txt'})
    else:
        raise AssertionError('aliasing negative control unexpectedly passed')
    duplicate = recursive([2, 2])
    assert len(duplicate) == 4 and len(normalized(duplicate)) == 3
    record['out_of_contract_controls'] = [{'input': [2, 2], 'actual': duplicate, 'duplicate_membership_detected': True, 'meaning': 'Confirms distinct-value premise is necessary; no support claimed.'}]
    # Repeated use of a Solution instance must not retain a previous result.
    instance = namespace['Solution']()
    previous = instance.subsets([2, 5])
    later = instance.subsets([0])
    assert later == [[], [0]] and previous == [[], [5], [2], [2, 5]]
    record['repeat_call_control'] = True
    record['status'] = 'passed'
except BaseException:
    record['status'] = 'failed'
    record['failures'].append(traceback.format_exc())
    (ROOT / 'runtime.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
    raise
else:
    (ROOT / 'runtime.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': record['status'], 'python': platform.python_version(), 'arrays': record['small_input_arrays'], 'checks': record['small_input_checks'], 'literal_checks': len(record['literal_checks']), 'boundary_checks': len(record['boundary_checks']), 'negative_controls': len(record['negative_controls'])}))
