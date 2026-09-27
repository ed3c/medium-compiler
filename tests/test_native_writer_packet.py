"""Controls for native cloud packet projection; never counted as writer behavior."""
import importlib.util, json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("native_writer_packet",ROOT/"scripts/native_writer_packet.py")
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
SPEC=ROOT/"evals/writing/ops-evidence-handoff/experiment.json"
NATIVE=ROOT/"evals/writing/ops-evidence-handoff/native-cloud.json"

class NativeWriterPacketTests(unittest.TestCase):
    def test_projects_six_fresh_native_runs_without_model_calls(self):
        r=mod.project(SPEC,NATIVE)
        self.assertEqual(r["status"],"READY_FOR_NATIVE_SUPERVISOR")
        self.assertEqual(len(r["launches"]),6)
        self.assertEqual(r["model_calls"],0)
        self.assertFalse(r["authorizes_native_launch"])
        self.assertIsNone(r["behavior"])
    def test_every_launch_uses_native_spawn_and_no_inherited_turns(self):
        r=mod.project(SPEC,NATIVE)
        for x in [r["pilot"],*r["launches"]]:
            self.assertEqual(x["tool"],"collaboration.spawn_agent")
            self.assertEqual(x["fork_turns"],"none")
            self.assertIsNone(x["model_override"])
    def test_arms_match_frozen_refs_and_order(self):
        s=json.loads(SPEC.read_text());r=mod.project(SPEC,NATIVE)
        self.assertEqual([x["arm"] for x in r["launches"]],s["order"])
        self.assertEqual({x["source_ref"] for x in r["launches"] if x["arm"]=="baseline"},
                         {s["arms"]["baseline"]["revision"]})
        self.assertEqual({x["source_ref"] for x in r["launches"] if x["arm"]=="treatment"},
                         {s["arms"]["treatment"]["revision"]})
    def test_consumer_message_keeps_answer_and_observer_outside(self):
        r=mod.project(SPEC,NATIVE)
        text="\n".join(x["message"] for x in r["launches"])
        self.assertIn("Do not read expected answers",text)
        self.assertNotIn("SCOPED_OBSERVED_ROUTE_IMPROVEMENT",text)
        self.assertEqual(r["observer_owner"],"external supervisor")
    def test_cloud_contract_rejects_local_cli_carrier(self):
        raw=json.loads(NATIVE.read_text());raw["carrier"]="host_codex_exec"
        p=ROOT/"tests/fixtures/native-cloud-invalid.json";p.write_text(json.dumps(raw))
        try:
            with self.assertRaisesRegex(mod.Invalid,"native collaboration"):
                mod.validate(SPEC,p)
        finally:p.unlink(missing_ok=True)
    def test_forked_conversation_is_rejected(self):
        raw=json.loads(NATIVE.read_text());raw["fork_turns"]="all"
        p=ROOT/"tests/fixtures/native-cloud-invalid.json";p.write_text(json.dumps(raw))
        try:
            with self.assertRaisesRegex(mod.Invalid,"must not inherit"):
                mod.validate(SPEC,p)
        finally:p.unlink(missing_ok=True)
    def test_missing_external_observer_boundary_is_rejected(self):
        raw=json.loads(NATIVE.read_text());raw["observer_owner"]="consumer"
        p=ROOT/"tests/fixtures/native-cloud-invalid.json";p.write_text(json.dumps(raw))
        try:
            with self.assertRaisesRegex(mod.Invalid,"observer"):
                mod.validate(SPEC,p)
        finally:p.unlink(missing_ok=True)
    def test_packet_never_claims_shared_storage_is_isolation(self):
        r=mod.project(SPEC,NATIVE)
        self.assertFalse(r["shared_storage_is_security_isolation"])

if __name__=="__main__": unittest.main()
