"""Native Chromium/Playwright acceptance for the real built ALG Four page.

Runs a real browser (not merely HTML string assertions). No learner progress,
publication, or Medium login is inferred from a successful UI assertion.
"""
from __future__ import annotations

import argparse
import contextlib
import http.server
import json
from pathlib import Path
import threading
from playwright.sync_api import sync_playwright


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass


def run(site: Path | None, output: Path, base_url: str | None = None) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    server=None
    if base_url:
        url=base_url.rstrip('/')+'/alg-four/'
    else:
        factory=lambda *args,**kwargs: QuietHandler(*args,directory=str(site),**kwargs)
        server=http.server.ThreadingHTTPServer(("127.0.0.1",0),factory)
        worker=threading.Thread(target=server.serve_forever,daemon=True)
        worker.start()
        url=f"http://127.0.0.1:{server.server_port}/alg-four/"
    report={"url":url,"desktop":{},"mobile":{},"status":"INCONCLUSIVE"}
    try:
        with sync_playwright() as playwright:
            browser=playwright.chromium.launch(headless=True,args=["--no-sandbox"])
            desktop=browser.new_page(viewport={"width":1440,"height":900})
            errors=[]
            desktop.on("pageerror",lambda err: errors.append(str(err)))
            response=desktop.goto(url,wait_until="networkidle")
            assert response is not None and response.status==200, "HTML is not served"
            article=desktop.locator("article.alg-four-source")
            assert article.is_visible()
            assert "Group Anagrams" in article.inner_text()
            assert "loop invariant" in article.inner_text().lower()
            source_response=desktop.request.get(url+"source.json")
            assert source_response.status==200, "source manifest is not served"
            source=source_response.json()
            paragraph_count=source["alignment"]["paragraph_count"]
            scroll_index=paragraph_count//2
            click_index=source["active_items"][0]["paragraph_index"]
            assert article.locator("figure.article-figure img").count()==7
            images=article.locator("figure.article-figure img")
            for img in images.all():
                img.scroll_into_view_if_needed()
                img.evaluate("e=>e.loading='eager'")
                desktop.wait_for_function(
                    "src=>{const e=[...document.images].find(i=>i.src===src);return e.complete && e.naturalWidth>0}",
                    arg=img.evaluate("e=>e.src"))
                assert img.evaluate("e=>new URL(e.src).origin===location.origin"), "Figure escaped deployed origin"
            assert desktop.locator("[data-outline-index]").count()==paragraph_count
            assert article.locator("[data-alg-four-index]").count()==paragraph_count
            assert desktop.locator(".alg-four-annotation").count()==paragraph_count
            assert desktop.locator(".alg-active-term").count()>=10
            assert desktop.locator(".alg-four-sidebar").bounding_box()["x"] > article.bounding_box()["x"]+article.bounding_box()["width"]-20
            assert desktop.locator(".alg-four-sidebar").evaluate("(e)=>getComputedStyle(e).position")=="sticky"

            # Real viewport scroll must pick the matching, detailed annotation.
            paragraph=article.locator(f'[data-alg-four-index="{scroll_index}"]')
            desktop.mouse.wheel(0, 600)
            desktop.wait_for_timeout(100)
            paragraph.evaluate("(el)=>el.scrollIntoView({block:'start',behavior:'auto'})")
            desktop.wait_for_timeout(250)
            active=desktop.locator('summary[data-outline-link][aria-current="location"]')
            assert active.count()==1, "one active source paragraph expected"
            assert desktop.locator(".alg-outline-paragraph[open]").count()==1
            assert desktop.locator(".alg-outline-section[open]").count()>=1
            current=int(active.get_attribute("data-outline-link"))
            assert abs(current-scroll_index)<=2, f"scroll observer chose unrelated paragraph {current}"

            # A real click changes hash and lands on its exact source paragraph.
            # Open the correct section via its actual outline hierarchy.
            target=desktop.locator(f'[data-outline-index="{click_index}"]')
            target.evaluate("(e)=>{for(let p=e.parentElement;p;p=p.parentElement)if(p.tagName==='DETAILS')p.open=true}")
            target.locator("summary[data-outline-link]").click()
            desktop.wait_for_timeout(400)
            assert desktop.evaluate("location.hash")==f"#alg-p-{click_index}"
            assert article.locator(f"#alg-p-{click_index}").count()==1
            reading=desktop.locator(f'.alg-outline-paragraph[data-outline-index="{click_index}"] .alg-reading-text')
            assert reading.count()==1
            try:
                reading.wait_for(state="visible",timeout=3500)
            except Exception:
                pass
            if not reading.is_visible() or not reading.text_content().strip():
                desktop.screenshot(path=str(output/"desktop-failure.png"),full_page=True)
                parents=target.evaluate("(el)=>{const states=[];for(let p=el;p;p=p.parentElement)if(p.tagName==='DETAILS')states.push({cls:p.className,open:p.open});return states}")
                raise AssertionError("Clicked paragraph annotation not visible: details.open="+
                    str(target.get_attribute("open"))+" active="+
                    str(desktop.locator('summary[data-outline-link][aria-current="location"]').get_attribute("data-outline-link"))+
                    " parents="+str(parents)+
                    " css="+str(reading.evaluate("(e)=>{let s=getComputedStyle(e),r=e.getBoundingClientRect();return {display:s.display,visibility:s.visibility,opacity:s.opacity,width:r.width,height:r.height,offsetParent:Boolean(e.offsetParent)}}"))+
                    " articleAside="+str(sidebar if False else desktop.locator(".alg-four-sidebar").is_visible())+
                    " text="+str(reading.text_content()[:120]))
            assert desktop.locator(".alg-active-term").first.evaluate(
                "(e)=>getComputedStyle(e).backgroundColor")=="rgb(245, 216, 88)"
            assert not errors, f"browser page errors: {errors}"

            desktop.screenshot(path=str(output/"desktop-viewport.png"))
            desktop.screenshot(path=str(output/"desktop.png"),full_page=True)
            report["desktop"]={"paragraphs":paragraph_count,"figures":7,"active_items":"at_least_10",
                               "scroll_tracked_paragraph":current,
                               "anchor_click":f"alg-p-{click_index}","javascript_errors":errors}

            mobile=browser.new_page(viewport={"width":390,"height":844},is_mobile=True,has_touch=True)
            m=mobile.goto(url,wait_until="networkidle")
            assert m and m.status==200
            sidebar=mobile.locator(".alg-four-sidebar")
            assert sidebar.is_visible()
            assert sidebar.evaluate("(e)=>getComputedStyle(e).position")=="relative"
            assert sidebar.bounding_box()["y"] < mobile.locator("article.alg-four-source").bounding_box()["y"]
            disclosure=sidebar.locator("details.alg-sidebar-shell")
            disclosure.locator("summary.alg-sidebar-toggle").click()
            assert disclosure.get_attribute("open") is None, "mobile outline did not collapse"
            disclosure.locator("summary.alg-sidebar-toggle").click()
            assert disclosure.get_attribute("open") is not None, "mobile outline did not re-open"
            # Keyboard activation of an actual source link.
            anchor=sidebar.locator('summary[data-outline-link="0"]')
            anchor.focus()
            anchor.press("Enter")
            mobile.wait_for_timeout(200)
            assert mobile.evaluate("location.hash")=="#alg-p-0"
            def assert_keyboard_target_visible():
                target_top=mobile.locator('#alg-p-0').bounding_box()['y']
                header_box=mobile.locator('header').bounding_box()
                header_bottom=header_box['y']+header_box['height']
                if not header_bottom <= target_top < 844:
                    mobile.screenshot(path=str(output/'mobile-failure.png'))
                    raise AssertionError(f'keyboard target top={target_top}, header bottom={header_bottom}')
                return {'target_top':target_top,'header_bottom':header_bottom}

            keyboard_position=assert_keyboard_target_visible()
            assert mobile.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"), "mobile page overflows horizontally"
            mobile.screenshot(path=str(output/"mobile-viewport.png"))
            mobile.screenshot(path=str(output/"mobile.png"),full_page=True)
            # A taller real sticky header must not cover keyboard navigation.
            mobile.add_style_tag(content='header{padding-top:34px;padding-bottom:34px}')
            anchor.focus()
            anchor.press('Enter')
            mobile.wait_for_timeout(250)
            tall_header_position=assert_keyboard_target_visible()
            mobile.screenshot(path=str(output/'mobile-tall-header.png'))
            report["mobile"]={"viewport":"390x844","collapsible_outline":True,"keyboard_anchor":"alg-p-0",
                              'keyboard_position':keyboard_position,'tall_header_position':tall_header_position}
            browser.close()
        report["status"]="PASS"
    finally:
        if server:
            server.shutdown()
            server.server_close()
        (output/"result.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    return report


def main():
    parser=argparse.ArgumentParser()
    source=parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--site",type=Path)
    source.add_argument("--url")
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    result=run(args.site.resolve() if args.site else None,args.out.resolve(),args.url)
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
