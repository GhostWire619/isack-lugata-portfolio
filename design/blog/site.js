(() => {
const toast=document.querySelector('.toast');
let toastTimer;
function notify(message){if(!toast)return;clearTimeout(toastTimer);toast.textContent=message;toast.hidden=false;toastTimer=setTimeout(()=>toast.hidden=true,4000);}
window.previewNotify=notify;
const searchButton=document.querySelector('.search-toggle');
searchButton?.addEventListener('click',()=>{const panel=document.querySelector('#search-panel');panel.hidden=!panel.hidden;searchButton.setAttribute('aria-expanded',String(!panel.hidden));if(!panel.hidden)panel.querySelector('input').focus();});
let topic='All';
function filter(){const query=(document.querySelector('#story-search')?.value||'').toLowerCase();let visible=0;document.querySelectorAll('[data-topic]').forEach(el=>{el.hidden=(topic!=='All'&&el.dataset.topic!==topic)||!(el.textContent+' '+el.dataset.search).toLowerCase().includes(query);if(!el.hidden)visible++;});const count=document.querySelector('#result-count');if(count)count.textContent=topic==='All'&&!query?'Ideas worth exploring':`${visible} ${visible===1?'story':'stories'} found`;const empty=document.querySelector('#no-results');if(empty)empty.hidden=visible!==0;}
document.querySelectorAll('[data-filter]').forEach(a=>a.addEventListener('click',event=>{event.preventDefault();topic=a.dataset.filter;document.querySelectorAll('[data-filter]').forEach(el=>el.removeAttribute('aria-current'));a.setAttribute('aria-current','page');filter();}));
document.querySelector('#story-search')?.addEventListener('input',filter);
document.querySelectorAll('[data-copy-link]').forEach(button=>button.addEventListener('click',async()=>{try{await navigator.clipboard.writeText(location.href);notify('Story link copied.');}catch{notify('Copy this page’s address from your browser to share it.');}}));
const stories={building:{title:'The tools we build change how we think.',category:'Technology',dek:'What the design of our everyday tools tells us about the way we work.',image:'lab.webp',credit:'Illustrative robotics artwork / existing portfolio asset'},coast:{title:'What the ocean can teach us about change.',category:'Science & nature',dek:'Exploring the systems and cycles that shape a world in constant motion.',image:'coast.webp',credit:'Illustrative photograph / Unsplash'},notes:{title:'Why every good question deserves more time.',category:'Ideas',dek:'The value of looking beyond the first answer.',image:'landscape.webp',credit:'Illustrative photograph / Unsplash'}};
const story=stories[new URLSearchParams(location.search).get('story')];
if(story&&document.querySelector('#article-title')){document.querySelector('#article-title').textContent=story.title;document.querySelector('#article-category').textContent=story.category;document.querySelector('#article-dek').textContent=story.dek;document.querySelector('#article-image').src='assets/'+story.image;document.querySelector('#article-image').alt=story.title;document.querySelector('#image-credit').textContent=story.credit;document.title=story.title+' · Side notes';}
if('IntersectionObserver'in window&&!matchMedia('(prefers-reduced-motion:reduce)').matches){const observer=new IntersectionObserver(entries=>entries.forEach(entry=>{if(entry.isIntersecting){entry.target.classList.add('reveal');observer.unobserve(entry.target);}}),{threshold:.06});document.querySelectorAll('.post-card,.journal-about').forEach(el=>observer.observe(el));}
const progress=document.querySelector('.progress');
if(progress){const update=()=>{const body=document.documentElement;progress.style.width=`${Math.max(0,Math.min(100,100*scrollY/(body.scrollHeight-innerHeight)))}%`;};document.addEventListener('scroll',update,{passive:true});update();}

})();
