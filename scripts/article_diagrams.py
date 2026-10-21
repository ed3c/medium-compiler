"""Versioned Mermaid -> reviewed build-time SVG registry; presentation only."""
from __future__ import annotations
import hashlib
import html
import json
import re
from pathlib import Path
from xml.etree import ElementTree as ET

HEX = re.compile(r'^[a-f0-9]{64}$')
SVG_NS = '{http://www.w3.org/2000/svg}'
FORBIDDEN = {'script', 'foreignObject', 'image', 'iframe', 'object', 'embed', 'animate'}
MAX_SVG = 2 * 1024 * 1024

def check_svg(svg: bytes) -> None:
    if len(svg) > MAX_SVG or b'<!DOCTYPE' in svg.upper() or b'<!ENTITY' in svg.upper():
        raise ValueError('UNSAFE_SVG')
    try:
        root = ET.fromstring(svg)
    except ET.ParseError as e:
        raise ValueError('INVALID_SVG') from e
    if root.tag != SVG_NS + 'svg':
        raise ValueError('INVALID_SVG_ROOT')
    for element in root.iter():
        tag = element.tag.rsplit('}', 1)[-1]
        if tag in FORBIDDEN:
            raise ValueError('UNSAFE_SVG_ELEMENT')
        for key, value in element.attrib.items():
            name = key.rsplit('}', 1)[-1].lower()
            if name.startswith('on') or name in ('href', 'src'):
                raise ValueError('UNSAFE_SVG_ATTRIBUTE')
            if re.search(r'url\s*\(\s*["\\']?\s*(https?:|data:|javascript:)', value, re.I):
                raise ValueError('UNSAFE_SVG_URL')
        if tag == 'style' and re.search(r'@import|url\s*\(\s*["\\']?\s*(https?:|data:)', element.text or '', re.I):
            raise ValueError('UNSAFE_SVG_STYLE')

class DiagramProjection:
    def __init__(self, root: Path, source: str, entries: list[dict]):
        self.root, self.source, self.entries = root, source, entries
        self.used = set()

    def figure(self, code: str, ordinal: int) -> str:
        matches = [e for e in self.entries if e['ordinal'] == ordinal]
        if len(matches) != 1:
            raise ValueError('UNREGISTERED_MERMAID_BLOCK')
        item = matches[0]
        if hashlib.sha256(code.encode('utf-8')).hexdigest() != item['mermaid_sha256']:
            raise ValueError('MERMAID_SOURCE_DRIFT')
        svg_file = self.root / 'site/article-diagrams' / (item['svg_sha256'] + '.svg')
        if not svg_file.is_file():
            raise ValueError('MISSING_REVIEWED_SVG')
        svg = svg_file.read_bytes()
        if hashlib.sha256(svg).hexdigest() != item['svg_sha256']:
            raise ValueError('SVG_DIGEST_DRIFT')
        check_svg(svg)
        self.used.add(ordinal)
        label = html.escape(item['alt'], quote=True)
        url = '/assets/article-diagrams/' + item['svg_sha256'] + '.svg'
        return '<figure class="article-figure article-diagram"><img loading="lazy" src="' + url + '" alt="' + label + '"><figcaption>' + html.escape(item['alt']) + '</figcaption></figure>'

    def check_complete(self) -> None:
        if self.used != {e['ordinal'] for e in self.entries}:
            raise ValueError('REGISTERED_MERMAID_NOT_PRESENT')

class DiagramRegistry:
    def __init__(self, root: Path):
        self.root = Path(root)
        manifest = json.loads((self.root / 'references/article-diagrams.json').read_text(encoding='utf-8'))
        if manifest.get('schema_version') != 'article-diagram-registry@1' or not isinstance(manifest.get('items'), list):
            raise ValueError('ARTICLE_DIAGRAM_REGISTRY_INVALID')
        self.items = manifest['items']
        identity = set()
        for item in self.items:
            source = item.get('source')
            ordinal = item.get('ordinal')
            if not isinstance(source, str) or not source.startswith('articles/') or '..' in source.split('/') or not source.endswith('.md'):
                raise ValueError('ARTICLE_DIAGRAM_SOURCE_INVALID')
            if not isinstance(ordinal, int) or ordinal < 0 or (source, ordinal) in identity:
                raise ValueError('ARTICLE_DIAGRAM_IDENTITY_INVALID')
            identity.add((source, ordinal))
            if not all(isinstance(item.get(k), str) and HEX.fullmatch(item[k])
                       for k in ('mermaid_sha256', 'svg_sha256')):
                raise ValueError('ARTICLE_DIAGRAM_DIGEST_INVALID')
            if not isinstance(item.get('alt'), str) or not item['alt'].strip():
                raise ValueError('ARTICLE_DIAGRAM_ALT_MISSING')

    def for_article(self, source: str):
        rows = [r for r in self.items if r['source'] == source]
        return DiagramProjection(self.root, source, rows) if rows else None

    def install_assets(self, out: Path):
        directory = out / 'assets/article-diagrams'
        directory.mkdir(parents=True, exist_ok=True)
        for item in self.items:
            name = item['svg_sha256'] + '.svg'
            source = self.root / 'site/article-diagrams' / name
            if not source.is_file():
                raise ValueError('MISSING_REVIEWED_SVG')
            raw = source.read_bytes()
            if hashlib.sha256(raw).hexdigest() != item['svg_sha256']:
                raise ValueError('SVG_DIGEST_DRIFT')
            check_svg(raw)
            (directory / name).write_bytes(raw)
