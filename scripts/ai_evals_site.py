"""Render source-owned evaluation reports without inferring quality scores."""
import hashlib
import html
import json
from pathlib import Path
import re


def checked_file(root, ref):
    path = (root / ref['path']).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError('Report file escapes repository')
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != ref['sha256']:
        raise ValueError('Report source hash mismatch: ' + ref['path'])
    return raw


def report_markdown(text, markdown):
    """Render pipe tables from the evaluation separately from article Markdown."""
    lines = text.splitlines()
    chunks, prose = [], []
    index = 0
    while index < len(lines):
        if (lines[index].startswith('|') and index + 1 < len(lines)
                and re.fullmatch(r'[| :\-]+', lines[index + 1])):
            chunks.append(markdown('\n'.join(prose)))
            prose = []
            cells = lambda line: [re.sub(r'`([^`]+)`', r'<code>\1</code>', html.escape(cell.strip())) for cell in line.strip('|').split('|')]
            header = ''.join('<th scope="col">'+cell+'</th>' for cell in cells(lines[index]))
            index += 2
            rows = []
            while index < len(lines) and lines[index].startswith('|'):
                rows.append('<tr>'+''.join('<td>'+cell+'</td>' for cell in cells(lines[index]))+'</tr>')
                index += 1
            chunks.append('<div style="overflow-x:auto"><table style="border-collapse:collapse;width:100%;text-align:left"><thead><tr>'+header+'</tr></thead><tbody>'+''.join(rows)+'</tbody></table></div>')
        else:
            prose.append(lines[index])
            index += 1
    chunks.append(markdown('\n'.join(prose)))
    return '\n'.join(chunks)


