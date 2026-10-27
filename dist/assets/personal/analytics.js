(() => {
  if (['localhost', '127.0.0.1', '[::1]'].includes(location.hostname) || navigator.doNotTrack === '1' || navigator.globalPrivacyControl) return;
  let page, activeSince, elapsed, progress;
  const path = () => location.pathname;
  const update = () => {
    if (activeSince) { elapsed += Date.now() - activeSince; activeSince = document.hidden ? 0 : Date.now(); }
    progress = Math.max(progress, Math.min(100, Math.round((scrollY + innerHeight) / Math.max(document.documentElement.scrollHeight, innerHeight) * 100)));
  };
  const send = (beacon = false) => {
    if (!page) return;
    update();
    const body = JSON.stringify({...page, seconds: Math.min(3600, Math.floor(elapsed / 1000)), progress});
    if (beacon && navigator.sendBeacon) navigator.sendBeacon('/events/', new Blob([body], {type: 'application/json'}));
    else fetch('/events/', {method: 'POST', headers: {'Content-Type': 'application/json'}, body, credentials: 'omit', keepalive: true}).catch(() => {});
  };
  const start = () => {
    if (page && page.path === path()) return;
    send(true);
    page = {id: crypto.randomUUID(), path: path(), referrer: document.referrer};
    elapsed = 0; progress = 0; activeSince = document.hidden ? 0 : Date.now();
    send();
  };
  document.addEventListener('visibilitychange', () => { send(true); activeSince = document.hidden ? 0 : Date.now(); });
  addEventListener('pagehide', () => send(true));
  for (const method of ['pushState', 'replaceState']) {
    const original = history[method];
    history[method] = function(...args) { const result = original.apply(this, args); start(); return result; };
  }
  addEventListener('popstate', start);
  start();
})();
