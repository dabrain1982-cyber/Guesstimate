import test from 'node:test';
import assert from 'node:assert/strict';
import { createTurnControls } from './turn-controls.js';

// Small DOM fixture for the real controller: the regression is a remote
// state change while no attack dialog is open, not a battle-model rule.
function fixture() {
  const nodes = new Map();
  class Element {
    constructor() {
      this.open = false; this.hidden = false; this.value = ''; this.dataset = {};
      this.events = new Map(); this.shown = 0;
      this.attributes = new Map();
      this.properties = new Map();
      this.style = { setProperty: (key,value) => this.properties.set(key,value) };
      this.classList = { toggle() {}, add() {} }; this.children=[];
    }
    get valueAsNumber() { return Number(this.value); }
    addEventListener(type, listener) { this.events.set(type, listener); }
    setAttribute(key, value) { this.attributes.set(key, value); }
    getAttribute(key) { return this.attributes.get(key) ?? null; }
    removeAttribute(key) { this.attributes.delete(key); }
    querySelectorAll() { return []; }
    querySelector() { return new Element(); }
    replaceChildren(...items) { this.children=items; }
    append(...items) { this.children.push(...items); }
    focus() {}
    showModal() { this.open = true; this.shown++; }
    close() { this.open = false; this.events.get('close')?.(); }
  }
  const node = selector => {
    if (!nodes.has(selector)) nodes.set(selector, new Element());
    return nodes.get(selector);
  };
  const previousDocument = globalThis.document;
  const previousOption=globalThis.Option;
  globalThis.Option=class {constructor(text,value){this.text=text;this.value=value;}};
  const previousSetTimeout=globalThis.setTimeout,previousClearTimeout=globalThis.clearTimeout;
  const timers=new Map();let timerId=0;
  globalThis.setTimeout=(callback,delay)=>{const id=++timerId;timers.set(id,{callback,delay});return id;};
  globalThis.clearTimeout=id=>timers.delete(id);
  globalThis.document = {
    createElement: () => new Element(),
    createElementNS: () => new Element(),
    querySelector: node,
    querySelectorAll: () => [...nodes.values()].filter(element => element.open),
  };
  const turn = {
    isRemote: true, phase: 'attack', ownerId: '1', canAct: true, canDefend: false,
    canAdvance: false, remaining: 0, conqueredCount: 0, turnNumber: 1,
    tradeInfo: { mandatory: false, can_trade: false, next_value: 4, count: 0 },
    battleRequest: { from: 'from', to: 'to', defender: '2' }, pendingConquest: null,
    hand: () => [], troops: id => id === 'from' ? 5 : 0,
    owner: id => id === 'from' ? '1' : '2',
    attackTargets: () => [], fortifyTargets: () => [],
    subscribe(listener) { this.emit = listener; },
  };
  const controls = createTurnControls({
    remote: turn,
    armies: [{ id: '1', name: 'Angreifer', color: '#aa0', ink: '#000' },
             { id: '2', name: 'Verteidiger', color: '#a00', ink: '#fff' }],
    territories: [{ id: 'from', name: 'Startland' }, { id: 'to', name: 'Zielland' }],
    onChange() {},
  });
  const capture = () => {
    turn.battleRequest = null;
    turn.pendingConquest = { from: 'from', to: 'to', min: 3, max: 4 };
    turn.emit();
  };
  return { turn, controls, node, capture, timers, dispose() {
    if(previousOption===undefined)delete globalThis.Option;else globalThis.Option=previousOption;
    globalThis.setTimeout=previousSetTimeout;globalThis.clearTimeout=previousClearTimeout;
    if (previousDocument === undefined) delete globalThis.document;
    else globalThis.document = previousDocument;
  } };
}

test('A resumed attacker sees the waiting defender, then mandatory occupation without another reload', () => {
  const f = fixture();
  try {
    f.controls.start();
    assert.match(f.node('#turn-hint').textContent, /Verteidigung von Verteidiger wird automatisch/);
    assert.equal(f.node('#deployment-controls').hidden, true);
    f.capture();
    assert.equal(f.node('#deployment-controls').hidden, false);
    assert.equal(f.node('#deployment-land').textContent, 'Startland → Zielland');
    assert.equal(f.node('#deployment-amount').min, '3');
    assert.equal(f.node('#deployment-amount').max, '4');
    assert.equal(f.node('#confirm-deployment').disabled, false);
    f.turn.emit();
    assert.equal(f.node('#deployment-controls').shown, 0);
  } finally { f.dispose(); }
});

