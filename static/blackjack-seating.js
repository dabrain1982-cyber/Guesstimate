import {recipe,renderButton,createSound,audioRecords} from './blackjack-workshop.js';
import {createPlayerPortrait} from './player-portrait.js';
import {createRoundView,tablePlayerName} from './blackjack-round-view.js';
import {createActionIntentGuard} from './blackjack-action-intent.js';
import {createJetonMotion} from './blackjack-jeton-motion.js';

const root=document.getElementById('stormseed-blackjack');
const q=selector=>root.querySelector(selector);
const roundView=createRoundView(root,{onChange:()=>render(true)});
const jetons=createJetonMotion(root,{onChange:()=>requestAnimationFrame(()=>render(true)),playSound:id=>roundView.playJetonSound(id)});
let snapshot=JSON.parse(document.getElementById('blackjack-initial').textContent);
let pending=false,polling=false,connected=true,stopped=false,soundEnabled=true;
let timer,sequence=0,signature='',notice='',riskChoice=null,riskPending=false;
const portraits=new Map();
const prepareAction=createActionIntentGuard();
const simulation=Boolean(document.querySelector('.blackjack-test-banner'));
const sound=createSound(text=>{root.dataset.buttonSoundMessage=text;if(!text.endsWith(' %')){q('[data-sound-status]').textContent=text;q('[data-sound-status]').hidden=false;}});
sound.configure(audioRecords);
const selectedSound={play:(...args)=>{if(soundEnabled)return sound.play(...args);}};
root.dataset.buttonRecipe=recipe.id;
root.dataset.buttonSoundVolume=String(recipe.settings.volume);

