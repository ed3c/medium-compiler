"""Real article, synthetic owner receipts: fixtures are never human learning evidence."""
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
EV = ROOT / 'evidence/issue-8'
spec = importlib.util.spec_from_file_location('handoff_batch', ROOT / 'scripts/lossless_batch.py')
batch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(batch)


class LearningHandoffTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        shutil.copytree(EV / 'inputs', self.root / 'inputs')
        self.article = EV / 'before.md'
        self.plan = json.loads((EV / 'plan.json').read_text())
        self.plan['purpose'] = 'learning-episode'
        self.plan['learning'] = {'episode_id': 'synthetic-episode',
            'lesson_ref': 'synthetic-course@fixed:one-lesson', 'handoff_source': 'owner-handoff'}
        self.record = {'schema_version': 'medium-learning-handoff@1',
            'episode_id': 'synthetic-episode', 'lesson_ref': 'synthetic-course@fixed:one-lesson',
            'case': self.plan['case'], 'status': 'ACCEPTED', 'product_decision': 'NO_CHANGE',
            'evidence_refs': [{'source_id': 'ops-runtime-result', 'anchor': 'cross_currency_not_subtracted'}],
            'human_checkpoint': {'source_id': 'human-answer', 'anchor': 'SYNTHETIC HUMAN ANSWER'},
            'learning_record': {'source_id': 'learning-record', 'anchor': 'SYNTHETIC OWNER ACCEPTANCE'}}
        self.add_source('human-answer', b'SYNTHETIC HUMAN ANSWER\n', 'synthetic learner, test only')
        self.add_source('learning-record', b'SYNTHETIC OWNER ACCEPTANCE\n', 'synthetic course owner, test only')
        self.run = self.root / 'run'
        self.sync()

    def add_source(self, sid, data, provenance):
        rel = f'inputs/{sid}.txt'
        (self.root / rel).write_bytes(data)
        self.plan['sources'] = [s for s in self.plan['sources'] if s['id'] != sid]
        self.plan['sources'].append({'id': sid, 'path': rel, 'sha256': batch.digest(data), 'provenance': provenance})

    def sync(self):
        self.add_source('owner-handoff', batch.encoded(self.record), 'synthetic external owner declaration, not a real learning event')
        self.path = self.root / 'plan.json'
        self.path.write_bytes(batch.encoded(self.plan))

    def all_bytes(self):
        return {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}

    def cli(self, *args):
        return subprocess.run([sys.executable, str(ROOT / 'scripts/lossless_batch.py'), *map(str, args)],
                              capture_output=True, text=True, timeout=30)

    def test_preflight_ready_is_read_only_not_a_progress_update(self):
        before = self.all_bytes()
        r = batch.preflight(self.article, self.path)
        self.assertEqual(r['status'], 'READY')
        self.assertEqual(r['next'], {'owner': 'medium-compiler', 'operation': 'boot'})
        self.assertEqual(r['human_learning_outcome'], 'NOT_MEASURED')
        self.assertEqual(r['progress_write'], 'NEVER_BY_MEDIUM_COMPILER')
        self.assertEqual(before, self.all_bytes())

    def test_pending_human_names_owner_and_boot_never_writes(self):
        self.record['human_checkpoint'] = None; self.sync()
        before = self.all_bytes()
        r = batch.preflight(self.article, self.path)
        self.assertEqual(r['status'], 'BLOCKED')
        self.assertEqual(r['next']['owner'], 'learner')
        with self.assertRaises(batch.LearningPending): batch.boot(self.article, self.path, self.run)
        self.assertEqual(before, self.all_bytes()); self.assertFalse(self.run.exists())

    def test_no_change_is_not_learning_completion(self):
        self.record.update(status='PENDING', human_checkpoint=None, learning_record=None); self.sync()
        r = batch.preflight(self.article, self.path)
        self.assertFalse(r['article_mutation_allowed'])
        self.assertEqual(r['product_decision'], 'NO_CHANGE')
        self.assertEqual([m['input'] for m in r['missing']], ['human_checkpoint', 'accepted_learning_record'])

    def test_product_and_evidence_owner_routes(self):
        for changes, owner in [({'product_decision': 'PENDING'}, 'product-owner'),
                               ({'evidence_refs': []}, 'evidence-owner')]:
            old = copy.deepcopy(self.record)
            self.record.update(changes); self.sync()
            with self.subTest(owner=owner): self.assertEqual(batch.preflight(self.article, self.path)['next']['owner'], owner)
            self.record = old

    def test_recorded_answer_cannot_admit_own_lesson(self):
        self.record.update(status='PENDING', learning_record=None); self.sync()
        r = batch.preflight(self.article, self.path)
        self.assertEqual(r['next']['owner'], 'learning-owner')
        self.assertEqual(r['status'], 'BLOCKED')

    def test_wrong_episode_lesson_and_revision_refused(self):
        for key, value in [('episode_id', 'other'), ('lesson_ref', 'other'),
                            ('case', dict(self.plan['case'], revision='0'*40))]:
            old = copy.deepcopy(self.record)
            self.record[key] = value; self.sync()
            with self.subTest(key=key), self.assertRaises(batch.Refusal): batch.boot(self.article, self.path, self.run)
            self.assertFalse(self.run.exists()); self.record = old

    def test_changed_source_and_fake_anchor_refused(self):
        p = self.root / 'inputs/human-answer.txt'; original = p.read_bytes()
        p.write_bytes(b'changed')
        with self.assertRaisesRegex(batch.Refusal, 'digest'): batch.preflight(self.article, self.path)
        p.write_bytes(original)
        self.record['human_checkpoint']['anchor'] = 'not present'; self.sync()
        with self.assertRaisesRegex(batch.Refusal, 'anchor'): batch.preflight(self.article, self.path)

    def test_handoff_cannot_cite_itself_as_human_evidence(self):
        self.record['human_checkpoint'] = {'source_id': 'owner-handoff', 'anchor': 'ACCEPTED'}; self.sync()
        with self.assertRaisesRegex(batch.Refusal, 'separate pinned'): batch.preflight(self.article, self.path)

    def test_unknown_fields_or_forged_reader_status_refused(self):
        self.record['status'] = 'RECORDED_UNGRADED'; self.sync()
        with self.assertRaisesRegex(batch.Refusal, 'status'): batch.preflight(self.article, self.path)
        self.record['status'] = 'ACCEPTED'; self.record['mastered'] = True; self.sync()
        with self.assertRaisesRegex(batch.Refusal, 'fields'): batch.preflight(self.article, self.path)

    def test_learning_cannot_silently_use_source_explanation_mode(self):
        del self.plan['purpose']; self.sync()
        with self.assertRaisesRegex(batch.Refusal, 'purpose=learning-episode'): batch.preflight(self.article, self.path)
        self.plan['purpose'] = 'learning-episode'; del self.plan['learning']; self.sync()
        self.assertEqual(batch.preflight(self.article, self.path)['next']['missing_input'], 'learning_handoff')

    def test_external_learning_provenance_not_masquerading_as_ops_code(self):
        self.assertEqual(batch.preflight(self.article, self.path)['status'], 'READY')
        main = next(x for x in self.plan['sources'] if x['id'] == 'ops-main')
        main['provenance'] = 'other-project@'+'0'*40+':code'; self.sync()
        with self.assertRaisesRegex(batch.Refusal, 'case revision'): batch.preflight(self.article, self.path)

    def test_accepted_snapshot_survives_new_process_and_duplicate_patch_is_noop(self):
        batch.boot(self.article, self.path, self.run)
        batch.apply_patch(self.run, EV / 'patch-01.json')
        before = self.all_bytes()
        proc = self.cli('next', '--run-dir', self.run)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        r = json.loads(proc.stdout)
        self.assertEqual(r['source_cursor'], 'finding-precedence')
        self.assertEqual(r['learning_handoff']['episode_id'], 'synthetic-episode')
        self.assertEqual(batch.apply_patch(self.run, EV / 'patch-01.json')['operation'], 'NOOP')
        self.assertEqual(before, self.all_bytes())

    def test_source_snapshot_drift_refuses_continuation(self):
        batch.boot(self.article, self.path, self.run)
        path = self.run / 'sources/owner-handoff.txt'; path.write_bytes(path.read_bytes()+b' ')
        with self.assertRaisesRegex(batch.Refusal, 'source snapshot drift'): batch.inspect(self.run)

    def test_finished_article_does_not_write_progress_or_forge_reader(self):
        batch.boot(self.article, self.path, self.run)
        batch.apply_patch(self.run, EV / 'patch-01.json'); batch.apply_patch(self.run, EV / 'patch-02.json')
        done = batch.finish(self.run, EV / 'review.json')
        self.assertEqual(done['status'], 'DONE')
        self.assertEqual(done['human_checkpoint']['status'], 'PENDING')
        self.assertEqual(done['human_learning_outcome'], 'NOT_MEASURED')
        self.assertFalse(list(self.root.rglob('LEARNING.md')))

    def test_real_cli_blocks_pending_without_run(self):
        self.record['human_checkpoint'] = None; self.sync(); before = self.all_bytes()
        for args in [('preflight', '--article', self.article, '--plan', self.path),
                     ('boot', '--article', self.article, '--plan', self.path, '--run-dir', self.run)]:
            proc = self.cli(*args)
            self.assertEqual(proc.returncode, 3, proc.stderr)
            self.assertEqual(json.loads(proc.stdout)['next']['missing_input'], 'human_checkpoint')
        self.assertEqual(before, self.all_bytes())

    def test_active_run_has_only_one_executable_next(self):
        r = batch.boot(self.article, self.path, self.run)
        self.assertEqual(r['next'], 'drill-down')
        self.assertNotIn('next', r['learning_handoff'])

    def test_ordinary_article_explanation_does_not_require_a_learner(self):
        r = batch.preflight(self.article, EV / 'plan.json')
        self.assertEqual(r['status'], 'READY')
        self.assertEqual(r['purpose'], 'source-explanation')


if __name__ == '__main__': unittest.main()
