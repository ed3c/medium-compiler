"""Real user interactions shared by source-bound article browser drives."""
def drive_reading_navigation(page, output, name, mobile, expected_paragraphs):
    rail=page.locator('.reading-rail')
    dialog=page.locator('.reading-dialog')
    assert not dialog.is_visible(), 'contents should not compete with the body at entry'
    assert rail.get_attribute('aria-expanded')=='false'
    assert page.locator('.alg-four-annotation').count()==expected_paragraphs
    assert page.locator('article [data-alg-four-index]').count()==expected_paragraphs
    marks=page.locator('.reading-rail-mark')
    widths=marks.evaluate_all('(nodes)=>nodes.map(n=>n.style.getPropertyValue("--chapter-length"))')
    assert marks.count()>1 and len(set(widths))>1, 'chapter bars must encode real text amounts'
    actual_widths=marks.evaluate_all('(nodes)=>nodes.map(n=>n.getBoundingClientRect().width)')
    ordered=sorted(zip([float(width.rstrip('%')) for width in widths],actual_widths))
    assert ordered[-1][1]>ordered[0][1]+1, 'responsive CSS erased chapter-length differences'
    assert all(b[1]>a[1] for a,b in zip(ordered,ordered[1:]) if b[0]>a[0]+1), 'chapter bars clipped unequal amounts to the same width'
    article=page.locator('article.alg-four-source').bounding_box()
    assert article['width']<=722
    page.screenshot(path=str(output/(name+'-closed.png')))
    if not mobile:
        rail.hover()
        assert dialog.is_visible(), 'desktop hover did not reveal the outline'
        dialog.hover()
        page.wait_for_timeout(300)
        assert dialog.is_visible(), 'moving from rail to dialog closed the hover panel'
        page.keyboard.press('Escape')
        assert not dialog.is_visible()
        assert rail.evaluate('(el)=>document.activeElement===el')
    if mobile: rail.tap()
    else:
        rail.focus()
        rail.press("Enter")
    assert dialog.is_visible()
    assert rail.get_attribute('aria-expanded')=='true'
    assert dialog.evaluate('(el)=>el.scrollHeight>el.clientHeight'), 'long outline needs its own scroll'
    scroll_before=page.evaluate('scrollY')
    dialog.hover()
    page.mouse.wheel(0,420)
    page.wait_for_timeout(120)
    assert dialog.evaluate('(el)=>el.scrollTop')>0
    assert page.evaluate('scrollY')==scroll_before, 'panel scrolling moved the article'
    close=page.locator('.reading-dialog-close').bounding_box()
    bounds=dialog.bounding_box()
    assert bounds['y']<=close['y']<=bounds['y']+bounds['height']-close['height'], 'close control scrolled out of the panel'
    page.screenshot(path=str(output/(name+'-open.png')))
    page.locator('.reading-dialog-close').click()
    assert not dialog.is_visible()
    assert rail.evaluate('(el)=>document.activeElement===el')
    headings=page.locator('article [data-alg-heading]').evaluate_all('(nodes)=>nodes.filter(n=>n.tagName!=="H1").map(n=>n.id)')
    for target in (headings[0],headings[-1]):
        if not dialog.is_visible(): rail.click()
        link=page.locator(f'summary[data-target-id="{target}"]')
        link.focus()
        link.press('Enter')
        page.wait_for_function('(id)=>location.hash==="#"+id',arg=target)
        page.wait_for_timeout(100)
        top=page.locator('#'+target).bounding_box()['y']
        header_bottom=page.locator('body > header').bounding_box()['height']
        assert header_bottom<=top<page.viewport_size['height'], (top,header_bottom)
        assert page.evaluate('document.activeElement.id')==target
        # The chapter's own navigation tree defines whether a paragraph note exists.
        notes=page.locator(f'.alg-outline-section[data-heading-id="{target}"] [data-outline-index]')
        expected=notes.first.get_attribute('data-outline-index') if notes.count() else None
        active=page.locator('summary[data-outline-link][aria-current="location"]')
        if expected is None:
            assert active.count()==0, 'code-only section retained an unrelated paragraph note'
            if mobile:
                assert not dialog.is_visible(), 'mobile dialog covered the selected source'
                rail.tap()
            assert page.locator(f'.alg-outline-section[data-heading-id="{target}"] .alg-outline-empty').is_visible()
            if mobile: page.locator('.reading-dialog-close').click()
        else:
            assert active.get_attribute('data-outline-link')==expected
        if mobile: assert not dialog.is_visible(), 'mobile dialog covered the selected source'
    # A real scroll updates the rail and selects a paragraph without changing URL.
    if dialog.is_visible(): page.locator('.reading-dialog-close').click()
    target=expected_paragraphs//2
    page.locator(f'#alg-p-{target}').evaluate('(el)=>el.scrollIntoView({block:"start"})')
    page.mouse.wheel(0,1)
    page.wait_for_timeout(150)
    active=page.locator('summary[data-outline-link][aria-current="location"]')
    assert int(active.get_attribute('data-outline-link'))==target
    assert page.locator('.reading-rail-mark[data-current]').count()==1
    rail.click()
    note=page.locator(f'[data-outline-index="{target}"]')
    note.locator('summary[data-outline-link]').click()
    assert page.evaluate('location.hash')==f'#alg-p-{target}'
    if mobile: rail.click()
    assert note.locator('.alg-reading-text').is_visible()
    assert note.locator('.alg-four-zh').inner_text().strip()
    assert note.locator('.alg-reading-text').inner_text().strip()
    if '/articles/' in page.url:
        assert note.locator('.alg-reading-context').is_visible()
        assert note.locator('.alg-premise').first.is_visible()
        assert '非獨立結論' in note.locator('.alg-skeleton').inner_text()
        assert note.locator('.alg-reading-context').evaluate('(el)=>!!(el.compareDocumentPosition(el.parentElement.querySelector(".alg-skeleton")) & Node.DOCUMENT_POSITION_FOLLOWING)')
        supports=page.locator('.alg-supporting-sources a')
        assert supports.count()>0
        for href in supports.evaluate_all('(links)=>links.map(n=>n.getAttribute("href"))'):
            assert page.locator('article '+href).count()==1
    page.screenshot(path=str(output/(name+'-note.png')))
    if '/articles/' in page.url:
        premise=note.locator('.alg-context-sources a').first
        destination=premise.get_attribute('href')
        premise.click()
        assert page.evaluate('location.hash')==destination
        assert page.evaluate('document.activeElement.id')==destination[1:]
        if mobile:
            assert not dialog.is_visible()
            rail.tap()
    page.keyboard.press('Escape')
    assert not dialog.is_visible()
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
    # Direct shared heading URLs must resolve to their own paragraph, too.
    page.goto(page.url.split('#')[0]+'#'+headings[0],wait_until='networkidle')
    expected=page.locator('#'+headings[0]).evaluate('''(h)=>[...document.querySelectorAll('article [data-alg-four-index]')].find(n=>h.compareDocumentPosition(n)&Node.DOCUMENT_POSITION_FOLLOWING).dataset.algFourIndex''')
    assert page.locator('summary[aria-current="location"]').get_attribute('data-outline-link')==expected
    return {'chapters':marks.count(),'paragraphs':expected_paragraphs,'closed_at_entry':True,
            'keyboard_heading_and_paragraph':True,'panel_scroll':True,'escape_focus_return':True,
            'source_bound_note_visible':True,'direct_heading_hash':True}
