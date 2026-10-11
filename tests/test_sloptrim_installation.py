"""Verify the repository-local sloptrim installation matches its pinned upstream source."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".agents/skills/sloptrim"
LOCK = ROOT / "references/upstream/sloptrim-lock.json"


class SloptrimInstallationTests(unittest.TestCase):
    def test_upstream_blobs_and_complete_file_set(self):
        lock = json.loads(LOCK.read_text(encoding="utf-8"))
        self.assertEqual(lock["repository"], "seyedehsanhadi/sloptrim")
        self.assertEqual(lock["revision"], "38dbb7cb4e97de0b9bf157903c95bdcab016dda2")
        self.assertEqual(lock["version"], "0.9.4")
        expected = set()
        for entry in lock["files"]:
            expected.add((ROOT / entry["path"]).relative_to(SKILL).as_posix())
            if entry["source_path"] == "SKILL.md":
                path = ROOT / lock["project_customization"]["upstream_skill_copy"]
            else:
                path = ROOT / entry["path"]
            data = path.read_bytes()
            blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
            self.assertEqual(blob, entry["git_blob"], entry["source_path"])
        actual = {p.relative_to(SKILL).as_posix() for p in SKILL.rglob("*") if p.is_file()}
        self.assertEqual(actual, expected)
        local = lock["project_customization"]
        original = (ROOT / local["upstream_skill_copy"]).read_bytes()
        customized = (ROOT / local["active_skill_path"]).read_bytes()
        self.assertTrue(customized.startswith(original))
        supplement = customized[len(original):]
        self.assertTrue(supplement.startswith(b"\n\n## Medium-compiler reader-article editorial supplement"))
        self.assertIn(b"Do **not** remove:", supplement)
        self.assertIn(b"Never apply it to P-class guidance", supplement)
        blob = hashlib.sha1(
            b"blob " + str(len(customized)).encode() + b"\0" + customized
        ).hexdigest()
        self.assertEqual(blob, local["active_git_blob"])

    def test_detector_runs_without_external_dependencies(self):
        detector = SKILL / "scripts/detect.py"
        sample = "In today's rapidly evolving landscape, this solution will unlock a new era."
        result = subprocess.run(
            [sys.executable, str(detector)], input=sample, text=True,
            capture_output=True, check=True, timeout=15,
        )
        parsed = json.loads(result.stdout)
        self.assertIn("_metrics", parsed)
        self.assertIn("ai_tell_score", parsed["_metrics"])


if __name__ == "__main__":
    unittest.main()
