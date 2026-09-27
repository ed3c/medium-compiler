from html.parser import HTMLParser
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from test_learning_site import site, ROOT

class Navigation(HTMLParser):
    def __init__(self):
        super().__init__();self.links={}
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='a' and a.get('rel') in ('prev','next'):
            self.links[a['rel']]=a['href']

class CourseNavigationTests(unittest.TestCase):
    def test_next_lesson_follows_selected_route_and_published_articles(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td);site.build(out)
            first=Navigation();first.feed((out/'articles/application-engineering-colab/index.html').read_text())
            second=Navigation();second.feed((out/'articles/git-collaboration/index.html').read_text())
            third=Navigation();third.feed((out/'articles/python-environments/index.html').read_text())
            self.assertEqual(first.links['next'],'/articles/git-collaboration/')
            self.assertEqual(second.links['prev'],'/articles/application-engineering-colab/')
            self.assertEqual(second.links['next'],'/articles/python-environments/')
            self.assertEqual(third.links['prev'],'/articles/git-collaboration/')
            from urllib.parse import urlparse,parse_qs
            query=parse_qs(urlparse(third.links['next']).query)
            self.assertEqual(query['path'],['phases/00-setup-and-tooling/07-docker-for-ai'])
            self.assertEqual(query['learningPath'],['software-engineering-fundamentals'])
            page=(out/'articles/python-environments/index.html').read_text()
            self.assertIn('本站下一篇實作文章尚未發布',page)
            previous=(out/'articles/git-collaboration/index.html').read_text()
            self.assertNotIn('本站下一篇實作文章尚未發布',previous)
            self.assertIn('https://medium-compiler.vercel.app/articles/python-environments/',previous)
            self.assertNotIn('03-gpu-setup-and-cloud',second.links['next'])

    def test_route_bytes_are_pinned_and_unknown_lesson_refuses_navigation(self):
        data=(ROOT/'references/upstream/software-engineering-fundamentals.json').read_bytes()
        self.assertEqual(hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest(),'a1b09d143c1590896e69b5ba77a1918710f35874')
        with self.assertRaisesRegex(ValueError,'missing from the selected route'):
            site.lesson_navigation({'lesson':'not-a-real-lesson'},json.loads(data))
