const copy=value=>JSON.parse(JSON.stringify(value));
const node=(tag,cls,text)=>{const element=document.createElement(tag);if(cls)element.className=cls;if(text!==undefined)element.textContent=text;return element;};
const STEPS=['Form','Größe & Proportionen','Material & Farben','Speichern'];
async function api(path,payload){
  const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),10000);
  try{const response=await fetch(path,{signal:controller.signal,...(payload===undefined?{}:{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)})});const value=await response.json();if(!response.ok)throw Error(value.error||'Die Aktion hat nicht geklappt.');return value;}
  catch(error){if(error.name==='AbortError')throw Error('Die Werkstatt antwortet gerade nicht. Deine Eingaben bleiben erhalten.');throw error;}finally{clearTimeout(timer);}
}

export class PieceEditor {
  constructor(host,callbacks){this.host=host;this.callbacks=callbacks;this.step=0;this.parentId=null;this.savedId=null;this.revision=0;host.classList.add('piece-workshop');host.textContent='Deine Figuren werden vorbereitet …';this.ready=this.start();}
  fingerprint(){return JSON.stringify({name:this.name,settings:this.settings});}
  async start(){
    try{
      this.config=await api('/api/piece-designs');this.settings=copy(this.config.defaults);this.name='Mein Figurensatz';this.clean='';this.view={role:'pawn',side:'both',fit:false,comparison:true,scale:100};
      const id=new URLSearchParams(location.search).get('piece');
      if(id){const asset=this.callbacks.getData().assets.find(a=>a.kind==='pieces'&&a.id===id);if(!asset)throw Error('Der angeforderte Figurensatz wurde nicht gefunden.');this.load(asset);}
      let recovered=false;
      try{const draft=JSON.parse(sessionStorage.getItem('piece-editor-draft'));if(draft?.parentId===this.parentId&&draft.settings&&JSON.stringify({name:draft.name,settings:draft.settings})!==this.clean){this.settings=draft.settings;this.name=draft.name;this.savedId=null;this.step=Number.isInteger(draft.step)?Math.max(0,Math.min(3,draft.step)):0;recovered=true;}}catch{}
      this.build();this.fields();this.steps();this.state();this.previewSoon();if(recovered)this.message.textContent='Dein ungespeicherter Figurensatz wurde wieder aufgenommen.';
    }catch(error){this.host.replaceChildren(node('p','error',error.message));const retry=node('button','','Erneut laden');retry.addEventListener('click',()=>{this.ready=this.start();});this.host.append(retry);}
  }
  build(){
    const css=node('link');css.rel='stylesheet';css.href='/piece-editor.css';this.host.replaceChildren(css);
    const header=node('div','piece-editor-heading'),intro=node('div');intro.append(node('h3','','Dein Figurensatz'),node('p','piece-note','Gestalte einen gemeinsamen Satz. Die Änderungen gelten für alle Rollen und beide Seiten; jede Seite hat ihre eigene Farbe.'));
    const fresh=node('button','','Neuen Figurensatz beginnen');fresh.addEventListener('click',()=>this.newSet());header.append(intro,fresh);
    this.nav=node('nav','piece-editor-steps');this.nav.setAttribute('aria-label','Figuren gestalten');
    const grid=node('div','piece-editor-grid');this.controls=node('section','piece-editor-controls');this.controls.setAttribute('aria-label','Figureneinstellungen');
    const column=node('section','piece-editor-preview'),title=node('div','piece-preview-heading');this.savedState=node('span','piece-save-state');title.append(node('h3','','Deine Figuren'),this.savedState);
    this.viewControls=node('div','piece-preview-controls');this.frame=node('iframe');this.frame.title='Figurenvorschau mit Größenvergleich';this.frame.setAttribute('sandbox','allow-scripts allow-same-origin');
    const stage=node('div','piece-editor-stage');stage.append(this.frame);this.summary=node('p','piece-note');
    column.append(title,this.viewControls,stage,this.summary,node('p','piece-note','Karte und graue Vergleichsfigur bleiben gleich groß. So siehst du Größenänderungen direkt. „Alles einpassen“ aktiviert die automatische Einpassung. Die Hilfen und die Vorschaurolle werden nicht mitgespeichert.'));
    grid.append(this.controls,column);this.message=node('p','piece-editor-message');this.message.setAttribute('role','status');this.message.setAttribute('aria-live','polite');
    const navigation=node('div','piece-editor-navigation');this.back=node('button','','← Zurück');this.next=node('button','primary','Weiter →');this.back.addEventListener('click',()=>this.go(this.step-1));this.next.addEventListener('click',()=>this.go(this.step+1));navigation.append(this.back,this.next);
    this.host.append(header,this.nav,grid,this.message,navigation);this.views();
  }
  views(){
    this.viewControls.replaceChildren();
    if(this.settings.set==='chess'){
      const label=node('label','','Vorschaurolle'),select=node('select');select.setAttribute('aria-label','Vorschaurolle');
      for(const [key,title] of Object.entries({...this.config.roles,all:'Alle sechs Rollen'}))select.append(new Option(title,key));select.value=this.view.role;
      select.addEventListener('change',()=>{this.view.role=select.value;this.previewSoon();});label.append(select);this.viewControls.append(label);
    }
    const side=node('label','','Seiten'),select=node('select');select.setAttribute('aria-label','Seiten in der Vorschau');
    for(const [key,title] of [['both','Beide Seiten'],['light','Erste Seite'],['dark','Zweite Seite']])select.append(new Option(title,key));select.value=this.view.side;select.addEventListener('change',()=>{this.view.side=select.value;this.previewSoon();});side.append(select);this.viewControls.append(side);
    for(const [key,title] of [['comparison','Größenvergleich zeigen'],['fit','Alles einpassen']]){
      const label=node('label','piece-view-check'),input=node('input');input.type='checkbox';input.checked=this.view[key];input.addEventListener('change',()=>{this.view[key]=input.checked;this.previewSoon();});label.append(input,document.createTextNode(title));this.viewControls.append(label);
    }
    const zoomLabel=node('label','piece-view-zoom','Näher / weiter'),zoom=node('input');zoom.type='range';zoom.min=50;zoom.max=150;zoom.step=5;zoom.value=this.view.scale;zoom.setAttribute('aria-label','Figurenvorschau näher / weiter');zoom.addEventListener('input',()=>{this.view.scale=Number(zoom.value);this.previewSoon();});zoomLabel.append(zoom);this.viewControls.append(zoomLabel);
  }
  steps(){this.nav.replaceChildren();STEPS.forEach((text,index)=>{const button=node('button','',index+1+' · '+text);button.setAttribute('aria-current',index===this.step?'step':'false');button.addEventListener('click',()=>this.go(index));this.nav.append(button);});this.back.disabled=this.step===0;this.next.hidden=this.step===3;}
  go(step){this.step=Math.max(0,Math.min(3,step));this.steps();this.fields();this.remember();}
  visible(f){
    if(f.step!==this.step)return false;
    if(this.settings.representation==='2d'&&['style','height','stem','head','roughness','metallic'].includes(f.key))return false;
    if(this.settings.set==='checkers'&&['style','stem','head'].includes(f.key))return false;
    return true;
  }
  fields(){
    this.controls.replaceChildren(node('h3','',STEPS[this.step]));if(this.step===3){this.saveForm();return;}
    const notes=['Schachfiguren und Damesteine verwenden die vorhandenen gemeinsamen Modelle. Die Conquest-Truppenmarke bleibt vorerst als Original in der Bibliothek.',
      'Gesamtgröße vergrößert die Figur als Ganzes. Die weiteren Regler verändern ihre Proportionen. Der Vorschau-Maßstab bleibt dabei gleich.',
      'Beide Seiten haben unabhängige Farben. Mattheit und Metallwirkung betreffen den ganzen Satz und sind in 3D sichtbar.'];
    this.controls.append(node('p','piece-note',notes[this.step]));
    for(const f of this.config.fields.filter(f=>this.visible(f))){
      const wrap=node('div','piece-editor-field'),label=node('label');label.htmlFor='piece-field-'+f.key;label.textContent=this.settings.representation==='2d'&&f.key==='base'?'Markenbreite':f.label;
      let input;
      if(f.type==='select'){input=node('select');for(const [key,title] of Object.entries(f.options))input.append(new Option(title,key));}
      else{input=node('input');input.type=f.type;}
      input.id=label.htmlFor;if(f.min!==undefined){input.min=f.min;input.max=f.max;input.step=f.increment;}input.value=this.settings[f.key];
      const output=node('output','piece-field-value');const display=()=>f.type==='range'?(f.percent?Math.round(this.settings[f.key]*100):this.settings[f.key])+' %':'';output.textContent=display();output.htmlFor=input.id;
      input.addEventListener(f.type==='select'?'change':'input',()=>{
        this.settings[f.key]=f.type==='range'?Number(input.value):input.value;output.textContent=display();this.changed();
        if(f.type==='select'){this.fields();this.views();}
      });
      wrap.append(label,input);if(f.type==='range'){
        wrap.append(output);const exact=node('details','piece-exact'),summary=node('summary','','Genau einstellen'),number=node('input');number.type='number';const factor=f.percent?100:1;
        number.min=f.min*factor;number.max=f.max*factor;number.step=f.increment*factor;number.value=this.settings[f.key]*factor;number.setAttribute('aria-label',label.textContent+' · genauer Prozentwert');
        number.addEventListener('input',()=>{if(!number.value||!number.checkValidity())return;input.value=Number(number.value)/factor;input.dispatchEvent(new Event('input'));});input.addEventListener('input',()=>{number.value=Math.round(Number(input.value)*factor*1000)/1000;});exact.append(summary,number);wrap.append(exact);
      }
      this.controls.append(wrap);
    }
    if(this.settings.representation==='2d'&&this.step===1)this.controls.append(node('p','piece-note','Flache Marken haben keine Körperhöhe oder Kopfproportionen. Hier gestaltest du ihre Gesamtgröße und Breite.'));
  }
  saveForm(){
    const form=node('form','piece-save'),label=node('label','','Name deines Figurensatzes'),name=node('input');name.id='piece-design-name';name.required=true;name.maxLength=100;name.value=this.name;label.htmlFor=name.id;
    name.addEventListener('input',()=>{this.name=name.value;this.savedId=null;this.state();this.remember();});
    const save=node('button','primary','In Bibliothek speichern');save.type='submit';
    form.addEventListener('submit',async event=>{
      event.preventDefault();save.disabled=true;const fingerprint=this.fingerprint();
      try{
        const result=await api('/api/piece-designs',{name:this.name,settings:copy(this.settings),parent_id:this.parentId});const same=fingerprint===this.fingerprint();
        if(same){this.savedId=result.asset.id;this.parentId=result.asset.id;this.clean=fingerprint;this.url(this.savedId);try{sessionStorage.removeItem('piece-editor-draft');}catch{}}
        await this.callbacks.onSaved(result.asset,same);this.state();this.message.textContent=same?'„'+result.asset.name+'“ ist in deiner Bibliothek gespeichert.':'Der Stand ist gespeichert. Neuere Änderungen sind noch offen.';
      }catch(error){this.message.textContent=error.message;}finally{save.disabled=false;}
    });
    const library=node('a','','Meine Figurensätze ansehen →');library.href='#library/pieces';form.append(label,name,save,node('p','piece-note','Speichert die ganze Formfamilie mit Größe, Proportionen, Material und beiden Farben. Frühere Stände bleiben erhalten.'),library,node('p','piece-note','Speichern ersetzt noch keine Figuren in einem vorhandenen Spiel.'));this.controls.append(form);
  }
  changed(){this.savedId=null;this.message.textContent='';this.state();this.remember();this.previewSoon();}
  state(){const saved=this.savedId&&this.fingerprint()===this.clean;this.savedState.textContent=saved?'Gespeichert':'Noch nicht gespeichert';this.callbacks.onChange(saved?this.savedId:null);this.summary.textContent=(this.settings.set==='chess'?'Schachfiguren':'Damesteine')+' · '+this.settings.representation.toUpperCase()+' · Änderungen gelten für den ganzen Satz';}
  remember(){try{sessionStorage.setItem('piece-editor-draft',JSON.stringify({parentId:this.parentId,name:this.name,settings:this.settings,step:this.step}));}catch{this.message.textContent='Die Zwischenablage ist voll. Bitte speichere deinen Entwurf ausdrücklich.';}}
  previewSoon(){clearTimeout(this.timer);const revision=++this.revision;this.timer=setTimeout(async()=>{try{const result=await api('/api/piece-designs/preview',{settings:copy(this.settings),view:copy(this.view)});if(revision===this.revision)this.frame.srcdoc=result.html;}catch(error){if(revision===this.revision)this.message.textContent=error.message;}},100);}
  url(id){const url=new URL(location.href);url.searchParams.delete('review');if(id)url.searchParams.set('piece',id);else url.searchParams.delete('piece');history.replaceState(null,'',url.pathname+url.search+url.hash);}
  newSet(){this.settings=copy(this.config.defaults);this.name='Mein Figurensatz';this.parentId=null;this.savedId=null;this.clean='';this.step=0;this.url(null);this.steps();this.fields();this.views();this.changed();}
  load(asset){
    if(asset.component==='piece-design-v1'){this.settings=copy(asset.snapshot.settings);this.name=asset.name;this.savedId=asset.id;this.parentId=asset.id;this.clean=this.fingerprint();}
    else{
      const old=asset.component==='game-pieces-v1'?asset.snapshot.settings.figure:asset.snapshot.settings;if(!old)throw Error('Die Conquest-Marke bleibt vorerst als Original in der Bibliothek.');
      this.settings={...copy(this.config.defaults),...copy(old),representation:asset.representation};delete this.settings.arrangement;
      this.name=asset.name+' · Mein Entwurf';this.savedId=null;this.parentId=null;this.clean='';
    }
  }
  async openAsset(asset){await this.ready;if(!this.config||!this.frame)return;this.load(asset);this.url(this.savedId);this.step=0;this.steps();this.fields();this.views();this.state();this.previewSoon();this.remember();}
}
