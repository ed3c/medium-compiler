import hashlib,importlib.util,json,tempfile,unittest
from pathlib import Path,PurePosixPath
ROOT=Path(__file__).resolve().parents[1]
def load(name):
  spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/name)
  module=importlib.util.module_from_spec(spec)
  spec.loader.exec_module(module)
  return module
installer=load('install_diagram_authoring.py')
checker=load('verify_diagram_candidates.py')
def digest(data):return hashlib.sha256(data).hexdigest()
class VisualAuthoringTests(unittest.TestCase):
  def test_pins_are_exclusive_and_omm_push_is_not_selected(self):
    lock=json.loads((ROOT/'design/diagram-authoring.lock.json').read_text())
    self.assertEqual({x['repo'] for x in lock['sources']},
      {'Aryanutkarsh/SeeCode','oh-my-mermaid/oh-my-mermaid'})
    self.assertTrue(all(len(x['sha'])==40 for x in lock['sources']))
    sample={PurePosixPath('LICENSE'):b'MIT License\n',
      PurePosixPath('skills/omm-scan/SKILL.md'):b'scan',
      PurePosixPath('skills/omm-view/SKILL.md'):b'view',
      PurePosixPath('skills/omm-push/SKILL.md'):b'push'}
    selected=installer.select(lock['sources'][1],sample)
    self.assertEqual(set(selected),{'omm-scan','omm-view'})
  def test_omm_candidate_needs_exact_source_and_review_metadata(self):
    with tempfile.TemporaryDirectory() as td:
      root=Path(td);(root/'site').mkdir();(root/'docs/derived-architecture').mkdir(parents=True)
      a=b'export function sample() {}\n';b=b'graph LR\n  a -->|source| b\n'
      (root/'site/sample.mjs').write_bytes(a)
      (root/'docs/derived-architecture/diagram.mmd').write_bytes(b)
      entry={'kind':'omm-architecture','source':'site/sample.mjs','source_sha256':digest(a),
        'candidate':'docs/derived-architecture/diagram.mmd','candidate_sha256':digest(b),
        'status':'candidate','loss_report':[],'review_receipt':None}
      document={'schema_version':checker.SCHEMA,'items':[entry]}
      self.assertEqual(checker.check(root,document)['reviewed_claims'],0)
      entry['status']='reviewed'
      with self.assertRaisesRegex(ValueError,'MISSING_REVIEW_METADATA'):checker.check(root,document)
      entry['review_receipt']={'reviewer':'reviewer-not-a-native-oracle',
         'source_sha256':digest(a),'candidate_sha256':digest(b)}
      self.assertEqual(checker.check(root,document)['reviewed_claims'],1)
      (root/'site/sample.mjs').write_bytes(a+b'changed\n')
      with self.assertRaisesRegex(ValueError,'SOURCE_DIGEST_DRIFT'):checker.check(root,document)
  def test_editorial_must_have_system_fonts_and_source_binding(self):
    with tempfile.TemporaryDirectory() as td:
      root=Path(td);(root/'docs').mkdir();(root/'design/diagram-candidates').mkdir(parents=True)
      a=b'An approved source paragraph';source='docs/source.md'
      spec={'type':'flowchart','fonts':'system','motion':'step',
        'evidence':[{'id':'article','file':source,'line':1}]}
      b=json.dumps(spec).encode()
      (root/source).write_bytes(a)
      (root/'design/diagram-candidates/figure.json').write_bytes(b)
      entry={'kind':'seecode-editorial','source':source,'source_sha256':digest(a),
        'candidate':'design/diagram-candidates/figure.json','candidate_sha256':digest(b),
        'status':'candidate','loss_report':[],'review_receipt':None}
      doc={'schema_version':checker.SCHEMA,'items':[entry]}
      checker.check(root,doc)
      spec['fonts']='google'
      raw=json.dumps(spec).encode()
      (root/'design/diagram-candidates/figure.json').write_bytes(raw)
      entry['candidate_sha256']=digest(raw)
      with self.assertRaisesRegex(ValueError,'EXTERNAL_RESOURCE_OR_MOTION'):checker.check(root,doc)
  def test_checked_in_registry_has_no_fake_review(self):
    doc=json.loads((ROOT/'design/diagram-candidates/manifest.json').read_text())
    self.assertEqual(checker.check(ROOT,doc)['reviewed_claims'],0)
if __name__=='__main__':unittest.main()
