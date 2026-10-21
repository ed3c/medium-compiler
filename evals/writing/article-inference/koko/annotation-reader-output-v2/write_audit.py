from pathlib import Path
import json,copy,os,hashlib
r=Path('/var/folders/l6/44bf7nvs64j60f1mpyy88hdm0000gn/T/article-entailment-2x13kv72/koko');inp=r/'annotation-reader-input-v2';out=r/'annotation-reader-output-v2';original_path=r/'annotation-reader-output/audit.json'
old=json.loads(original_path.read_text());d=json.loads((out/'extracted.json').read_text());checks=json.loads((out/'verification.json').read_text())
entries=[];changes=[]
for a,e0 in zip(d['en']['annotations'],old['paragraph_audits']):
 e=copy.deepcopy(e0);i=e['paragraph_index'];oldfields={f['class']:{k:v for k,v in f.items() if k!='verdict'} for f in e0['all_visible_annotation_fields']};newfields=[];changed=[]
 for f in a['fields']:
  same=oldfields.get(f['class'])==f
  if not same:changed.append(f['class']);changes.append({'paragraph_index':i,'field_class':f['class'],'before':oldfields.get(f['class']),'current':f})
  st='NOT_ASSESSED_PROSODY_OR_LEARNING' if f['class'] in ('alg-reading-label','alg-source-explain') else 'PASS_BOUNDED'
  newfields.append({**f,'verdict':st,'judgment_origin':'REUSED_EXACTLY_UNCHANGED' if same else 'NEWLY_READ_AND_REVIEWED_V2'})
 e['all_visible_annotation_fields']=newfields;e['verdict']='PASS_BOUNDED';e['finding_ids']=[];e['changed_field_classes']=changed
 e['review_origin']='NEWLY_READ_AND_REVIEWED_COMPLETE_ANNOTATION_V2' if changed else 'REUSED_EXACTLY_UNCHANGED_ANNOTATION_AND_BODY'
 e['reuse_evidence']='Compared all current visible annotation fields, their target links and current linked body paragraphs against own original audit; exact unchanged content uses prior judgment. All present fields and supporting quotes below are from the current frozen packet.'
 ids=list(dict.fromkeys([f'alg-p-{i}']+[link for f in a['fields'] for link in f['links']]))
 e['supporting_body_quotes']=[{'body_id':bid,'en':d['en']['body'][bid],'zh-TW':d['zh-TW']['body'][bid]} for bid in ids]
 if i==10:
  e['assessment']='本次新讀整則註解與全部連結論證。context 現在明說「最小可行速度不超過 M，且可能恰好等於 M」，Oracle 亦新添 h=n 時最大堆需要 M 的解釋；alg-p-10 的 by M 與 alg-p-21 的 h=n 邊界直接支持，且新 sources link 指到後者。固定正整數 speed、每堆一小時、h>=n、inclusive [1,M] 和初始化 checkpoint 均完整。原問題 KOKO-ANNOTATION-01 在這個 packet 已消除。'
  e['nearby_illegal_inference_rejected']='可以推出 minimum<=M，不能推出存在 k<M 的可行 speed。新 context 和 Oracle 明確允許 minimum=M。'
  e['active_content_confirmation']='Active sentence 與 cue 逐字未變，原判斷沿用；Oracle 新增的 minimum can equal M / when h=n 論證已重新對正文核實。'
 if i==27:
  e['assessment']='本次新讀整則註解與全部連結論證。zh_note 現在把必要且充分限制在「這個允許一小時內跨堆並用滿容量的改題中」，並用原題 [4,4],h=3 表達不能通用；Oracle 同樣明說 in the changed task，保留容量上界與可達構造、(S+h-1)//h、單次 n-pile sum 及 fixed bounded arithmetic。它沒有再要求所有公式成立的個別原題實例都須先改規則。正文 alg-p-27、alg-p-3、alg-p-5 與 cost model alg-p-22 支持全部敘述。原問題 KOKO-ANNOTATION-02 在這個 packet 已消除。'
  e['nearby_illegal_inference_rejected']='跨堆規則提供該改題的一般充分性；原題不能一般套用，不等於原題每個實例必定與總量公式不同。新 zh_note/Oracle 沒有這個反向必要性主張。'
  e['active_content_confirmation']='Active sentence 的 If 前提與 cue 逐字未變，原判斷沿用；整段改寫的 Oracle 已重新對容量機制、一般性範圍及 bounded cost 前提核實。'
 entries.append(e)