test('An inline battle result does not block mandatory occupation', () => {
  const f = fixture();
  try {
    f.controls.start();
    f.capture();
    assert.equal(f.node('#deployment-controls').hidden, false);
    assert.equal(f.node('#deployment-controls').shown, 0);
    f.turn.emit();
    assert.equal(f.node('#deployment-controls').shown, 0);
  } finally { f.dispose(); }
});

test('The defending viewer cannot receive or confirm the attacker occupation dialog', () => {
  const f = fixture();
  try {
    f.turn.canAct = false;
    f.controls.start();
    f.capture();
    assert.equal(f.node('#deployment-controls').hidden, true);
  } finally { f.dispose(); }
});

test('A saved pending defense resolves once without opening a window or sending a dice choice', async () => {
  const f = fixture();
  try {
    let calls = 0, finish;
    f.turn.canAct = false; f.turn.canDefend = true; f.turn.inventoryOwnerId = '2';
    f.turn.troops = id => id === 'from' ? 5 : 2;
    f.turn.defend = (...args) => {
      calls++; assert.deepEqual(args, []);
      return new Promise(resolve => { finish = resolve; });
    };
    f.controls.start(); f.turn.emit();
    assert.equal(calls, 1);
    assert.equal(f.node('#defense-dialog').shown, 0);
    assert.equal(f.node('#next-phase').hidden, true);
    f.turn.canDefend = false; f.turn.battleRequest = null;
    f.turn.lastBattle = {sequence:1,from:'from',to:'to',defenderId:'2',attackRolls:[6],defenseRolls:[5,3],attackerLoss:0,defenderLoss:1,conquered:false};
    finish(f.turn.lastBattle); await Promise.resolve(); await Promise.resolve();
    assert.equal(f.node('#defense-dialog').shown, 0);
    assert.match(f.node('#battle-outcome').textContent, /Zielland verteidigt/);
    assert.equal(f.node('#battle-result').hidden, false);
  } finally { f.dispose(); }
});

test('Reinforcements wait for inline confirmation and the last placement advances exactly once', async () => {
  const f = fixture();
  try {
    let places=0, advances=0, troops=5;
    Object.assign(f.turn,{phase:'reinforce',remaining:3,battleRequest:null,total:3});
    Object.defineProperty(f.turn,'canAdvance',{get(){return this.phase==='reinforce' && this.remaining===0;}});
    f.turn.canReinforce=id=>id==='from' && f.turn.remaining>0;
    f.turn.troops=()=>troops;
    f.turn.place=async(id,count)=>{places++;troops+=count;f.turn.remaining-=count;};
    f.turn.advance=async()=>{advances++;f.turn.phase='attack';};
    f.controls.start();f.controls.selected({id:'from',name:'Startland'});
    assert.equal(f.node('#deployment-controls').hidden,false);
    assert.equal(f.node('#deployment-controls').shown,0);
    assert.equal(f.node('#next-phase').hidden,true);
    const amount=f.node('#deployment-amount');amount.value='2';amount.events.get('input')();
    f.turn.emit();assert.equal(amount.value,'2','Polling preserves the chosen quantity');
    assert.equal(places,0);
    await f.node('#deployment-form').events.get('submit')({preventDefault(){}});
    assert.equal(places,1);assert.equal(troops,7);assert.equal(f.turn.remaining,1);
    assert.equal(advances,0);assert.equal(f.node('#deployment-controls').hidden,true);
    f.controls.selected({id:'from',name:'Startland'});
    await f.node('#deployment-form').events.get('submit')({preventDefault(){}});
    await Promise.resolve();f.turn.emit();
    assert.equal(advances,1);assert.equal(f.turn.phase,'attack');assert.equal(troops,8);
    assert.equal(f.node('#reinforcement-receipt').shown,0);
  }finally{f.dispose();}
});

test('A possible or mandatory card trade prevents automatic advance',()=>{
  for(const mandatory of [false,true]){
    const f=fixture();try{
      let advances=0;
      Object.assign(f.turn,{phase:'reinforce',remaining:0,canAdvance:!mandatory,battleRequest:null,
        tradeInfo:{mandatory,can_trade:true,next_value:4,count:0}});
      f.turn.advance=async()=>{advances++;};
      f.controls.start();f.turn.emit();
      assert.equal(advances,0);
      assert.equal(f.node('#next-phase').hidden,mandatory);
    }finally{f.dispose();}
  }
});

