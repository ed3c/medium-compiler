"""Negative controls for the existing-article path and re-read validation."""
import json
from pathlib import Path
import tempfile
import unittest

import medium_compiler as mc


class RevisionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.run = self.root / 'run'
        self.before = self.root / 'before.md'
        self.before.write_text('# 文件版本\n\n本文將介紹 `candidate`。\n\n'
                               '[來源](https://example.org/v2)說明版本。\n\n'
                               '```python\nprint("v2")\n```\n', encoding='utf-8')
        self.after = self.root / 'after.md'
        self.after.write_text(self.before.read_text().replace('本文將介紹', '結果是'), encoding='utf-8')
        self.spec = self.root / 'spec.json'
        self.spec.write_text(json.dumps({'topic': '版本', 'claims': [], 'terms': []}), encoding='utf-8')
        self.coverage = self.root / 'coverage.json'
        self.coverage.write_text(json.dumps({'elements': ['copyedit'], 'claims': [], 'terms': []}))
        mc.init_run(self.spec, self.run, self.before)

    def submit(self):
        return mc.submit_stage(self.run, 6, self.after, self.coverage)

    def finish(self):
        self.submit()
        mc.assemble(self.run)
        mc.build_receipt(self.run)

    def test_import_does_not_fabricate_stages(self):
        self.assertEqual(mc.next_action(self.run)['next_stage'], 6)
        self.assertEqual(json.loads((self.run/'state.json').read_text())['submitted_stages'], [])

    def test_revision_proof_is_bound_to_imported_before(self):
        self.finish()
        self.before.write_text('unrelated old article')
        with self.assertRaisesRegex(mc.CompilerError, 'imported baseline'):
            mc.prove_article_update(self.run, 1, self.before, self.after, self.root/'proof.json')

    def test_spec_change_is_refused_without_advancing_state(self):
        state = (self.run/'state.json').read_bytes()
        (self.run/'spec.json').write_text('{"topic":"changed"}')
        with self.assertRaisesRegex(mc.CompilerError, 'admitted artifact changed'):
            self.submit()
        self.assertEqual(state, (self.run/'state.json').read_bytes())
        self.assertFalse((self.run/'parts/stage-06.md').exists())

    def test_inline_code_change_is_refused(self):
        self.after.write_text(self.after.read_text().replace('`candidate`', '`verified`'))
        with self.assertRaisesRegex(mc.CompilerError, 'inline code'):
            self.submit()

    def test_link_change_is_refused(self):
        self.after.write_text(self.after.read_text().replace('example.org/v2', 'example.org/v1'))
        with self.assertRaisesRegex(mc.CompilerError, 'source links'):
            self.submit()

    def test_prose_adjacent_to_link_can_change(self):
        self.after.write_text(self.after.read_text().replace('說明版本。', '列出了版本。'))
        self.submit()

    def test_unclosed_fence_is_refused(self):
        self.after.write_text(self.after.read_text().rstrip()[:-3])
        with self.assertRaisesRegex(mc.CompilerError, 'unclosed fenced'):
            self.submit()

    def test_tilde_fence_code_mutation_is_detected(self):
        before = '~~~python\nx = 1\n~~~\n'
        with self.assertRaisesRegex(mc.CompilerError, 'changed fenced'):
            mc._validate_copyedit({}, before, before.replace('1', '2'))

    def test_renewing_receipt_does_not_launder_mutated_code(self):
        self.finish()
        old = (self.run/'validation-receipt.json').read_bytes()
        for name in ('parts/stage-06.md', 'medium-canonical.md'):
            p = self.run/name
            p.write_text(p.read_text().replace('print("v2")', 'print("v1")'))
        with self.assertRaisesRegex(mc.CompilerError, 'admitted artifact changed'):
            mc.build_receipt(self.run)
        self.assertEqual(old, (self.run/'validation-receipt.json').read_bytes())

    def test_coverage_change_invalidates_receipt(self):
        self.finish()
        (self.run/'parts/stage-06.coverage.json').write_text('{}')
        with self.assertRaisesRegex(mc.CompilerError, 'admitted artifact changed'):
            mc.check_receipt(self.run)

    def test_semantic_snapshot_is_not_mutable_after_import(self):
        (self.run/'semantic-draft.md').write_text('different baseline')
        with self.assertRaisesRegex(mc.CompilerError, 'admitted artifact changed'):
            self.submit()

    def test_receipt_cannot_promote_its_own_semantic_status(self):
        self.finish()
        path = self.run/'validation-receipt.json'
        receipt = json.loads(path.read_text())
        receipt['semantic_correctness'] = 'PASS'
        path.write_text(json.dumps(receipt))
        with self.assertRaisesRegex(mc.CompilerError, 'evidence changed'):
            mc.check_receipt(self.run)

    def test_next_stops_after_valid_receipt(self):
        self.finish()
        result = mc.next_action(self.run)
        self.assertEqual(result['status'], 'VALIDATED')
        self.assertIsNone(result['next'])

    def test_proof_cannot_overwrite_article(self):
        self.finish()
        old = self.after.read_bytes()
        with self.assertRaisesRegex(mc.CompilerError, 'overwrite'):
            mc.prove_article_update(self.run, 1, self.before, self.after, self.after)
        self.assertEqual(old, self.after.read_bytes())

    def test_receipt_check_is_read_only(self):
        self.finish()
        before = {str(p): p.read_bytes() for p in self.run.rglob('*') if p.is_file()}
        mc.check_receipt(self.run)
        after = {str(p): p.read_bytes() for p in self.run.rglob('*') if p.is_file()}
        self.assertEqual(before, after)


if __name__ == '__main__':
    unittest.main()
