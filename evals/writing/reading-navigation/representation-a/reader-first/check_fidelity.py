exec(open('/var/folders/l6/44bf7nvs64j60f1mpyy88hdm0000gn/T/complete-annotation-reader-gkwz12f9/output/read_extract.py').read())
import re
norm=lambda s:re.sub(r'\s+',' ',s).strip()
def unmark(n):
 if isinstance(n,str):return n
 if n.a.get('class') in ['alg-reading-mark','alg-minor-break','alg-major-break']:return ''
 return ''.join(unmark(x) for x in n.c)
def mdblocks(s):
 out=[];in_code=False;buf=[]
 for l in s.splitlines():
  if l.startswith('```'):
   if in_code:out.append(('pre','\n'.join(buf)));buf=[]
   in_code=not in_code;continue
  if in_code:buf.append(l);continue
  if not l.strip():continue
  tag='h1' if l.startswith('# ') else 'h2' if l.startswith('## ') else 'p'
  l=re.sub(r'^#{1,2} ','',l)
  l=re.sub(r'\[([^\]]+)\]\([^)]*\)',r'\1',l).replace('`','')
  out.append((tag,l))
 return out
results={}
for stem,src in [('water','leetcode-11-container-with-most-water'),('course','leetcode-207-course-schedule')]:
 for lang in ['zh','en']:
  name=f'{stem}.{lang}.html';h=Parser();h.feed((P/name).read_text());ns=list(h.root.walk())
  article=next(n for n in ns if n.t=='article' and n.cls('alg-four-source'))
  blocks=[(n.t,n.text()) for n in article.c if isinstance(n,N) and n.t in ['p','pre','h1','h2']]
  expected=mdblocks((P/(src+('.en.md' if lang=='en' else '.md'))).read_text())
  diffs=[{'i':i,'html':a,'md':b} for i,(a,b) in enumerate(zip(blocks,expected)) if (a[0],norm(a[1]))!=(b[0],norm(b[1]))]
  readings=[n for n in ns if n.cls('alg-reading-text')]
  enps=data[stem+'.en.html']['source'];rd=[{'index':i,'read':unmark(n),'source':enps[str(i)]} for i,n in enumerate(readings) if norm(unmark(n))!=norm(enps[str(i)])]
  links=[n.a['href'] for n in article.walk() if n.t=='a']
  mdlinks=re.findall(r'\[[^\]]+\]\(([^)]+)\)',(P/(src+('.en.md' if lang=='en' else '.md'))).read_text())
  results[name]={'source_blocks_html':len(blocks),'source_blocks_md':len(expected),'block_differences':diffs,'external_links_exact':links==mdlinks,'reading_plaintext_differences':rd}
  print(name,results[name])
(P/'output/fidelity-checks.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
for stem in ['water','course']:
 h=Parser();h.feed((P/(stem+'.en.html')).read_text())
 print('\nCHUNKS',stem)
 for n in h.root.walk():
  if n.cls('alg-outline-paragraph'):
   idx=n.a['data-outline-index'];r=next(x for x in n.walk() if x.cls('alg-reading-text'))
   bundles=[x.text() for x in r.walk() if x.cls('alg-bundle')];stress=[x.text() for x in r.walk() if x.cls('alg-stress')]
   print(idx,'bundles',bundles,'stress',stress)
