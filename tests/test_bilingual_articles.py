"""Reader-visible bilingual routes and source-preserving website delivery."""
import importlib.util
import json
import re
from unittest.mock import patch
from html.parser import HTMLParser
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("article_site", ROOT / "scripts/build_site.py")
site = importlib.util.module_from_spec(spec)
spec.loader.exec_module(site)


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.language = None
        self.ids = []
        self.links = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "html":
            self.language = attrs.get("lang")
        if attrs.get("id"):
            self.ids.append(attrs["id"])
        if tag == "a":
            self.links.append(attrs.get("href"))


class BilingualArticleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.out = Path(cls.temporary.name) / "site"
        site.build(cls.out)

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def test_both_languages_are_discoverable_and_download_exact_approved_sources(self):
        for slug, case, headings in (
            ("leetcode-11-container-with-most-water", "container", 8),
            ("leetcode-207-course-schedule", "courses", 7),
            ("leetcode-875-koko-eating-bananas", "koko", 9),
            ("leetcode-56-merge-intervals", "intervals", 10),
        ):
            route = "/articles/" + slug + "/"
            for listing in ("index.html", "articles/index.html"):
                page = Page((self.out / listing).read_text())
                self.assertIn(route, page.links)
                self.assertIn(route + "en/", page.links)
            for lang, directory, download in (
                ("zh-TW", self.out / "articles" / slug, "article.md"),
                ("en", self.out / "articles" / slug / "en", "article.en.md"),
            ):
                with self.subTest(slug=slug, language=lang):
                    text = (directory / "index.html").read_text()
                    page = Page(text)
                    self.assertEqual(page.language, "en" if lang == "en" else "zh-Hant")
                    expected_ids = [f"section-{i}" for i in range(1, headings + 1)]
                    self.assertEqual([i for i in page.ids if i.startswith("section-")], expected_ids)
                    self.assertEqual(len(page.ids), len(set(page.ids)))
                    self.assertTrue(all('data-target-id="'+target+'"' in text for target in expected_ids))
                    manifest=json.loads((directory.parent / "source.json" if lang=="en" else directory / "source.json").read_text())
                    count=manifest["alignment"]["paragraph_count"]
                    self.assertEqual(text.count('class="alg-four-annotation"'),count)
                    self.assertEqual(text.count('class="reading-rail-mark"'),headings+1)
                    self.assertIn('aria-expanded="false"',text)
                    reviewed_stress=sum(len(token.get('stress',[])) for note in manifest['paragraph_annotations']
                                        for token in note['speed_reading']['tokens'])
                    self.assertEqual(text.count('class="alg-stress"'),reviewed_stress)
                    self.assertEqual(manifest['annotation_authority'],'speed-reading')
                    self.assertEqual(text.count('class="alg-reading-context"'),count)
                    self.assertEqual(text.count('閱讀提示（非獨立結論）'),count)
                    for note in manifest['paragraph_annotations']:
                        context=note['reading_context']
                        self.assertTrue(context['premises'])
                        self.assertIn('checkpoint',context)
                    self.assertEqual([i for i in page.ids if i.startswith("alg-p-")],[f"alg-p-{i}" for i in range(count)])
                    self.assertIn(route + download, page.links)
                    self.assertIn(route + ("en/" if lang == "zh-TW" else ""), page.links)
                    approved = (ROOT / "evals/writing/article-inference" / case / "accepted" / f"article.{lang}.md"
                                if case in ('koko','intervals') else
                                ROOT / "evals/writing/leetcode-cost-premises" / case / f"article.{lang}.md")
                    self.assertEqual((self.out / "articles" / slug / download).read_bytes(), approved.read_bytes())
                    self.assertIn("class Solution:", text)
                    self.assertNotIn("evals/writing/", text)
        self.assertFalse((self.out / "evals").exists())

    def test_duplicate_nested_headings_and_fenced_heading_have_unique_source_targets(self):
        item=next(item for item in site.ARTICLES if item.get('bilingual'))
        *_,projection=site.load_article_annotations(ROOT/item['annotations'])
        fence=chr(96)*3
        source='# Title\n\n## Same\n\n'+fence+'python\n## Hidden\n'+fence+'\n\n## Same\n\n### Nested'
        rendered,outline,_,_=projection.render_outline(site.markdown(source),[],{}, {},heading_prefix='section-')
        self.assertEqual(Page(rendered).ids,['article-title','section-1','section-2','section-3'])
        self.assertNotIn('Hidden',outline)
        self.assertIn('<pre><code>## Hidden</code></pre>',rendered)

    def test_emphasis_is_rendered_but_code_stars_and_unsafe_text_stay_literal(self):
        self.assertEqual(site.inline("A *mutable* list; `x * y` and `**a**`"),
                         "A <em>mutable</em> list; <code>x * y</code> and <code>**a**</code>")
        self.assertEqual(site.inline("<script>"),"&lt;script&gt;")
        self.assertEqual(site.inline("[`ord`](https://docs.python.org/3.14/library/functions.html#ord)"),
                         '<a href="https://docs.python.org/3.14/library/functions.html#ord" target="_blank" rel="noreferrer"><code>ord</code></a>')

    def test_notes_refuse_missing_coverage_and_empty_active_quotes_without_extra_sha256(self):
        item=next(item for item in site.ARTICLES if item.get("bilingual"))
        manifest=ROOT/item['annotations']
        original=json.loads(manifest.read_text())
        for failure in ('omitted','empty_quote','bad_support','missing_layout','missing_context','empty_premises','missing_checkpoint','bad_context_quote'):
            data=json.loads(manifest.read_text())
            if failure=='omitted': data['paragraph_annotations'].pop()
            elif failure=='empty_quote': data['active_items'][0]['source_quote']=''
            elif failure=='missing_layout': del data['paragraph_annotations'][0]['speed_reading']
            elif failure=='missing_context': del data['paragraph_annotations'][0]['reading_context']
            elif failure=='empty_premises': data['paragraph_annotations'][0]['reading_context']['premises']=[]
            elif failure=='missing_checkpoint': del data['paragraph_annotations'][0]['reading_context']['checkpoint']
            elif failure=='bad_context_quote': data['paragraph_annotations'][0]['reading_context']['premises'][0]['supporting_sources'][0]['english_quote']='Absent prerequisite'
            else: data['active_items'][0]['supporting_sources']=[{'paragraph_index':0,'english_quote':'Invented supporting premise'}]
            with tempfile.TemporaryDirectory() as td:
                candidate=Path(td)/'manifest.json'
                candidate.write_text(json.dumps(data))
                with self.assertRaisesRegex(ValueError,'every original prose paragraph|source paragraph, decision or sentence|supporting premise|complete reading view|requires premises|exact supporting source'):
                    site.load_article_annotations(candidate)
        with patch.object(site.hashlib,'sha256',side_effect=AssertionError('No report-only SHA-256')):
            site.load_article_annotations(manifest)
        self.assertEqual(json.loads(manifest.read_text()),original)

    def test_incomplete_metadata_is_refused_instead_of_rendering_a_language_fallback(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError, "complete titles"):
                site.render_bilingual_article({"slug": "incomplete", "title": "Title"}, Path(td))

    def test_active_decision_must_belong_to_its_paragraph_but_may_share_other_decisions(self):
        item=next(item for item in site.ARTICLES if item.get('bilingual'))
        data=json.loads((ROOT/item['annotations']).read_text())
        active=data['active_items'][0]
        note=data['paragraph_annotations'][active['paragraph_index']]
        other=next(d['id'] for d in data['decisions'] if d['id'] not in note['decision_ids']
                   and d.get('active_cue') and d.get('oracle'))
        active['decision_id']=other
        with tempfile.TemporaryDirectory() as td:
            candidate=Path(td)/'manifest.json'
            candidate.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,'Active decision is not linked'):
                site.load_article_annotations(candidate)
            note['decision_ids'].append(other)
            candidate.write_text(json.dumps(data))
            site.load_article_annotations(candidate)

    def test_private_evaluation_paths_cannot_be_used_as_public_article_sources(self):
        item=dict(next(item for item in site.ARTICLES if item.get("bilingual")))
        item["source"]="evals/writing/leetcode-cost-premises/container/article.zh-TW.md"
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError, "inside articles/"):
                site.render_bilingual_article(item, Path(td))


if __name__ == "__main__":
    unittest.main()