test('Mandatory occupation stays inline, cannot be cancelled and blocks duplicate submission',async()=>{
  const f=fixture();try{
    let calls=0,finish;
    f.turn.occupy=count=>{calls++;assert.equal(count,3);return new Promise(resolve=>{finish=()=>{f.turn.pendingConquest=null;resolve();};});};
    f.controls.start();f.capture();
    assert.equal(f.node('#cancel-deployment').hidden,true);
    const submit=()=>f.node('#deployment-form').events.get('submit')({preventDefault(){}});
    const pending=submit();await submit();assert.equal(calls,1);
    finish();await pending;
    assert.equal(f.node('#deployment-controls').hidden,true);
    assert.equal(f.node('#deployment-controls').shown,0);
  }finally{f.dispose();}
});

test('A failed inline placement keeps the amount and visible error available for retry',async()=>{
  const f=fixture();try{
    Object.assign(f.turn,{phase:'reinforce',remaining:2,battleRequest:null});
    f.turn.canReinforce=id=>id==='from';
    f.turn.place=async()=>{throw new Error('Speichern fehlgeschlagen');};
    f.controls.start();f.controls.selected({id:'from',name:'Startland'});
    await f.node('#deployment-form').events.get('submit')({preventDefault(){}});
    assert.equal(f.node('#deployment-controls').hidden,false);
    assert.equal(f.node('#deployment-amount').value,'1');
    assert.equal(f.node('#deployment-error').textContent,'Speichern fehlgeschlagen');
    assert.equal(f.node('#confirm-deployment').disabled,false);
  }finally{f.dispose();}
});

test('One end-turn press without a reward hands off once and never opens a dialog',async()=>{
  const f=fixture();try{
    let calls=0,finish;
    Object.assign(f.turn,{phase:'fortify',battleRequest:null,canAdvance:true});
    f.turn.endTurn=()=>{calls++;return new Promise(resolve=>{finish=()=>{f.turn.phase='reinforce';f.turn.ownerId='2';f.turn.canAct=false;resolve({ownerId:'1',turnNumber:1,conqueredCount:0,card:null});};});};
    f.controls.start();
    const click=()=>f.node('#next-phase').events.get('click')();
    const pending=click();await click();assert.equal(calls,1);assert.equal(f.node('#next-phase').disabled,true);
    finish();await pending;
    assert.equal(f.turn.ownerId,'2');assert.equal(f.node('#turn-end-dialog').shown,0);
    assert.equal(f.node('#next-phase').hidden,true);assert.equal(f.node('#turn-receipt').hidden,true);
  }finally{f.dispose();}
});

test('A new reward stays centered for two seconds then flies to its owner, once despite polling',async()=>{
  const f=fixture();try{
    const result={ownerId:'1',turnNumber:4,conqueredCount:1,card:{id:'alaska',name:'Alaska',type:'Infanterie',symbol:'infantry'}};
    Object.assign(f.turn,{phase:'fortify',battleRequest:null,canAdvance:true,inventoryOwnerId:'1'});
    f.turn.endTurn=async()=>{f.turn.phase='reinforce';f.turn.ownerId='2';f.turn.canAct=false;f.turn.lastTurnResult=result;return result;};
    f.controls.start();await f.node('#next-phase').events.get('click')();
    assert.equal(f.node('#turn-receipt').hidden,false);
    assert.equal(f.node('#turn-receipt').dataset.stage,'center');
    assert.equal(f.node('#awarded-card').children[0].dataset.cardId,'alaska');
    assert.equal(f.node('#turn-end-dialog').shown,0);
    const wait=[...f.timers.values()][0];assert.equal(wait.delay,2000);
    f.turn.emit();assert.equal([...f.timers.values()][0],wait);
    const portrait=f.node('#player-roster').children[0].children[0].children[1];
    // The next actor is player 2; the destination must still be player 1.
    portrait.getBoundingClientRect=()=>({left:20,top:30,width:60,height:60});
    f.node('#turn-receipt').getBoundingClientRect=()=>({left:500,top:250,width:180,height:306});
    wait.callback();
    assert.equal(f.node('#turn-receipt').dataset.stage,'flying');
    assert.equal(f.node('#turn-receipt').properties.get('--receipt-x'),'-540px');
    assert.equal(f.node('#turn-receipt').properties.get('--receipt-y'),'-343px');
    const flight=[...f.timers.values()].find(timer=>timer.delay===480);assert.ok(flight);
    f.turn.emit();assert.equal(f.node('#turn-receipt').dataset.stage,'flying');
    flight.callback();f.turn.emit();
    assert.equal(f.node('#turn-receipt').hidden,true);
    assert.equal(f.turn.ownerId,'2');
  }finally{f.dispose();}
});

