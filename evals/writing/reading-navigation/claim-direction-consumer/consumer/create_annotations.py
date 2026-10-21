import json, os, pathlib, datetime
ROOT=pathlib.Path('/var/folders/l6/44bf7nvs64j60f1mpyy88hdm0000gn/T/reading-navigation-mtgts0x3/pclass-claim-direction')
task=json.loads((ROOT/'task.json').read_text());out=pathlib.Path(task['output_directory'])
records=json.loads((out/'paragraph-read-records.json').read_text());paragraphs={r['path']:r['paragraphs'] for r in records}
slugs=['leetcode-11-container-with-most-water','leetcode-207-course-schedule']
base='/Users/neon/.codex/worktrees/leetcode-article-depth/medium-compiler/articles/'
def para(slug,index,lang='en'):
 return paragraphs[base+slug+('.en.md' if lang=='en' else '.md')][index]
def support(slug,index,quote):
 assert quote in para(slug,index)
 return {'source':slug,'paragraph_index':index,'english_quote':quote,'english_source_path':base+slug+'.en.md','navigation_binding':'alg-four must resolve this source paragraph to its existing anchor'}
def premise(text,*sources):return {'text':text,'supporting_sources':list(sources)}
s1,s2=slugs
p22=support(s1,22,'Python integers are immutable: `left += 1` computes an integer value and rebinds `left`, rather than changing an integer stored inside `height`.')
pwrite=support(s1,22,'An assignment targeting an item such as `height[left]` would write that item; no such assignment occurs here.')
pread=support(s1,22,'Reading `height[left]` retrieves an element without removing it. Assigning that value to `left_height` binds a local name; it does not copy the list.')
pindices=support(s1,10,'These indices are called two pointers here; they are ordinary integer positions, not copied sublists or Python memory addresses.')
p26=support(s2,26,'A growth may copy the old references, so one append is not always constant work.')
ppolicy=support(s2,26,"CPython v3.14.0's [list resize policy](https://github.com/python/cpython/blob/v3.14.0/Objects/listobject.c) reserves spare capacity on single-item growth, roughly one eighth of the requested size beyond the items, with small rounding and padding.")
pmodel=support(s2,23,'Reading or writing one list slot, comparing bounded integers, incrementing a counter, and moving or retaining one object reference are elementary constant-size operations.')
pcopy=support(s2,23,'Allocating or copying `k` slots costs proportional to `k`.')
psequence=support(s2,27,'Final capacity is proportional to the final length, so `d` single-item appends, including their ordinary writes, take `O(d)` total work. This aggregate guarantee is called amortized constant time per append.')
pcondition=support(s2,27,'It applies here because each adjacency list only grows by one appended item at a time; no alternating deletion or bulk update is being smuggled into the argument.')
pderive=support(s2,27,'After growing a sufficiently large list of size `m`, proportional spare room allows at least a fixed fraction of `m` further single-item appends before another growth. Charge the cost proportional to `m` of that growth across those following appends; each receives only a constant charge.')
annotations=[{
 'source':s1,'source_paths':{'zh_tw':base+s1+'.md','en':base+s1+'.en.md'},'paragraph_index':22,
 'concept_id':'integer-local-rebinding-and-input-preservation','content_owner':'speed-reading','binding_consumer':'alg-four','role':'PASSIVE_AND_ACTIVE',
 'explanation_zh_tw':'此處 two pointers 是 integer 位置：讀取 `height[left]` 不會移除元素，綁定 `left_height` 不會複製 list，而 `left += 1` 會重綁 local name。原文另說 item assignment 會寫入指定 item，且本實作沒有這類 assignment；這個例子沒有把 item assignment 說成所有 list 寫入的必要形式。',
 'source_paragraph_zh_tw':para(s1,22,'zh'),
 'reading_projection':{'label':'【極速流暢標註文本】','text':para(s1,22),'format':'faithful_plain_english','added_markers':[]},
 'reading_context':{
  'premises':[
   premise('討論對象是本解法的普通 integer indices `left`、`right`，不是 sublist 或 Python memory address；因此 index 的重綁定與輸入 list 的寫入要分開判讀。',pindices,p22),
   premise('本段分開描述 element retrieval、local-name binding 與 item assignment：讀取不移除元素，local binding 不複製 list；`left += 1` 不會改寫 `height` 裡的 integer。',pread,p22),
   premise('item assignment 的敘述以「這樣的 target 會寫入該 item」為範圍，並明說本實作沒有這種 assignment；它沒有列出所有可能的 list 寫入方式，不能倒推成寫入必須使用 item assignment。',pwrite)
  ],'checkpoint':None},
 'reading_cue':{'label':'閱讀提示（非獨立結論）','text':'此處重綁的是哪個 local name，寫入 item 的敘述涵蓋什麼？'},
 'active':[{
  'id':'rebind-local-name','term':'rebind','sense':'bind a local name to the computed integer value','paragraph_index':22,
  'production_sentences':['In this implementation, `left += 1` rebinds `left` rather than changing an integer stored inside `height`.'],
  'supporting_sources':[p22,pindices],
  'self_expression_cue':'不用照抄原文，用英文說明本實作 `left += 1` 改變哪個 binding，以及它沒有改變 `height` 裡的什麼。指出支援答案的原文句。',
  'meaning_oracle':'答案須區分 local name `left` 與 `height` 內的 integer：運算得到 integer value，然後重綁 `left`；沒有把它說成修改 list item。請引用本段包含 “computes an integer value and rebinds `left`” 的句子。'},
  {'id':'item-assignment-write-example','term':'assignment targeting an item','sense':'an assignment whose target is a list item','paragraph_index':22,
   'production_sentences':['An assignment targeting `height[left]` would write that item, but no such assignment occurs in this implementation.'],
   'supporting_sources':[pwrite],
   'self_expression_cue':'用英文說明原文對 item assignment 的正向敘述，並回答這句是否給出了所有 list 寫入方式的必要條件。請引用原文，勿補外部機制。',
   'meaning_oracle':'可說指定 item 為 assignment target 會寫入該 item，而且本實作沒有這種 assignment；不能把這段當成只有 item assignment 才能寫入 list 的證明。依據是 “An assignment targeting an item such as `height[left]` would write that item; no such assignment occurs here.”；該句沒有排他性的 only 或必要條件。'}]
},{
 'source':s2,'source_paths':{'zh_tw':base+s2+'.md','en':base+s2+'.en.md'},'paragraph_index':26,
 'concept_id':'list-growth-possible-copying-versus-aggregate-append-cost','content_owner':'speed-reading','binding_consumer':'alg-four','role':'PASSIVE_AND_ACTIVE',
 'explanation_zh_tw':'本段針對 CPython v3.14.0 的 adjacency lists：單項成長會預留 spare capacity，擴容可能複製既有 references，因此不能保證每次 `list.append` 都是 constant work。這是可能成本，並非每次 append 或每次成長必然複製。接續第 27 段才藉 append-only sequence 的分攤推導 `O(d)` 總工作；amortized constant time 不代表每次操作都等量。',
 'source_paragraph_zh_tw':para(s2,26,'zh'),
 'reading_projection':{'label':'【極速流暢標註文本】','text':para(s2,26),'format':'faithful_plain_english','added_markers':[]},
 'reading_context':{
  'premises':[
   premise('成本討論限定於這裡的 adjacency lists 與 CPython v3.14.0 單項成長 policy；spare capacity 約為要求大小的八分之一，另含 rounding、padding，不能把近似量讀成精確比例。',ppolicy),
   premise('operation-count model 把搬移一個 reference 視為固定大小工作，配置或複製 `k` slots 的成本則與 `k` 成正比；因此可能複製舊 references 的成長，不能一律當成單次固定工作。',pmodel,pcopy,p26),
   premise('“may copy” 只指出成長可能帶來複製成本，沒有聲稱每次成長必定複製，也沒有聲稱每次 append 都會成長；要保留這個可能性才不會把 aggregate guarantee 誤讀成逐次保證。',p26,support(s2,26,'A list sometimes runs out of allocated slots.')),
   premise('若要接著談 amortized constant time，須連同第 27 段的 append-only 限定與推導：與 `m` 成正比的 spare room 容納固定比例乘上 `m` 次 appends，將與 `m` 成正比的成長成本分攤後，每次只分到 constant charge；包含一般寫入的 `d` 次 appends 總共為 `O(d)`。這個推導沒有涵蓋交替刪除或 bulk update。',pderive,psequence,pcondition)
  ],'checkpoint':None},
 'reading_cue':{'label':'閱讀提示（非獨立結論）','text':'本段的可能成本與第 27 段的整段保證有何不同？'},
 'active':[{
  'id':'spare-capacity-single-item-growth','term':'spare capacity','sense':'slots reserved beyond the currently requested items under the stated growth policy','paragraph_index':26,
  'production_sentences':["CPython v3.14.0's list resize policy reserves spare capacity on single-item growth, but a growth may copy old references."],
  'supporting_sources':[ppolicy,p26],
  'self_expression_cue':'用英文說明此 policy 預留什麼，以及擴容可能增加什麼工作；指出哪個原文字排除了「每次必定複製」的解讀。',
  'meaning_oracle':'答案須保留 single-item growth、spare capacity 與 may copy old references。引用第 26 段 “A growth may copy the old references” 中的 may；不能改為 every growth copies 或 every append grows。'},
  {'id':'amortized-constant-time-append','term':'amortized constant time','sense':'aggregate linear work for the stated append-only sequence, not a uniform per-operation bound','paragraph_index':26,
   'production_sentences':['Although a growth may copy old references, the stated append-only sequence of `d` single-item appends takes `O(d)` total work under the article\'s cost model.'],
   'supporting_sources':[p26,pmodel,pcopy,pderive,psequence,pcondition],
   'self_expression_cue':'連到第 27 段，以英文重建為何本段的可能複製成本能與 `d` 次 appends 的 `O(d)` 總工作並存。引用成本 model、分攤步驟與操作序列限制；若換成交替刪除或 bulk update，原文推導是否已涵蓋？',
   'meaning_oracle':'答案須說總工作與單次成本不同：可能與 `m` 成正比的 growth work，分攤到 spare room 容納的固定比例乘上 `m` 次 appends，每次 constant charge；再保留一般寫入與 bounded-scalar model，才能說整段 `O(d)`。須引用第 23 段的 copying cost 及第 27 段的 charging 與 append-only 限定。交替刪除或 bulk update 未被此推導涵蓋，不能由此宣稱該情況必定成立或必定失敗。'}]
}]
result={'annotation_content_created':True,'source_body_changed':False,'publication_performed':False,'CODEX_THREAD_ID':os.environ.get('CODEX_THREAD_ID'),'annotations':annotations,'handoff_limits':['Only the two requested paragraph annotations were authored; this is not full-article annotation coverage.','No source Git blob or existing manifest was read under the input allowlist; the original feedback producer/alg-four must bind immutable source identity and paragraph anchors.','Pronunciation and display segmentation were not checked against external references; complete faithful plain English is used.','Human response, learning outcomes, independent reader outcomes, website integration and external publication were not observed.']}
(out/'firstdraft.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
(out/'rawoutput.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
# These checks cover literal source binding only, not semantic quality.
checks=[]
for a in annotations:
 slug=a['source'];idx=a['paragraph_index']
 assert a['reading_projection']['text']==para(slug,idx)
 assert a['source_paragraph_zh_tw']==para(slug,idx,'zh')
 assert a['reading_context']['checkpoint'] is None
 refs=[]
 for p in a['reading_context']['premises']:refs.extend(p['supporting_sources'])
 for active in a['active']:refs.extend(active['supporting_sources'])
 for r in refs:assert r['english_quote'] in para(r['source'],r['paragraph_index'])
 checks.append({'source':slug,'paragraph_index':idx,'complete_english_equal_to_source':True,'complete_zh_equal_to_source':True,'all_support_quotes_found_in_bound_paragraph':True,'checkpoint_null_reason':'Descriptive language/container behavior and sequence-cost analysis; no loop-state observation is asserted.'})
source_records=json.loads((out/'source-read-records.json').read_text())
unchanged=all(pathlib.Path(r['path']).read_text()==r['content'] for r in source_records)
assert unchanged
review={'literal_checks':checks,'source_bodies_equal_initial_reads':unchanged,'semantic_quality_claim':None,'pronunciation_evidence':'NOT_AVAILABLE_WITHIN_ALLOWLIST; plain-word fallback','chunk_evidence':'NOT_CHECKED; plain-English fallback','missing_source_identity':'Git blob and manifest deliberately not accessed; binding remains for original producer/alg-four','scope_review_notes':[{'source':s1,'paragraph_index':22,'risk_considered':'Turning the stated item-assignment mechanism into an exclusive or necessary list-write mechanism.','draft_choice':'Keep the positive item-target statement and explicitly avoid its unsupported converse. No claim that all mutations require item assignment.','checkpoint_choice':'No temporal invariant is being projected.'},{'source':s2,'paragraph_index':26,'risk_considered':'Changing may-copy growth into always-copy growth, or treating amortized constant time as constant work for every append.','draft_choice':'Retain may, bind cost model p23 and full charging argument plus append-only restriction p27 for the aggregate statement. Changed operation mix is outside this argument, not automatically a counterexample.','checkpoint_choice':'No live loop state is claimed; append-only operation restriction is a premise rather than an invented observation checkpoint.'}],'failures':[{'stage':'instruction tool display','description':'Combined instruction display was truncated. The lesson-contract and article-content-profile were reread individually in full.'}],'learner_response':'NOT_OBSERVED','external_pronunciation_lookup':'NOT_RUN','external_publication':'NOT_RUN'}
(out/'review-record.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
events=[{'event':'task_read','path':str(ROOT/'task.json'),'tool_chunk':'87e3a0'},{'event':'instructions_read','paths':task['instructions'],'tool_chunk':'54ddd1','saved':'instruction-read-records.json'},{'event':'instruction_reread_after_truncation','file':'lesson-contract.md','tool_chunk':'ab5300'},{'event':'instruction_reread_after_truncation','file':'article-content-profile.md','tool_chunk':'e3bb22'},{'event':'all_sources_read_and_content_saved','paths':task['sources'],'saved':'source-read-records.json','tool_chunk':'1d094f'},{'event':'complete_bodies_displayed','tool_chunks':['1d094f','c4ab69','223bf3','14a179']},{'event':'prose_paragraph_indices_derived','tool_chunk':'8ed6ec','saved':'paragraph-read-records.json'},{'event':'first_draft_saved','path':str(out/'firstdraft.json')},{'event':'raw_output_saved','path':str(out/'rawoutput.json')},{'event':'literal_projection_and_quote_checks_executed','details':checks},{'event':'four_source_bodies_compared_to_initial_read','unchanged':unchanged}]
with (out/'trace.jsonl').open('w') as f:
 for event in events:f.write(json.dumps(event,ensure_ascii=False)+'\n')
print(json.dumps({'CODEX_THREAD_ID':os.environ.get('CODEX_THREAD_ID'),'output':str(out/'rawoutput.json'),'annotations':len(annotations),'source_bodies_unchanged':unchanged,'literal_checks':checks},ensure_ascii=False,indent=2))
