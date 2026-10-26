(() => {
  const contact = {"email": "lugata619@gmail.com", "whatsapp": "+255749498117", "instagram": "https://www.instagram.com/zac_eye/", "inquiry": "Hi Isack, I came across your portfolio and would like to discuss a project.\n\nProject idea: \nWhat I need help with: \nTimeline: \nBudget range: "};
  const whatsapp = 'https://wa.me/' + contact.whatsapp.replace(/\D/g, '') + '?text=' + encodeURIComponent(contact.inquiry);
  const email = 'mailto:' + contact.email + '?subject=' + encodeURIComponent('Project enquiry') + '&body=' + encodeURIComponent(contact.inquiry);
  let dialog;
  function init() {
    dialog = document.createElement('dialog');
    dialog.className = 'portfolio-contact';
    dialog.setAttribute('aria-labelledby', 'contact-title');
    dialog.innerHTML = '<button class="contact-close" aria-label="Close contact options">×</button><h2 id="contact-title">Let’s build something.</h2><p>Have a project in mind? Choose how you’d like to get in touch.</p><a class="contact-option" data-contact-direct="true"><img src="/assets/identity/contact-email.svg?v=18b110fea435234d" alt=""><div>Email me<span></span></div></a><a class="contact-option" data-contact-direct="true" target="_blank" rel="noopener noreferrer"><img src="/assets/identity/contact-whatsapp.svg?v=18b110fea435234d" alt=""><div>Chat on WhatsApp<span></span></div></a>';
    const options = dialog.querySelectorAll('a');
    options[0].href = email;
    options[0].querySelector('span').textContent = contact.email;
    options[1].href = whatsapp;
    options[1].querySelector('span').textContent = contact.whatsapp;
    document.body.append(dialog);
    dialog.querySelector('button').addEventListener('click', () => dialog.close());
    dialog.addEventListener('click', event => { if (event.target === dialog) { const r=dialog.getBoundingClientRect(); if(event.clientX<r.left || event.clientX>r.right || event.clientY<r.top || event.clientY>r.bottom) dialog.close(); } });
    document.addEventListener('click', event => {
      const a = event.target.closest('a');
      if (!a || a.dataset.contactDirect || !a.getAttribute('href')?.startsWith('mailto:') || a.getAttribute('href').includes('?subject=')) return;
      event.preventDefault(); event.stopImmediatePropagation();
      if (!dialog.open) dialog.showModal();
    }, true);
  }
  function enhance() {
    document.querySelectorAll('a[href="https://github.com/GhostWire619"]').forEach(github => {
      const wrapper = github.parentElement;
      if (!wrapper.className.includes('-container')) return;
      const row = wrapper.parentElement;
      row.classList.add('portfolio-social-row');
      [['instagram', contact.instagram, 'Isack Lugata on Instagram — @zac_eye'], ['whatsapp', whatsapp, 'WhatsApp Isack Lugata — '+contact.whatsapp]].forEach(([name, href, label]) => {
        if (row.querySelector('[data-contact-social="'+name+'"]')) return;
        const clone = wrapper.cloneNode(true);
        clone.querySelectorAll('[id]').forEach(el => el.removeAttribute('id'));
        clone.querySelectorAll('[data-framer-appear-id]').forEach(el => el.removeAttribute('data-framer-appear-id'));
        const a=clone.querySelector('a');
        a.href=href; a.target='_blank'; a.rel='noopener noreferrer'; a.dataset.contactDirect='true'; a.dataset.contactSocial=name; a.setAttribute('aria-label',label);
        const img=a.querySelector('img');
        const dark=img?.getAttribute('src')?.includes('-dark');
        if (img) { img.src='/assets/identity/icon-'+name+'-'+(dark?'dark':'light')+'.svg'; img.removeAttribute('srcset'); img.alt=label; }
        row.append(clone);
      });
    });
  }
  function start() {
    if (document.querySelector('[data-framer-appear-id]') && !window.MotionIsMounted) { requestAnimationFrame(start); return; }
    init(); enhance();
    let pending=false;
    new MutationObserver(() => { if(pending)return; pending=true; requestAnimationFrame(()=>{pending=false;enhance();}); }).observe(document.body,{childList:true,subtree:true});
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded',start,{once:true});
  else start();
})();
