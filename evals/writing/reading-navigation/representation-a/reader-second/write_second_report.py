from pathlib import Path
import json,os,csv,difflib
P=Path('/var/folders/l6/44bf7nvs64j60f1mpyy88hdm0000gn/T/complete-annotation-reader-gkwz12f9');S=P/'second';O=S/'output'
old=json.loads((P/'output/audit.json').read_text());d=json.loads((O/'extracted.json').read_text());delta=json.loads((O/'actual-delta.json').read_text());oldext=json.loads((P/'output/extracted.json').read_text())
changes={(x['page'].split('.')[0],x['index']) for x in delta['annotation_changes']}
rows=[]
for prior in old:
 r=dict(prior);stem=prior['id'].split(':')[0];i=int(prior['id'].split('p')[-1]);ann=d[stem+'.en.html']['annotations'][i];r['review_round']=2;r['previous_audit_verdict']=prior['verdict'];r['prior_audit_reference']='../../output/audit.json#'+prior['id']
 if (stem,i) not in changes:
  assert ann==oldext[stem+'.en.html']['annotations'][i]
  assert d[stem+'.zh.html']['annotations'][i]==oldext[stem+'.zh.html']['annotations'][i]
  r['observation_status']='REUSED_UNCHANGED';r['reuse_basis']='完整annotation fields（包括note、所有context/checkpoint、reading、links、role、Active/cue/oracle）在兩語均exact unchanged；全部source bodies及article HTML亦exact unchanged。重用首次判讀，不冒稱本輪全新獨立閱讀。'
 else:
  r['observation_status']='NEW_READ_CHANGED_COMPLETE_ANNOTATION';r['reuse_basis']='只有未變的source/reading/Active可沿用fidelity；本項全部note/context/cue/Active與明鏈中英source均重新讀取及判讀。'
  r['verdict']='PASS_BOUNDED'
  r['displayed_note_quote']=next(x['text'] for x in ann['rows'] if x['class']=='alg-four-zh');r['displayed_context_quotes']=[x for x in ann['rows'] if x['class'] in ['alg-premise','alg-checkpoint']];r['displayed_reading_quote']=next(x['text'] for x in ann['rows'] if x['class']=='alg-reading-text');r['displayed_cue_quote']=next(x['text'] for x in ann['rows'] if x['class']=='alg-skeleton');r['active_sentences']=ann['active'];r['active_cues_or_oracles']=[x['text'] for x in ann['rows'] if x['class']=='']
  refs=list(dict.fromkeys(h for x in ann['rows'] for h in x['links']));r['linked_source_quotes']=[{'href':h,'en_quote':d[stem+'.en.html']['source'][h.removeprefix('#alg-p-')],'zh_quote':d[stem+'.zh.html']['source'][h.removeprefix('#alg-p-')]} for h in refs]
  if stem=='water':
   r['licensed_meaning']='此實作的height元素讀取、local binding及integer left重綁定不會修改input list。來源提供item assignment作為會寫入item的例子；它沒有提出所有list mutation必須使用item assignment的必要條件。'
   r['required_premises']='限定所示程式及integer left、讀取height[left]、綁定left_height等具體操作；不得由沒有item assignment單獨推出任意程式都不修改list。'
   r['state_or_order_checkpoint']='無新增時間要求；這是各種展示操作的效果與適用範圍，不是先後順序命題。'
   r['gap_or_failure']='原F1的排他note及premise均已移除；新context明確否認把item assignment當所有mutation必要條件。完整新註解與所鏈source未見剩餘條件缺漏。'
   r['nearby_unlicensed_inference_or_counterexample']='height=[2,5]合法起始，height.append(1)無item assignment卻會修改list；新註解限定原程式且拒絕一般必要條件，已不推出這個錯誤。這不是原函式出現append的證據。'
   r['historical_finding']='F1_RESOLVED_IN_SECOND_FROZEN_CONTENT; original first-round FAIL remains unchanged.'
  else:
   r['licensed_meaning']='此comprehension逐課各自求值[]，足以得到獨立inner lists；[[]]*V則重複同一mutable list reference，單處append會在各entry看見。[0]*V配immutable integer與slot replacement在此安全。'
   r['required_premises']='說的是指定comprehension與[[]]*V，不是只有[]語法才能建立獨立lists；各課append針對其inner list；零counter更新替換單slot。'
   r['state_or_order_checkpoint']='無時間要求；建立方式、reference共享與slot replacement效果不需額外時間checkpoint。'
   r['gap_or_failure']='新note與首premise使用「此comprehension…因此」，並明確拒絕只有[]語法的必要條件。原source只授權其做法足夠，不授權唯一構造；新註解保持充分方向。未見現行缺漏。'
   r['nearby_unlicensed_inference_or_counterexample']='V=2時[[]]*2的after[0].append(1)讓兩entry均看見1，支持來源的共享反例；[list() for _ in range(2)]也能各建list，否定「只有[]語法」的一般化。新註解沒有這個必要條件。後一反例是讀者檢查方向，不拿它替新註解補前提。'
   r['historical_finding']='首次audit給此項PASS_BOUNDED；本輪重看舊note「才有」可產生必要方向歧義，首次未另標出。此事保留為historical review limitation，沒有回寫首次判定。'
  r['active_assessment']='PASS_BOUNDED，已重新閱讀：Active句子原文不變；cue/oracle只談指定實作中的重綁定或shared-list repetition，完整context與單一明鏈source足以支持，沒有新增唯一機制的claim。'
  r['chunk_assessment']='PASS_BOUNDED，重新讀完整reading；chunk/bundle/stress與第一輪exact unchanged，plain reading/source對照可重用；不新增發音或人類流暢效果觀察。'
 rows.append(r)
