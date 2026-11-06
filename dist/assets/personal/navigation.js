(() => {
  const caseRoutes = new Set(["/ecofy", "/wakili-msomi", "/globoexpats", "/habitek", "/osher-market", "/falco", "/tanstack-tanzania"]);
  const projectDescriptions = {"/ecofy": "Farm planning and agricultural guidance, from interface to AI.", "/wakili-msomi": "Frontend and backend for a Swahili legal-assistance platform.", "/globoexpats": "Frontend for a marketplace connecting people settling in Tanzania.", "/habitek": "Frontend and backend connecting property discovery with management.", "/osher-market": "Backend application services for a commerce platform.", "/falco": "The backend behind an internal business management system.", "/tanstack-tanzania": "Backend services connecting students with resources and opportunities."};
  document.addEventListener('click', event => {
    if (['localhost','127.0.0.1'].includes(location.hostname) || navigator.doNotTrack === '1' || navigator.globalPrivacyControl || typeof window.gtag !== 'function') return;
    const link = event.target.closest('a[href]');
    if (!link) return;
    const url = new URL(link.href, location.href);
    if (url.origin === location.origin && caseRoutes.has(url.pathname)) {
      window.gtag('event','portfolio_project_open',{project:url.pathname.slice(1),source_page:location.pathname});
    } else if (url.hostname === 'wa.me' || url.protocol === 'mailto:') {
      window.gtag('event','portfolio_contact_click',{channel:url.hostname === 'wa.me' ? 'whatsapp' : 'email',source_page:location.pathname});
    } else if (url.hostname === 'nenaai.ecofy.co.tz') {
      window.gtag('event','portfolio_demo_open',{project:'nena-ai',source_page:location.pathname});
    }
  });
  const testimonialsMarkup = `<span class="engagement-eyebrow">Testimonials · Sample preview</span><h2>Good work starts with good conversations.</h2><p class="testimonial-note">Illustrative quotes, not actual client endorsements. Approved client feedback is coming soon.</p><div class="testimonial-grid"><blockquote><span class="sample-label">Sample quote</span><p>“Isack made the technical decisions easy to understand. We could review progress, ask questions, and stay involved throughout the build.”</p><cite>Client name & company to be added</cite></blockquote><blockquote><span class="sample-label">Sample quote</span><p>“He took time to understand how our team works. The conversations were practical, and the handover gave us a clear starting point for what comes next.”</p><cite>Client name & company to be added</cite></blockquote></div><a href="/pricing" class="engagement-contact">Find a package for your project ↗</a>`;
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
        if (a.closest('.framer-lvzy8y') && !a.textContent.includes('More projects')) {
          a.dataset.projectDescription = projectDescriptions[route];
        }
        a.closest('[class*="-container"]')?.classList.add('portfolio-project-tile');
      });
    });
    document.querySelectorAll('.framer-lvzy8y a').forEach(a => {
      if (!a.textContent.includes('More projects')) return;
      a.removeAttribute('href');
      a.removeAttribute('data-project-description');
      a.removeAttribute('aria-label');
      a.setAttribute('role','note');
      a.setAttribute('aria-disabled','true');
      a.tabIndex = -1;
      a.style.cursor = 'default';
      if (!a.dataset.placeholderGuard) {
        a.dataset.placeholderGuard = 'true';
        a.addEventListener('click', e => { e.preventDefault(); e.stopPropagation(); }, true);
      }
    });
    const services = document.querySelector('[data-framer-name="areas"]');
    if (services && !services.id) services.id = 'services';
    if (services && !document.querySelector('.portfolio-testimonials')) {
      const section = document.createElement('section');
      section.className = 'portfolio-testimonials';
      section.innerHTML = testimonialsMarkup;
      services.insertAdjacentElement('afterend', section);
    }
    const explorations = document.querySelector('[data-framer-name="explorations"]');
    if (explorations && !explorations.querySelector('.lab-explorations')) {
      const grid = document.createElement('div');
      grid.className = 'lab-explorations';
      grid.innerHTML = `<a href="https://nenaai.ecofy.co.tz/" target="_blank" rel="noopener noreferrer"><span class="engagement-eyebrow">Live product · Kiswahili & English</span><h3>Nena AI</h3><p>Turn words and product photos into motion ads and marketing visuals, with voice-overs in Kiswahili or English.</p><span class="exploration-flow" aria-label="Nena product workflow">Words & photos <span aria-hidden="true">→</span> Ad studio <span aria-hidden="true">→</span> Ready to share</span><span class="exploration-link">Try Nena AI ↗</span></a><a href="/robotics"><span class="engagement-eyebrow">UDSM · Leadership & engineering</span><h3>Inside the robotics lab</h3><p>My work as former chairperson and backend contributor, alongside the team behind Nena AI and TanStack Tanzania.</p><img src="/assets/personal/robotics-live.opt.webp?v=b185cdb7dd2eff5d" alt="UDSM 3D Solutions and Robotics Lab public website" loading="lazy" width="1440" height="900"><span class="exploration-link">Explore the lab work ↗</span></a>`;
      explorations.append(grid);
    }
    const intro = document.querySelector('.framer-180tc9q');
    if (intro && !document.querySelector('.portfolio-mobile-jumps')) {
      const jumps = document.createElement('nav');
      jumps.className = 'portfolio-mobile-jumps';
      jumps.setAttribute('aria-label','On this page');
      jumps.innerHTML = '<a href="#projects">Selected work <span aria-hidden="true">↓</span></a><a href="#services">What I do <span aria-hidden="true">↓</span></a>';
      intro.append(jumps);
    }
  }
  function start() {
    if (document.querySelector('[data-framer-appear-id]') && !window.MotionIsMounted) { requestAnimationFrame(start); return; }
    fixLinks();
    let pending = false;
    new MutationObserver(() => {
      if (pending) return;
      pending = true;
      requestAnimationFrame(() => { pending = false; fixLinks(); });
    }).observe(document.body, {childList:true, subtree:true});
  }
  start();
})();
