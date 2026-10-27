import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
const source = readFileSync(new URL('../backend/static/sidenotes/clarity.js', import.meta.url), 'utf8');
function browser({hostname='isack.space', pathname='/blog/', dnt='0', gpc=false, consent=null}={}) {
  const scripts=[], idle=[], events={}, buttons={}, status={};
  const storage=new Map(consent ? [['journal-clarity-consent',consent]] : []);
  for (const value of ['granted','denied']) buttons[value]={dataset:{clarityConsent:value},addEventListener(_name,fn){this.click=fn;}};
  const context={location:{hostname,pathname},navigator:{doNotTrack:dnt,globalPrivacyControl:gpc},
    localStorage:{getItem:key=>storage.get(key),setItem:(key,value)=>storage.set(key,value)},
    document:{querySelector:()=>status,querySelectorAll:()=>Object.values(buttons),
      createElement:()=>({}),head:{appendChild:script=>scripts.push(script)}},
    addEventListener:(name,fn)=>events[name]=fn,requestIdleCallback:fn=>idle.push(fn)};
  context.window=context;
  vm.runInNewContext(source,context);
  return {context,scripts,idle,events,buttons,status};
}
for (const options of [{hostname:'localhost'},{hostname:'preview.example'},{pathname:'/admin/ai/'},
  {pathname:'/security/verify/'},{pathname:'/oauth/token/'},{pathname:'/mcp'}, {dnt:'1'},{gpc:true}]) {
  const result=browser(options);
  assert.equal(result.idle.length,0);
  assert.equal(result.scripts.length,0);
  assert.equal(result.context.clarity,undefined);
}
const page=browser();
assert.equal(page.scripts.length,0);
assert.equal(page.context.clarity.q[0][0],'consentv2');
assert.equal(page.context.clarity.q[0][1].analytics_Storage,'denied');
page.idle[0]();
assert.equal(page.scripts[0].src,'https://www.clarity.ms/tag/z485ii73vk');
assert.equal(page.scripts[0].async,true);
assert.equal(page.scripts[1].src,'https://www.googletagmanager.com/gtag/js?id=G-XWWT4YVE88');
assert.equal(page.scripts[1].async,true);
assert.equal(page.context.dataLayer[0][0],'consent');
assert.equal(page.context.dataLayer[0][1],'default');
assert.equal(page.context.dataLayer[0][2].analytics_storage,'denied');
assert.equal(page.context.dataLayer[0][2].ad_storage,'denied');
assert.equal(page.context.dataLayer[2][0],'config');
assert.equal(page.context.dataLayer[2][1],'G-XWWT4YVE88');
page.buttons.granted.click();
assert.equal(page.context.clarity.q.at(-1)[1].analytics_Storage,'granted');
assert.equal(page.context.clarity.q.at(-1)[1].ad_Storage,'denied');
assert.equal(page.context.dataLayer.at(-1)[2].analytics_storage,'granted');
assert.equal(page.context.dataLayer.at(-1)[2].ad_storage,undefined);
page.buttons.denied.click();
assert.equal(page.context.clarity.q.at(-1)[1].analytics_Storage,'denied');
assert.equal(page.context.dataLayer.at(-1)[2].analytics_storage,'denied');
page.events.storage({key:'journal-clarity-consent',newValue:'granted'});
assert.equal(page.context.clarity.q.at(-1)[1].analytics_Storage,'granted');
vm.runInNewContext(source,page.context);
assert.equal(page.idle.length,1);
assert.equal(browser({consent:'granted'}).context.clarity.q[0][1].analytics_Storage,'granted');
console.log('Clarity and GA4 checks passed: privacy signals, private/local exclusions, deferred single loading, consent defaults and changes. No external requests made.');
