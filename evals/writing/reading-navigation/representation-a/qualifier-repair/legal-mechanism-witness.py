from pathlib import Path
import json,re
P=Path('/tmp/speed-reading-a-qualifiers-49d7u1dd')
height=[2,5];alias=height;before=height.copy();height.append(1)
assert alias is height and height==[2,5,1]
blocks=re.findall(r"```python\n(.*?)```",(P/'leetcode-11-container-with-most-water.en.md').read_text(),re.S)
code=next(b for b in blocks if 'class Solution:' in b)
ns={};exec(code,ns)
source_input=[2,5];source_before=source_input.copy()
answer=ns['Solution']().maxArea(source_input)
assert answer==2 and source_input==source_before
independent=[list() for _ in range(2)];independent[0].append(1)
assert independent==[[1],[]] and independent[0] is not independent[1]
shared=[[]]*2;shared[0].append(1)
assert shared==[[1],[1]] and shared[0] is shared[1]
result={'water_legal_alternative':{'code':'height=[2,5]; height.append(1)','before':before,'after':height,'same_list_identity':alias is height,'contains_item_assignment':False},'displayed_function':{'extracted_code':code,'input':source_before,'after':source_input,'answer':answer,'preserves_input_for_this_case':True},'course_legal_alternative':{'code':'after=[list() for _ in range(2)]; after[0].append(1)','result':independent,'distinct_inner_lists':independent[0] is not independent[1],'uses_empty_list_literal_allocation':False},'course_repetition_control':{'code':'after=[[]]*2; after[0].append(1)','result':shared,'shared_inner_list':shared[0] is shared[1]},'limit':'These are concrete counterexamples to exclusive mechanism wording, not exhaustive function verification or learner evidence.'}
(P/'legal-mechanism-witness-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False,indent=2))
