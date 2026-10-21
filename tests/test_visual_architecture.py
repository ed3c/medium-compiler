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
        self.assertNotIn('already-reviewed\\ninline public content',doc)
        self.assertIn('readReviewedArtifact',doc)
        self.assertNotIn('The native renderer and its source\\nidentity must be integrated',read('apps/loop-workbench/README.md'))
    def test_frozen_scope_and_public_promotion_are_not_fabricated(self):
        for file in ('AGENTS.md','.agents/skills/loop-visual-design/SKILL.md',
                     '.agents/skills/viewenv/SKILL.md',
                     '.agents/skills/medium-writing/SKILL.md',
                     'docs/visualization-integration.md'):
            with self.subTest(file=file):
                self.assertIn('visual-architecture.md',read(file))
        self.assertIn('ARC-02 A',read('docs/diagram-authoring.md'))
        self.assertEqual(json.loads(read('design/diagram-candidates/manifest.json'))['items'],[])
        self.assertEqual(json.loads(read('references/article-diagrams.json'))['items'],[])
        self.assertIn('no Cloud Push',read('docs/visual-architecture.md'))
        self.assertIn('Draft',read('docs/visual-architecture.md'))
    def test_no_new_runtime_authority_from_visual_router(self):
        router=read('.agents/skills/loop-visual-design/SKILL.md')
        self.assertIn('no',router.lower())
        self.assertIn('does not produce runtime truth',router)
        routes=read('apps/loop-workbench/src/routes/panorama.tsx')
        self.assertNotIn('fetch("http://localhost',routes)
        self.assertNotIn('method: "POST"',routes)

if __name__=='__main__':
    unittest.main()
