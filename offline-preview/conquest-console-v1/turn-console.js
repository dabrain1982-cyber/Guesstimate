import {renderButton,materialize} from '/workshop/renderer.js';
import {die} from '/shared/components.js';
import {createPlayerPortrait} from '/shared/player-portrait.js';
import {PHASES,PHASE_LABELS,PLAYERS,COUNTRIES,ownTurn,maxMove} from './model.js';

export function roleRecipe(recipe,role='secondary'){
  const result=structuredClone(recipe);
  result.settings.accent=role==='primary'?'#d8ff42':recipe.settings.accent;
  return result;
}

// One view, retained through every example action. Buttons keep their press animation.
export function createTurnConsole(host,{recipe,sound,onAction,onSelect,onCount}){
  const root=document.createElement('section');root.className='turn-console';root.setAttribute('aria-label','Deine Zuganzeige');
  root.innerHTML='<div class="console-top"><div class="player-host"></div><span class="turn-number">Zug <b data-value="turn"></b></span></div>'+
    '<div class="army-stats"><div><span>Länder</span><strong data-value="countries"></strong></div><div><span>Truppen</span><strong data-value="troops"></strong></div><div class="reserve-stat"><span>Reserve</span><strong data-value="reserve"></strong></div></div>'+
    '<div class="phase-track" role="group" aria-label="Zugphasen"><div data-button="reinforce"></div><div data-button="attack"></div><div data-button="fortify"></div></div>'+
    '<div class="console-body"><div class="task-heading"><span class="task-number" data-value="step"></span><div><p class="eyebrow" data-value="kicker"></p><h2 data-value="title"></h2></div></div><p class="task-copy" data-value="copy"></p>'+
    '<div class="phase-panel" data-panel="reinforce"><label for="country-choice">Wohin mit der Verstärkung?</label><select id="country-choice"></select><div class="reserve-meter"><span data-value="progress"></span><div role="progressbar" aria-label="Verteilte Verstärkungen" aria-valuemin="0" aria-valuemax="6"><i></i></div></div><div data-button="place"></div></div>'+
    '<div class="phase-panel" data-panel="attack"><div class="country-route"><div><span>Westeuropa</span><b data-value="attack-from"></b><small>deine Truppen</small></div><span class="route-arrow" aria-hidden="true">➜</span><div class="enemy-country"><span>Nordafrika</span><b data-value="attack-to"></b><small>Robins Truppen</small></div></div><div class="battle-result" hidden><div><span>Angriff</span><div data-dice="attack"></div></div><div><span>Verteidigung</span><div data-dice="defense"></div></div><p>Nordafrika verliert 2 Truppen.</p></div><div data-button="battle"></div><p class="field-hint">Ein fester Beispielwurf, um die Anzeige zu testen.</p></div>'+
    '<div class="phase-panel" data-panel="fortify"><div class="country-route"><div><span>Westeuropa</span><b data-value="move-from"></b><small>Ausgangsland</small></div><span class="route-arrow" aria-hidden="true">➜</span><div><span>Südeuropa</span><b data-value="move-to"></b><small>Nachbarland</small></div></div><label for="move-count">Wie viele Truppen sollen umziehen?</label><div class="move-controls"><input id="move-count" type="number" min="1" value="3" inputmode="numeric"><span data-value="move-hint"></span></div><div data-button="move"></div></div>'+
    '<div class="phase-panel quiet-panel" data-panel="ended"><span class="quiet-symbol" aria-hidden="true">✓</span><strong>Alles für die Übergabe bereit.</strong><p>Dein Zug ist abgeschlossen. Sieh dir die Zusammenfassung an und gib an Robin weiter.</p></div>'+
    '<div class="phase-panel quiet-panel" data-panel="waiting"><span class="waiting-dots" aria-hidden="true"><i></i><i></i><i></i></span><strong>Robin spielt seinen Zug.</strong><p>Du kannst die Karte weiter ansehen. Deine Spielaktionen sind in dieser Zeit gesperrt.</p></div>'+
    '<p class="console-feedback" role="status" data-value="feedback"></p><div class="next-action" data-button="next"></div></div>'+
    '<div class="console-bottom"><span>Dein Inventar <b>3</b></span><div data-button="cards"></div></div>';
  host.replaceChildren(root);
  const query=s=>root.querySelector(s),text=(key,value)=>{query('[data-value="'+key+'"]').textContent=value;};
  const portrait=createPlayerPortrait(query('.player-host')),buttons={};
  const applyRole=(view,role)=>materialize(view.element,roleRecipe(recipe,role),{tintStrength:role==='primary'?84:null});
  const mount=(key,label,symbol,role,action)=>buttons[key]=renderButton(query('[data-button="'+key+'"]'),roleRecipe(recipe,role),{label,symbol,size:17,sound,action,tintStrength:role==='primary'?84:null});
  PHASES.forEach((phase,i)=>{mount(phase,(i+1)+' '+PHASE_LABELS[phase],null,'secondary',()=>{});buttons[phase].element.setAttribute('aria-label','Phase '+(i+1)+': '+PHASE_LABELS[phase]);});
  mount('place','+1 Truppe',null,'primary',()=>onAction('place'));
  mount('battle','Angriff ansehen','sword','primary',()=>onAction('battle'));
  mount('move','Truppen verlegen','arrow','primary',()=>onAction('move'));
  mount('next','Angriffsphase starten','arrow','primary',()=>onAction('next'));
  mount('cards','Karten ansehen','cards','secondary',()=>onAction('cards'));
  const select=query('#country-choice');
  for(const [key,country] of Object.entries(COUNTRIES)){if(country.owner!==0)continue;const option=document.createElement('option');option.value=key;option.textContent=country.name;select.append(option);}
  select.addEventListener('change',()=>onSelect(select.value));
  const moveInput=query('#move-count');moveInput.addEventListener('input',()=>onCount(Number(moveInput.value)));
  [5,3,2].forEach(n=>query('[data-dice="attack"]').append(die(n)));
  [4,1].forEach(n=>query('[data-dice="defense"]').append(die(n)));
  return {
    resetCount(){moveInput.value='3';},
    feedback(message){text('feedback',message);},
    update(state){
      const own=ownTurn(state),visible=own?state.phase:'waiting',player=PLAYERS[state.actor];
      root.dataset.phase=visible;root.style.setProperty('--army-color',player.color);
      portrait.update({...player,status:own?'du bist am zug':'jetzt am zug',metrics:player.colorName+' · Runde '+state.round});
      text('turn',String(state.turn).padStart(2,'0'));text('countries',player.countries);text('troops',state.totals[state.actor]);text('reserve',own?state.remaining:'–');
      for(const phase of PHASES){const current=phase===state.phase;buttons[phase].element.disabled=!own||!current;buttons[phase].element.setAttribute('aria-pressed',String(current));if(current)buttons[phase].element.setAttribute('aria-current','step');else buttons[phase].element.removeAttribute('aria-current');applyRole(buttons[phase],current?'primary':'secondary');}
      const headings={reinforce:['01','Deine Verstärkung','Mach deine Grenzen stärker.','Verteile deine 6 neuen Truppen auf eigene Länder. Danach beginnt die Angriffsphase.'],attack:['02','Dein Angriff','Wohin zieht dein Feldzug?','Hier kannst du einen Angriff vorbereiten und den Beispielwurf ansehen. Du kannst auch direkt weitergehen.'],fortify:['03','Deine Absicherung','Bring deine Truppen in Position.','Verlege einmal Truppen in ein eigenes Nachbarland. Mindestens eine Truppe bleibt zurück.'],ended:['✓','Dein Zugende','Gut gespielt. Weiter geht’s.','Dein Zug ist abgeschlossen. Die Zusammenfassung wartet auf dich.'],waiting:['…','Der nächste Zug','Kurz durchatmen.','Robin ist am Zug. Deine eigenen Spielaktionen warten bis zu deinem nächsten Zug.']};
      const heading=headings[visible];['step','kicker','title','copy'].forEach((key,i)=>text(key,heading[i]));
      root.querySelectorAll('[data-panel]').forEach(panel=>{panel.hidden=panel.dataset.panel!==visible;});
      select.value=state.selected;select.disabled=!own||state.remaining===0;
      text('progress',state.placed+' von 6 verteilt · '+state.remaining+' übrig');query('[role="progressbar"]').setAttribute('aria-valuenow',String(state.placed));query('.reserve-meter i').style.width=(state.placed/6*100)+'%';
      buttons.place.element.disabled=!own||state.phase!=='reinforce'||state.remaining===0;
      text('attack-from',state.board.westeuropa.armies);text('attack-to',state.board.nordafrika.armies);
      query('.battle-result').hidden=!state.attacked;buttons.battle.element.disabled=state.attacked||!own;
      buttons.battle.label(state.attacked?'Beispielwurf gezeigt':'Angriff ansehen');
      text('move-from',state.board.westeuropa.armies);text('move-to',state.board.suedeuropa.armies);
      moveInput.max=String(maxMove(state));moveInput.disabled=state.fortified||!own;
      const count=Number(moveInput.value),valid=moveInput.value!==''&&Number.isInteger(count)&&count>=1&&count<=maxMove(state);
      text('move-hint',state.fortified?state.moved+' Truppen verlegt.':valid?'Danach: '+(state.board.westeuropa.armies-count)+' → '+(state.board.suedeuropa.armies+count)+' Truppen':'Wähle 1 bis '+maxMove(state)+' Truppen.');
      buttons.move.element.disabled=!own||state.fortified||!valid;buttons.move.label(state.fortified?'Truppen sind verlegt':'Truppen verlegen');
      buttons.next.element.disabled=!own||(state.phase==='reinforce'&&state.remaining>0);
      buttons.next.label(!own?'Warten auf Robin':state.phase==='reinforce'?'Angriffsphase starten':state.phase==='attack'?'Angriff beenden':state.phase==='fortify'?'Zug abschließen':'Zusammenfassung ansehen');
      // While placing troops, +1 owns the action color. Other navigation stays quieter.
      applyRole(buttons.next,own&&((state.phase==='reinforce'&&state.remaining===0)||state.phase==='ended'||(state.phase==='fortify'&&state.fortified))?'primary':'secondary');
    },
  };
}
