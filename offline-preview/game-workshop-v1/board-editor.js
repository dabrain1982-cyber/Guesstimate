const clone=value=>JSON.parse(JSON.stringify(value));
const el=(tag,className,text)=>{const n=document.createElement(tag);if(className)n.className=className;if(text!==undefined)n.textContent=text;return n;};
const STEPS=['Form & Größe','Oberfläche & Bild','Felder','Speichern'];
async function request(path,payload){
  const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),10000);
  try{
    const response=await fetch(path,{signal:controller.signal,...(payload===undefined?{}:{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)})});
    const value=await response.json();if(!response.ok)throw Error(value.error||'Die Aktion hat nicht geklappt.');return value;
  }catch(e){if(e.name==='AbortError')throw Error('Die Werkstatt antwortet gerade nicht. Deine Eingaben bleiben erhalten.');throw e;}
  finally{clearTimeout(timer);}
}

export class BoardEditor {
  constructor(host,callbacks){
    this.host=host;this.callbacks=callbacks;this.step=0;this.parentId=null;this.savedId=null;this.revision=0;
    this.host.classList.add('board-workshop');this.host.textContent='Dein Brett wird vorbereitet …';
    this.ready=this.start();
  }
  fingerprint(){return JSON.stringify({name:this.name,settings:this.settings});}
  async start(){
    try{
      this.config=await request('/api/board-designs');this.settings=clone(this.config.defaults);this.name='Mein Brett';this.clean='';
      this.view={fit:false,comparison:true,scale:100};
      const id=new URLSearchParams(location.search).get('board');
      if(id){const asset=this.callbacks.getData().assets.find(a=>a.kind==='board'&&a.id===id);if(!asset)throw Error('Der angeforderte Brettentwurf wurde nicht gefunden.');this.loadAsset(asset);}
      let resumed=false;
      try{
        const draft=JSON.parse(sessionStorage.getItem('board-editor-draft'));
        if(draft?.parentId===this.parentId&&draft.settings&&Object.keys(this.config.defaults).every(k=>k in draft.settings)&&JSON.stringify({name:draft.name,settings:draft.settings})!==this.clean){
          this.settings=draft.settings;this.name=draft.name;this.step=Number.isInteger(draft.step)&&draft.step>=0&&draft.step<4?draft.step:0;this.savedId=null;resumed=true;
        }
      }catch{}
      this.build();this.renderFields();this.renderSteps();this.queuePreview();this.state();
      if(resumed)this.message.textContent='Dein ungespeicherter Entwurf wurde wieder aufgenommen.';
    }catch(error){
      this.host.replaceChildren(el('p','error',error.message));const retry=el('button','','Erneut laden');retry.addEventListener('click',()=>{this.ready=this.start();});this.host.append(retry);
    }
  }
  build(){
    const css=el('link');css.rel='stylesheet';css.href='/board-editor.css';this.host.replaceChildren(css);
    const heading=el('div','board-heading'),intro=el('div');intro.append(el('h3','','Dein eigenes Brett'),el('p','board-note','Erst die Form, dann die Fläche und bei Bedarf Felder. Du kannst jeden Schritt jederzeit wieder öffnen.'));
    const fresh=el('button','','Neues Brett beginnen');fresh.type='button';fresh.addEventListener('click',()=>this.newBoard());heading.append(intro,fresh);
    this.steps=el('nav','board-steps');this.steps.setAttribute('aria-label','Brett gestalten');
    const grid=el('div','board-editor-grid');this.properties=el('section','board-properties');this.properties.setAttribute('aria-label','Bretteinstellungen');
    const preview=el('section','board-preview-column');const top=el('div','board-preview-heading');top.append(el('h3','','Dein Brett'));this.saveState=el('span','board-save-state');top.append(this.saveState);
    this.frame=el('iframe');this.frame.title='Vorschau deines Bretts';this.frame.setAttribute('sandbox','allow-scripts allow-same-origin');
    const stage=el('div','board-preview-stage');stage.append(this.frame);
    const tools=el('div','board-comparison-tools');
    for(const [key,title] of [['comparison','Karte und Figur zum Größenvergleich'],['fit','Ganzes Brett einpassen']]){
      const label=el('label');const input=el('input');input.type='checkbox';input.checked=this.view[key];input.addEventListener('change',()=>{this.view[key]=input.checked;this.queuePreview();});label.append(input,document.createTextNode(title));tools.append(label);
    }
    const zoomLabel=el('label','board-preview-zoom','Ansicht näher / weiter');const zoom=el('input');zoom.type='range';zoom.min=50;zoom.max=150;zoom.step=5;zoom.value=this.view.scale;zoom.setAttribute('aria-label','Ansicht näher / weiter');zoom.addEventListener('input',()=>{this.view.scale=Number(zoom.value);this.queuePreview();});zoomLabel.append(zoom);tools.append(zoomLabel);
    this.summary=el('p','board-note');preview.append(top,tools,stage,this.summary,el('p','board-note','Der Maßstab bleibt beim Ändern der Brettgröße gleich. Karte und Figur sind nur Vergleichshilfen und werden nicht mitgespeichert. „Ganzes Brett einpassen“ passt die Ansicht automatisch an.'));
    grid.append(this.properties,preview);
    this.message=el('p','board-message');this.message.setAttribute('role','status');this.message.setAttribute('aria-live','polite');
    const navigation=el('div','board-navigation');this.back=el('button','','← Zurück');this.next=el('button','primary','Weiter →');
    this.back.addEventListener('click',()=>this.setStep(this.step-1));this.next.addEventListener('click',()=>this.setStep(this.step+1));navigation.append(this.back,this.next);
    this.host.append(heading,this.steps,grid,this.message,navigation);
  }
  setStep(step){this.step=Math.max(0,Math.min(3,step));this.renderSteps();this.renderFields();this.remember();}
  renderSteps(){
    this.steps.replaceChildren();STEPS.forEach((label,index)=>{const button=el('button','',''+(index+1)+' · '+label);button.type='button';button.setAttribute('aria-current',index===this.step?'step':'false');button.addEventListener('click',()=>this.setStep(index));this.steps.append(button);});
    this.back.disabled=this.step===0;this.next.hidden=this.step===3;
  }
  fieldVisible(field){
    const s=this.settings;
    if(field.key==='height'&&s.shape==='round')return false;
    if(['thickness','finish'].includes(field.key)&&s.representation==='2d')return false;
    if(field.key==='image_fit'&&!s.image_id)return false;
    if(['columns','rows','secondary','pattern_opacity'].includes(field.key)&&s.pattern==='none')return false;
    return field.step===this.step;
  }
  renderFields(){
    this.properties.replaceChildren(el('h3','',STEPS[this.step]));
    if(this.step===3){this.renderSave();return;}
    if(this.step===0)this.properties.append(el('p','board-note','Die Maße beziehen sich auf die Spielfläche. Der Rahmen kommt außen hinzu. Bei einem runden Brett stellst du den Durchmesser ein.'));
    if(this.step===1)this.properties.append(el('p','board-note','Die Farbe bleibt unabhängig vom Bild. Sie ist auch in freien Bildrändern sichtbar. Glanz siehst du in der räumlichen Ansicht.'));
    if(this.step===2)this.properties.append(el('p','board-note','Felder sind freiwillig. Ein Gitter ist eine Gestaltungshilfe; Spielregeln und Bewegungsziele legen wir später im Spiel fest.'));
    for(const field of this.config.fields.filter(f=>this.fieldVisible(f))){
      const wrap=el('div','board-field'),label=el('label');label.htmlFor='board-field-'+field.key;
      label.textContent=field.key==='width'&&this.settings.shape==='round'?'Durchmesser der Spielfläche':field.label;
      let input;
      if(field.type==='select'||field.type==='image'){
        input=el('select');const options=field.type==='image'?[["",'Kein Bild · Flächenfarbe'],...this.config.images.map(a=>[a.id,a.name])]:Object.entries(field.options);
        for(const [value,name] of options)input.append(new Option(name,value));
      }else{input=el('input');input.type=['width','height'].includes(field.key)?'range':field.type;}
      input.id=label.htmlFor;
      if(field.min!==undefined){input.min=field.min;input.max=field.max;input.step=field.increment;}
      input.value=this.settings[field.key]??'';
      const output=el('output','board-field-value',field.unit!==undefined?this.settings[field.key]+' '+field.unit:'');output.htmlFor=input.id;
      input.addEventListener(field.type==='select'||field.type==='image'?'change':'input',()=>{
        if(['number','range'].includes(field.type)&&(!input.value||!input.checkValidity()))return;
        this.settings[field.key]=field.type==='image'?(input.value||null):['number','range'].includes(field.type)?Number(input.value):input.value;
        if(this.settings.shape==='round'&&['width','shape'].includes(field.key))this.settings.height=this.settings.width;
        output.textContent=field.unit!==undefined?this.settings[field.key]+' '+field.unit:'';
        this.changed();if(['select','image'].includes(field.type))this.renderFields();
      });
      wrap.append(label,input);if(field.unit!==undefined)wrap.append(output);
      if(['width','height','border','thickness'].includes(field.key)){
        const exact=el('details','board-exact'),summary=el('summary','','Genau einstellen');const number=el('input');number.type='number';number.min=field.min;number.max=field.max;number.step=field.increment;number.value=this.settings[field.key];number.setAttribute('aria-label',label.textContent+' · genauer Wert in cm');
        number.addEventListener('input',()=>{if(!number.value||!number.checkValidity())return;input.value=number.value;input.dispatchEvent(new Event('input'));});
        input.addEventListener('input',()=>{number.value=input.value;});exact.append(summary,number);wrap.append(exact);
      }
      this.properties.append(wrap);
    }
    if(this.step===1){
      const label=el('label','board-upload','Eigenes Brettbild hinzufügen');const upload=el('input');upload.type='file';upload.accept='image/png,image/jpeg,image/webp';upload.setAttribute('aria-label','Eigenes Brettbild hinzufügen');
      upload.addEventListener('change',()=>this.importImage(upload));label.append(upload);this.properties.append(label,el('p','board-note','PNG, JPEG oder WebP vom PC. Das Bild wird als eigenes Original in der Bildbibliothek gespeichert.'));
    }
    if(this.settings.image_id&&this.settings.pattern==='checker'&&this.settings.pattern_opacity===100)
      this.properties.append(el('p','board-hint','Das zweifarbige Feldmuster liegt über dem Bild. Unter Felder kannst du seine Deckkraft senken, Gitterlinien wählen oder die Felder abschalten.'));
    if(this.step===2&&this.settings.width/this.settings.columns!==this.settings.height/this.settings.rows&&this.settings.pattern!=='none')
      this.properties.append(el('p','board-note','Mit diesen Maßen und Feldzahlen sind die Felder rechteckig.'));
  }
  renderSave(){
    const form=el('form','board-save');const label=el('label','','Name deines Bretts');label.htmlFor='board-name';const name=el('input');name.id=label.htmlFor;name.maxLength=100;name.required=true;name.value=this.name;
    name.addEventListener('input',()=>{this.name=name.value;this.savedId=null;this.state();this.remember();});
    const save=el('button','primary','In Bibliothek speichern');save.type='submit';
    form.addEventListener('submit',async event=>{
      event.preventDefault();save.disabled=true;const fingerprint=this.fingerprint(),parent=this.parentId;
      try{
        const result=await request('/api/board-designs',{name:this.name,settings:clone(this.settings),parent_id:parent});
        const same=fingerprint===this.fingerprint();
        if(same){this.savedId=result.asset.id;this.parentId=result.asset.id;this.clean=fingerprint;this.url(result.asset.id);try{sessionStorage.removeItem('board-editor-draft');}catch{}}
        await this.callbacks.onSaved(result.asset,same);this.state();this.message.textContent=same?'„'+result.asset.name+'“ ist in deiner Bibliothek gespeichert.':'Der Stand ist gespeichert. Deine neueren Änderungen sind noch offen.';
      }catch(error){this.message.textContent=error.message;}finally{save.disabled=false;}
    });
    form.append(label,name,save,el('p','board-note','Speichert Form, Maße, Oberfläche, Bild und Felder zusammen. Frühere Stände bleiben erhalten.'));
    const library=el('a','','Meine Bretter ansehen →');library.href='#library/board';form.append(library,el('p','board-note','Ein gespeicherter Entwurf ersetzt noch kein Brett in einem vorhandenen Spiel.'));
    this.properties.append(form);
  }
  state(){
    const same=this.savedId&&this.fingerprint()===this.clean;this.saveState.textContent=same?'Gespeichert':'Noch nicht gespeichert';this.callbacks.onChange(same?this.savedId:null);
    const s=this.settings,dimensions=s.shape==='round'?'Ø '+s.width+' cm':s.width+' × '+s.height+' cm';
    this.summary.textContent=s.representation.toUpperCase()+' · '+dimensions+' Spielfläche · '+s.border+' cm Rahmen'+(s.pattern!=='none'?' · '+s.columns+' × '+s.rows+' Felder':' · ohne Felder');
  }
  changed(){this.savedId=null;this.message.textContent='';this.state();this.remember();this.queuePreview();}
  remember(){try{sessionStorage.setItem('board-editor-draft',JSON.stringify({parentId:this.parentId,name:this.name,settings:this.settings,step:this.step}));}catch{this.message.textContent='Die Zwischenablage ist voll. Bitte speichere deinen Entwurf ausdrücklich.';}}
  queuePreview(){clearTimeout(this.timer);const revision=++this.revision;this.timer=setTimeout(()=>this.preview(revision),100);}
  async preview(revision){
    try{const result=await request('/api/board-designs/preview',{settings:clone(this.settings),view:clone(this.view)});if(revision===this.revision)this.frame.srcdoc=result.html;}
    catch(error){if(revision===this.revision)this.message.textContent=error.message;}
  }
  async importImage(input){
    const file=input.files[0];if(!file)return;input.disabled=true;
    try{
      if(file.size>20*1024*1024)throw Error('Bitte ein Bild mit höchstens 20 MB wählen.');
      const response=await fetch('/api/images/import',{method:'POST',headers:{'X-Filename':encodeURIComponent(file.name),'X-Image-Kind':'background'},body:file});
      const result=await response.json();if(!response.ok)throw Error(result.error||'Das Bild konnte nicht hinzugefügt werden.');
      this.config=await request('/api/board-designs');this.settings.image_id=result.asset.id;this.changed();this.renderFields();await this.callbacks.onImported();
      this.message.textContent='Dein Bild ist gespeichert und für dieses Brett ausgewählt.';
    }catch(error){this.message.textContent=error.message;}finally{input.disabled=false;}
  }
  url(id){const url=new URL(location.href);url.searchParams.delete('review');if(id)url.searchParams.set('board',id);else url.searchParams.delete('board');history.replaceState(null,'',url.pathname+url.search+url.hash);}
  newBoard(){this.parentId=null;this.savedId=null;this.settings=clone(this.config.defaults);this.name='Mein Brett';this.clean='';this.url(null);this.step=0;this.renderSteps();this.renderFields();this.changed();}
  loadAsset(asset){
    if(asset.component==='board-design-v1'){
      this.settings=clone(asset.snapshot.settings);this.name=asset.name;this.parentId=asset.id;this.savedId=asset.id;this.clean=this.fingerprint();
    }else{
      const old=asset.component==='game-board-v1'?asset.snapshot.settings.grid:asset.snapshot.settings;
      if(!old)throw Error('Diese Originalfläche bleibt vorerst in der Bibliothek. Beginne ein eigenes Brett im Editor.');
      this.settings={...clone(this.config.defaults),representation:asset.representation,width:old.square*old.columns*10,height:old.square*old.rows*10,
        border:old.border*10,thickness:Math.round(old.thickness*100)/10,pattern:old.pattern,columns:old.columns,rows:old.rows,surface:old.light,secondary:old.dark,frame:old.frame};
      this.name=asset.name+' · Mein Entwurf';this.parentId=null;this.savedId=null;this.clean='';
    }
  }
  async openAsset(asset){await this.ready;if(!this.config||!this.frame)return;this.loadAsset(asset);this.url(this.savedId);this.step=0;this.renderSteps();this.renderFields();this.state();this.queuePreview();this.remember();}
}
