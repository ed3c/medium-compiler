"""Drive the selected real article; controls mutate only external copies."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
ENTRY = ROOT / '.agents/skills/verify-medium/scripts/verify.py'
ARTICLE = ROOT / 'articles/git-collaboration.md'
CONTEXT = ARTICLE.with_suffix('.context.json')


class SelectedArticleVerificationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='selected-article-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.article = self.root / ARTICLE.name
        self.context = self.article.with_suffix('.context.json')
        self.article.write_bytes(ARTICLE.read_bytes())
        self.context.write_bytes(CONTEXT.read_bytes())

    def drive(self, article, expected):
        out = self.root / 'evidence'
        result = subprocess.run(
            [sys.executable, str(ENTRY), '--feature', 'learning-article',
             '--article', str(article), '--out', str(out)],
            cwd=ROOT, capture_output=True, text=True, timeout=40,
            env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return out, json.loads(result.stdout)['features']['learning-article']

    def test_real_article_is_bound_recompiled_and_unchanged(self):
        before = {p: p.read_bytes() for p in (ARTICLE, CONTEXT)}
        out, row = self.drive(ARTICLE.relative_to(ROOT), 0)
        self.assertEqual(row['status'], 'PASS')
        self.assertEqual(row['article'], str(ARTICLE))
        self.assertEqual(row['article_sha256'],
                         'sha256:' + hashlib.sha256(before[ARTICLE]).hexdigest())
        self.assertEqual((out / 'article-run/medium-canonical.md').read_bytes(), before[ARTICLE])
        self.assertEqual((out / 'input.context.json').read_bytes(), before[CONTEXT])
        self.assertEqual(row['semantic_correctness'], 'NOT_ASSESSED')
        self.assertEqual(row['human_learning_outcome'], 'NOT_MEASURED')
        self.assertEqual({p: p.read_bytes() for p in before}, before)
        commands = json.loads((out / 'commands.json').read_text())['commands']
        self.assertIn('check-receipt', [c['argv'][2] for c in commands])
        self.assertTrue((out / 'article-run/validation-receipt.json').is_file())
        self.assertFalse(list(out.glob('scratch-*')))

    def test_changed_article_refuses_before_compiler_import(self):
        self.article.write_bytes(self.article.read_bytes() + '\n新內容。\n'.encode())
        before = self.article.read_bytes()
        out, row = self.drive(self.article, 2)
        self.assertIn('article/context hash mismatch', row['error'])
        self.assertEqual((out / 'input.md').read_bytes(), before)
        commands = json.loads((out / 'commands.json').read_text())['commands']
        self.assertNotIn('init', [c['argv'][2] for c in commands])
        self.assertEqual(self.article.read_bytes(), before)

    def test_stale_context_refuses_without_rewriting_it(self):
        context = json.loads(self.context.read_text())
        context['assembly']['article_sha256'] = '0' * 64
        self.context.write_text(json.dumps(context))
        before = self.context.read_bytes()
        _, row = self.drive(self.article, 2)
        self.assertIn('article/context hash mismatch', row['error'])
        self.assertEqual(self.context.read_bytes(), before)

    def test_missing_context_refuses(self):
        self.context.unlink()
        _, row = self.drive(self.article, 2)
        self.assertIn('.context.json', row['error'])

    def test_missing_hash_refuses(self):
        self.context.write_text('{}')
        _, row = self.drive(self.article, 2)
        self.assertIn('assembly.article_sha256', row['error'])

    def test_context_hash_alone_does_not_bypass_compiler(self):
        data = b'# Invalid article\n\n```python\nprint(1)\n'
        self.article.write_bytes(data)
        self.context.write_text(json.dumps({
            'assembly': {'article_sha256': hashlib.sha256(data).hexdigest()}}))
        out, row = self.drive(self.article, 2)
        self.assertEqual(row['status'], 'FAIL')
        commands = json.loads((out / 'commands.json').read_text())['commands']
        self.assertTrue(any(c['exit'] == 2 and 'fenced' in c['stderr'] for c in commands))

    def test_article_argument_is_required_and_never_silently_ignored(self):
        for args in (['--feature', 'learning-article'],
                     ['--feature', 'doctor', '--article', str(ARTICLE)]):
            with self.subTest(args=args):
                out = self.root / 'unused'
                result = subprocess.run([sys.executable, str(ENTRY), *args, '--out', str(out)],
                                        capture_output=True, text=True, timeout=10)
                self.assertEqual(result.returncode, 2)
                self.assertIn('--article', result.stderr)
                self.assertFalse(out.exists())


if __name__ == '__main__':
    unittest.main()
