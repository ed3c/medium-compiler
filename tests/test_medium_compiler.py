from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import medium_compiler as mc  # noqa: E402


class MediumCompilerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.spec_path = self.root / "spec.json"
        self.run_dir = self.root / "run"
        self.spec = {
            "topic": "fixture topic",
            "claims": [
                {
                    "id": f"C{stage}",
                    "stage": stage,
                    "description": f"claim for stage {stage}",
                    "protected_literals": [f"exact-{stage}"],
                }
                for stage in range(1, 6)
            ],
            "terms": [
                {
                    "id": "T1",
                    "canonical": "canonical key",
                    "first_stage": 3,
                    "forbidden_variants": ["標準鍵值"],
                }
            ],
        }
        self.spec_path.write_text(
            json.dumps(self.spec, ensure_ascii=False), encoding="utf-8"
        )
        mc.init_run(self.spec_path, self.run_dir)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _coverage(self, stage: int, *, claims=None, terms=None, elements=None) -> Path:
        value = {
            "elements": elements
            if elements is not None
            else list(mc.STAGE_ELEMENTS[stage]),
            "claims": claims
            if claims is not None
            else ([f"C{stage}"] if 1 <= stage <= 5 else []),
            "terms": terms if terms is not None else (["T1"] if stage == 3 else []),
        }
        path = self.root / f"coverage-{stage}.json"
        path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
        return path

    def _text(self, stage: int) -> str:
        if stage == 0:
            return "# TOC\n\nDecision map\n\n\`\`\`text\ninput -> output\n\`\`\`\n"
        text = f"## Stage {stage}\n\nexact-{stage}\n"
        if stage == 3:
            text += "\ncanonical key\n"
        if stage == 4:
            text += "\n\`\`\`python\nprint('protected')\n\`\`\`\n"
        return text

    def _submit(self, stage: int, text: str | None = None, coverage: Path | None = None):
        input_path = self.root / f"stage-{stage}.md"
        input_path.write_text(text if text is not None else self._text(stage), encoding="utf-8")
        return mc.submit_stage(
            self.run_dir,
            stage,
            input_path,
            coverage if coverage is not None else self._coverage(stage),
        )

    def _through_stage5(self) -> None:
        for stage in range(0, 6):
            self._submit(stage)

    def test_init_exposes_stage_zero(self):
        action = mc.next_action(self.run_dir)
        self.assertEqual(action["next_stage"], 0)
        self.assertEqual(
            set(action["required_elements"]),
            {"toc", "decision_map", "runtime_map"},
        )

    def test_stage_skip_is_refused(self):
        with self.assertRaisesRegex(mc.CompilerError, "out-of-order"):
            self._submit(1)

    def test_dropped_claim_coverage_is_refused(self):
        self._submit(0)
        bad = self._coverage(1, claims=[])
        with self.assertRaisesRegex(mc.CompilerError, "claim coverage"):
            self._submit(1, coverage=bad)

    def test_term_drift_is_refused(self):
        self._submit(0)
        self._submit(1)
        self._submit(2)
        with self.assertRaisesRegex(mc.CompilerError, "technical term drift"):
            self._submit(3, text="exact-3\ncanonical key\n標準鍵值\n")

    def test_missing_canonical_term_is_refused(self):
        self._submit(0)
        self._submit(1)
        self._submit(2)
        with self.assertRaisesRegex(mc.CompilerError, "missing canonical term"):
            self._submit(3, text="exact-3\n")

    def test_semantic_draft_excludes_stage_zero(self):
        self._through_stage5()
        draft = (self.run_dir / "semantic-draft.md").read_text(encoding="utf-8")
        self.assertNotIn("# TOC", draft)
        self.assertIn("exact-1", draft)
        self.assertIn("exact-5", draft)

    def test_copyedit_must_preserve_fenced_blocks(self):
        self._through_stage5()
        draft = (self.run_dir / "semantic-draft.md").read_text(encoding="utf-8")
        mutated = draft.replace("print('protected')", "print('changed')")
        with self.assertRaisesRegex(mc.CompilerError, "changed fenced"):
            self._submit(6, text=mutated)

    def test_copyedit_must_preserve_exact_literals(self):
        self._through_stage5()
        draft = (self.run_dir / "semantic-draft.md").read_text(encoding="utf-8")
        mutated = draft.replace("exact-2", "rewritten")
        with self.assertRaisesRegex(mc.CompilerError, "dropped protected literal"):
            self._submit(6, text=mutated)

    def test_copyedit_must_preserve_canonical_terms(self):
        self._through_stage5()
        draft = (self.run_dir / "semantic-draft.md").read_text(encoding="utf-8")
        mutated = draft.replace("canonical key", "another phrase")
        with self.assertRaisesRegex(mc.CompilerError, "dropped canonical"):
            self._submit(6, text=mutated)

    def test_assembly_is_exact_stage6_bytes(self):
        self._through_stage5()
        draft = (self.run_dir / "semantic-draft.md").read_text(encoding="utf-8")
        self._submit(6, text=draft)
        result = mc.assemble(self.run_dir)
        self.assertEqual(result["status"], "ASSEMBLED")
        self.assertEqual(
            (self.run_dir / "medium-canonical.md").read_bytes(),
            (self.run_dir / "parts/stage-06.md").read_bytes(),
        )

    def test_machine_sidecar_is_refused_at_assembly(self):
        self._through_stage5()
        draft = (self.run_dir / "semantic-draft.md").read_text(encoding="utf-8")
        self._submit(6, text=draft + "\n<!-- RUN_STATE {} -->\n")
        with self.assertRaisesRegex(mc.CompilerError, "machine sidecar"):
            mc.assemble(self.run_dir)

    def test_stale_receipt_is_refused_after_article_change(self):
        self._through_stage5()
        draft = (self.run_dir / "semantic-draft.md").read_text(encoding="utf-8")
        self._submit(6, text=draft)
        mc.assemble(self.run_dir)
        mc.build_receipt(self.run_dir)
        canonical = self.run_dir / "medium-canonical.md"
        canonical.write_text(canonical.read_text(encoding="utf-8") + "\nmanual drift\n", encoding="utf-8")
        with self.assertRaisesRegex(mc.CompilerError, "article bytes changed"):
            mc.check_receipt(self.run_dir)

    def test_receipt_is_valid_for_untouched_artifacts(self):
        self._through_stage5()
        draft = (self.run_dir / "semantic-draft.md").read_text(encoding="utf-8")
        self._submit(6, text=draft)
        mc.assemble(self.run_dir)
        mc.build_receipt(self.run_dir)
        result = mc.check_receipt(self.run_dir)
        self.assertEqual(result["status"], "VALID")
        self.assertEqual(result["semantic_correctness"], "NOT_ASSESSED")

    def test_style_lint_is_advisory(self):
        path = self.root / "article.md"
        path.write_text(
            "本文將介紹一件事。\n\n這一階段的產物是測試。\n", encoding="utf-8"
        )
        result = mc.style_lint(path)
        self.assertGreaterEqual(result["finding_count"], 2)
        self.assertFalse(result["blocking"])


if __name__ == "__main__":
    unittest.main()