test('Saved rewards do not replay after reload, a later award does, and closing cancels its timer',()=>{
  const f=fixture();try{
    const card={id:'alaska',name:'Alaska',type:'Infanterie',symbol:'infantry'};
    Object.assign(f.turn,{battleRequest:null,inventoryOwnerId:'1',lastTurnResult:{ownerId:'1',turnNumber:1,conqueredCount:1,card}});
    f.controls.start();f.turn.emit();
    assert.equal(f.node('#turn-receipt').hidden,true);assert.equal(f.timers.size,0);
    f.turn.lastTurnResult={...f.turn.lastTurnResult,turnNumber:4};f.turn.emit();
    assert.equal(f.node('#turn-receipt').hidden,false);assert.equal(f.timers.size,1);
    f.node('#dismiss-turn-receipt').events.get('click')();f.turn.emit();
    assert.equal(f.node('#turn-receipt').hidden,true);assert.equal(f.timers.size,0);
    f.turn.lastTurnResult={...f.turn.lastTurnResult,turnNumber:7};f.turn.emit();
    assert.equal(f.node('#turn-receipt').dataset.stage,'center');
    f.node('#awarded-card').events.get('click')();
    assert.equal(f.node('#turn-receipt').hidden,true);assert.equal(f.timers.size,0);
    assert.equal(f.node('#card-hand').dataset.expanded,'true');
  }finally{f.dispose();}
});

test('Reduced motion keeps the two-second card presentation and skips the flight',()=>{
  const previous=globalThis.matchMedia;
  const f=fixture();try{
    globalThis.matchMedia=()=>({matches:true});
    Object.assign(f.turn,{battleRequest:null,inventoryOwnerId:'1'});f.controls.start();
    f.turn.lastTurnResult={ownerId:'1',turnNumber:1,conqueredCount:1,card:{id:'alaska',name:'Alaska',type:'Infanterie',symbol:'infantry'}};f.turn.emit();
    f.node('#player-roster').children[0].children[0].children[1].getBoundingClientRect=()=>({left:20,top:30,width:60,height:60});
    f.node('#turn-receipt').getBoundingClientRect=()=>({left:500,top:250,width:180,height:306});
    const wait=[...f.timers.values()][0];assert.equal(wait.delay,2000);wait.callback();
    assert.equal(f.node('#turn-receipt').hidden,true);assert.equal(f.timers.size,0);
  }finally{if(previous===undefined)delete globalThis.matchMedia;else globalThis.matchMedia=previous;f.dispose();}
});

test('An old saved ended turn resumes automatically without a second end-turn click',async()=>{
  const f=fixture();try{
    let calls=0;
    Object.assign(f.turn,{phase:'ended',battleRequest:null,canAdvance:false});
    f.turn.endTurn=async()=>{calls++;f.turn.phase='reinforce';f.turn.ownerId='2';f.turn.canAct=false;return{ownerId:'1',turnNumber:1,conqueredCount:0,card:null};};
    f.controls.start();await Promise.resolve();f.turn.emit();
    assert.equal(calls,1);assert.equal(f.turn.ownerId,'2');
    assert.equal(f.node('#turn-end-dialog').shown,0);
  }finally{f.dispose();}
});

test('The own-turn notice shows the reserve for two seconds without restarting on polling',()=>{
  const f=fixture();try{
    Object.assign(f.turn,{phase:'reinforce',remaining:4,battleRequest:null});
    f.controls.start();
    assert.equal(f.node('#turn-notice').hidden,false);
    assert.equal(f.node('#turn-notice-armies').textContent,'4');
    assert.equal(f.timers.size,1);
    const timer=[...f.timers.values()][0];assert.equal(timer.delay,2000);
    f.turn.remaining=3;f.turn.emit();assert.equal(f.timers.size,1);
    assert.equal(f.node('#turn-notice-armies').textContent,'3');
    timer.callback();f.turn.emit();assert.equal(f.node('#turn-notice').hidden,true);
  }finally{f.dispose();}
});

