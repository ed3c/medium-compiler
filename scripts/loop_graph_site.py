"""Publish reviewed graph data as a static, content-addressed display package."""
import copy
import hashlib
import html
import json
from pathlib import Path
import shutil


MAX_ARTIFACT_BYTES = 2 * 1024 * 1024
MAX_SNAPSHOT_BYTES = 32 * 1024 * 1024
ROOT = Path(__file__).resolve().parents[1]


def validate_public_graph(snapshot, check_text):
    # Load the unchanged validator from the canonical display owner.
    import importlib.util
    path = ROOT / 'scripts/loop_graph_contract.py'
    spec = importlib.util.spec_from_file_location('public_loop_graph_contract', path)
    owner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(owner)
    owner.validate(snapshot)

    def private_check(value):
        if isinstance(value, str):
            check_text(value)
        elif isinstance(value, list):
            for item in value:
                private_check(item)
        elif isinstance(value, dict):
            for key, item in value.items():
                check_text(key)
                private_check(item)
    private_check(snapshot['graph'])
    for artifact in snapshot['graph']['artifacts']:
        if 'content' in artifact or 'content_encoding' in artifact:
            raise ValueError('Public graph requires reviewed public_content, never original content')
        content = artifact.get('public_content')
        if content is None:
            if 'public_sha256' in artifact or 'public_bytes' in artifact:
                raise ValueError('Public artifact digest without reviewed content')
            continue
        raw = content.encode('utf-8')
        if len(raw) > MAX_ARTIFACT_BYTES:
            raise ValueError('Public artifact exceeds size limit')
        if artifact.get('public_sha256') != hashlib.sha256(raw).hexdigest() or artifact.get('public_bytes') != len(raw):
            raise ValueError('Public artifact bytes or digest mismatch')
        if artifact['status'] == 'not_public':
            raise ValueError('Nonpublic artifact cannot include public content')
        if artifact['role'] in ('raw_trace', 'raw_event_log', 'credentials'):
            raise ValueError('Raw traces and credentials are not public artifacts')
    return snapshot


def build_graph_package(snapshot, digest, target):
    destination = target.parent / 'assets' / 'loop-data' / digest
    destination.mkdir(parents=True, exist_ok=True)
    artifacts = destination / 'artifacts'
    artifacts.mkdir(exist_ok=True)
    graph = copy.deepcopy(snapshot['graph'])
    content_urls = {}
    for artifact in graph['artifacts']:
        content = artifact.pop('public_content', None)
        if content is not None:
            filename = artifact['public_sha256'] + '.txt'
            (artifacts / filename).write_bytes(content.encode('utf-8'))
            content_urls[artifact['id']] = '/assets/loop-data/' + digest + '/artifacts/' + filename
    runs = []
    collection_refs = {}
    for run in snapshot['runs']:
        collection = {key: run[key] for key in ('cards', 'notes')}
        raw = json.dumps(collection, ensure_ascii=False).encode('utf-8')
        collection_digest = hashlib.sha256(raw).hexdigest()
        filename = 'collection-' + collection_digest + '.json'
        (destination / filename).write_bytes(raw)
        collection_refs[run['id']] = {'url': '/assets/loop-data/' + digest + '/' + filename,
                                      'sha256': collection_digest, 'bytes': len(raw)}
        runs.append({key: run[key] for key in ('id', 'repository', 'mode', 'status', 'next')})
    payload = {'schema_version': 2, 'snapshot_sha256': digest, 'runs': runs, 'graph': graph,
               'content_urls': content_urls, 'collection_refs': collection_refs}
    (destination / 'graph.json').write_text(json.dumps(payload, ensure_ascii=False), encoding='utf-8')
    assets = target.parent / 'assets'
    assets.mkdir(exist_ok=True)
    for name in ('loop-graph.mjs', 'loop-graph-layout.mjs', 'loop-graph.css', 'loop-panorama.mjs', 'loop-panorama.css', 'loop-isometric.mjs', 'loop-repository.mjs', 'loop-anatomy.mjs', 'loop-comparison.mjs'):
        shutil.copyfile(ROOT / 'site' / name, assets / name)
    shutil.copytree(ROOT / 'site' / 'anatomy', assets / 'anatomy', dirs_exist_ok=True)
    return '/assets/loop-data/' + digest + '/graph.json'


def render_graph_run(run, url):
    esc = html.escape
    return f'''<link rel="stylesheet" href="/assets/loop-graph.css"><link rel="stylesheet" href="/assets/loop-panorama.css">
<section class="page-head loop-head"><div class="eyebrow">Loop · 公開證據快照</div>
<h1>跨 repo 資料流工作台</h1><p>{esc(run['repository'])} · {esc(run['status'])}</p>
<p class="loop-note">預設顯示全部 runs；可選單一範圍。只顯示已公開的來源與原 Owner 觀察。圖上接口與下一步是資料，不會執行命令。</p></section>
<div id="loop-graph-app" data-manifest="{esc(url, quote=True)}" data-run="{esc(run['id'], quote=True)}">
<p role="status">載入公開資料圖…</p></div>
<noscript><p>互動資料圖需要 JavaScript。既有 v1 紀錄仍可閱讀；本頁未推論新交接。</p></noscript>
<script type="module" src="/assets/loop-graph.mjs"></script><p><a href="/loops/">返回所有 Loops</a></p>'''
