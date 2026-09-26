"""Executable refusal/continuation controls, not fresh Agent behavior evals."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import unittest
from unittest.mock import patch

import medium_compiler as mc
import test_medium_compiler as fixtures


class ReopenTests(unittest.TestCase):
    setUp = fixtures.MediumCompilerTests.setUp
    tearDown = fixtures.MediumCompilerTests.tearDown
    _coverage = fixtures.MediumCompilerTests._coverage
    _text = fixtures.MediumCompilerTests._text
    _submit = fixtures.MediumCompilerTests._submit
    _through_stage5 = fixtures.MediumCompilerTests._through_stage5
    _assemble_valid_run = fixtures.MediumCompilerTests._assemble_valid_run

    def snapshot(self):
        return {str(p.relative_to(self.run_dir)): p.read_bytes()
                for p in self.run_dir.rglob('*') if p.is_file()}

    def refuse_unchanged(self, stage, message):
        before = self.snapshot()
        with self.assertRaisesRegex(mc.CompilerError, message):
            mc.reopen_stage(self.run_dir, stage)
        self.assertEqual(before, self.snapshot())

    def test_earlier_submit_still_refuses_without_reopen(self):
        self._through_stage5()
        before = self.snapshot()
        with self.assertRaisesRegex(mc.CompilerError, 'out-of-order'):
            self._submit(4)
        self.assertEqual(before, self.snapshot())

    def test_invalid_targets_refuse_without_writes(self):
        self._through_stage5()
        for stage in (-1, 0, 6, 7, True, 1.0, '4'):
            with self.subTest(stage=stage):
                self.refuse_unchanged(stage, 'target must be an integer in 1..5')

    def test_unfrozen_or_unadmitted_target_refuses(self):
        self._submit(0)
        self._submit(1)
        self.refuse_unchanged(1, 'only before assembly after semantic freeze')
        self.refuse_unchanged(5, 'only before assembly after semantic freeze')

    def test_imported_article_has_no_semantic_stages_to_reopen(self):
        draft = self.root / 'existing.md'
        draft.write_text('# Existing article\n', encoding='utf-8')
        shutil.rmtree(self.run_dir)
        mc.init_run(self.spec_path, self.run_dir, draft)
        self.refuse_unchanged(4, 'imported drafts have no admitted semantic stages')
        self.assertEqual(mc.next_action(self.run_dir)['next_stage'], 6)

    def test_assembled_run_refuses_without_touching_receipt(self):
        self._assemble_valid_run()
        self.refuse_unchanged(4, 'only before assembly after semantic freeze')
        self.assertEqual(mc.check_receipt(self.run_dir)['status'], 'VALID')

    def test_reopen_four_preserves_prefix_and_rebuilds_claims(self):
        self._through_stage5()
        before = self.snapshot()
        result = mc.reopen_stage(self.run_dir, 4)
        expected_removed = {'semantic-draft.md', 'parts/stage-04.md',
                            'parts/stage-04.coverage.json', 'parts/stage-05.md',
                            'parts/stage-05.coverage.json'}
        self.assertEqual(set(result['invalidated_artifacts']), expected_removed)
        self.assertEqual(result['target_stage'], 4)
        self.assertEqual(result['next']['next'], 'submit')
        self.assertEqual(result['next']['next_stage'], 4)
        after = self.snapshot()
        for name in set(before) - expected_removed - {'state.json'}:
            self.assertEqual(before[name], after[name], name)
        self.assertTrue(expected_removed.isdisjoint(after))
        state = json.loads(after['state.json'])
        self.assertEqual(state['submitted_stages'], [0, 1, 2, 3])
        self.assertEqual(state['covered_claims'], ['C1', 'C2', 'C3'])
        self.assertEqual(state['defined_terms'], ['T1'])
        self.assertEqual(set(state['admitted_files']), set(after) - {'state.json'})
        self.assertEqual(mc.next_action(self.run_dir), result['next'])

    def test_reopen_one_removes_claims_and_terms_but_keeps_stage_zero(self):
        self._through_stage5()
        before = (self.run_dir/'parts/stage-00.md').read_bytes()
        mc.reopen_stage(self.run_dir, 1)
        state = json.loads((self.run_dir/'state.json').read_text())
        self.assertEqual(state['submitted_stages'], [0])
        self.assertEqual(state['covered_claims'], [])
        self.assertEqual(state['defined_terms'], [])
        self.assertEqual(before, (self.run_dir/'parts/stage-00.md').read_bytes())

    def test_reopen_after_stage_six_invalidates_accepted_copyedit(self):
        self._through_stage5()
        self._submit(6, (self.run_dir/'semantic-draft.md').read_text())
        result = mc.reopen_stage(self.run_dir, 5)
        self.assertIn('parts/stage-06.md', result['invalidated_artifacts'])
        self.assertIn('parts/stage-06.coverage.json', result['invalidated_artifacts'])
        with self.assertRaisesRegex(mc.CompilerError, 'only after admitted Stage 6'):
            mc.assemble(self.run_dir)

    def test_reopened_run_requires_resubmission_before_another_reopen(self):
        self._through_stage5()
        mc.reopen_stage(self.run_dir, 4)
        self.refuse_unchanged(1, 'only before assembly after semantic freeze')

    def test_full_corrected_path_keeps_copyedit_guard_and_terminal_next(self):
        self._through_stage5()
        old_code = "print('protected')"
        new_code = "print('corrected')"
        original = (self.run_dir/'semantic-draft.md').read_text()
        with self.assertRaisesRegex(mc.CompilerError, 'changed fenced'):
            self._submit(6, original.replace(old_code, new_code))
        mc.reopen_stage(self.run_dir, 4)
        self._submit(4, self._text(4).replace(old_code, new_code))
        self._submit(5)
        refreshed = (self.run_dir/'semantic-draft.md').read_text()
        self.assertIn(new_code, refreshed)
        with self.assertRaisesRegex(mc.CompilerError, 'changed fenced'):
            self._submit(6, refreshed.replace(new_code, old_code))
        self._submit(6, refreshed)
        self.assertEqual(mc.next_action(self.run_dir)['next'], 'assemble')
        mc.assemble(self.run_dir)
        mc.build_receipt(self.run_dir)
        self.assertEqual(mc.check_receipt(self.run_dir)['status'], 'VALID')
        terminal = mc.next_action(self.run_dir)
        self.assertIsNone(terminal['next'])
        self.assertEqual(terminal['semantic_correctness'], 'NOT_ASSESSED')

    def test_plain_copyedit_needs_no_reopen(self):
        self._through_stage5()
        draft = (self.run_dir/'semantic-draft.md').read_text()
        self._submit(6, draft.replace('## Stage 1', '## Introduction'))
        mc.assemble(self.run_dir)
        mc.build_receipt(self.run_dir)
        self.assertEqual(mc.check_receipt(self.run_dir)['status'], 'VALID')

    def test_admitted_drift_is_not_laundered_by_reopen(self):
        self._through_stage5()
        (self.run_dir/'parts/stage-04.md').write_text('direct edit')
        self.refuse_unchanged(4, 'admitted artifact changed')

    def test_missing_stage_binding_refuses(self):
        self._through_stage5()
        state_path = self.run_dir/'state.json'
        state = json.loads(state_path.read_text())
        del state['admitted_files']['parts/stage-04.coverage.json']
        state_path.write_text(json.dumps(state))
        self.refuse_unchanged(4, 'incomplete admission bindings')

    def test_invalid_submitted_order_refuses(self):
        self._through_stage5()
        state_path = self.run_dir/'state.json'
        state = json.loads(state_path.read_text())
        state['submitted_stages'] = [0, 1, 2, 4, 3, 5]
        state_path.write_text(json.dumps(state))
        self.refuse_unchanged(4, 'invalid submitted stage order')

    def test_bound_but_false_coverage_is_rechecked_before_invalidation(self):
        self._through_stage5()
        coverage = self.run_dir/'parts/stage-01.coverage.json'
        value = json.loads(coverage.read_text())
        value['claims'] = []
        coverage.write_text(json.dumps(value))
        state_path = self.run_dir/'state.json'
        state = json.loads(state_path.read_text())
        state['admitted_files']['parts/stage-01.coverage.json'] = mc._sha256_path(coverage)
        state_path.write_text(json.dumps(state))
        self.refuse_unchanged(4, 'claim coverage')

    def test_unexpected_final_artifacts_are_preserved_and_refused(self):
        self._through_stage5()
        for name in ('medium-canonical.md', 'validation-receipt.json'):
            p = self.run_dir/name
            p.write_text('unknown provenance')
            self.refuse_unchanged(4, 'unexpected final artifact')
            p.unlink()

    def test_symlinked_artifact_is_not_moved_or_deleted(self):
        self._through_stage5()
        part = self.run_dir/'parts/stage-04.md'
        external = self.root/'external.md'
        external.write_bytes(part.read_bytes())
        part.unlink()
        part.symlink_to(external)
        self.refuse_unchanged(4, 'symlink')
        self.assertTrue(part.is_symlink())
        self.assertEqual(external.read_bytes(), self._text(4).encode())

    def test_mid_move_error_restores_all_original_bytes(self):
        self._through_stage5()
        before = self.snapshot()
        original = Path.replace
        calls = []
        def fail_once(source, target):
            calls.append(str(source))
            if len(calls) == 2:
                raise OSError('injected rename failure')
            return original(source, target)
        with patch.object(Path, 'replace', fail_once):
            with self.assertRaisesRegex(OSError, 'injected rename failure'):
                mc.reopen_stage(self.run_dir, 4)
        self.assertEqual(before, self.snapshot())
        self.assertEqual(mc.next_action(self.run_dir)['next_stage'], 6)

    def test_state_commit_error_restores_all_original_bytes(self):
        self._through_stage5()
        before = self.snapshot()
        original = Path.replace
        def fail_commit(source, target):
            if Path(target) == self.run_dir/'state.json':
                raise OSError('injected state commit failure')
            return original(source, target)
        with patch.object(Path, 'replace', fail_commit):
            with self.assertRaisesRegex(OSError, 'injected state commit failure'):
                mc.reopen_stage(self.run_dir, 4)
        self.assertEqual(before, self.snapshot())

    def test_actual_cli_routes_to_target_and_rejects_invalid_target(self):
        self._through_stage5()
        cli = Path(mc.__file__).resolve()
        common = [sys.executable, str(cli), 'reopen', '--run-dir', str(self.run_dir)]
        bad = subprocess.run(common + ['--stage', '6'], capture_output=True, text=True)
        self.assertEqual(bad.returncode, 2)
        good = subprocess.run(common + ['--stage', '4'], capture_output=True, text=True)
        self.assertEqual(good.returncode, 0, good.stderr)
        self.assertEqual(json.loads(good.stdout)['next']['next_stage'], 4)
        self.assertEqual(mc.next_action(self.run_dir)['next'], 'submit')


if __name__ == '__main__':
    unittest.main()
