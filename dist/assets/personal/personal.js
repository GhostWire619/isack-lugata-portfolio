
(() => {
  const posters = ["/assets/personal/robotics-0.svg", "/assets/personal/rag-platform-0.svg", "/assets/personal/infrastructure-0.svg", "/assets/personal/ecofy-0.svg"];
  let pending = false;
  function update() {
    pending = false;
    // Original showreels are replaced with labeled engineering sketches.
    document.querySelectorAll('video[src]').forEach((video, i) => {
      video.pause();
      video.removeAttribute('autoplay');
      const holder = video.parentElement;
      holder.style.backgroundImage = `url("${posters[i % posters.length]}")`;
      holder.style.backgroundSize = 'cover';
      holder.style.backgroundPosition = 'center';
      video.setAttribute('aria-hidden', 'true');
      video.style.visibility = 'hidden';
      video.removeAttribute('src');
      video.load();
    });
    document.querySelectorAll('p').forEach(p => { if (p.textContent.startsWith('[CONFIRM]')) p.classList.add('personal-confirmation'); });
    document.querySelectorAll('a[href="#unused-social"]').forEach(a => a.setAttribute('aria-hidden', 'true'));
    // Framer's original head snippets must not identify the previous portfolio owner.
    document.querySelectorAll('meta[name="p:domain_verify"]').forEach(m => m.remove());
  }
  function schedule() { if (!pending) { pending = true; requestAnimationFrame(update); } }
  document.addEventListener('DOMContentLoaded', () => {
    update();
    new MutationObserver(schedule).observe(document.body, { childList:true, subtree:true, attributes:true, attributeFilter:['src'] });
  });
})();