resolved=[{'original_finding_id':'KOKO-ANNOTATION-01','paragraph_index':10,'status':'RESOLVED_IN_V2_VISIBLE_TEXT','current_visible_quotes':['答案是正整數 speed，因此至少為 1；speed M 已可行，所以最小可行速度不超過 M，且可能恰好等於 M。','The minimum can equal M: when h = n, every pile must fit into one hour and the largest pile requires speed M.'],'supporting_body_quotes':[{'body_id':'alg-p-10','en':'No positive answer lies below 1, and an answer exists by M, so start with the inclusive interval [low, high] = [1, M].','zh-TW':'正整數答案不可能低於 1，而最遲在 M 就有答案，所以從 inclusive interval [low, high] = [1, M] 開始。'},{'body_id':'alg-p-21','en':'If h = n, each pile must fit into its one hour, so the largest pile forces the answer to be M.','zh-TW':'若 h = n，每堆都必須在分配給自己的一小時內吃完，因此最大那堆迫使答案為 M。'}]},
{'original_finding_id':'KOKO-ANNOTATION-02','paragraph_index':27,'status':'RESOLVED_IN_V2_VISIBLE_TEXT','current_visible_quotes':['在這個允許一小時內跨堆並用滿容量的改題中，h * k >= S 既必要又充分，答案為 ceiling(S / h)。','這個總量判準不能通用於原題，[4,4]、h = 3 就會失敗。','The changed task can attain total capacity h * k across pile boundaries until bananas run out, so h * k >= S is necessary and sufficient and the minimum integer k is (S + h - 1) // h.','Original [4, 4], h = 3 shows that the total-capacity criterion is not a general feasibility test for the original task.'],'supporting_body_quotes':[{'body_id':'alg-p-27','en':'Suppose Koko could switch piles within an hour and use the entire capacity k across them.','zh-TW':'假設 Koko 能在一小時內切換香蕉堆，把完整容量 k 用在多堆之間。'},{'body_id':'alg-p-27','en':'In that changed task, h hours can consume at most h * k bananas, and continuously taking bananas across pile boundaries can achieve that capacity until the supply ends.','zh-TW':'在這個改題版本中，h 小時至多能吃 h * k 根；持續跨堆取香蕉，也能在香蕉吃完前用滿這個容量。'},{'body_id':'alg-p-27','en':'This formula fails for the original [4, 4], h = 3 precisely because that original task does not allow switching piles mid-hour.','zh-TW':'這個公式套在原題的 [4, 4], h = 3 會失敗，正是因為原題不允許在一小時中途換堆。'}]}]
paths=[str(inp/n) for n in ['task.json','article.en.md','article.zh-TW.md','page.en.html','page.zh-TW.html']]+[str(original_path)]
audit={'verdict':'PASS_BOUNDED','CODEX_THREAD_ID':os.environ.get('CODEX_THREAD_ID'),'review_identity':'Same Reader reread of frozen v2, not a second independent Reader.','actual_read_paths':paths,'local_derivative_read_paths':[str(out/'extracted.json'),str(out/'verification.json')],'original_audit_untouched':True,'scope':'All 35 complete current public annotations in both frozen v2 HTML pages and their linked current body arguments; both complete current Markdown bodies and generated trace, code and Master Map.','method':'Parsed all current full annotation fields and current full body text locally. Compared exact text/links to own original audit. Reused only exactly unchanged judgments. Newly read/reviewed complete current annotations at indices 10 and 27, including every unchanged and changed field and linked argument. Rechecked current source/page body, complete English reading text and code/trace/Master Map mechanically. Quotes normalize whitespace only, retaining visual reading markers.','limits':old['limits']+['This is a same-Reader reread; no second independent Reader claim, publishing authority or learner-benefit inference.'],'coverage':{'reviewed_current_count':35,'paragraph_indices':list(range(35)),'exactly_unchanged_annotation_judgments_reused':33,'complete_changed_annotations_newly_reviewed':[10,27],'changed_field_count':len(changes),'annotation_fields_same_across_pages':True,'current_findings_count':0,'pass_count':35},'shared_content_confirmation':{'alg-four-label_shared_decision_labels':'All 35 unchanged byte-for-text/links relative to original audit; prior judgments reused.','alg-skeleton_reading_cues':'All 35 unchanged; remain questions/hints, not independent theorem statements.','alg-active-word_sentences':'All present Active sentences unchanged; prior judgments reused with unchanged linked body premises.','alg-four-recall':'Only indices 10 and 27 changed; both current full cue/Oracle blocks newly read and reviewed.','body_arguments':'All 35 current paragraphs per language equal original quoted body arguments; all current linked body arguments explicitly included per audit entry.'},'findings':[],'resolved_original_findings':resolved,'changes_read':changes,'structural_verification':checks,'paragraph_audits':entries}
for z in resolved:
 e=entries[z['paragraph_index']]
 for q in z['current_visible_quotes']:assert any(q in f['text'] for f in e['all_visible_annotation_fields'])
 for b in z['supporting_body_quotes']:
  for lang in ['en','zh-TW']:assert b[lang] in d[lang]['body'][b['body_id']]
