(() => {
const notify=message=>window.previewNotify?.(message);
const rows=[{title:'When AI becomes part of everyday life.',topic:'Technology',status:'Published',views:'1,842',time:'4m 12s',updated:'24 Oct',image:'landscape.webp'}, {title:'The tools we build change how we think.',topic:'Technology',status:'Published',views:'986',time:'3m 08s',updated:'21 Oct',image:'lab.webp'},{title:'What the ocean can teach us about change.',topic:'Science & nature',status:'Scheduled',views:'–',time:'–',updated:'28 Oct',image:'coast.webp'},{title:'Why every good question deserves more time.',topic:'Ideas',status:'Draft',views:'–',time:'–',updated:'Today',image:'landscape.webp'}];
function renderRows(){const query=(document.querySelector('#post-search')?.value||'').toLowerCase();const status=document.querySelector('#post-status')?.value||'All statuses';const filtered=rows.filter(r=>r.title.toLowerCase().includes(query)&&(status==='All statuses'||r.status===status));function html(items){return items.map(r=>`<tr><td><a class="table-story" href="editor.html"><img src="assets/${r.image}" alt=""><div><strong>${r.title}</strong><small>${r.topic}</small></div></a></td><td><span class="badge ${r.status.toLowerCase()}">${r.status}</span></td><td>${r.views}</td><td>${r.time}</td><td>${r.updated}</td></tr>`).join('');}const overview=document.querySelector('#overview-posts');if(overview)overview.innerHTML=html(rows.slice(0,3));const all=document.querySelector('#all-posts');if(all)all.innerHTML=html(filtered);const empty=document.querySelector('#posts-empty');if(empty)empty.hidden=filtered.length>0;}
renderRows();
function showView(name){const panel=document.querySelector(`[data-panel="${name}"]`);if(!panel)return;document.querySelectorAll('[data-panel]').forEach(el=>el.hidden=el!==panel);document.querySelectorAll('[data-view]').forEach(el=>{el.removeAttribute('aria-current');if(el.dataset.view===name)el.setAttribute('aria-current','page');});document.querySelector('#breadcrumb').textContent=({posts:'Stories',connections:'AI connections',media:'Media library'})[name]||name[0].toUpperCase()+name.slice(1);history.replaceState(null,'','#'+name);setMenu(false);}
document.querySelectorAll('[data-view]').forEach(button=>button.addEventListener('click',()=>showView(button.dataset.view)));

document.querySelector('[data-open-posts]')?.addEventListener('click',()=>showView('posts'));
document.querySelector('#post-search')?.addEventListener('input',renderRows);
document.querySelector('#post-status')?.addEventListener('change',renderRows);
const phone=matchMedia('(max-width:760px)');
function setMenu(open){const sidebar=document.querySelector('.sidebar');sidebar.classList.toggle('open',open);sidebar.inert=phone.matches&&!open;document.querySelector('.mobile-menu')?.setAttribute('aria-expanded',String(open));}
setMenu(false);
if(location.hash)showView(location.hash.slice(1));
phone.addEventListener('change',()=>setMenu(false));
document.querySelector('.mobile-menu')?.addEventListener('click',()=>{setMenu(!document.querySelector('.sidebar').classList.contains('open'));});
document.querySelector('.sidebar-close')?.addEventListener('click',()=>{setMenu(false);document.querySelector('.mobile-menu')?.focus();});
document.addEventListener('keydown',event=>{if(event.key==='Escape'){setMenu(false);}});
document.querySelectorAll('[data-close-dialog]').forEach(button=>button.addEventListener('click',()=>button.closest('dialog').close()));
document.querySelectorAll('[data-auth-preview]').forEach(button=>button.addEventListener('click',()=>document.querySelector('#auth-dialog').showModal()));
document.querySelector('.period')?.addEventListener('change',()=>notify('Period changed in the preview. Figures are illustrative.'));
document.querySelector('#analytics-scope')?.addEventListener('change',event=>{const values=event.target.value==='Journal only'?['1,925','4,219']:event.target.value==='Portfolio only'?['1,243','1,961']:['2,846','6,180'];document.querySelectorAll('[data-scope-metric]').forEach((el,index)=>el.textContent=values[index]);});
const localKey='isack-blog-design-draft-v1';
function putLocal(key,value){try{localStorage.setItem(key,JSON.stringify(value));return true;}catch{notify('Browser storage is unavailable. Your preview could not be saved.');return false;}}
function getLocal(key){try{return JSON.parse(localStorage.getItem(key));}catch{return null;}}
document.querySelector('#settings-form')?.addEventListener('submit',event=>{event.preventDefault();if(putLocal('isack-blog-design-settings',Object.fromEntries(new FormData(event.target))))notify('Preview settings saved in this browser.');});
const settings=getLocal('isack-blog-design-settings');if(settings){Object.entries(settings).forEach(([name,value])=>{const input=document.querySelector(`#settings-form [name="${name}"]`);if(input)input.value=value;});}
function localImage(input,callback){const file=input.files[0];if(!file)return;if(!['image/jpeg','image/png','image/webp','image/avif','image/gif'].includes(file.type)){notify('Choose a JPG, PNG, WebP, AVIF, or GIF photograph.');return;}if(file.size>15*1024*1024){notify('Choose an image smaller than 15 MB for this preview.');return;}callback(URL.createObjectURL(file),file);}
document.querySelector('#library-upload')?.addEventListener('change',event=>localImage(event.target,(url,file)=>{const figure=document.createElement('figure');const image=document.createElement('img');image.src=url;image.alt=file.name;const caption=document.createElement('figcaption');caption.textContent=file.name+' · local preview';figure.append(image,caption);document.querySelector('.media-grid').prepend(figure);notify('Image added temporarily. Nothing has been uploaded.');}));
const body=document.querySelector('#edit-body');
if(body){
 const title=document.querySelector('#edit-title'),description=document.querySelector('#edit-description'),slug=document.querySelector('#edit-slug'),seo=document.querySelector('#edit-seo'),topic=document.querySelector('#edit-topic');
 function cleanHTML(html){const template=document.createElement('template');template.innerHTML=html;template.content.querySelectorAll('script,style,iframe,object,embed,link,meta,svg').forEach(el=>el.remove());template.content.querySelectorAll('*').forEach(el=>{for(const attr of [...el.attributes]){if(attr.name!=='src'&&attr.name!=='alt')el.removeAttribute(attr.name);if(attr.name==='src'&&!/^(assets\/|blob:)/.test(attr.value))el.removeAttribute('src');}});return template.innerHTML;}
 const saved=getLocal(localKey);
 if(saved){title.value=saved.title||title.value;description.value=saved.description||description.value;slug.value=saved.slug||slug.value;seo.value=saved.seo||seo.value;topic.value=saved.topic||topic.value;if(saved.body)body.innerHTML=cleanHTML(saved.body);document.querySelector('#save-state').textContent='Restored your draft from this browser.';}
 function update(){const count=body.innerText.trim().split(/\s+/).filter(Boolean).length;document.querySelector('#word-count').textContent=count+' words · '+Math.max(1,Math.ceil(count/220))+' min read';document.querySelector('#snippet-title').textContent=title.value||'Your story title';document.querySelector('#snippet-description').textContent=seo.value;document.querySelector('#snippet-url').textContent='isack.space/blog/'+slug.value;}
 function save(extra={}){const ok=putLocal(localKey,{title:title.value,description:description.value,slug:slug.value,seo:seo.value,topic:topic.value,body:cleanHTML(body.innerHTML),...extra});if(ok){document.querySelector('#save-state').textContent='Draft saved in this browser. Nothing is published.';}return ok;}
 [title,description,slug,seo,topic,body].forEach(el=>el.addEventListener('input',()=>{update();document.querySelector('#save-state').textContent='Unsaved changes in this preview.';}));
 document.querySelector('#save-draft').addEventListener('click',()=>{if(save())notify('Draft saved locally.');});
 document.querySelectorAll('[data-command]').forEach(button=>{button.addEventListener('mousedown',event=>event.preventDefault());button.addEventListener('click',()=>{body.focus();document.execCommand(button.dataset.command,false,button.dataset.value||null);update();});});
 document.querySelector('#insert-picture').addEventListener('click',()=>document.querySelector('#inline-image').click());
 document.querySelector('#inline-image').addEventListener('change',event=>localImage(event.target,(url,file)=>{const img=document.createElement('img');img.src=url;img.alt=file.name;body.append(img);notify('Picture added locally. Uploaded pictures will be compressed by the backend.');}));
 document.querySelector('#cover-input').addEventListener('change',event=>localImage(event.target,(url)=>{document.querySelector('#cover-preview').src=url;notify('Cover changed for this preview session.');}));
 document.querySelector('#preview-draft').addEventListener('click',()=>{document.querySelector('#draft-preview-title').textContent=title.value;document.querySelector('#draft-preview-description').textContent=description.value;document.querySelector('#draft-preview-body').innerHTML=cleanHTML(body.innerHTML);document.querySelector('#draft-preview-cover').src=document.querySelector('#cover-preview').src;document.querySelector('#draft-dialog').showModal();});
 document.querySelector('#publish-preview').addEventListener('click',()=>document.querySelector('#publish-dialog').showModal());
 document.querySelector('#save-schedule').addEventListener('click',()=>{const date=document.querySelector('#schedule-date').value;if(!date){notify('Choose a date and time for the publishing plan.');return;}if(new Date(date+'+03:00')<=new Date()){notify('Choose a future date and time.');return;}if(save({plannedPublishAt:date,timezone:'Africa/Nairobi'})){document.querySelector('#publish-dialog').close();notify('Plan saved locally. No publishing task has been scheduled.');}});
 update();
}

})();
