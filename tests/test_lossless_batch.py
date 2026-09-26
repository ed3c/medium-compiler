"""All controls begin with the actual Ops article and its two requested expansions."""
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("lossless", ROOT / "scripts/lossless_batch.py")
batch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(batch)
EV = ROOT / "evidence/issue-8"


class LosslessBatchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.run = self.root / "run"
        batch.boot(EV / "before.md", EV / "plan.json", self.run)

    def snapshot(self):
        return {str(p.relative_to(self.run)): p.read_bytes() for p in self.run.rglob("*") if p.is_file()}

    def patch(self, n):
        return batch.apply_patch(self.run, EV / f"patch-0{n}.json")

    def both(self):
        self.patch(1)
        self.patch(2)

    def test_boot_exposes_pending_work_not_done(self):
        r = batch.inspect(self.run)
        self.assertEqual(r["status"], "CONTINUE")
        self.assertEqual(r["source_cursor"], "transaction-index")
        self.assertEqual(len(r["remaining_work"]), 2)

    def test_early_finish_refuses_without_mutation(self):
        before = self.snapshot()
        with self.assertRaisesRegex(batch.Refusal, "pending work"):
            batch.finish(self.run, EV / "review.json")
        self.assertEqual(before, self.snapshot())

    def test_second_patch_cannot_skip_first(self):
        before = self.snapshot()
        with self.assertRaisesRegex(batch.Refusal, "wrong unit"):
            self.patch(2)
        self.assertEqual(before, self.snapshot())

    def test_restart_reconstructs_next_from_journal(self):
        self.patch(1)
        self.assertEqual(batch.inspect(self.run)["source_cursor"], "finding-precedence")

    def test_retry_is_noop_with_no_writes(self):
        self.patch(1)
        before = self.snapshot()
        self.assertEqual(self.patch(1)["operation"], "NOOP")
        self.assertEqual(before, self.snapshot())

    def test_conflicting_retry_is_refused(self):
        self.patch(1)
        p = json.loads((EV / "patch-01.json").read_text())
        p["text"] += "wrong\n\n"
        bad = self.root / "bad.json"; bad.write_bytes(batch.encoded(p))
        with self.assertRaisesRegex(batch.Refusal, "conflicting replay"):
            batch.apply_patch(self.run, bad)

    def test_patch_cannot_request_replacement(self):
        p = json.loads((EV / "patch-01.json").read_text()); p["replace"] = "drop old body"
        bad = self.root / "bad.json"; bad.write_bytes(batch.encoded(p))
        with self.assertRaisesRegex(batch.Refusal, "accepts only"):
            batch.apply_patch(self.run, bad)

    def test_unknown_unit_refused(self):
        p = json.loads((EV / "patch-01.json").read_text()); p["unit_id"] = "unknown"
        bad = self.root / "bad.json"; bad.write_bytes(batch.encoded(p))
        with self.assertRaisesRegex(batch.Refusal, "wrong unit"):
            batch.apply_patch(self.run, bad)

    def test_admitted_patch_mutation_detected(self):
        self.patch(1)
        p = next((self.run / "patches").glob("*.json"))
        p.write_bytes(p.read_bytes()+b" ")
        with self.assertRaisesRegex(batch.Refusal, "out-of-order patch"):
            batch.inspect(self.run)

    def test_boot_and_source_drift_refused(self):
        for rel in ("boot.md", "sources/ops-main.txt"):
            with self.subTest(rel=rel):
                p = self.run / rel; old = p.read_bytes();p.write_bytes(old+b"x")
                with self.assertRaises(batch.Refusal): batch.inspect(self.run)
                p.write_bytes(old)

    def test_unclosed_fence_refused(self):
        p = json.loads((EV / "patch-01.json").read_text());p["text"] += "```python\nx=1\n\n"
        bad=self.root / "bad.json";bad.write_bytes(batch.encoded(p))
        with self.assertRaisesRegex(batch.mc.CompilerError, "unclosed"):
            batch.apply_patch(self.run,bad)

    def test_original_bytes_and_new_context_survive(self):
        self.both()
        _, data, _ = batch.replay(self.run)
        self.assertEqual(data, (EV/"expected-after.md").read_bytes())
        restored = data.decode()
        for n in (1, 2):
            delta = json.loads((EV / f"patch-0{n}.json").read_text())["text"]
            self.assertEqual(restored.count(delta), 1)
            restored = restored.replace(delta, "", 1)
        self.assertEqual(restored.encode(), (EV / "before.md").read_bytes())

    def test_no_silent_done_before_review(self):
        self.both()
        r = batch.inspect(self.run)
        self.assertEqual(r["status"], "CONTINUE")
        self.assertEqual(r["next"], "review-and-finish")

    def test_stale_or_failed_review_refused(self):
        self.both()
        for key,val in [("article_sha256","sha256:wrong"),("verdict","FAIL"),("unresolved_gaps",["missing cause"]),("unit_ids",[])]:
            review=json.loads((EV/"review.json").read_text());review[key]=val
            bad=self.root/"review.json";bad.write_bytes(batch.encoded(review))
            with self.subTest(key=key),self.assertRaises(batch.Refusal):batch.finish(self.run,bad)
        self.assertFalse((self.run/"final").exists())

    def test_finish_uses_existing_compiler_and_stops(self):
        self.both()
        r = batch.finish(self.run, EV / "review.json")
        self.assertEqual(r["status"],"DONE")
        self.assertEqual(r["semantic_review"],"AUTHOR_REVIEW_ONLY")
        self.assertEqual((self.run/"final/compiled/medium-canonical.md").read_bytes(),(EV/"expected-after.md").read_bytes())
        self.assertIsNone(batch.inspect(self.run)["next"])

    def test_changed_final_is_not_revalidated_as_done(self):
        self.both();batch.finish(self.run, EV / "review.json")
        p=self.run/"final/compiled/medium-canonical.md";p.write_bytes(p.read_bytes()+b"x")
        with self.assertRaises((batch.Refusal,batch.mc.CompilerError)):batch.inspect(self.run)

    def test_missing_patch_and_source_anchor_refused(self):
        self.both();next((self.run/"patches").glob("0000-*.json")).unlink()
        with self.assertRaises(batch.Refusal):batch.inspect(self.run)
        plan=json.loads((EV/"plan.json").read_text());plan["units"][0]["source_anchor"]="not a source quote"
        sources={"ops-main":(EV/"inputs/ops-main.py").read_bytes()}
        with self.assertRaisesRegex(batch.Refusal,"source anchor"):
            batch.validate_plan(plan,(EV/"before.md").read_text(),sources)

    def test_inspection_is_read_only(self):
        before=self.snapshot();batch.inspect(self.run);self.assertEqual(before,self.snapshot())

    def test_boot_refuses_existing_directory(self):
        with self.assertRaisesRegex(batch.Refusal,"new directory"):
            batch.boot(EV/"before.md",EV/"plan.json",self.run)


if __name__ == "__main__": unittest.main()
