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


def run(site: Path, output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
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
            assert "Loop invariant" in article.inner_text()
            assert article.locator("figure.article-figure img").count()==7
            assert desktop.locator("[data-outline-index]").count()==36
            assert article.locator("[data-alg-four-index]").count()==36
            assert desktop.locator(".alg-four-annotation").count()==36
            assert desktop.locator(".alg-active-term").count()>=10
            assert desktop.locator(".alg-four-sidebar").bounding_box()["x"] > article.bounding_box()["x"]+article.bounding_box()["width"]-20
            assert desktop.locator(".alg-four-sidebar").evaluate("(e)=>getComputedStyle(e).position")=="sticky"

            # Real viewport scroll must pick the matching, detailed annotation.
            paragraph=article.locator('[data-alg-four-index="22"]')
            desktop.mouse.wheel(0, 600)
            desktop.wait_for_timeout(100)
            paragraph.evaluate("(el)=>el.scrollIntoView({block:'start',behavior:'auto'})")
            desktop.wait_for_timeout(250)
            active=desktop.locator('summary[data-outline-link][aria-current="location"]')
            assert active.count()==1, "one active source paragraph expected"
            assert desktop.locator(".alg-outline-paragraph[open]").count()==1
            assert desktop.locator(".alg-outline-section[open]").count()>=1
            current=int(active.get_attribute("data-outline-link"))
            assert abs(current-22)<=2, f"scroll observer chose unrelated paragraph {current}"

            # A real click changes hash and lands on its exact source paragraph.
            # Open the correct section via its actual outline hierarchy.
            target=desktop.locator('[data-outline-index="15"]')
            target.evaluate("(e)=>{for(let p=e.parentElement;p;p=p.parentElement)if(p.tagName==='DETAILS')p.open=true}")
            target.locator("summary[data-outline-link]").click()
            desktop.wait_for_timeout(400)
            assert desktop.evaluate("location.hash")=="#alg-p-15"
            assert article.locator("#alg-p-15").count()==1
            assert desktop.locator('.alg-outline-paragraph[data-outline-index="15"] .alg-reading-text').count()==1
            reading=desktop.locator('.alg-outline-paragraph[data-outline-index="15"] .alg-reading-text')
            if not reading.is_visible() or not reading.text_content().strip():
                desktop.screenshot(path=str(output/"desktop-failure.png"),full_page=True)
                parents=target.evaluate("(el)=>{const states=[];for(let p=el;p;p=p.parentElement)if(p.tagName==='DETAILS')states.push({cls:p.className,open:p.open});return states}")
                raise AssertionError("Clicked paragraph annotation not visible: details.open="+
                    str(target.get_attribute("open"))+" active="+
                    str(desktop.locator('summary[data-outline-link][aria-current="location"]').get_attribute("data-outline-link"))+
                    " parents="+str(parents)+" text="+str(reading.text_content()[:120]))
            assert desktop.locator(".alg-active-term").first.evaluate(
                "(e)=>getComputedStyle(e).backgroundColor")=="rgb(245, 216, 88)"
            assert not errors, f"browser page errors: {errors}"

            desktop.screenshot(path=str(output/"desktop.png"),full_page=True)
            report["desktop"]={"paragraphs":36,"figures":7,"active_items":"at_least_10",
                               "scroll_tracked_paragraph":current,
                               "anchor_click":"alg-p-15","javascript_errors":errors}

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
            mobile.screenshot(path=str(output/"mobile.png"),full_page=True)
            report["mobile"]={"viewport":"390x844","collapsible_outline":True,"keyboard_anchor":"alg-p-0"}
            browser.close()
        report["status"]="PASS"
    finally:
        server.shutdown()
        server.server_close()
        (output/"result.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    return report


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--site",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    result=run(args.site.resolve(),args.out.resolve())
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
