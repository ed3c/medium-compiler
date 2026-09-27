"""Flow learning controls on the real pinned Ops case; answers here are synthetic."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("lossless", ROOT / "scripts/lossless_batch.py")
batch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(batch)
EV = ROOT / "evidence/issue-8"


class FlowLearningTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.run = self.root / "run"
        batch.boot(EV / "before.md", EV / "plan.json", self.run)

    def complete_patches(self):
        batch.apply_patch(self.run, EV / "patch-01.json")
        batch.apply_patch(self.run, EV / "patch-02.json")

    def response(self):
        state = batch.inspect(self.run)
        return {"case": state["case"], "article_sha256": state["article_sha256"],
                "answers": [{"unit_id": p["unit_id"], "answer": "synthetic test answer"}
                            for p in state["human_checkpoint"]["prompts"]]}

    def test_boot_exposes_case_decision_and_real_evidence(self):
        state = batch.inspect(self.run)
        self.assertEqual(state["status"], "CONTINUE")
        self.assertEqual(state["case"]["id"], "ops-reconciliation-copilot")
        self.assertEqual(len(state["case"]["revision"]), 40)
        self.assertIn("T100", state["decision_prompt"])
        self.assertIn("A03", state["learning_step"])
        self.assertEqual({ref["role"] for ref in state["evidence_refs"]}, {"code", "test", "test_result"})
        runtime = json.loads((EV / "inputs/ops-runtime-manifest.json").read_text())
        self.assertEqual(runtime["checkout_sha"], state["case"]["revision"])
        self.assertEqual(len(runtime["checks"]), 10)
        self.assertTrue(all(check["passed"] for check in runtime["checks"]))
        self.assertFalse(runtime["live_llm"])
        self.assertEqual(state["human_checkpoint"]["status"], "DEFERRED")

    def test_planted_wrong_revision_and_anchor_fail(self):
        plan = json.loads((EV / "plan.json").read_text())
        sources = {entry["id"]: (EV / entry["path"]).read_bytes() for entry in plan["sources"]}
        original = plan["case"]["revision"]
        plan["case"]["revision"] = "0" * 40
        with self.assertRaisesRegex(batch.Refusal, "case revision"):
            batch.validate_plan(plan, (EV / "before.md").read_text(), sources)
        plan["case"]["revision"] = original
        plan["units"][0]["evidence_refs"][0]["anchor"] = "invented behavior"
        with self.assertRaisesRegex(batch.Refusal, "evidence anchor"):
            batch.validate_plan(plan, (EV / "before.md").read_text(), sources)

    def test_checkpoint_is_receipted_but_ungraded(self):
        self.complete_patches()
        response = self.response()
        path = self.root / "response.json"
        path.write_bytes(batch.encoded(response))
        result = batch.record_checkpoint(self.run, path)
        self.assertEqual(result["human_checkpoint"]["status"], "RECORDED_UNGRADED")
        self.assertEqual(batch.record_checkpoint(self.run, path)["operation"], "NOOP")
        receipt = next(self.run.glob("human-checkpoint-*.json"))
        receipt.write_bytes(receipt.read_bytes() + b" ")
        with self.assertRaisesRegex(batch.Refusal, "receipt is stale"):
            batch.inspect(self.run)

    def test_stale_and_wrong_unit_refuse_without_writing(self):
        self.complete_patches()
        response = self.response()
        path = self.root / "response.json"
        response["article_sha256"] = "sha256:" + "0" * 64
        path.write_bytes(batch.encoded(response))
        with self.assertRaisesRegex(batch.Refusal, "stale"):
            batch.record_checkpoint(self.run, path)
        response["article_sha256"] = batch.inspect(self.run)["article_sha256"]
        response["answers"][0]["unit_id"] = "another-case"
        path.write_bytes(batch.encoded(response))
        with self.assertRaisesRegex(batch.Refusal, "stable unit"):
            batch.record_checkpoint(self.run, path)
        self.assertFalse(list(self.run.glob("human-checkpoint-*.json")))

    def test_done_does_not_claim_human_learning(self):
        self.complete_patches()
        done = batch.finish(self.run, EV / "review.json")
        self.assertEqual(done["status"], "DONE")
        self.assertEqual(done["human_checkpoint"]["status"], "PENDING")
        self.assertEqual(done["human_learning_outcome"], "NOT_MEASURED")
