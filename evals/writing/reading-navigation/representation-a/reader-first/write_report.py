from pathlib import Path
import json,os,re,csv
P=Path('/var/folders/l6/44bf7nvs64j60f1mpyy88hdm0000gn/T/complete-annotation-reader-gkwz12f9');O=P/'output'
exec((O/'judgments.py').read_text())
d=json.loads((O/'extracted.json').read_text())
rows=[]
for stem,js in [('water',W),('course',C)]:
 for a,j in zip(d[stem+'.en.html']['annotations'],js):
  idx=a['index'];fields=a['rows'];refs=list(dict.fromkeys(h for r in fields for h in r['links']))
  support=[]
  for h in refs:
   k=h.removeprefix('#alg-p-')
   support.append({'href':h,'en_quote':d[stem+'.en.html']['source'][k],'zh_quote':d[stem+'.zh.html']['source'][k]})
  note=next(r['text'] for r in fields if r['class']=='alg-four-zh')
  cue=next(r['text'] for r in fields if r['class']=='alg-skeleton')
  ctx=[r for r in fields if r['class'] in ['alg-premise','alg-checkpoint']]
  active=[r['text'] for r in fields if r['class']=='']
  verdict='PASS_BOUNDED'
  gap='未發現 complete annotation 加其明鏈來源仍缺少的必要演算法前提。鄰近錯誤讀法列於下欄，並非候選本身一定犯錯。'
  if stem=='water' and idx==22:
   verdict='FAIL_SOURCE_SCOPE; RECONSTRUCTION_PASS_BOUNDED'
   gap='note「只有針對 height item 的 assignment 才會寫回」與context「只有 item assignment 才是另一種操作」帶排他性。來源僅說 item assignment 會寫入及展示程式沒有這種操作，沒有聲稱它是所有修改 list 的唯一機制。若限定為本程式 reads/bindings，保留輸入的重建成立；排他一般化不可接受。'
  rows.append({'id':f'{stem}:p{idx:02d}','page_indices':'zero-based; UI paragraph '+str(idx+1),'pages':[stem+'.zh.html',stem+'.en.html'],'verdict':verdict,'licensed_meaning':j[0],'required_premises':j[1],'state_or_order_checkpoint':j[2],'displayed_note_quote':note,'displayed_context_quotes':ctx,'displayed_reading_quote':next(r['text'] for r in fields if r['class']=='alg-reading-text'),'displayed_cue_quote':cue,'linked_source_quotes':support,'active_sentences':a['active'],'active_cues_or_oracles':active,'active_assessment':'PASS_BOUNDED: source sentence保留；cue/oracle按本行完整前提閱讀可重建；不可剝掉context當無條件定理。' if a['active'] else 'NOT_APPLICABLE','chunk_assessment':'PASS_BOUNDED: reading plain text對應同index完整English source；bundle未換修飾對象；/與//作停頓不作新命題。自然度或學習速度未測。','gap_or_failure':gap,'nearby_unlicensed_inference_or_counterexample':j[3]})
