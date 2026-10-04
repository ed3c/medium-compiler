#!/usr/bin/env python3
"""Build the dependency-free AI Engineer learning site from repository truth."""
from __future__ import annotations
import argparse, hashlib, html, json, re, shutil
from pathlib import Path
from urllib.parse import urlencode

ROOT=Path(__file__).resolve().parents[1]
ARTICLES=[
    {
        "slug": "agent-primitives-product-differentiation",
        "title": "每個人都在做 Agent，為什麼產品仍然可以不同？",
        "description": "從 Alex Atallah 的 Web 類比，思考交付條件、證據版本與每件完成工作的成本。",
        "source": "articles/agent-primitives-product-differentiation.md",
        "source_manifest": "references/transcripts/openrouter-agent-primitives.json",
        "context": "articles/agent-primitives-product-differentiation.context.json"
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

def inline(text:str)->str:
    text=html.escape(text,quote=False)
    text=re.sub(r'`([^`]+)`',r'<code>\1</code>',text)
    text=re.sub(r'\*\*([^*]+)\*\*',r'<strong>\1</strong>',text)
    text=re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)',r'<a href="\2" target="_blank" rel="noreferrer">\1</a>',text)
    return text

def markdown(text:str)->str:
    out=[]; paragraph=[]; in_code=False; code=[]; list_kind=None
    def flush_p():
        nonlocal paragraph
        if paragraph:
            out.append('<p>'+inline(' '.join(x.strip() for x in paragraph))+'</p>');paragraph=[]
    def close_list():
        nonlocal list_kind
        if list_kind: out.append(f'</{list_kind}>');list_kind=None
    for raw in text.splitlines():
        line=raw.rstrip()
        if line.startswith('```'):
            flush_p();close_list()
            if in_code:
                out.append('<pre><code>'+html.escape('\n'.join(code))+'</code></pre>');code=[];in_code=False
            else: in_code=True
            continue
        if in_code: code.append(line);continue
        if not line.strip(): flush_p();close_list();continue
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
    if in_code: out.append('<pre><code>'+html.escape('\n'.join(code))+'</code></pre>')
    return '\n'.join(out)

def page(title:str, body:str, active:str='')->str:
    nav=[('home','/','首頁'),('learning','/learning/','Learning'),('alg','/cefr-alg-c2/','CEFR ALG C2+'),('experiments','/experiments/','Experiments'),('evals','/ai-evals/','AI Evals'),('article','/articles/','Articles'),('transcripts','/transcripts/','逐字稿來源')]
    links=''.join(f'<a class="{"active" if key==active else ""}" href="{href}">{label}</a>' for key,href,label in nav)
    return f'''<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title><meta name="description" content="Evidence-driven AI Engineer learning, experiments and articles."><link rel="stylesheet" href="/assets/styles.css"></head><body><header><a class="brand" href="/">AI Engineer Lab</a><nav>{links}</nav></header><main>{body}</main><footer>Curriculum guides learning · Ops owns experiments · medium-compiler explains and publishes.</footer></body></html>'''

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
    # Source metadata is controlled by the repository, but URL attributes are escaped.
    video=html.escape(meta['video_url']+'&t=845',quote=True)
    provider=html.escape(meta['source_url'],quote=True)
    fetched=html.escape(meta.get('retrieved_at') or 'HTML 匯入，未宣稱 HTTP 取得時間')
    panel=f'''<section class="panel" aria-label="文章來源"><h2>閱讀來源</h2>
<p><a href="{video}" target="_blank" rel="noreferrer">回看原影片 · 14:05</a> · <a href="{provider}" target="_blank" rel="noreferrer">第三方逐字稿 · PodScripts</a></p>
<p>本篇取材範圍：14:05–15:40 的基本元件類比。商品頁案例與工程設計是作者延伸分析。文字依第三方轉錄核對，尚未逐句核對音訊。</p>
<p>來源取得時間：{fetched}。快照包含 {meta['segment_count']} 個區段，最後時間戳 {html.escape(meta['last_timestamp'])}；這不證明整集完整。</p>
<p><a href="article.md" download>下載 Medium 文章（Markdown）</a> · <a href="source.json">來源紀錄</a> · <a href="/transcripts/">取得逐字稿的方法</a></p></section>'''
    (article_dir/'source.json').write_bytes(manifest_bytes)
    (article_dir/'article.md').write_bytes(source_bytes)
    return panel, {'source_manifest':item['source_manifest'],'source_manifest_sha256':manifest_hash,
                   'source_route':'/articles/'+item['slug']+'/source.json','audio_verified':False}


def build(out:Path)->dict:
    out=out.resolve()
    if out.exists(): shutil.rmtree(out)
    out.mkdir(parents=True)
    (out/'assets').mkdir()
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
    eval_home='<section class="panel"><div class="eyebrow">Engineering judgment</div><h2>AI Evals · Soodles</h2><p>閱讀六份歷史 Agent reports 的工程評估，區分可支持的判斷與缺少的證據。</p><a href="/ai-evals/">查看 AI Evals 報告 →</a></section>'
    (out/'index.html').write_text(page('AI Engineer Lab',hero+stats+eval_home+alg+flow+exp+art,'home'),encoding='utf-8')
    (out/'experiments').mkdir();(out/'experiments/index.html').write_text(page('Experiments · AI Engineer Lab',f'''<section class="page-head"><div class="eyebrow">Ops Reconciliation Copilot</div><h1>Experiment Templates</h1><p>這些卡片來自 Ops provider snapshot <code>{snapshot['provider_revision'][:12]}</code>。範本只定義實驗邊界，不代表實驗已執行，也不授權 production promotion。</p></section>{cards(snapshot)}''','experiments'),encoding='utf-8')
    learn_body=f'''<section class="page-head"><div class="eyebrow">AI Engineering from Scratch</div><h1>Learning Progress</h1><p>目前狀態：<strong>{state['status']}</strong></p></section><section class="panel"><h2>Source of truth</h2><p><code>LEARNING.md</code> 由 upstream <code>start-learning</code> / <code>learn</code> skills 管理。medium-compiler 不自行猜 placement，也不把文章進度當課程進度。</p><pre><code>Use start-learning to begin the course.
Use learn to continue one lesson.</code></pre><dl><dt>Entry point</dt><dd>{state['entry_point'] or '尚未執行 placement'}</dd><dt>Pace</dt><dd>{state['pace'] or '尚未設定'}</dd><dt>Logged lessons</dt><dd>{state['progress_rows']}</dd><dt>Review items</dt><dd>{state['review_items']}</dd></dl></section>'''
    learn_body+='<section class="panel"><h2>從第一篇學習文章開始</h2><p>逐章理解開發環境，實作四語言與 Python 運算，再核對本機與 Colab 的替代範圍；閱讀或執行範例不會自動變更課程進度。</p><a href="/articles/application-engineering-colab/">開啟開發環境設定學習文章 →</a></section>'
    (out/'learning').mkdir();(out/'learning/index.html').write_text(page('Learning · AI Engineer Lab',learn_body,'learning'),encoding='utf-8')
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
        article_body='<article class="article"><div class="article-source">Built from <code>'+html.escape(item['source'])+'</code></div>'+markdown(source_bytes.decode('utf-8'))+lesson_navigation(item,course_route)+'</article>'
        article_dir=article_root/item['slug'];article_dir.mkdir()
        source_record={}
        if item.get('source_manifest'):
            panel,source_record=transcript_source(item,source_bytes,article_dir)
            article_body+=panel
        (article_dir/'index.html').write_text(page(item['title'],article_body,'article'),encoding='utf-8')
        article_provenance.append({'source':item['source'],'route':'/articles/'+item['slug']+'/','sha256':hashlib.sha256(source_bytes).hexdigest(),**source_record})
        if item.get('notebook'):
            destination=out/item['notebook'];destination.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(ROOT/item['notebook'],destination)
    provenance={'schema_version':'ai-engineer-site-build@1','article':'articles/ai-engineer-learning-path.md','ops_provider_revision':snapshot['provider_revision'],'curriculum_revision':json.loads((ROOT/'references/upstream/ai-engineering-skills-lock.json').read_text())['revision'],'learning':state,'articles':article_provenance}
    provenance['ai_evals']=eval_provenance
    provenance['cefr_alg']={'repository':alg_provenance['repository'],'revision':alg_provenance['revision'],'route':alg_provenance['route'],'manifest':'/cefr-alg-c2/provenance.json'}
    (out/'provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return provenance

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=ROOT/'dist');a=p.parse_args()
    print(json.dumps(build(a.out),ensure_ascii=False,indent=2))

if __name__=='__main__':main()
