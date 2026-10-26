
(() => {
  const gallery = [{"title": "Nena AI", "subtitle": "Swahili speech \u00b7 Lab team project", "href": "/robotics#nena-ai", "image": "/assets/identity/cover-nena.svg?v=edcbd969365f51e4"}, {"title": "3D Solutions & Robotics", "subtitle": "Backend \u00b7 Former chairperson", "href": "/robotics", "image": "/assets/personal/robotics-live.opt.webp?v=edcbd969365f51e4"}, {"title": "TanStack Tanzania", "subtitle": "Backend development", "href": "/tanstack-tanzania", "image": "/assets/personal/tanstack-live.opt.webp?v=edcbd969365f51e4"}, {"title": "GloboExpats", "subtitle": "Mainly frontend development", "href": "/globoexpats", "image": "/assets/personal/globoexpats-live.opt.webp?v=edcbd969365f51e4"}];
  const projects = [{"slug": "ecofy", "name": "Ecofy Africa", "role": "Frontend & backend \u00b7 Co-founder, CEO & AI Lead", "url": "https://ecofy.co.tz/", "cover": "/assets/identity/cover-ecofy.svg?v=edcbd969365f51e4"}, {"slug": "wakili-msomi", "name": "Wakili Msomi", "role": "Frontend & backend development", "url": "https://wakilimsomi.sheriakiganjani.co.tz/", "cover": "/assets/identity/cover-wakili-msomi.svg?v=edcbd969365f51e4"}, {"slug": "globoexpats", "name": "GloboExpats", "role": "Mainly frontend development", "url": "https://globoexpats.com/", "cover": "/assets/identity/cover-globoexpats.svg?v=edcbd969365f51e4"}, {"slug": "habitek", "name": "Habitek", "role": "Frontend & backend development", "url": "https://habitek.co.tz/", "cover": "/assets/identity/cover-habitek.svg?v=edcbd969365f51e4"}, {"slug": "osher-market", "name": "Osher Market", "role": "Backend development", "url": "https://oshermarket.com/", "cover": "/assets/identity/cover-osher-market.svg?v=edcbd969365f51e4"}, {"slug": "falco", "name": "Falco Finance", "role": "Internal management backend development", "url": "https://falco.co.tz/", "cover": "/assets/identity/cover-falco.svg?v=edcbd969365f51e4"}, {"slug": "tanstack-tanzania", "name": "TanStack Tanzania", "role": "Backend development \u00b7 Lab project", "url": "https://tanstack.co.tz/", "cover": "/assets/identity/cover-tanstack-tanzania.svg?v=edcbd969365f51e4"}];
  const companies = [{"name": "Ecofy Africa", "logo": "/assets/identity/brand-ecofy.svg?v=edcbd969365f51e4", "url": "https://ecofy.co.tz/"}, {"name": "GloboExpats", "logo": "/assets/identity/brand-globo.svg?v=edcbd969365f51e4", "url": "https://globoexpats.com/"}, {"name": "Osher Market", "logo": "/assets/identity/brand-osher.svg?v=edcbd969365f51e4", "url": "https://oshermarket.com/"}, {"name": "Habitek", "logo": "/assets/identity/wordmark-habitek.svg?v=edcbd969365f51e4", "url": "https://habitek.co.tz/"}, {"name": "Falco Finance", "logo": "/assets/identity/brand-falco.svg?v=edcbd969365f51e4", "url": "https://falco.co.tz/"}, {"name": "Wakili Msomi", "logo": "/assets/identity/wordmark-wakili.svg?v=edcbd969365f51e4", "url": "https://wakilimsomi.sheriakiganjani.co.tz/"}, {"name": "TanStack Tanzania", "logo": "/assets/identity/tanstack-light.png?v=edcbd969365f51e4", "url": "https://tanstack.co.tz/"}, {"name": "UDSM Robotics Lab", "logo": "/assets/identity/brand-lab.svg?v=edcbd969365f51e4", "url": "https://robotics.udsm.ac.tz/"}];
  let pending = false;
  function update() {
    pending = false;
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
    if (project && !document.querySelector('.personal-live-link')) {
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
