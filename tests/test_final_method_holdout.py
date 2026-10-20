"""Replay observed article solutions, not model generation or prose grading."""
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKETS = (
    (ROOT / "evals/writing/leetcode-final-method-holdout", ("islands", "intervals")),
    (ROOT / "evals/writing/leetcode-route-closure", ("temperatures", "subsets")),
    (ROOT / "evals/writing/leetcode-cost-premises", ("container", "courses")),
)


class FinalMethodHoldoutTests(unittest.TestCase):
    def test_frozen_article_solutions_against_independent_definitions(self):
        for packet, cases in PACKETS:
            spec = importlib.util.spec_from_file_location("holdout_runtime", packet / "runtime_controls.py")
            controls = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(controls)
            for case in cases:
                with self.subTest(packet=packet.name, case=case):
                    results = controls.check(case)
                    self.assertTrue(results)
                    for result in results:
                        self.assertEqual(result["failures"], [])
                        self.assertEqual(result["passed"], result["checks"])

    def test_reader_evidence_keeps_raw_gaps_and_audited_quote_errors(self):
        for packet, cases in PACKETS:
            questions = json.loads((packet / "reader-questions.json").read_text())
            expected_ids = {q["id"] for q in questions["questions"]}
            audits = json.loads((packet / "quote-audit.json").read_text())
            audit_by_quote = {(a["case"], a["answer_id"], a["quote_index"]): a for a in audits}
            used_audits = set()
            for case in (*cases, "cost-control"):
                directory = packet / case
                output = directory / ("output.json" if case == "cost-control" else "reader.raw.json")
                result = json.loads(output.read_text())
                articles = {lang: (directory / f"article.{lang}.md").read_text()
                            for lang in ("en", "zh-TW")}
                ids = [a["id"] for a in result["answers"]]
                self.assertEqual(len(ids), len(set(ids)))
                self.assertEqual(set(ids), {"cost"} if case == "cost-control" else expected_ids)
                self.assertEqual(set(result["unanswered_question_ids"]),
                                 {a["id"] for a in result["answers"] if a["missing"]})
                # A gap is retained evidence, not a reason to fail this mechanical check.
                for answer in result["answers"]:
                    self.assertTrue(answer["quotes"])
                    for index, quote in enumerate(answer["quotes"]):
                        with self.subTest(packet=packet.name, case=case, answer=answer["id"], quote=index):
                            article = articles[quote["language"]]
                            if quote["text"] in article:
                                continue
                            key = (case, answer["id"], index)
                            self.assertIn(key, audit_by_quote)
                            audit = audit_by_quote[key]
                            self.assertEqual(audit["raw_quote"], quote["text"])
                            self.assertIn(audit["exact_article_passage"], article)
                            used_audits.add(key)
            self.assertEqual(used_audits, set(audit_by_quote))


if __name__ == "__main__":
    unittest.main()