def render_reports(root, out, page, markdown):
    catalog_path = root / 'reports/ai-evals/catalog.json'
    catalog = json.loads(catalog_path.read_bytes())
    target = out / 'ai-evals'
    target.mkdir()
    cards, provenance = [], []
    seen = set()
    for entry in catalog['reports']:
        report_raw = checked_file(root, entry)
        report = json.loads(report_raw)
        language = report.get('language', 'en')
        localized = language == 'zh-Hant'
        labels = {
            'coverage': '證據涵蓋範圍（Evidence coverage）' if localized else 'Evidence coverage',
            'coverage_note': '以下標示哪些面向有證據可評估；它們不是品質分數。' if localized else 'These labels describe what can be assessed. They are not quality scores.',
            'dimension': '評估面向' if localized else 'Dimension',
            'scope': '涵蓋程度' if localized else 'Coverage',
            'boundary': '證據限制' if localized else 'Evidence boundary',
            'subject': '評估對象' if localized else 'Subject',
            'reviewer': '評估者' if localized else 'Reviewer',
            'calibration': '人類校準（Human calibration）' if localized else 'Human calibration',
            'files': '證據與參考附件' if localized else 'Evidence files',
            'report': '結構化報告（Report JSON）' if localized else 'Report JSON',
            'manifest': '來源清單（Source manifest）' if localized else 'Source manifest',
            'assessment': '繁體中文評估正文' if localized else 'English assessment',
            'sources': '查看固定版本來源與 SHA-256' if localized else 'Open pinned sources and SHA-256 identities',
        }
        slug = report['id']
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug) or slug in seen:
            raise ValueError('Invalid or duplicate evaluation report ID')
        seen.add(slug)
        assessment = checked_file(root, report['assessment']).decode('utf-8')
        guide = checked_file(root, report['guide']).decode('utf-8')
        audit_raw = checked_file(root, report['audit'])
        audit = json.loads(audit_raw)
        if (audit['repository'], audit['revision']) != (report['repository'], report['revision']):
            raise ValueError('Report and archive subject differ')
        dest = target / slug
        dest.mkdir()
        (dest / 'report.json').write_bytes(report_raw)
        (dest / 'archive-audit.json').write_bytes(audit_raw)
        (dest / 'assessment.md').write_text(assessment)
        for attachment in report.get('supplementary_evidence', []):
            (dest / Path(attachment['path']).name).write_bytes(checked_file(root, attachment))
        title = html.escape(report['title'])
        route = '/ai-evals/' + slug + '/'
        cards.append(f'<article class="card"><div class="eyebrow">{html.escape(report["mode"])}</div><h2>{title}</h2><p>{html.escape(report["summary_zh"])}</p><a href="{route}">閱讀評估報告 →</a></article>')
        rows = ''.join('<tr><th scope="row">'+html.escape(d['name'])+'</th><td>'+html.escape(d['status'])+'</td><td>'+html.escape(d['reason'])+'</td></tr>' for d in report['dimensions'])
        attachments = ''.join('<li><a href="'+route+html.escape(Path(a['path']).name, quote=True)+'">'+html.escape(a.get('label', Path(a['path']).name))+'</a></li>' for a in report.get('supplementary_evidence', []))
        sources = ''.join('<li><a href="'+html.escape(s['url'], quote=True)+'">'+html.escape(s['path'])+'</a><br><code>'+s['sha256']+'</code></li>' for s in audit['sources'])
        review_scope = ('<p>Review mode: <code>'+html.escape(report['review_mode'])+'</code> · Capture: '+html.escape(report['capture_scope'])+'</p>') if report.get('review_mode') else ''
        coverage = f'<section class="panel"><h2>{labels["coverage"]}</h2><p>{labels["coverage_note"]}</p><div style="overflow-x:auto"><table style="border-collapse:collapse;width:100%;text-align:left"><thead><tr><th>{labels["dimension"]}</th><th>{labels["scope"]}</th><th>{labels["boundary"]}</th></tr></thead><tbody>{rows}</tbody></table></div></section>'
        decisions_first = report.get('review_mode') in {'agent_workflow_evaluation', 'combined'}
        body = f'''<section class="page-head"><div class="eyebrow">AI Engineering Evals · {html.escape(report['mode'])}</div><h1>{title}</h1><p>{html.escape(report['summary_zh'])}</p><p>{labels['subject']}: <code>{html.escape(report['repository'])}@{report['revision']}</code></p><p>{labels['reviewer']}: {html.escape(report['reviewer'])} · {labels['calibration']}: {html.escape(report['human_calibration'])}</p></section>
{review_scope}<section class="panel">{markdown(guide)}</section>
{'' if decisions_first else coverage}
<article class="article" lang="{html.escape(language, quote=True)}">{report_markdown(assessment, markdown)}</article>
{coverage if decisions_first else ''}
<section class="panel"><h2>{labels['files']}</h2><p><a href="{route}report.json">{labels['report']}</a> · <a href="{route}archive-audit.json">{labels['manifest']}</a> · <a href="{route}assessment.md">{labels['assessment']}</a></p><ul>{attachments}</ul><details><summary>{labels['sources']}</summary><ul>{sources}</ul></details><p><a href="/ai-evals/">返回 AI Evals</a></p></section>'''
        (dest / 'index.html').write_text(page(report['title'], body, 'evals'))
        provenance.append({'route': route, 'report_sha256': entry['sha256'],
                           'repository': report['repository'], 'revision': report['revision'],
                           'assessment_sha256': report['assessment']['sha256'],
                           'audit_sha256': report['audit']['sha256'], 'mode': report['mode']})
    intro = '<section class="page-head"><div class="eyebrow">Engineering judgment · Evidence first</div><h1>AI Evals</h1><p>從真實工程流程檢查 Agent 的判斷、除錯與交付說明。歷史證據、新觀察與尚未驗證的能力分開呈現。</p><p>報告由 AI 協助完成，供人工校準與作品討論。它不是 G2i 官方評分，也不證明個人的 Staff-level 能力。</p></section>'
    (target / 'index.html').write_text(page('AI Evals · AI Engineer Lab', intro+'<div class="cards">'+''.join(cards)+'</div>', 'evals'))
    return provenance
