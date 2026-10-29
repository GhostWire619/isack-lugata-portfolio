(() => {
  if (window.__journalClarity) return;
  window.__journalClarity = true;
  const key = 'journal-clarity-consent';
  const blocked = navigator.doNotTrack === '1' || navigator.globalPrivacyControl;
  const eligible = ['isack.space', 'www.isack.space'].includes(location.hostname)
    && !/^\/(admin|security|oauth|mcp)(\/|$)/.test(location.pathname);
  let granted = false;
  try { granted = localStorage.getItem(key) === 'granted'; } catch {}
  const status = () => {
    const node = document.querySelector('[data-clarity-status]');
    if (node) node.textContent = blocked ? 'Clarity and Google Analytics are disabled by your browser privacy preference.'
      : granted ? 'Analytics cookies are allowed.' : 'Analytics cookies are off. Clarity and Google Analytics use limited, cookie-free measurement.';
  };
  status();
  if (!eligible || blocked) return;
  window.clarity = window.clarity || function() { (window.clarity.q = window.clarity.q || []).push(arguments); };
  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function() { window.dataLayer.push(arguments); };
  const googleConsent = () => ({analytics_storage: granted ? 'granted' : 'denied',
    ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied'});
  window.gtag('consent', 'default', googleConsent());
  window.gtag('js', new Date());
  // GA4's enhanced measurement handles browser-history page views; do not
  // also send manual page_view events and count the same navigation twice.
  window.gtag('config', 'G-XWWT4YVE88', {
    allow_google_signals: false, allow_ad_personalization_signals: false
  });
  // Start Google's independent loader immediately. Deferring it behind a
  // session-replay loader can delay page views on short visits.
  const google = document.createElement('script');
  google.async = true;
  google.src = 'https://www.googletagmanager.com/gtag/js?id=G-XWWT4YVE88';
  google.onerror = () => console.warn('Google Analytics could not load. Check browser blocking or network access.');
  document.head.appendChild(google);
  const apply = () => {
    window.clarity('consentv2', {ad_Storage: 'denied', analytics_Storage: granted ? 'granted' : 'denied'});
    window.gtag('consent', 'update', {analytics_storage: granted ? 'granted' : 'denied'});
    status();
  };
  // Queue the real consent choice before downloading Microsoft's tracker.
  apply();
  document.querySelectorAll('[data-clarity-consent]').forEach(button => button.addEventListener('click', () => {
    granted = button.dataset.clarityConsent === 'granted';
    try { localStorage.setItem(key, granted ? 'granted' : 'denied'); } catch {}
    apply();
  }));
  addEventListener('storage', event => {
    if (event.key !== key && event.key !== null) return;
    granted = event.newValue === 'granted';
    apply();
  });
  const load = () => {
    const script = document.createElement('script');
    script.async = true;
    script.src = 'https://www.clarity.ms/tag/z485ii73vk';
    document.head.appendChild(script);
  };
  if ('requestIdleCallback' in window) window.requestIdleCallback(load, {timeout: 1500});
  else setTimeout(load, 0);
})();
