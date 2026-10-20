"""Source-preserving ALG Four article + right-hand reading-outline projection.

This module does not compile or rewrite the approved Markdown.  It annotates
only the generated DOM, with source-bound notes inside a separate outline.
"""
from __future__ import annotations

import html
import re


BLOCK = re.compile(r'<h([1-4])>(.*?)</h\1>|<(p|blockquote)>(.*?)</\3>', re.S)
PLAIN = re.compile(r'<[^>]+>')


def plain_text(markup: str) -> str:
    return html.unescape(PLAIN.sub('', markup)).strip()


# Optional, deliberately small and reviewed syllable accents.  Never infer a
# stress boundary for a word that has no reviewed entry.
STRESS = {
    "anagrams": ("an", "agrams"),
    "vectors": ("vec", "tors"),
    "vector": ("vec", "tor"),
    "characters": ("char", "acters"),
    "character": ("char", "acter"),
    "counting": ("count", "ing"),
    "sorting": ("sort", "ing"),
    "hashing": ("hash", "ing"),
    "dictionary": ("dic", "tionary"),
    "contract": ("con", "tract"),
}

# Source-attested expressions; brackets are a *reading aid*, not the source.
BUNDLES = {
    "D1": ("character-frequency vectors", "previously processed words", "canonical vector"),
    "D2": ("input contract", "lowercase English letters", "26-counter vector", "all-zero vector"),
    "D3": ("Unicode code point", "lowercase ASCII letters", "indices 0 through 25"),
    "D4": ("canonical key", "logical group identity", "candidate entries", "hash collision",
           "missing key", "explicit branch"),
    "D5": ("during scanning", "hashable tuple", "dictionary lookup", "per-word time cost"),
}


def _emphasize(match: re.Match[str]) -> str:
    word = match.group(0)
    matched = STRESS.get(word.lower())
    if not matched:
        return html.escape(word)
    first, second = matched
    if len(first) + len(second) != len(word):
        return html.escape(word)
    return '<strong class="alg-stress">' + html.escape(word[:len(first)]) + '</strong>' + html.escape(word[len(first):])


def scan_reading(english: str, decision_id: str) -> str:
    """Add only layout marks to source-faithful English; no lexical rewriting.

    The slash and square-bracket policy is conservative: clause boundaries and
    reviewed lexical bundles are marked.  Accent only reviewed content words.
    """
    # Match source spans once; never reparse original punctuation as added marks.
    phrases = BUNDLES.get(decision_id, ())
    bundle = '|'.join(re.escape(phrase) for phrase in sorted(phrases, key=len, reverse=True))
    rules = []
    if bundle:
        rules.append(r'(?P<bundle>(?<!\w)(?i:' + bundle + r')(?!\w))')
    rules.extend((
        r'(?P<major_period>(?<=\.)\s+(?=[A-Z]))',
        r'(?P<major_semicolon>; )',
        r'(?P<major_comma>, (?=but\b))',
        r'(?P<minor>(?<![\w\[/]) (?=(?i:during|before|with|without|through|into|under|after|from|for)\b))',
    ))
    pattern = re.compile('|'.join(rules))

    def render_text(text):
        return re.sub(r'\b[A-Za-z]+\b', _emphasize, html.escape(text))

    result = []
    cursor = 0
    for match in pattern.finditer(english):
        result.append(render_text(english[cursor:match.start()]))
        if match.lastgroup == 'bundle':
            result.extend(('<span class="alg-bundle"><span class="alg-reading-mark">[</span>',
                           render_text(match.group()),
                           '<span class="alg-reading-mark">]</span></span>'))
        else:
            result.append(render_text(match.group()))
            if match.lastgroup == 'minor':
                result.append('<span class="alg-minor-break">/</span>')
            else:
                result.append('<span class="alg-major-break">//</span><br>')
        cursor = match.end()
    result.append(render_text(english[cursor:]))
    return ''.join(result)