test('Mandatory trading keeps the turn notice open with a card button until the trade is resolved',()=>{
  const f=fixture();try{
    Object.assign(f.turn,{phase:'reinforce',remaining:3,battleRequest:null,tradeInfo:{mandatory:true,can_trade:true,next_value:4,count:0}});
    f.controls.start();f.turn.emit();
    assert.equal(f.node('#turn-notice').hidden,false);
    assert.equal(f.node('#notice-open-cards').hidden,false);assert.equal(f.timers.size,0);
    f.node('#notice-open-cards').events.get('click')();
    assert.equal(f.node('#card-hand').dataset.expanded,'true');
    assert.equal(f.node('#hand-dialog').shown,0);
    f.turn.tradeInfo.mandatory=false;f.turn.tradeInfo.can_trade=false;f.turn.remaining=7;f.turn.emit();
    assert.equal(f.node('#turn-notice').hidden,true);
    f.node('#cards-toggle').events.get('click')();
    assert.equal(f.node('#turn-notice-armies').textContent,'7');assert.equal(f.timers.size,1);
    [...f.timers.values()][0].callback();assert.equal(f.node('#turn-notice').hidden,true);
  }finally{f.dispose();}
});

test('Two owned countries require no bonus selection and send only the selected cards',async()=>{
  const f=fixture();try{
    const cards=[{id:'alaska',name:'Alaska',type:'Infanterie',symbol:'infantry'},
      {id:'alberta',name:'Alberta',type:'Reiter',symbol:'cavalry'},
      {id:'brasilien',name:'Brasilien',type:'Geschütz',symbol:'artillery'}];
    Object.assign(f.turn,{phase:'reinforce',remaining:3,battleRequest:null,
      tradeInfo:{mandatory:false,can_trade:true,territory_bonus_available:true,next_value:4,count:0},
      hand:()=>cards,owner:id=>id==='alaska'||id==='alberta'?'1':'2'});
    f.controls.start();f.node('#hand-cards').children[0].events.get('click')();
    for(let index=0;index<3;index++)f.node('#hand-cards').children[index].events.get('click')();
    assert.equal(f.node('#trade-cards').disabled,false);
    let submitted;f.turn.trade=async(...args)=>{submitted=args;return {trade_number:1,units:4,bonus:4,bonus_territories:['alaska','alberta']};};
    await f.node('#trade-cards').events.get('click')();
    assert.deepEqual(submitted,[['alaska','alberta','brasilien']]);
    assert.match(f.node('#turn-status').textContent,/Je \+2 direkt auf alaska, alberta/);
  }finally{f.dispose();}
});


test('A compact card expands the hand first; only the second click selects, polling keeps selection',()=>{
  const f=fixture();try{
    const cards=[{id:'alaska',name:'Alaska',type:'Infanterie',symbol:'infantry'}];
    Object.assign(f.turn,{hand:()=>cards,battleRequest:null});
    f.controls.start();
    f.node('#hand-cards').children[0].events.get('click')();
    assert.equal(f.node('#card-hand').dataset.expanded,'true');
    assert.equal(f.node('#hand-cards').children[0].getAttribute('aria-pressed'),'false');
    f.node('#hand-cards').children[0].events.get('click')();f.turn.emit();
    assert.equal(f.node('#hand-cards').children[0].getAttribute('aria-pressed'),'true');
    f.node('#cards-toggle').events.get('click')();
    assert.equal(f.node('#card-hand').dataset.expanded,'false');
    assert.equal(f.node('#hand-dialog').shown,0);
  }finally{f.dispose();}
});

test('Mission appears once at the start, stays accessible at the avatar and can be reopened',()=>{
  const f=fixture();const oldStorage=globalThis.localStorage;
  const saved=new Map();globalThis.localStorage={getItem:key=>saved.get(key),setItem:(key,value)=>saved.set(key,value)};
  try{
    Object.assign(f.turn,{phase:'setup',setupInfo:{target_owner:'1'},ownMission:{text:'Erobere 24 Länder.'},missionKey:'test-game-1',battleRequest:null});
    f.controls.start();f.turn.emit();
    assert.equal(f.node('#mission-reveal').shown,1);
    assert.equal(f.node('#review-mission').title,'Erobere 24 Länder.');
    f.node('#accept-mission').events.get('click')();f.turn.emit();
    assert.equal(saved.get('test-game-1'),'seen');assert.equal(f.node('#mission-reveal').shown,1);
    f.node('#review-mission').events.get('click')();assert.equal(f.node('#mission-reveal').shown,2);
  }finally{globalThis.localStorage=oldStorage;f.dispose();}
});

