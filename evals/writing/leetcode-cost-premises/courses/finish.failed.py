from pathlib import Path
import json
import re

p = Path(__file__).parent
english = (p/'article.en.md').read_text()
translation = (p/'article.first.zh-TW.md').read_text()
# First full translation reviewed against the already approved English; retain unchanged.
(p/'article.zh-TW.md').write_text(translation)
checks = {
    'all_fenced_blocks_identical': re.findall(r'```.*?```', english, re.S) == re.findall(r'```.*?```', translation, re.S),
    'inline_code_sequence_identical': re.findall(r'(?<!`)`([^`\n]+)`(?!`)', english) == re.findall(r'(?<!`)`([^`\n]+)`(?!`)', translation),
    'source_url_sequence_identical': re.findall(r'\]\((https?://[^)]+)\)', english) == re.findall(r'\]\((https?://[^)]+)\)', translation),
    'same_heading_count': len(re.findall(r'^#{1,6} ', english, re.M)) == len(re.findall(r'^#{1,6} ', translation, re.M)),
    'interview_questions_and_answers_unchanged': english.split('## Interview English and a master map\n\n')[1].split('\n\nThe master map')[0] == translation.split('## Interview English 與 master map\n\n')[1].split('\n\nmaster map')[0]
}
(p/'bilingual-controls.json').write_text(json.dumps(checks, indent=2) + '\n')
assert all(checks.values()), checks
# Exact raw final-body passages complement the prose reconstruction in report.md.
paragraphs = english.split('\n\n')
starts = [
    'The checkpoint is just before',
    'Whenever a course is removed',
    'Let `V = numCourses`',
    'The queue choice affects',
    "CPython v3.14.0's [deque implementation]",
    'Adjacency lists use',
    'Here is why a whole append-only sequence',
    'Building the `V` independent',
    'The readiness scan checks',
    'For auxiliary space',
    'If storing another `E` references',
    'The same legality and finite-cycle',
    'A different requirement changes',
    'This adaptation adds',
    'A tempting wrong return'
]
with (p/'report.md').open('a') as file:
    file.write('\n## Translation review and immutable support excerpts\n\n')
    file.write('The complete first translation was preserved as article.first.zh-TW.md. Author review found no required correction; article.zh-TW.md therefore retains its exact bytes. Full sections were read against English in order. Checked pair orientation, legal self-loop, isolated courses, None return, no bounded deque, all movie vectors and completion totals, zero crossing, checkpoint timing, finite-cycle proof, fixed-scalar assumptions, geometric append-only argument, per-list sum, old/new resize overlap, repeated-scan rounds and buffers, returned-order auxiliary/output split, and conditional minimality. English interview practice is deliberately identical. These are author checks, not independent review or learner evidence.\n\n')
    file.write('bilingual-controls.json records actual exact equality controls for all fenced blocks, inline-code sequence, source URL sequence, heading count and interview English. TRANSLATION_REVIEWED: yes. No revised English edition was translated after approval, and no later English repair was made.\n\n')
    file.write('The following excerpts are copied mechanically from the actual final English body, preserving Markdown identifiers and complete causal paragraphs. They support the reconstructions above; each inference is explained there and in these body passages, rather than inferred merely from quotation presence.\n\n')
    for start in starts:
        matches = [paragraph for paragraph in paragraphs if paragraph.startswith(start)]
        assert len(matches) == 1, start
        file.write('```text\n' + matches[0] + '\n```\n\n')

(p/'output.json').write_text(json.dumps({
    'english_reviewed_before_translation': True,
    'runtime_test_executed': True,
    'reference_article_read': False,
    'published': False,
    'final_body_review_recorded': True
}, indent=2) + '\n')
print(json.dumps(checks, indent=2))