function render(force=false){
  roundView.syncClock(snapshot);
  // Keep the pressed workshop button mounted until its action is confirmed.
  if(pending)return;
  const {server_time,...stable}=snapshot;
  const next=JSON.stringify([stable,connected,stopped,notice]);
  if(!force&&next===signature)return;
  signature=next;
  const round=roundView.render(snapshot);
  for(const seat of snapshot.seats){
    const host=q('[data-seat="'+seat.slot+'"]');
    host.dataset.current=String(Boolean(seat.player?.is_self));
    host.dataset.empty=String(!seat.player);
    host.hidden=!seat.player;
    host.dataset.seatNumber=String(seat.number);
    if(seat.player){
      if(!portraits.has(host))portraits.set(host,createPlayerPortrait(host));
      const hand=snapshot.game.players.find(player=>player.seat===seat.number);
      const wager=seat.player.wager??(hand?hand.hands.reduce((sum,h)=>sum+h.bet,0):snapshot.game.phase==='betting'?snapshot.game.bets.find(b=>b.seat===seat.number)?.amount||0:0);
      const balance=seat.player.table_points??(seat.player.is_self?snapshot.game.bankroll:null);
      const queued=seat.player.next_bet??(snapshot.game.phase!=='betting'?snapshot.game.bets.find(b=>b.seat===seat.number)?.amount||0:0);
      const onTable=queued||(wager+(hand?.insurance||0));
      const gain=snapshot.game.phase==='result'&&!round.animating&&hand?hand.hands.reduce((sum,h)=>sum+(h.net||0),hand.insurance_net||0):null;
      portraits.get(host).update({name:tablePlayerName(seat.player.name,simulation),portrait:seat.player.portrait,
        current:Boolean(hand?.hands.some(h=>h.active)),kind:'player',layout:'table',color:'#80613e',
        wallet:{balance,wager:onTable,gain,unit:snapshot.game.currency==='points'?'Tischpunkte':'iKühe'},
        status:''});
    }else{
      portraits.delete(host);
      host.replaceChildren();
    }
  }
  jetons.sync(snapshot,{animating:round.animating});
  const own=snapshot.viewer_seat;
  q('[data-message]').textContent=stopped?'Bitte melde dich erneut an.':!connected?
    'Verbindung unterbrochen. Die Plätze werden erneut abgefragt.':notice||
    (snapshot.occupied===3&&!own?'Alle drei Plätze sind belegt. Du schaust zu.':round.message);
  q('[data-detail]').textContent=round.detail;
  q('[data-seat-note]').textContent=round.note;
  q('[data-login]').hidden=!stopped;
  const betFocused=document.activeElement?.matches('[data-bet-amount]');
  const actions=q('[data-actions]');actions.replaceChildren();
  q('[data-table-limits]').textContent=snapshot.game.fixed_bet?snapshot.game.fixed_bet+(snapshot.game.currency==='account-ikuehe'?' iKühe':' Test-iKühe')+' · fester Einsatz':'10–500 Tischpunkte';
  if(round.betting&&!snapshot.game.fixed_bet){
    const label=document.createElement('label'),input=document.createElement('input');
    label.className='bj-bet-choice';label.textContent=round.betLabel||'Einsatz in Tischpunkten';
    input.type='number';input.min='10';input.max='500';input.step='10';input.value=round.draft;input.className='bj-bet-input';input.dataset.betAmount='';input.setAttribute('aria-label','Einsatz in Tischpunkten');label.append(input);actions.append(label);if(betFocused)input.focus({preventScroll:true});
  }
  const choices=own?(snapshot.game.leaving?[]:round.choices):
    (snapshot.game.currency_change_pending?[]:snapshot.seats.filter(seat=>!seat.player)).map(seat=>({label:'Platz '+seat.number+' nehmen',seat:seat.number,url:root.dataset.joinUrl,note:['Links','Mitte','Rechts'][seat.number-1]}));
  const room=q('.bj-room').getBoundingClientRect();
  const nativeWidth=recipe.settings.size*(recipe.base?recipe.base.width/23:12);
  const exitChoice=own&&!snapshot.game.leaving?{label:'Tisch verlassen',url:root.dataset.leaveUrl,note:round.leaveNote}:null;
  const exit=q('[data-exit-actions]');exit.replaceChildren();exit.hidden=!exitChoice;
  const exitScale=Math.min(1,room.height/900);
  root.dataset.seated=String(Boolean(exitChoice));
  root.style.setProperty('--bj-exit-width',Math.ceil(nativeWidth*exitScale)+'px');
  const available=actions.getBoundingClientRect().width;
  const scale=Math.min(1,room.height/900,Math.max(.5,(available-(round.betting?120:0)-choices.length*10)/(Math.max(1,choices.length)*nativeWidth)));
  let actionHeight=0;
  for(const choice of [...choices,...(exitChoice?[exitChoice]:[])]){
    const slot=document.createElement('div'),host=document.createElement('div'),detail=document.createElement('small');
    slot.className='bj-button-slot';host.className='bj-workshop-host';detail.className='bj-slot-note';
    detail.textContent=choice.note;slot.append(host,detail);(choice===exitChoice?exit:actions).append(slot);
    const dealing=round.animating&&['hit','stand','double','split','surrender','insurance','no-insurance','deal','next'].includes(choice.command);
    const available=()=>connected&&!stopped&&!pending&&!riskChoice&&!dealing&&!choice.disabled;
    let acceptsPress;
    const view=renderButton(host,structuredClone(recipe),{label:choice.label,sound:selectedSound,
      size:recipe.settings.size*(choice===exitChoice?exitScale:scale),state:'normal',action:event=>{
        if(acceptsPress(event))act(choice,view.element);
      }});
    acceptsPress=prepareAction(view.element,choice.command||choice.url,available);
    view.element.setAttribute('aria-disabled',String(!available()));
    view.element.title=choice.note||choice.label;
    view.element.dataset.workshopRecipe=recipe.id;
    if(choice.command)view.element.dataset.gameAction=choice.command;
    if(choice.seat)view.element.dataset.seatTarget=String(choice.seat);
    const buttonScale=choice===exitChoice?exitScale:scale;
    if(buttonScale>0)actionHeight=Math.max(actionHeight,view.element.getBoundingClientRect().height*exitScale/buttonScale);
  }
  // Reserve the canonical button's full height even while another seat plays.
  // The measured recipe stays authoritative; fewer/smaller actions do not move the table.
  if(actionHeight>0)root.style.setProperty('--bj-action-height',Math.ceil(actionHeight)+'px');
  measureLayout();
}

