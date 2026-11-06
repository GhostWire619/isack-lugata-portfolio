(() => {
  const caseRoutes = new Set(__CASE_ROUTES__);
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
})();
