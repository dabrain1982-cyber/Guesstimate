import assert from 'node:assert/strict';
import {fallStep} from './motion.js';
for(const gravity of [2,10,20])for(const bounce of [0,.35,.8]) {
  let body={y:3,velocity:2};let elapsed=0;
  while(elapsed<6&&!body.resting){body=fallStep(body,1/120,gravity,bounce,.25);assert.ok(body.y>=.25);assert.ok(Number.isFinite(body.velocity));elapsed+=1/120;}
  assert.ok(body.y>=.25);
  if(bounce<=.35)assert.equal(body.resting,true,'Normal fall probe should come to rest');
}
console.log('Fallprobe: Tischkontakt, Grenzwerte und Stillstand geprüft.');
