(() => {
  const caseRoutes = new Set(__CASE_ROUTES__);
  let navigating = false;
  function navigate(destination, a) {
    if (navigating) return;
    navigating = true;
    const rect = a.getBoundingClientRect();
    const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
    const nativeTransition = 'onpageswap' in window && 'onpagereveal' in window;
    const mode = reduceMotion ? 'none' : nativeTransition ? 'native' : 'fallback';
    try {
      sessionStorage.setItem('portfolio-page-transition', JSON.stringify({
        path:destination.pathname.replace(/\/$/, '') || '/',
        x:Math.round(rect.left + rect.width / 2),
        y:Math.round(rect.top + rect.height / 2),
        time:Date.now(), mode
      }));
    } catch (_) {}
    if (mode !== 'fallback') { location.assign(destination.href); return; }
    const veil = document.createElement('div');
    veil.className = 'portfolio-transition-bridge';
    veil.setAttribute('aria-hidden','true');
    document.body.append(veil);
    const animation = veil.animate([{opacity:0},{opacity:1}], {duration:130, easing:'ease-out', fill:'forwards'});
    animation.finished.catch(()=>{}).then(()=>location.assign(destination.href));
  }
  function fixLinks() {
    document.querySelectorAll('a').forEach(a => {
      const label = a.textContent.trim();
      if (label === 'Story' && !a.getAttribute('href')) a.setAttribute('href', '/about');
      if (label === 'Works' && !a.getAttribute('href')) a.setAttribute('href', '/');
    });
    caseRoutes.forEach(route => {
      document.querySelectorAll(`a[href=".${route}"],a[href="${route}"]`).forEach(a => {
        if (!a.className.includes('framer-')) return;
        a.classList.add('portfolio-project-card');
        a.closest('[class*="-container"]')?.classList.add('portfolio-project-tile');
      });
    });
    const services = document.querySelector('[data-framer-name="areas"]');
    if (services && !services.id) services.id = 'services';
    const intro = document.querySelector('.framer-180tc9q');
    if (intro && !document.querySelector('.portfolio-mobile-jumps')) {
      const jumps = document.createElement('nav');
      jumps.className = 'portfolio-mobile-jumps';
      jumps.setAttribute('aria-label','On this page');
      jumps.innerHTML = '<a href="#projects">Selected work <span aria-hidden="true">↓</span></a><a href="#services">What I do <span aria-hidden="true">↓</span></a>';
      intro.append(jumps);
    }
  }
  // The captured router retains animation state between mobile pages and still
  // contains the old gallery-only case components. Load their real documents.
  document.addEventListener('click', event => {
    if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    const a = event.target instanceof Element ? event.target.closest('a') : null;
    if (!a || a.target === '_blank' || a.hasAttribute('download')) return;
    const label = a.textContent.trim();
    if (a.getAttribute('aria-disabled') === 'true' || label.includes('More projects coming soon')) return;
    const href = a.getAttribute('href') || (label === 'Story' ? '/about' : label === 'Works' ? '/' : '');
    if (!href) return;
    const destination = new URL(href, location.href);
    if (destination.origin !== location.origin) return;
    const path = destination.pathname.replace(/\/$/, '') || '/';
    const pageTab = label === 'Story' || label === 'Works';
    if (!pageTab && !caseRoutes.has(path)) return;
    event.preventDefault();
    event.stopImmediatePropagation();
    if (path === (location.pathname.replace(/\/$/, '') || '/') && !destination.hash) {
      window.scrollTo({top:0, left:0, behavior:'instant'});
      return;
    }
    if (destination.hash) { location.assign(destination.href); return; }
    navigate(destination, a);
  }, true);
  function start() {
    if (document.querySelector('[data-framer-appear-id]') && !window.MotionIsMounted) { requestAnimationFrame(start); return; }
    fixLinks();
    let pending = false;
    new MutationObserver(() => {
      if (pending) return;
      pending = true;
      requestAnimationFrame(() => { pending = false; fixLinks(); });
    }).observe(document.body, {childList:true, subtree:true});
  }
  start();
  window.addEventListener('pageshow', () => {
    navigating = false;
    document.querySelectorAll('.portfolio-transition-bridge').forEach(el=>el.remove());
    setTimeout(()=>{
      if (document.documentElement.hasAttribute('data-portfolio-entry')) document.documentElement.dataset.portfolioEntry = 'settled';
    },700);
  });
})();
