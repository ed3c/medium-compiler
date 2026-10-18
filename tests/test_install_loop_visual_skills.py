"""Offline, no-network tests for the pinned design skill installer."""
import importlib.util
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("visual_install", ROOT / "scripts/install_loop_visual_skills.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def archive(members):
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as tar:
        for name, content in members.items():
            payload = content.encode()
            info = tarfile.TarInfo("pinned-upstream/" + name)
            info.size = len(payload)
            tar.addfile(info, io.BytesIO(payload))
    return buffer.getvalue()


class DesignInstallerTests(unittest.TestCase):
    def test_select_taste_and_preserve_skill_source(self):
        source = {"id":"taste","repo":"Example/taste","sha":"a"*40,
                  "license":"MIT","source":"skills/taste-skill","targets":["taste-skill"]}
        members = module.extracted_files(archive({
            "skills/taste-skill/SKILL.md":"---\\nname: test\\n---",
            "skills/taste-skill/references/example.md":"a",
            "LICENSE":"MIT"}), source)
        result = module.selected_skills(source, members)
        self.assertIn("taste-skill", result)
        self.assertIn(module.PurePosixPath("references/example.md"), result["taste-skill"])
        self.assertIn(module.PurePosixPath(".upstream-provenance.json"), result["taste-skill"])

    def test_refuse_tar_symlink(self):
        b = io.BytesIO()
        with tarfile.open(fileobj=b, mode="w:gz") as tar:
            info = tarfile.TarInfo("pinned-upstream/skills/link")
            info.type = tarfile.SYMTYPE
            info.linkname = "../../private"
            tar.addfile(info)
        with self.assertRaisesRegex(ValueError, "symlink"):
            module.extracted_files(b.getvalue(), {"id":"test"})

    def test_refuse_incomplete_skill(self):
        source = {"id":"taste","repo":"Example/taste","sha":"a"*40,
                  "license":"MIT","source":"skills/taste-skill","targets":["taste-skill"]}
        with self.assertRaisesRegex(ValueError, "SKILL.md"):
            module.selected_skills(source, {module.PurePosixPath("skills/taste-skill/README.md"):b"hello"})

    def test_pins_and_licenses(self):
        lock = json.loads((ROOT / "design/visual-skills.lock.json").read_text())
        self.assertEqual(4, len(lock["sources"]))
        for entry in lock["sources"]:
            self.assertRegex(entry["sha"], r"^[0-9a-f]{40}$")
            self.assertIn(entry["license"], ("MIT", "Apache-2.0"))


if __name__ == "__main__":
    unittest.main()