assert [e['paragraph_index'] for e in entries]==list(range(35)) and len(changes)==5
(out/'audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
(out/'findings.json').write_text(json.dumps({'verdict':'PASS_BOUNDED','CODEX_THREAD_ID':audit['CODEX_THREAD_ID'],'review_identity':audit['review_identity'],'findings':[],'resolved_original_findings':resolved},ensure_ascii=False,indent=2)+'\n')
md=['# Koko v2 同一 Reader 複審','','判定：**PASS_BOUNDED**。35/35 完整當前註解覆蓋；本輪沒有未解決 finding。這是同一 Reader 的重讀，不是第二位獨立 Reader。原始 NEEDS_REVISION 報告未修改。',f"\nCODEX_THREAD_ID: `{audit['CODEX_THREAD_ID']}`",'','## 沿用與新審','',audit['method'],'','- 33 則註解的全部可見欄位、連結及正文逐字一致，沿用原判斷。','- 第 11、28 段完整重新審查；共 5 個欄位變更。','- 所有 shared decision labels、reading cues、Active sentences 未變；兩段 Active Oracle 的新增／改寫已實際閱讀並對正文核實。','- 兩頁 35 個正文段落、完整 English reading text、3 個 pre blocks 與本次 Markdown 的實體比對均通過。','','實際讀取路徑：','']+[f'- `{p}`' for p in paths]+['','## 原問題的當前證據','']
for z in resolved:
 md += [f"### {z['original_finding_id']} — {z['status']}",'','當前可見精確引文：','']+[f'- {q}' for q in z['current_visible_quotes']]+['','正文精確引文：','']
 for b in z['supporting_body_quotes']:md += [f"- `{b['body_id']}` EN: {b['en']}",f"  ZH: {b['zh-TW']}"]
 md += ['']
md += ['## 範圍限制','']+[f'- {x}' for x in audit['limits']]+['','## 逐段完整當前稽核','']
for e in entries:
 md += [f"### 第 {e['paragraph_number']} 段 / {e['body_id']} — {e['verdict']}",'',f"判斷來源：{e['review_origin']}",'',e['assessment'],'',f"相鄰不合法推論：{e['nearby_illegal_inference_rejected']}",'',e['cue_check']]
 if 'active_content_confirmation' in e:md+=['',e['active_content_confirmation']]
 md+=['','完整當前可見欄位（兩頁一致）：','']
 for f in e['all_visible_annotation_fields']:md += [f"- `{f['class']}` [{f['verdict']}; {f['judgment_origin']}]: {f['text']}"]
 md+=['','當前正文及連結論證精確引文：','']
 for b in e['supporting_body_quotes']:md += [f"- `{b['body_id']}` EN: {b['en']}",f"  ZH: {b['zh-TW']}"]
 md+=['']
(out/'audit.md').write_text('\n'.join(md)+'\n')
receipt={'verdict':'PASS_BOUNDED','CODEX_THREAD_ID':audit['CODEX_THREAD_ID'],'review_identity':audit['review_identity'],'actual_read_paths':paths,'read_hashes':{p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in paths},'coverage':audit['coverage'],'outputs':['audit.json','audit.md','findings.json','verification.json'],'quote_verification':'All current resolution quotes and corresponding body quotes verified as exact substrings; all 35 unique paragraph entries present.'}
(out/'read-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'verdict':audit['verdict'],'entries':len(entries),'newly_reviewed_indices':[10,27],'unchanged_reused':33,'changed_fields':len(changes),'current_findings':0,'thread':audit['CODEX_THREAD_ID']},ensure_ascii=False))
