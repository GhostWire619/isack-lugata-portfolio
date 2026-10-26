(() => {
 const reduced = matchMedia('(prefers-reduced-motion: reduce)');
 const observed = new WeakSet();
 const observer = new IntersectionObserver(entries => {
  entries.forEach(entry => {
   const el=entry.target;
   if(!entry.isIntersecting){el.dataset.revealOutside='true';return;}
   if(el.dataset.revealOutside==='true' && !reduced.matches){
    el.getAnimations().filter(a=>a.id==='portfolio-reveal').forEach(a=>a.cancel());
    const from=entry.boundingClientRect.top<0?-14:14;
    el.animate([{opacity:.35,translate:`0 ${from}px`},{opacity:1,translate:'0 0'}],{duration:420,easing:'cubic-bezier(.2,.7,.2,1)',id:'portfolio-reveal'});
   }
   el.dataset.revealOutside='false';
  });
 },{threshold:0});
 function scan(){
  document.querySelectorAll('[data-case-reveal],.portfolio-project-tile,[data-framer-appear-id]').forEach(el=>{
   if(observed.has(el) || el.closest('#hero,.framer-QEZlT,.framer-KEAwE'))return;
   const bounds=el.getBoundingClientRect();
   if(bounds.width<80 || bounds.height<50)return;
   observed.add(el);
   const r=el.getBoundingClientRect();
   el.dataset.revealOutside=String(r.top>=innerHeight || r.bottom<=0);
   observer.observe(el);
  });
  bindRail();
 }
 function bindRail(){
  const reduceMotion=reduced.matches;
  const rail = document.querySelector('.more-work-rail');
  if (!rail || rail.dataset.railBound) return;
  rail.dataset.railBound = 'true';
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
 }
 let pending=false;
 function schedule(){if(pending)return;pending=true;requestAnimationFrame(()=>{pending=false;scan();});}
 new MutationObserver(schedule).observe(document.body,{childList:true,subtree:true});
 document.addEventListener('portfolio:route',schedule);
 scan();
})();
