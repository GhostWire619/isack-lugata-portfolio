(() => {
 const toggle=document.querySelector('.search-toggle');
 toggle?.addEventListener('click',()=>{const form=document.querySelector('#search-panel');form.hidden=!form.hidden;toggle.setAttribute('aria-expanded',String(!form.hidden));if(!form.hidden)form.querySelector('input').focus();});
 let timer;
 document.querySelectorAll('[data-copy-link]').forEach(button=>button.addEventListener('click',async()=>{
  const toast=document.querySelector('.toast');
  try{await navigator.clipboard.writeText(document.querySelector('link[rel="canonical"]').href);toast.textContent='Article link copied.';}catch{toast.textContent='Copy this page’s address from your browser to share it.';}
  clearTimeout(timer);toast.hidden=false;timer=setTimeout(()=>toast.hidden=true,4000);
 }));
 const progress=document.querySelector('.progress');
 if(progress){let pending=false;const update=()=>{pending=false;const height=document.documentElement.scrollHeight-innerHeight;progress.style.width=(height>0?Math.min(100,100*scrollY/height):100)+'%';};document.addEventListener('scroll',()=>{if(!pending){pending=true;requestAnimationFrame(update);}},{passive:true});update();}
})();
