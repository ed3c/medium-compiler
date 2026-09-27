import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from html.parser import HTMLParser

from test_learning_site import site, ROOT

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = []
    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.hrefs.extend(value for key, value in attrs if key == "href")

class ColabArticleTests(unittest.TestCase):
    def test_notebook_runs_in_order_and_matches_article_code(self):
        notebook = json.loads((ROOT / "notebooks/application-engineering-colab.ipynb").read_text())
        article = (ROOT / "articles/application-engineering-colab.md").read_text()
        cells = [c for c in notebook["cells"] if c["cell_type"] == "code"]
        for cell in cells:
            self.assertIsNone(cell["execution_count"])
            self.assertEqual(cell["outputs"], [])
            self.assertIn("".join(cell["source"]).strip(), article)
        code = "\n".join("".join(c["source"]) for c in cells)
        with tempfile.TemporaryDirectory() as td:
            result = subprocess.run([sys.executable, "-c", code], cwd=td, capture_output=True, text=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("3 tests passed", result.stdout)
            receipt = json.loads((Path(td) / "environment-check.json").read_text())
            self.assertEqual(receipt["input"], [1, 2, 3])
            self.assertEqual(receipt["result"], 14)
            self.assertEqual(receipt["scope"], "environment-and-example-only")
            bad = code.replace("return sum(value * value for value in values)", "return 14")
            failed = subprocess.run([sys.executable, "-c", bad], cwd=td, capture_output=True, text=True, timeout=20)
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn("AssertionError", failed.stderr)

    def test_built_navigation_provenance_and_notebook_are_complete(self):
        import hashlib
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "dist"
            provenance = site.build(out)
            for route in ("index.html", "learning/index.html", "articles/index.html"):
                self.assertIn("/articles/application-engineering-colab/", (out / route).read_text())
            guide = (out / "articles/application-engineering-colab/index.html").read_text()
            self.assertIn("3 tests passed", guide)
            self.assertIn("Colab", guide)
            source = ROOT / "articles/application-engineering-colab.md"
            entry = next(a for a in provenance["articles"] if a["source"] == str(source.relative_to(ROOT)))
            self.assertEqual(entry["sha256"], hashlib.sha256(source.read_bytes()).hexdigest())
            self.assertEqual((out / "notebooks/application-engineering-colab.ipynb").read_bytes(),
                             (ROOT / "notebooks/application-engineering-colab.ipynb").read_bytes())
            for file in out.rglob("*.html"):
                links = Links(); links.feed(file.read_text())
                for href in links.hrefs:
                    if href.startswith("/"):
                        target = out / href.lstrip("/")
                        if href.endswith("/"):
                            target = target / "index.html"
                        self.assertTrue(target.is_file(), (file, href))

