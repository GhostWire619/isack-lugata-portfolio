(() => {
  const caseRoutes = new Set(["/ecofy", "/wakili-msomi", "/globoexpats", "/habitek", "/osher-market", "/falco", "/tanstack-tanzania"]);
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
