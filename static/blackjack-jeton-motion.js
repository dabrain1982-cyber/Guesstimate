// Public wagers only. Presentation never credits/debits a balance.
export function chipValues(amount){
  const greens=Math.max(0,Math.floor(amount/500));
  return [...Array(greens).fill(500),...(amount-greens*500>=250?[250]:[])];
}

export function describeJetons(snapshot){
  const {game}=snapshot,placed={},active={},results=[];
  for(const player of game.players){
    const amount=player.hands.reduce((sum,h)=>sum+h.bet,player.insurance||0);
    const key=game.round+':'+player.seat;
    placed[key]={key,seat:player.seat,round:game.round,amount};
    if(game.phase!=='result')active[player.seat]=placed[key];
    if(game.phase==='result'){
      const portions=player.hands.map(h=>({stake:h.bet,payout:h.bet+(h.net||0)}));
      if(player.insurance)portions.push({stake:player.insurance,payout:player.insurance+(player.insurance_net||0)});
      results.push({kind:'settle',key,seat:player.seat,round:game.round,amount,
        lost:portions.reduce((sum,p)=>sum+Math.max(0,p.stake-p.payout),0),
        returned:portions.reduce((sum,p)=>sum+Math.min(p.stake,p.payout),0),
        profit:portions.reduce((sum,p)=>sum+Math.max(0,p.payout-p.stake),0)});
    }
  }
  for(const bet of game.bets){
    const key=game.bet_round+':'+bet.seat;
    placed[key]={key,seat:bet.seat,round:game.bet_round,amount:bet.amount};
    active[bet.seat]=placed[key];
  }
  return {round:game.round,phase:game.phase,placed,active,results,currency:game.currency};
}

export function planJetonMotion(before,after){
  if(!before||after.round<before.round||after.round>before.round+1)return [];
  const events=[];
  for(const wager of Object.values(after.placed)){
    const from=before.placed[wager.key]?.amount||0;
    if(wager.amount>from)events.push({kind:'place',...wager,from,added:wager.amount-from});
  }
  if(after.phase==='result'&&(before.phase!=='result'||before.round!==after.round))events.push(...after.results);
  // A next-round wager must arrive after the previous hand's money is cleared.
  return events.sort((a,b)=>a.round-b.round||Number(a.kind==='settle')-Number(b.kind==='settle'));
}

export function paintJetonStack(bet,amount,label=''){
  const values=chipValues(amount),key=values.join(','),stack=bet.querySelector('[data-bet-value]');
  if(bet.dataset.chipValues!==key){
    stack.replaceChildren();
    values.forEach((value,index)=>{
      const chip=bet.ownerDocument.createElement('span');chip.className='bj-jeton';chip.dataset.value=String(value);
      chip.style.setProperty('--bj-jeton-index',String(index));chip.setAttribute('aria-hidden','true');stack.append(chip);
    });
    bet.dataset.chipValues=key;bet.dataset.chipCount=String(values.length);
    bet.style.setProperty('--bj-stack-lift',String(Math.max(0,values.length-1)));
  }
  bet.dataset.remainder=String(amount-values.reduce((sum,v)=>sum+v,0));
  bet.hidden=!amount;bet.title=label;bet.setAttribute('aria-label',label);
}

