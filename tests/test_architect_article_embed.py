"""Exact source identity and safe YouTube embed for the architect Medium article."""
import hashlib
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from test_learning_site import site

ROOT=Path(__file__).resolve().parents[1]
SLUG='architect-amplifier-payment-decisions'
VIDEO='F8X9_Dp3ZUk'

class FrameParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.frames=[]
    def handle_starttag(self,tag,attrs):
        if tag=='iframe': self.frames.append(dict(attrs))

class ArchitectArticleSiteTests(unittest.TestCase):
    def test_exact_article_embed_and_download(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/'dist'; provenance=site.build(out)
            page=(out/'articles'/SLUG/'index.html').read_text(encoding='utf-8')
            parser=FrameParser();parser.feed(page)
            self.assertEqual(len(parser.frames),1)
            frame=parser.frames[0]
            self.assertEqual(frame['src'],'https://www.youtube-nocookie.com/embed/'+VIDEO)
            self.assertEqual(frame['loading'],'lazy')
            self.assertIn('allowfullscreen',frame)
            self.assertIn('title',frame)
            self.assertIn('aspect-ratio:16/9',(out/'assets/styles.css').read_text())
            self.assertIn('/articles/'+SLUG+'/',(out/'articles/index.html').read_text())
            article=(ROOT/'articles'/f'{SLUG}.md').read_bytes()
            self.assertEqual((out/'articles'/SLUG/'article.md').read_bytes(),article)
            meta=next(v for v in provenance['articles'] if v['route']=='/articles/'+SLUG+'/')
            self.assertEqual(meta['sha256'],hashlib.sha256(article).hexdigest())
            self.assertEqual(meta['video_id'],VIDEO)
            self.assertEqual(meta['video_url'],'https://www.youtube.com/watch?v='+VIDEO)
            self.assertIn('Timeout 不是 Payment Failure',page)
            self.assertIn('來源：Gregor Hohpe',page)

    def test_iframe_ids_are_constrained(self):
        item={'title':'t','video_id':'"><img src=x onerror=alert(1)>'}
        with self.assertRaisesRegex(ValueError,'Invalid YouTube video ID'):
            site.youtube_article_embed(item)
        self.assertEqual(site.youtube_article_embed({'title':'t'}),'')

if __name__=='__main__':
    unittest.main()
