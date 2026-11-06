(() => {
  // Replaces the even two-column project grid with one stacking deck. On larger screens
  // each project also zooms up to fill the stage before the next climbs over it.
  const PROJECTS = __SHOWCASE_PROJECTS__;
  const ORDER = ['globoexpats', 'falco', 'wakili-msomi', 'tanstack-tanzania', 'ecofy', 'habitek', 'osher-market'];

  const ZOOM_HOLD = .6;   // matches the 60vh gap between cards in the stylesheet
  const clamp = (value, min = 0, max = 1) => Math.min(max, Math.max(min, value));
  const ease = t => 1 - (1 - t) ** 3;
  const still = matchMedia('(prefers-reduced-motion: reduce)');
  const phoneQuery = matchMedia('(max-width:760px)');
  const items = ORDER.map(slug => PROJECTS.find(project => project.slug === slug)).filter(Boolean);

  let section = null, cards = [], frame = 0, cursor = null;

  function element(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function buildCard(project, index) {
    const card = element('a', 'showcase-card');
    card.href = `/${project.slug}`;
    card.style.setProperty('--tint', project.color || '#eee');
    card.style.setProperty('--stick', `${68 + index * 9}px`);
    card.style.setProperty('--stick-wide', `${70 + index * 8}px`);
    card.setAttribute('aria-label', `${project.name}: ${project.role}`);

    const media = element('div', 'showcase-media');
    const image = element('img');
    image.src = project.cover;
    image.alt = '';
    image.loading = index < 2 ? 'eager' : 'lazy';
    image.decoding = 'async';
    media.append(image);

    const caption = element('div', 'showcase-caption');
    const top = element('div', 'showcase-caption-top');
    top.append(element('span', 'showcase-index', String(index + 1).padStart(2, '0')), element('h3', '', project.name));
    const role = element('p', 'showcase-role', project.role);
    const tags = element('ul', 'showcase-tags');
    (project.tags || []).slice(0, 3).forEach(tag => tags.append(element('li', '', tag)));
    const arrow = element('span', 'showcase-arrow');
    arrow.setAttribute('aria-hidden', 'true');
    arrow.innerHTML = '<svg viewBox="0 0 20 20" width="18" height="18"><path d="M6 14L14 6M7.5 6H14v6.5" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>';
    caption.append(top, role, tags, arrow);
    card.append(media, caption);

    // Hand the click to the original Framer link so the site's router still does the transition.
    card.addEventListener('click', event => {
      if (event.defaultPrevented || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button) return;
      const original = document.querySelector(`.framer-lvzy8y a[href="./${project.slug}"]`);
      if (!original) return;
      event.preventDefault();
      original.click();
    });
    return { el: card, media, image, caption, wasPhone: null };
  }

  function mount(grid) {
    section = element('section', 'showcase');
    section.setAttribute('aria-label', 'Selected projects');
    cards = items.map(buildCard);
    cards.forEach(card => section.append(card.el));
    section.append(element('p', 'showcase-more', 'More projects coming soon'));
    grid.after(section);
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
    ['transform', 'clipPath', 'opacity'].forEach(property => {
      card.el.style[property] = '';
      card.media.style[property] = '';
      card.image.style[property] = '';
    });
    card.el.style.removeProperty('--dim');
  }

  function updatePhone(viewH) {
    cards.forEach((card, index) => {
      const rect = card.el.getBoundingClientRect();
      const next = cards[index + 1]?.el.getBoundingClientRect();
      // Sliding in: the photo settles while the card rises into place.
      const arrival = ease(clamp((viewH - rect.top) / (viewH * .7)));
      card.image.style.transform = `scale(${(1.16 - .16 * arrival).toFixed(3)})`;
      card.el.classList.toggle('is-in', arrival > .55);
      // Buried: as the next card climbs over, this one shrinks back into the deck.
      const buried = next ? clamp(1 - (next.top - rect.top) / Math.max(rect.height, 1)) : 0;
      const tilt = index % 2 ? -1.5 : 1.5;
      card.el.style.transform = `scale(${(1 - buried * .07).toFixed(3)}) rotate(${(tilt * buried).toFixed(2)}deg)`;
      card.el.style.setProperty('--dim', (buried * .34).toFixed(3));
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
      card.media.style.transform = `scale(${(.72 + .28 * zoom).toFixed(4)})`;
      card.image.style.transform = `scale(${(1.1 - .1 * zoom).toFixed(4)})`;
      card.el.classList.toggle('is-in', zoom > .82);

      // Buried: the next project climbs over and this one sinks back into the deck.
      const buried = next ? clamp(1 - (next.top - stick) / Math.max(rect.height, 1)) : 0;
      card.el.style.transform = `scale(${(1 - buried * .06).toFixed(4)})`;
      card.el.style.setProperty('--dim', (buried * .4).toFixed(3));
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
    const grid = document.querySelector('.framer-lvzy8y');
    if (!grid) {
      // Left the home page through the client router.
      document.documentElement.classList.remove('showcase-on');
      cursor?.classList.remove('is-on');
      return;
    }
    if (grid.nextElementSibling?.classList.contains('showcase')) return;
    mount(grid);
  }

  function start() {
    // Same wait as navigation.js: hydration must finish before adding beside React's nodes.
    if (document.querySelector('[data-framer-appear-id]') && !window.MotionIsMounted) { setTimeout(start, 60); return; }
    sync();
    let pending = false;
    new MutationObserver(() => {
      if (pending) return;
      pending = true;
      setTimeout(() => { pending = false; sync(); }, 80);
    }).observe(document.body, { childList: true, subtree: true });
    addEventListener('scroll', schedule, { passive: true });
    addEventListener('resize', schedule, { passive: true });
    still.addEventListener('change', schedule);
  }
  start();
})();