(O/'audit.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
with (O/'audit.tsv').open('w') as f:
 fields=['id','verdict','licensed_meaning','required_premises','state_or_order_checkpoint','displayed_note_quote','gap_or_failure','nearby_unlicensed_inference_or_counterexample']
 wr=csv.DictWriter(f,fieldnames=fields,delimiter='\t',extrasaction='ignore');wr.writeheader();wr.writerows(rows)
md=['# 83 項完整 annotation 獨立閱讀稽核','', '每個 p 為 HTML data-alg-four-index 的零基底值；同一項覆核中英兩頁。PASS_BOUNDED 僅指 frozen content 的可重建性；短 cue 不是獨立定理。完整來源引用保存在 audit.json；下表保留每項 note 與一段明鏈來源代表引文，其他明鏈前提亦已讀。','', '| ID | 結果 | 獨立重建／前提／時點 | 顯示 note 與明鏈來源引文 | 鄰近不合法推論或反例 |','|---|---|---|---|---|']
esc=lambda s:s.replace('|','\\|').replace('\n','<br>')
for r in rows:
 # Pick the attached paragraph if linked; otherwise first explicitly linked source.
 target='#alg-p-'+str(int(r['id'].split('p')[-1]));s=next((x for x in r['linked_source_quotes'] if x['href']==target),r['linked_source_quotes'][0])
 md.append('| '+' | '.join(esc(x) for x in [r['id'],r['verdict'],r['licensed_meaning']+' 前提：'+r['required_premises']+' 時點：'+r['state_or_order_checkpoint'],'note「'+r['displayed_note_quote']+'」；'+s['href']+'「'+s['en_quote']+'」',r['nearby_unlicensed_inference_or_counterexample']])+' |')
(O/'audit.md').write_text('\n'.join(md)+'\n')
findings=[{'id':'F1','severity':'bounded wording/source-scope failure','rows':['water:p22'],'duplicate_surfaces':['water.zh.html','water.en.html'],'note_quote':rows[22]['displayed_note_quote'],'source_quote':next(x for x in rows[22]['linked_source_quotes'] if x['href']=='#alg-p-22')['en_quote'],'failure':rows[22]['gap_or_failure'],'counterexample':rows[22]['nearby_unlicensed_inference_or_counterexample'],'scope':'不否定展示程式的 input-preservation。不是執行到的程式 bug。'}]
(O/'findings.json').write_text(json.dumps(findings,ensure_ascii=False,indent=2))
active_rows=[r for r in rows if r['active_sentences']]
report=f'''# 有界的獨立 Reader report

我以 elementary Python 讀者身分從四份完整批准 source bodies 重建兩篇文章，再逐一讀完 83 個 complete paragraph annotations（Water 43、Course 40），包含 note、全部 premise/checkpoint、所鏈段落、reading markup、短 cue、Active sentence/cue/oracle。繁中、英文各複製一份，共 166 個展示 instances；兩語同項 annotation fields 完全相同，因此不是 166 個獨立語意案例。

結論：82/83 項為 PASS_BOUNDED；water:p22 有一項 source scope 措辭 FAIL，其限定於展示程式的重建仍通過。發現是「只有 item assignment」的排他語氣，比來源的充分例示更強。合法起始 list [2,5] 可經 height.append(1) 修改而無 item assignment；這只否定一般化，不表示原函式有這項 mutation。完整引文與界限在 findings.json / audit.json，沒有刪去此失敗。

Water 的核心重建是：同一合法 pair 的正寬乘非負短高；在短端分支只界住保留該短端的 inward partners；先把已量 endpoint area 納入 best，才刪這組候選。每次 while 檢查時，best 同時最大化已量候選並涵蓋區間外 pair。距離歸零才覆蓋全域，且 best 來自真實候選。座標版另需 x 嚴增、對齊且已供應。沒有把「內縮」擴成所有內部 pair，也沒有從 safe discard 推下一 area 改善。

Course 的核心重建是：b→a 表示 b 完成才消除 a 的一項義務；counts 必須是數量，初始零由完整 ID scan 納入、後來正值剛達零再納入。checkpoint 僅在前一 completion 的整份 dependent updates 完成後，要求 distinct finished、unfinished counts 正確以及 ready 恰含所有 available unfinished courses 各一次。最終完整 ready 空並且仍有 unfinished 課，才能用有限逆追推出 cycle。FIFO 無 smallest-first 保證；self-loop 包含在 contract。

來源與reading fidelity：四頁 article block 序列（每份 Water 55 blocks、Course 51 blocks）與各自完整 Markdown 在去除 Markdown/HTML 表示層後對應，段落／headings／code 沒有發現內容遺失；外部 source links 的順序和 URL 相同。每項 reading 去除新增的 break、bundle 邊框與重音標記後，逐字內容（僅合併空白）對應同 index 的 English source。完整中文 source 與完整英文 source 也已分別通讀，沒有發現改掉 contract、否定、數量或證明關係。這些逐項比較只是 fidelity 證據，語意判斷另見 83 行 audit。

Chunk/cue：83 reading texts 與全部 bundle/stress attachments 已讀。未發現 bundle 換掉關係子句對象、not/only/either 指向或把 selected object 換成較大的集合。/、// 有些切得很細，例如 Course p15 的「3 stays /out of the queue //because ...」，但後接原因、完整 context 及 source 均仍在；我不把停頓處視為獨立定理。短 cue 明示非獨立結論，判定以 complete annotation 與其明鏈argument為單位。

Active：{len(active_rows)} 個含Active的paragraph，合計 {sum(len(r['active_sentences']) for r in active_rows)} 個term/sentence entries。每個展示 sentence 與原段可對照，cue/oracle 的推論均可由該項完整 context 加其明鏈來源重建。重要的限定包括 Water p21 的「這份程式每branch各一次index update」、Water p35 的非負高度／有序對齊座標，以及 Course p6/p18 的完整 dependent updates 檢查點。若將 oracle 單獨抽離，這些短回答不足作無條件 theorem；本 request 的驗收單位沒有要求那樣閱讀。沒有另發現 Active 內容上的FAIL。

界限：我只讀指定 frozen HTML 與source文字，沒有開瀏覽器、取得CSS/JS或執行互動；不判定視覺遮擋、展開/點擊功能、音訊、壓力/斷句的人類效果、或程式測試。像 algorithm 的 al stress markup 只是可觀察的字形標記，批准輸入沒有提供可獨立核對音韻的音源/詞典；發音 evidence 為 partial，不能標總體 pronunciation PASS。批准 bodies 裡的外部 LeetCode/Python/CPython links 只核對保留，依只讀 allowlist 的邊界沒有fetch其內容，因此不把上述教材忠實性說成已另行查證那些上游版本實況。沒有真實學習者、計時、前後測或跨版本抽樣，所以不宣稱速度、學習成效或普遍穩定。

交付：audit.json 含完整83行、全部明鏈中英source引文、展示context、reading、Active及逐行重建；audit.tsv / audit.md 方便掃讀。findings.json 保留全部實際失敗。actual-reads.json 與 CODEX_THREAD_ID.txt 記本reader可觀察身分及讀取。由父代理另跑的code tests沒有混入本判定。
'''
(O/'report.md').write_text(report)
(O/'CODEX_THREAD_ID.txt').write_text(os.environ.get('CODEX_THREAD_ID','UNAVAILABLE')+'\n')
log=json.loads((O/'actual-reads.json').read_text());log['completed_review']={'all_complete_annotations_read':83,'duplicated_language_instances':166,'ranges_displayed':['water notes/context/cue/Active p0..21','water notes/context/cue/Active p22..42','course notes/context/cue/Active p0..19','course notes/context/cue/Active p20..39','water reading p0..20,p21..42','course reading p0..20,p21..39','all bundle/stress terms from both unique pages','course p21,p34 raw stress markup'],'source_support':'All explicitly linked source paragraphs read in complete source bodies; all links and full source quotations included in audit.json.','no_input_edits':True,'no_external_reads':True,'not_observed':['browser rendered UI','interactive state','runtime tests','audio/pronunciation source verification','human learning outcomes']};(O/'actual-reads.json').write_text(json.dumps(log,ensure_ascii=False,indent=2))
print('83 rows saved; active paragraphs',len(active_rows),'entries',sum(len(r['active_sentences']) for r in active_rows));print('findings',len(findings));print('thread',os.environ.get('CODEX_THREAD_ID','UNAVAILABLE'))
