"""Render catalog-approved public Loop snapshots as inert text."""
import hashlib
import html
import json
from pathlib import Path
import re


PRIVATE_TEXT = re.compile(
    r'(?:/(?:Users|home|tmp|private|var|etc|opt|root|mnt|Volumes)/|(?<![A-Za-z0-9])[A-Za-z]:[\\/]|'
    r'file://|~/|-----BEGIN [A-Z ]*PRIVATE KEY-----|'
    r'\b(?:sk-[A-Za-z0-9_-]{16,}|gh[pousr]_[A-Za-z0-9_]{16,})|'
    r'\b(?:authorization\s*:\s*bearer|(?:api[_-]?key|access[_-]?token|password|secret)\s*[=:]))',
    re.IGNORECASE,
)


def fields(value, required, optional=()):
    if not isinstance(value, dict) or not set(required) <= value.keys() or value.keys() - set(required) - set(optional):
        raise ValueError('Invalid public Loop fields')


def text(value):
    if not isinstance(value, str) or PRIVATE_TEXT.search(value):
        raise ValueError('Public Loop text contains private data or is not text')
    return value


def items(value):
    if not isinstance(value, list):
        raise ValueError('Public Loop collection must be a list')
    return value


def identifier(value):
    if not isinstance(value, str) or not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_-]*', value):
        raise ValueError('Invalid public Loop ID')
    return value


def validate_snapshot(snapshot):
    fields(snapshot, ('schema_version', 'runs'))
    if type(snapshot['schema_version']) is not int or snapshot['schema_version'] != 1:
        raise ValueError('Unsupported public Loop schema')
    seen = set()
    for run in items(snapshot['runs']):
        fields(run, ('id', 'repository', 'mode', 'status', 'stages', 'cards', 'notes', 'breakpoints', 'next'), ('resources',))
        identifier(run['id'])
        if run['id'] in seen:
            raise ValueError('Duplicate public Loop run ID')
        seen.add(run['id'])
        for key in ('repository', 'mode', 'status'):
            text(run[key])
        if run['next'] is not None:
            text(run['next'])
        stage_ids = set()
        for stage in items(run['stages']):
            fields(stage, ('id', 'kind', 'status', 'prompt', 'input_refs', 'output_refs', 'consumer_status'))
            identifier(stage['id'])
            if stage['id'] in stage_ids:
                raise ValueError('Duplicate public Loop stage ID')
            stage_ids.add(stage['id'])
            for key in ('kind', 'status', 'prompt', 'consumer_status'):
                text(stage[key])
            for key in ('input_refs', 'output_refs'):
                for ref in items(stage[key]):
                    text(ref)
        for collection in ('cards', 'notes'):
            entry_ids = set()
            for entry in items(run[collection]):
                required = ('id', 'title', 'body', 'source_refs') + (('type',) if collection == 'cards' else ())
                fields(entry, required)
                identifier(entry['id'])
                if entry['id'] in entry_ids:
                    raise ValueError('Duplicate public Loop entry ID')
                entry_ids.add(entry['id'])
                for key in ('title', 'body') + (('type',) if collection == 'cards' else ()):
                    text(entry[key])
                for ref in items(entry['source_refs']):
                    text(ref)
        for point in items(run['breakpoints']):
            fields(point, ('kind', 'status', 'stage_id', 'message'))
            for key in ('kind', 'status', 'message'):
                text(point[key])
            if point['stage_id'] is not None and point['stage_id'] not in stage_ids:
                raise ValueError('Unknown public Loop breakpoint stage')
        for resource in items(run.get('resources', [])):
            fields(resource, ('label', 'value'))
            text(resource['label'])
            text(resource['value'])
    return snapshot


def checked_snapshot(root, entry):
    fields(entry, ('path', 'sha256'))
    name = entry['path']
    if not isinstance(name, str) or Path(name).is_absolute() or '..' in Path(name).parts:
        raise ValueError('Invalid public Loop snapshot path')
    path = (root / name).resolve()
    if (not path.is_relative_to(root.resolve())
            or not path.is_relative_to((root / 'reports/loops').resolve())):
        raise ValueError('Public Loop snapshot escapes its catalog directory')
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != entry['sha256']:
        raise ValueError('Public Loop snapshot hash mismatch')
    return validate_snapshot(json.loads(raw))