export function createJetonMotion(root,{onChange=()=>{},playSound=()=>{}}={}){
  const q=selector=>root.querySelector(selector),room=q('.bj-room');
  const layer=root.ownerDocument.createElement('div');layer.className='bj-jeton-layer';layer.setAttribute('aria-hidden','true');q('.bj-scene').append(layer);
  const slots=new Map([1,2,3].map(seat=>[seat,{bet:q('[data-table-bet="'+seat+'"]'),queue:[],running:false}]));
  const animations=new Set(),delays=new Map();
  let previous=null,latest=null,cardsBusy=false,serial=0,suspended=false;
  const reduced=()=>matchMedia('(prefers-reduced-motion: reduce)').matches;
  function show(slot,amount){
    const unit=latest.currency==='test-ikuehe'?'iKühe':'Pkt.';
    paintJetonStack(slot.bet,amount,amount?'Einsatz: '+Number(amount).toLocaleString('de-DE')+' '+unit:'');
    slot.bet.style.removeProperty('visibility');
  }
  function report(kind,seat,stage){
    root.dispatchEvent(new CustomEvent('blackjack-jeton-motion',{detail:{kind,seat,stage}}));
    const active=[...slots.values()].filter(s=>s.running).length;
    if(active)root.dataset.jetonMotion=kind;else delete root.dataset.jetonMotion;
  }
  function cancel(){
    serial++;
    for(const animation of animations)animation.cancel();animations.clear();
    for(const [timer,resolve] of delays){clearTimeout(timer);resolve();}delays.clear();
    for(const slot of slots.values()){slot.queue=[];slot.running=false;slot.bet.style.removeProperty('visibility');}
    layer.replaceChildren();delete root.dataset.jetonMotion;
  }
  const pause=ms=>new Promise(resolve=>{const timer=setTimeout(()=>{delays.delete(timer);resolve();},ms);delays.set(timer,resolve);});
  function vector(seat,toward){
    const bet=slots.get(seat).bet.getBoundingClientRect();
    const avatar=q('[data-seat-number="'+seat+'"]')?.getBoundingClientRect();
    const bank=q('.bj-bank-hand').getBoundingClientRect();
    const bounds=room.getBoundingClientRect();
    const target=toward==='bank'?(bank.width?bank:{left:bounds.left+bounds.width/2,top:bounds.top+bounds.height*.45,width:0,height:0}):avatar?.width?avatar:{left:bet.left,top:bounds.bottom,width:bet.width,height:0};
    const dx=target.left+target.width/2-bet.left-bet.width/2,dy=target.top+target.height/2-bet.top-bet.height/2;
    const distance=Math.hypot(dx,dy)||1,length=Math.min(48,distance*.8);
    return {x:dx/distance*length,y:dy/distance*length};
  }
  async function fly(slot,amount,toward,incoming,ticket){
    if(!amount||ticket!==serial)return;
    const bet=slot.bet,bounds=room.getBoundingClientRect(),rect=bet.getBoundingClientRect();
    const flight=bet.cloneNode(true);flight.removeAttribute('data-table-bet');flight.removeAttribute('aria-label');flight.removeAttribute('title');
    flight.classList.add('bj-jeton-flight');flight.hidden=false;flight.style.visibility='visible';
    paintJetonStack(flight,amount);flight.setAttribute('aria-hidden','true');
    Object.assign(flight.style,{left:rect.left-bounds.left+'px',top:rect.bottom-bounds.top+'px',transform:'translateY(-100%)'});
    layer.append(flight);
    const {x,y}=vector(Number(bet.dataset.tableBet),toward);
    const rest='translate(0, -100%)';
    const away=`translate(${x}px, calc(-100% + ${y}px))`;
    const arc=`translate(${x*.35}px, calc(-100% + ${y*.35-5}px))`;
    const frames=incoming?[{transform:away,opacity:.15},{transform:arc,opacity:1,offset:.6},{transform:rest,opacity:1}]:
      [{transform:rest,opacity:1},{transform:arc,opacity:1,offset:.35},{transform:away,opacity:0}];
    const animation=flight.animate(frames,{duration:incoming?260:290,easing:'cubic-bezier(.22,.65,.3,1)',fill:'both'});
    animations.add(animation);
    try{await animation.finished;}catch{}finally{animation.cancel();animations.delete(animation);flight.remove();}
  }
  async function run(slot,event){
    const ticket=serial;slot.running=true;report(event.kind,event.seat,'start');
    const valid=()=>ticket===serial;
    try{
      // Preserve the wager's full layout footprint while its first chip arrives.
      if(event.kind==='place'){
        show(slot,event.amount);if(!event.from)slot.bet.style.visibility='hidden';else show(slot,event.from);
      }else show(slot,event.amount);
      await new Promise(requestAnimationFrame);
      if(!valid())return;
      if(!reduced()){
        if(event.kind==='place'){
          await fly(slot,event.added,'avatar',true,ticket);
          if(!valid())return;show(slot,event.amount);playSound('chips-place');
        }else{
          if(event.lost){
            // A half refund becomes two 250 portions, using the approved black chip.
            show(slot,event.amount);const flight=fly(slot,event.lost,'bank',false,ticket);
            show(slot,event.returned);await flight;if(!valid())return;
          }
          if(event.profit){
            // Lay the added winnings on the felt before returning the whole payout.
            if(!event.returned){show(slot,event.profit);slot.bet.style.visibility='hidden';}
            await fly(slot,event.profit,'bank',true,ticket);
            if(!valid())return;show(slot,event.returned+event.profit);playSound('chips-payout');
            report('win-added',event.seat,'landed');onChange();await pause(140);if(!valid())return;
          }
          const payout=event.returned+event.profit;
          if(payout){
            show(slot,payout);const flight=fly(slot,payout,'avatar',false,ticket);
            slot.bet.style.visibility='hidden';await flight;if(!valid())return;
            if(!event.profit)playSound('chips-payout');
          }else if(event.lost)playSound('chips-place');
          show(slot,0);
        }
      }else{
        show(slot,event.kind==='place'?event.amount:0);
        playSound(event.kind==='place'?'chips-place':event.returned+event.profit?'chips-payout':'chips-place');
      }
      report(event.kind,event.seat,'finish');
    }finally{
      if(valid()){slot.running=false;drain(slot);onChange();}
    }
  }
  function drain(slot){
    if(slot.running)return;
    if(!slot.queue.length){show(slot,latest.active[Number(slot.bet.dataset.tableBet)]?.amount||0);return;}
    if(slot.queue[0].kind==='settle'&&cardsBusy)return;
    const event=slot.queue.shift();
    run(slot,event).catch(()=>{cancel();for(const slot of slots.values())show(slot,latest.active[Number(slot.bet.dataset.tableBet)]?.amount||0);onChange();});
  }
  function sync(snapshot,{animating=false}={}){
    const next=describeJetons(snapshot);cardsBusy=animating;latest=next;
    if(suspended||document.hidden||!previous||next.round<previous.round||next.round>previous.round+1){
      cancel();for(const [seat,slot] of slots)show(slot,next.active[seat]?.amount||0);suspended=false;
    }else{
      for(const event of planJetonMotion(previous,next))slots.get(event.seat)?.queue.push(event);
      for(const slot of slots.values())drain(slot);
    }
    previous=next;
    if(![...slots.values()].some(s=>s.running))delete root.dataset.jetonMotion;
  }
  function suspend(){cancel();previous=null;suspended=true;}
  return {sync,suspend};
}
