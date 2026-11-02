import {createRoundSound} from './blackjack-round-sound.js';
import {createCardMotion,planCardMotion} from './blackjack-card-motion.js';
import {frontUrl,frontSetId} from './blackjack-card-art.js';

export function tablePlayerName(name,simulation=false){
  return simulation?String(name).replace(/\s*·\s*(?:Test|simuliert)\s*$/iu,''):name;
}

export function createRoundView(root,{onChange=()=>{}}={}){
  root.dataset.cardFrontSet=frontSetId;
  const q=selector=>root.querySelector(selector),sound=createRoundSound(root);
  const simulation=Boolean(root.ownerDocument.querySelector('.blackjack-test-banner'));
  let draft='50',previous=null,clock=null,clockOffset=0,clockTimer=null,detail='',prebet=false,currency='points';
  let paintedKey='',motionMessage='';
  const notify=()=>requestAnimationFrame(onChange);
  const motion=createCardMotion(root,{sound,onChange:notify});
  const counter=q('[data-detail]');counter.setAttribute('aria-live','off');
  function updateCounter(){
    let suffix='';
    if(clock?.automatic&&clock.deadline!=null){
      const left=Math.max(0,Math.ceil(clock.deadline-(Date.now()/1000+clockOffset)));
      suffix=left?(clock.kind==='betting'?'':'Nächste Runde: ')+left+' s':clock.kind==='betting'?'Einsatzphase endet …':'Nächste Einsatzphase …';
      if(!prebet&&!left&&clock.kind==='betting')for(const button of root.querySelectorAll('[data-game-action="bet"],[data-game-action="cancel-bet"]'))button.disabled=true;
    }
    counter.textContent=detail+(suffix?' · '+suffix:'');
  }
  function syncClock(snapshot){
    clock=snapshot.game.clock;
    prebet=Boolean(snapshot.game.prebet_supported);
    clockOffset=snapshot.server_time? snapshot.server_time-Date.now()/1000:0;
    if(clockTimer===null)clockTimer=setInterval(updateCounter,250);
    updateCounter();
  }
  root.addEventListener('input',event=>{if(event.target.matches('[data-bet-amount]'))draft=event.target.value;});
  const points=amount=>Number(amount).toLocaleString('de-DE')+(currency==='account-ikuehe'?' iKühe':currency==='test-ikuehe'?' Test-iKühe':' Pkt.');
  const signed=amount=>(amount>0?'+':'')+points(amount);
  const node=(tag,cls,text)=>{const el=document.createElement(tag);if(cls)el.className=cls;if(text!=null)el.textContent=text;return el;};
  function cards(list){
    const row=node('div','bj-cards');
    for(const code of list){
      const card=node('div','bj-card'),image=node('img');
      image.src=code?frontUrl(code):q('[data-card-back-url]').value;
      image.alt=code?({J:'Bube',Q:'Dame',K:'König',A:'Ass'}[code.slice(0,-1)]||code.slice(0,-1))+' '+({S:'Pik',H:'Herz',D:'Karo',C:'Kreuz'}[code.slice(-1)]):'Verdeckte Karte';
      image.draggable=false;card.append(image);row.append(card);
    }
    return row;
  }
  function paint(game){
    const key=JSON.stringify([game.round,game.phase,game.dealer,game.dealer_total,game.players]);
    // Polls, bets and profile refreshes must not restart an in-flight card.
    if(key===paintedKey||motion.busy)return;
    const before=previous,steps=planCardMotion(before,game);
    const bank=q('.bj-bank-hand');bank.hidden=!game.dealer.length;
    q('[data-bank-cards]').replaceChildren(...cards(game.dealer).children);
    q('[data-bank-score]').textContent=game.dealer.length?game.dealer_total+(game.phase==='result'?'':' offen'):'';
    for(const [seat,selector] of [[1,'.bj-guest-left'],[2,'.bj-your-spot'],[3,'.bj-guest-right']]){
      const host=q(selector),player=game.players.find(p=>p.seat===seat);host.hidden=!player;
      if(!player){host.replaceChildren();continue;}
      const hands=node('div','bj-your-hands');
      player.hands.forEach((hand,index)=>{
        const el=node('div','bj-own-hand'+(hand.active?' is-current':''));
        const label=node('div','bj-hand-label');
        const identity=tablePlayerName(player.name,simulation)+(player.hands.length>1?' · Hand '+(index+1):'');
        const caption=hand.result?(player.hands.length>1?'Hand '+(index+1)+' · ':'')+hand.result+' · '+signed(hand.net):identity;
        const text=node('span','',caption);text.title=identity+(hand.result?' · '+caption:'');
        if(hand.result)label.dataset.handResult='';
        label.append(text,node('b','',hand.total));
        el.append(label,cards(hand.cards));
        hands.append(el);
      });host.replaceChildren(hands);
    }
    let finishSound=null;
    if(before){
      if(game.phase==='result'&&(before.phase!=='result'||game.round!==before.round)){
        const own=game.players.find(p=>p.own),net=own?own.hands.reduce((s,h)=>s+h.net,own.insurance_net||0):0;
        finishSound=net<0?'lose':null;
      }else if(game.phase==='betting'&&before.phase==='result')sound.play('shuffle');
    }
    previous=game;paintedKey=key;
    if(steps.length){
      motionMessage=game.round!==before.round?'Der Geber teilt die Karten aus …':steps.some(step=>step.seat===0)?'Die Bank spielt ihre Hand …':'Die nächste Karte kommt …';
      motion.play(steps).then(completed=>{if(completed&&previous===game&&finishSound)sound.play(finishSound);notify();}).catch(()=>{motion.cancel();notify();});
    }else if(finishSound)sound.play(finishSound);
  }
  function layout(){
    for(const label of root.querySelectorAll('.bj-hand-label'))label.style.removeProperty('transform');
    const scene=q('.bj-scene').getBoundingClientRect();
    if(!scene.height)return;
    for(const selector of ['.bj-guest-left','.bj-your-spot','.bj-guest-right']){
      const host=q(selector);if(host.hidden)continue;
      const list=[...host.querySelectorAll('.bj-card')];if(!list.length)continue;
      const ringTop=parseFloat(getComputedStyle(host).getPropertyValue('--bj-ring-top'));
      if(!Number.isFinite(ringTop))continue;
      const target=scene.top+scene.height*(ringTop+2)/100;
      // Anchor the projected card edges to the painted bet circle, not the HUD.
      // A second pass accounts for the shared 45-degree perspective projection.
      for(let pass=0;pass<4;pass++){
        const bottom=Math.max(...list.map(card=>card.getBoundingClientRect().bottom));
        const delta=target-bottom;if(Math.abs(delta)<.2)break;
        host.style.top=(parseFloat(getComputedStyle(host).top)+delta)+'px';
      }
    }
  }
  function layoutCaptions(){
    const labels=[...root.querySelectorAll('.bj-hand-label')];
    for(const label of labels)label.style.removeProperty('transform');
    if(matchMedia('(max-width:900px)').matches)return;
    const scene=q('.bj-scene').getBoundingClientRect();
    const visible=selector=>[...root.querySelectorAll(selector)].map(e=>e.getBoundingClientRect()).filter(r=>r.width);
    const bank=visible('.bj-bank-hand .bj-card,.bj-bank-hand .bj-score');
    const portraits=visible('.bj-seat:not([hidden])');
    const bets=visible('.bj-bet-spot[data-table-bet]:not([hidden])');
    const union=rects=>({left:Math.min(...rects.map(r=>r.left)),top:Math.min(...rects.map(r=>r.top)),right:Math.max(...rects.map(r=>r.right)),bottom:Math.max(...rects.map(r=>r.bottom))});
    const overlaps=(a,b)=>Math.min(a.right,b.right)>Math.max(a.left,b.left)+1&&Math.min(a.bottom,b.bottom)>Math.max(a.top,b.top)+1;
    const placed=[];
    for(const label of labels){
      const children=[...label.children].map(e=>e.getBoundingClientRect());
      if(!children.length||!children.some(r=>r.width))continue;
      const current=union(children);
      if(![...bank,...portraits,...placed].some(box=>overlaps(current,box))){placed.push(current);continue;}
      const hand=label.closest('.bj-own-hand');
      const cards=union([...hand.querySelectorAll('.bj-card')].map(e=>e.getBoundingClientRect()));
      const width=current.right-current.left,height=current.bottom-current.top;
      const center=(cards.left+cards.right)/2;
      const middle=(cards.top+cards.bottom-height)/2;
      // Prefer the clear felt between cards and wager; use a side only if needed.
      const candidates=[
        {left:center-width/2,top:cards.bottom+5},
        {left:cards.left-width-12,top:middle},
        {left:cards.right+12,top:middle},
        {left:center-width/2,top:cards.top-height-8}
      ];
      const obstacles=[...bank,...portraits,...bets,...placed,...visible('.bj-card')];
      const position=candidates.map(p=>({...p,right:p.left+width,bottom:p.top+height})).find(p=>p.left>=scene.left+6&&p.right<=scene.right-6&&p.top>=scene.top&&p.bottom<=scene.bottom-6&&!obstacles.some(box=>overlaps(p,box)));
      if(position){
        label.style.transform='translate('+(position.left-current.left)+'px,'+(position.top-current.top)+'px)';
        placed.push(position);
      }else placed.push(current);
    }
  }
  function render(snapshot){
    const game=snapshot.game,own=snapshot.viewer_seat,player=game.players.find(p=>p.own),choices=[];
    currency=game.currency;
    const walletRule=q("[data-wallet-rule]");
    if(walletRule&&currency==="account-ikuehe")walletRule.textContent='Hier spielst du um die iKühe deines normalen Spielerkontos. Der Grundeinsatz beträgt fest 500 iKühe. Einsätze und Zusatzwetten können verloren gehen; Gewinne werden demselben Konto gutgeschrieben. Es gibt kein kostenloses Auffüllen am Tisch.';
    const dealerRule=q('[data-dealer-check-rule]'),surrenderRule=q('[data-surrender-rule]');
    if(dealerRule)dealerRule.textContent=game.dealer_peek===false?
      'Die verdeckte Karte wird erst nach Abschluss aller Spielerhände aufgedeckt. Bei Bank-Blackjack geht nur der Grundeinsatz verloren; Zusatzbeträge aus Teilen und Verdoppeln kommen zurück.':
      'Prüfung auf Blackjack vor den Spielerzügen.'+(game.next_dealer_peek===false?' Ab der nächsten Runde wird erst nach den Spielerhänden aufgedeckt.':'');
    if(surrenderRule)surrenderRule.textContent=game.dealer_peek===false?
      'Mit den ersten zwei Karten und vor dem Teilen: Hälfte des Einsatzes zurück. Hat die Bank Blackjack, geht der ganze Grundeinsatz verloren.':
      'Mit den ersten zwei Karten, nach der Blackjack-Prüfung der Bank und vor dem Teilen: Hälfte des Einsatzes zurück.';
    if(!previous&&game.own_bet)draft=String(game.own_bet);
    if(game.fixed_bet)draft=String(game.fixed_bet);
    paint(game);
    const eligible=game.can_bet??Boolean(own&&!game.leaving&&!game.own_bet&&game.bankroll>=10&&(['betting','result'].includes(game.phase)||!player));
    const canBet=eligible&&!(motion.busy&&player);
    if(q('.bj-money'))q('.bj-money').hidden=!own;
    if(q('[data-bankroll]'))q('[data-bankroll]').textContent=points(game.bankroll||0);
    if(q('[data-wager]'))q('[data-wager]').textContent=points(game.own_wager);
    const queued=q('[data-next-bet-stat]');
    if(queued){queued.hidden=!own||!game.next_bet;q('[data-next-bet]').textContent=points(game.next_bet||0);}
    const make=(command,label,note)=>choices.push({label,note,command,url:q('[data-game-url]').value,
      data:()=>({action:command,revision:String(snapshot.revision),...(command==='bet'?{amount:draft}:{})})});
    let message='Wähle einen freien Platz am Tisch.',note='Alle am Tisch sehen dieselbe Belegung.';
    if(game.phase==='betting'){
      if(own){
        message=game.own_bet?(game.clock?.automatic?'Dein Einsatz ist bereit. Der Geber wartet auf die übrigen Einsätze oder das Ende der Einsatzzeit.':'Dein Einsatz ist bereit. Austeilen startet mit den gesetzten Einsätzen.'):game.prebet_supported&&snapshot.occupied===1?'Du spielst allein. Dein Einsatz startet die Runde sofort.':'Setze deinen Einsatz für die nächste Runde.';
        if(canBet)make('bet','Einsatz',(game.fixed_bet?points(game.fixed_bet):'10–500 Tischpunkte')+' · gilt für genau eine Runde');
        if(game.own_bet&&!game.clock?.automatic)make('deal','Austeilen','Mit allen gesetzten Einsätzen beginnen');
      }
      note=game.bets.length?game.bets.map(b=>'Platz '+b.seat+': '+points(b.amount)).join(' · '):'Noch keine Einsätze gesetzt.';
    }else if(game.phase==='insurance'){
      message=game.actions.length?'Die Bank zeigt ein Ass. Versicherung wählen oder ablehnen.':'Warte auf die übrigen Versicherungsentscheidungen.';
      note=player?'Versicherung: maximal die Hälfte deines Grundeinsatzes.':'Du steigst in der nächsten Einsatzphase ein.';
    }else if(game.phase==='turn'){
      const activePlayer=game.players.find(p=>p.seat===game.active_seat);
      message=game.active_seat===own?'Du bist dran.':(activePlayer?tablePlayerName(activePlayer.name,simulation):'Platz '+game.active_seat)+' ist am Zug.';
      note=game.waiting_next?'Du steigst in der nächsten Einsatzphase ein.':'Jeder spielt seine Hände nacheinander gegen die Bank.';
    }else{
      message='Runde '+game.round+' ist beendet.';
      if(player){const net=player.hands.reduce((sum,h)=>sum+h.net,player.insurance_net||0);message+=' Dein Ergebnis: '+signed(net);}
      note=player?.insurance?'Versicherung: '+signed(player.insurance_net)+'.':'Die Bank hält ab 17, auch bei Soft 17.';
      if(own&&!game.clock?.automatic)make('next','Neue Runde','Zur nächsten Einsatzphase');
    }
    const labels={hit:['Karte ziehen','Hit'],stand:['Halten','Stand'],double:['Verdoppeln','Gleicher Zusatzeinsatz · genau eine Karte'],split:['Teilen','Split · gleicher Zusatzeinsatz'],surrender:['Aufgeben',game.dealer_peek===false?'Hälfte zurück, sofern die Bank keinen Blackjack hat':'Hälfte des Einsatzes zurück'],insurance:['Versicherung','Zusatzwette: '+points(player?.hands[0]?.bet/2||0)],'no-insurance':['Ohne Versicherung','Keine zusätzliche Wette']};
    const actions=[...game.actions];
    const insuranceCost=player?.hands[0]?.bet/2;
    const insuranceUnavailable=game.phase==='insurance'&&actions.includes('no-insurance')&&!actions.includes('insurance')&&game.bankroll<insuranceCost;
    if(insuranceUnavailable)actions.unshift('insurance');
    for(const command of actions){
      make(command,...labels[command]);
      if(command==='insurance'&&insuranceUnavailable){
        const reason='Nicht genug Guthaben für die Versicherung. Benötigt: '+points(insuranceCost)+'. Verfügbar: '+points(game.bankroll)+'.';
        Object.assign(choices.at(-1),{note:reason,unavailableReason:reason});
      }
    }
    if(game.blocked_actions?.split){
      const {required,available}=game.blocked_actions.split;
      const explanation='Zum Teilen brauchst du weitere '+points(required)+'. Verfügbar: '+points(available)+'.';
      make('split','Teilen',explanation);choices.at(-1).disabled=true;
      message+=' '+explanation;
    }
    if(own&&game.prebet_supported&&game.phase!=='betting'){
      const available=game.bankroll+game.own_bet;
      if(canBet&&available>=10)make('bet','Einsatz','Für Runde '+game.bet_round+(game.phase==='result'&&snapshot.occupied===1?' · startet sofort':''));
      if(game.waiting_next){
        message=game.own_bet?points(game.own_bet)+' liegen für Runde '+game.bet_round+'. Du bist in der nächsten Runde dabei.':'Die Runde läuft. Lege deinen Einsatz für Runde '+game.bet_round+'.';
        note='Ein gelegter Einsatz nimmt an genau einer Runde teil. Danach entscheidest du neu.';
      }else if(game.own_bet)note+=' Für Runde '+game.bet_round+' liegen '+points(game.own_bet);
    }
    if(player?.split_aces)message+=' Geteilte Asse erhalten je eine Zusatzkarte; beide Hände werden danach gehalten.';
    if(game.phase==='result'&&game.dealer.length===2&&game.dealer_total===21)message=(game.dealer_peek===false?'Blackjack der Bank nach Abschluss der Spielerhände. ':'Blackjack der Bank: Die Runde endet ohne weitere Spielerzüge. ')+message;
    if(!own&&game.prebet_supported&&game.phase!=='betting')note='Nimm einen freien Platz und lege deinen Einsatz für die nächste Runde.';
    if(own&&currency!=='account-ikuehe'&&!game.currency_change_pending&&game.bankroll<(game.min_bet||10)&&!game.own_bet&&['betting','result'].includes(game.phase))make('refill','Testguthaben auffüllen',points(game.test_refill||1000));
    if(own&&currency==='account-ikuehe'&&game.bankroll<(game.min_bet||500)&&!game.own_bet&&['betting','result'].includes(game.phase))message+=' Für einen Einsatz brauchst du '+points(game.min_bet||500)+'. Dein Kontostand: '+points(game.bankroll)+'.';
    if(game.currency_change_pending){message='Der bisherige Testtisch wird beendet. Bitte stehe nach der laufenden Hand auf.';for(let i=choices.length-1;i>=0;i--)if(['bet','refill'].includes(choices[i].command))choices.splice(i,1);}
    if(game.leaving){message='Du hast den Tisch verlassen. Dein Einsatz ist verfallen.';note='Der Platz wird nach Rundenende freigegeben.';choices.length=0;}
    if(motion.busy)message=motionMessage;
    detail='Runde '+(game.phase==='betting'?game.round+1:game.round)+' · '+snapshot.occupied+' / 3 Plätze belegt · '+({betting:'Einsatzphase',insurance:'Versicherung',turn:'Spielzüge',result:'Ergebnis'}[game.phase]||game.phase);
    updateCounter();
    return {message,note,choices,animating:motion.busy,betting:canBet&&(game.phase==='betting'||game.prebet_supported),
      betLabel:game.phase==='betting'?'Dein Einsatz':'Für Runde '+game.bet_round,
      detail:counter.textContent,draft,
      leaveNote:'Aufstehen · ein liegender Einsatz verfällt'};
  }
  return {render,layout,layoutCaptions,syncClock,playJetonSound(id){sound.play(id);},pause(){clearInterval(clockTimer);clockTimer=null;motion.cancel();},setSoundEnabled:value=>sound.setEnabled(value)};
}
