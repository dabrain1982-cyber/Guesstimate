// One image editor for every raster element type. The server renders both preview and file.
const copy=value=>JSON.parse(JSON.stringify(value));
const clamp=(v,min,max)=>Math.max(min,Math.min(max,v));
export class ImageEditor {
  constructor(host,{getData,onChange,onImported,onSaved,message,idPrefix='',cropOnly=false,fixedRatio=null,outputWidth=null,initialRecipe=null,onRecipeChange=null,storageKey='image-workshop-drafts-v1',storage=localStorage}) {
    Object.assign(this,{host,getData,onChange,onImported,onSaved,message});
    Object.assign(this,{cropOnly,fixedRatio,outputWidth,initialRecipe,onRecipeChange,storageKey,storage});
    this.kind=null;this.state=null;this.info=null;this.serial=0;this.previewSerial=0;
    try{this.drafts=JSON.parse(storage.getItem(storageKey))||{};}catch{this.drafts={};}
    host.innerHTML=[
      '<div class="image-import-bar"><button id="image-import" type="button">Bild vom PC importieren</button><input id="image-file" type="file" accept="image/png,image/jpeg,image/webp,.png,.jpg,.jpeg,.webp" hidden><label for="image-source">Oder aus der Bibliothek öffnen<select id="image-source"><option value="">Bild auswählen …</option></select></label><small>PNG, JPEG oder WebP · bis 20 MB</small></div>',
      '<p id="image-status" class="image-status" role="status">Wähle ein Bild. Ein Import bewahrt die Originaldatei unverändert auf.</p>',
      '<div id="image-empty" class="image-empty"><span aria-hidden="true">▧</span><h3>Ein Bild, viele Möglichkeiten.</h3><p>Importiere ein eigenes Bild oder öffne ein vorhandenes Motiv. Daraus kannst du Ausschnitte und Größen für unterschiedliche Elemente speichern.</p></div>',
      '<div id="image-workbench" class="image-workbench" hidden><section class="image-crop-panel"><div class="image-panel-heading"><h3>Bildausschnitt wählen</h3><button id="image-reset" type="button">Ganzes Original verwenden</button></div><p class="image-help">Rahmen ziehen oder an den Ecken verändern. Pfeiltasten verschieben den Ausschnitt; mit Umschalt in größeren Schritten.</p>',
      '<div class="image-crop-surface"><div id="image-crop-board" class="image-crop-board" tabindex="0" role="group" aria-label="Bildausschnitt bearbeiten"><img id="image-original" alt="Original mit bearbeitbarem Ausschnitt" draggable="false"><svg id="image-overlay" aria-hidden="true"><defs><mask id="image-crop-mask"><rect id="image-mask-base" fill="white"></rect><rect id="image-mask-hole" fill="black"></rect></mask></defs><rect id="image-shade" fill="#10261d" opacity=".58" mask="url(#image-crop-mask)"></rect><rect id="image-selection" data-action="move" fill="transparent" stroke="#fff9d8" stroke-width="2" vector-effect="non-scaling-stroke"></rect><circle data-corner="nw"></circle><circle data-corner="ne"></circle><circle data-corner="se"></circle><circle data-corner="sw"></circle></svg></div></div>',
      '<p id="image-original-caption" class="image-original-caption"></p></section>',
      '<section class="image-properties"><h3>Deine Bildvariante</h3><div class="image-result checkerboard"><img id="image-result" alt="Ergebnis des gewählten Bildausschnitts" hidden></div><p id="image-result-caption" class="image-help"></p><fieldset id="image-fields"><label>Format des Ausschnitts<select id="image-format"><option value="free">Frei wählen</option><option value="source">Wie das Original</option><option value="16:9">Breit · 16:9</option><option value="4:3">Quer · 4:3</option><option value="1:1">Quadratisch · 1:1</option><option value="2:3">Hoch · 2:3</option></select></label>',
      '<div class="image-number-grid"><label>Links · px<input id="image-x" type="number" min="0" step="1"></label><label>Oben · px<input id="image-y" type="number" min="0" step="1"></label><label>Ausschnittbreite<input id="image-crop-width" type="number" min="1" step="1"></label><label>Ausschnitthöhe<input id="image-crop-height" type="number" min="1" step="1"></label></div>',
      '<div class="image-number-grid image-output-size"><label>Ausgabebreite · px<input id="image-output-width" type="number" min="1" max="4096" step="1"></label><label>Ausgabehöhe · px<input id="image-output-height" type="number" min="1" max="4096" step="1"></label></div><p class="image-help">Breite und Höhe bleiben proportional. Transparente Flächen bleiben transparent.</p>',
      '<label>Speichern unter<select id="image-kind"></select></label><label>Name der Variante<input id="image-name" maxlength="100" placeholder="z. B. Mein Hintergrund · Querformat"></label><button id="image-save" class="primary" type="button">Variante in Bibliothek speichern</button></fieldset></section></div>'
    ].join('');
    const nodes={};for(const element of host.querySelectorAll('[id]')){nodes[element.id]=element;element.id=idPrefix+element.id;}
    for(const label of host.querySelectorAll('label[for]'))label.htmlFor=idPrefix+label.htmlFor;
    for(const element of host.querySelectorAll('[mask]'))element.setAttribute('mask',element.getAttribute('mask').replace('url(#','url(#'+idPrefix));
    this.$=id=>nodes[id];host.classList.toggle('image-crop-only',cropOnly);
    this.$('image-import').addEventListener('click',()=>this.$('image-file').click());
    this.$('image-file').addEventListener('change',event=>{const file=event.target.files[0];event.target.value='';if(file)this.importFile(file);});
    this.$('image-source').addEventListener('change',()=>{const id=this.$('image-source').value;if(id)this.load(id);});
    this.$('image-name').addEventListener('input',()=>{this.state.name=this.$('image-name').value;this.changed(false);});
    this.$('image-kind').addEventListener('change',()=>{this.state.category=this.$('image-kind').value;this.changed(false);});
    this.$('image-format').addEventListener('change',()=>{this.state.format=this.$('image-format').value;this.fitFormat();this.changed();});
    const fields={'image-x':'x','image-y':'y','image-crop-width':'width','image-crop-height':'height'};
    for(const [id,key] of Object.entries(fields))this.$(id).addEventListener('input',()=>{
      const value=this.$(id).value;if(value==='')return;
      this.state.recipe[key]=Math.round(Number(value));this.normalize(key);this.changed();
    });
    this.$('image-output-width').addEventListener('input',()=>this.outputSize('width'));
    this.$('image-output-height').addEventListener('input',()=>this.outputSize('height'));
    this.$('image-reset').addEventListener('click',()=>{if(this.fixedRatio)this.fitFormat();else{Object.assign(this.state.recipe,{x:0,y:0,width:this.info.width,height:this.info.height});this.state.format='free';this.normalize();}this.changed();});
    this.$('image-save').addEventListener('click',()=>this.save());
    const board=this.$('image-crop-board');
    board.addEventListener('pointerdown',event=>this.pointerDown(event));
    board.addEventListener('pointermove',event=>this.pointerMove(event));
    board.addEventListener('pointerup',event=>{this.drag=null;if(board.hasPointerCapture(event.pointerId))board.releasePointerCapture(event.pointerId);});
    board.addEventListener('pointercancel',()=>{this.drag=null;});
    board.addEventListener('keydown',event=>{
      if(!this.state||!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(event.key))return;
      event.preventDefault();const amount=event.shiftKey?10:1,r=this.state.recipe;
      r.x+=event.key==='ArrowLeft'?-amount:event.key==='ArrowRight'?amount:0;r.y+=event.key==='ArrowUp'?-amount:event.key==='ArrowDown'?amount:0;
      this.normalize('move');this.changed();
    });
    new ResizeObserver(()=>this.overlay()).observe(board);
  }
  setData(){const data=this.getData(),current=this.state?.selected_id||this.$('image-source').value;this.$('image-source').replaceChildren(new Option('Bild auswählen …',''));
    for(const asset of data.assets.filter(a=>data.image_kinds.includes(a.kind)&&a.image&&!a.image.toLowerCase().endsWith('.svg'))){
      this.$('image-source').append(new Option(data.kinds[asset.kind].title+' · '+asset.name,asset.id));
    }
    this.$('image-source').value=current;const selected=this.state?.category||this.kind;
    this.$('image-kind').replaceChildren(...data.image_kinds.filter(k=>['image','avatar'].includes(data.kinds[k].editor)).map(k=>new Option(data.kinds[k].title,k)));this.$('image-kind').value=selected;
  }
  setKind(kind){this.setData();if(kind===this.kind)return;this.persist();this.kind=kind;this.state=null;this.info=null;this.serial++;this.previewSerial++;clearTimeout(this.previewTimer);this.previewAbort?.abort();
    this.$('image-workbench').hidden=true;this.$('image-empty').hidden=false;this.$('image-source').value='';
    this.onChange(kind,null);
    const draft=this.drafts[kind];if(draft?.selected_id)this.load(draft.selected_id,copy(draft));
    else this.status('Importiere ein Bild oder öffne ein Motiv aus der Bibliothek.');
  }
  persist(){if(this.kind&&this.state){this.drafts[this.kind]=copy(this.state);try{this.storage.setItem(this.storageKey,JSON.stringify(this.drafts));}catch{this.status('Bitte die Variante ausdrücklich speichern; die Browser-Zwischenablage ist voll.',true);}}}
  status(text,error=false){this.$('image-status').textContent=text;this.$('image-status').classList.toggle('error',error);}
  async request(path,options={},binary=false){const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),20000);try{
    const response=await fetch(path,{...options,signal:controller.signal});
    if(!response.ok){let value={};try{value=await response.json();}catch{}throw Error(value.error||'Die lokale Bildwerkstatt antwortet gerade nicht.');}
    return binary?await response.blob():await response.json();
  }catch(error){if(error.name==='AbortError')throw Error('Die Bildverarbeitung dauert zu lange. Dein Entwurf bleibt erhalten.');throw error;}finally{clearTimeout(timer);}}
  async importFile(file){if(this.importing)return;if(file.size>20*1024*1024){this.status('Bitte ein Bild mit höchstens 20 MB wählen.',true);return;}
    this.importing=true;this.$('image-import').disabled=true;this.status('Original wird auf diesem PC gesichert …');const category=this.kind;
    try{const result=await this.request('/api/images/import',{method:'POST',headers:{'Content-Type':file.type||'application/octet-stream','X-Filename':encodeURIComponent(file.name),'X-Image-Kind':category},body:file});
      await this.onImported(result.asset);this.setData();if(this.kind===category)await this.load(result.asset.id);this.status('Das Original liegt unverändert in der Bibliothek. Du kannst jetzt eine eigene Variante speichern.');
    }catch(error){this.status(error.message,true);}finally{this.importing=false;this.$('image-import').disabled=false;}
  }
  async openAsset(asset){this.kind=asset.kind;this.setData();await this.load(asset.id);}
  async load(id,draft=null){const serial=++this.serial;this.previewAbort?.abort();this.status('Bild wird geöffnet …');this.onChange(this.kind,null);
    try{const info=await this.request('/api/images/source?id='+encodeURIComponent(id));if(serial!==this.serial)return;this.info=info;
      this.state=draft||{selected_id:id,source_id:info.source_id,recipe:copy(info.recipe),name:(info.name.slice(0,85)+(info.role==='variant'?'':' · Variante')),category:this.kind,format:'free',savedId:info.role==='variant'?id:null};
      if(!draft&&info.role!=='variant'&&this.initialRecipe)this.state.recipe=this.initialRecipe(info);
      if(this.fixedRatio)this.state.format='1:1';
      if(this.getData().kinds[this.state.category]?.editor!=='image')this.state.category=this.kind;
      this.state.source_id=info.source_id;this.$('image-original').src=info.image_url;this.$('image-crop-board').style.setProperty('--source-aspect',info.width/info.height);
      this.$('image-overlay').setAttribute('viewBox','0 0 '+info.width+' '+info.height);
      for(const key of ['image-mask-base','image-shade']){this.$(key).setAttribute('width',info.width);this.$(key).setAttribute('height',info.height);}
      this.$('image-workbench').hidden=false;this.$('image-empty').hidden=true;this.$('image-source').value=id;
      this.$('image-original-caption').textContent=info.filename+' · Original '+info.width+' × '+info.height+' px';
      this.normalize();this.controls();this.overlay();this.persist();this.preview();
      this.onChange(this.kind,this.state.savedId);this.onRecipeChange?.(copy(this.state),info);this.status(info.role==='variant'?'Gespeicherte Variante geöffnet. Weitere Änderungen erzeugen einen eigenen Stand.':'Das Original bleibt erhalten. Bestimme Ausschnitt, Größe und Namen deiner Variante.');
    }catch(error){if(serial===this.serial)this.status(error.message,true);}
  }
  ratio(){if(this.fixedRatio)return this.fixedRatio;const f=this.state.format;if(f==='source')return this.info.width/this.info.height;if(f==='free')return null;const values=f.split(':').map(Number);return values[0]/values[1];}
  normalize(changed=null){const r=this.state.recipe,source=this.info;
    r.width=clamp(Math.round(r.width)||1,1,source.width);r.height=clamp(Math.round(r.height)||1,1,source.height);
    if(changed==='move'||changed==='x'||changed==='y'){r.x=clamp(Math.round(r.x)||0,0,source.width-r.width);r.y=clamp(Math.round(r.y)||0,0,source.height-r.height);}
    else {r.x=clamp(Math.round(r.x)||0,0,source.width-1);r.y=clamp(Math.round(r.y)||0,0,source.height-1);r.width=Math.min(r.width,source.width-r.x);r.height=Math.min(r.height,source.height-r.y);}
    const ratio=this.ratio();if(ratio&&changed!=='move'&&changed!=='x'&&changed!=='y'){
      if(changed==='height')r.width=Math.max(1,Math.round(r.height*ratio));else r.height=Math.max(1,Math.round(r.width/ratio));
      if(r.width>source.width-r.x){r.width=source.width-r.x;r.height=Math.max(1,Math.round(r.width/ratio));}
      if(r.height>source.height-r.y){r.height=source.height-r.y;r.width=Math.max(1,Math.round(r.height*ratio));}
    }
    r.output_width=clamp(Math.round(r.output_width)||1,1,Math.max(1,Math.min(4096,Math.floor(4096*r.width/r.height))));
    if(this.outputWidth)r.output_width=this.outputWidth;
  }
  fitFormat(){const ratio=this.ratio();if(!ratio)return;const r=this.state.recipe,w=Math.min(this.info.width,this.info.height*ratio),h=w/ratio;
    Object.assign(r,{width:Math.max(1,Math.round(w)),height:Math.max(1,Math.round(h)),x:Math.max(0,Math.round((this.info.width-w)/2)),y:Math.max(0,Math.round((this.info.height-h)/2))});this.normalize();
  }
  outputSize(axis){if(!this.state)return;const input=this.$('image-output-'+axis);if(!input.value)return;
    const r=this.state.recipe;r.output_width=axis==='width'?Number(input.value):Math.round(Number(input.value)*r.width/r.height);this.normalize('move');this.changed();
  }
  controls(){if(!this.state)return;const r=this.state.recipe;
    for(const [id,key] of Object.entries({'image-x':'x','image-y':'y','image-crop-width':'width','image-crop-height':'height','image-output-width':'output_width'}))this.$(id).value=r[key];
    this.$('image-output-height').value=Math.max(1,Math.round(r.output_width*r.height/r.width));
    this.$('image-format').value=this.state.format;this.$('image-name').value=this.state.name;this.$('image-kind').value=this.state.category;
    this.$('image-result-caption').textContent='Ausgabe: '+r.output_width+' × '+Math.max(1,Math.round(r.output_width*r.height/r.width))+' px · PNG';
  }
  overlay(){if(!this.info||!this.state)return;const r=this.state.recipe,rect=this.$('image-selection'),hole=this.$('image-mask-hole');
    for(const element of [rect,hole])for(const key of ['x','y','width','height'])element.setAttribute(key,r[key]);
    const corners={nw:[r.x,r.y],ne:[r.x+r.width,r.y],se:[r.x+r.width,r.y+r.height],sw:[r.x,r.y+r.height]};
    const cssWidth=this.$('image-crop-board').getBoundingClientRect().width||400;
    for(const c of this.host.querySelectorAll('[data-corner]')){const p=corners[c.dataset.corner];c.setAttribute('cx',p[0]);c.setAttribute('cy',p[1]);c.setAttribute('r',this.info.width/cssWidth*7);}
    this.$('image-crop-board').setAttribute('aria-label','Bildausschnitt: links '+r.x+', oben '+r.y+', '+r.width+' mal '+r.height+' Pixel. Mit Pfeiltasten verschieben.');
  }
  changed(preview=true){this.state.savedId=null;this.onChange(this.kind,null);this.controls();this.overlay();this.persist();this.onRecipeChange?.(copy(this.state),this.info);if(preview){clearTimeout(this.previewTimer);this.previewTimer=setTimeout(()=>this.preview(),180);}this.status('Änderungen noch nicht gespeichert. Das Original bleibt erhalten.');}
  point(event){const box=this.$('image-crop-board').getBoundingClientRect();return {x:clamp((event.clientX-box.left)/box.width*this.info.width,0,this.info.width),y:clamp((event.clientY-box.top)/box.height*this.info.height,0,this.info.height)};}
  pointerDown(event){if(!this.state||event.button!==0)return;event.preventDefault();this.$('image-crop-board').focus();const point=this.point(event),corner=event.target.dataset.corner,r=copy(this.state.recipe);
    this.drag={point,recipe:r,corner,move:event.target.dataset.action==='move'};this.$('image-crop-board').setPointerCapture(event.pointerId);
  }
  pointerMove(event){if(!this.drag)return;event.preventDefault();const p=this.point(event),d=this.drag,r=this.state.recipe;
    if(d.move){r.x=Math.round(d.recipe.x+p.x-d.point.x);r.y=Math.round(d.recipe.y+p.y-d.point.y);this.normalize('move');}
    else {let anchor=d.point;if(d.corner)anchor={x:d.corner.includes('w')?d.recipe.x+d.recipe.width:d.recipe.x,y:d.corner.includes('n')?d.recipe.y+d.recipe.height:d.recipe.y};
      Object.assign(r,{x:Math.round(Math.min(anchor.x,p.x)),y:Math.round(Math.min(anchor.y,p.y)),width:Math.max(1,Math.round(Math.abs(p.x-anchor.x))),height:Math.max(1,Math.round(Math.abs(p.y-anchor.y)))});this.normalize();}
    this.changed();
  }
  async preview(){if(!this.state||this.cropOnly)return;this.previewAbort?.abort();const serial=++this.previewSerial,controller=new AbortController();this.previewAbort=controller;
    const timer=setTimeout(()=>controller.abort(),10000);this.host.dataset.previewReady='false';
    try{const response=await fetch('/api/images/preview',{method:'POST',signal:controller.signal,headers:{'Content-Type':'application/json'},body:JSON.stringify({source_id:this.state.source_id,recipe:this.state.recipe})});
      if(!response.ok){const value=await response.json();throw Error(value.error||'Die Bildvorschau konnte nicht geladen werden.');}
      const blob=await response.blob();if(serial!==this.previewSerial)return;const url=URL.createObjectURL(blob),old=this.previewUrl;this.previewUrl=url;this.$('image-result').src=url;this.$('image-result').hidden=false;this.host.dataset.previewReady='true';if(old)URL.revokeObjectURL(old);
    }catch(error){if(error.name!=='AbortError')this.status(error.message,true);}finally{clearTimeout(timer);}
  }
  async save(){if(!this.state||this.saving)return;this.saving=true;this.$('image-save').disabled=true;this.status('Bildvariante wird auf diesem PC gespeichert …');const submitted=copy(this.state),editedKind=this.kind;
    try{const result=await this.request('/api/images/variants',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({source_id:submitted.source_id,name:submitted.name,kind:submitted.category,recipe:submitted.recipe})});
      const same=JSON.stringify(this.state)===JSON.stringify(submitted)&&this.kind===editedKind;
      if(same){this.state.selected_id=result.asset.id;this.state.savedId=result.asset.id;if(result.asset.kind!==editedKind)delete this.drafts[editedKind];this.drafts[result.asset.kind]=copy(this.state);this.kind=result.asset.kind;this.persist();}
      await this.onSaved(result.asset,same);this.setData();this.status('„'+result.asset.name+'“ ist als eigene Bildvariante gespeichert. Das Original bleibt erhalten.');
    }catch(error){this.status(error.message,true);}finally{this.saving=false;this.$('image-save').disabled=false;}
  }
}
