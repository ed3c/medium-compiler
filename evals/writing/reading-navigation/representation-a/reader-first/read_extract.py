from pathlib import Path
from html.parser import HTMLParser
import json,os
P=Path('/var/folders/l6/44bf7nvs64j60f1mpyy88hdm0000gn/T/complete-annotation-reader-gkwz12f9')
class N:
 def __init__(self,t,a=None):self.t=t;self.a=dict(a or []);self.c=[]
 def text(self):return ''.join(x.text() if isinstance(x,N) else x for x in self.c)
 def walk(self):
  yield self
  for x in self.c:
   if isinstance(x,N):yield from x.walk()
 def cls(self,c):return c in self.a.get('class','').split()
class Parser(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.root=N('root');self.s=[self.root]
 def handle_starttag(self,t,a):
  n=N(t,a);self.s[-1].c.append(n)
  if t not in ['meta','link','br','input','img','hr','source']:self.s.append(n)
 def handle_endtag(self,t):
  for i in range(len(self.s)-1,0,-1):
   if self.s[i].t==t:self.s=self.s[:i];break
 def handle_data(self,s):self.s[-1].c.append(s)
data={}
for name in ['water.zh.html','water.en.html','course.zh.html','course.en.html']:
 s=(P/name).read_text();h=Parser();h.feed(s)
 nodes=list(h.root.walk());ps={n.a['data-alg-four-index']:n.text() for n in nodes if 'data-alg-four-index' in n.a}
 anns=[]
 for n in nodes:
  if n.cls('alg-outline-paragraph'):
   a=next(x for x in n.walk() if x.cls('alg-four-annotation'))
   rows=[{'class':x.a.get('class',''),'text':x.text(),'links':[y.a['href'] for y in x.walk() if y.t=='a']} for x in a.walk() if x.t=='p']
   active=[x.text() for x in a.walk() if x.cls('alg-active-word')]
   anns.append({'index':int(n.a['data-outline-index']),'role':a.a.get('data-alg-four-role'),'rows':rows,'active':active})
 data[name]={'source':ps,'annotations':anns}
(P/'output/extracted.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
(P/'output/actual-reads.json').write_text(json.dumps({'CODEX_THREAD_ID':os.environ.get('CODEX_THREAD_ID','UNAVAILABLE'),'inputs_read':['request.json']+[n for n in ['water.zh.html','water.en.html','course.zh.html','course.en.html','leetcode-11-container-with-most-water.md','leetcode-11-container-with-most-water.en.md','leetcode-207-course-schedule.md','leetcode-207-course-schedule.en.md']],'method':'All input bytes read with pathlib; full four Markdown source bodies displayed. Four HTML parsed; annotation fields read in ranges; cross-language duplicated fields compared. No outside sources opened.','limits':'Reading frozen HTML text and structure, not a browser rendering or interaction test.'},ensure_ascii=False,indent=2))
print([(n,len(v['source']),len(v['annotations'])) for n,v in data.items()])
for stem in ['water','course']:
 a=data[stem+'.zh.html']['annotations'];b=data[stem+'.en.html']['annotations']
 print(stem,'identical annotations',a==b)
 if a!=b:
  for x,y in zip(a,b):
   if x!=y:print('diff index',x['index'])
