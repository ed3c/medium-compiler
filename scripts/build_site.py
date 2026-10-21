#!/usr/bin/env python3
"""Build the dependency-free AI Engineer learning site from repository truth."""
from __future__ import annotations
import argparse, hashlib, html, json, re, shutil
from pathlib import Path
from urllib.parse import urlencode

ROOT=Path(__file__).resolve().parents[1]

import importlib.util
_diagram_spec=importlib.util.spec_from_file_location('article_diagrams',ROOT/'scripts/article_diagrams.py')
_diagram_module=importlib.util.module_from_spec(_diagram_spec)
_diagram_spec.loader.exec_module(_diagram_module)
DiagramRegistry=_diagram_module.DiagramRegistry

MAIN_ORIGIN='https://medium-compiler.vercel.app'
LAB_ORIGIN='https://medium-compiler.ga874199.workers.dev'
ARTICLES=[
    {
        "slug": "agent-handbook-zero-context",
        "title": "Agent 不是一段 Prompt：安全修補背後的七個工程決策",
        "description": "基於 AI Agent Handbook，透過安全修補案例追蹤 Model、Harness、Context、工具授權與完成驗證。",
        "source": "articles/agent-handbook-zero-context.md",
        "english_source": "articles/agent-handbook-zero-context.en.md",
        "companion_route": "/more-route/",
        "download_markdown": True,
    },
    {
        "slug": "agent-primitives-product-differentiation",
        "title": "每個人都在做 Agent，為什麼產品仍然可以不同？",
        "description": "從 Alex Atallah 的 Web 類比，思考交付條件、證據版本與每件完成工作的成本。",
        "source": "articles/agent-primitives-product-differentiation.md",
        "source_manifest": "references/transcripts/openrouter-agent-primitives.json",
        "context": "articles/agent-primitives-product-differentiation.context.json"
    },
    {
        "slug": "architect-amplifier-payment-decisions",
        "title": "架構師不再贏辯論的那一天：一張付款流程圖如何改變團隊的決策",
        "description": "從付款 Timeout、架構選型到主管決策，跟著團隊用證據重新理解架構爭論。",
        "source": "articles/architect-amplifier-payment-decisions.md",
        "video_id": "F8X9_Dp3ZUk",
        "next_article_slug": "checkout-reliability-large-traffic",
    },
    {
        "slug": "checkout-reliability-large-traffic",
        "title": "一場促銷揭露了付款系統的未知狀態：從故障實驗學會可靠的分散式系統",
        "description": "實作 Payment Idempotency、Outbox、Lost Reply、Crash Recovery，再擴展到 Load、Business Impact 和英文 Incident Communication。",
        "source": "articles/checkout-reliability-large-traffic.md",
        "download_markdown": True,
    },
    {
        "slug": "ai-engineer-learning-path",
        "title": "從軟體工程師到 AI Engineer",
        "description": "以 Ops Reconciliation Copilot 串起技術決策、實驗與來源證據。",
        "source": "articles/ai-engineer-learning-path.md"
    },
    {
        "slug": "application-engineering-colab",
        "title": "開發環境設定：逐章理解、本機實作與 Colab 操作紀錄",
        "description": "依原課逐章回答理論與實務，驗證四語言、MPS 與本機／Colab 的指定計算結果。",
        "source": "articles/application-engineering-colab.md",
        "notebook": "notebooks/application-engineering-colab.ipynb",
        "lesson": "phases/00-setup-and-tooling/01-dev-environment",
        "lesson_title": "開發環境設定",
        "next_lesson_title": "Git & Collaboration"
    },
    {
        "slug": "git-collaboration",
        "title": "Git 與協作：讓每次練習都能追蹤、隔離與備份",
        "description": "從暫存區到 GitHub 實際追蹤內容，完成 fork、分支推送、忽略規則與歷史閱讀。",
        "source": "articles/git-collaboration.md",
        "lesson": "phases/00-setup-and-tooling/02-git-and-collaboration",
        "lesson_title": "Git & Collaboration",
        "next_lesson_title": "Python Environments"
    },
    {
        "slug": "python-environments",
        "title": "Python 環境：讓套件彼此隔離，也讓專案能重新建立",
        "description": "實跑原課四個練習，追蹤套件位置、驗證 NumPy 隔離與 lockfile 重建，直接回答環境管理問題。",
        "source": "articles/python-environments.md",
        "lesson": "phases/00-setup-and-tooling/06-python-environments",
        "lesson_title": "Python Environments",
        "next_lesson_title": "Docker for AI"
    }
]

def lesson_navigation(item:dict, route:dict)->str:
    if not item.get('lesson'):
        return ''
    paths=[lesson['path'] for lesson in route['lessons']]
    if item['lesson'] not in paths:
        raise ValueError(f"Article lesson is missing from the selected route: {item['lesson']}")
    index=paths.index(item['lesson'])
    published={article['lesson']:article for article in ARTICLES if article.get('lesson')}
    links=[]
    if index and paths[index-1] in published:
        previous=published[paths[index-1]]
        links.append(f'<p><a rel="prev" href="/articles/{previous["slug"]}/">上一課：{html.escape(previous["lesson_title"])}</a></p>')
    if index+1 < len(paths):
        next_path=paths[index+1]
        following=published.get(next_path)
        if following:
            url=f'/articles/{following["slug"]}/'
            title=following['lesson_title']
            note=''
        else:
            url='https://aiengineeringfromscratch.com/lesson?'+urlencode({'path':next_path,'learningPath':route['id']})
            title=item['next_lesson_title']
            note='<p>本站下一篇實作文章尚未發布，先閱讀原課教材。</p>'
        links.append(f'<p><a rel="next" href="{html.escape(url,quote=True)}">下一課：{html.escape(title)}</a></p>'+note)
    else:
        links.append('<p>已到這條學習路線的最後一課。</p>')
    return '<section class="panel" aria-label="課程導航"><h2>接續課程</h2><p>'+html.escape(route['title'])+f' · 第 {index+1} / {len(paths)} 課</p>'+''.join(links)+'</section>'

