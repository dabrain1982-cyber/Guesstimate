// UI-only example state. It never reads or changes a saved game.
export const PHASES=['reinforce','attack','fortify'];
export const PHASE_LABELS={reinforce:'verstärken',attack:'angreifen',fortify:'festigen',ended:'zug abgeschlossen'};
export const PLAYERS=[
  {name:'Stormseed',color:'#dab249',colorName:'Gold',countries:14,portrait:{url:'/shared/waschbaer.webp',alt:'Avatar Waschbär',crop:{scale:1.7,top:-48}}},
  {name:'Robin',color:'#ad3935',colorName:'Rot',countries:12,portrait:{url:'/shared/fennek.webp',alt:'Avatar Fennek',crop:{scale:1.7,top:-48}}},
];
export const COUNTRIES={
  westeuropa:{name:'Westeuropa',owner:0,armies:8,x:42.7,y:49.3},
  suedeuropa:{name:'Südeuropa',owner:0,armies:6,x:50.1,y:47.7},
  peru:{name:'Peru',owner:0,armies:4,x:15.6,y:68},
  nordafrika:{name:'Nordafrika',owner:1,armies:3,x:43.6,y:60.1},
  aegypten:{name:'Ägypten',owner:1,armies:5,x:50.9,y:56},
  nordeuropa:{name:'Nordeuropa',owner:1,armies:6,x:49.2,y:43.9},
};
export const ownTurn=state=>state.actor===state.viewer;
export const maxMove=state=>state.board.westeuropa.armies-1;
export function createExample(scenario='reinforce'){
  if(!['reinforce','attack','fortify','ended','waiting'].includes(scenario))throw new Error('Unbekannte Beispielansicht.');
  const state={scenario,viewer:0,actor:0,round:4,turn:7,phase:'reinforce',remaining:6,placed:0,totals:[42,37],
    board:structuredClone(COUNTRIES),selected:'westeuropa',fortified:false,moved:0,attacked:false,log:[]};
  if(['attack','fortify','ended'].includes(scenario)){
    state.remaining=0;state.placed=6;state.board.westeuropa.armies+=6;state.totals[0]+=6;state.phase=scenario;
    state.log.push('6 Beispieltruppen sind bereits verteilt.');
  }
  if(scenario==='waiting'){
    state.actor=1;state.phase='attack';state.remaining=0;state.totals[1]+=4;state.board.aegypten.armies+=4;
    state.log.push('Beispielansicht: Robin ist am Zug.');
  }
  return state;
}
export function act(current,action,payload={}){
  if(!ownTurn(current))throw new Error('Du wartest auf den nächsten Zug.');
  const state=structuredClone(current);
  const require=(condition,message)=>{if(!condition)throw new Error(message);};
  if(action==='select'){
    require(state.phase==='reinforce'&&state.board[payload.country]?.owner===state.actor,'Wähle ein eigenes Land.');
    state.selected=payload.country;return state;
  }
  if(action==='place'){
    require(state.phase==='reinforce'&&state.remaining>0,'Zuerst die Verstärkungsphase wählen.');
    const country=state.board[state.selected];require(country.owner===state.actor,'Verstärke ein eigenes Land.');
    country.armies++;state.remaining--;state.placed++;state.totals[state.actor]++;
    state.log.push('+1 Truppe in '+country.name+'.');
  }else if(action==='advance'){
    if(state.phase==='reinforce'){require(state.remaining===0,'Verteile zuerst alle verfügbaren Truppen.');state.phase='attack';state.log.push('Angriffsphase begonnen.');}
    else if(state.phase==='attack'){state.phase='fortify';state.log.push('Angriff beendet. Jetzt kannst du festigen.');}
    else throw new Error('Diese Phase kann nicht übersprungen werden.');
  }else if(action==='attack-demo'){
    require(state.phase==='attack'&&!state.attacked,'Der Beispielwurf wurde bereits gezeigt.');
    require(state.board.westeuropa.armies>=4&&state.board.nordafrika.armies>=2,'Dieser Beispielwurf ist jetzt nicht möglich.');
    state.board.nordafrika.armies-=2;state.totals[1]-=2;state.attacked=true;
    state.log.push('Beispielwurf: 5 · 3 · 2 gegen 4 · 1. Nordafrika verliert 2 Truppen.');
  }else if(action==='fortify'){
    require(state.phase==='fortify'&&!state.fortified,'Festigen ist einmal pro Zug möglich.');
    const count=payload.count;
    require(Number.isInteger(count)&&count>=1&&count<=maxMove(state),'Mindestens eine Truppe muss in Westeuropa bleiben.');
    state.board.westeuropa.armies-=count;state.board.suedeuropa.armies+=count;state.fortified=true;state.moved=count;
    state.log.push(count+' Truppen von Westeuropa nach Südeuropa verlegt.');
  }else if(action==='end'){
    require(state.phase==='fortify','Beende zuerst die laufende Phase.');state.phase='ended';
    state.log.push('Zug abgeschlossen. Die Übergabe steht bereit.');
  }else if(action==='pass'){
    require(state.phase==='ended','Schließe zuerst deinen Zug ab.');state.actor=1;state.turn++;state.phase='reinforce';state.remaining=4;
    state.log.push('Der nächste Beispielzug gehört Robin.');
  }else throw new Error('Unbekannte Beispielaktion.');
  state.log=state.log.slice(-7);return state;
}
