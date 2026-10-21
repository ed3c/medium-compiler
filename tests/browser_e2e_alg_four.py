"""Verify the original ALG Four content with the shared collapsed reading UI."""
import argparse
import functools
import http.server
import json
from pathlib import Path
from urllib.parse import urljoin
import threading
from playwright.sync_api import sync_playwright
from reading_navigation import drive_reading_navigation


def run(site, url, output):
    output.mkdir(parents=True,exist_ok=True)
    server=None
    if url: url=url.rstrip('/')+'/alg-four/'
    report={'status':'INCONCLUSIVE','public_deployment':False}
    if site:
        server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(site)))
        threading.Thread(target=server.serve_forever,daemon=True).start()
        url=f'http://127.0.0.1:{server.server_port}/alg-four/'
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True)
            try:
                for mobile in (False,True):
                    page=browser.new_page(viewport={'width':390,'height':844} if mobile else {'width':1440,'height':900},is_mobile=mobile,has_touch=mobile)
                    errors=[]
                    page.on('pageerror',lambda error:errors.append(str(error)))
                    assert page.goto(url,wait_until='networkidle').status==200
                    manifest=page.request.get(url+'source.json').json()
                    source_download=page.request.get(url+'article.md')
                    assert source_download.status==200
                    assert source_download.body()==(Path(__file__).resolve().parents[1]/manifest['source']['path']).read_bytes()
                    article=page.locator('article.alg-four-source')
                    assert 'Group Anagrams' in article.inner_text()
                    assert 'loop invariant' in article.inner_text().lower()
                    assert page.locator('.alg-active-term').first.evaluate('(el)=>getComputedStyle(el).backgroundColor')=='rgb(245, 216, 88)'
                    images=page.locator('article figure img')
                    assert images.count()==7
                    assert page.locator('.alg-active-term').count()==len(manifest['active_items'])
                    for image in images.all():
                        image.evaluate("(el)=>{el.loading='eager'}")
                        page.wait_for_function("src=>{const image=[...document.images].find(el=>el.src===src);return image.complete&&image.naturalWidth>0}",arg=image.evaluate('(el)=>el.src'))
                        response=page.request.get(urljoin(url,image.get_attribute('src')))
                        assert response.status==200 and '<svg' in response.text()
                        assert image.evaluate('(e)=>new URL(e.src).origin===location.origin')
                    mode='mobile' if mobile else 'desktop'
                    report[mode]=drive_reading_navigation(page,output,mode,mobile,manifest['alignment']['paragraph_count'])
                    # A dynamic sticky header must not hide keyboard destinations.
                    page.add_style_tag(content='header{padding-top:34px;padding-bottom:34px}')
                    page.locator('.reading-rail').click()
                    # Current chapter starts at this paragraph for the reported historical URL.
                    heading=page.locator('summary[data-target-id="alg-heading-4"]')
                    heading.click()
                    target=page.locator('#alg-heading-4').bounding_box()
                    header=page.locator('header').bounding_box()
                    assert target['y']>=header['height']
                    assert page.locator('summary[aria-current="location"]').get_attribute('data-outline-link')=='33'
                    assert not errors, errors
                    page.close()
            except Exception:
                if 'page' in locals() and not page.is_closed(): page.screenshot(path=str(output/'failure.png'))
                raise
            finally: browser.close()
        report['status']='PASS'
        return report
    finally:
        if server: server.shutdown();server.server_close()
        (output/'result.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    source=parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--site',type=Path)
    source.add_argument('--url')
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(run(args.site,args.url,args.out),ensure_ascii=False,indent=2))