def sequel_navigation(item:dict)->str:
    slug=item.get('next_article_slug')
    if not slug:
        return ''
    matches=[article for article in ARTICLES if article['slug']==slug]
    if len(matches)!=1:
        raise ValueError('Sequel article registry target is missing or ambiguous')
    target=matches[0]
    return (f'<section class="panel"><h2>延伸實作</h2><p>下一篇將付款狀態與 '
            f'Unknown Outcome 變成可執行的故障測試。</p>'
            f'<a rel="next" href="/articles/{html.escape(slug,quote=True)}/">'
            f'{html.escape(target["title"])}</a></section>')

def inline(text:str)->str:
    text=html.escape(text,quote=False)
    text=re.sub(r'`([^`]+)`',r'<code>\1</code>',text)
    text=re.sub(r'\*\*([^*]+)\*\*',r'<strong>\1</strong>',text)
    text=re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)',r'<a href="\2" target="_blank" rel="noreferrer">\1</a>',text)
    return text

def markdown(text:str, diagrams=None)->str:
    out=[]; paragraph=[]; in_code=False; code=[]; list_kind=None
    mermaid=False; diagram_index=0
    def flush_p():
        nonlocal paragraph
        if paragraph:
            out.append('<p>'+inline(' '.join(x.strip() for x in paragraph))+'</p>');paragraph=[]
    def close_list():
        nonlocal list_kind
        if list_kind: out.append(f'</{list_kind}>');list_kind=None
    for raw in text.splitlines():
        line=raw.rstrip()
        if line.startswith('```') or line.startswith('~~~'):
            flush_p();close_list()
            if in_code:
                out.append(diagrams.figure('\n'.join(code),diagram_index) if mermaid and diagrams else '<pre><code>'+html.escape('\n'.join(code))+'</code></pre>');diagram_index+=int(mermaid);code=[];in_code=False;mermaid=False
            else: in_code=True;mermaid=diagrams is not None and line[3:].strip().lower()=='mermaid'
            continue
        if in_code: code.append(line);continue
        if not line.strip(): flush_p();close_list();continue
        img=re.fullmatch(r'!\[([^\]]*)\]\((https://medium-compiler\.vercel\.app/assets/alg-four/[a-z0-9-]+\.svg)\)',line)
        if img:
            flush_p();close_list()
            out.append('<figure class="article-figure"><img loading="lazy" src="'+html.escape(img.group(2),quote=True)+'" alt="'+html.escape(img.group(1),quote=True)+'"></figure>')
            continue
        m=re.match(r'^(#{1,4})\s+(.+)$',line)
        if m:
            flush_p();close_list();n=len(m.group(1));out.append(f'<h{n}>'+inline(m.group(2))+f'</h{n}>');continue
        m=re.match(r'^[-*]\s+(.+)$',line)
        if m:
            flush_p()
            if list_kind!='ul': close_list();out.append('<ul>');list_kind='ul'
            out.append('<li>'+inline(m.group(1))+'</li>');continue
        m=re.match(r'^\d+\.\s+(.+)$',line)
        if m:
            flush_p()
            if list_kind!='ol': close_list();out.append('<ol>');list_kind='ol'
            out.append('<li>'+inline(m.group(1))+'</li>');continue
        if line.startswith('> '):
            flush_p();close_list();out.append('<blockquote>'+inline(line[2:])+'</blockquote>');continue
        paragraph.append(line)
    flush_p();close_list()
    if in_code:
        if mermaid: raise ValueError('INCOMPLETE_MERMAID_BLOCK')
        out.append('<pre><code>'+html.escape('\n'.join(code))+'</code></pre>')
    if diagrams: diagrams.check_complete()
    return '\n'.join(out)

def youtube_article_embed(item:dict)->str:
    """Render a source-bound, responsive YouTube iframe from an allowlisted video ID."""
    video_id=item.get('video_id')
    if not video_id:
        return ''
    if not isinstance(video_id,str) or not re.fullmatch(r'[A-Za-z0-9_-]{11}',video_id):
        raise ValueError('Invalid YouTube video ID in site article registry')
    video_url='https://www.youtube.com/watch?v='+video_id
    return (f'<section class="article-video" aria-label="訪談影片">'
            f'<div class="youtube-frame"><iframe '
            f'src="https://www.youtube-nocookie.com/embed/{video_id}" '
            f'title="Beyond Coding — Gregor Hohpe 訪談" '
            f'loading="lazy" referrerpolicy="strict-origin-when-cross-origin" '
            f'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" '
            f'allowfullscreen></iframe></div>'
            f'<p class="video-caption">原始訪談：<a href="{video_url}" target="_blank" '
            f'rel="noopener noreferrer">Gregor Hohpe × Patrick Akil · Beyond Coding</a></p>'
            f'</section>')

