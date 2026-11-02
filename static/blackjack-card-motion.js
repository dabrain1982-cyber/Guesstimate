// Presentation only: cards and their order come from the public table snapshot.
const playerCard=(player,hand,index)=>({seat:player.seat,hand,index,code:player.hands[hand].cards[index]});
const bankCard=(game,index)=>({seat:0,index,code:game.dealer[index]});

export function planCardMotion(before,after){
  if(!before||after.round<before.round||!after.dealer.length)return [];
  const steps=[],players=[...after.players].sort((a,b)=>a.seat-b.seat);
  const add=(kind,card)=>steps.push({kind,...card});
  if(after.round>before.round){
    const initial=new Set();
    for(let pass=0;pass<2;pass++){
      for(const player of players){
        // A split may already have happened before this browser's next poll.
        const hand=pass===1&&player.hands.length>1?1:0,index=hand===1?0:pass;
        if(player.hands[hand]?.cards[index]!=null){
          const card=playerCard(player,hand,index);add('deal',card);
          initial.add([card.seat,hand,index].join(':'));
        }
      }
      if(after.dealer.length>pass)add('deal',{...bankCard(after,pass),...(pass===1?{code:null}:{})});
    }
    for(const player of players)player.hands.forEach((hand,h)=>hand.cards.forEach((_,i)=>{
      if(!initial.has([player.seat,h,i].join(':')))add('deal',playerCard(player,h,i));
    }));
    if(after.dealer[1]!=null)add('reveal',bankCard(after,1));
    for(let i=2;i<after.dealer.length;i++)add('deal',bankCard(after,i));
  }else{
    for(const player of players){
      const old=before.players.find(p=>p.seat===player.seat),counts=new Map();
      for(const hand of old?.hands||[])for(const code of hand.cards)counts.set(code,(counts.get(code)||0)+1);
      player.hands.forEach((hand,h)=>hand.cards.forEach((code,i)=>{
        if(counts.get(code))counts.set(code,counts.get(code)-1);
        else add('deal',playerCard(player,h,i));
      }));
    }
    after.dealer.forEach((code,i)=>{
      if(i>=before.dealer.length)add('deal',bankCard(after,i));
      else if(before.dealer[i]==null&&code!=null)add('reveal',bankCard(after,i));
    });
  }
  return steps;
}

export function createCardMotion(root,{onChange=()=>{},sound}={}){
  let busy=false,serial=0,timer=null,resolveDelay=null;
  const animations=new Set(),restore=new Map(),pendingHands=new Set();
  const layer=document.createElement('div');layer.className='bj-deal-layer';layer.setAttribute('aria-hidden','true');
  root.querySelector('.bj-room').append(layer);
  const back=root.querySelector('[data-card-back-url]').value;
  function cleanup(){
    for(const animation of animations)animation.cancel();animations.clear();
    clearTimeout(timer);resolveDelay?.();resolveDelay=null;
    for(const [card,old] of restore){const image=card.querySelector('img');card.style.visibility=old.visibility;image.src=old.src;image.alt=old.alt;}
    for(const hand of pendingHands)delete hand.dataset.cardPending;pendingHands.clear();
    restore.clear();layer.replaceChildren();busy=false;
    delete root.dataset.cardMotion;delete root.dataset.cardMotionStep;
  }
  function cancel(){serial++;cleanup();}
  const delay=ms=>new Promise(resolve=>{resolveDelay=resolve;timer=setTimeout(()=>{resolveDelay=null;resolve();},ms);});
  async function animate(element,frames,duration){
    const animation=element.animate(frames,{duration,easing:'cubic-bezier(.22,.65,.3,1)',fill:'both'});
    animations.add(animation);
    try{await animation.finished;}catch{}finally{animation.cancel();animations.delete(animation);}
  }
  function target(step){
    if(step.seat===0)return root.querySelector('[data-bank-cards]').children[step.index];
    const host=root.querySelector(['','.bj-guest-left','.bj-your-spot','.bj-guest-right'][step.seat]);
    return host?.querySelectorAll('.bj-own-hand')[step.hand]?.querySelectorAll('.bj-card')[step.index];
  }
  async function play(steps){
    cancel();
    if(!steps.length||window.matchMedia('(prefers-reduced-motion: reduce)').matches)return true;
    const ticket=serial;
    const queue=steps.map(step=>({...step,card:target(step)})).filter(step=>step.card);
    if(!queue.length)return false;
    busy=true;root.dataset.cardMotion='dealing';onChange();
    for(const step of queue){
      const image=step.card.querySelector('img'),hand=step.card.closest('.bj-own-hand,.bj-bank-hand');
      if(hand){pendingHands.add(hand);hand.dataset.cardPending='true';}
      if(!restore.has(step.card))restore.set(step.card,{visibility:step.card.style.visibility,src:image.src,alt:image.alt});
      if(step.kind==='deal')step.card.style.visibility='hidden';
      if(step.kind==='reveal'||step.code==null){image.src=back;image.alt='Verdeckte Karte';}
    }
    try{
      // Let the action row and its measured card positions settle first.
      await new Promise(requestAnimationFrame);await new Promise(requestAnimationFrame);
      for(const [index,step] of queue.entries()){
        if(ticket!==serial)return false;
        root.dataset.cardMotionStep=String(index+1)+'/'+queue.length;
        const image=step.card.querySelector('img');
        if(step.kind==='reveal'){
          await animate(step.card,[{scale:'1 1'},{scale:'0 1'}],120);
          if(ticket!==serial)return false;
          image.src=restore.get(step.card).src;image.alt=restore.get(step.card).alt;
          await animate(step.card,[{scale:'0 1'},{scale:'1 1'}],120);
        }else{
          const rect=step.card.getBoundingClientRect(),room=root.querySelector('.bj-room').getBoundingClientRect();
          const flight=document.createElement('div'),picture=document.createElement('img');
          flight.className='bj-flight-card';picture.src=step.code==null?back:image.src;picture.alt='';flight.append(picture);
          Object.assign(flight.style,{left:(rect.left-room.left)+'px',top:(rect.top-room.top)+'px',width:rect.width+'px',height:rect.height+'px'});
          layer.append(flight);
          const dx=room.left+room.width*.85-(rect.left+rect.width/2),dy=room.top+room.height*.39-(rect.top+rect.height/2);
          sound?.play('card-deal');
          await animate(flight,[{transform:`translate(${dx}px,${dy}px) rotate(-15deg) scale(.82)`,opacity:.4},{transform:'translate(0,0) rotate(0) scale(1)',opacity:1}],270);
          if(ticket!==serial)return false;
          if(step.code==null)image.src=back;
          step.card.style.visibility=restore.get(step.card).visibility;flight.remove();
        }
        root.dispatchEvent(new CustomEvent('blackjack-card-arrived',{detail:{kind:step.kind,seat:step.seat,hand:step.hand,index:step.index}}));
        if(step.kind==='reveal')sound?.play('card-move');
        await delay(85);
      }
      return ticket===serial;
    }finally{if(ticket===serial){cleanup();onChange();}}
  }
  return {get busy(){return busy;},play,cancel};
}
