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
result = {'runtime': sys.version, 'implementation': platform.python_implementation(),
          'executed': False, 'unexpected_failures': [], 'negative_controls': []}
started = time.perf_counter()


def check(got, expected, label):
    if got != expected:
        raise AssertionError(f'{label}: got {got!r}; expected {expected!r}')


def oracle(values, equal=False):
    out = []
    for i, value in enumerate(values):
        qualifying = [j for j in range(i + 1, len(values))
                      if values[j] > value or (equal and values[j] == value)]
        out.append(min(qualifying) - i if qualifying else 0)
    return out


def load(code):
    namespace = {}
    exec(compile(code, '<extracted final English>', 'exec'), namespace)
    return namespace


try:
    english = (ROOT / 'article.en.md').read_text()
    blocks = re.findall(r'```python\n(.*?)```', english, re.S)
    check(len(blocks), 2, 'complete article code block count')
    for i, code in enumerate(blocks):
        ast.parse(code)
        (ROOT / f'extracted-{i + 1}.py').write_text(code)
    scan = load(blocks[0])['daily_temperatures_scan']
    main = load(blocks[1])['Solution']().dailyTemperatures
    pivot_code = blocks[1].replace('temperature > temperatures[pending[-1]]',
                                   'temperature >= temperatures[pending[-1]]')
    assert pivot_code != blocks[1]
    (ROOT / 'extracted-warmer-or-equal-adaptation.py').write_text(pivot_code)
    pivot = load(pivot_code)['Solution']().dailyTemperatures
    result['extraction'] = {'complete_solutions': 2, 'pivot': 'explicit prose-directed comparison substitution; not a third complete article code block'}
    literals = [
        ([73,74,75,71,69,72,76,73], [1,1,4,2,1,1,0,0]),
        ([30,40,50,60], [1,1,1,0]),
        ([30,60,90], [1,1,0]),
        ([70,70,69,72,71], [3,2,1,0,0]),
        ([70,70], [0,0]),
        ([71,70,72], [2,1,0]),
        ([70,70,71], [2,1,0]),
        ([72,70,71,73], [3,1,1,0]),
        ([30], [0]),
        ([100], [0]),
        ([100,30], [0,0]),
        ([30,100], [1,0]),
    ]
    for values, expected in literals:
        check(oracle(values), expected, 'literal oracle')
        for label, method in [('scan', scan), ('stack', main)]:
            incoming = values.copy()
            got = method(incoming)
            check(got, expected, f'{label} literal {values}')
            check(incoming, values, f'{label} input preservation')
            assert got is not incoming
    result['literal_cases'] = len(literals)
    exhaustive = 0
    for n in range(1, 9):
        for sequence in itertools.product((30, 31, 32), repeat=n):
            values = list(sequence)
            expected = oracle(values)
            check(main(values), expected, 'exhaustive stack')
            check(scan(values), expected, 'exhaustive scan')
            check(pivot(values), oracle(values, equal=True), 'exhaustive changed contract')
            exhaustive += 1
    result['exhaustive'] = {'alphabet': [30,31,32], 'lengths': [1,8],
                            'inputs': exhaustive, 'methods_checked': ['scan','stack','warmer-or-equal adaptation']}
    n = 100_000
    ascending = [30 + i % 71 for i in range(n)]
    ascending_expected = [1 if value < 100 and i < n - 1 else 0 for i,value in enumerate(ascending)]
    boundaries = [
        ('maximum-length equal minimum', [30] * n, [0] * n),
        ('maximum-length equal maximum', [100] * n, [0] * n),
        ('maximum-length mass pop', [70] * (n-1) + [100], list(range(n-1,0,-1)) + [0]),
        ('maximum-length alternating endpoints', [30,100] * (n//2), [1,0] * (n//2)),
        ('maximum-length bounded increasing cycles', ascending, ascending_expected),
        ('full-range descending', list(range(100,29,-1)), [0] * 71),
        ('full-range ascending', list(range(30,101)), [1] * 70 + [0]),
    ]
    result['boundaries'] = []
    for label, values, expected in boundaries:
        before = values.copy()
        t = time.perf_counter()
        check(main(values), expected, label)
        check(values, before, label + ' preserves input')
        result['boundaries'].append({'case':label,'n':len(values),'passed':True,
                                     'seconds':time.perf_counter()-t})
    check(pivot([70,70,71]), [1,1,0], 'changed contract witness')
    check(pivot([70]*n), [1]*(n-1)+[0], 'changed contract maximum-length equality')
    result['negative_controls'] = []
    mutants = [
        ('wrong-strictness', pivot_code, [70,70], [0,0], [1,0]),
        ('wrong-single-if', blocks[1].replace('while pending and', 'if pending and'),
         [71,70,72], [2,1,0], [0,1,0]),
    ]
    for label, code, values, expected, wrong in mutants:
        (ROOT / f'{label}.py').write_text(code)
        got = load(code)['Solution']().dailyTemperatures(values)
        check(got, wrong, label + ' actual wrong output')
        assert got != expected
        result['negative_controls'].append({'variant':label,'input':values,
                                           'expected_under_original_statement':expected,
                                           'observed_wrong_output':got,'mismatch_expected':True})
    class AuditList(list):
        instance = None
        def __init__(self):
            super().__init__()
            self.pushes = self.pops = self.maximum = 0
            self.events = []
            AuditList.instance = self
        def append(self, value):
            super().append(value)
            self.pushes += 1
            self.maximum = max(self.maximum, len(self))
            if self.pushes <= 5:
                self.events.append({'action':'append','index':value,'after':list(self)})
        def pop(self):
            value = super().pop()
            self.pops += 1
            if self.pushes <= 5:
                self.events.append({'action':'pop','returned':value,'after':list(self)})
            return value
    instrumented_code = blocks[1].replace('pending = []', 'pending = AuditList()')
    namespace = {'AuditList':AuditList}
    exec(compile(instrumented_code,'<article with observer list>','exec'),namespace)
    observed = namespace['Solution']().dailyTemperatures
    check(observed([70,70,69,72,71]), [3,2,1,0,0], 'observed program movie')
    result['program_movie_events'] = AuditList.instance.events
    observed([70]*(n-1)+[100])
    audit = AuditList.instance
    result['observed_mass_pop'] = {'n':n,'appends':audit.pushes,'pops':audit.pops,'maximum_pending':audit.maximum,
                                    'qualification':'observer subclass substituted only for empty pending list; primary tests run exact extracted code'}
    result['bilingual_code_identical'] = re.findall(r'```python\n(.*?)```',(ROOT/'article.zh-TW.md').read_text(),re.S) == blocks
    assert result['bilingual_code_identical']
    result['out_of_contract'] = 'Empty input, temperatures outside 30..100, and n >100000 are not required and were not treated as statement cases.'
    result['executed'] = True
except Exception:
    result['unexpected_failures'].append(traceback.format_exc())
    raise
finally:
    result['elapsed_seconds'] = time.perf_counter() - started
    (ROOT / 'runtime.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))
