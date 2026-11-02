import assert from 'node:assert/strict';
import {chipValues,describeJetons,planJetonMotion} from '../static/blackjack-jeton-motion.js';

const snapshot=(phase='turn',round=1,hands=[{bet:500,net:null}],insurance=0,insurance_net=null,bets=[])=>({game:{phase,round,bet_round:round+1,currency:'test-ikuehe',bets,players:hands.length?[{seat:2,hands,insurance,insurance_net}]:[]}});
const view=(...args)=>describeJetons(snapshot(...args));
const opening=view();
let checks=0;
function check(name,body){body();checks++;}
check('no replay on hydration',()=>assert.deepEqual(planJetonMotion(null,opening),[]));
check('polls do not repeat placements',()=>assert.deepEqual(planJetonMotion(opening,structuredClone(opening)),[]));
check('first bet lands once even when the solo round starts immediately',()=>{
 const before=view('betting',0,[]),events=planJetonMotion(before,opening);
 assert.deepEqual(events.map(e=>[e.kind,e.added,e.round]),[['place',500,1]]);
});
check('queued wager is not re-thrown during dealing',()=>{
 const before=view('betting',0,[],0,null,[{seat:2,amount:500}]);
 assert.deepEqual(planJetonMotion(before,opening),[]);
});
check('doubling adds only the extra wager',()=>assert.equal(planJetonMotion(opening,view('turn',1,[{bet:1000}]))[0].added,500));
check('splitting adds only the new hand',()=>assert.equal(planJetonMotion(opening,view('turn',1,[{bet:500},{bet:500}]))[0].added,500));
check('insurance adds a single black 250 chip',()=>assert.equal(planJetonMotion(opening,view('insurance',1,[{bet:500}],250))[0].added,250));
const outcome=(hands,insurance=0,insuranceNet=0)=>view('result',1,hands,insurance,insuranceNet).results[0];
check('win doubles the wager before returning it',()=>{
 const r=outcome([{bet:500,net:500}]);assert.deepEqual([r.lost,r.returned,r.profit],[0,500,500]);
});
check('natural includes the black 250 portion',()=>{
 const r=outcome([{bet:500,net:750}]);assert.deepEqual(chipValues(r.returned+r.profit),[500,500,250]);
});
check('loss sends only the stake to the bank',()=>{
 const r=outcome([{bet:500,net:-500}]);assert.deepEqual([r.lost,r.returned,r.profit],[500,0,0]);
});
check('push returns the stake without a fake profit',()=>{
 const r=outcome([{bet:500,net:0}]);assert.deepEqual([r.lost,r.returned,r.profit],[0,500,0]);
});
check('surrender divides loss and refund into 250 portions',()=>{
 const r=outcome([{bet:500,net:-250}]);assert.deepEqual([r.lost,r.returned,r.profit],[250,250,0]);
});
check('split hands keep both a win and loss even with zero net',()=>{
 const r=outcome([{bet:500,net:-500},{bet:500,net:500}]);assert.deepEqual([r.lost,r.returned,r.profit],[500,500,500]);
});
check('late bank blackjack returns split/double additions',()=>{
 const r=outcome([{bet:1000,net:-500},{bet:1000,net:0}]);assert.deepEqual([r.lost,r.returned,r.profit],[500,1500,0]);
});
check('insurance and main hand move separately',()=>{
 const r=outcome([{bet:500,net:-500}],250,500);assert.deepEqual([r.amount,r.lost,r.returned,r.profit],[750,500,250,500]);
});
check('result transition runs once',()=>{
 const result=view('result',1,[{bet:500,net:500}]);
 assert.equal(planJetonMotion(opening,result).filter(e=>e.kind==='settle').length,1);
 assert.deepEqual(planJetonMotion(result,structuredClone(result)),[]);
});
check('opening a finished table leaves no old chips on the felt',()=>assert.deepEqual(view('result',1,[{bet:500,net:500}]).active,{}));
check('next round wager remains after prior payout',()=>{
 const after=view('result',1,[{bet:500,net:500}],0,0,[{seat:2,amount:500}]);
 assert.deepEqual(planJetonMotion(opening,after).map(e=>[e.kind,e.round]),[['settle',1],['place',2]]);
 assert.equal(after.active[2].amount,500);
});
check('finished table does not replay when the next wager arrives',()=>{
 const before=view('result',1,[{bet:500,net:500}]);
 const after=view('result',1,[{bet:500,net:500}],0,0,[{seat:2,amount:500}]);
 assert.deepEqual(planJetonMotion(before,after).map(e=>e.kind),['place']);
});
check('missed revisions keep placement before immediate natural settlement',()=>{
 const events=planJetonMotion(view('betting',0,[]),view('result',1,[{bet:500,net:750}]));
 assert.deepEqual(events.map(e=>e.kind),['place','settle']);
});
check('returning after multiple missed rounds does not invent old flights',()=>assert.deepEqual(planJetonMotion(opening,view('turn',4)),[]));
check('all approved denominations are exact with black last',()=>{
 for(const amount of [0,250,500,750,1000,1250,1500,2000,3000]){
  const values=chipValues(amount);assert.equal(values.reduce((a,b)=>a+b,0),amount);
  if(amount%500)assert.equal(values.at(-1),250);
 }
});
console.log(checks+' jeton-motion checks passed.');
