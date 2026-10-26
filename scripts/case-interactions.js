(() => {
  const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (!reduceMotion && 'IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      });
    }, {threshold:.08});
    document.querySelectorAll('[data-case-reveal]').forEach(el => {
      if (el.getBoundingClientRect().top < innerHeight) return;
      el.classList.add('reveal-pending');
      observer.observe(el);
    });
  }
  const rail = document.querySelector('.more-work-rail');
  if (!rail) return;
  const previous = document.querySelector('[data-rail-previous]');
  const next = document.querySelector('[data-rail-next]');
  function update() {
    previous.disabled = rail.scrollLeft < 2;
    next.disabled = rail.scrollLeft >= rail.scrollWidth - rail.clientWidth - 2;
  }
  function move(direction) {
    const card = rail.querySelector('a');
    rail.scrollBy({left:direction * (card.getBoundingClientRect().width + 16), behavior:reduceMotion ? 'instant' : 'smooth'});
  }
  previous.addEventListener('click',()=>move(-1));
  next.addEventListener('click',()=>move(1));
  rail.addEventListener('scroll',update,{passive:true});
  window.addEventListener('resize',update);
  update();
})();
