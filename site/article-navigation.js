(() => {
  const header = document.querySelector("body > header");
  const contents = document.querySelector(".article-toc");
  if (!header || !contents) return;
  const updateOffset = () => {
    document.documentElement.style.setProperty(
      "--article-header-offset", Math.ceil(header.getBoundingClientRect().height + 20) + "px"
    );
  };
  updateOffset();
  new ResizeObserver(updateOffset).observe(header);
  contents.open = !window.matchMedia("(max-width: 800px)").matches;
  if (location.hash) {
    requestAnimationFrame(() => {
      const target = document.getElementById(location.hash.slice(1));
      if (target) target.scrollIntoView({block: "start"});
    });
  }
})();
