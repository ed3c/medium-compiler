/* Reading position selects source-bound notes; it records no learning events. */
(() => {
  "use strict";
  const source = document.querySelector(".alg-four-source");
  const sidebar = document.querySelector(".alg-four-sidebar");
  if (!source || !sidebar) return;
  const dialog = sidebar.querySelector("dialog");
  const rail = sidebar.querySelector(".reading-rail");
  const close = sidebar.querySelector(".reading-dialog-close");
  const header = document.querySelector("body > header");
  const paragraphs = [...source.querySelectorAll("[data-alg-four-index]")];
  const entries = [...sidebar.querySelectorAll("details[data-outline-index]")];
  const marks = [...sidebar.querySelectorAll("[data-chapter-target]")];
  const headings = [...source.querySelectorAll("[data-alg-heading]")];
  if (!dialog || !rail || paragraphs.length !== entries.length) return;
  let active = -1;
  let pinned = false;
  let hoverTimer;
  let scheduled = false;
  const mobile = () => matchMedia("(max-width:600px)").matches;
  const headerBottom = () => header ? Math.max(0, header.getBoundingClientRect().bottom) : 0;
  const refreshOffset = () => source.style.setProperty("--alg-scroll-offset", `${headerBottom() + 24}px`);

  function reveal(manual = false) {
    clearTimeout(hoverTimer);
    pinned = pinned || manual;
    if (!dialog.open) {
      if (mobile()) dialog.showModal();
      else dialog.show();
    }
    rail.setAttribute("aria-expanded", "true");
    if (manual) close.focus({preventScroll:true});
    else rail.focus({preventScroll:true});
    revealEntry();
  }
  function hide(restore = false) {
    clearTimeout(hoverTimer);
    pinned = false;
    dialog.close();
    rail.setAttribute("aria-expanded", "false");
    if (restore) rail.focus({preventScroll:true});
  }
  function revealEntry() {
    if (!dialog.open || active < 0) return;
    const entry = entries[active];
    const top = entry.offsetTop;
    const bottom = top + entry.offsetHeight;
    if (top < dialog.scrollTop + 100 || bottom > dialog.scrollTop + dialog.clientHeight - 20) {
      dialog.scrollTop = Math.max(0, top - 130);
    }
  }
  function activate(index) {
    if (!entries[index]) return;
    const changed = index !== active;
    active = index;
    const entry = entries[index];
    const ancestry = new Set();
    for (let node = entry; node && node !== dialog; node = node.parentElement) {
      if (node.matches("details")) ancestry.add(node);
    }
    sidebar.querySelectorAll(".alg-outline-paragraph,.alg-outline-section").forEach(node => {
      node.open = ancestry.has(node);
    });
    entries.forEach((node, i) => {
      const summary = node.querySelector("summary");
      if (i === index) summary.setAttribute("aria-current", "location");
      else summary.removeAttribute("aria-current");
    });
    if (changed) revealEntry();
  }
  function follow() {
    scheduled = false;
    // A visible chapter heading takes precedence over the preceding paragraph.
    const line = headerBottom() + 28;
    let chapter = 0;
    marks.forEach((mark, index) => {
      if (document.getElementById(mark.dataset.chapterTarget).getBoundingClientRect().top <= line + 4) chapter = index;
    });
    marks.forEach((mark, index) => mark.toggleAttribute("data-current", chapter === index));
    sidebar.querySelector(".reading-rail-position").textContent = `${chapter + 1}/${marks.length}`;
    let index = 0;
    for (let i = 0; i < paragraphs.length; i++) {
      if (paragraphs[i].getBoundingClientRect().top <= line + 4) index = i;
      else break;
    }
    const nextHeading = headings.findLast(node => node.getBoundingClientRect().top <= line + 4);
    if (nextHeading && nextHeading.compareDocumentPosition(paragraphs[index]) & Node.DOCUMENT_POSITION_PRECEDING) {
      const following = paragraphs.find(node => nextHeading.compareDocumentPosition(node) & Node.DOCUMENT_POSITION_FOLLOWING);
      if (following) index = Number(following.dataset.algFourIndex);
    }
    activate(index);
  }
  function schedule() {
    if (!scheduled) { scheduled = true; requestAnimationFrame(follow); }
  }
  function navigate(id, focus = true) {
    const target = document.getElementById(id);
    if (!target || !source.contains(target)) return;
    refreshOffset();
    history.replaceState(null, "", "#" + id);
    if (mobile()) hide();
    target.scrollIntoView({block:"start", behavior:"auto"});
    if (focus) {
      target.setAttribute("tabindex", "-1");
      target.focus({preventScroll:true});
    }
    follow();
    revealEntry();
  }
  rail.addEventListener("click", () => dialog.open && pinned ? hide(true) : reveal(true));
  rail.addEventListener("pointerenter", event => { if (event.pointerType === "mouse" && !mobile()) reveal(); });
  dialog.addEventListener("pointerenter", () => clearTimeout(hoverTimer));
  sidebar.addEventListener("pointerleave", event => {
    if (event.pointerType === "mouse" && !pinned && !dialog.contains(document.activeElement)) {
      hoverTimer = setTimeout(() => hide(), 250);
    }
  });
  close.addEventListener("click", () => hide(true));
  dialog.addEventListener("cancel", event => { event.preventDefault(); hide(true); });
  document.addEventListener("keydown", event => {
    if (event.key === "Escape" && dialog.open) { event.preventDefault(); hide(true); }
  });
  document.addEventListener("pointerdown", event => {
    if (dialog.open && !sidebar.contains(event.target)) hide();
  });
  sidebar.addEventListener("click", event => {
    const link = event.target.closest("[data-target-id]");
    if (!link) return;
    event.preventDefault();
    navigate(link.dataset.targetId);
  });
  window.addEventListener("scroll", schedule, {passive:true});
  window.addEventListener("resize", () => { refreshOffset(); schedule(); });
  window.addEventListener("hashchange", () => navigate(location.hash.slice(1), false));
  if (header) new ResizeObserver(() => { refreshOffset(); schedule(); }).observe(header);
  refreshOffset();
  requestAnimationFrame(() => location.hash ? navigate(location.hash.slice(1), false) : follow());
})();
