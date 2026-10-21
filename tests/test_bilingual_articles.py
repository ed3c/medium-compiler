"""Reader-visible bilingual routes and source-preserving website delivery."""
import importlib.util
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
                    self.assertEqual(page.ids, expected_ids)
                    self.assertEqual(len(page.ids), len(set(page.ids)))
                    self.assertTrue(all("#" + target in page.links for target in expected_ids))
                    self.assertIn(route + download, page.links)
                    self.assertIn(route + ("en/" if lang == "zh-TW" else ""), page.links)
                    approved = ROOT / "evals/writing/leetcode-cost-premises" / case / f"article.{lang}.md"
                    self.assertEqual((self.out / "articles" / slug / download).read_bytes(), approved.read_bytes())
                    self.assertIn("class Solution:", text)
                    self.assertNotIn("evals/writing/", text)
        self.assertFalse((self.out / "evals").exists())

    def test_contents_ignore_fences_and_keep_duplicate_and_nested_headings_addressable(self):
        fence = chr(96) * 3
        source = "# Title\n\n## Same\n\n" + fence + "python\n## Hidden\n" + fence + "\n\n## Same\n\n### Nested"
        rendered, contents = site.article_contents(site.markdown(source))
        self.assertEqual(Page(rendered).ids, ["section-1", "section-2", "section-3"])
        self.assertEqual(Page(contents).links, ["#section-1", "#section-2", "#section-3"])
        self.assertNotIn("Hidden", contents)
        self.assertIn("<pre><code>## Hidden</code></pre>", rendered)
        self.assertIn('class="toc-level-3"', contents)

    def test_incomplete_metadata_is_refused_instead_of_rendering_a_language_fallback(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError, "complete titles"):
                site.render_bilingual_article({"slug": "incomplete", "title": "Title"}, Path(td))

    def test_private_evaluation_paths_cannot_be_used_as_public_article_sources(self):
        item=dict(next(item for item in site.ARTICLES if item.get("bilingual")))
        item["source"]="evals/writing/leetcode-cost-premises/container/article.zh-TW.md"
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError, "inside articles/"):
                site.render_bilingual_article(item, Path(td))


if __name__ == "__main__":
    unittest.main()
