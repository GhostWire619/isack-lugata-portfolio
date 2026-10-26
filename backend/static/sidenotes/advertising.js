(() => {
  // Google’s published CMP handles the consent signal. Never simulate consent.
  const requested = new WeakSet();
  const requestAd = ad => {
    // A hidden desktop rail never generates a mobile impression.
    if (requested.has(ad) || !ad.getClientRects().length || ad.offsetWidth === 0) return;
    const markup = ad.querySelector('[data-ad-markup]');
    if (!markup) return;
    requested.add(ad);
    // Only materialize visible units: AdSense processes pending <ins> nodes in
    // DOM order, so pre-inserting a hidden rail can initialize the wrong unit.
    ad.append(markup.content.cloneNode(true));
    try { (window.adsbygoogle = window.adsbygoogle || []).push({}); } catch {}
  };
  const ads = document.querySelectorAll('[data-ad-container]');
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      entries.filter(entry => entry.isIntersecting).forEach(entry => {
        requestAd(entry.target);
        if (requested.has(entry.target)) observer.unobserve(entry.target);
      });
    }, {rootMargin: '300px'});
    ads.forEach(ad => observer.observe(ad));
  } else {
    const loadVisible = () => ads.forEach(requestAd);
    loadVisible();
    addEventListener('resize', loadVisible, {passive:true});
  }
  window.googlefc = window.googlefc || {};
  window.googlefc.callbackQueue = window.googlefc.callbackQueue || [];
  window.googlefc.callbackQueue.push({'CONSENT_API_READY': () => {
    if (typeof window.googlefc.showRevocationMessage !== 'function') return;
    document.querySelectorAll('[data-google-privacy]').forEach(button => {
      button.hidden = false;
      button.addEventListener('click', () => window.googlefc.callbackQueue.push({
        'CONSENT_API_READY': () => window.googlefc.showRevocationMessage()
      }));
    });
  }});
})();
