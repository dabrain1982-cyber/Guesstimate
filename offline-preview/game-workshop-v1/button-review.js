// A read-only comparison of registered originals. Decisions stay in the conversation.
const n=(tag,className,text)=>{const el=document.createElement(tag);if(className)el.className=className;if(text!==undefined)el.textContent=text;return el;};
export const REVIEW_GROUPS=[
  {id:'start',title:'Startseitenstil: Zustände und Nachholen',proposal:'Festgelegt: 01 und 02 sind dieselbe Startseitenaktion in verschiedenen Spielständen. 03 soll zum selben Startseitenstil passen. Seine aktuelle Tiefe bleibt für deinen persönlichen Editortest unverändert.',cards:[
    {number:'01',label:'spielen →',title:'Spielen / Runde fortsetzen',purpose:'Startet die heutige Runde oder setzt sie fort.',role:'Zustand: Runde offen oder bereits begonnen'},
    {number:'02',label:'heutiges ergebnis →',title:'Heutiges Ergebnis',purpose:'Öffnet nach der Runde das Tagesergebnis.',role:'Dieselbe Position nach abgeschlossener Runde'}]},
  {id:'actions',title:'Spielaktion und Abschlusszustand',proposal:'Weiterer Vorschlag: 05 als gesperrten Abschlusszustand von 04 führen. Das ist noch nicht zusammengeführt.',cards:[
    {number:'03',label:'alle 3 verpassten runden nachholen',title:'Alle verpassten Runden nachholen',purpose:'Gehört zum Startseitenstil, besitzt derzeit aber eine andere Gestaltung mit fester Seitenwand. Du prüfst die Anpassung selbst im gemeinsamen Editor.',role:'Ziel: derselbe Startseitenstil',testEditor:true},
    {number:'04',label:'weiter zu frage 2',title:'Weiter zur nächsten Frage',purpose:'Führt nach der Auflösung weiter. Die vorhandene Wartezeit und der Countdown bleiben Teil der Spielfunktion.',role:'Nächster Schritt im Spiel'},
    {number:'05',label:'schau morgen wieder rein',title:'Runde abgeschlossen',purpose:'Zeigt den Abschluss an und ist nicht anklickbar.',role:'Gesperrter Abschlusszustand'}]},
  {id:'secondary',title:'Zurückhaltende Nebenaktionen',proposal:'Vorschlag: eine gemeinsame Rolle als Nebenaktion. Die Proportionen und Schriftgrößen unterscheiden sich jedoch; eine optische Angleichung müssen wir vorher festlegen.',cards:[
    {number:'06',label:'lieber nur heute spielen',title:'Nur heute spielen',purpose:'Wählt im Nachhol-Dialog die heutige Runde.',role:'Nebenaktion im Dialog'},
    {number:'07',label:'3 verpasste runden nachholen',title:'Verpasste Runden nachholen',purpose:'Öffnet die Nachholrunden von der Startseite aus. Die Zahl ist ein Beispielwert.',role:'Nebenaktion auf der Startseite'}]},
  {id:'roles',title:'Eigene Rollen zunächst behalten',proposal:'Vorschlag: Navigation, auswählbare Antwort und unauffällige Textaktion vorerst getrennt führen. Ihre unterschiedlichen Aufgaben sind beabsichtigt.',cards:[
    {number:'08',label:'Vorheriges Spiel',title:'Vorheriges / nächstes Spiel',purpose:'Blättert zwischen den Spielangeboten auf der Startseite.',role:'Navigation mit Pfeilsymbol'},
    {number:'09',label:'Beispielantwort',title:'Antwort auswählen',purpose:'Wählt bei Zuordnungsfragen ein Gegenstück. Die Auswahl muss sichtbar erkennbar bleiben.',role:'Auswahl mit eigenem Zustand',selection:true},
    {number:'10',label:'abmelden',title:'Abmelden',purpose:'Beendet die Anmeldung. Die Aktion besitzt keine gefüllte Buttonfläche.',role:'Zurückhaltende Textaktion'}]}
];
REVIEW_GROUPS[0].cards.push(REVIEW_GROUPS[1].cards.shift());

export function resolveReview(assets){
  return REVIEW_GROUPS.map(group=>({...group,cards:group.cards.map(spec=>{
    const asset=assets.find(a=>a.source==='game'&&a.game==='Guesstimate'&&a.label===spec.label);
    return {...spec,asset,variants:asset?assets.filter(a=>a.source==='game'&&a.model_id===asset.model_id):[]};
  })}));
}

export function normalDifference(a,b){
  if(!a?.base||!b?.base)return null;
  const withoutText=value=>Object.fromEntries(Object.entries(value).filter(([key])=>!['text','initial'].includes(key)));
  const left=withoutText(a.base),right=withoutText(b.base);
  return Object.keys(left).filter(key=>JSON.stringify(left[key])!==JSON.stringify(right[key]));
}

function describe(profile){
  const p=profile.base;if(!p)return null;
  const radius=p.contour.points.some(point=>point.round>0)?'gerundet':'ohne Rundung';
  const surface=p.background.includes('gradient(')?'Farbverlauf':p.opacity===0?'keine gefüllte Fläche':p.opacity<100?'durchscheinende Fläche':'Farbfläche';
  const depth=p.depth.x||p.depth.y?'versetzte Seitenwand':p.soft_shadow!=='none'?'Leuchten / weicher Schatten':'ohne Tiefe';
  return [['Form',radius+' · '+Math.round(p.width)+' × '+Math.round(p.height)+' px'],['Fläche',surface],['Tiefe',depth],['Schrift',Math.round(p.font_size*10)/10+' px · '+(Number(p.font_weight)>=700?'kräftig':'normal')]];
}

