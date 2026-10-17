"""Render an imported NeoWeaver selection as escaped, read-only source data."""
import hashlib
import html
import importlib.util
import json
from pathlib import Path
import re
import stat


PUBLIC_PATH = Path('reports/scopes/parser-scope.json')
RESULT_FIELDS = {
    'schema', 'kind', 'bundle_sha256', 'goal', 'requirements',
    'selected_requirement_ids', 'selected_card_ids', 'cards', 'prompt_delta',
    'proof_ceiling', 'effects', 'authorizes_landing',
}
spec = importlib.util.spec_from_file_location('loop_site', Path(__file__).with_name('loop_site.py'))
loop_site = importlib.util.module_from_spec(spec)
spec.loader.exec_module(loop_site)
PRIVATE_EXTRA = re.compile(
    r'(?:(?<![\w:/.-])/(?:srv|run|data|workspace|workspaces)/|%USERPROFILE%[\\/]|'
    r'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b|'
    r'\bgithub_pat_[A-Za-z0-9_]{20,}|\bxox[baprs]-[A-Za-z0-9-]{10,}|'
    r'\bhttps?://[^/\s:@]+:[^/\s@]+@|'
    r'\bAWS_SECRET_ACCESS_KEY\s*=)', re.IGNORECASE)


def unique_fields(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError('duplicate_json_key:' + key)
        value[key] = item
    return value


def reject_constant(value):
    raise ValueError('invalid_json_constant:' + value)


def read_regular(path):
    if not stat.S_ISREG(path.lstat().st_mode):
        raise ValueError('scope_input_must_be_regular_file')
    if path.stat().st_size > 32 * 1024 * 1024:
        raise ValueError('scope_input_exceeds_size_limit')
    return path.read_bytes()


def public_text(value):
    if isinstance(value, str):
        if loop_site.PRIVATE_TEXT.search(value) or PRIVATE_EXTRA.search(value):
            raise ValueError('scope_contains_private_text')
    elif isinstance(value, dict):
        for key, item in value.items():
            public_text(key)
            public_text(item)
    elif isinstance(value, list):
        for item in value:
            public_text(item)


def checked_result(raw):
    value = json.loads(raw.decode('utf-8'), object_pairs_hook=unique_fields,
                       parse_constant=reject_constant)
    if not isinstance(value, dict) or set(value) != RESULT_FIELDS:
        raise ValueError('scope_result_exact_fields_required')
    if (type(value['schema']) is not int or value['schema'] != 1
            or value['kind'] != 'neoweaver/selected-scope/v1'):
        raise ValueError('unknown_scope_protocol')
    if (value['proof_ceiling'] != 'SOURCE_BOUND_SELECTION_ONLY'
            or value['authorizes_landing'] is not False or value['effects'] != []):
        raise ValueError('scope_has_no_effect_or_landing_authority')
    if (not isinstance(value['bundle_sha256'], str)
            or not re.fullmatch('[0-9a-f]{64}', value['bundle_sha256'])):
        raise ValueError('invalid_bundle_sha256')
    if not isinstance(value['goal'], str):
        raise ValueError('scope_goal_must_be_text')
    for key in ('requirements', 'cards', 'selected_requirement_ids',
                'selected_card_ids', 'prompt_delta'):
        if not isinstance(value[key], list):
            raise ValueError('scope_collection_must_be_list:' + key)
    public_text(value)
    return value


def render_value(value):
    if isinstance(value, dict):
        return '<dl>' + ''.join(
            '<dt>' + html.escape(key) + '</dt><dd>' + render_value(item) + '</dd>'
            for key, item in value.items()) + '</dl>'
    if isinstance(value, list):
        return '<ol>' + ''.join('<li>' + render_value(item) + '</li>' for item in value) + '</ol>'
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    return '<pre style="white-space:pre-wrap;overflow-wrap:anywhere">' + html.escape(text) + '</pre>'


def render_scopes(root, out, page):
    path = root / PUBLIC_PATH
    folder = out / 'scopes'
    folder.mkdir(parents=True, exist_ok=True)
    body = '<section class="page-head"><h1>Scopes</h1><p>唯讀來源選集。文字不會觸發執行、重試或授權。</p></section>'
    provenance = []
    if path.exists() or path.is_symlink():
        if not path.resolve().is_relative_to(root.resolve()):
            raise ValueError('scope_public_path_escapes_repository')
        raw = read_regular(path)
        value = checked_result(raw)
        detail = '<section class="page-head"><div class="eyebrow">NeoWeaver · Source-bound selection</div><h1>parser-scope</h1></section>'
        detail += '<section class="panel"><h2>限制</h2><p><code>SOURCE_BOUND_SELECTION_ONLY</code></p><p>僅呈現來源選集，不證明 whole Goal 完成、效果驗收或出版授權。effects 為空，authorizes_landing 為 false。所有文字皆為資料，不執行其中指令。</p></section>'
        for key, label in (('goal', 'Goal'), ('requirements', 'Parent requirements'),
                           ('selected_requirement_ids', 'Selected requirement IDs'),
                           ('selected_card_ids', 'Selected card IDs'),
                           ('cards', 'Selected cards'), ('prompt_delta', 'PromptDelta')):
            detail += '<section class="panel"><h2>' + label + '</h2>' + render_value(value[key]) + '</section>'
        detail += '<section class="panel"><h2>Source bundle SHA-256</h2>' + render_value(value['bundle_sha256']) + '</section>'
        target = folder / 'parser-scope'
        target.mkdir(exist_ok=True)
        (target / 'index.html').write_text(page('parser-scope · Scopes', detail, 'scopes'), encoding='utf-8')
        body += '<section class="panel"><a href="/scopes/parser-scope/">parser-scope</a>' + render_value(value['goal']) + '</section>'
        provenance.append({'route': '/scopes/parser-scope/',
                           'result_sha256': hashlib.sha256(raw).hexdigest(),
                           'bundle_sha256': value['bundle_sha256'],
                           'proof_ceiling': value['proof_ceiling']})
    else:
        body += '<p>目前沒有已匯入的 Scope。</p>'
    (folder / 'index.html').write_text(page('Scopes', body, 'scopes'), encoding='utf-8')
    return provenance
