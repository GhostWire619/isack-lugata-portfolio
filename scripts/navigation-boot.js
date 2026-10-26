(() => {
  const root = document.documentElement;
  try {
    const key = 'portfolio-page-transition';
    const transition = JSON.parse(sessionStorage.getItem(key) || 'null');
    sessionStorage.removeItem(key);
    const path = location.pathname.replace(/\/$/, '') || '/';
    if (!transition || transition.path !== path || Date.now() - transition.time > 15000) return;
    root.style.setProperty('--portfolio-wipe-x', transition.x + 'px');
    root.style.setProperty('--portfolio-wipe-y', transition.y + 'px');
    root.dataset.portfolioEntry = matchMedia('(prefers-reduced-motion: reduce)').matches ? 'settled' : transition.mode;
    if (transition.mode === 'native') {
      // Keep the outgoing snapshot until the destination's SSR content is parsed.
      const ready = document.createElement('link');
      ready.rel = 'expect';
      ready.href = '#portfolio-render-ready';
      ready.setAttribute('blocking','render');
      document.head.append(ready);
    }
  } catch (_) {
    // Storage restrictions must never prevent ordinary page navigation.
  }
})();