assert len(rows)==83 and sum(r['observation_status']=='REUSED_UNCHANGED' for r in rows)==81
(O/'audit.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
with (O/'audit.tsv').open('w') as f:
 fields=['id','observation_status','verdict','previous_audit_verdict','licensed_meaning','required_premises','state_or_order_checkpoint','displayed_note_quote','gap_or_failure','nearby_unlicensed_inference_or_counterexample'];w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',extrasaction='ignore');w.writeheader();w.writerows(rows)
esc=lambda s:s.replace('|','\\|').replace('\n','<br>')
md=['# 第二輪 83 項 audit','', '81項REUSED_UNCHANGED，2項NEW_READ_CHANGED_COMPLETE_ANNOTATION。全部明鏈中英引文、context、reading與Active在audit.json。首次報告未改。','', '| ID | 觀察來源 | 結果 | 意義／前提／時點 | 顯示note與source | 反例／鄰近不合法推論 |','|---|---|---|---|---|---|']
for r in rows:
 src=r['linked_source_quotes'][0];md.append('| '+' | '.join(esc(v) for v in [r['id'],r['observation_status'],r['verdict'],r['licensed_meaning']+' 前提：'+r['required_premises']+' 時點：'+r['state_or_order_checkpoint'],'note「'+r['displayed_note_quote']+'」；'+src['href']+'「'+src['en_quote']+'」',r['nearby_unlicensed_inference_or_counterexample']])+' |')
(O/'audit.md').write_text('\n'.join(md)+'\n')
findings={'review_round':2,'current_unresolved_findings':[],'historical_findings':[{'id':'F1','row':'water:p22','first_round_status':'FAIL_SOURCE_SCOPE; RECONSTRUCTION_PASS_BOUNDED','second_round_status':'RESOLVED_IN_SECOND_FROZEN_CONTENT','original_note':old[22]['displayed_note_quote'],'original_failure':old[22]['gap_or_failure'],'current_note':rows[22]['displayed_note_quote'],'basis':rows[22]['gap_or_failure'],'counterexample_retained':rows[22]['nearby_unlicensed_inference_or_counterexample'],'first_round_artifacts_preserved':True},{'id':'H2','row':'course:p07','kind':'newly recognized historical wording-direction ambiguity, not a current candidate failure','first_round_recorded_status':'PASS_BOUNDED','second_round_status':'PASS_BOUNDED after actual wording change','original_note':old[43+7]['displayed_note_quote'],'current_note':rows[43+7]['displayed_note_quote'],'limit':'首次未將「才有」的必要方向歧義單列；不能宣稱第二輪只修一項或首次已發現此問題。此處如實記錄，首次原audit不改。'}]}
(O/'findings.json').write_text(json.dumps(findings,ensure_ascii=False,indent=2))
report='''# 第二輪有界 Reader report

現行凍結內容83項均為PASS_BOUNDED：81項沿用第一次exact unchanged內容判讀，2項完整新判讀。不是新83項全獨立重測。第一次全部audit/report/FAIL保留，未改驗收criteria。

actual delta：Water p22（UI第23段）及Course p7（UI第8段），各在中英兩頁同步更換note與首條premise。其餘81項完整annotation在兩語皆exact unchanged。四份批准Markdown bytes完全不變；四頁正文article HTML完全不變。所有reading markup、source links、短cue、Active sentences/cues/oracles都不變。故不能將變動數寫為「1項修稿／82項沿用」。

Water p22新note說「此實作…不修改 input list；item assignment會寫入item，但這裡沒有這種assignment」，首premise又限定原程式並明說source沒有將它當所有mutation的必要條件。其明鏈#alg-p-22原文為「An assignment targeting an item such as height[left] would write that item; no such assignment occurs here」，且解釋讀取/local binding/integer重綁定的效果。新註解保持充分例示與展示程式範圍，不再倒推唯一機制。原F1 counterexample仍有效：合法起始height=[2,5]可經append修改而沒有item assignment；新註解已不推出其否定。F1在第二份凍結內容RESOLVED，第一輪FAIL永久保留。

Course p7新note說「此comprehension對每門課分別求值[]，會產生獨立inner lists」，新context明示這是source做法的效果，不宣稱只有[]語法可建獨立lists。明鏈#alg-p-7的「Evaluating [] separately for each course makes independent inner lists」只給這個充分方向；相鄰原文分清[[]]*V共享mutable list、[0]*V配integer slot replacement安全。合法V=2的shared-list append反例和完整context一致。另一方面list()逐課建立也能獨立，說明不能加唯一語法必要條件；本反例只檢查推論方向，不替註解補來源前提。

對歷史判讀的限制：原Course p7的「每次求值[]才有獨立inner lists」也有必要方向歧義；第一輪給PASS而未單列。本輪對照actual修稿才明確記錄此歷史風險。沒有回寫原結果，也沒有冒稱第一次已抓到它。新文字已去除此歧義，現行沒有追加FAIL。

兩項新判讀都沒有時間checkpoint要求，故不添加先後順序前提。完整reading、bundle、Active sentence/cue/oracle已重讀，與首次內容相同；其Active只談指定重綁定或shared-list repetition，明鏈source直接支持。短question仍只是閱讀cue，沒有當成獨立theorem驗收。

source losslessness、其餘chunk attachment/cue/Active的既有有界判斷可沿用，理由是完整內容與source exact unchanged，並非本輪又測得新證據。全部83行連同note/context、完整明鏈中英source引文、必要前提與附近反例在audit.json；audit.tsv及audit.md供掃讀。actual-delta.json記逐頁實際變動。

範圍依舊只有指定frozen HTML/source文字與本人第一次原稿/audit。沒有Ownerledger、skill、expected answer、其他讀者trace或repository history。未fetch外部source links，未開瀏覽器、聽音訊、跑runtime、收真人資料或增加發音證據；不宣稱人類速度、學習效果或一般穩定性。same Reader/same thread作修稿後有界複核，不是新獨立Reader session。
'''
(O/'report.md').write_text(report)
reads={'review_round':2,'CODEX_THREAD_ID':os.environ.get('CODEX_THREAD_ID','UNAVAILABLE'),'same_reader_same_thread':True,'request_read':str(S/'request.json'),'new_allowlisted_inputs_all_bytes_read':[str(S/x['name']) for x in delta['files']],'own_first_round_material_read':[str(P/x['name']) for x in delta['files']]+[str(P/'output/extracted.json'),str(P/'output/audit.json')],'new_semantic_reads':['water:p22 complete annotation in zh/en plus linked #alg-p-22 zh/en source','course:p07 complete annotation in zh/en plus linked #alg-p-7 zh/en source'],'reused_exact_unchanged_rows':[r['id'] for r in rows if r['observation_status']=='REUSED_UNCHANGED'],'original_artifacts_written':False,'candidate_inputs_written':False,'excluded_inputs_not_read':['owner ledger','skills','expected answers','other reader reviews','repository history'],'not_observed':['browser rendering/interactions','runtime/code test','audio/independent pronunciation verification','human outcomes','general stability'],'method':'Read every second input byte, compare to own first inputs, parse complete annotation fields, show all actual HTML deltas and both changed complete annotations/linked sources; reuse81 and newly judge2.'}
(O/'actual-reads.json').write_text(json.dumps(reads,ensure_ascii=False,indent=2));(O/'CODEX_THREAD_ID.txt').write_text(os.environ.get('CODEX_THREAD_ID','UNAVAILABLE')+'\n')
print('rows',len(rows),'reuse',sum(r['observation_status']=='REUSED_UNCHANGED' for r in rows),'new',sum(r['observation_status'].startswith('NEW_READ') for r in rows),'current fails',len(findings['current_unresolved_findings']))