function measureLayout(){
  roundView.layout();
  const seats=[...q('.bj-seats').children];
  for(const seat of seats)for(const property of ['left','top','--player-portrait-size'])seat.style.removeProperty(property);
  root.style.removeProperty('--bj-status-inset');
  root.style.removeProperty('--bj-status-width');
  if(matchMedia('(max-width:900px)').matches){roundView.layoutCaptions();return;}
  const room=q('.bj-room').getBoundingClientRect();
  const overlaps=(a,b)=>Math.min(a.right,b.right)>Math.max(a.left,b.left)&&Math.min(a.bottom,b.bottom)>Math.max(a.top,b.top);
  const own=seats.find(seat=>!seat.hidden&&seat.dataset.current==='true');
  if(own){
    if(own.dataset.seat==='left'){
      const bet=q('[data-table-bet="'+own.dataset.seatNumber+'"]');
      if(!bet.hidden)own.style.top=(bet.getBoundingClientRect().bottom-room.top+8)+'px';
    }
    const box=own.getBoundingClientRect();
    const cards=[...q('.bj-scene').querySelectorAll('.bj-card')].map(e=>e.getBoundingClientRect()).filter(card=>card.width&&overlaps(box,card));
    if(cards.length){
      const offset=own.dataset.seat==='left'?0:box.height/2;
      own.style.top=(Math.max(...cards.map(card=>card.bottom))-room.top+12+offset)+'px';
    }
    const status=q('.bj-status').getBoundingClientRect(),message=q('[data-message]').getBoundingClientRect(),portrait=own.getBoundingClientRect();
    if(overlaps(portrait,message)){
      if(portrait.left-room.left<room.width*.3)root.style.setProperty('--bj-status-inset',Math.max(0,portrait.right-status.left+12)+'px');
      else root.style.setProperty('--bj-status-width',Math.max(120,portrait.left-status.left-12)+'px');
    }
  }
  const bank=[...q('.bj-bank-hand').querySelectorAll('.bj-card,.bj-score')].map(e=>e.getBoundingClientRect()).filter(r=>r.width);
  if(!bank.length){roundView.layoutCaptions();return;}
  const middle=q('.bj-seat[data-seat="self"]');
  const aboveBank=()=>Math.min(...bank.map(r=>r.top))-room.top-12;
  for(const seat of seats.filter(seat=>seat!==middle&&seat!==own&&!seat.hidden)){
    if(bank.some(card=>overlaps(seat.getBoundingClientRect(),card)))seat.style.top=aboveBank()+'px';
  }
  if(middle.hidden||middle===own){roundView.layoutCaptions();return;}
  const box=middle.getBoundingClientRect();
  const preferred=box.left-room.left;
  const left=Math.max(preferred,Math.max(...bank.map(r=>r.right))-room.left+12);
  const rightSeat=q('.bj-seat[data-seat="right"]'),rightBox=rightSeat.getBoundingClientRect();
  const sameRow=!rightSeat.hidden&&Math.min(box.bottom,rightBox.bottom)>Math.max(box.top,rightBox.top);
  const limit=sameRow?rightBox.left-room.left-12:room.width-12;
  const scale=Math.min(1,Math.max(0,limit-left)/box.width);
  if(scale>=.82&&left-preferred<=room.width*.06){
    const size=parseFloat(getComputedStyle(middle).fontSize);
    if(scale<1)middle.style.setProperty('--player-portrait-size',size*scale+'px');
    middle.style.left=left+'px';
  }else{
    // A long bank hand uses its full card row; retain a readable portrait above it.
    middle.style.top=aboveBank()+'px';
  }
  roundView.layoutCaptions();
}

const layoutObserver=new ResizeObserver(measureLayout);
layoutObserver.observe(q('.bj-console'));for(const seat of q('.bj-seats').children)layoutObserver.observe(seat);
let layoutFrame;
new ResizeObserver(()=>{cancelAnimationFrame(layoutFrame);layoutFrame=requestAnimationFrame(()=>{if(!pending)render(true);});}).observe(q('.bj-room'));

async function requestState(url,data){
  const controller=new AbortController(),timeout=setTimeout(()=>controller.abort(),8000);
  try{
    const response=await fetch(url,{credentials:'same-origin',cache:'no-store',signal:controller.signal,
      ...(data?{method:'POST',body:new URLSearchParams({...data,csrf_token:root.dataset.csrf})}:{})});
    if(response.redirected||response.status===401){stopped=true;throw new Error('session');}
    let body;try{body=await response.json();}catch{body={error:'Die Anfrage konnte nicht bestätigt werden. Bitte lade die Seite neu.'};}
    if(!response.ok)return {error:body.error||'Die Anfrage konnte nicht bestätigt werden.',snapshot:body.seats?body:null};
    if(!Array.isArray(body.seats)||body.seats.length!==3)throw new Error('state');
    return {snapshot:body};
  }finally{clearTimeout(timeout);}
}

function schedule(){clearTimeout(timer);if(!stopped&&!pending)timer=setTimeout(refresh,1500);}
async function refresh(){
  if(pending||polling||stopped)return;
  polling=true;const ticket=++sequence;
  try{
    const result=await requestState(root.dataset.statusUrl);
    if(ticket!==sequence)return;
    if(!result.snapshot)throw new Error('state');
    snapshot=result.snapshot;connected=true;render();
  }catch{
    if(ticket===sequence){connected=false;render();}
  }finally{polling=false;schedule();}
}

