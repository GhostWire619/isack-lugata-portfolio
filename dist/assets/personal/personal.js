
(() => {
  const gallery = [{"title": "Nena AI", "subtitle": "Swahili speech \u00b7 Lab team project", "href": "/robotics#nena-ai", "image": "/assets/identity/cover-nena.svg?v=1e7fa648e579b1ed"}, {"title": "3D Solutions & Robotics", "subtitle": "Backend \u00b7 Former chairperson", "href": "/robotics", "image": "/assets/personal/robotics-live.opt.webp?v=1e7fa648e579b1ed"}, {"title": "TanStack Tanzania", "subtitle": "Backend development", "href": "/tanstack-tanzania", "image": "/assets/personal/tanstack-live.opt.webp?v=1e7fa648e579b1ed"}, {"title": "GloboExpats", "subtitle": "Mainly frontend development", "href": "/globoexpats", "image": "/assets/personal/globoexpats-live.opt.webp?v=1e7fa648e579b1ed"}];
  const projects = [{"slug": "ecofy", "name": "Ecofy Africa", "role": "Frontend & backend \u00b7 Co-founder, CEO & AI Lead", "url": "https://ecofy.co.tz/", "cover": "/assets/identity/cover-ecofy.svg?v=1e7fa648e579b1ed"}, {"slug": "wakili-msomi", "name": "Wakili Msomi", "role": "Frontend & backend development", "url": "https://wakilimsomi.sheriakiganjani.co.tz/", "cover": "/assets/identity/cover-wakili-msomi.svg?v=1e7fa648e579b1ed"}, {"slug": "globoexpats", "name": "GloboExpats", "role": "Mainly frontend development", "url": "https://globoexpats.com/", "cover": "/assets/identity/cover-globoexpats.svg?v=1e7fa648e579b1ed"}, {"slug": "habitek", "name": "Habitek", "role": "Frontend & backend development", "url": "https://habitek.co.tz/", "cover": "/assets/identity/cover-habitek.svg?v=1e7fa648e579b1ed"}, {"slug": "osher-market", "name": "Osher Market", "role": "Backend development", "url": "https://oshermarket.com/", "cover": "/assets/identity/cover-osher-market.svg?v=1e7fa648e579b1ed"}, {"slug": "falco", "name": "Falco Finance", "role": "Internal management backend development", "url": "https://falco.co.tz/", "cover": "/assets/identity/cover-falco.svg?v=1e7fa648e579b1ed"}, {"slug": "tanstack-tanzania", "name": "TanStack Tanzania", "role": "Backend development \u00b7 Lab project", "url": "https://tanstack.co.tz/", "cover": "/assets/identity/cover-tanstack-tanzania.svg?v=1e7fa648e579b1ed"}];
  const companies = [{"name": "Ecofy Africa", "logo": "/assets/identity/brand-ecofy.svg?v=1e7fa648e579b1ed", "url": "https://ecofy.co.tz/"}, {"name": "GloboExpats", "logo": "/assets/identity/brand-globo.svg?v=1e7fa648e579b1ed", "url": "https://globoexpats.com/"}, {"name": "Osher Market", "logo": "/assets/identity/brand-osher.svg?v=1e7fa648e579b1ed", "url": "https://oshermarket.com/"}, {"name": "Habitek", "logo": "/assets/identity/wordmark-habitek.svg?v=1e7fa648e579b1ed", "url": "https://habitek.co.tz/"}, {"name": "Falco Finance", "logo": "/assets/identity/brand-falco.svg?v=1e7fa648e579b1ed", "url": "https://falco.co.tz/"}, {"name": "Wakili Msomi", "logo": "/assets/identity/wordmark-wakili.svg?v=1e7fa648e579b1ed", "url": "https://wakilimsomi.sheriakiganjani.co.tz/"}, {"name": "TanStack Tanzania", "logo": "/assets/identity/tanstack-light.png?v=1e7fa648e579b1ed", "url": "https://tanstack.co.tz/"}, {"name": "UDSM Robotics Lab", "logo": "/assets/identity/brand-lab.svg?v=1e7fa648e579b1ed", "url": "https://robotics.udsm.ac.tz/"}];
  const storyGallery = [{"thumbnail": "/assets/identity/isack-startup-challenge.thumb.webp?v=1e7fa648e579b1ed", "src": "/assets/identity/isack-startup-challenge.webp?v=1e7fa648e579b1ed", "alt": "Isack and two teammates at the Imbeju\u2013UDSM Startup Challenge", "fullWidth": 443, "fullHeight": 792}, {"thumbnail": "/assets/identity/isack-tanzania-ai-forum.thumb.webp?v=1e7fa648e579b1ed", "src": "/assets/identity/isack-tanzania-ai-forum.webp?v=1e7fa648e579b1ed", "alt": "Screenshot of the ICT Commission\u2019s Instagram post showing Isack speaking at Tanzania AI Forum 2025", "fullWidth": 1166, "fullHeight": 552}, {"thumbnail": "/assets/identity/isack-costume-event.thumb.webp?v=1e7fa648e579b1ed", "src": "/assets/identity/isack-costume-event.webp?v=1e7fa648e579b1ed", "alt": "Group in costume at an outdoor evening event", "fullWidth": 530, "fullHeight": 848}, {"thumbnail": "/assets/identity/isack-nena-01.thumb.webp?v=1e7fa648e579b1ed", "src": "/assets/identity/isack-nena-01.opt.webp?v=1e7fa648e579b1ed", "alt": "Isack at the Nena AI booth at the UDSM Innovation and Technology Exhibition", "fullWidth": 937, "fullHeight": 1250}, {"thumbnail": "/assets/identity/isack-nena-03.thumb.webp?v=1e7fa648e579b1ed", "src": "/assets/identity/isack-nena-03.opt.webp?v=1e7fa648e579b1ed", "alt": "Isack beside the Nena AI display at UDSM", "fullWidth": 937, "fullHeight": 1250}, {"thumbnail": "/assets/identity/isack-nena-04.thumb.webp?v=1e7fa648e579b1ed", "src": "/assets/identity/isack-nena-04.opt.webp?v=1e7fa648e579b1ed", "alt": "Visitors gathered around the Nena AI booth", "fullWidth": 937, "fullHeight": 1250}, {"thumbnail": "/assets/identity/isack-nena-05.thumb.webp?v=1e7fa648e579b1ed", "src": "/assets/identity/isack-nena-05.opt.webp?v=1e7fa648e579b1ed", "alt": "The Nena AI team speaking with a visitor at the booth", "fullWidth": 937, "fullHeight": 1250}, {"thumbnail": "/assets/identity/isack-nena-06.thumb.webp?v=1e7fa648e579b1ed", "src": "/assets/identity/isack-nena-06.opt.webp?v=1e7fa648e579b1ed", "alt": "A closer view of the discussion at the Nena AI booth", "fullWidth": 937, "fullHeight": 1250}, {"thumbnail": "/assets/identity/isack-bluefin-01.thumb.webp?v=1e7fa648e579b1ed", "src": "/assets/identity/isack-bluefin-01.opt.webp?v=1e7fa648e579b1ed", "alt": "Isack at Bluefin Solutions", "fullWidth": 937, "fullHeight": 1250}, {"thumbnail": "/assets/identity/isack-instagram-weekend-01.thumb.webp?v=1e7fa648e579b1ed", "src": "/assets/identity/isack-instagram-weekend-01.opt.webp?v=1e7fa648e579b1ed", "alt": "Isack seated in a sunlit room", "fullWidth": 960, "fullHeight": 1280}, {"thumbnail": "/assets/identity/isack-instagram-weekend-02.thumb.webp?v=1e7fa648e579b1ed", "src": "/assets/identity/isack-instagram-weekend-02.opt.webp?v=1e7fa648e579b1ed", "alt": "A closer portrait of Isack seated in a sunlit room", "fullWidth": 960, "fullHeight": 1280}, {"thumbnail": "/assets/identity/isack-instagram-weekend-03.thumb.webp?v=1e7fa648e579b1ed", "src": "/assets/identity/isack-instagram-weekend-03.opt.webp?v=1e7fa648e579b1ed", "alt": "Isack and friends on a balcony", "fullWidth": 960, "fullHeight": 1280}, {"thumbnail": "/assets/identity/isack-instagram-weekend-04.thumb.webp?v=1e7fa648e579b1ed", "src": "/assets/identity/isack-instagram-weekend-04.opt.webp?v=1e7fa648e579b1ed", "alt": "Isack and friends posing for another balcony photo", "fullWidth": 960, "fullHeight": 1280}, {"thumbnail": "/assets/identity/coict-zanzibar-02.thumb.webp?v=1e7fa648e579b1ed", "src": "/assets/identity/coict-zanzibar-02.jpg?v=1e7fa648e579b1ed", "alt": "Three Ecofy team members at the Faculty Exchange Programme in Zanzibar", "fullWidth": 1114, "fullHeight": 1536}, {"thumbnail": "/assets/identity/coict-zanzibar-03.thumb.webp?v=1e7fa648e579b1ed", "src": "/assets/identity/coict-zanzibar-03.jpg?v=1e7fa648e579b1ed", "alt": "Ecofy team and fellow participants at the Faculty Exchange Programme", "fullWidth": 800, "fullHeight": 595}, {"thumbnail": "/assets/identity/coict-zanzibar-04.thumb.webp?v=1e7fa648e579b1ed", "src": "/assets/identity/coict-zanzibar-04.jpg?v=1e7fa648e579b1ed", "alt": "Group photo in front of the Faculty Exchange Programme backdrop", "fullWidth": 800, "fullHeight": 533}, {"thumbnail": "/assets/identity/coict-zanzibar-07.thumb.webp?v=1e7fa648e579b1ed", "src": "/assets/identity/coict-zanzibar-07.jpg?v=1e7fa648e579b1ed", "alt": "Ecofy team lined up beside their presentation", "fullWidth": 800, "fullHeight": 555}, {"thumbnail": "/assets/identity/coict-zanzibar-10.thumb.webp?v=1e7fa648e579b1ed", "src": "/assets/identity/coict-zanzibar-10.opt.webp?v=1e7fa648e579b1ed", "alt": "Attendees during a session at the Faculty Exchange Programme", "fullWidth": 800, "fullHeight": 533}];
  let pending = false;
  function addStoryGallery() {
    const stack = document.querySelector('#test .framer-rpyux0');
    if (!stack || stack.nextElementSibling?.classList.contains('story-gallery')) return;
    const wrap = document.createElement('div');
    wrap.className = 'story-gallery';
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'story-gallery-button';
    button.setAttribute('aria-haspopup', 'dialog');
    const label = document.createElement('span');
    label.className = 'story-gallery-label';
    label.textContent = 'View gallery';
    const count = document.createElement('span');
    count.className = 'story-gallery-count';
    count.textContent = `${storyGallery.length} photos`;
    button.append(label, count);
    button.insertAdjacentHTML('beforeend', '<svg class="story-gallery-arrow" viewBox="0 0 20 20" aria-hidden="true"><path fill="currentColor" d="M7.2 5.3c-.5-.3-1.1 0-1.1.6v8.2c0 .6.6.9 1.1.6l6.6-4.1c.5-.3.5-1 0-1.3z"/></svg>');
    // The 3D world is a separate download; start fetching when interest shows.
    const load = () => import('/assets/personal/castle/castle-gallery.js?v=1e7fa648e579b1ed');
    button.addEventListener('pointerenter', load, {once:true});
    button.addEventListener('focus', load, {once:true});
    button.addEventListener('click', async () => {
      if (button.dataset.loading !== undefined) return;
      button.dataset.loading = '';
      try {
        const {openCastle} = await load();
        await openCastle({photos:storyGallery, trigger:button});
      } finally {
        delete button.dataset.loading;
      }
    });
    wrap.append(button);
    stack.after(wrap);
  }
  function update() {
    pending = false;
    if (location.pathname === '/about' || location.pathname === '/about/') addStoryGallery();
    function setCover(img, project) {
      if (img.getAttribute('src') !== project.cover) img.setAttribute('src', project.cover);
      if (img.hasAttribute('srcset')) img.removeAttribute('srcset');
      img.alt = project.name + ' — ' + project.role;
    }
    projects.forEach(project => {
      document.querySelectorAll(`a[href="./${project.slug}"],a[href="/${project.slug}"]`).forEach(a => {
        a.querySelectorAll('img').forEach(img => setCover(img, project));
      });
    });
    const companyGrid = document.querySelector('.framer-1yix6hu');
    if (companyGrid && companies.length) {
      companyGrid.classList.add('personal-companies-grid');
      [...companyGrid.children].forEach((cell,index) => {
        if (index >= companies.length) { cell.classList.add('personal-company-hidden'); return; }
        cell.classList.add('personal-company-cell');
        const img = cell.querySelector('img');
        if (img) {
          const company=companies[index];
          if (img.getAttribute('src') !== company.logo) img.src=company.logo;
          img.removeAttribute('srcset'); img.alt=company.name;
        }
      });
    }
    // Original showreels are replaced with labeled engineering sketches.
    document.querySelectorAll('video[src]').forEach((video, i) => {
      video.pause();
      video.removeAttribute('autoplay');
      const holder = video.parentElement;
      const item = gallery[i % gallery.length];
      holder.style.backgroundImage = `url("${item.image}")`;
      holder.style.backgroundSize = 'cover';
      holder.style.backgroundPosition = 'center';
      video.setAttribute('aria-hidden', 'true');
      video.style.visibility = 'hidden';
      video.removeAttribute('src');
      video.load();
      holder.dataset.personalGallery = item.href;
      holder.dataset.personalGalleryLabel = item.title + '\n' + item.subtitle;
      holder.setAttribute('role', 'link'); holder.tabIndex = 0;
      holder.setAttribute('aria-label', item.title + ' — ' + item.subtitle);
      holder.addEventListener('click', event => { event.stopPropagation(); location.assign(item.href); }, true);
      holder.addEventListener('keydown', event => { if (event.key === 'Enter') location.assign(item.href); });
    });
    const project = projects.find(p => location.pathname === '/' + p.slug);
    if (project) {
      const heroImage = [...document.querySelectorAll('#main [data-framer-name="project stack"] img')].find(img => !img.closest('a') && img.getBoundingClientRect().width > 250);
      if (heroImage) setCover(heroImage, project);
    }
    if (project && !document.querySelector('.portfolio-case-root,.personal-live-link')) {
      const heading = document.querySelector('h1');
      const paragraphs = [...document.querySelectorAll('#main p')];
      const intro = paragraphs.find(p => p.textContent.length > 90);
      if (heading && intro) {
        const link = document.createElement('a');
        link.className = 'personal-live-link'; link.href = project.url;
        link.target = '_blank'; link.rel = 'noopener noreferrer';
        link.textContent = project.slug === 'falco' ? 'Company website ↗' : 'View live website ↗';
        const role = document.createElement('span');
        role.className = 'personal-project-role';
        role.textContent = 'My contribution: ' + project.role;
        intro.insertAdjacentElement('afterend', link);
        link.insertAdjacentElement('afterend', role);
      }
    }
    document.querySelectorAll('a[href*="pinterest.com"],a[href*="dribbble.com"],a[href*="unused-social"]').forEach(a => {
      a.style.display='none';
      if (a.parentElement.className.includes('-container')) a.parentElement.style.display='none';
    });
    document.querySelectorAll('#main a').forEach(a => {
      if (a.textContent.includes('More projects') && !a.dataset.personalPlaceholder) {
        a.dataset.personalPlaceholder='true'; a.setAttribute('aria-disabled','true');
        a.style.cursor='default'; a.tabIndex=-1;
        a.addEventListener('click',event=>{event.preventDefault();event.stopPropagation();},true);
      }
    });
    document.querySelectorAll('p').forEach(p => { if (p.textContent.startsWith('[CONFIRM]')) p.classList.add('personal-confirmation'); });
    document.querySelectorAll('a[href="#unused-social"]').forEach(a => a.setAttribute('aria-hidden', 'true'));
    // Framer's original head snippets must not identify the previous portfolio owner.
    document.querySelectorAll('meta[name="p:domain_verify"]').forEach(m => m.remove());
  }
  function schedule() { if (!pending) { pending = true; requestAnimationFrame(update); } }
  function start() {
    // Wait for the captured motion tree to mount before enhancing its DOM.
    if (!window.MotionIsMounted) { requestAnimationFrame(start); return; }
    requestAnimationFrame(() => {
      update();
      new MutationObserver(schedule).observe(document.body, { childList:true, subtree:true, attributes:true, attributeFilter:['src'] });
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start, {once:true});
  else start();
})();
