import {button, icon, die} from './components.js';
import {createPlayerPortrait} from '/shared/player-portrait.js';

for (const slot of document.querySelectorAll('[data-icon]')) slot.replaceChildren(icon(slot.dataset.icon));
const buttons = {};
function mount(key, options) {
  const view = button(options);
  document.querySelector(`[data-button="${key}"]`).replaceChildren(view.element);
  buttons[key]=view;
  return view;
}

let toastTimer;
function toast(message) {
  const note=document.querySelector('#toast');
  note.textContent=message; note.hidden=false;
  clearTimeout(toastTimer); toastTimer=setTimeout(()=>{note.hidden=true;},2800);
}

const phaseData = {
  reinforce:{step:1,tab:'verstärken',icon:'plus',title:'Mach deine Länder stärker.',detail:'6 Truppen warten darauf, auf deine Länder verteilt zu werden.',action:'truppen verteilen',sticker:'stärker!'},
  attack:{step:2,tab:'angreifen',icon:'sword',title:'Angreifen oder sichern?',detail:'Greif weiter an oder wechsle zur Phase „Festigen“. Du entscheidest.',action:'angriff beenden',sticker:'spannend!'},
  fortify:{step:3,tab:'festigen',icon:'shield',title:'Sichere deine Grenzen.',detail:'Verlege einmal Truppen oder beende deinen Zug direkt.',action:'zug beenden',sticker:'sicher!'},
};
let phase='attack';
let actor=0;
const players=[
  {name:'Stormseed',color:'#dab249',portrait:{url:'/shared/waschbaer.webp',alt:'Avatar Waschbär',crop:{scale:1.7,top:-48}}},
  {name:'Robin',color:'#ad3935',portrait:{url:'/shared/fennek.webp',alt:'Avatar Fennek',crop:{scale:1.7,top:-48}}},
];
const playerView=createPlayerPortrait(document.querySelector('#demo-player'));
for (const [key,data] of Object.entries(phaseData)) {
  const view=mount('phase-'+key,{label:`${data.step} ${data.tab}`,symbol:data.icon,small:true,variant:'secondary',action:()=>{phase=key;renderPhase();}});
  view.element.setAttribute('role','tab');
  view.element.id='phase-tab-'+key;
  view.element.setAttribute('aria-controls','phase-description');
}
function renderPhase(message) {
  const data=phaseData[phase];
  document.querySelector('#phase-title').textContent=data.title;
  document.querySelector('#phase-emblem').replaceChildren(icon(data.icon));
  document.querySelector('#phase-description').textContent=data.detail;
  document.querySelector('#phase-description').setAttribute('aria-labelledby','phase-tab-'+phase);
  document.querySelector('#phase-sticker').textContent=data.sticker;
  document.querySelector('#demo-feedback').textContent=message || 'Beispielwerte · Hier werden keine Spielzüge gespeichert.';
  for(const [key] of Object.entries(phaseData)) {
    const control=buttons['phase-'+key].element;
    control.setAttribute('aria-selected',String(key===phase));
    control.tabIndex=key===phase?0:-1;
  }
  buttons['next-phase'].label(data.action);
  playerView.update({...players[actor],status:`Am Zug · ${actor?'Rot':'Gold'} · Phase ${data.step}/3`});
}
mount('next-phase',{label:'angriff beenden',symbol:'arrow',action:()=>{
  if(phase==='reinforce'){phase='attack';renderPhase('Die Angriffsphase ist dran. Nur ein Beispielwechsel.');}
  else if(phase==='attack'){phase='fortify';renderPhase('Angriff beendet. Jetzt kannst du deine Grenzen festigen.');}
  else {actor=1-actor;phase='reinforce';renderPhase(`${players[actor].name} übernimmt den Beispielzug.`);}
}});
const inventory=document.querySelector('#inventory-dialog');
mount('inventory',{label:'3',symbol:'cards',variant:'secondary',ariaLabel:'Beispielinventar mit drei Karten öffnen',action:()=>inventory.showModal()});
mount('close-inventory',{label:'zurück zum tisch',symbol:'arrow',action:()=>inventory.close()});
inventory.addEventListener('click',event=>{if(event.target===inventory)inventory.close();});
document.querySelector('.phase-keys').addEventListener('keydown',event=>{
  if(!['ArrowLeft','ArrowRight','Home','End'].includes(event.key))return;
  event.preventDefault();
  const order=Object.keys(phaseData);let index=order.indexOf(phase);
  index=event.key==='Home'?0:event.key==='End'?2:(index+(event.key==='ArrowRight'?1:2))%3;
  phase=order[index];renderPhase();buttons['phase-'+phase].element.focus();
});