test('Winner appears at the board and can be collapsed and reopened without a dialog',async()=>{
  const f=fixture();try{
    Object.assign(f.turn,{phase:'completed',canAct:false,battleRequest:null,
      winner:{member_id:'1',name:'Angreifer',reason:'Alle Länder erobert.'}});
    f.controls.start();assert.equal(f.node('#victory-result').hidden,false);
    assert.equal(f.node('#victory-dialog').shown,0);
    f.node('#close-victory').events.get('click')();f.turn.emit();
    assert.equal(f.node('#victory-result').hidden,true);
    await f.node('#next-phase').events.get('click')();assert.equal(f.node('#victory-result').hidden,false);
  }finally{f.dispose();}
});


test('Only a valid selected set shows the trade action with automatic bonuses',()=>{
  const f=fixture();try{
    const cards=[{id:'alaska',name:'Alaska',type:'Infanterie',symbol:'infantry'},
      {id:'alberta',name:'Alberta',type:'Reiter',symbol:'cavalry'},
      {id:'brasilien',name:'Brasilien',type:'Geschütz',symbol:'artillery'}];
    Object.assign(f.turn,{phase:'reinforce',inventoryOwnerId:'1',battleRequest:null,
      tradeInfo:{can_trade:true,mandatory:true,territory_bonus_available:true,next_value:4,count:0},
      hand:()=>cards,owner:id=>id==='brasilien'?'2':'1'});
    f.controls.start();assert.equal(f.node('#card-hand').dataset.owner,'1');
    assert.equal(f.node('#trade-panel').hidden,true);
    f.node('#hand-cards').children[0].events.get('click')();
    for(let i=0;i<2;i++)f.node('#hand-cards').children[i].events.get('click')();
    assert.equal(f.node('#trade-panel').hidden,true);
    f.node('#hand-cards').children[2].events.get('click')();
    assert.equal(f.node('#trade-panel').hidden,false);
    assert.equal(f.node('#trade-cards').disabled,false);
    f.turn.tradeInfo.territory_bonus_available=false;f.turn.emit();
    assert.equal(f.node('#trade-cards').disabled,false);
    f.node('#hand-cards').children[1].events.get('click')();
    assert.equal(f.node('#trade-panel').hidden,true);
  }finally{f.dispose();}
});


test('The hand collapses only after a confirmed trade; pending and rejected trades keep the selection',async()=>{
  for(const fails of [false,true]){
    const f=fixture();try{
      let cards=['alaska','alberta','brasilien'].map(id=>({id,name:id,type:'Infanterie',symbol:'infantry'}));
      Object.assign(f.turn,{phase:'reinforce',remaining:3,battleRequest:null,hand:()=>cards,
        tradeInfo:{mandatory:false,can_trade:true,next_value:4,count:0}});
      let finish;
      f.turn.trade=()=>new Promise((resolve,reject)=>{finish=()=>{
        if(fails)reject(new Error('Tausch nicht gespeichert'));
        else {cards=[];resolve({trade_number:1,units:4,bonus:0,bonus_territories:[]});}
      };});
      f.controls.start();f.node('#hand-cards').children[0].events.get('click')();
      for(let i=0;i<3;i++)f.node('#hand-cards').children[i].events.get('click')();
      const pending=f.node('#trade-cards').events.get('click')();
      assert.equal(f.node('#card-hand').dataset.expanded,'true');
      assert.equal(f.node('#trade-cards').disabled,true);
      finish();await pending;
      assert.equal(f.node('#card-hand').dataset.expanded,fails?'true':'false');
      if(fails){
        assert.equal(f.node('#trade-feedback').hidden,false);
        assert.match(f.node('#trade-feedback').textContent,/nicht gespeichert/);
        assert.equal(f.node('#hand-cards').children.filter(el=>el.getAttribute('aria-pressed')==='true').length,3);
        assert.equal(f.node('#trade-cards').disabled,false);
      }
    }finally{f.dispose();}
  }
});
