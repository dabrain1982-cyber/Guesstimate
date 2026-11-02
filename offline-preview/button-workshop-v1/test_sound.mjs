import assert from 'node:assert/strict';
import {createSound} from './sound.js';
const starts=[],messages=[];let requests=0;
class Context{
  constructor(){this.state='running';this.currentTime=0;this.destination={};}
  async resume(){}
  async decodeAudioData(){return {duration:1.2};}
  createGain(){return {gain:{setValueAtTime(){},linearRampToValueAtTime(){}},connect(){},disconnect(){}};}
  createBufferSource(){return {connect(){},stop(){},start(...args){starts.push(args);}};}
}
globalThis.window={AudioContext:Context};
globalThis.fetch=async()=>{requests++;return {ok:true,arrayBuffer:async()=>new ArrayBuffer(1)};};
const engine=createSound(message=>messages.push(message));
engine.configure([{id:'stone-scrape',name:'Stein-Kandidat',file:'stone.wav',button_offset:.05,button_duration:.38},
 {id:'wood-plank',name:'Holz-Kandidat',file:'wood.ogg',button_offset:0,button_duration:.4},
 {id:'click',name:'Klick',file:'click.ogg',button_offset:0,button_duration:.1}]);
const recipe=sound=>({settings:{sound,material:'stone',volume:20}});
await engine.play(recipe('stone-scrape'),'down');await engine.play(recipe('stone-scrape'),'up');
assert.equal(starts.length,1,'Release must not add a second material impact');assert.equal(requests,1);
await engine.play(recipe('stone-scrape'),'down');assert.equal(requests,1,'Decoded recordings should be reused');
let began,finish;const fetching=new Promise(resolve=>{began=resolve;});
globalThis.fetch=()=>{began();return new Promise(resolve=>{finish=resolve;});};
const pending=engine.play(recipe('wood-plank'),'down');await fetching;engine.stop();
finish({ok:true,arrayBuffer:async()=>new ArrayBuffer(1)});await pending;
assert.equal(starts.length,2,'Stop must cancel a recording that is still loading');
globalThis.fetch=async()=>({ok:false});await engine.play(recipe('click'),'down');
assert.match(messages.at(-1),/konnte nicht geladen/);assert.equal(starts.length,2);
await engine.play(recipe('off'),'down');assert.equal(starts.length,2);
console.log('Audio: single press, no release duplicate, cache, stopped pending playback and failed file passed.');