mount('sample-primary',{label:'spiel starten',symbol:'play',action:()=>toast('So fühlt sich die Hauptaktion an. Es wurde kein Spiel gestartet.')});
mount('sample-secondary',{label:'inventar öffnen',symbol:'cards',variant:'secondary',action:()=>inventory.showModal()});
const pinned=mount('sample-pressed',{label:'druck festhalten',symbol:'hand',variant:'blue',action:()=>{
  const held=pinned.element.getAttribute('aria-pressed')!=='true';
  pinned.element.setAttribute('aria-pressed',String(held));
  pinned.label(held?'wieder loslassen':'druck festhalten');
}});
pinned.element.setAttribute('aria-pressed','false');
mount('sample-disabled',{label:'nicht verfügbar',symbol:'shield',disabled:true});
mount('sample-danger',{label:'lobby beenden',symbol:'flag',variant:'danger',small:true,action:()=>toast('Nur ein Gestaltungsbeispiel. Deine normale Lobby bleibt geöffnet.')});
mount('sample-focus',{label:'fokus zeigen',symbol:'keyboard',variant:'secondary',small:true,action:()=>{
  buttons['sample-primary'].element.dataset.showFocus='true';
  buttons['sample-primary'].element.focus();
}});
buttons['sample-primary'].element.addEventListener('blur',()=>{delete buttons['sample-primary'].element.dataset.showFocus;});
document.querySelector('#depth').addEventListener('input',event=>{
  document.documentElement.style.setProperty('--button-depth',`${Number(event.target.value)/16}em`);
  document.querySelector('#depth-label').textContent={4:'dezent',6:'spürbar',8:'kräftig',10:'satt',12:'extra plastisch'}[event.target.value];
});

let rolls=2;
let values=[2,5,3,6,1];
function renderDice() {
  document.querySelector('#roll-count').textContent=String(rolls);
  const tray=document.querySelector('#dice-tray');tray.replaceChildren(...values.map(die));
  tray.setAttribute('aria-label','Beispielwurf: '+values.join(', '));
  document.querySelector('#dice-heading').textContent=rolls===3?'Jetzt zählt dein Wurf.':'Da geht noch was!';
  document.querySelector('#dice-description').textContent=rolls===3?'Alle Würfe verbraucht. Zeit für deine Wahl.':`${3-rolls} ${rolls===2?'Wurf ist':'Würfe sind'} noch übrig.`;
  const status=document.querySelector('#dice-status');status.textContent=rolls===3?'bereit zum eintragen':'du bist dran';
  status.className='status-badge '+(rolls===3?'status-ready':'status-active');
  buttons.roll.element.disabled=rolls===3;
  buttons.roll.label(rolls===3?'würfe verbraucht':'noch mal würfeln');
}
mount('roll',{label:'noch mal würfeln',symbol:'dice',action:()=>{if(rolls<3){rolls++;values=values.map((value,index)=>(value+index+2)%6+1);renderDice();}}});
mount('reset-roll',{label:'',symbol:'reset',variant:'secondary',ariaLabel:'Beispielwürfe zurücksetzen',action:()=>{rolls=1;values=[2,5,3,6,1];renderDice();}});

let seconds=18;let interval=null;
function stopTimer(){clearInterval(interval);interval=null;}
function renderTimer() {
  document.querySelector('#timer-value').textContent='00:'+String(seconds).padStart(2,'0');
  document.querySelector('#time-fill').style.width=`${seconds/30*100}%`;
  document.querySelector('#time-track').setAttribute('aria-valuenow',String(seconds));
  const urgent=seconds<=8;
  document.querySelector('.timer-panel').classList.toggle('is-urgent',urgent);
  document.querySelector('#timer-heading').textContent=seconds===0?'Die Zeit ist um.':urgent?'Jetzt gilt’s!':'Deine Zeit läuft.';
  document.querySelector('#timer-status').textContent=seconds===0?'zeit abgelaufen':urgent?'letzte sekunden':'deine antwort zählt';
  buttons.timer.label(interval?'timer pausieren':seconds===0?'zeit abgelaufen':'timer starten');
  buttons.timer.element.disabled=seconds===0;
}
mount('timer',{label:'timer starten',symbol:'play',variant:'blue',action:()=>{
  if(interval)stopTimer();else interval=setInterval(()=>{seconds--;if(seconds===0)stopTimer();renderTimer();},1000);
  renderTimer();
}});
mount('reset-timer',{label:'',symbol:'reset',variant:'secondary',ariaLabel:'Beispielzeit zurücksetzen',action:()=>{stopTimer();seconds=18;renderTimer();}});
window.addEventListener('pagehide',()=>{stopTimer();clearTimeout(toastTimer);},{once:true});
renderPhase();renderDice();renderTimer();
document.body.dataset.ready='true';