def refs(values):
    return '<ul>' + ''.join('<li><code>' + html.escape(value) + '</code></li>' for value in values) + '</ul>'


def render_run(run):
    esc = html.escape
    body = f'<section class="page-head"><div class="eyebrow">Loop · {esc(run["mode"])}</div><h1>{esc(run["id"])}</h1><p>{esc(run["repository"])} · {esc(run["status"])}</p></section>'
    body += '<section class="panel"><h2>Prompt 階段</h2>'
    for stage in run['stages']:
        body += f'<article id="stage-{stage["id"]}"><h3>{esc(stage["id"])} · {esc(stage["kind"])}</h3><p>狀態：{esc(stage["status"])} · Consumer：{esc(stage["consumer_status"])}</p><pre style="white-space:pre-wrap;overflow-wrap:anywhere">{esc(stage["prompt"])}</pre><h4>輸入來源</h4>{refs(stage["input_refs"])}<h4>輸出來源</h4>{refs(stage["output_refs"])}</article>'
    body += '</section>'
    for collection, label in (('cards', '規格卡片'), ('notes', '卡盒筆記')):
        body += '<section class="panel"><h2>' + label + '</h2>'
        for entry in run[collection]:
            body += '<article><h3>' + esc(entry['title']) + '</h3><p><code>' + esc(entry['id']) + '</code> ' + esc(entry.get('type', '')) + '</p><pre style="white-space:pre-wrap;overflow-wrap:anywhere">' + esc(entry['body']) + '</pre>' + refs(entry['source_refs']) + '</article>'
        body += '</section>'
    body += '<section class="panel"><h2>停止與待確認事項</h2>'
    for point in run['breakpoints']:
        body += '<p>' + esc(point['kind']) + ' · ' + esc(point['status']) + ' · ' + esc(point['stage_id'] or '') + '</p><p>' + esc(point['message']) + '</p>'
    body += '<h3>下一步說明</h3><p>' + esc(run['next'] if run['next'] is not None else '未提供下一步') + '</p></section>'
    if run.get('resources'):
        body += '<section class="panel"><h2>資源觀察</h2><dl>' + ''.join('<dt>' + esc(r['label']) + '</dt><dd>' + esc(r['value']) + '</dd>' for r in run['resources']) + '</dl></section>'
    return body + '<p><a href="/loops/">返回 Loops</a></p>'


def render_loops(root, out, page):
    catalog = json.loads((root / 'reports/loops/catalog.json').read_bytes())
    fields(catalog, ('schema_version', 'snapshots'))
    if type(catalog['schema_version']) is not int or catalog['schema_version'] != 1:
        raise ValueError('Unsupported public Loop catalog')
    runs, provenance, seen = [], [], set()
    for entry in items(catalog['snapshots']):
        snapshot = checked_snapshot(root, entry)
        for run in snapshot['runs']:
            if run['id'] in seen:
                raise ValueError('Duplicate public Loop run across snapshots')
            seen.add(run['id'])
            runs.append(run)
            provenance.append({'route': '/loops/' + run['id'] + '/', 'snapshot_sha256': entry['sha256'], 'repository': run['repository'], 'mode': run['mode'], 'status': run['status']})
    target = out / 'loops'
    target.mkdir()
    links = []
    for run in runs:
        destination = target / run['id']
        destination.mkdir()
        (destination / 'index.html').write_text(page(run['id'] + ' · Loops', render_run(run), 'loops'), encoding='utf-8')
        links.append('<article class="card"><h2>' + html.escape(run['id']) + '</h2><p>' + html.escape(run['repository']) + ' · ' + html.escape(run['mode']) + ' · ' + html.escape(run['status']) + '</p><a href="/loops/' + run['id'] + '/">查看階段與卡片 →</a></article>')
    intro = '<section class="page-head"><h1>Loops</h1><p>閱讀已公開的 Prompt 階段、規格卡片與筆記。狀態保留來源的觀察結果；本頁不執行工作。</p></section>'
    empty = '<p>目前沒有已公開的 Loop 紀錄。</p>' if not runs else ''
    (target / 'index.html').write_text(page('Loops · AI Engineer Lab', intro + empty + '<div class="cards">' + ''.join(links) + '</div>', 'loops'), encoding='utf-8')
    return provenance
