"""Mechanical source/visual routing consistency, not a semantic reviewer."""
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
def read(path):
    return (ROOT/path).read_text(encoding='utf-8')

class VisualArchitectureTests(unittest.TestCase):
    def test_router_points_to_original_owners(self):
        table=read('docs/visual-architecture.md')
        for fragment in (
          'ARC-01 A','ARC-02 A','Soodles','Noodle',
          'DuckDB-Wasm','Pyodide','SeeCode','oh-my-mermaid',
          'PaperBanana','Typed Code Explorer','Source-bound',
          'NOT_RUN','NOT_IMPLEMENTED','NOT_ACCEPTED',
          'docs/public-loop-graph.md',
          'apps/loop-workbench/src/public-artifact.mjs',
          'scripts/article_diagrams.py'):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment,table)
        self.assertEqual(table.count('# Unified Visual Architecture'),1)
        for file in ('site/loop-graph-layout.mjs','apps/loop-workbench/vendor/noodle/loop-panorama.mjs',
                     'apps/loop-workbench/src/routes/panorama.tsx',
                     'apps/loop-workbench/src/public-artifact.mjs',
                     'scripts/loop_graph_site.py','scripts/build_site.py',
                     'scripts/article_diagrams.py','scripts/ai_evals_site.py',
                     'apps/loop-workbench/src/learning-store.ts',
                     'design/diagram-authoring.lock.json',
                     'docs/diagram-authoring.md','docs/learning-duckdb-architecture.md'):
            with self.subTest(path=file):
                self.assertTrue((ROOT/file).is_file(),file)
    def test_public_artifact_documentation_matches_actual_reader(self):
        actual=read('apps/loop-workbench/src/routes/panorama.tsx')
        reader=read('apps/loop-workbench/src/public-artifact.mjs')
        publisher=read('scripts/loop_graph_site.py')
        doc=read('docs/viewenv-unified-panorama.md')
        self.assertIn('readReviewedArtifact(',actual)
        self.assertIn('snapshot.content_urls[id]',reader)
        self.assertIn('payload.byteLength !== ref.bytes',reader)
        self.assertIn('cryptoImpl.subtle.digest',reader)
        self.assertIn("artifact.pop('public_content', None)",publisher)
        self.assertNotIn('already-reviewed inline public content',doc.replace('\n',' '))
        self.assertIn('readReviewedArtifact',doc)
        self.assertNotIn('must be integrated and browser-verified before product acceptance',read('apps/loop-workbench/README.md'))
    def test_frozen_scope_and_public_promotion_are_not_fabricated(self):
        for file in ('AGENTS.md','.agents/skills/loop-visual-design/SKILL.md',
                     '.agents/skills/viewenv/SKILL.md',
                     '.agents/skills/medium-writing/SKILL.md',
                     'docs/visualization-integration.md'):
            with self.subTest(file=file):
                self.assertIn('visual-architecture.md',read(file))
        self.assertIn('ARC-02 A',read('docs/diagram-authoring.md'))
        for item in json.loads(read('design/diagram-candidates/manifest.json'))['items']:
            self.assertEqual(item['status'],'candidate')
            self.assertIsNone(item['review_receipt'])
        self.assertEqual(json.loads(read('references/article-diagrams.json'))['items'],[])
        self.assertIn('no cloud push',read('docs/visual-architecture.md').lower())
        self.assertIn('Draft',read('docs/visual-architecture.md'))
    def test_cloudflare_faithful_port_reference_is_source_bound_not_runtime_admission(self):
        import json
        research=read('docs/typescript-rust-port-integration.md')
        handoff=read('docs/handoff.md')
        architecture=read('docs/visual-architecture.md')
        for fragment in ('blog.cloudflare.com/typescript-rust-port',
                         'oxc-project/tsrs',
                         'cloudflare/vinext',
                         '0341578031c47ecf555a35492554b4d212d07459',
                         '9fcbed8634be6ba3cadfb1383153963febb5456f',
                         'NOT_RUN','NOT_IMPLEMENTED','NOTICE'):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment,research)
                self.assertIn(fragment,handoff if fragment != 'NOTICE' else research)
        self.assertIn('typescript-rust-port-integration.md',architecture)
        self.assertIn('typescript-rust-port-integration.md',read('AGENTS.md'))
        package=json.loads(read('apps/loop-workbench/package.json'))
        self.assertEqual(package['devDependencies']['typescript'],'npm:@typescript/typescript6@6.0.2')
        self.assertEqual(package['devDependencies']['@typescript/native'],'npm:typescript@7.0.2')
        self.assertEqual(package['devDependencies']['@tsrs/wasm'],'0.18.0-ts7.1.0-dev.20260929')
        self.assertNotIn('tsrs',package['dependencies'])
        self.assertNotIn('@tsrs/wasm',package['dependencies'])
        self.assertIn('typescript-rust-port-integration.md',read('docs/visual-architecture.md'))
        self.assertIn('same upstream TypeScript commit',research)
        self.assertIn('isolated dev-only tsrs WASM smoke',research)

    def test_no_new_runtime_authority_from_visual_router(self):
        router=read('.agents/skills/loop-visual-design/SKILL.md')
        self.assertIn('No new P-class conditions, Graph schema, cross-repo scan, Production deployment',router)
        self.assertIn('does not produce runtime truth',router)
        routes=read('apps/loop-workbench/src/routes/panorama.tsx')
        self.assertNotIn('fetch("http://localhost',routes)
        self.assertNotIn('method: "POST"',routes)

if __name__=='__main__':
    unittest.main()
