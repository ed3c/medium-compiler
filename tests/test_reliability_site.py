"""Static site contract for the browser-only reliability lab; not a browser drive."""
import hashlib
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
            self.assertIn('from "./sqlite/index.mjs"',worker)
            lock=json.loads((ROOT/'references/sqlite-wasm-lock.json').read_text())
            self.assertEqual(lock['version'],'3.53.4-build2')
            for name,digest in lock['files'].items():
                asset=output/'assets/reliability/sqlite'/name
                self.assertEqual(hashlib.sha256(asset.read_bytes()).hexdigest(),digest)
            self.assertNotIn("Payment Provider API Key",worker)
    def test_cross_origin_isolation_is_scoped_to_lab(self):
        settings=json.loads((ROOT/"vercel.json").read_text())
        routes={x["source"]:x["headers"] for x in settings["headers"]}
        for path in ("/reliability/","/reliability/:path*","/assets/reliability/:path*"):
            headers={v["key"]:v["value"] for v in routes[path]}
            self.assertEqual(headers["Cross-Origin-Opener-Policy"],"same-origin")
            self.assertEqual(headers["Cross-Origin-Embedder-Policy"],"require-corp")
        self.assertNotIn("/:path*",routes)

    def test_cloudflare_subsite_keeps_assets_local_and_total_site_on_vercel(self):
        import importlib.util
        import sys
        sys.path.insert(0,str(ROOT/'scripts'))
        spec=importlib.util.spec_from_file_location('lab_build',ROOT/'scripts/build_reliability_site.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)/'lab';module.build(out)
            page=(out/'reliability/index.html').read_text()
            self.assertIn('href="https://medium-compiler.vercel.app/"',page)
            self.assertIn('href="https://medium-compiler.ga874199.workers.dev/reliability/"',page)
            self.assertIn('src="/assets/reliability/app.mjs"',page)
            self.assertTrue((out/'assets/reliability/sqlite/sqlite3.wasm').exists())
            self.assertFalse((out/'articles').exists())
            self.assertFalse((out/'cefr-alg-c2').exists())
            self.assertIn('/ https://medium-compiler.vercel.app/ 302',(out/'_redirects').read_text())
            self.assertEqual((out/'_headers').read_bytes(),(ROOT/'site/_headers').read_bytes())

if __name__=="__main__":
    unittest.main()
