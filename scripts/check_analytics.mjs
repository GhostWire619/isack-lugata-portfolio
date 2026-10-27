import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
const source = readFileSync(new URL('../backend/static/sidenotes/analytics.js',import.meta.url),'utf8');
function browser({hostname='isack.space', dnt='0', gpc=false}={}) {
  const requests=[], handlers={};
  const location={hostname,pathname:'/'};
  const document={hidden:false,referrer:'https://search.example/?q=private',documentElement:{scrollHeight:2000},
    addEventListener(name,fn){handlers[name]=fn;}};
  let id=0;
  const context={location,document,navigator:{doNotTrack:dnt,globalPrivacyControl:gpc,sendBeacon(url,body){requests.push({url,beacon:true,body});}},
    crypto:{randomUUID(){return 'page-'+(++id);}},Date,Math,JSON,Blob,scrollY:0,innerHeight:800,
    addEventListener(name,fn){handlers[name]=fn;},history:{pushState(_a,_b,path){location.pathname=path;},replaceState(_a,_b,path){location.pathname=path;}},
    fetch(url,options){requests.push({url,...options});return Promise.resolve({ok:true});}};
  vm.runInNewContext(source,context);
  return {context,requests,handlers};
}
for (const options of [{hostname:'localhost'},{dnt:'1'},{gpc:true}]) assert.equal(browser(options).requests.length,0);
const {context,requests,handlers}=browser();
assert.equal(requests.length,1);
assert.equal(requests[0].credentials,'omit');
assert.equal(JSON.parse(requests[0].body).path,'/');
context.history.pushState(null,'','/about');
assert.equal(requests.length,3); // flush old page, begin new page
const next=JSON.parse(requests[2].body);
assert.equal(next.path,'/about');
assert.notEqual(next.id,JSON.parse(requests[0].body).id);
context.history.replaceState(null,'','/about');
assert.equal(requests.length,3); // no duplicate for the same route
handlers.pagehide();
assert.equal(requests.at(-1).beacon,true);
console.log('Analytics checks passed: privacy signals, local exclusion, cookie-free requests, route tracking and page-view deduplication.');
