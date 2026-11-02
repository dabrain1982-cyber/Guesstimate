import {renderButton} from '/workshop/renderer.js';
import {createSound} from '/workshop/sound.js';
import {createTurnConsole,roleRecipe} from './turn-console.js';
import {createExample,act,PLAYERS,ownTurn,maxMove} from './model.js';

const $=selector=>document.querySelector(selector);
async function start(){
  const [profile,catalog]=await Promise.all([fetch('/profile.json').then(r=>r.json()),fetch('/sound-catalog.json').then(r=>r.json())]);
  const recipe=profile.recipe,soundEnabled=$('#sound-enabled');
  const audio=createSound(message=>{$('#sound-state').textContent=message;});audio.configure(catalog.sounds);
  const sound={play:(value,edge)=>{if(soundEnabled.checked)audio.play(value,edge);}};
  soundEnabled.addEventListener('change',()=>{audio.stop();$('#sound-state').textContent=soundEnabled.checked?'Materialklang bereit · Planken-Kandidat · 30 %':'Ohne Ton';});
  let state=createExample(),moveCount=3,modalAction=null,busy=false,returnFocus=null;
  const dialog=$('#action-dialog');
  const actionButton=(host,label,symbol,role,action)=>renderButton($(host),roleRecipe(recipe,role),{label,symbol,size:17,sound,action,tintStrength:role==='primary'?84:null});
  const confirm=actionButton('#dialog-confirm','Bestätigen','check','primary',()=>{
    if(busy||!modalAction)return;
    busy=true;confirm.element.disabled=true;cancel.element.disabled=true;
    try{modalAction();$('#dialog-status').textContent='Erledigt.';setTimeout(closeDialog,recipe.settings.duration);}
    catch(error){busy=false;confirm.element.disabled=false;cancel.element.disabled=false;$('#dialog-status').textContent=error.message;}
  });
  const cancel=actionButton('#dialog-cancel','Zurück zum Zug',null,'secondary',()=>{if(!busy)closeDialog();});
  function closeDialog(){dialog.close();busy=false;modalAction=null;returnFocus?.focus();}
  function openDialog({kicker='Deine Entscheidung',title,html,label='Bestätigen',action}){
    returnFocus=document.activeElement;$('#dialog-kicker').textContent=kicker;$('#dialog-title').textContent=title;$('#dialog-body').innerHTML=html;$('#dialog-status').textContent='';
    modalAction=action;busy=false;confirm.label(label);confirm.element.hidden=!action;confirm.element.disabled=false;cancel.element.disabled=false;cancel.label(action?'Zurück zum Zug':'Zurück zum Zug');
    dialog.showModal();cancel.element.focus();
  }
  dialog.addEventListener('cancel',event=>{event.preventDefault();if(!busy)closeDialog();});
  function commit(action,payload){state=act(state,action,payload);view.feedback('');render();}
  function summary(){openDialog({kicker:'Dein Zug · Runde '+state.round,title:'Der nächste Zug gehört Robin.',html:'<div class="summary-grid"><div><b>'+state.placed+'</b><span>Truppen verteilt</span></div><div><b>'+(state.attacked?'1':'0')+'</b><span>Beispielangriff</span></div><div><b>'+state.moved+'</b><span>Truppen verlegt</span></div></div><p>Kein Land erobert, keine neue Länderkarte. Dein Zug ist abgeschlossen. Du entscheidest, wann du weitergibst.</p>',label:'An Robin übergeben',action:()=>commit('pass')});}
  function handleAction(action){
    try{
      if(action==='place')commit('place');
      else if(action==='next'){
        if(state.phase==='ended')summary();else if(state.phase==='fortify'){commit('end');summary();}else commit('advance');
      }else if(action==='battle')openDialog({kicker:'Angriff vorbereiten',title:'Westeuropa → Nordafrika',html:'<div class="dialog-route"><strong>'+state.board.westeuropa.armies+'<small>deine Truppen</small></strong><span>gegen</span><strong>'+state.board.nordafrika.armies+'<small>Robins Truppen</small></strong></div><p>3 Angriffswürfel gegen 2 Verteidigungswürfel. Für diesen Entwurf steht das Ergebnis fest: 5 · 3 · 2 gegen 4 · 1.</p><p class="dialog-note">So lassen sich Bestätigung und Ergebnisanzeige ausprobieren.</p>',label:'Beispielwurf zeigen',action:()=>commit('attack-demo')});
      else if(action==='move'){
        if(!Number.isInteger(moveCount)||moveCount<1||moveCount>maxMove(state))throw new Error('Wähle eine gültige Anzahl.');
        const planned=moveCount;openDialog({kicker:'Grenzen festigen',title:planned+' Truppen verlegen?',html:'<div class="transfer-preview"><div><span>Westeuropa</span><strong>'+state.board.westeuropa.armies+' → '+(state.board.westeuropa.armies-planned)+'</strong></div><div><span>Südeuropa</span><strong>'+state.board.suedeuropa.armies+' → '+(state.board.suedeuropa.armies+planned)+'</strong></div></div><p>Die Länder grenzen aneinander und gehören dir. Festigen ist einmal pro Zug möglich.</p>',label:'Verlegung bestätigen',action:()=>commit('fortify',{count:planned})});
      }else if(action==='cards')openDialog({kicker:'Dein Inventar · Beispiel',title:'Drei Karten in deiner Hand.',html:'<div class="example-cards"><div><span>Infanterie</span><strong>A</strong></div><div><span>Kavallerie</span><strong>B</strong></div><div><span>Artillerie</span><strong>C</strong></div></div><p>Platzhalter für den Blick ins Inventar. Die Karten stammen aus keiner gespeicherten Partie.</p>',action:null});
    }catch(error){view.feedback(error.message);}
  }
  const view=createTurnConsole($('#turn-console-host'),{recipe,sound,onAction:handleAction,onSelect:country=>{try{commit('select',{country});}catch(error){view.feedback(error.message);}},onCount:count=>{moveCount=count;view.update(state);}});
  const pins=new Map();
  for(const [key,country] of Object.entries(state.board)){
    const pin=document.createElement('button');pin.type='button';pin.className='army-pin';pin.style.left=country.x+'%';pin.style.top=country.y+'%';pin.style.setProperty('--pin-color',PLAYERS[country.owner].color);pin.innerHTML='<span></span>';
    pin.addEventListener('click',()=>{try{commit('select',{country:key});}catch(error){view.feedback(error.message);}});$('#board-pins').append(pin);pins.set(key,pin);
  }
  actionButton('#reset-example','Beispiel zurücksetzen','reset','secondary',reset);
  $('#scenario').addEventListener('change',reset);
  function reset(){if(dialog.open)closeDialog();audio.stop();state=createExample($('#scenario').value);moveCount=3;view.resetCount();view.feedback('');render();}
  function render(){
    view.update(state);$('#board-round').textContent=String(state.round).padStart(2,'0');
    for(const [key,pin] of pins){const country=state.board[key];pin.querySelector('span').textContent=country.armies;pin.setAttribute('aria-label',country.name+': '+country.armies+' Truppen · '+PLAYERS[country.owner].colorName);pin.title=pin.getAttribute('aria-label');pin.setAttribute('aria-pressed',String(key===state.selected));pin.disabled=!ownTurn(state)||state.phase!=='reinforce'||country.owner!==state.actor||state.remaining===0;}
    const country=state.board[state.selected];$('#board-selection').textContent=country.name;$('#board-selection-detail').textContent=country.armies+' Truppen · '+PLAYERS[country.owner].colorName;
    const log=$('#turn-log');log.replaceChildren();
    for(const message of state.log.length?state.log:['Dein Zug beginnt. 6 neue Truppen warten auf ihren Einsatz.']){const item=document.createElement('li');item.textContent=message;log.append(item);}
  }
  $('#recipe-description').textContent='Aus „'+profile.source_button.name+'“ und „'+profile.source_shape.name+'“: deine Kontur mit '+recipe.contour.points.length+' Punkten, Fredoka und dezentem Druckweg. Form und Oberfläche bleiben Arbeitsentwürfe.';
  const credit=catalog.sounds.find(row=>row.id===recipe.settings.sound);
  const creditLine=document.createElement('p');creditLine.className='sound-credit';creditLine.textContent='Klang-Kandidat: '+credit.name+' · '+credit.author+' · '+credit.license+'. Ohne Ton gestartet. ';
  const credits=document.createElement('a');credits.href='/sound-credits';credits.target='_blank';credits.rel='noopener';credits.textContent='Quelle & Lizenz ↗';creditLine.append(credits);$('.design-note').append(creditLine);
  render();
}
start().catch(error=>{const target=$('#startup-error');target.hidden=false;target.textContent='Die Tafel konnte nicht geladen werden: '+error.message;});
