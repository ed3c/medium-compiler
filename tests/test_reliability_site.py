"""Static site contract for the browser-only reliability lab; not a browser drive."""
import json
import tempfile
import unittest
from pathlib import Path
from test_learning_site import site

ROOT=Path(__file__).resolve().parents[1]

class ReliabilitySiteTests(unittest.TestCase):
    def test_static_lab_is_built_and_scope_is_visible(self):
        with tempfile.TemporaryDirectory() as temp:
            output=Path(temp)/"dist"
            site.build(output)
            html=(output/"reliability/index.html").read_text()
            self.assertIn("SQLite-Wasm + OPFS",html)
            self.assertIn("Browser Worker",html)
            self.assertIn("不是多節點測試",html)
            self.assertIn("/assets/reliability/app.mjs",html)
            self.assertIn("/reliability/",(output/"articles/index.html").read_text())
            for name in ("app.mjs","browser-worker.mjs","logic.mjs","styles.css"):
                self.assertEqual((output/"assets/reliability"/name).read_bytes(),
                                 (ROOT/"site/reliability"/name).read_bytes())
            worker=(output/"assets/reliability/browser-worker.mjs").read_text()
            self.assertIn("OpfsDb",worker)
            self.assertIn("3.53.4-build2",worker)
            self.assertNotIn("Payment Provider API Key",worker)
    def test_cross_origin_isolation_is_scoped_to_lab(self):
        settings=json.loads((ROOT/"vercel.json").read_text())
        routes={x["source"]:x["headers"] for x in settings["headers"]}
        for path in ("/reliability/:path*","/assets/reliability/:path*"):
            headers={v["key"]:v["value"] for v in routes[path]}
            self.assertEqual(headers["Cross-Origin-Opener-Policy"],"same-origin")
            self.assertEqual(headers["Cross-Origin-Embedder-Policy"],"require-corp")
        self.assertNotIn("/:path*",routes)

if __name__=="__main__":
    unittest.main()
