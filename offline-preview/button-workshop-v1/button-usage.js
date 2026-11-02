import {renderButton} from './media-renderer.js';
const node=(tag,cls,text)=>{const element=document.createElement(tag);if(cls)element.className=cls;if(text!==undefined)element.textContent=text;return element;};
const date=value=>new Intl.DateTimeFormat('de-DE',{dateStyle:'short',timeStyle:'medium',timeZone:'Europe/Berlin'}).format(new Date(value));
async function request(value){
  const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),6000);
  try{
    let response,payload;
    try{response=await fetch('/api/button-usage',{signal:controller.signal,cache:'no-store',...(value?{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(value)}:{})});payload=await response.json();}
    catch{throw Error('Die lokale Werkstatt antwortet gerade nicht. Bitte öffne die Übersicht erneut.');}
    if(!response.ok)throw Error(payload.error||'Die Zuordnung konnte nicht gelesen werden.');return payload;
  }finally{clearTimeout(timer);}
}
export class ButtonUsageDialog{
  constructor(){
    const link=node('link');link.rel='stylesheet';link.href=new URL('./button-usage.css',import.meta.url);document.head.append(link);
    this.dialog=node('dialog','button-usage-dialog');this.dialog.setAttribute('aria-labelledby','usage-title');
    const header=node('header','usage-header'),title=node('h2','','Verwendungen verwalten');title.id='usage-title';
    const close=node('button','workshop-action','Schließen');close.type='button';close.addEventListener('click',()=>this.dialog.close());header.append(title,close);
    this.name=node('h3');this.version=node('p','usage-help');this.preview=node('div','usage-preview');
    const help=node('p','usage-help','Wähle die Einsatzgruppen für dieses Modell. Gekoppelte Stellen ändern sich gemeinsam. Beschriftung und Spielfunktion bleiben am jeweiligen Einsatzort erhalten.');
    this.active=node('p','usage-active');
    const filters=node('div','usage-filters'),searchLabel=node('label','','Einsatzstellen suchen'),gameLabel=node('label','','Spiel'),scopeLabel=node('label','','Anzeige');
    this.search=node('input');this.search.type='search';this.search.placeholder='Zum Beispiel Startseite oder Shop';searchLabel.append(this.search);
    this.game=node('select');gameLabel.append(this.game);this.scope=node('select');this.scope.append(new Option('Passende & zugeordnete','related'),new Option('Alle Einsatzstellen','all'));scopeLabel.append(this.scope);filters.append(searchLabel,gameLabel,scopeLabel);
    this.search.addEventListener('input',()=>this.renderRows());this.game.addEventListener('change',()=>this.renderRows());this.scope.addEventListener('change',()=>this.renderRows());
    this.rows=node('div','usage-rows');this.summary=node('p','usage-summary');this.message=node('p','usage-message');this.message.setAttribute('role','status');
    const footer=node('footer','usage-footer');this.apply=node('button','workshop-action primary','Zuordnung übernehmen');this.reset=node('button','workshop-action','Original wiederherstellen');
    this.apply.type=this.reset.type='button';this.apply.addEventListener('click',()=>this.commit(this.recipeId));this.reset.addEventListener('click',()=>this.commit(null));
    const runtimeNote=node('p','usage-help','Die Zuordnung gilt für das lokale Hauptspiel. Offene Spielseiten übernehmen sie automatisch; ein geschlossenes Spiel beim nächsten Start.');
    footer.append(this.summary,this.apply,this.reset,this.message,runtimeNote);
    this.dialog.append(header,this.name,this.version,this.preview,help,this.active,filters,this.rows,footer);document.body.append(this.dialog);
    this.context=node('dialog','button-usage-dialog usage-context-dialog');this.context.setAttribute('aria-labelledby','usage-context-title');
    const contextHeader=node('header','usage-header');this.contextTitle=node('h2','','Einsatzort im Spiel');this.contextTitle.id='usage-context-title';
    const back=node('button','workshop-action','Zur Übersicht');back.type='button';back.addEventListener('click',()=>this.context.close());contextHeader.append(this.contextTitle,back);
    this.contextName=node('h3');const stateLabel=node('label','usage-context-state','Spielzustand');this.contextState=node('select');stateLabel.append(this.contextState);
    this.contextState.addEventListener('change',()=>this.loadContext());
    const contextHelp=node('p','usage-help','Originale Spielansicht mit Beispieldaten. Der orange umrandete Knopf ist die gewählte Einsatzstelle.');
    this.contextStage=node('div','usage-context-stage');this.contextStatus=node('p','usage-help');
    const contextFooter=node('footer','usage-footer');this.contextSelection=node('p','usage-summary');this.contextSelect=node('button','workshop-action primary');this.contextSelect.type='button';
    this.contextSelect.addEventListener('click',()=>{const id=this.contextRow.id;if(this.selected.has(id))this.selected.delete(id);else this.selected.add(id);this.renderRows();this.updateContextSelection();});
    contextFooter.append(this.contextSelection,this.contextSelect,node('p','usage-help','Diese Auswahl wird erst mit „Zuordnung übernehmen“ in der Übersicht gespeichert.'));
    this.context.append(contextHeader,this.contextName,stateLabel,contextHelp,this.contextStage,this.contextStatus,contextFooter);document.body.append(this.context);
    this.context.addEventListener('close',()=>this.contextStage.replaceChildren());
    this.contextResize=new ResizeObserver(()=>this.sizeContext());this.contextResize.observe(this.contextStage);
    window.addEventListener('message',event=>{if(event.origin!==location.origin||event.source!==this.contextFrame?.contentWindow||event.data?.channel!=='stormseed-button-context')return;
      this.contextStatus.textContent=event.data.ready?'Du kannst die Spielansicht durch Scrollen ansehen. Spielaktionen sind in dieser Vorschau ausgeschaltet.':'Diese Spielansicht ist gerade nicht verfügbar. Den Grund siehst du im Vorschaufenster.';
      if(!event.data.ready)this.contextSelect.disabled=true;
    });
  }
  async open(identifier,recipe){
    this.recipeId=identifier;this.message.textContent='';this.selected=new Set();this.search.value='';
    this.rows.replaceChildren();this.active.textContent='';this.summary.textContent='';this.version.textContent='';this.preview.replaceChildren();this.name.textContent='Verwendungen werden geladen …';
    this.apply.disabled=this.reset.disabled=this.search.disabled=this.game.disabled=this.scope.disabled=true;
    if(!this.dialog.open)this.dialog.showModal();
    try{
      this.data=await request();this.recipe=this.data.recipes.find(row=>row.id===identifier);
      if(!this.recipe)throw Error('Bitte zuerst einen vollständigen Buttonentwurf speichern.');
      this.name.textContent=this.recipe.name;this.preview.replaceChildren();
      this.version.textContent='Gespeicherter Stand: '+date(this.recipe.created);
      if(recipe)renderButton(this.preview,recipe,{size:16});this.preview.inert=true;
      const active=this.data.models.filter(row=>row.recipe_id===identifier);for(const row of active)this.selected.add(row.id);
      if(!this.selected.size&&this.recipe.source_model&&this.data.models.find(row=>row.id===this.recipe.source_model)?.supported)this.selected.add(this.recipe.source_model);
      this.game.replaceChildren(new Option('Alle Spiele','all'));
      for(const game of [...new Set(this.data.models.flatMap(row=>row.games))].sort())this.game.append(new Option(game,game));
      const preferred=this.data.models.find(row=>row.id===this.recipe.source_model)?.games[0];this.game.value=preferred||'all';
      this.scope.value=this.recipe.source_model?'related':'all';
      this.search.disabled=this.game.disabled=this.scope.disabled=false;this.renderRows();
    }catch(error){this.name.textContent='Verwendungen verwalten';this.rows.replaceChildren();this.message.textContent=error.message;this.apply.disabled=this.reset.disabled=true;if(!this.dialog.open)this.dialog.showModal();}
  }
  renderRows(){
    const query=this.search.value.toLocaleLowerCase('de-DE');this.rows.replaceChildren();
    const source=this.data.models.find(row=>row.id===this.recipe.source_model);
    const models=[...this.data.models].sort((a,b)=>Number(b.id===this.recipe.source_model)-Number(a.id===this.recipe.source_model)||Number(b.recipe_id===this.recipeId)-Number(a.recipe_id===this.recipeId)||Number(b.model_id===source?.model_id)-Number(a.model_id===source?.model_id)||a.name.localeCompare(b.name,'de'));
    for(const row of models){
      if(this.game.value!=='all'&&!row.games.includes(this.game.value))continue;
      const related=row.id===source?.id||row.recipe_id===this.recipeId||this.selected.has(row.id)||row.classes?.some(value=>source?.classes?.includes(value));
      if(this.scope.value==='related'&&!query&&!related)continue;
      if(query&&!JSON.stringify([row.name,row.games,row.uses]).toLocaleLowerCase('de-DE').includes(query))continue;
      const card=node('article','usage-row'+(row.recipe_id===this.recipeId?' is-assigned':'')),label=node('label','usage-selection');
      const input=node('input');input.type='checkbox';input.value=row.id;input.checked=this.selected.has(row.id);input.disabled=!row.supported;
      const text=node('span'),name=node('strong','',row.name),detail=node('small','',row.games.join(', ')+' · '+row.uses.length+(row.uses.length===1?' Einsatzstelle':' Einsatzstellen')+(row.coupled?' · gemeinsam gekoppelt':''));text.append(name,detail);label.append(input,text);
      input.addEventListener('change',()=>{if(input.checked)this.selected.add(row.id);else this.selected.delete(row.id);this.updateSummary();});
      const current=node('p','usage-current','Aktuell zugeordnet: '+row.active_name+(row.active_created?' · '+date(row.active_created):''));card.append(label,current);
      const show=node('button','usage-show-context','Im Spiel ansehen');show.type='button';show.disabled=!row.uses.some(use=>use.context_preview);show.addEventListener('click',()=>this.openContext(row));card.append(show);
      const details=node('details'),summary=node('summary','','Einsatzstellen auflisten'),list=node('ul');
      for(const use of row.uses)list.append(node('li','',use.game+' · '+use.place+' · '+(use.state||use.label)));
      details.append(summary,list);card.append(details);if(!row.supported)card.append(node('p','usage-unavailable',row.reason));this.rows.append(card);
    }
    if(!this.rows.children.length)this.rows.append(node('p','','Keine Einsatzstellen für diesen Filter.'));
    const active=this.data.models.filter(row=>row.recipe_id===this.recipeId);
    this.active.textContent=active.length?'Dieser Entwurf ist '+active.length+' Gruppen mit '+active.reduce((sum,row)=>sum+row.uses.length,0)+' Einsatzstellen zugeordnet.':'Dieser Entwurf ist noch keinem Spielbutton zugeordnet.';
    if(this.data.stale.length)this.active.textContent+=' '+this.data.stale.length+' ältere Zuordnungen benötigen eine erneute Quellenprüfung.';
    this.updateSummary();
  }
  updateSummary(){
    const selected=this.data.models.filter(row=>this.selected.has(row.id));
    this.summary.textContent='Auswahl: '+selected.length+(selected.length===1?' Gruppe':' Gruppen')+' · '+selected.reduce((sum,row)=>sum+row.uses.length,0)+' Einsatzstellen. Änderungen werden erst mit „Zuordnung übernehmen“ angewendet.';
    this.apply.disabled=!selected.length;this.reset.disabled=!selected.some(row=>row.recipe_id);
  }
  openContext(row){
    this.contextRow=row;this.contextName.textContent=row.name;this.contextState.replaceChildren();
    for(const [index,use] of row.uses.entries())if(use.context_preview)this.contextState.append(new Option(use.game+' · '+use.place+' · '+(use.state||use.label),String(index)));
    this.contextState.parentElement.hidden=this.contextState.options.length<2;this.updateContextSelection();
    this.context.showModal();this.loadContext();
  }
  updateContextSelection(){
    const selected=this.selected.has(this.contextRow.id);
    this.contextSelect.textContent=selected?'Gruppe aus Auswahl entfernen':'Diese Gruppe auswählen';
    this.contextSelect.disabled=!this.contextRow.supported;
    this.contextSelection.textContent=(selected?'Ausgewählt':'Noch nicht ausgewählt')+' · '+this.contextRow.uses.length+(this.contextRow.uses.length===1?' Einsatzstelle':' gemeinsam gekoppelte Einsatzstellen');
  }
  loadContext(){
    const use=this.contextRow.uses[Number(this.contextState.value)];this.contextStatus.textContent='Spielansicht wird geladen …';this.updateContextSelection();
    const frame=node('iframe');frame.title='Einsatzort: '+use.game+' · '+use.place+' · '+(use.state||use.label);frame.src=use.context_preview;
    frame.setAttribute('sandbox','allow-scripts allow-same-origin');this.contextFrame=frame;this.contextStage.replaceChildren(frame);this.sizeContext();
  }
  sizeContext(){
    if(!this.contextFrame?.isConnected)return;const box=this.contextStage.getBoundingClientRect();
    this.contextFrame.style.transform='translate(-50%,-50%) scale('+Math.min(box.width/1280,box.height/800)+')';
  }
  async commit(identifier){
    this.apply.disabled=this.reset.disabled=true;this.message.textContent='Zuordnung wird gespeichert …';
    try{
      this.data=await request({revision:this.data.revision,recipe_id:identifier,models:[...this.selected]});
      this.renderRows();this.message.textContent=identifier?'Zuordnung übernommen. Sie gilt für die gewählten Einsatzgruppen im lokalen Hauptspiel.':'Original für die gewählten Einsatzgruppen wiederhergestellt.';
      document.dispatchEvent(new CustomEvent('button-usage-changed'));
    }catch(error){this.message.textContent=error.message;this.updateSummary();}
  }
}
