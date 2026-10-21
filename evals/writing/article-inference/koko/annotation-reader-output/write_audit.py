from pathlib import Path
import json,os,hashlib
r=Path('/var/folders/l6/44bf7nvs64j60f1mpyy88hdm0000gn/T/article-entailment-2x13kv72/koko');inp=r/'annotation-reader-input';out=r/'annotation-reader-output'
d=json.loads((out/'extracted.json').read_text())
notes=[
('精確 hours test 本身不足以授權刪除整段；context 明列原題判準及提高 speed 不增加 T(k)，連結正文給出每堆到總和的原因。','不把成功的 probe 當最小值；不把未排序的 piles 當搜尋順序。'),
('zh_note、英文全文與 premise 保留非空正數 piles、正整數 speed、至多 h，以及同一小時不能換堆。','不能把提早完成剩餘容量轉給另一堆；不是要求恰好用 h 小時。'),
('每堆至少一小時提供必要條件；取最大堆 M 且每堆一小時提供 h>=n 下的可行構造。數值限制、只讀與排除範圍保留。','h<n 不得沿用可行 high；h>=n 的充分性有 M 構造而非單靠下界。'),
('固定 [4,4], h=3；四與兩小時及答案 4 均維持，pooling 的錯誤機制連到禁止換堆及逐堆 ceiling。','「k=4 才能完成」在最小速度語境是門檻，不授權聲稱 k>4 失敗。'),
('正 p,k 的完整群組加非零 remainder 的整小時，支撐 ceiling；Active sentence/cue/oracle 保留原題禁止 pooling。','remainder=0 不另加小時；不是把所有香蕉合併後一次 ceiling。'),
('正整數、// 向下取整及 0<=r<k 都明列，兩分支提供 q 與 q+1 的完整算術解釋。','不能延用到任意負數或零 divisor；r=0 不能多加一小時。'),
('zh_note/context/Active 都給出合法 schedule 下界與逐堆完成的可達構造，必要且充分的兩方向都在正文。','必要性不等同充分性；原題的逐堆時段限制不可省略。'),
('固定 k=4 與輸入，完整前綴總和 1,3,5,8；checkpoint 限定每堆完成後，Active oracle 指出 processed piles sum。','中途 hours 是已處理堆的總和，不是全部 piles 的總和，也未存 contribution list。'),
('每堆不增加再求和給出非增加方向，feasibility 的失敗前綴允許為空；oracle 用正文 4 與 5 同為八小時排除嚴格下降。','不增加不等於每次加速都省一小時，也不要求每次 k 增加都切換布林結果。'),
('context 固定同一 piles,h；失敗排除 <=6，成功只證明 minimum<=6，英文與 zh_note 都保留 may be smaller。','可行 probe 不是最小證明；不能由 6 成功排除更小 speed。'),
('inclusive interval、M 的可行構造與 Active sentence/oracle 正確；但 context 的「在 M 前」沒有保留 by M 的端點。','不允許從 M 可行推成存在嚴格小於 M 的可行 speed；h=n 時答案可以等於 M。'),
('兩條 invariant 與 iteration-start checkpoint 都明列，Active oracle 的兩分支由 linked proof 支持，終點 singleton 保證也有正文。','invariant 不是全體 speeds 的單調性；也不聲稱 interval 中每個 speed 都可行。'),
('完整 hours test 後以 >h 作失敗分支，low=mid+1 與 high=mid 的非對稱保留、停止條件均未改。','成功不能 high=mid-1；失敗不能保留已否定的 mid；equality 屬成功分支。'),
('scan 前 low=high=1 與結束 high=11 的時點清楚，每個新 speed 的 hours 重設有 code 與正文理由。','未把初始最大值 scan 中的 high 當成已證可行的 search high；也未沿用上一 probe 的 total。'),
('固定例子與 h=8 保留；6 可行但答案4，以及4、5同八小時，由 generated trace 完整驗證。','第一次成功或恰等於 deadline 都不能單獨證最小；不是禁止 singleton 時回傳。'),
('p=11,k=4 的4,4,3與最後時段的歸屬保留，正文每小時規則支撐 pooling 錯誤機制。','不能把最後一小時餘量移到其他堆；未聲稱最後一定吃滿 k。'),
('high 的「已讀最大值」限於每讀一個元素後；正 pile 令 high=1 初始化合法。wrapper/self 與同一 list 的 scope 符合 code。','不能在尚未讀任何元素時說 high 等於已讀最大值；不能把 loop scalar 說成 instance state。'),
('本文指定 code 把 reset 放 while 內、總和存 scalar、scan 後才更新端點；正 endpoints 保證正 mid，沒有 state/history 副作用。','不能把 += 當 list append；不能把每個新 test 當累積先前 probes 的 hours。'),
('先假設 invariant，再由 monotonicity 分別保留答案及可行 high；context 逐項交代前後狀態。','失敗不保留 mid；成功保留 mid 但不保證 mid 已最小；不是只用單調性便宣告搜尋狀態正確。'),
('low<high 下 lower middle 的界線、端點嚴格移動、interval 非空與有限整數候選形成停止論證；singleton 套 invariant。','不需再測試最後值不等於可以省略 invariant；也未聲稱 interval 能變空再回傳。'),
('以指定 [2],h=1,[1,2] 反例顯示 low=mid 可能完全不前進，checkpoint 明確是錯誤 assignment 後狀態。','是存在卡住反例，並未聲稱每個 failure 都卡住；+1 必須移除已否定候選。'),
('四個邊界及原題限制保持；M=1 不進 search、h=n 的最大堆、h>=香蕉總數的1及h<n無解都有正文因果。','M=1 不進 search 不等於整個算法不掃描；h<n 不因速度加大而可解。'),
('numeric range 與 operation-count model 明列，Active 另外連到掃描、halving、fixed live state 的完整正文論證；oracle 排除任意長整數。','常數成本是宣告模型，不是所有 Python 指令 wall-clock 相同；O(1) 不延伸到無界 bit-size。'),
('指定 code 每次完整掃 n 堆，固定有界工作支持 proportional n；英文、zh_note及 context 限定無 early exit。','不能把超過 h 後提前停止當成這份 code 的行為；也不能把一個 test 當常數總成本。'),
('兩組大小、ceil(L/2)、11->6->3->2->1、t 次更新上界與初始 n scan 全保留，M=1 特例亦未刪。','ceil(log2 M) 是至多次數，不是每個輸入精確次數；O(n log M) 簡寫限 M>=2。'),
('固定 live scalar、traversal state、暫時 bounded values，排除 caller input；單整數 output 與任意長整數例外都有。','固定變數數量不單獨授權無界整數 O(1) bytes；未把輸入大小或 history 算成不存在。'),
('按1到a逐一完整test提供首成功最小；n*a 計數、a<=M及一堆 M,h=1 的反例支撐所述上界；tiny fixed M 與無 speed 保證都保留。','小 M 支持簡單 control flow，不能推出速度必優於 binary search；沒有用對數 scan 數替代 a。'),
('跨堆可達容量機制、positive h、S定義與 bounded pass 成本都完整；但 zh_note 的「只有…才」新增必要規則變更，超出正文 conditional。','改題規則使總量公式對該改題普遍成立，不等於原題每一個實例都必須先改規則才可能有同一判準。'),
('練習輸入及起始範圍固定；linked monotonicity/interval 更新支撐對未逐測候選的排除理由，cue 是問題。','未把練習的要求等同學習者已具備能力；不能只背 assignment 形式便省略排除理由。'),
('generated/source trace 的 mid 3,2,1、hours 3,4,7、端點 [1,3],[1,2],[2,2] 全保留；最後移除1有 invariant 支持最小2。','最後一次失敗不是證明2可行的唯一依據；可行性由一直維持的 high/invariant 保留。'),
('ordered 物件為正整數 speeds，原題 per-pile hours 判準與 T 非增加充分給出 feasibility 方向；context 特別排除每次切換。','false-to-true 是允許的變化方向，不主張必須存在 failing prefix 或每步都轉換；不要求 piles 已排序。'),
('whole-hour remainder、不能跨堆移容量，另有 linked 下界與可達性，支撐所需時間恰為 per-pile ceilings 和。','不是 ceiling(sum/k)；只有下界不足以稱 exact required time，但正文已給逐堆構造。'),
('兩個 invariant clauses、失敗移除方向與成功保留 mid 均正確；context 對每 branch 更新到 singleton 的時點有正文 proof。','成功並不讓整個 interval 每個候選都可行；沒有由單次成功就推出最小。'),
('n/M 定義、有界算術、initial/probe 全scan、halving及live state 證據都在 context links；英文成本包括1+log M。','不是只報O記號而無計數，也未去掉 M=1 的初始scan或把input列為auxiliary。'),
('註解只重述本文引用分工且明確未外讀引用；context 連到正文實際 rounding、schedule、monotonicity、proof及成本論證。','引用不是推導完成或外部來源已核實；本稽核不能聲稱驗證了未開啟的來源內容。')]
findings=[
{'id':'KOKO-ANNOTATION-01','paragraph_index':10,'paragraph_number':11,'severity':'medium','location':'alg-reading-context / 適用前提 (both generated pages)','visible_quote':'答案是正整數 speed，因此至少為 1，並在 M 前已有可行值。','body_quotes':[{'id':'alg-p-10','en':'No positive answer lies below 1, and an answer exists by M, so start with the inclusive interval [low, high] = [1, M].','zh-TW':'正整數答案不可能低於 1，而最遲在 M 就有答案，所以從 inclusive interval [low, high] = [1, M] 開始。'},{'id':'alg-p-21','en':'If h = n, each pile must fit into its one hour, so the largest pile forces the answer to be M.','zh-TW':'若 h = n，每堆都必須在分配給自己的一小時內吃完，因此最大那堆迫使答案為 M。'}],'issue':'「M 前」通常是嚴格小於 M；正文只證明到 M 為止（含 M）存在可行值，且明給答案等於 M 的合法邊界。旁邊 inclusive/Active 正確並不能消除這個 premise 的端點歧義。','licensed_inference':'minimum <= M，M 可行。','illegal_inference':'存在可行 k < M。','suggested_revision':'答案是正整數 speed，因此至少為 1；M 本身可行，所以在不大於 M 的速度中已有可行值。'},
{'id':'KOKO-ANNOTATION-02','paragraph_index':27,'paragraph_number':28,'severity':'medium','location':'alg-four-zh / zh_note (both generated pages)','visible_quote':'只有改成一小時內可跨堆用滿容量，h * k >= S 才既必要又充分，答案為 ceiling(S / h)。','body_quotes':[{'id':'alg-p-27','en':'Suppose Koko could switch piles within an hour and use the entire capacity k across them.','zh-TW':'假設 Koko 能在一小時內切換香蕉堆，把完整容量 k 用在多堆之間。'},{'id':'alg-p-27','en':'Therefore h * k >= S is sufficient as well as necessary, and the minimum integer speed is (S + h - 1) // h.','zh-TW':'因此，h * k >= S 既是必要條件，也是充分條件，最小整數速度便是 (S + h - 1) // h。'},{'id':'alg-p-20','en':'For piles = [2], h = 1, the interval is [1, 2] and mid = 1 fails.','zh-TW':'對 piles = [2]、h = 1，interval 是 [1, 2]，而 mid = 1 失敗。'},{'id':'alg-p-4','en':'If some bananas remain, they need another whole hour. This count is the ceiling of p / k: the smallest integer at least as large as that quotient.','zh-TW':'若還有剩餘香蕉，就需要額外一個完整小時。這個數量是 p / k 的 ceiling，也就是不小於該商的最小整數。'}],'issue':'正文提出一個足以確保容量可達的改題條件；「只有…才」卻把它變成總量判準成立的必要條件，未限定是在兩種一般題目規則之間比較。對正文的原題單堆 [2], h=1，沒有可換的第二堆；按正文 ceiling 定義，原題可行恰為 k>=2，也恰為 h*k>=S，完全不用改規則。','licensed_inference':'在允許同小時跨堆用滿容量的改題中，h*k>=S 對所有合法輸入是必要且充分；原題不能一般套用，正文 [4,4],h=3 是失敗例。','illegal_inference':'只要某個實例的 h*k>=S 是必要且充分，就一定已改成允許跨堆規則。','suggested_revision':'在這個改成一小時內可跨堆用滿容量的題目中，h * k >= S 既必要又充分，答案為 ceiling(S / h)；原題不能一般套用這個公式。'}]
by_idx={f['paragraph_index']:f for f in findings}
entries=[]
for a,(reason,challenge) in zip(d['en']['annotations'],notes):
 i=a['index'];links=[]
 for f in a['fields']:
  for link in f['links']:
   if link and link not in links:links.append(link)
 if f'alg-p-{i}' not in links:links.insert(0,f'alg-p-{i}')
 field_checks=[]
 for f in a['fields']:
  st='NOT_ASSESSED_PROSODY_OR_LEARNING' if f['class'] in ('alg-reading-label','alg-source-explain') else 'PASS_BOUNDED'
  if i==10 and f['class']=='alg-reading-context' or i==27 and f['class']=='alg-four-zh':st='NEEDS_REVISION'
  field_checks.append({**f,'verdict':st})
 entries.append({'paragraph_index':i,'paragraph_number':i+1,'body_id':f'alg-p-{i}','applies_to':['page.en.html','page.zh-TW.html'],'verdict':'NEEDS_REVISION' if i in by_idx else 'PASS_BOUNDED','all_visible_annotation_fields':field_checks,'supporting_body_quotes':[{'body_id':link,'en':d['en']['body'][link],'zh-TW':d['zh-TW']['body'][link]} for link in links],'assessment':reason,'nearby_illegal_inference_rejected':challenge,'cue_check':'本段 reading cue 為問題；Active cue 如存在亦為解釋／比較任務。未把短提示當獨立 theorem。','finding_ids':[by_idx[i]['id']] if i in by_idx else []})
