// Verify lazy slots without loading Google or creating real impressions.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';

const source = readFileSync(new URL('../backend/static/sidenotes/advertising.js',import.meta.url),'utf8');
const makeSlot = visible => ({visible, inserted:0, placement:{hidden:false}, unit:{status:null,getAttribute(){return this.status;}},
  get offsetWidth(){return this.visible?300:0;}, getClientRects(){return this.visible?[{}]:[];},
  closest(){return this.placement;},
  querySelector(selector){return selector==='ins.adsbygoogle'?this.unit:{content:{cloneNode(){return {};}}};},
  append(){this.inserted++;}});
const mutations=[];
const hiddenRail = makeSlot(false), horizontal = makeSlot(true);
let observerCallback;
const buttons = [{hidden:true, addEventListener(event, callback){this.click = callback;}}];
const scope = {window:{adsbygoogle:[]},document:{querySelectorAll(selector){return selector==='[data-ad-container]'?[hiddenRail,horizontal]:buttons;}},
  console, addEventListener(){}, WeakSet, MutationObserver:class {constructor(callback){this.callback=callback;mutations.push(this);} observe(){} disconnect(){}}, IntersectionObserver:class {constructor(callback){observerCallback=callback;} observe(){} unobserve(){}}};
scope.window.IntersectionObserver=scope.IntersectionObserver;
scope.window.MutationObserver=scope.MutationObserver;
vm.runInNewContext(source,scope);
const entries=[hiddenRail,horizontal].map(target=>({target,isIntersecting:true}));
observerCallback(entries);
observerCallback(entries);
assert.equal(scope.window.adsbygoogle.length,1);
assert.equal(horizontal.inserted,1);
assert.equal(hiddenRail.inserted,0);
hiddenRail.visible=true;
observerCallback(entries);
assert.equal(scope.window.adsbygoogle.length,2);
assert.equal(hiddenRail.inserted,1);
horizontal.unit.status='filled';
mutations[0].callback();
assert.equal(horizontal.placement.hidden,false,'Filled ads stay visible');
horizontal.unit.status='unfilled';
mutations[0].callback();
assert.equal(horizontal.placement.hidden,true,'Confirmed empty ads lose their entire wrapper');
assert.equal(hiddenRail.placement.hidden,false,'Pending ads stay visible');
let reopened=false;
scope.window.googlefc.showRevocationMessage=()=>{reopened=true;};
scope.window.googlefc.callbackQueue[0].CONSENT_API_READY();
assert.equal(buttons[0].hidden,false);
buttons[0].click();
scope.window.googlefc.callbackQueue.at(-1).CONSENT_API_READY();
assert.equal(reopened,true);
console.log('Advertising loader checks passed: hidden rail skipped, slots requested once, CMP preferences reopen.');
