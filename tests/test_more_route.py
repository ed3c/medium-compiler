import hashlib, importlib.util, json, tempfile, unittest
from html.parser import HTMLParser
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("more_route_site",ROOT/"scripts/build_site.py")
site=importlib.util.module_from_spec(spec);spec.loader.exec_module(site)
class MoreRouteSiteTests(unittest.TestCase):
    def test_source_and_bilingual_semantic_markers(self):
        m=json.loads((ROOT/"references/upstream/more-route-learning-sources.json").read_text())
        self.assertEqual(m["semantics"]["decision_count"],7)
        self.assertEqual(m["semantics"]["execution_claim"],"NOT_RUN")
        self.assertEqual(len(m["sources"]),2)
        for src in m["sources"]:
            self.assertEqual(len(src["revision"]),40)
            for section in src["selected_sections"]:self.assertIn(src["revision"],section["url"])
        self.assertEqual(m["sources"][1]["license"],"NOT_CONFIRMED")
        en=(ROOT/"articles/agent-handbook-zero-context.en.md").read_text()
        zh=(ROOT/"articles/agent-handbook-zero-context.md").read_text()
        for i in range(1,8):
            self.assertIn("## D"+str(i),en);self.assertIn("## D"+str(i),zh)
        for term in ("NOT_RUN","UNKNOWN","approval","readback"):self.assertIn(term,en)
        for term in ("NOT_RUN","UNKNOWN","核准","否定"):self.assertIn(term,zh)
    def test_decision_route_and_provenance(self):
        class Parser(HTMLParser):
            def __init__(self):super().__init__();self.choices=[];self.panels=[];self.graph_nodes=[];self.edges=[];self.scripts=[];self.css=[]
            def handle_starttag(self,tag,attrs):
                a=dict(attrs)
                if "data-mr-choice" in a:self.choices.append(a["data-mr-choice"])
                if "data-mr-panel" in a:self.panels.append(a["data-mr-panel"])
                if "data-mr-node" in a:self.graph_nodes.append(a["data-mr-node"])
                if "data-mr-edge" in a:self.edges.append(a["data-mr-edge"])
                if tag=="script" and a.get("src"):self.scripts.append(a["src"])
                if tag=="link" and a.get("rel")=="stylesheet":self.css.append(a["href"])
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/"dist";p=site.build(out)
            page=(out/"more-route/index.html").read_text()
            parser=Parser();parser.feed(page)
            self.assertEqual(parser.choices,["D"+str(i) for i in range(1,8)])
            self.assertEqual(parser.panels,["D"+str(i) for i in range(1,8)])
            self.assertEqual(parser.graph_nodes,["D"+str(i) for i in range(1,8)])
            self.assertEqual(parser.edges,["D1:D2","D2:D3","D3:D4","D1:D5","D4:D5","D2:D6","D5:D6","D6:D7"])
            for edge in parser.edges:
                parent, child=edge.split(":")
                self.assertIn(parent,parser.graph_nodes)
                self.assertIn(child,parser.graph_nodes)
                self.assertLess(int(parent[1:]),int(child[1:]))
            self.assertIn("/assets/more-route.js",parser.scripts)
            self.assertIn("/assets/more-route.css",parser.css)
            self.assertNotIn(" hidden",page)
            for path in ("index.html","learning/index.html","articles/agent-handbook-zero-context/index.html"):
                self.assertIn("/more-route/",(out/path).read_text())
            self.assertEqual((out/"more-route/source.json").read_bytes(),
                (ROOT/"references/upstream/more-route-learning-sources.json").read_bytes())
            self.assertEqual(p["more_route"]["decision_count"],7)
            self.assertEqual(p["more_route"]["manifest_sha256"],hashlib.sha256((out/"more-route/source.json").read_bytes()).hexdigest())
            self.assertEqual((out/"articles/agent-handbook-zero-context/article.en.md").read_bytes(),
                (ROOT/"articles/agent-handbook-zero-context.en.md").read_bytes())
            for asset in ("more-route.js","more-route.css"):
                self.assertEqual((out/"assets"/asset).read_bytes(),(ROOT/"site/more-route"/asset).read_bytes())