async function act(choice,element){
  if(pending||!connected||stopped)return;
  pending=true;++sequence;clearTimeout(timer);root.setAttribute('aria-busy','true');
  for(const button of root.querySelectorAll('.bj-button-slot button'))button.setAttribute('aria-disabled','true');
  try{
    // Keep the canonical press visible before replacing its button.
    await Promise.all((element.querySelector('.comic-button-face')?.getAnimations()||[]).map(animation=>animation.finished.catch(()=>{})));
    if(choice.unavailableReason){notice=choice.unavailableReason;return;}
    if(choice.seat&&!choice.riskAccepted&&snapshot.game.currency==='account-ikuehe'){
      riskChoice=choice;q('[data-risk]').hidden=false;q('[data-risk]').scrollTop=0;q('#bj-risk-heading').focus({preventScroll:true});return;
    }
    const result=await requestState(choice.url,choice.data?choice.data():choice.seat?{seat:String(choice.seat),...(choice.riskAccepted?{accept_risk:'1'}:{})}:{});
    if(result.snapshot)snapshot=result.snapshot;
    notice=result.error||'';connected=true;
  }catch{connected=false;}
  finally{pending=false;root.removeAttribute('aria-busy');render(true);schedule();}
}

const riskButtons={};
function closeRisk(){
  const seat=riskChoice?.seat;riskChoice=null;q('[data-risk]').hidden=true;
  render(true);(q('[data-seat-target="'+seat+'"]')||q('[data-action="rules"]')).focus();
}
for(const [key,label] of [['cancel','Abbrechen'],['confirm','Platz nehmen']]){
  const host=document.createElement('div');q('[data-risk-actions]').append(host);
  let acceptsPress;
  const view=renderButton(host,structuredClone(recipe),{label,sound:selectedSound,size:recipe.settings.size,state:'normal',action:async event=>{
    if(!acceptsPress(event))return;
    riskPending=true;
    await Promise.all((view.element.querySelector('.comic-button-face')?.getAnimations()||[]).map(animation=>animation.finished.catch(()=>{})));
    if(key==='cancel'){closeRisk();riskPending=false;return;}
    const choice=riskChoice;riskChoice=null;q('[data-risk]').hidden=true;riskPending=false;
    if(choice)await act({...choice,riskAccepted:true},view.element);
  }});
  acceptsPress=prepareAction(view.element,'risk-'+key,()=>Boolean(riskChoice)&&!riskPending&&!pending&&(key==='cancel'||(connected&&!stopped)));
  riskButtons[key]=view.element;
}

root.addEventListener('click',event=>{
  const action=event.target.closest('[data-action]')?.dataset.action;
  if(action==='toggle-sound'){
    soundEnabled=!soundEnabled;if(!soundEnabled)sound.stop();
    roundView.setSoundEnabled(soundEnabled);
    const button=q('[data-action="toggle-sound"]');button.textContent=soundEnabled?'Ton an':'Ton aus';button.setAttribute('aria-pressed',String(soundEnabled));
  }else if(action==='rules'){
    q('[data-rules]').hidden=false;q('[data-action="close-rules"]').focus();
  }else if(action==='close-rules'){
    q('[data-rules]').hidden=true;q('[data-action="rules"]').focus();
  }
});
root.addEventListener('keydown',event=>{
  if(!q('[data-risk]').hidden){
    if(event.key==='Escape'){event.preventDefault();if(!riskPending)closeRisk();}
    if(event.key==='Tab'){event.preventDefault();const buttons=[riskButtons.cancel,riskButtons.confirm],index=buttons.indexOf(document.activeElement);buttons[index<0?(event.shiftKey?1:0):(index+(event.shiftKey?-1:1)+2)%2].focus();}
    return;
  }
  if(event.key==='Escape'&&!q('[data-rules]').hidden){q('[data-rules]').hidden=true;q('[data-action="rules"]').focus();}
  if(event.key==='Tab'&&!q('[data-rules]').hidden){event.preventDefault();q('[data-action="close-rules"]').focus();}
});
document.addEventListener('visibilitychange',()=>{if(document.hidden)jetons.suspend();else refresh();});
window.addEventListener('pagehide',()=>{stopped=true;clearTimeout(timer);sound.stop();roundView.pause();jetons.suspend();});
window.addEventListener('pageshow',event=>{if(event.persisted){stopped=false;signature='';refresh();}});
render();refresh();
