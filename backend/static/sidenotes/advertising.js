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
    const unit = ad.querySelector('ins.adsbygoogle');
    const placement = ad.closest('.journal-ad');
    const update = () => {
      // Only hide units Google explicitly declares empty; a slow request is
      // not proof of no fill. Never hide or modify a filled ad iframe.
      if (unit && unit.getAttribute('data-ad-status') === 'unfilled' && placement) {
        placement.hidden = true;
        statusObserver?.disconnect();
      }
    };
    const statusObserver = unit && 'MutationObserver' in window
      ? new MutationObserver(update) : null;
    statusObserver?.observe(unit, {attributes:true, attributeFilter:['data-ad-status']});
    update();
    try { (window.adsbygoogle = window.adsbygoogle || []).push({}); } catch (error) {
      statusObserver?.disconnect();
      if (placement) placement.hidden = true;
      console.warn('Journal advertisement could not initialize.', error);
    }
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
