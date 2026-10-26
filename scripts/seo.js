(() => {
  const pages = __PORTFOLIO_SEO__;
  const origin = __PORTFOLIO_ORIGIN__;
  let pending = false;
  function update() {
    pending = false;
    const path = location.pathname.replace(/\.html$/, '').replace(/\/$/, '') || '/';
    const page = pages[path === '/test-1' ? '/' : path];
    if (!page) return;
    const url = origin + (path === '/test-1' ? '/' : path);
    if (document.title !== page.title) document.title = page.title;
    function meta(key, value, property = false) {
      const attr = property ? 'property' : 'name';
      let tag = document.head.querySelector(`meta[${attr}="${key}"]`);
      if (!tag) { tag = document.createElement('meta'); tag.setAttribute(attr, key); document.head.append(tag); }
      if (tag.content !== value) tag.content = value;
    }
    meta('description', page.description);
    meta('robots', path === '/test-1' ? 'noindex, follow' : 'index, follow, max-image-preview:large');
    for (const [key, value] of Object.entries({'og:title':page.title, 'og:description':page.description, 'og:url':url, 'og:image':page.image})) meta(key, value, true);
    for (const [key, value] of Object.entries({'twitter:title':page.title, 'twitter:description':page.description, 'twitter:image':page.image})) meta(key, value);
    let canonical = document.head.querySelector('link[rel="canonical"]');
    if (!canonical) { canonical = document.createElement('link'); canonical.rel = 'canonical'; document.head.append(canonical); }
    if (canonical.href !== url) canonical.href = url;
    let schema = document.getElementById('portfolio-structured-data');
    if (!schema) { schema = document.createElement('script'); schema.type = 'application/ld+json'; schema.id = 'portfolio-structured-data'; document.head.append(schema); }
    const json = JSON.stringify(page.schema);
    if (schema.textContent !== json) schema.textContent = json;
  }
  function schedule() { if (!pending) { pending = true; requestAnimationFrame(update); } }
  update();
  new MutationObserver(schedule).observe(document.head, {subtree:true, childList:true, characterData:true, attributes:true, attributeFilter:['content','href']});
  window.addEventListener('popstate',schedule);
  window.addEventListener('pageshow',schedule);
})();