export class ButtonReview{
  constructor(host,{preview,request,inspect,edit}){this.host=host;this.preview=preview;this.request=request;this.inspect=inspect;this.edit=edit;this.generation=0;}
  async render(assets){
    const generation=++this.generation,groups=resolveReview(assets),profiles=new Map(),pending=[];
    this.host.replaceChildren();
    const note=n('p','review-intro','Originale aus der Bibliothek. Die Vorschau führt keine Spielaktion aus. Bereits Festgelegtes ist gekennzeichnet; weitere Zusammenführungen bleiben Vorschläge.');this.host.append(note);
    for(const group of groups){
      const section=n('section','review-section');section.dataset.reviewGroup=group.id;
      section.append(n('h3','',group.title));
      const grid=n('div','review-grid');section.append(grid);this.host.append(section);
      for(const item of group.cards){
        const card=n('article','review-card');card.dataset.reviewNumber=item.number;card.dataset.asset=item.asset?.id||'';
        const heading=n('div','review-card-heading');heading.append(n('span','review-number',item.number),n('h4','',item.title));card.append(heading);
        if(!item.asset){card.append(n('p','','Diese Quelle ist inzwischen verändert oder nicht mehr vorhanden. Vor einer Entscheidung erneut prüfen.'));grid.append(card);continue;}
        const preview=this.preview(item.asset,true);preview.classList.add('review-original');card.append(preview);
        const originalFrame=preview.querySelector('iframe');
        if(originalFrame){originalFrame.loading='eager';pending.push(new Promise(resolve=>{const timer=setTimeout(resolve,5000);originalFrame.addEventListener('load',()=>{Promise.resolve(originalFrame.contentDocument?.fonts?.ready).finally(()=>{clearTimeout(timer);requestAnimationFrame(()=>resolve());});},{once:true});}));}
        const body=n('div','review-card-body');body.append(n('p','review-role',item.role),n('p','review-purpose',item.purpose));
        if(item.testEditor&&this.edit){const edit=n('button','review-test','Im Editor testen');edit.type='button';edit.addEventListener('click',()=>this.edit(item.asset));body.append(edit);}
        const facts=n('dl','review-facts');facts.setAttribute('aria-label','Die vier Buttonbausteine');body.append(facts);
        pending.push(this.request('/api/game-buttons/'+encodeURIComponent(item.asset.id)+'/recipe').then(result=>{
          if(generation!==this.generation)return;profiles.set(item.number,result.recipe);
          for(const [name,value]of describe(result.recipe)||[]){const row=n('div');row.append(n('dt','',name),n('dd','',value));facts.append(row);}
        }).catch(()=>{facts.append(n('div','','Die Ausgangswerte konnten gerade nicht gelesen werden.'));}));
        if(item.selection){
          const toggle=n('button','review-selection','Ausgewählt anzeigen');toggle.type='button';toggle.setAttribute('aria-pressed','false');let selected=false;
          const frame=preview.querySelector('iframe');
          const apply=()=>{const root=frame?.contentDocument?.querySelector('#source-context .match-option');if(!root)return;root.classList.toggle('is-selected',selected);root.setAttribute('aria-pressed',String(selected));};
          frame?.addEventListener('load',apply);toggle.addEventListener('click',()=>{selected=!selected;toggle.setAttribute('aria-pressed',String(selected));toggle.textContent=selected?'Normale Ansicht zeigen':'Ausgewählt anzeigen';apply();});body.append(toggle);
        }
        const uses=n('details','review-uses'),summary=n('summary','','Beschriftungen & Einsatzorte ('+item.variants.length+')'),list=n('ul');
        for(const variant of item.variants)list.append(n('li','',variant.game+' · '+variant.usage+' · '+variant.label));uses.append(summary,list);body.append(uses);
        const see=n('button','review-inspect','Original ansehen');see.type='button';see.setAttribute('aria-label','Original '+item.number+' ansehen');see.addEventListener('click',()=>this.inspect(item.asset));body.append(see);
        card.append(body);grid.append(card);
      }
      const findings=n('p','review-findings');findings.dataset.reviewFinding=group.id;section.append(findings,n('p','review-proposal',group.proposal));
    }
    await Promise.allSettled(pending);if(generation!==this.generation)return;
    const same=(a,b)=>{const differences=normalDifference(profiles.get(a),profiles.get(b));return differences!==null&&!differences.length;};
    const finding=id=>this.host.querySelector('[data-review-finding="'+id+'"]');
    finding('start').textContent=same('01','02')?'01 und 02: gleiche Normaldarstellung, unterschiedliche Spielstände. 03 weicht derzeit sichtbar ab, besonders durch die feste Seitenwand.':'01 und 02: Vor einer Zusammenführung müssen die sichtbaren Unterschiede geprüft werden.';
    finding('actions').textContent='04 und 05: dieselbe Grundform, aber andere Farben und ein gesperrter Abschlusszustand. Die vorhandene Wartezeit und Spielfunktion bleiben erhalten.';
    finding('secondary').textContent='06 ist kompakter und höher, 07 breiter und flacher. Das ist aktuell keine rein proportionale Verkleinerung.';
    finding('roles').textContent='Bei 09 kannst du den tatsächlichen Auswahlzustand aus der vorhandenen Gestaltung ansehen.';
    this.host.dataset.ready='true';
  }
}
