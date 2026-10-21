import json
import hashlib
from html.parser import HTMLParser
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
class Scripts(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sources=[]
        self.csp=[]
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if tag=='script' and 'src' in d:self.sources.append(d['src'])
        if tag=='meta' and d.get('http-equiv')=='Content-Security-Policy':
            self.csp.append(d.get('content',''))
class AifsIntegrationTests(unittest.TestCase):
    def test_source_byte_identity_and_html_mount(self):
        lock=json.loads((ROOT/'references/aifs-figure-vendor.json').read_text())
        self.assertEqual(lock['schema_version'],'aifs-figure-vendor@1')
        for row in lock['source_files']:
            data=(ROOT/row['vendor_path']).read_bytes()
            identity=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
            self.assertEqual(identity,row['git_blob_sha1'],row['source_path'])
        parser=Scripts()
        source=(ROOT/'apps/loop-workbench/public/aifs/figure-lab.html').read_text()
        parser.feed(source)
        self.assertEqual(parser.sources,['./lesson-figures.js','./figures-math.js','./figures-demo.js'])
        self.assertIn('window.mountLessonFigures(document)',source)
        self.assertEqual(len(parser.csp),1)
        self.assertIn("connect-src 'none'",parser.csp[0])
        self.assertIn("font-src 'none'",parser.csp[0])
    def test_isolated_frame_and_no_untrusted_effect_permissions(self):
        route=(ROOT/'apps/loop-workbench/src/routes/figures.tsx').read_text()
        self.assertIn('sandbox="allow-scripts"',route)
        self.assertNotIn('allow-same-origin',route)
        self.assertNotIn('allow-top-navigation',route)
        self.assertNotIn('fetch(',route)
        self.assertNotIn('ServerFunction',route)
    def test_manifest_and_source_only_boundary(self):
        meta=json.loads((ROOT/'references/aifs-figure-vendor.json').read_text())
        self.assertEqual(meta['license'],'MIT')
        self.assertEqual(len(meta['ordered_scripts']),3)
        self.assertEqual(len(meta['selected_figures']),3)
        self.assertNotIn('LESSON.md',str(meta))
if __name__=='__main__':unittest.main()