def page(title:str, body:str, active:str='', main_origin:str='')->str:
    nav=[('home','/','首頁'),('learning','/learning/','Learning'),('alg','/cefr-alg-c2/','CEFR ALG C2+'),('experiments','/experiments/','Experiments'),('evals','/ai-evals/','AI Evals'),('loops','/loops/','Loops'),('scopes','/scopes/','Scopes'),('article','/articles/','Articles'),('reliability','/reliability/','Reliability Lab'),('transcripts','/transcripts/','逐字稿來源')]
    links=''.join(f'<a class="{"active" if key==active else ""}" href="{LAB_ORIGIN+href if key=="reliability" else main_origin+href}">{label}</a>' for key,href,label in nav)
    return f'''<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title><meta name="description" content="Evidence-driven AI Engineer learning, experiments and articles."><link rel="stylesheet" href="/assets/styles.css"></head><body><header><a class="brand" href="{main_origin}/">AI Engineer Lab</a><nav>{links}</nav></header><main>{body}</main><footer>Curriculum guides learning · Ops owns experiments · medium-compiler explains and publishes.</footer></body></html>'''

def build_reliability(out:Path, main_origin:str='')->None:
    lab_dir=out/'reliability';lab_dir.mkdir(parents=True)
    lab_source=ROOT/'site/reliability'
    shutil.copytree(lab_source,out/'assets/reliability')
    lab_html=(lab_source/'fragment.html').read_text(encoding='utf-8')
    sqlite_version=json.loads((ROOT/'references/sqlite-wasm-lock.json').read_text(encoding='utf-8'))['version']
    lab_html=lab_html.replace('{{SQLITE_WASM_VERSION}}',html.escape(sqlite_version))
    lab_html=lab_html.replace('href="/articles/',f'href="{MAIN_ORIGIN}/articles/')
    (lab_dir/'index.html').write_text(page('Checkout Reliability Lab',lab_html,'reliability',main_origin),encoding='utf-8')

def learning_state()->dict:
    path=ROOT/'LEARNING.md'
    if not path.exists():
        return {'status':'NOT_INITIALIZED','entry_point':None,'pace':None,'progress_rows':0,'review_items':0}
    text=path.read_text(encoding='utf-8')
    entry=re.search(r'^- Entry point:\s*(.+)$',text,re.M)
    pace=re.search(r'^- Pace:\s*(.+)$',text,re.M)
    progress=0
    if '## Progress log' in text:
        section=text.split('## Progress log',1)[1].split('## ',1)[0]
        progress=sum(1 for l in section.splitlines() if l.startswith('|') and '---' not in l and 'Date' not in l)
    reviews=0
    if '## Review queue' in text:
        section=text.split('## Review queue',1)[1].split('## ',1)[0]
        reviews=sum(1 for l in section.splitlines() if l.strip().startswith(('-', '*')))
    return {'status':'ACTIVE','entry_point':entry.group(1) if entry else 'UNKNOWN','pace':pace.group(1) if pace else 'UNKNOWN','progress_rows':progress,'review_items':reviews}

def cards(snapshot:dict,limit=None)->str:
    items=snapshot['templates'][:limit] if limit else snapshot['templates']
    chunks=[]
    for t in items:
        outcomes=' · '.join(t['outcomes'])
        chunks.append(f'''<article class="card"><div class="eyebrow">{html.escape(t['category'])}</div><h3>{html.escape(t['title'])}</h3><p>{html.escape(t['question'])}</p><div class="meta"><b>Trigger</b> {html.escape(t['trigger'])}</div><div class="meta"><b>Outcomes</b> {html.escape(outcomes)}</div><div class="gate">{html.escape(t['promotion_gate'])}</div></article>''')
    return '<div class="cards">'+''.join(chunks)+'</div>'

def add_local_video_controls(text:str)->str:
    replacements=[
        ('<div id="fixed-media" hidden>', '''<div id="fixed-media" hidden>
<div class="tech-actions"><label for="local-video-file">Choose local video <input id="local-video-file" type="file" accept="video/*"></label><button id="reset-lesson-video" class="secondary" disabled>Restore supplied video</button></div>
<p id="local-video-status" class="muted tiny" role="status">Choose a video from this device. It stays in your browser; no upload.</p>'''),
        ('<p class="muted tiny">Supplied Hypit video', '<p id="supplied-video-note" class="muted tiny">Supplied Hypit video'),
        ('</p></div>\n<div id="pass-script"', '''</p></div>
<p id="local-video-warning" class="muted tiny" hidden>Local video is not checked against this lesson. Lesson hashes and the practice receipt refer to the supplied lesson, not this local file. Supplied captions are disabled.</p>
<div id="pass-script"'''),
        ('</body>', '<script defer src="./local-lesson-video.js"></script></body>'),
    ]
    for anchor,replacement in replacements:
        if text.count(anchor)!=1:
            raise ValueError(f'Technical local-video import requires one anchor: {anchor!r}')
        text=text.replace(anchor,replacement,1)
    return text