paths=[str(inp/x) for x in ['task.json','article.en.md','article.zh-TW.md','page.en.html','page.zh-TW.html']]
audit={'verdict':'NEEDS_REVISION','CODEX_THREAD_ID':os.environ.get('CODEX_THREAD_ID'),'actual_read_paths':paths,'local_derivative_read_paths':[str(out/'extracted.json')],'scope':'35 complete annotations in both generated HTML pages, both complete source Markdown bodies, all linked paragraph arguments and generated trace/code/Master Map blocks. No external sources, repository, author/Owner reports, prior Readers or manifests read.','method':'Locally parsed complete HTML without output truncation; 35 indexed body paragraphs and 35 complete annotations per page; all annotation fields identical between pages. Read full English, zh_note, premises/checkpoints, cues, Active sentences/cues/oracles and each linked body paragraph. HTML text quotes normalize whitespace only; /, // and [] reading markers retained.','limits':['No semantic score, learner benefit, mastery, reading speed or pronunciation verdict.','Citation provenance was compared to supplied body only; external linked documents were not opened.','Findings concern visible wording, not a demonstrated Python algorithm defect.','PASS_BOUNDED means no further unsupported technical assertion found within this supplied packet; not a universal correctness or learning claim.'],'coverage':{'paragraph_indices':list(range(35)),'reviewed_count':35,'page_languages':['en','zh-TW'],'annotation_fields_same_across_pages':True,'per_paragraph_pass_count':33,'per_paragraph_revision_count':2,'findings_count':len(findings)},'findings':findings,'paragraph_audits':entries}
(out/'audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
(out/'findings.json').write_text(json.dumps({'verdict':audit['verdict'],'CODEX_THREAD_ID':audit['CODEX_THREAD_ID'],'findings':findings},ensure_ascii=False,indent=2)+'\n')
md=['# Koko 完整註解獨立 Reader 稽核','','判定：**NEEDS_REVISION**。35/35 已審，兩頁註解內容一致；33 段有界通過，2 段需修正可見措辭。未作學習效果或語意分數宣稱。',f"\nCODEX_THREAD_ID: `{audit['CODEX_THREAD_ID']}`",'','實際輸入讀取路徑：','']+[f'- `{x}`' for x in paths]+['',audit['method'],'','範圍限制：','']+[f'- {x}' for x in audit['limits']]+['','## 發現','']
for f in findings:
 md += [f"### {f['id']}：第 {f['paragraph_number']} 段（index {f['paragraph_index']}）",'',f"可見原文：> {f['visible_quote']}",'',f['issue'],'',f"授權推論：{f['licensed_inference']}",f"不合法加強：{f['illegal_inference']}",'',f"建議：{f['suggested_revision']}",'','正文精確引文：','']
 for b in f['body_quotes']:md += [f"- `{b['id']}` EN: {b['en']}",f"  ZH: {b['zh-TW']}"]
 md += ['']
md+=['## 逐段完整稽核','']
for e in entries:
 md += [f"### 第 {e['paragraph_number']} 段 / {e['body_id']} — {e['verdict']}",'',e['assessment'],'',f"相鄰不合法推論：{e['nearby_illegal_inference_rejected']}",'',e['cue_check'],'','完整可見註解欄位（兩頁一致）：','']
 for f in e['all_visible_annotation_fields']:md += [f"- `{f['class']}` [{f['verdict']}]: {f['text']}"]
 md += ['','正文支撐及連結論證（完整精確段落）：','']
 for b in e['supporting_body_quotes']:md += [f"- `{b['body_id']}` EN: {b['en']}",f"  ZH: {b['zh-TW']}"]
 md += ['']
(out/'audit.md').write_text('\n'.join(md)+'\n')
receipt={'verdict':audit['verdict'],'CODEX_THREAD_ID':audit['CODEX_THREAD_ID'],'actual_read_paths':paths,'read_hashes':{p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in paths},'outputs':['audit.json','audit.md','findings.json'],'reviewed_count':35}
(out/'read-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'verdict':audit['verdict'],'entries':len(entries),'finding_ids':[f['id'] for f in findings],'outputs':receipt['outputs'],'thread':audit['CODEX_THREAD_ID']},ensure_ascii=False))
