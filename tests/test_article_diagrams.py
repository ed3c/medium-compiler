import hashlib, importlib.util, json, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('article_diagrams',ROOT/'scripts/article_diagrams.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
site_spec=importlib.util.spec_from_file_location('article_site',ROOT/'scripts/build_site.py')
site=importlib.util.module_from_spec(site_spec);site_spec.loader.exec_module(site_spec)
SAMPLE='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 40"><rect x="2" y="2" width="116" height="36" rx="8"/><text x="12" y="26">Goal</text></svg>'
CODE='flowchart LR\n  Goal --> Verify'

class ArticleDiagramTests(unittest.TestCase):
    def fixture(self, folder):
        root=Path(folder);(root/'references').mkdir();(root/'site/article-diagrams').mkdir(parents=True)
        sha=hashlib.sha256(SAMPLE.encode()).hexdigest()
        (root/'site/article-diagrams'/f'{sha}.svg').write_text(SAMPLE)
        rows=[{'source':'articles/flow.md','ordinal':0,
               'mermaid_sha256':hashlib.sha256(CODE.encode()).hexdigest(),
               'svg_sha256':sha,'alt':'Evidence flow','reviewed':True}]
        (root/'references/article-diagrams.json').write_text(
          json.dumps({'schema_version':'article-diagram-registry@1','items':rows}))
        return root,sha

    def test_exact_mermaid_block_to_static_reviewed_figure(self):
        with tempfile.TemporaryDirectory() as d:
            root,sha=self.fixture(d)
            registry=mod.DiagramRegistry(root)
            projection=registry.for_article('articles/flow.md')
            markup=site.markdown('# Source\n\n'+chr(96)*3+'mermaid\n'+CODE+'\n'+chr(96)*3,projection)
            projection.check_complete()
            self.assertIn('/assets/article-diagrams/'+sha+'.svg',markup)
            self.assertIn('Evidence flow',markup)
            self.assertNotIn('<pre><code>flowchart',markup)
            registry.install_assets(root/'output')
            self.assertTrue((root/'output/assets/article-diagrams'/f'{sha}.svg').exists())

    def test_wrong_source_missing_output_and_inline_scripts_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            root,sha=self.fixture(d)
            p=mod.DiagramRegistry(root).for_article('articles/flow.md')
            with self.assertRaisesRegex(ValueError,'MERMAID_SOURCE_DRIFT'):
                p.figure('flowchart LR\n  Goal --> Accept',0)
            with self.assertRaisesRegex(ValueError,'UNREGISTERED_MERMAID_BLOCK'):
                p.figure(CODE,1)
            bad='<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>'
            (root/'site/article-diagrams'/f'{sha}.svg').write_text(bad)
            with self.assertRaisesRegex(ValueError,'SVG_DIGEST_DRIFT'):
                p.figure(CODE,0)
            with self.assertRaisesRegex(ValueError,'UNSAFE_SVG_ELEMENT'):
                mod.check_svg(bad.encode())

    def test_unregistered_ordinary_code_and_article_source_remain_unchanged(self):
        self.assertIn('<pre><code>',site.markdown(''+chr(96)*3+'python\nprint(1)\n'+chr(96)*3))
        self.assertEqual(mod.DiagramRegistry(ROOT).items,[])
if __name__=='__main__':unittest.main()
