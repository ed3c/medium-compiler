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
            self.assertEqual(len(provenance),1)
            route=out/'ai-evals/soodles-claim-refusal'
            report=json.loads((route/'report.json').read_text())
            audit=json.loads((route/'archive-audit.json').read_text())
            self.assertEqual(audit['fresh_coding_model_runs'],0)
            self.assertFalse(audit['complete_platform_transcript'])
            self.assertEqual(len(audit['observations']),6)
            self.assertEqual(report['human_calibration'],'NOT_PERFORMED')
            self.assertEqual(hashlib.sha256((route/'assessment.md').read_bytes()).hexdigest(),provenance[0]['assessment_sha256'])
            rendered=(route/'index.html').read_text()
            self.assertIn('Evidence coverage',rendered)
            self.assertIn('lang="en"',rendered)
            self.assertIn('/ai-evals/soodles-claim-refusal/',(out/'ai-evals/index.html').read_text())
