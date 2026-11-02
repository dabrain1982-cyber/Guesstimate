const copy=value=>JSON.parse(JSON.stringify(value));
const node=(tag,cls,text)=>{const el=document.createElement(tag);if(cls)el.className=cls;if(text!==undefined)el.textContent=text;return el;};
const STEPS=['Format & Größe','Vorderseite','Rückseite','Karteninhalt','Speichern'];
async function api(path,value){const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),10000);try{const response=await fetch(path,{signal:controller.signal,...(value===undefined?{}:{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(value)})});const result=await response.json();if(!response.ok)throw Error(result.error||'Die Aktion hat nicht geklappt.');return result;}catch(error){if(error.name==='AbortError')throw Error('Die Werkstatt antwortet gerade nicht. Deine Eingaben bleiben erhalten.');throw error;}finally{clearTimeout(timer);}}

export class CardEditor {
  constructor(host,callbacks){this.host=host;this.callbacks=callbacks;this.step=0;this.parentId=null;this.savedId=null;this.revision=0;host.classList.add('card-workshop');host.textContent='Dein Kartensatz wird vorbereitet …';this.ready=this.start();}
  fingerprint(){return JSON.stringify({name:this.name,settings:this.settings,members:this.members});}
  async start(){
    try{
      this.config=await api('/api/card-designs');this.settings=copy(this.config.defaults);this.members=copy(this.config.members);this.name='Mein Kartensatz';this.clean='';
      this.view={member_id:this.members[0].id,face:'both',comparison:true,fit:false,scale:100,tilt:true};
      const id=new URLSearchParams(location.search).get('deck');if(id){const asset=this.callbacks.getData().assets.find(a=>a.kind==='cards'&&a.id===id);if(!asset)throw Error('Der angeforderte Kartensatz wurde nicht gefunden.');this.load(asset);}
      let restored=false,restoredMember=null;
      try{const draft=JSON.parse(sessionStorage.getItem('card-editor-draft'));if(draft?.parentId===this.parentId&&draft.settings&&Array.isArray(draft.members)&&draft.members.length&&JSON.stringify({name:draft.name,settings:draft.settings,members:draft.members})!==this.clean){this.settings=draft.settings;this.members=draft.members;this.name=draft.name;this.savedId=null;this.step=Number.isInteger(draft.step)?Math.max(0,Math.min(4,draft.step)):0;restoredMember=draft.member_id;restored=true;}}catch{}
      this.view.member_id=this.members.some(m=>m.id===restoredMember)?restoredMember:this.members[0].id;this.build();this.steps();this.fields();this.state();this.previewSoon();if(restored)this.message.textContent='Dein ungespeicherter Kartensatz wurde wieder aufgenommen.';
    }catch(error){this.host.replaceChildren(node('p','error',error.message));const retry=node('button','','Erneut laden');retry.addEventListener('click',()=>{this.ready=this.start();});this.host.append(retry);}
  }
  build(){
    const css=node('link');css.rel='stylesheet';css.href='/card-editor.css';this.host.replaceChildren(css);
    const heading=node('div','card-editor-heading'),intro=node('div');intro.append(node('h3','','Dein eigener Kartensatz'),node('p','card-note','Eine gemeinsame Gestaltung für alle Karten. Titel, Text und Zeichen bearbeitest du je Karte.'));
    const fresh=node('button','','Neuen Kartensatz beginnen');fresh.addEventListener('click',()=>this.newDeck());heading.append(intro,fresh);
    this.nav=node('nav','card-editor-steps');this.nav.setAttribute('aria-label','Kartensatz gestalten');const grid=node('div','card-editor-grid');this.controls=node('section','card-editor-controls');this.controls.setAttribute('aria-label','Karteneinstellungen');
    const preview=node('section','card-editor-preview'),title=node('div','card-preview-heading');this.saveState=node('span','card-save-state');title.append(node('h3','','Deine Karten'),this.saveState);
    this.viewControls=node('div','card-preview-controls');this.frame=node('iframe');this.frame.title='Kartenvorschau mit Größenvergleich';this.frame.setAttribute('sandbox','allow-scripts allow-same-origin');const stage=node('div','card-editor-stage');stage.append(this.frame);
    this.summary=node('p','card-note');preview.append(title,this.viewControls,stage,this.summary,node('p','card-note','Die Vergleichskarte rechts bleibt 6 × 9 cm groß. „Alles einpassen“ aktiviert die automatische Einpassung. Vergleich und Ansicht gehören nur zur Vorschau.'));
    grid.append(this.controls,preview);this.message=node('p','card-editor-message');this.message.setAttribute('role','status');this.message.setAttribute('aria-live','polite');
    const bottom=node('div','card-editor-navigation');this.back=node('button','','← Zurück');this.next=node('button','primary','Weiter →');this.back.addEventListener('click',()=>this.go(this.step-1));this.next.addEventListener('click',()=>this.go(this.step+1));bottom.append(this.back,this.next);
    this.host.append(heading,this.nav,grid,this.message,bottom);this.views();
  }
  steps(){this.nav.replaceChildren();STEPS.forEach((title,index)=>{const button=node('button','',index+1+' · '+title);button.setAttribute('aria-current',index===this.step?'step':'false');button.addEventListener('click',()=>this.go(index));this.nav.append(button);});this.back.disabled=this.step===0;this.next.hidden=this.step===4;}
  go(index){this.step=Math.max(0,Math.min(4,index));if(this.step===1||this.step===3)this.view.face='front';if(this.step===2)this.view.face='back';if(this.step===4)this.view.face='both';this.steps();this.fields();this.views();this.remember();this.previewSoon();}
  memberMenu(){this.memberSelect.replaceChildren();this.members.forEach((m,index)=>this.memberSelect.append(new Option(index+1+' · '+(m.title||'Ohne Titel'),m.id)));this.memberSelect.value=this.view.member_id;}
  views(){
    this.viewControls.replaceChildren();const memberLabel=node('label','','Karte im Satz');this.memberSelect=node('select');this.memberSelect.setAttribute('aria-label','Karte im eigenen Satz');this.memberMenu();this.memberSelect.addEventListener('change',()=>{this.view.member_id=this.memberSelect.value;if(this.step===3)this.fields();this.remember();this.previewSoon();});memberLabel.append(this.memberSelect);this.viewControls.append(memberLabel);
    const faceLabel=node('label','','Ansicht'),face=node('select');face.setAttribute('aria-label','Kartenseite in der Vorschau');for(const [value,title] of [['both','Vorder- und Rückseite'],['front','Vorderseite'],['back','Rückseite']])face.append(new Option(title,value));face.value=this.view.face;face.addEventListener('change',()=>{this.view.face=face.value;this.previewSoon();});faceLabel.append(face);this.viewControls.append(faceLabel);
    for(const [key,title] of [['comparison','Größenvergleich'],['fit','Alles einpassen'],...(this.settings.representation==='3d'?[['tilt','Schräg ansehen']]:[])]){const label=node('label','card-view-check'),input=node('input');input.type='checkbox';input.checked=this.view[key];input.addEventListener('change',()=>{this.view[key]=input.checked;this.previewSoon();});label.append(input,document.createTextNode(title));this.viewControls.append(label);}
    const zoomLabel=node('label','card-view-zoom','Näher / weiter'),zoom=node('input');zoom.type='range';zoom.min=50;zoom.max=150;zoom.step=5;zoom.value=this.view.scale;zoom.setAttribute('aria-label','Kartenvorschau näher / weiter');zoom.addEventListener('input',()=>{this.view.scale=Number(zoom.value);this.previewSoon();});zoomLabel.append(zoom);this.viewControls.append(zoomLabel);
  }
  fields(){
    this.controls.replaceChildren(node('h3','',STEPS[this.step]));if(this.step===3){this.cardContents();return;}if(this.step===4){this.saveForm();return;}
    if(this.step===0){
      this.controls.append(node('p','card-note','Die Größe siehst du direkt neben der festen Vergleichskarte. Format und Größe gelten für alle Karten des Satzes.'));
      const formats=node('div','card-format-choices');for(const [ratio,title] of [[.7,'Hochkant'],[1,'Quadratisch'],[1.4,'Querformat']]){const button=node('button','',title);button.addEventListener('click',()=>{this.settings.ratio=ratio;this.changed();this.fields();});formats.append(button);}this.controls.append(formats);
    }else this.controls.append(node('p','card-note',this.step===1?'Farben für die gemeinsame Vorderseite. Den Inhalt der einzelnen Karten legst du unter Karteninhalt fest.':'Die Rückseite gilt für den ganzen Satz. Ihre Farben bleiben unabhängig von der Vorderseite.'));
    for(const f of this.config.fields.filter(f=>f.step===this.step&&!(f.key==='edge'&&this.settings.representation==='2d'))){
      const wrap=node('div','card-editor-field'),label=node('label');label.htmlFor='card-field-'+f.key;label.textContent=f.label;let input;
      if(f.type==='select'){input=node('select');for(const [key,title] of Object.entries(f.options))input.append(new Option(title,key));}else{input=node('input');input.type=f.type;}
      input.id=label.htmlFor;if(f.min!==undefined){input.min=f.min;input.max=f.max;input.step=f.increment;}input.value=this.settings[f.key];
      const output=node('output','card-field-value');output.htmlFor=input.id;const display=()=>f.type==='range'?(f.percent?Math.round(this.settings[f.key]*100)+' %':this.settings[f.key]+' '+f.unit):'';output.textContent=display();
      input.addEventListener(f.type==='select'?'change':'input',()=>{this.settings[f.key]=f.type==='range'?Number(input.value):input.value;output.textContent=display();this.changed();if(f.type==='select'){this.fields();this.views();}});wrap.append(label,input);
      if(f.type==='range'){
        wrap.append(output);const exact=node('details','card-exact'),summary=node('summary','','Genau einstellen'),number=node('input'),factor=f.percent?100:1;number.type='number';number.min=f.min*factor;number.max=f.max*factor;number.step=f.increment*factor;number.value=this.settings[f.key]*factor;number.setAttribute('aria-label',f.label+' · genauer Wert');
        number.addEventListener('input',()=>{if(!number.value||!number.checkValidity())return;input.value=Number(number.value)/factor;input.dispatchEvent(new Event('input'));});input.addEventListener('input',()=>{number.value=Math.round(Number(input.value)*factor*1000)/1000;});exact.append(summary,number);wrap.append(exact);
      }
      this.controls.append(wrap);
    }
  }
  cardContents(){
    const member=this.members.find(m=>m.id===this.view.member_id);this.controls.append(node('p','card-note','Wähle oben eine Karte. Nur ihr Titel, Text und Zeichen ändern sich; die Gestaltung bleibt für den Satz gemeinsam.'));
    const actions=node('div','card-member-actions');const add=node('button','','Neue Karte'),duplicate=node('button','','Karte duplizieren'),remove=node('button','','Karte entfernen');add.disabled=duplicate.disabled=this.members.length>=this.config.max_cards;remove.disabled=this.members.length===1;
    const append=value=>{const next={...value,id:'card-'+crypto.randomUUID().replaceAll('-','')};this.members.push(next);this.view.member_id=next.id;this.views();this.fields();this.changed();};
    add.addEventListener('click',()=>append({title:'Neue Karte',text:'',symbol:'none'}));duplicate.addEventListener('click',()=>append(member));remove.addEventListener('click',()=>{this.members=this.members.filter(m=>m.id!==member.id);this.view.member_id=this.members[0].id;this.views();this.fields();this.changed();});actions.append(add,duplicate,remove);this.controls.append(actions);
    for(const [key,title] of [['title','Kartentitel'],['text','Kartentext'],['symbol','Zeichen']]){
      const label=node('label','card-content-field',title);let input;if(key==='symbol'){input=node('select');for(const [value,title] of Object.entries(this.config.symbols))input.append(new Option(title,value));}else if(key==='text'){input=node('textarea');input.rows=7;input.maxLength=500;}else{input=node('input');input.type='text';input.maxLength=55;}
      input.setAttribute('aria-label',title);input.value=member[key];input.addEventListener(key==='symbol'?'change':'input',()=>{member[key]=input.value;this.memberMenu();this.changed();});label.append(input);this.controls.append(label);
    }
    this.controls.append(node('p','card-note',this.members.length+' von höchstens '+this.config.max_cards+' Karten in diesem Satz.'));
  }
  saveForm(){
    const form=node('form','card-save'),label=node('label','','Name deines Kartensatzes'),name=node('input');name.id='card-design-name';name.maxLength=100;name.required=true;name.value=this.name;label.htmlFor=name.id;name.addEventListener('input',()=>{this.name=name.value;this.savedId=null;this.state();this.remember();});
    const save=node('button','primary','Ganzen Kartensatz speichern');save.type='submit';form.addEventListener('submit',async event=>{event.preventDefault();save.disabled=true;const fingerprint=this.fingerprint();try{const result=await api('/api/card-designs',{name:this.name,settings:copy(this.settings),members:copy(this.members),parent_id:this.parentId});const same=fingerprint===this.fingerprint();if(same){this.parentId=this.savedId=result.asset.id;this.clean=fingerprint;this.url(this.savedId);try{sessionStorage.removeItem('card-editor-draft');}catch{}}await this.callbacks.onSaved(result.asset,same);this.state();this.message.textContent=same?'„'+result.asset.name+'“ mit '+this.members.length+' Karten ist gespeichert.':'Der Stand ist gespeichert. Neuere Änderungen sind noch offen.';}catch(error){this.message.textContent=error.message;}finally{save.disabled=false;}});
    const library=node('a','','Meine Kartensätze ansehen →');library.href='#library/cards';form.append(label,name,save,node('p','card-note','Speichert die Gestaltung und alle '+this.members.length+' Karten zusammen. Frühere Stände bleiben erhalten.'),library,node('p','card-note','Speichern ersetzt noch keinen Kartensatz in einem vorhandenen Spiel.'));this.controls.append(form);
  }
  state(){const saved=this.savedId&&this.fingerprint()===this.clean;this.saveState.textContent=saved?'Gespeichert':'Noch nicht gespeichert';this.callbacks.onChange(saved?this.savedId:null);this.summary.textContent=this.members.length+' Karten im eigenen Satz · '+this.settings.representation.toUpperCase()+' · gemeinsame Vorder- und Rückseitengestaltung';}
  changed(){this.savedId=null;this.message.textContent='';this.state();this.remember();this.previewSoon();}
  remember(){try{sessionStorage.setItem('card-editor-draft',JSON.stringify({parentId:this.parentId,name:this.name,settings:this.settings,members:this.members,step:this.step,member_id:this.view.member_id}));}catch{this.message.textContent='Die Zwischenablage ist voll. Bitte speichere deinen Kartensatz ausdrücklich.';}}
  previewSoon(){clearTimeout(this.timer);const revision=++this.revision;this.timer=setTimeout(async()=>{try{const result=await api('/api/card-designs/preview',{settings:copy(this.settings),members:copy(this.members),view:copy(this.view)});if(revision===this.revision)this.frame.srcdoc=result.html;}catch(error){if(revision===this.revision)this.message.textContent=error.message;}},100);}
  url(id){const url=new URL(location.href);url.searchParams.delete('review');if(id)url.searchParams.set('deck',id);else url.searchParams.delete('deck');history.replaceState(null,'',url.pathname+url.search+url.hash);}
  newDeck(){this.settings=copy(this.config.defaults);this.members=copy(this.config.members);this.name='Mein Kartensatz';this.clean='';this.parentId=this.savedId=null;this.step=0;this.view.member_id=this.members[0].id;this.url(null);this.steps();this.fields();this.views();this.changed();}
  load(asset){
    if(asset.component==='card-design-v1'){this.settings=copy(asset.snapshot.settings);this.members=copy(asset.snapshot.members);this.name=asset.name;this.parentId=this.savedId=asset.id;this.clean=this.fingerprint();}
    else{const old=asset.snapshot.settings;if(typeof old.title!=='string')throw Error('Dieser Originalsatz bleibt vorerst in der Bibliothek. Beginne einen eigenen Satz im Editor.');this.settings={...copy(this.config.defaults),representation:asset.representation,height:Math.round(old.size*1700)/100,ratio:old.ratio,front:old.front,back:old.back,ink:old.ink,front_accent:old.accent,back_accent:old.accent,symbol_color:old.accent};this.members=[{id:'card-1',title:old.title,text:old.text,symbol:old.symbol}];this.name=asset.name+' · Mein Satz';this.parentId=this.savedId=null;this.clean='';}
    this.view.member_id=this.members[0].id;
  }
  async openAsset(asset){await this.ready;if(!this.config||!this.frame)return;this.load(asset);this.url(this.savedId);this.step=0;this.steps();this.fields();this.views();this.state();this.previewSoon();this.remember();}
}
