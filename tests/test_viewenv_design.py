import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
module_spec = importlib.util.spec_from_file_location("design",
    ROOT / "scripts/viewenv_design.py")
design = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(design)


class ViewEnvDesignTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "design").mkdir()
        source_lock = json.loads((ROOT / "design/visual-skills.lock.json").read_text())
        (self.root / "design/visual-skills.lock.json").write_text(json.dumps(source_lock))
        (self.root / "task.txt").write_text("original observed task", encoding="utf-8")
        self.request = {"mode":"operations","source":"task.txt",
                        "goal":"Read original occurrence","reviews":[]}

    def test_source_identity_and_skill_selection(self):
        result = design.compile_design(self.request, self.root)
        self.assertEqual("planned",result["status"])
        self.assertEqual("impeccable",result["primary_skill"])
        self.assertEqual(64,len(result["source"]["sha256"]))
        self.assertFalse(result["execution_authority"])
        self.assertFalse(result["skill_invoked"])

    def test_all_routes_are_explicit_and_secondary_on_demand(self):
        cases={"public_story":"taste-skill","mechanism":"anatomy",
               "motion_audit":"emil-design-eng","annotation":"build-review-interface"}
        for mode,skill in cases.items():
            req={**self.request, "mode":mode}
            self.assertEqual(skill,design.compile_design(req,self.root)["primary_skill"])
        x=design.compile_design({**self.request,"reviews":["motion_review"]},self.root)
        self.assertEqual(["review-animations"],x["secondary_skills"])

    def test_refuse_symlink_escape_and_undeclared_review(self):
        (self.root/"alias").symlink_to(self.root/"task.txt")
        for source in ("alias","../escape","/tmp/task.txt"):
            with self.assertRaises(ValueError):
                design.compile_design({**self.request,"source":source},self.root)
        with self.assertRaises(ValueError):
            design.compile_design({**self.request,"reviews":["execute_harness"]},self.root)

    def test_changed_source_changes_pin_no_claim(self):
        x=design.compile_design(self.request,self.root)
        (self.root/"task.txt").write_text("new content")
        y=design.compile_design(self.request,self.root)
        self.assertNotEqual(x["source"]["sha256"],y["source"]["sha256"])
        self.assertEqual("planned",y["status"])


if __name__ == "__main__":
    unittest.main()
