const node=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
const clone=value=>structuredClone(value);
async function request(path,value){
  const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),8000);
  try{
    const response=await fetch(path,{cache:'no-store',signal:controller.signal,...(value?{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(value)}:{})});
    const data=await response.json();if(!response.ok)throw Error(data.error||'Die Fensterwerkstatt antwortet gerade nicht.');return data;
  }catch(error){throw Error(error.name==='AbortError'?'Die Fensterwerkstatt antwortet gerade nicht. Bitte erneut versuchen.':error.message);}
  finally{clearTimeout(timer);}
}
const rgbToHex=(value,fallback)=>{const rgb=value?.match(/[\d.]+/g);return rgb?.length>=3?'#'+rgb.slice(0,3).map(v=>Math.round(Number(v)).toString(16).padStart(2,'0')).join(''):fallback;};
export class WindowEditor{
  constructor(host,{getData,onChange,onSaved}){
    this.host=host;this.getData=getData;this.onChange=onChange;this.onSaved=onSaved;this.step=0;this.controls=new Map();this.generation=0;
    const css=node('link');css.rel='stylesheet';css.href=new URL('./window-editor.css',import.meta.url);document.head.append(css);
    host.classList.add('window-workshop');
    const intro=node('p','window-note','Beginne mit dem vorhandenen Nachholfenster. Größe skaliert das ganze Fenster mit seinen Bestandteilen. Texte und Buttons stammen aus der Vorlage.');
    this.sourceName=node('p','window-source');this.steps=node('nav','window-steps');this.steps.setAttribute('aria-label','Schritte der Fenstergestaltung');
    for(const [index,label] of ['1 · Form','2 · Farben','3 · Speichern'].entries()){
      const button=node('button','',label);button.type='button';button.addEventListener('click',()=>this.showStep(index));this.steps.append(button);
    }
    const grid=node('div','window-grid');this.properties=node('section','window-properties');this.properties.setAttribute('aria-label','Fenstereinstellungen');
    const column=node('section','window-preview-column'),toolbar=node('div','window-preview-tools');
    const compareLabel=node('label');this.compare=node('input');this.compare.type='checkbox';compareLabel.append(this.compare,document.createTextNode('Original zum Vergleich'));
    this.compare.addEventListener('change',()=>{this.updateControls();this.queuePreview();});
    const backgroundLabel=node('label','','Arbeitsfläche');this.background=node('select');this.background.append(new Option('Hell','light'),new Option('Dunkel','dark'),new Option('Prüfraster','checker'));backgroundLabel.append(this.background);
    this.background.addEventListener('change',()=>{try{localStorage.setItem('window-preview-background',this.background.value);}catch{}this.setBackground();});
    try{this.background.value=localStorage.getItem('window-preview-background')||'light';}catch{}
    if(!this.background.value)this.background.value='light';toolbar.append(compareLabel,backgroundLabel);
    this.stage=node('div','window-preview-stage');this.previewStatus=node('p','window-note');this.previewStatus.setAttribute('role','status');
    this.retry=node('button','','Vorschau erneut laden');this.retry.type='button';this.retry.hidden=true;this.retry.addEventListener('click',()=>this.config?this.queuePreview():this.start());
    this.dirty=node('p','window-save-state');column.append(this.dirty,toolbar,this.stage,this.previewStatus,this.retry,
      node('p','window-note','Die Arbeitsfläche gehört nicht zum Fenster. Die Vorschau verändert keine Spielstände.'));
    grid.append(this.properties,column);this.message=node('p','window-message');this.message.setAttribute('role','status');
    host.append(intro,this.sourceName,this.steps,grid,this.message);
    this.resize=new ResizeObserver(()=>this.sizePreview());this.resize.observe(this.stage);
    this.ready=this.start();
  }
  async start(){
    this.previewStatus.textContent='Fenstervorlage wird geladen …';
    try{
      this.config=await request('/api/window-designs');this.buildControls();
      const savedId=new URLSearchParams(location.search).get('window');
      const asset=savedId?this.getData().assets.find(a=>a.kind==='windows'&&a.id===savedId):null;
      if(savedId&&!asset)throw Error('Der angeforderte Fensterentwurf ist nicht verfügbar. Bitte die Bibliothek öffnen.');
      this.open(asset||this.config.sources[0]);
      try{
        const draft=JSON.parse(sessionStorage.getItem('window-editor-draft')||'null');
        if(draft&&draft.sourceId===this.sourceId&&draft.parentId===this.parentId&&typeof draft.name==='string'&&this.config.fields.every(f=>Object.hasOwn(draft.settings||{},f.key))){
          this.settings=draft.settings;this.recordName=draft.name;this.name.value=draft.name;this.updateControls();this.queuePreview();
          this.message.textContent='Ungespeicherten Fensterentwurf in diesem Tab wieder aufgenommen.';
        }
      }catch{}
    }catch(error){this.message.textContent=error.message;this.previewStatus.textContent='';this.retry.hidden=false;}
  }
  buildControls(){
    for(const spec of this.config.fields){
      const row=node('div','window-field');row.dataset.step=spec.step;
      const label=node('label','',spec.label),input=node('input');input.id='window-'+spec.key;input.type=spec.type;label.htmlFor=input.id;
      if(spec.type==='range'){input.min=spec.min;input.max=spec.max;input.step=spec.increment;}
      const output=node('output');output.htmlFor=input.id;const restore=node('button','window-original','Original');restore.type='button';
      restore.addEventListener('click',()=>{this.settings[spec.key]=this.config.defaults[spec.key];this.changed();});
      input.addEventListener('input',()=>{this.settings[spec.key]=spec.type==='range'?Number(input.value):input.value;this.changed();});
      row.append(label,output,input,restore);this.properties.append(row);this.controls.set(spec.key,{row,input,output,restore,spec});
    }
    this.savePanel=node('section','window-save');this.savePanel.dataset.step=2;
    const label=node('label','','Name deines Fensterentwurfs');this.name=node('input');this.name.type='text';this.name.maxLength=100;this.name.id='window-name';label.htmlFor=this.name.id;
    this.name.addEventListener('input',()=>{this.recordName=this.name.value;this.changed(false);});
    this.save=node('button','primary','Fensterentwurf speichern');this.save.type='button';this.save.addEventListener('click',()=>this.saveDesign());
    const library=node('a','','Eigene Fensterentwürfe öffnen →');library.href='#library/windows';
    this.savePanel.append(label,this.name,this.save,node('p','window-note','Speichert einen eigenen Stand in deiner Bibliothek. Ältere Stände und das Fenster im Spiel bleiben erhalten.'),library);
    this.properties.append(this.savePanel);
  }
  async openAsset(asset){
    await this.ready;if(!this.config)return;
    const url=new URL(location.href);url.searchParams.delete('review');
    if(asset.component==='window-design-v1')url.searchParams.set('window',asset.id);else url.searchParams.delete('window');
    history.replaceState(null,'',url);this.open(asset);
  }
  open(asset){
    if(!asset)throw Error('Keine bearbeitbare Fenstervorlage gefunden.');
    const saved=asset.component==='window-design-v1';
    this.sourceId=saved?asset.snapshot.source_id:asset.id;
    if(!this.config.sources.some(s=>s.id===this.sourceId))throw Error('Für dieses Fenster ist die Bearbeitung noch nicht eingerichtet.');
    this.settings=clone(saved?asset.snapshot.settings:this.config.defaults);this.recordName=saved?asset.name:'Mein Nachholfenster';this.parentId=saved?asset.id:null;
    this.clean=saved?this.fingerprint():'';this.name.value=this.recordName;this.compare.checked=false;this.original=null;
    this.sourceName.textContent='Vorlage: '+this.config.sources.find(s=>s.id===this.sourceId).name;
    this.onChange(saved?asset.id:null);this.updateControls();this.showStep(0);this.queuePreview();
  }
  fingerprint(){return JSON.stringify({source:this.sourceId,name:this.recordName,settings:this.settings});}
  changed(preview=true){
    this.message.textContent='';this.onChange(null);this.updateControls();
    try{sessionStorage.setItem('window-editor-draft',JSON.stringify({sourceId:this.sourceId,parentId:this.parentId,name:this.recordName,settings:this.settings}));}catch{}
    if(preview)this.queuePreview();
  }
  showStep(step){
    this.step=step;for(const [index,button]of [...this.steps.children].entries())button.setAttribute('aria-current',index===step?'step':'false');
    for(const panel of this.properties.children)panel.hidden=Number(panel.dataset.step)!==step;
  }
  updateControls(){
    if(!this.settings)return;
    for(const [key,{input,output,restore,spec}]of this.controls){
      const inherited=this.settings[key]===null||key==='scale'&&this.settings[key]===100;
      const value=this.settings[key]??this.original?.[key];
      input.value=value??(spec.type==='color'?'#000000':0);
      output.textContent=(value===undefined?'Lädt …':value+(spec.unit||''))+(inherited?' · Original':' · Eigener Wert');
      input.disabled=!this.original||this.compare.checked;restore.disabled=inherited||this.compare.checked;
    }
    this.save.disabled=!this.original||!this.recordName.trim()||this.compare.checked;
    this.dirty.textContent=this.fingerprint()===this.clean?'Gespeicherter Stand':'Noch nicht gespeichert';
  }
  queuePreview(){
    const generation=++this.generation;clearTimeout(this.timer);this.timer=setTimeout(()=>this.drawPreview(generation),80);
  }
  async drawPreview(generation){
    this.previewStatus.textContent='Fenstervorschau wird geladen …';this.retry.hidden=true;
    try{
      const result=await request('/api/window-designs/preview',{source_id:this.sourceId,settings:this.compare.checked?this.config.defaults:this.settings});
      if(generation!==this.generation)return;
      const frame=node('iframe');frame.title='Fenstervorschau: Guesstimate-Nachholdialog';frame.setAttribute('sandbox','allow-same-origin');
      frame.style.width=result.width+'px';frame.style.height=result.height+'px';
      frame.addEventListener('load',()=>{
        if(generation!==this.generation)return;
        try{
          const doc=frame.contentDocument,root=doc.querySelector('.workshop-window-root'),sheet=doc.getElementById('window-design-overrides')?.sheet;
          if(!root)throw Error('Die Fenstervorlage konnte nicht dargestellt werden.');
          if(sheet)sheet.disabled=true;
          const css=doc.defaultView.getComputedStyle(root),heading=root.querySelector('.catchup-panel h2'),text=root.querySelector('.catchup-panel>p:not(.eyebrow)');
          this.original={scale:100,radius:Math.round(parseFloat(css.borderTopLeftRadius)),border_width:Math.round(parseFloat(css.borderTopWidth)),
            surface:rgbToHex(css.backgroundColor,'#10142f'),border:rgbToHex(css.borderTopColor,'#d8ff42'),
            heading:rgbToHex(doc.defaultView.getComputedStyle(heading).color,'#e3e7ef'),text:rgbToHex(doc.defaultView.getComputedStyle(text).color,'#aeb7ca')};
          if(sheet)sheet.disabled=false;
          this.setBackground();this.sizePreview();this.updateControls();
          this.previewStatus.textContent=this.compare.checked?'Du siehst das unveränderte Original. Zum Weitergestalten den Vergleich ausschalten.':'Deine Änderungen sind in dieser Vorschau sichtbar. Inhalt und Knöpfe kommen aus der Vorlage.';
        }catch(error){this.previewStatus.textContent=error.message;this.retry.hidden=false;}
      });
      this.frame=frame;this.frameWidth=result.width;this.frameHeight=result.height;frame.srcdoc=result.html;this.stage.replaceChildren(frame);this.sizePreview();
    }catch(error){if(generation===this.generation){this.previewStatus.textContent=error.message;this.retry.hidden=false;}}
  }
  sizePreview(){
    if(!this.frame?.isConnected)return;const box=this.stage.getBoundingClientRect();
    this.frame.style.transform='translate(-50%,-50%) scale('+Math.min(box.width/this.frameWidth,box.height/this.frameHeight)+')';
  }
  setBackground(){
    const doc=this.frame?.contentDocument;if(!doc?.body)return;
    const values={light:'#e4e6e9',dark:'#142439',checker:'repeating-conic-gradient(#d6dbe0 0 25%,#eef0f2 0 50%) 0 / 24px 24px'};
    for(const element of [doc.documentElement,doc.body])element.style.setProperty('background',values[this.background.value]||values.light,'important');
  }
  async saveDesign(){
    this.save.disabled=true;this.message.textContent='Fensterentwurf wird gespeichert …';
    try{
      const fingerprint=this.fingerprint(),result=await request('/api/window-designs',{source_id:this.sourceId,name:this.recordName,settings:this.settings,parent_id:this.parentId});
      this.parentId=result.asset.id;this.clean=fingerprint;
      try{sessionStorage.removeItem('window-editor-draft');}catch{}
      const url=new URL(location.href);url.searchParams.delete('review');url.searchParams.set('window',result.asset.id);history.replaceState(null,'',url);
      await this.onSaved(result.asset,this.fingerprint()===fingerprint);this.updateControls();
      this.message.textContent='Als eigener Fensterentwurf gespeichert. Du findest ihn in der Bibliothek unter Fenster → Meine Entwürfe.';
    }catch(error){this.message.textContent=error.message;this.updateControls();}
  }
}
