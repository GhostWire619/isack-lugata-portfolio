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
  }
  const quietSelector = '.zenitsu-pet,.zenitsu-chat,.zenitsu-launcher,.showcase,.showcase-cursor,.castle';
  const onlyWidgets = records => records.every(({ target, addedNodes, removedNodes }) => target.closest?.(quietSelector)
    || (target === document.body && [...addedNodes, ...removedNodes].every(node => node.nodeType !== 1 || node.matches(quietSelector))));
  function start() {
    if (document.querySelector('[data-framer-appear-id]') && !window.MotionIsMounted) { requestAnimationFrame(start); return; }
    fixLinks();
    let pending = false;
    new MutationObserver(records => {
      if (pending || onlyWidgets(records)) return;
      pending = true;
      requestAnimationFrame(() => { pending = false; fixLinks(); });
    }).observe(document.body, {childList:true, subtree:true});
  }
  start();
})();
