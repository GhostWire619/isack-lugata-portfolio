(() => {
  // One stacking deck of projects. On larger screens each project also zooms up to fill
  // the stage before the next climbs over it. The deck is already in the built page; this
  // adds its motion, and restores it when the router returns to Home.
  const MARKUP = "<section class=\"showcase\" aria-label=\"Selected projects\"><a class=\"showcase-card\" href=\"/globoexpats\" aria-label=\"GloboExpats: Mainly frontend development\" style=\"--tint:#ddd4eb;--stick:68px;--stick-wide:70px\"><div class=\"showcase-media\"><img src=\"/assets/personal/showcase/globoexpats-720.webp?v=a0a140b664f3b03d\" srcset=\"/assets/personal/showcase/globoexpats-720.webp?v=a0a140b664f3b03d 720w, /assets/personal/showcase/globoexpats-1280.webp?v=a0a140b664f3b03d 1280w\" sizes=\"(max-width:760px) calc(100vw - 38px), 92vw\" alt=\"\" fetchpriority=\"high\"></div><div class=\"showcase-caption\"><div class=\"showcase-caption-top\"><span class=\"showcase-index\">01</span><h3>GloboExpats</h3></div><p class=\"showcase-role\">Mainly frontend development</p><ul class=\"showcase-tags\"><li>Frontend</li><li>Marketplace</li><li>Web app</li></ul><span class=\"showcase-arrow\" aria-hidden=\"true\"><svg viewBox=\"0 0 20 20\" width=\"18\" height=\"18\"><path d=\"M6 14L14 6M7.5 6H14v6.5\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.5\" stroke-linecap=\"round\" stroke-linejoin=\"round\"/></svg></span></div></a><a class=\"showcase-card\" href=\"/falco\" aria-label=\"Falco Finance: Internal management backend development\" style=\"--tint:#d2d7de;--stick:77px;--stick-wide:78px\"><div class=\"showcase-media\"><img src=\"/assets/personal/showcase/falco-720.webp?v=a0a140b664f3b03d\" srcset=\"/assets/personal/showcase/falco-720.webp?v=a0a140b664f3b03d 720w, /assets/personal/showcase/falco-1280.webp?v=a0a140b664f3b03d 1280w\" sizes=\"(max-width:760px) calc(100vw - 38px), 92vw\" alt=\"\" loading=\"lazy\" decoding=\"async\"></div><div class=\"showcase-caption\"><div class=\"showcase-caption-top\"><span class=\"showcase-index\">02</span><h3>Falco Finance</h3></div><p class=\"showcase-role\">Internal management backend development</p><ul class=\"showcase-tags\"><li>Backend</li><li>Internal systems</li><li>Business</li></ul><span class=\"showcase-arrow\" aria-hidden=\"true\"><svg viewBox=\"0 0 20 20\" width=\"18\" height=\"18\"><path d=\"M6 14L14 6M7.5 6H14v6.5\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.5\" stroke-linecap=\"round\" stroke-linejoin=\"round\"/></svg></span></div></a><a class=\"showcase-card\" href=\"/wakili-msomi\" aria-label=\"Wakili Msomi: Frontend &amp; backend development\" style=\"--tint:#cbd4ee;--stick:86px;--stick-wide:86px\"><div class=\"showcase-media\"><img src=\"/assets/personal/showcase/wakili-msomi-720.webp?v=a0a140b664f3b03d\" srcset=\"/assets/personal/showcase/wakili-msomi-720.webp?v=a0a140b664f3b03d 720w, /assets/personal/showcase/wakili-msomi-1280.webp?v=a0a140b664f3b03d 1280w\" sizes=\"(max-width:760px) calc(100vw - 38px), 92vw\" alt=\"\" loading=\"lazy\" decoding=\"async\"></div><div class=\"showcase-caption\"><div class=\"showcase-caption-top\"><span class=\"showcase-index\">03</span><h3>Wakili Msomi</h3></div><p class=\"showcase-role\">Frontend &amp; backend development</p><ul class=\"showcase-tags\"><li>Full-stack</li><li>Legal AI</li><li>Swahili</li></ul><span class=\"showcase-arrow\" aria-hidden=\"true\"><svg viewBox=\"0 0 20 20\" width=\"18\" height=\"18\"><path d=\"M6 14L14 6M7.5 6H14v6.5\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.5\" stroke-linecap=\"round\" stroke-linejoin=\"round\"/></svg></span></div></a><a class=\"showcase-card\" href=\"/tanstack-tanzania\" aria-label=\"TanStack Tanzania: Backend development · Lab project\" style=\"--tint:#e1cec0;--stick:95px;--stick-wide:94px\"><div class=\"showcase-media\"><img src=\"/assets/personal/showcase/tanstack-tanzania-720.webp?v=a0a140b664f3b03d\" srcset=\"/assets/personal/showcase/tanstack-tanzania-720.webp?v=a0a140b664f3b03d 720w, /assets/personal/showcase/tanstack-tanzania-1280.webp?v=a0a140b664f3b03d 1280w\" sizes=\"(max-width:760px) calc(100vw - 38px), 92vw\" alt=\"\" loading=\"lazy\" decoding=\"async\"></div><div class=\"showcase-caption\"><div class=\"showcase-caption-top\"><span class=\"showcase-index\">04</span><h3>TanStack Tanzania</h3></div><p class=\"showcase-role\">Backend development · Lab project</p><ul class=\"showcase-tags\"><li>Backend</li><li>Community</li><li>Platform</li></ul><span class=\"showcase-arrow\" aria-hidden=\"true\"><svg viewBox=\"0 0 20 20\" width=\"18\" height=\"18\"><path d=\"M6 14L14 6M7.5 6H14v6.5\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.5\" stroke-linecap=\"round\" stroke-linejoin=\"round\"/></svg></span></div></a><a class=\"showcase-card\" href=\"/ecofy\" aria-label=\"Ecofy Africa: Frontend &amp; backend · Co-founder, CEO &amp; AI Lead\" style=\"--tint:#dbe6a0;--stick:104px;--stick-wide:102px\"><div class=\"showcase-media\"><img src=\"/assets/personal/showcase/ecofy-720.webp?v=a0a140b664f3b03d\" srcset=\"/assets/personal/showcase/ecofy-720.webp?v=a0a140b664f3b03d 720w, /assets/personal/showcase/ecofy-1280.webp?v=a0a140b664f3b03d 1280w\" sizes=\"(max-width:760px) calc(100vw - 38px), 92vw\" alt=\"\" loading=\"lazy\" decoding=\"async\"></div><div class=\"showcase-caption\"><div class=\"showcase-caption-top\"><span class=\"showcase-index\">05</span><h3>Ecofy Africa</h3></div><p class=\"showcase-role\">Frontend &amp; backend · Co-founder, CEO &amp; AI Lead</p><ul class=\"showcase-tags\"><li>Full-stack</li><li>Applied AI</li><li>Founder</li></ul><span class=\"showcase-arrow\" aria-hidden=\"true\"><svg viewBox=\"0 0 20 20\" width=\"18\" height=\"18\"><path d=\"M6 14L14 6M7.5 6H14v6.5\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.5\" stroke-linecap=\"round\" stroke-linejoin=\"round\"/></svg></span></div></a><a class=\"showcase-card\" href=\"/habitek\" aria-label=\"Habitek: Frontend &amp; backend development\" style=\"--tint:#ecd6ad;--stick:113px;--stick-wide:110px\"><div class=\"showcase-media\"><img src=\"/assets/personal/showcase/habitek-720.webp?v=a0a140b664f3b03d\" srcset=\"/assets/personal/showcase/habitek-720.webp?v=a0a140b664f3b03d 720w, /assets/personal/showcase/habitek-1280.webp?v=a0a140b664f3b03d 1280w\" sizes=\"(max-width:760px) calc(100vw - 38px), 92vw\" alt=\"\" loading=\"lazy\" decoding=\"async\"></div><div class=\"showcase-caption\"><div class=\"showcase-caption-top\"><span class=\"showcase-index\">06</span><h3>Habitek</h3></div><p class=\"showcase-role\">Frontend &amp; backend development</p><ul class=\"showcase-tags\"><li>Full-stack</li><li>Property</li><li>Web app</li></ul><span class=\"showcase-arrow\" aria-hidden=\"true\"><svg viewBox=\"0 0 20 20\" width=\"18\" height=\"18\"><path d=\"M6 14L14 6M7.5 6H14v6.5\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.5\" stroke-linecap=\"round\" stroke-linejoin=\"round\"/></svg></span></div></a><a class=\"showcase-card\" href=\"/osher-market\" aria-label=\"Osher Market: Backend development\" style=\"--tint:#c5ddd6;--stick:122px;--stick-wide:118px\"><div class=\"showcase-media\"><img src=\"/assets/personal/showcase/osher-market-720.webp?v=a0a140b664f3b03d\" srcset=\"/assets/personal/showcase/osher-market-720.webp?v=a0a140b664f3b03d 720w, /assets/personal/showcase/osher-market-1280.webp?v=a0a140b664f3b03d 1280w\" sizes=\"(max-width:760px) calc(100vw - 38px), 92vw\" alt=\"\" loading=\"lazy\" decoding=\"async\"></div><div class=\"showcase-caption\"><div class=\"showcase-caption-top\"><span class=\"showcase-index\">07</span><h3>Osher Market</h3></div><p class=\"showcase-role\">Backend development</p><ul class=\"showcase-tags\"><li>Backend</li><li>Commerce</li><li>APIs</li></ul><span class=\"showcase-arrow\" aria-hidden=\"true\"><svg viewBox=\"0 0 20 20\" width=\"18\" height=\"18\"><path d=\"M6 14L14 6M7.5 6H14v6.5\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.5\" stroke-linecap=\"round\" stroke-linejoin=\"round\"/></svg></span></div></a><p class=\"showcase-more\">More projects coming soon</p></section>";
  const ROUTES = { ecofy: 'OJvd1BNaN', 'osher-market': 'IhYkVKpYR', 'wakili-msomi': 'boFkVS3RZ', falco: 'Zmwx4Ibvc', habitek: 'mld1MIphZ', 'tanstack-tanzania': 'wi2Xaghpb', globoexpats: 'kuKUydbQG' };
  const ZOOM_HOLD = .6;   // matches the 60vh gap between cards in the stylesheet
  const clamp = (value, min = 0, max = 1) => Math.min(max, Math.max(min, value));
  const ease = t => 1 - (1 - t) ** 3;
  const still = matchMedia('(prefers-reduced-motion: reduce)');
  const phoneQuery = matchMedia('(max-width:760px)');

  let section = null, cards = [], frame = 0, cursor = null;

  // Skip style writes that wouldn't change anything; each one costs phones a recalculation.
  function setStyle(node, property, value) {
    const cache = node.__styleCache || (node.__styleCache = {});
    if (cache[property] === value) return;
    cache[property] = value;
    node.style[property] = value;
  }
  function setVar(node, name, value) {
    const cache = node.__styleCache || (node.__styleCache = {});
    if (cache[name] === value) return;
    cache[name] = value;
    node.style.setProperty(name, value);
  }

  function element(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function bind(deck) {
    section = deck;
    cards = [...section.querySelectorAll('.showcase-card')].map(el => ({
      el, media: el.querySelector('.showcase-media'), image: el.querySelector('img'), wasPhone: null,
    }));
    // Use the site's router for a seamless transition; a plain link is the fallback,
    // including for a tap made before the page has hydrated.
    section.addEventListener('click', event => {
      if (event.defaultPrevented || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button) return;
      const route = ROUTES[event.target.closest('.showcase-card')?.getAttribute('href').slice(1)];
      if (!window.__portfolioNavigate || !route) return;
      event.preventDefault();
      window.__portfolioNavigate(route);
    });
    document.documentElement.classList.add('showcase-on');
    if (matchMedia('(hover:hover) and (pointer:fine)').matches && !still.matches) attachCursor();
    schedule();
  }

  /* ---------- a label that follows the pointer over a project ---------- */

  function attachCursor() {
    if (!cursor) {
      cursor = element('div', 'showcase-cursor', 'View project');
      cursor.setAttribute('aria-hidden', 'true');
      document.body.append(cursor);
    }
    section.addEventListener('pointermove', event => {
      cursor.style.transform = `translate3d(${event.clientX + 14}px,${event.clientY + 14}px,0)`;
      cursor.classList.toggle('is-on', !!event.target.closest('.showcase-media'));
    }, { passive: true });
    section.addEventListener('pointerleave', () => cursor.classList.remove('is-on'));
  }

  /* ---------- scroll choreography: transforms only, visible cards only ---------- */

  function clear(card) {
    [card.el, card.media, card.image].forEach(node => {
      node.__styleCache = {};
      node.style.transform = '';
    });
    card.el.style.removeProperty('--dim');
  }

  function updatePhone(viewH) {
    cards.forEach((card, index) => {
      const rect = card.el.getBoundingClientRect();
      const next = cards[index + 1]?.el.getBoundingClientRect();
      // Sliding in: the photo settles while the card rises into place.
      const arrival = ease(clamp((viewH - rect.top) / (viewH * .7)));
      setStyle(card.image, 'transform', `scale(${(1.14 - .14 * arrival).toFixed(2)})`);
      card.el.classList.toggle('is-in', arrival > .55);
      // Buried: as the next card climbs over, this one shrinks back into the deck.
      const buried = next ? clamp(1 - (next.top - rect.top) / Math.max(rect.height, 1)) : 0;
      const tilt = index % 2 ? -1.5 : 1.5;
      setStyle(card.el, 'transform', `scale(${(1 - buried * .07).toFixed(3)}) rotate(${(tilt * buried).toFixed(1)}deg)`);
      setVar(card.el, '--dim', (buried * .34).toFixed(2));
    });
  }

  function updateWide(viewH) {
    cards.forEach((card, index) => {
      const rect = card.el.getBoundingClientRect();
      if (rect.bottom < -80 || rect.top > viewH + 80) return;
      const stick = parseFloat(card.el.style.getPropertyValue('--stick-wide'));
      const next = cards[index + 1]?.el.getBoundingClientRect();

      // Zoom: rises in small, keeps growing after it pins, then holds at full size.
      const rising = clamp((viewH - rect.top) / Math.max(viewH - stick, 1));
      const pinnedFor = next ? clamp(1 - (next.top - viewH) / (viewH * ZOOM_HOLD)) : 1;
      const zoom = ease(rising * .55 + pinnedFor * .45);
      setStyle(card.media, 'transform', `scale(${(.72 + .28 * zoom).toFixed(3)})`);
      setStyle(card.image, 'transform', `scale(${(1.1 - .1 * zoom).toFixed(3)})`);
      card.el.classList.toggle('is-in', zoom > .82);

      // Buried: the next project climbs over and this one sinks back into the deck.
      const buried = next ? clamp(1 - (next.top - stick) / Math.max(rect.height, 1)) : 0;
      setStyle(card.el, 'transform', `scale(${(1 - buried * .06).toFixed(3)})`);
      setVar(card.el, '--dim', (buried * .4).toFixed(2));
    });
  }

  function update() {
    frame = 0;
    if (!section?.isConnected) return;
    if (still.matches) {
      cards.forEach(card => { clear(card); card.el.classList.add('is-in'); });
      return;
    }
    const phone = phoneQuery.matches;
    cards.forEach(card => {
      if (card.wasPhone !== phone) { clear(card); card.wasPhone = phone; }
    });
    const viewH = innerHeight;
    const box = section.getBoundingClientRect();
    if (box.bottom < -200 || box.top > viewH + 200) return;
    if (phone) updatePhone(viewH);
    else updateWide(viewH);
  }

  function schedule() {
    if (!frame) frame = requestAnimationFrame(update);
  }

  function sync() {
    const host = document.querySelector('.framer-lvzy8y > .framer-oy8a34');
    if (!host) {
      // Left the home page through the client router.
      document.documentElement.classList.remove('showcase-on');
      cursor?.classList.remove('is-on');
      return;
    }
    if (host.querySelector('.showcase') === section && section) return;
    if (!host.querySelector('.showcase')) host.innerHTML = MARKUP;
    bind(host.querySelector('.showcase'));
  }

  function start() {
    // Safe before hydration: React leaves everything inside the deck's slot alone.
    sync();
    const quietSelector = '.zenitsu-pet,.zenitsu-chat,.zenitsu-launcher,.showcase,.showcase-cursor,.castle';
    const onlyWidgets = records => records.every(({ target, addedNodes, removedNodes }) => target.closest?.(quietSelector)
      || (target === document.body && [...addedNodes, ...removedNodes].every(node => node.nodeType !== 1 || node.matches(quietSelector))));
    // Runs before the browser paints, so returning to Home never shows the page without its deck.
    new MutationObserver(records => {
      if (!onlyWidgets(records)) sync();
    }).observe(document.body, { childList: true, subtree: true });
    addEventListener('scroll', schedule, { passive: true });
    addEventListener('resize', schedule, { passive: true });
    still.addEventListener('change', schedule);
  }
  start();
})();