def note_html(i: int, note: dict, decisions: dict, index_items: dict) -> str:
    esc = html.escape
    kind = note['kind']
    decision_id = note['decision_ids'][0]
    decision = decisions[decision_id]
    label = "Passive + Active" if kind == "PASSIVE_AND_ACTIVE" else "Passive"
    out = [
        f'<div class="alg-four-annotation" data-alg-four-role="{kind}">',
        f'<p class="alg-four-label">{label} · {esc(", ".join(note["decision_ids"]))}</p>',
        f'<p class="alg-four-zh">{esc(note["zh_note"])}</p>',
        '<p class="alg-reading-label">Passive · 模式 C 語塊閱讀</p>',
        f'<p class="alg-reading-text" lang="en">{scan_reading(note.get("english_source", decision["passive"]), decision_id)}</p>',
        '<p class="alg-source-explain">衍生閱讀示例，並非改寫左側原文；重音只標記已核對的字詞。</p>'
    ]
    skeleton = note.get('passive_skeleton')
    if skeleton:
        # One decision-bound cognitive cue, not a replacement for the source.
        if len(skeleton.split()) > 15 or '→' not in skeleton:
            raise ValueError('ALG Four Mode C skeleton must be concise and source-bound')
        out.append('<p class="alg-skeleton"><strong>極簡認知骨架</strong>：'
                   + esc(skeleton) + '</p>')
    for item in index_items.get(i, []):
        out.append('<div class="alg-active-word">'
                   f'<span class="alg-active-term">{esc(item["term"])}</span>'
                   f'<span lang="en">{esc(item["english_sentence"])}</span></div>')
    if kind == 'PASSIVE_AND_ACTIVE':
        cues = ' '.join(decisions[x]['active_cue'] for x in note['decision_ids'])
        oracles = ' '.join(decisions[x]['oracle'] for x in note['decision_ids'])
        out.append('<details class="alg-four-recall"><summary>Active · 自行表達後核對</summary>'
                   f'<p lang="en">{esc(cues)}</p>'
                   '<details><summary>Oracle · 嘗試後展開</summary>'
                   f'<p lang="en">{esc(oracles)}</p></details></details>')
    out.append('</div>')
    return ''.join(out)


def render_outline(source_html: str, notes: list[dict], decisions: dict, index_items: dict):
    """Return DOM-anchored source HTML and hierarchical right-hand sidecar.

    A human-readable HTML source can be recovered by deleting only ID/data
    attributes added to original opening tags.  Text and code bytes remain.
    """
    tokens = list(BLOCK.finditer(source_html))
    paras = [m for m in tokens if m.group(3)]
    if len(paras) != len(notes):
        raise ValueError('ALG Four must annotate every original prose paragraph without omissions')
    root = {'level': 0, 'title': '開頭段落', 'heading': None, 'children': []}
    stack = [root]
    replacements = []
    p_index = 0
    heading_index = 0
    for token in tokens:
        start, end = token.span()
        if token.group(1):
            level = int(token.group(1))
            heading_id = f'alg-heading-{heading_index}'
            heading_index += 1
            replacements.append((start, end,
                                 f'<h{level} id="{heading_id}" data-alg-heading="{heading_index - 1}">'
                                 + token.group(2) + f'</h{level}>'))
            node = {'level': level, 'title': plain_text(token.group(2)),
                    'heading': heading_id, 'children': []}
            while stack[-1]['level'] >= level:
                stack.pop()
            stack[-1]['children'].append(node)
            stack.append(node)
        else:
            tag = token.group(3)
            text = token.group(4)
            p_id = f'alg-p-{p_index}'
            original = token.group(0)
            replacement = (f'<{tag} id="{p_id}" data-alg-four-index="{p_index}">' +
                           text + f'</{tag}>')
            replacements.append((start, end, replacement))
            title = plain_text(text)
            title = re.sub(r'\s+', ' ', title)
            # A short source-derived navigation label, never a paraphrase.
            title = title[:86].rstrip() + ('…' if len(title) > 86 else '')
            stack[-1]['children'].append({
                'paragraph': p_index,
                'title': title or f'段落 {p_index + 1}',
                'note': notes[p_index]
            })
            p_index += 1

    result = []
    last = 0
    for start, end, replacement in replacements:
        result.append(source_html[last:start])
        result.append(replacement)
        last = end
    result.append(source_html[last:])
    annotated = ''.join(result)

    esc = html.escape
    def create_nav(node) -> str:
        if 'paragraph' in node:
            i = node['paragraph']
            note = node['note']
            return (
                f'<details class="alg-outline-paragraph" data-outline-index="{i}">'
                f'<summary data-outline-link="{i}" data-target-id="alg-p-{i}">'
                f'<span class="alg-paragraph-num">{i+1:02}</span> {esc(node["title"])}</summary>'
                + note_html(i, note, decisions, index_items)
                + '</details>'
            )
        contents = ''.join(create_nav(child) for child in node['children'])
        if node['heading'] is None:
            return contents
        return (
            '<details class="alg-outline-section" data-heading-id="' + node['heading'] + '">'
            '<summary data-target-id="' + node['heading'] + '">' + esc(node['title']) + '</summary>'
            '<div class="alg-outline-children">' + contents + '</div>'
            '</details>'
        )

    nav = (
        '<aside class="alg-four-sidebar" aria-label="ALG Four 文章索引與英語註解">'
        '<details class="alg-sidebar-shell" open>'
        '<summary class="alg-sidebar-toggle">文章索引 · ALG Four <span>Active / Passive</span></summary>'
        '<p class="alg-sidebar-help">點擊標題或段落定位；閱讀時自動展開所在章節。'
        '黃色表示 Active 詞彙；Passive 語塊是衍生閱讀層，不改動正文。</p>'
        '<nav class="alg-outline-nav" aria-label="文章大綱與段落連結">'
        + create_nav(root) + '</nav></details></aside>'
    )
    return annotated, nav, p_index, heading_index
