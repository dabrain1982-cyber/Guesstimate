import assert from 'node:assert/strict';
import {planCardMotion} from '../static/blackjack-card-motion.js';

const player=(seat,...hands)=>({seat,hands:hands.map(cards=>({cards}))});
const table=(round,players,dealer)=>({round,players,dealer});
const empty=table(0,[],[]);
const opening=table(1,[player(3,['10C','7H']),player(1,['9S','7D']),player(2,['5C','6H'])],['6D',null]);
const order=steps=>steps.map(s=>[s.kind,s.seat,s.hand??null,s.index,s.code]);

assert.deepEqual(planCardMotion(null,opening),[],'opening an existing table never replays the deal');
assert.deepEqual(order(planCardMotion(empty,opening)),[
  ['deal',1,0,0,'9S'],['deal',2,0,0,'5C'],['deal',3,0,0,'10C'],['deal',0,null,0,'6D'],
  ['deal',1,0,1,'7D'],['deal',2,0,1,'6H'],['deal',3,0,1,'7H'],['deal',0,null,1,null],
],'one complete lap before the second card; the bank hole stays face down');
assert.deepEqual(planCardMotion(opening,structuredClone(opening)),[],'polling cannot repeat cards');
const hit=structuredClone(opening);hit.players.find(p=>p.seat===2).hands[0].cards.push('3D');
assert.deepEqual(order(planCardMotion(opening,hit)),[['deal',2,0,2,'3D']],'a hit adds exactly one card');
const result=structuredClone(hit);result.dealer=['6D','10S','4D'];
assert.deepEqual(order(planCardMotion(hit,result)),[['reveal',0,null,1,'10S'],['deal',0,null,2,'4D']],'reveal the hole before the bank draws');
const naturalResult=table(1,[player(1,['AS','KH'])],['10D','AS']);
assert.deepEqual(order(planCardMotion(empty,naturalResult)).slice(-2),[['deal',0,null,1,null],['reveal',0,null,1,'AS']],'even an immediate result deals the hole face down first');
const splitBefore=table(2,[player(2,['AS','AH'])],['6D',null]);
const splitAfter=table(2,[player(2,['AS','9C'],['AH','8C'])],['6D',null]);
assert.deepEqual(order(planCardMotion(splitBefore,splitAfter)),[['deal',2,0,1,'9C'],['deal',2,1,1,'8C']],'the two existing split cards are not dealt again');
const duplicate=table(3,[player(1,['9S','9S'])],['5D',null]);
const duplicateHit=table(3,[player(1,['9S','9S','9S'])],['5D',null]);
assert.equal(planCardMotion(duplicate,duplicateHit).length,1,'identical faces in six decks remain separate cards');
assert.deepEqual(planCardMotion(result,table(1,[],[])),[],'clearing a table never invents a card');
console.log('9 card-presentation checks passed: laps, hidden hole, hits, reveal, split, duplicate faces, polling, hydration and clearing.');