def import_alg(out:Path)->dict:
    """Verify the pinned snapshot, then adapt navigation for our clean URLs."""
    lock=json.loads((ROOT/'references/cefr-alg-site-lock.json').read_text())
    source=ROOT/'site/cefr-alg-c2'
    actual={p.relative_to(source).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
            for p in source.rglob('*') if p.is_file()}
    if actual != lock['files']:
        raise ValueError('CEFR ALG snapshot differs from its pinned file manifest')
    target=out/'cefr-alg-c2'
    shutil.copytree(source,target)
    shutil.copyfile(ROOT/'site/local-lesson-video.js',target/'local-lesson-video.js')
    for name in ('index.html','compare.html','technical.html'):
        path=target/name
        text=path.read_text(encoding='utf-8')
        text=text.replace('<head>','<head><base href="/cefr-alg-c2/">',1)
        text=text.replace('</head>','<style>.topbar{height:auto;min-height:90px;gap:12px;flex-wrap:wrap;padding-top:14px;padding-bottom:14px}</style></head>',1)
        if name=='compare.html':
            text=text.replace('href="#lab"','href="./compare#lab"',1)
        if name=='technical.html':
            text=add_local_video_controls(text)
            text=text.replace('Downstream import remains pending','Pinned snapshot imported here')
            text=text.replace('Medium owns the subsequent pinned snapshot, lock and build import, which remains pending.',
                              'Medium verifies and imports this pinned snapshot. Its source revision and built bytes are recorded in provenance.json.')
            text=text.replace('</body>','''<script>
for (const link of document.querySelectorAll('a[href^="#"]')) {
  link.href = location.pathname + location.search + link.hash;
}
</script></body>''',1)
        text=text.replace('</header>','<a class="text-link" href="/">AI Engineer Lab ↗</a></header>',1)
        path.write_text(text,encoding='utf-8')
    lock['output_sha256']={p.relative_to(target).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                           for p in sorted(target.rglob('*')) if p.is_file()}
    (target/'provenance.json').write_text(json.dumps(lock,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return lock

def transcript_source(item:dict, source_bytes:bytes, article_dir:Path)->tuple[str,dict]:
    """Bind the article to its reviewed source metadata, never publish raw transcripts."""
    manifest_bytes=(ROOT/item['source_manifest']).read_bytes()
    context=json.loads((ROOT/item['context']).read_bytes())
    article_hash=hashlib.sha256(source_bytes).hexdigest()
    manifest_hash=hashlib.sha256(manifest_bytes).hexdigest()
    if (context['article_sha256']!=article_hash or context['source_manifest']!=item['source_manifest']
            or context['source_manifest_sha256']!=manifest_hash):
        raise ValueError('Transcript article or source metadata changed since its author review')
    meta=json.loads(manifest_bytes)
    if (meta.get('schema_version')!='medium-transcript-source@1'
            or meta.get('publication')!='metadata_only_no_transcript_republication'
            or meta.get('audio_verified') is not False):
        raise ValueError('Unsupported transcript provenance')
    scope=context['source_scope']
    timestamps=scope.get('timestamps',[])
    if (not timestamps or any(not re.fullmatch(r'\d{2}:[0-5]\d:[0-5]\d', t) for t in timestamps)
            or timestamps!=sorted(set(timestamps))):
        raise ValueError('Transcript source scope requires ordered exact timestamps')
    if item['slug']=='agent-primitives-product-differentiation' and 'public_note' not in scope:
        scope_note='14:05–15:40 的基本元件類比。'
        analysis_note='商品頁案例與工程設計是作者延伸分析。'
    else:
        scope_note=scope.get('public_note','').strip()
        analysis_note=scope.get('analysis_note','').strip()
        if not scope_note or not analysis_note:
            raise ValueError('New podcast articles require their own scope and analysis notes')
    # Source metadata is controlled by the repository, but URL attributes are escaped.
    video_link=''
    if meta.get('video_url'):
        h,m,s=map(int,timestamps[0].split(':'))
        video=html.escape(meta['video_url']+'&t='+str(h*3600+m*60+s),quote=True)
        label=timestamps[0][3:] if timestamps[0].startswith('00:') else timestamps[0]
        video_link=f'<a href="{video}" target="_blank" rel="noreferrer">回看原影片 · {label}</a> · '
    provider=html.escape(meta['source_url'],quote=True)
    fetched=html.escape(meta.get('retrieved_at') or 'HTML 匯入，未宣稱 HTTP 取得時間')
    panel=f'''<section class="panel" aria-label="文章來源"><h2>閱讀來源</h2>
<p>{video_link}<a href="{provider}" target="_blank" rel="noreferrer">第三方逐字稿 · PodScripts</a></p>
<p>本篇取材範圍：{html.escape(scope_note)}{html.escape(analysis_note)}文字依第三方轉錄核對，尚未逐句核對音訊。</p>
<p>來源取得時間：{fetched}。快照包含 {meta['segment_count']} 個區段，最後時間戳 {html.escape(meta['last_timestamp'])}；這不證明整集完整。</p>
<p><a href="article.md" download>下載 Medium 文章（Markdown）</a> · <a href="source.json">來源紀錄</a> · <a href="/transcripts/">取得逐字稿的方法</a></p></section>'''
    (article_dir/'source.json').write_bytes(manifest_bytes)
    (article_dir/'article.md').write_bytes(source_bytes)
    return panel, {'source_manifest':item['source_manifest'],'source_manifest_sha256':manifest_hash,
                   'source_route':'/articles/'+item['slug']+'/source.json','audio_verified':False}



def render_alg_four(out:Path)->dict:
    """Render byte-pinned source with navigation anchors and a separate ALG Four sidecar."""
    manifest_path=ROOT/'references/learning/alg-four-group-anagrams.json'
    raw=manifest_path.read_bytes()
    data=json.loads(raw)
    if (data.get('schema_version')!='alg-four-reading-projection@4'
            or data.get('owner')!='alg-four'
            or data.get('format')!='source_preserved_with_right_outline'):
        raise ValueError('ALG Four requires source-preserving paragraph annotation schema')
    source=data.get('source',{})
    source_path=(ROOT/source.get('path','')).resolve()
    if not source_path.is_relative_to(ROOT.resolve()) or not source_path.is_file():
        raise ValueError('ALG Four source must resolve inside repository')
    source_bytes=source_path.read_bytes()
    git_blob=hashlib.sha1(f"blob {len(source_bytes)}\0".encode()+source_bytes).hexdigest()
    if git_blob!=source.get('git_blob'):
        raise ValueError('ALG Four pinned source blob changed without lesson revision')
    original_html=markdown(source_bytes.decode('utf-8'))
    english=data.get('english_source',{})
    english_path=(ROOT/english.get('path','')).resolve()
    if not english_path.is_relative_to(ROOT.resolve()) or not english_path.is_file():
        raise ValueError('ALG Four aligned English source is missing')
    english_bytes=english_path.read_bytes()
    english_blob=hashlib.sha1(f"blob {len(english_bytes)}\0".encode()+english_bytes).hexdigest()
    if english_blob!=english.get('git_blob'):
        raise ValueError('ALG Four aligned English source blob changed')
    english_html=markdown(english_bytes.decode('utf-8'))
    def structure(markup):
        return [
            ('h'+a if a else b) for a,b in
            re.findall(r'<h([1-4])>.*?</h\1>|<(p|blockquote)>.*?</\2>',markup,re.S)
        ]
    if structure(original_html)!=structure(english_html):
        raise ValueError('ALG Four bilingual heading/paragraph structure drift')
    if re.findall(r'<pre><code>.*?</code></pre>',original_html,re.S)!=re.findall(r'<pre><code>.*?</code></pre>',english_html,re.S):
        raise ValueError('ALG Four bilingual source code diverged')
    if original_html.count('<figure')!=7 or english_html.count('<figure')!=7:
        raise ValueError('ALG Four canonical Cover + six Figure slots missing')
    pattern=re.compile(r'<p>.*?</p>|<blockquote>.*?</blockquote>',re.S)
    paragraphs=list(pattern.finditer(original_html))
    notes=data.get('paragraph_annotations',[])
    if not paragraphs or len(notes)!=len(paragraphs):
        raise ValueError('ALG Four must annotate every original prose paragraph without omissions')
    english_paragraphs=list(pattern.finditer(english_html))
    if len(english_paragraphs)!=len(paragraphs):
        raise ValueError('ALG Four bilingual paragraph count changed')
    for i,(native,note) in enumerate(zip(english_paragraphs,notes)):
        source_text=html.unescape(re.sub(r'<[^>]+>','',native.group(0)))
        if note.get('paragraph_index')!=i or note.get('english_source')!=source_text:
            raise ValueError('ALG Four aligned English paragraph drift')
    decisions={d['id']:d for d in data.get('decisions',[])}
    if not decisions or len(decisions)!=len(data.get('decisions',[])):
        raise ValueError('ALG Four has duplicate or empty decision IDs')
    items=data.get('active_items',[])
    item_ids=[x.get('id') for x in items]
    if len(item_ids)!=len(set(item_ids)):
        raise ValueError('ALG Four Active item IDs must be unique')
    index_items={}
    for item in items:
        i=item.get('paragraph_index')
        if (not isinstance(i,int) or not 0<=i<len(paragraphs)
                or item.get('decision_id') not in decisions
                or not item.get('english_sentence') or not item.get('term')
                or item.get('source_quote','').casefold() not in notes[i].get('english_source','').casefold()):
            raise ValueError('ALG Four Active word has no exact source paragraph, decision or sentence')
        index_items.setdefault(i,[]).append(item)
    for i,note in enumerate(notes):
        if (note.get('paragraph_index')!=i
                or note.get('kind') not in ('PASSIVE','PASSIVE_AND_ACTIVE')
                or not note.get('zh_note')
                or not note.get('decision_ids')
                or any(d not in decisions for d in note['decision_ids'])):
            raise ValueError('ALG Four paragraph annotation index, role or decision coverage is invalid')
    policy=data.get('learning_policy',{})
    if (policy.get('goal_active_lexical_items')!=2000
            or policy.get('goal_linked_english_sentences')!=2000
            or policy.get('learner_evidence')!='NOT_OBSERVED'
            or policy.get('scope')!='cumulative_across_source_articles_not_per_single_article'):
        raise ValueError('ALG Four 2000-item cross-article selection policy or evidence status invalid')
    import importlib.util
    projection_path=ROOT/'scripts/alg_four_projection.py'
    spec=importlib.util.spec_from_file_location('alg_four_projection',projection_path)
    projection=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(projection)
    body,outline,para_count,heading_count=projection.render_outline(original_html,notes,decisions,index_items)
    if para_count!=len(notes):
        raise ValueError('ALG Four rendering omitted original paragraphs')
    esc=html.escape
    instructions=(
        '<section class="page-head alg-four-head">'
        '<div class="eyebrow">ALG Four · Source-locked reading companion</div>'
        '<h1>Group Anagrams · 文章段落索引與 Active／Passive</h1>'
        '<p>先閱讀完整原文；右側依 Markdown 標題層級展開索引。'
        '點擊任一段落就能跳轉，捲動時會自動顯示對應語塊與練習。'
        '黃色詞彙為 Active；Passive 的句型折行與主重音只存在於註解視圖，不變更原始文章。</p>'
        '<p>四次 cognitive encounters 使用同一份原文，不產生四份改寫文章。'
        'Active 2,000 詞與 2,000 句是跨文章累積目標，本頁沒有學習結果觀察。</p>'
        '<p><a href="/alg-four/source.json">Source / annotation manifest</a> · '
        '<a href="https://github.com/ed3c/medium-compiler/blob/main/'+esc(source['path'],quote=True)+
        '">查看原始 Markdown</a></p></section>')
    target=out/'alg-four'
    target.mkdir()
    for asset in ('alg-four.css','alg-four.js'):
        shutil.copyfile(ROOT/'site'/asset,out/'assets'/asset)
    full_body=(instructions+'<link rel="stylesheet" href="/assets/alg-four.css">'
               '<div class="alg-four-reading-layout">'
               '<article class="article alg-four-source">'+body+'</article>'+outline+'</div>'
               '<script defer src="/assets/alg-four.js"></script>')
    (target/'index.html').write_text(
        page('ALG Four · Annotated Original',full_body,'learning'),encoding='utf-8')
    (target/'source.json').write_bytes(raw)
    return {'route':'/alg-four/','source_manifest':'/alg-four/source.json',
            'manifest_sha256':hashlib.sha256(raw).hexdigest(),'source_blob':git_blob,
            'english_source_blob':english_blob,
            'annotated_paragraphs':len(notes),'active_paragraphs':sum(n['kind']=='PASSIVE_AND_ACTIVE' for n in notes),
            'active_items_collected':len(items),'active_vocabulary_goal':2000,
            'source_article_unchanged':True,'learning_evidence':'NOT_OBSERVED',
            'annotation_projection':'right_outline','heading_count':heading_count,
            'native_runtime':'NOT_RUN'}


def build(out:Path)->dict:
    out=out.resolve()
    if out.exists(): shutil.rmtree(out)
    out.mkdir(parents=True)
    (out/'assets').mkdir()
    diagram_registry=DiagramRegistry(ROOT)
    diagram_registry.install_assets(out)
    shutil.copytree(ROOT/'site/alg-four-figures',out/'assets/alg-four')
    shutil.copyfile(ROOT/'site/_headers',out/'_headers')
    css=(ROOT/'site/styles.css').read_text(encoding='utf-8');(out/'assets/styles.css').write_text(css,encoding='utf-8')
    snapshot=json.loads((ROOT/'references/ops-experiment-catalog.json').read_text())
    state=learning_state()
    hero=f'''<section class="hero"><div class="eyebrow">Evidence-driven learning runtime</div><h1>AI Engineer<br>from Evidence</h1><p>課程決定現在研究哪種能力；Ops Reconciliation Copilot 負責真實實驗與 runtime evidence；medium-compiler 把已成立的理解編譯成文章與學習網站。</p><div class="actions"><a class="button" href="/learning/">開始 Learning</a><a class="button secondary" href="/experiments/">查看 Experiments</a></div></section>'''
    stats=f'''<section class="stats"><div><b>{len(snapshot['templates'])}</b><span>Experiment templates</span></div><div><b>{state['progress_rows']}</b><span>Lessons logged</span></div><div><b>{len(ARTICLES)}</b><span>Learning articles</span></div><div><b>{state['status']}</b><span>Learning state</span></div></section>'''
    flow='''<section><div class="section-title"><span>Runtime</span><h2>Learn → Experiment → Evidence → Explain → Ship</h2></div><div class="flow"><div>Curriculum<br><small>lesson / placement</small></div><i>→</i><div>Ops Lab<br><small>EXPERIMENT / NO_CHANGE</small></div><i>→</i><div>Evidence<br><small>tests / evals / runtime</small></div><i>→</i><div>Compiler<br><small>zero-context explanation</small></div><i>→</i><div>Site<br><small>article / checkpoint</small></div></div></section>'''
    exp=f'''<section><div class="section-title"><span>Experiment Library</span><h2>把 syllabus 變成可驗證實驗，而不是產品 backlog</h2></div>{cards(snapshot,3)}<p><a href="/experiments/">查看全部 {len(snapshot['templates'])} 個範本 →</a></p></section>'''
    article_links=''.join(f'<article class="card"><h3>{html.escape(a["title"])}</h3><p>{html.escape(a["description"])}</p><a href="/articles/{a["slug"]}/">閱讀文章 →</a></article>' for a in ARTICLES)
    art='<section><div class="section-title"><span>Learning Articles</span><h2>從環境到應用，逐步留下可驗證成果</h2></div><div class="cards">'+article_links+'</div></section>'
    alg='''<section id="cefr-alg" class="alg-section" aria-labelledby="alg-title"><div class="section-title"><span>English Studio · Listening first</span><h2 id="alg-title">CEFR ALG C2+</h2><p>從理解情境開始，聽懂想法，再選擇用自己的語言表達。以技術決策、工作對話與生活情境練習精準而自然的英文。</p></div><div class="cards"><article class="card"><div class="eyebrow">01 · Understand</div><h3>先聽懂，再開口</h3><p>4 個情境、12 個片段，提供直接與細膩兩種英文版本。預設 Parler TTS，可切換 Kokoro browser；按播放即可接續朗讀；字幕由你決定何時打開。</p><a href="/cefr-alg-c2/">進入 ALG 情境 →</a></article><article class="card"><div class="eyebrow">02 · Express</div><h3>保留意思，說得自然</h3><p>自由選擇口語錄音與寫作練習。從修改前後的例子，觀察如何保留條件、不確定性與證據。</p><a href="/cefr-alg-c2/">開啟 English Studio →</a></article><article class="card"><div class="eyebrow">03 · Compare</div><h3>找到想繼續聽的聲音</h3><p>用相同對話比較五組已生成的語音，隱藏模型名稱並記下感受。可在瀏覽器以 Kokoro 生成其他課程，無需 API key。</p><a href="/cefr-alg-c2/compare.html">試聽 Voice Lab →</a></article></div><p class="alg-note">C2+ 是學習目標與專案名稱；CEFR 最高正式等級為 C2。本站不提供能力認證。五組音檔可直接播放，首次瀏覽器生成需下載模型。<a href="/cefr-alg-c2/provenance.json">查看來源版本</a></p></section>'''
    alg=alg.replace('</section>','<p><a href="/cefr-alg-c2/technical?lesson=software-factory-sole-acceptance">Software Factory · 英文、圖解與 Four-Pass 練習 →</a></p></section>')
    alg_provenance=import_alg(out)
    import importlib.util
    eval_spec=importlib.util.spec_from_file_location("ai_evals_site",ROOT/"scripts/ai_evals_site.py")
    eval_module=importlib.util.module_from_spec(eval_spec)
    eval_spec.loader.exec_module(eval_module)
    render_reports=eval_module.render_reports
    eval_provenance=render_reports(ROOT,out,page,markdown)
    loop_spec=importlib.util.spec_from_file_location("loop_site",ROOT/"scripts/loop_site.py")
    loop_module=importlib.util.module_from_spec(loop_spec)
    loop_spec.loader.exec_module(loop_module)
    loop_provenance=loop_module.render_loops(ROOT,out,page)
    scope_spec=importlib.util.spec_from_file_location("scope_site",ROOT/"scripts/scope_site.py")
    scope_module=importlib.util.module_from_spec(scope_spec)
    scope_spec.loader.exec_module(scope_module)
    scope_provenance=scope_module.render_scopes(ROOT,out,page)
    eval_home='<section class="panel"><div class="eyebrow">Engineering judgment</div><h2>AI Evals · Soodles</h2><p>閱讀六份歷史 Agent reports 的工程評估，區分可支持的判斷與缺少的證據。</p><a href="/ai-evals/">查看 AI Evals 報告 →</a></section>'
    more_intro='<section class="panel"><h2>More Route · Seven Engineering Decisions</h2><p>閱讀 AI Agent Handbook 的 Zero Context 教學，追蹤七個工程決策、失敗反例與可觀察證據。</p><a href="/more-route/">Open decision explorer →</a></section>'
    (out/'index.html').write_text(page('AI Engineer Lab',hero+stats+eval_home+alg+flow+exp+art+more_intro,'home'),encoding='utf-8')
    (out/'experiments').mkdir();(out/'experiments/index.html').write_text(page('Experiments · AI Engineer Lab',f'''<section class="page-head"><div class="eyebrow">Ops Reconciliation Copilot</div><h1>Experiment Templates</h1><p>這些卡片來自 Ops provider snapshot <code>{snapshot['provider_revision'][:12]}</code>。範本只定義實驗邊界，不代表實驗已執行，也不授權 production promotion。</p></section>{cards(snapshot)}''','experiments'),encoding='utf-8')
    learn_body=f'''<section class="page-head"><div class="eyebrow">AI Engineering from Scratch</div><h1>Learning Progress</h1><p>目前狀態：<strong>{state['status']}</strong></p></section><section class="panel"><h2>Source of truth</h2><p><code>LEARNING.md</code> 由 upstream <code>start-learning</code> / <code>learn</code> skills 管理。medium-compiler 不自行猜 placement，也不把文章進度當課程進度。</p><pre><code>Use start-learning to begin the course.
Use learn to continue one lesson.</code></pre><dl><dt>Entry point</dt><dd>{state['entry_point'] or '尚未執行 placement'}</dd><dt>Pace</dt><dd>{state['pace'] or '尚未設定'}</dd><dt>Logged lessons</dt><dd>{state['progress_rows']}</dd><dt>Review items</dt><dd>{state['review_items']}</dd></dl></section>'''
    learn_body+='<section class="panel"><h2>從第一篇學習文章開始</h2><p>逐章理解開發環境，實作四語言與 Python 運算，再核對本機與 Colab 的替代範圍；閱讀或執行範例不會自動變更課程進度。</p><a href="/articles/application-engineering-colab/">開啟開發環境設定學習文章 →</a></section>'
    learn_body+='<section class="panel"><h2>More Route · Agent Engineering</h2><p>從真實 Domain 問題建立理論、Runtime、反例及可重現驗證的關係。</p><a href="/more-route/">Explore seven engineering decisions →</a></section>'
    learn_body+='<section class="panel"><h2>ALG Four · English from Engineering</h2><p>從完整演算法文章的所有 Decision 與 Runtime 出發，以四遍學習英文理解與主動生成。</p><a href="/alg-four/">Open English acquisition worksheet →</a></section>'
    (out/'learning').mkdir();(out/'learning/index.html').write_text(page('Learning · AI Engineer Lab',learn_body,'learning'),encoding='utf-8')
    alg_four_provenance=render_alg_four(out)
    # Single-browser fault experiments are static and require no server credentials.
    build_reliability(out)
    # More Route is a static, reviewed explanation. No tool, task or browser effects.
    more_source=ROOT/'site/more-route'
    more_dir=out/'more-route'
    more_dir.mkdir()
    more_manifest_bytes=(ROOT/'references/upstream/more-route-learning-sources.json').read_bytes()
    more_manifest=json.loads(more_manifest_bytes)
    if (more_manifest.get('schema_version')!='more-route-learning-sources@1'
            or more_manifest.get('semantics',{}).get('decision_count')!=7
            or len(more_manifest.get('sources',[]))!=2):
        raise ValueError('More Route source registry is invalid for this selected case')
    for asset in ('more-route.js','more-route.css'):
        shutil.copyfile(more_source/asset,out/'assets'/asset)
    more_fragment=(more_source/'fragment.html').read_text(encoding='utf-8')
    if (len(re.findall(r'data-mr-choice="D[1-7]"',more_fragment))!=7
            or len(re.findall(r'data-mr-panel="D[1-7]"',more_fragment))!=7):
        raise ValueError('More Route needs seven matching decisions and source panels')
    more_body='<link rel="stylesheet" href="/assets/more-route.css">'+more_fragment+'<script defer src="/assets/more-route.js"></script>'
    (more_dir/'index.html').write_text(page('More Route · Agent Engineering',more_body,'learning'),encoding='utf-8')
    (more_dir/'source.json').write_bytes(more_manifest_bytes)
    more_provenance={'route':'/more-route/','decision_count':7,'source_manifest':'/more-route/source.json',
                     'manifest_sha256':hashlib.sha256(more_manifest_bytes).hexdigest(),
                     'native_experiment':'NOT_RUN'}
    article_root=out/'articles';article_root.mkdir()
    (article_root/'index.html').write_text(page('Articles · AI Engineer Lab','<section class="page-head"><h1>Learning Articles</h1><p>閱讀操作指南與來源說明，保存自己的練習成果。</p></section><div class="cards">'+article_links+'</div>','article'),encoding='utf-8')
    transcript_dir=out/'transcripts';transcript_dir.mkdir()
    for asset in ('transcripts.js', 'transcripts.css'):
        shutil.copyfile(ROOT/'site'/asset,out/'assets'/asset)
    transcript_body='<link rel="stylesheet" href="/assets/transcripts.css">'+(ROOT/'site/transcripts.html').read_text(encoding='utf-8')
    transcript_body+='<details class="panel"><summary>CLI 取得來源與寫作流程</summary><article class="article">'+markdown((ROOT/'docs/transcripts.md').read_text(encoding='utf-8'))+'</article></details>'
    (transcript_dir/'index.html').write_text(page('逐字稿來源 · AI Engineer Lab',transcript_body,'transcripts'),encoding='utf-8')
    course_route=json.loads((ROOT/'references/upstream/software-engineering-fundamentals.json').read_text())
    article_provenance=[]
    for item in ARTICLES:
        source_bytes=(ROOT/item['source']).read_bytes()
        content_html=markdown(source_bytes.decode('utf-8'),diagram_registry.for_article(item['source']))
        video_html=youtube_article_embed(item)
        if video_html:
            if '</p>' not in content_html:
                raise ValueError('Video article must have an introductory paragraph')
            content_html=content_html.replace('</p>','</p>'+video_html,1)
        article_body='<article class="article"><div class="article-source">Built from <code>'+html.escape(item['source'])+'</code></div>'+content_html+lesson_navigation(item,course_route)+sequel_navigation(item)+'</article>'
        if item.get('companion_route'):
            route=html.escape(item['companion_route'],quote=True)
            article_body+='<section class="panel"><h2>Interactive Decision Explorer</h2><p>Explore seven decisions, alternatives and counterexamples with the original source index.</p><a href="'+route+'">Open interactive lesson →</a></section>'
        article_dir=article_root/item['slug'];article_dir.mkdir()
        source_record={}
        if item.get('source_manifest'):
            panel,source_record=transcript_source(item,source_bytes,article_dir)
            article_body+=panel
        (article_dir/'index.html').write_text(page(item['title'],article_body,'article'),encoding='utf-8')
        if item.get('video_id') or item.get('download_markdown'):
            (article_dir/'article.md').write_bytes(source_bytes)
        if item.get('english_source'):
            english_bytes=(ROOT/item['english_source']).read_bytes()
            (article_dir/'article.en.md').write_bytes(english_bytes)
            source_record['english_source']=item['english_source']
            source_record['english_sha256']=hashlib.sha256(english_bytes).hexdigest()
        if item.get('video_id'):
            source_record['video_id']=item['video_id']
            source_record['video_url']='https://www.youtube.com/watch?v='+item['video_id']
        article_provenance.append({'source':item['source'],'route':'/articles/'+item['slug']+'/','sha256':hashlib.sha256(source_bytes).hexdigest(),**source_record})
        if item.get('notebook'):
            destination=out/item['notebook'];destination.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(ROOT/item['notebook'],destination)
    provenance={'schema_version':'ai-engineer-site-build@1','article':'articles/ai-engineer-learning-path.md','ops_provider_revision':snapshot['provider_revision'],'curriculum_revision':json.loads((ROOT/'references/upstream/ai-engineering-skills-lock.json').read_text())['revision'],'learning':state,'articles':article_provenance}
    provenance['more_route']=more_provenance
    provenance['alg_four']=alg_four_provenance
    provenance['ai_evals']=eval_provenance
    provenance['loops']=loop_provenance
    provenance['scopes']=scope_provenance
    provenance['cefr_alg']={'repository':alg_provenance['repository'],'revision':alg_provenance['revision'],'route':alg_provenance['route'],'manifest':'/cefr-alg-c2/provenance.json'}
    (out/'provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return provenance

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=ROOT/'dist');a=p.parse_args()
    print(json.dumps(build(a.out),ensure_ascii=False,indent=2))

if __name__=='__main__':main()
