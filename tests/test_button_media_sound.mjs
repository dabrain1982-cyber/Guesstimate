import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createSound} from '../offline-preview/button-workshop-v1/sound.js';
const catalog=JSON.parse(fs.readFileSync(process.argv[2]||new URL('../docs/BUTTON_MEDIEN_INTEGRATION.json',import.meta.url),'utf8'));
const sounds=catalog.button_media?.sounds||catalog.sounds.filter(row=>row.media_short),byFile=new Map(sounds.map(row=>[row.file,row]));
assert.equal(sounds.length,13);
const starts=[],requests=[],messages=[];
class Context{
  constructor(){this.state='running';this.currentTime=0;this.destination={};}
  async resume(){}
  async decodeAudioData(data){const bytes=Buffer.from(data);let rate=0,length=0;for(let i=12;i+8<=bytes.length;){const name=bytes.toString('ascii',i,i+4),size=bytes.readUInt32LE(i+4);if(name==='fmt ')rate=bytes.readUInt32LE(i+16);if(name==='data')length=size;i+=8+size+(size%2);}return {duration:length/rate};}
  createGain(){return {gain:{setValueAtTime(){},linearRampToValueAtTime(){}},connect(){},disconnect(){}};}
  createBufferSource(){return {connect(){},stop(){},start(...args){starts.push(args);}};}
}
globalThis.window={AudioContext:Context};
globalThis.fetch=async url=>{requests.push(url);const row=byFile.get(path.basename(url));assert(row);const buffer=fs.readFileSync(path.resolve('offline-preview/game-workshop-v1/assets/media/sounds',row.id.slice(6)+'.wav'));return {ok:true,arrayBuffer:async()=>buffer.buffer.slice(buffer.byteOffset,buffer.byteOffset+buffer.byteLength)};};
const sound=createSound(message=>messages.push(message));sound.configure(catalog.sounds);
for(const row of sounds){const recipe={settings:{sound:row.id,material:'stone',volume:40}};const count=starts.length;await sound.play(recipe,'down');await sound.play(recipe,'up');assert.equal(starts.length,count+1);assert.equal(starts.at(-1)[1],0);assert(Math.abs(starts.at(-1)[2]-row.duration)<.0001);}
assert.equal(requests.length,13);assert.equal(starts.length,13);
await sound.play({settings:{sound:sounds[0].id,material:'stone',volume:40}},'down');assert.equal(requests.length,13);
await sound.play({settings:{sound:sounds[0].id,material:'stone',volume:0}},'down');assert.equal(starts.length,14);
sound.stop();console.log('Curated sounds: 13 exact local files, whole short clips, no second release, cached replay and silent volume passed.');
