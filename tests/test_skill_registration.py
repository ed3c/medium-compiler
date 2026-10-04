"""Repository discovery, pinned methods, and the actual article's extracted core logic."""
import ast
from collections import defaultdict
from decimal import Decimal, InvalidOperation
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import unittest
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / '.agents/skills'
spec = importlib.util.spec_from_file_location('verify_medium', SKILLS/'verify-medium/scripts/verify.py')
verify_medium = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify_medium)


class SkillRegistrationTests(unittest.TestCase):
    def test_unique_frontmatter_names_match_directories(self):
        names=[]
        for p in SKILLS.glob('*/SKILL.md'):
            text=p.read_text(encoding='utf-8')
            self.assertTrue(text.startswith('---\n'))
            name=re.search(r'(?m)^name:\s*(.+)$',text).group(1).strip('"\'')
            self.assertEqual(name,p.parent.name)
            self.assertIn('description:',text.split('---',2)[1])
            names.append(name)
        self.assertEqual(len(names),22)
        self.assertEqual(len(names),len(set(names)))

    def test_root_is_a_pointer_not_a_second_registered_skill(self):
        text=(ROOT/'SKILL.md').read_text()
        self.assertFalse(text.startswith('---'))
        self.assertIn('.agents/skills/medium-writing/SKILL.md',text)
        self.assertIn('Boot Batch',(SKILLS/'medium-writing/SKILL.md').read_text())
        self.assertIn('writing-contract.md',(SKILLS/'medium-writing/SKILL.md').read_text())

    def test_cefr_skills_match_complete_pinned_dependency_closure(self):
        verify_medium.verify_cefr_skill_lock(ROOT)

    def test_cefr_lock_refuses_changed_missing_and_extra_files(self):
        verify_medium.verify_cefr_skill_lock(ROOT)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            for name in verify_medium.CEFR_SKILL_FILES | {'references/upstream/cefr-alg-skills-lock.json'}:
                target = root/name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT/name, target)
            verify_medium.verify_cefr_skill_lock(root)
            target = root/'.agents/skills/cefr-alg-four-pass/references/execution-protocol.md'
            original = target.read_bytes()
            target.write_bytes(original + b'\nChanged protocol\n')
            with self.assertRaisesRegex(ValueError, 'vendored bytes drift'):
                verify_medium.verify_cefr_skill_lock(root)
            target.unlink()
            with self.assertRaisesRegex(ValueError, 'complete lock manifest'):
                verify_medium.verify_cefr_skill_lock(root)
            target.write_bytes(original)
            (target.parent/'unlocked.md').write_text('Unpinned dependency\n')
            with self.assertRaisesRegex(ValueError, 'complete lock manifest'):
                verify_medium.verify_cefr_skill_lock(root)

    def test_learning_feature_map_and_composition_resolve_local_dependencies(self):
        directory = SKILLS/'verify-learning-article/features'
        self.assertEqual(verify_medium.relative_doc_targets(directory/'README.md', ROOT),
                         {path.resolve() for path in directory.glob('*.md') if path.name != 'README.md'})
        entry_targets = verify_medium.relative_doc_targets(directory.parent/'SKILL.md', ROOT)
        self.assertIn((directory/'four-pass-composition.md').resolve(), entry_targets)
        targets = verify_medium.relative_doc_targets(directory/'four-pass-composition.md', ROOT)
        for name in ('cefr-alg-four-pass', 'alg-vocab-encounter', 'alg-explainer-video', 'verify-medium'):
            self.assertIn((SKILLS/name/'SKILL.md').resolve(), targets)
        for path in directory.glob('*.md'):
            verify_medium.relative_doc_targets(path, ROOT)

    def test_relative_dependency_resolution_rejects_missing_and_wrong_base(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            source = root/'skill/references/entry.md'
            source.parent.mkdir(parents=True)
            sibling = root/'skill/SKILL.md'
            sibling.write_text('# Fixture\n')
            source.write_text('[Entry](../SKILL.md#fixture) and `../SKILL.md`\n')
            self.assertEqual(verify_medium.relative_doc_targets(source, root), {sibling})
            source.write_text('[Directory](../)\n')
            self.assertEqual(verify_medium.relative_doc_targets(source, root), {sibling.parent})
            source.write_text('[Wrong base](SKILL.md)\n')
            with self.assertRaisesRegex(ValueError, 'Unresolved local dependency'):
                verify_medium.relative_doc_targets(source, root)
            source.write_text('[Missing](../missing.md)\n')
            with self.assertRaisesRegex(ValueError, 'Unresolved local dependency'):
                verify_medium.relative_doc_targets(source, root)
            source.write_text('[Outside](../../../outside.md)\n')
            with self.assertRaisesRegex(ValueError, 'Unresolved local dependency'):
                verify_medium.relative_doc_targets(source, root)

    def test_upstream_bytes_and_license_preserved(self):
        lock=json.loads((ROOT/'references/upstream/skills-lock.json').read_text())
        self.assertEqual(len(lock['files']),24)
        for record in lock['files']:
            path=ROOT/record['path']
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),record['sha256'])
        self.assertIn('Apache License',(ROOT/'references/upstream/evals-skills.LICENSE').read_text())

    def test_feature_index_and_four_headings(self):
        directory=SKILLS/'verify-medium/features'
        index=(directory/'README.md').read_text()
        linked=re.findall(r'\]\(([^)]+\.md)\)',index)
        siblings={p.name for p in directory.glob('*.md') if p.name!='README.md'}
        self.assertEqual(set(linked),siblings)
        self.assertEqual(len(linked),len(siblings))
        expected=['Sub-features','How to get to it (user POV)','Driving it with verify-medium','Gotchas']
        for name in siblings:
            headings=re.findall(r'^## (.+)$',(directory/name).read_text(),re.M)
            self.assertEqual(headings,expected)

    def test_real_body_is_only_five_declared_insertions(self):
        current=(ROOT/'articles/ai-engineer-learning-path.md').read_bytes()
        for rel in ['writer-pair/drill-down.md','authority/drill-down.md','handoff/drill-down.md']:
            extra=(ROOT/'evidence/issue-8'/rel).read_bytes()
            self.assertEqual(current.count(extra),1)
            current=current.replace(extra,b'',1)
        for name in ['drill-down-01.md','drill-down-02.md']:
            delta=(ROOT/'evidence/issue-8'/name).read_bytes()
            self.assertEqual(current.count(delta),1)
            current=current.replace(delta,b'',1)
        self.assertEqual(current,(ROOT/'evidence/issue-8/before.md').read_bytes())


