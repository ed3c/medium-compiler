/* Sidecar-only ALG Four navigation; no article mutations or learning telemetry. */
(() => {
  "use strict";
  const source = document.querySelector(".alg-four-source");
  const sidebar = document.querySelector(".alg-four-sidebar");
  if (!source || !sidebar) return;

  const paragraphs = Array.from(source.querySelectorAll("[data-alg-four-index]"));
  const entries = Array.from(sidebar.querySelectorAll("details[data-outline-index]"));
  if (!paragraphs.length || paragraphs.length !== entries.length) return;

  const byIndex = new Map(entries.map((el) => [Number(el.dataset.outlineIndex), el]));
  const shell = sidebar.querySelector(".alg-sidebar-shell");
  const reduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  let active = -1;
  let scheduled = false;

  function activate(index, moveOutline = false) {
    const entry = byIndex.get(index);
    if (!entry) return;
    const changed = active !== index;
    if (changed) {
      if (active >= 0 && paragraphs[active]) {
        paragraphs[active].classList.remove("alg-current-source");
      }
      paragraphs[index].classList.add("alg-current-source");
      sidebar.querySelectorAll('summary[aria-current="location"]').forEach((el) => el.removeAttribute("aria-current"));
      const activeLink = entry.querySelector("summary[data-outline-link]");
      if (activeLink) activeLink.setAttribute("aria-current", "location");
      active = index;
    }

    // Automatically expand exactly the current heading/subheading lineage.
    const keep = new Set([shell]);
    for (let p = entry; p && p !== sidebar; p = p.parentElement) {
      if (p.matches && p.matches("details")) keep.add(p);
    }
    sidebar.querySelectorAll(".alg-outline-paragraph, .alg-outline-section").forEach((el) => {
      el.open = keep.has(el);
    });
    if (shell && window.innerWidth > 950) shell.open = true;

    if (changed || moveOutline) {
      const rect = entry.getBoundingClientRect();
      const bounds = sidebar.getBoundingClientRect();
      if (rect.top < bounds.top + 24) sidebar.scrollTop += rect.top - bounds.top - 32;
      if (rect.bottom > bounds.bottom - 24) sidebar.scrollTop += rect.bottom - bounds.bottom + 32;
    }
  }

  function currentParagraph() {
    const line = Math.max(130, Math.min(160, window.innerHeight * 0.18));
    let index = 0;
    for (let i = 0; i < paragraphs.length; i += 1) {
      const box = paragraphs[i].getBoundingClientRect();
      if (box.top <= line) index = i;
      else break;
    }
    return index;
  }

  function update() {
    scheduled = false;
    activate(currentParagraph());
  }

  function scheduleUpdate() {
    if (scheduled) return;
    scheduled = true;
    window.requestAnimationFrame(update);
  }

  sidebar.addEventListener("click", (event) => {
    const link = event.target.closest("summary[data-target-id]");
    if (!link) return;
    const id = link.dataset.targetId;
    const target = document.getElementById(id);
    if (!target || !source.contains(target)) return;
    event.preventDefault();

    // Choose its paragraph, or the first paragraph under a section heading.
    let selected;
    if (target.hasAttribute("data-alg-four-index")) {
      selected = Number(target.dataset.algFourIndex);
    } else {
      const following = paragraphs.find((node) => Boolean(target.compareDocumentPosition(node) & Node.DOCUMENT_POSITION_FOLLOWING));
      selected = following ? Number(following.dataset.algFourIndex) : 0;
    }
    activate(selected, true);
    if (window.history && window.history.replaceState) {
      window.history.replaceState(null, "", "#" + id);
    }
    target.scrollIntoView({ behavior: "auto", block: "start" });
    window.requestAnimationFrame(() => activate(selected, true));
  });

  window.addEventListener("scroll", scheduleUpdate, { passive: true });
  window.addEventListener("resize", scheduleUpdate);
  window.addEventListener("hashchange", () => {
    const id = window.location.hash.slice(1);
    const node = document.getElementById(id);
    if (node && node.dataset && node.dataset.algFourIndex) {
      activate(Number(node.dataset.algFourIndex), true);
    } else {
      scheduleUpdate();
    }
  });

  const initiallySelected = document.getElementById(window.location.hash.slice(1));
  if (initiallySelected && initiallySelected.dataset && initiallySelected.dataset.algFourIndex) {
    activate(Number(initiallySelected.dataset.algFourIndex), true);
  } else {
    activate(currentParagraph(), true);
  }
})();
