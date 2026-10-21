"""Drive the real built article list, language pages and heading navigation."""
import argparse
import functools
import http.server
import importlib.util
import json
from pathlib import Path
import re
import threading
from playwright.sync_api import sync_playwright
from reading_navigation import drive_reading_navigation

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("article_site", ROOT / "scripts/build_site.py")
article_site = importlib.util.module_from_spec(spec)
spec.loader.exec_module(article_site)
CASES = tuple(item for item in article_site.ARTICLES if item.get("bilingual"))


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass


def run(site, output):
    output.mkdir(parents=True, exist_ok=True)
    server = http.server.ThreadingHTTPServer(
        ("127.0.0.1", 0), functools.partial(QuietHandler, directory=str(site)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    report = {"status": "INCONCLUSIVE", "pages": [], "public_deployment": False}
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True, args=["--no-sandbox"])
            try:
                for mobile in (False, True):
                    context = browser.new_context(
                        viewport={"width": 390, "height": 844} if mobile else {"width": 1440, "height": 900},
                        is_mobile=mobile, has_touch=mobile)
                    page = context.new_page()
                    errors = []
                    page.on("pageerror", lambda error: errors.append(str(error)))
                    mode = "mobile" if mobile else "desktop"
                    for item in CASES:
                        slug = item["slug"]
                        route = "/articles/" + slug + "/"
                        for lang in ("zh-TW", "en"):
                            target = route + ("en/" if lang == "en" else "")
                            for listing in ("/", "/articles/"):
                                response = page.goto(base + listing, wait_until="networkidle")
                                assert response.status == 200
                                link = page.locator(f'.card a[href="{target}"]')
                                assert link.count() == 1, "article is missing from listing"
                                link.click()
                                page.wait_for_url(base + target)
                                assert page.locator("article.bilingual-article").is_visible()
                            expected_lang = "en" if lang == "en" else "zh-Hant"
                            assert page.locator("html").get_attribute("lang") == expected_lang
                            source = ROOT / item["english_source" if lang == "en" else "source"]
                            text = source.read_text()
                            fence = chr(96) * 3
                            code = re.findall(r"(?ms)^" + fence + r"[^\n]*\n(.*?)^" + fence + r"\s*$", text)
                            actual = page.locator("article.bilingual-article pre code").all_text_contents()
                            assert [value.rstrip("\n") for value in code] == actual
                            assert code, "empty source/code comparison"
                            manifest=page.request.get(base+route+'source.json').json()
                            reading=drive_reading_navigation(page,output,f"{mode}-{slug}-{lang}",mobile,
                                                             manifest['alignment']['paragraph_count'])
                            download = page.locator(".article-download").get_attribute("href")
                            fetched = page.request.get(base + download)
                            assert fetched.status == 200 and fetched.body() == source.read_bytes()
                            other = "en" if lang == "zh-TW" else "zh-Hant"
                            page.locator(f'.article-languages a[hreflang="{other}"]').click()
                            page.wait_for_url(base + route + ("en/" if other == "en" else ""))
                            assert page.locator("html").get_attribute("lang") == other
                            assert not errors, errors
                            report["pages"].append({"viewport": mode, "slug": slug, "language": lang,
                                                    "headings": page.locator("article.bilingual-article h2").count(), "code_blocks": len(code),
                                                    "listing_clicks": 2, "keyboard_anchor": True,
                                                    "source_bytes_equal": True, "language_switch": True, "reading":reading})
                    context.close()
            except Exception:
                if "page" in locals() and not page.is_closed():
                    page.screenshot(path=str(output / "failure.png"), full_page=True)
                raise
            finally:
                browser.close()
        report["status"] = "PASS"
        return report
    except Exception as exc:
        report["error"] = str(exc)
        raise
    finally:
        (output / "result.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
        server.shutdown()
        server.server_close()
        thread.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.site.resolve(), args.out.resolve()), ensure_ascii=False, indent=2))