class ExtractedOpsLogicTests(unittest.TestCase):
    """Execute only the unmodified normalize/reconcile AST, not HTTP or a provider."""
    @classmethod
    def setUpClass(cls):
        path=ROOT/'evidence/issue-8/inputs/ops-main.py'
        module=ast.parse(path.read_text())
        functions=[n for n in module.body if isinstance(n,ast.FunctionDef) and n.name in {'normalize','reconcile'}]
        if len(functions)!=2:raise AssertionError('expected exact core functions')
        env={'defaultdict':defaultdict,'Decimal':Decimal,'InvalidOperation':InvalidOperation,
             'HTTPException':RuntimeError}
        exec(compile(ast.Module(body=functions,type_ignores=[]),str(path),'exec'),env)
        cls.normalize=staticmethod(env['normalize']);cls.reconcile=staticmethod(env['reconcile'])
        cls.mapping={'transaction_id':'id','amount':'amount','currency':'currency'}

    def source(self, rows):
        return {'headers':['id','amount','currency'],'rows':rows}

    def row(self, id='T100', amount='100.00', currency='USD'):
        return {'id':id,'amount':amount,'currency':currency}

    def test_duplicate_ids_keep_both_rows_and_source_line_numbers(self):
        result=self.normalize(self.source([self.row(),self.row()]),self.mapping)
        self.assertEqual([r['row'] for r in result['T100']],[2,3])
        self.assertEqual(len(result['T100']),2)

    def test_unique_pair_produces_2_00_only_for_amount_mismatch(self):
        left=self.normalize(self.source([self.row()]),self.mapping)
        right=self.normalize(self.source([self.row(amount='98.00')]),self.mapping)
        result=self.reconcile(left,right)
        self.assertEqual((result[0]['type'],result[0]['delta']),('amount_mismatch','2.00'))

    def test_duplicate_precedes_missing_and_currency_precedes_amount(self):
        left=self.normalize(self.source([self.row(),self.row()]),self.mapping)
        result=self.reconcile(left,{})
        self.assertEqual((result[0]['type'],result[0]['delta']),('duplicate_key',None))
        left=self.normalize(self.source([self.row()]),self.mapping)
        right=self.normalize(self.source([self.row(amount='98.00',currency='EUR')]),self.mapping)
        result=self.reconcile(left,right)
        self.assertEqual((result[0]['type'],result[0]['delta']),('currency_mismatch',None))

    def test_id_case_is_preserved_while_currency_is_uppercased(self):
        result=self.normalize(self.source([self.row(id=' t100 ',currency=' usd ')]),self.mapping)
        self.assertIn('t100',result)
        self.assertNotIn('T100',result)
        self.assertEqual(result['t100'][0]['currency'],'USD')


if __name__=='__main__':unittest.main()
