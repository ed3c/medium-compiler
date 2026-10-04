import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('eval_site', ROOT/'scripts/ai_evals_site.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class AIEvalsSiteTests(unittest.TestCase):
    def test_stale_or_escaped_sources_are_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); (root/'a.md').write_text('original')
            ref={'path':'a.md','sha256':hashlib.sha256(b'original').hexdigest()}
            self.assertEqual(module.checked_file(root,ref),b'original')
            (root/'a.md').write_text('changed')
            with self.assertRaises(ValueError): module.checked_file(root,ref)
            with self.assertRaises(ValueError): module.checked_file(root,{'path':'../outside','sha256':'0'*64})

    def test_published_report_preserves_scope_and_download_identities(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)
            provenance=module.render_reports(ROOT,out,lambda title,body,active:body,lambda s:s)
            catalog=json.loads((ROOT/'reports/ai-evals/catalog.json').read_text())
            expected={}
            for entry in catalog['reports']:
                source=json.loads(module.checked_file(ROOT,entry))
                expected['/ai-evals/'+source['id']+'/']=(entry,source)
            self.assertEqual({p['route'] for p in provenance},set(expected))
            self.assertEqual(len(provenance),len(expected))
            for item in provenance:
                entry,source=expected[item['route']]
                delivered=out/item['route'].strip('/')
                self.assertEqual(hashlib.sha256((delivered/'report.json').read_bytes()).hexdigest(),entry['sha256'])
                self.assertEqual(hashlib.sha256((delivered/'assessment.md').read_bytes()).hexdigest(),source['assessment']['sha256'])
                self.assertIn(item['route'],(out/'ai-evals/index.html').read_text())
                if source.get('review_mode') in {'agent_workflow_evaluation','combined'}:
                    rendered=(delivered/'index.html').read_text()
                    self.assertIn('Review mode:',rendered)
                    self.assertIn(source['review_mode'],rendered)
                    coverage_heading = '證據涵蓋範圍（Evidence coverage）' if source.get('language') == 'zh-Hant' else 'Evidence coverage'
                    self.assertLess(rendered.index('<article class="article"'),rendered.index('<h2>'+coverage_heading))
                if source.get('language') == 'zh-Hant':
                    rendered=(delivered/'index.html').read_text()
                    self.assertIn('lang="zh-Hant"',rendered)
                    self.assertIn('繁體中文評估正文',rendered)
                    self.assertNotIn('>English assessment</a>',rendered)
            route=out/'ai-evals/soodles-claim-refusal'
            report=json.loads((route/'report.json').read_text())
            audit=json.loads((route/'archive-audit.json').read_text())
            self.assertEqual(audit['fresh_coding_model_runs'],0)
            self.assertFalse(audit['complete_platform_transcript'])
            self.assertEqual(len(audit['observations']),6)
            self.assertEqual(report['human_calibration'],'NOT_PERFORMED')
            original=next(p for p in provenance if p['route']=='/ai-evals/soodles-claim-refusal/')
            self.assertEqual(hashlib.sha256((route/'assessment.md').read_bytes()).hexdigest(),original['assessment_sha256'])
            rendered=(route/'index.html').read_text()
            self.assertIn('Evidence coverage',rendered)
            self.assertIn('lang="en"',rendered)
            self.assertIn('/ai-evals/soodles-claim-refusal/',(out/'ai-evals/index.html').read_text())
