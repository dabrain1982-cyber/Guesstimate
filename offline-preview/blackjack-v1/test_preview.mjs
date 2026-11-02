import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
const source=fs.readFileSync(new URL('./blackjack-tisch.html',import.meta.url),'utf8').match(/<script>([\s\S]*?)<\/script>/)[1];
const nodes=new Map(),handlers={},timers=new Map(),windowHandlers={};let timerNumber=0,saves=0,lastSnapshot;
const node=selector=>{if(!nodes.has(selector))nodes.set(selector,{innerHTML:'',textContent:'',hidden:false,setAttribute(){},focus(){},querySelectorAll(){return[]}});return nodes.get(selector)};
const root={dataset:{},style:{setProperty(){}},querySelector:node,querySelectorAll(){return[]},addEventListener(name,fn){handlers[name]=fn}};
class AudioContext {
  state='running';currentTime=0;destination={};
  resume(){return Promise.resolve()}
  decodeAudioData(){return Promise.resolve({duration:.2})}
  createGain(){return {gain:{setValueAtTime(){},linearRampToValueAtTime(){}},connect(){},disconnect(){}}}
  createBufferSource(){return {connect(){},start(){},stop(){}}}
  createDynamicsCompressor(){return {threshold:{},knee:{},ratio:{},attack:{},release:{},connect(){}}}
}
const sandbox={document:{getElementById(){return root}},Intl,Number,structuredClone,atob,Uint8Array,clearTimeout(id){timers.delete(id)},setTimeout(fn){timers.set(++timerNumber,fn);return timerNumber},window:{AudioContext,addEventListener(name,fn){windowHandlers[name]=fn},openai:{setWidgetState(snapshot){saves++;assert.ok(saves<30,'state echo loop');lastSnapshot=structuredClone(snapshot);queueMicrotask(()=>windowHandlers['openai:set_globals']?.({detail:{globals:{widgetState:structuredClone(snapshot)}}}));return Promise.resolve()}}}};
vm.runInNewContext(source,sandbox);
const click=action=>handlers.click({target:{closest(){return {dataset:{action},disabled:false}}}});
const flush=()=>new Promise(resolve=>setImmediate(resolve));
click('stand');await flush();await flush();
assert.equal(timers.size,1,'one bank timer after own state echo');
assert.equal(saves,1,'own echo must not save again');
assert.deepEqual(JSON.parse(root.dataset.soundLog),['card-move']);
windowHandlers['openai:set_globals']({detail:{globals:{widgetState:structuredClone(lastSnapshot)}}});await flush();
assert.equal(timers.size,1,'repeated echoed state must not restart bank');
assert.deepEqual(JSON.parse(root.dataset.soundLog),['card-move']);
const finish=[...timers.values()][0];timers.clear();finish();await flush();await flush();
assert.equal(saves,2);assert.equal(timers.size,0);
assert.deepEqual(JSON.parse(root.dataset.soundLog),['card-move','card-place','lose']);
assert.match(node('[data-message]').textContent,/Verloren/);
assert.equal(root.dataset.soundMix,'balanced-v1');
console.log('State-echo regression passed: one bank turn; exactly one move, placement and result sound.');

// A button must complete its shared press animation before controls are replaced.
click('again');click('split');click('stand');click('stand');
assert.equal(timers.size,1);const finishSplit=[...timers.values()][0];timers.clear();finishSplit();
await flush();await flush();assert.match(node('[data-message]').textContent,/Hand 2/);
const splitResult=node('[data-message]').textContent;const savesBefore=saves;
let finishAnimation;const finished=new Promise(resolve=>{finishAnimation=resolve;});
const nextRound={dataset:{action:'new-round'},disabled:false,isConnected:true,querySelector(){return {getAnimations(){return [{finished}]}}}};
const event={target:{closest(){return nextRound}}};
handlers.click(event);handlers.click(event);
assert.equal(root.dataset.buttonPending,'new-round');
assert.equal(node('[data-message]').textContent,splitResult,'press must remain visible');
assert.equal(saves,savesBefore,'no early state change or repeated click');
finishAnimation();await flush();await flush();
assert.match(node('[data-message]').textContent,/Einsatz/);
assert.equal(lastSnapshot.privateContent.game.phase,'betting');
assert.equal(lastSnapshot.privateContent.game.active,0,'split hand index resets');
assert.equal(lastSnapshot.privateContent.game.hands.length,1);
assert.equal(saves,savesBefore+1,'one round change after animation');
console.log('Button regression passed: complete animation, duplicate-click guard, new round after split.');

const handBeforeBackChange=JSON.stringify(lastSnapshot.privateContent.game);
handlers.change({target:{value:'Nachtblau & Messing',matches(selector){return selector==='[data-card-back]'}}});
await flush();await flush();
assert.equal(lastSnapshot.privateContent.design.back,'Nachtblau & Messing');
assert.equal(JSON.stringify(lastSnapshot.privateContent.game),handBeforeBackChange,'back choice must not change the hand');
const savesBeforeInvalidBack=saves;
handlers.change({target:{value:'unknown-back',matches(selector){return selector==='[data-card-back]'}}});
await flush();assert.equal(saves,savesBeforeInvalidBack,'unknown back is ignored');
console.log('Card-back regression passed: choice persists without changing gameplay.');
