"""Source-only controls: design skill install manifest does not grant execution."""
import contextlib
import io
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import install_loop_design_skills as module

class InstallPlanTests(unittest.TestCase):
    def test_pins_are_full_and_paths_are_project_local(self):
        plan = module.load_plan()
        self.assertEqual([x["id"] for x in plan["sources"]],
                         ["taste","anatomy","impeccable","emil"])
        for source in plan["sources"]:
            self.assertEqual(len(source["commit"]),40)
            self.assertTrue(source["destination"].startswith(".agents/skills/"))

    def test_plan_has_no_install_effect(self):
        with contextlib.redirect_stdout(io.StringIO()) as stream:
            code = module.main(["--plan"])
        self.assertEqual(code, 0)
        data = json.loads(stream.getvalue())
        self.assertEqual(data["status"], "PLAN_ONLY")
        self.assertNotIn("FILES_INSTALLED",stream.getvalue())

if __name__ == "__main__":
    unittest.main()
