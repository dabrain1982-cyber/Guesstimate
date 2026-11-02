// Read the actual component in an isolated, script-free frame. Only edit a copy.
export const isSourceRecipe=recipe=>recipe?.schema_version===3&&!!recipe.source_button;
export function settleSourceMotion(doc){
  // Compare/capture the same instant in isolated previews. Keep the original
  // animation definitions; never change a game stylesheet or live document.
  for(const animation of doc.getAnimations()){
    const timing=animation.effect?.getComputedTiming();
    try{if(Number.isFinite(timing?.endTime))animation.finish();else{animation.pause();animation.currentTime=0;}}catch{}
  }
}
export function partElement(root,key){let el=root;for(const index of key.split('::')[0].split('.').slice(1))el=el?.children[Number(index)];return el;}
export function sourceParts(root){
  const parts=[{key:'root',element:root,name:'Ganzer Button'}];
  function visit(el,key){
    for(const [i,child] of [...el.children].entries()){
      const path=key+'.'+i;if(['SCRIPT','STYLE'].includes(child.tagName))continue;
      const name=child.tagName.toLowerCase(),text=(child.textContent||'').trim().replace(/\s+/g,' ').slice(0,32);
      parts.push({key:path,element:child,name:({svg:'Symbol',img:'Bild',span:'Beschriftung / Fläche',strong:'Hervorhebung',small:'Zusatztext'}[name]||name)+(text?' · '+text:'')});
      if(name!=='svg'&&parts.length<55)visit(child,path);
    }
  }
  visit(root,'root');
  for(const part of [...parts])for(const pseudo of ['before','after']){
    const style=root.ownerDocument.defaultView.getComputedStyle(part.element,'::'+pseudo);
    if(style.content&&!['none','normal'].includes(style.content))parts.push({...part,key:part.key+'::'+pseudo,name:part.name+' · '+(pseudo==='before'?'vordere':'hintere')+' Zusatzfläche'});
  }
  return parts.slice(0,64);
}
function copyStateRules(doc){
  const output=[];
  function walk(rules){let css='';for(const rule of rules){
    if(rule.selectorText&&/:(hover|active|focus|focus-visible)/.test(rule.selectorText))css+=rule.selectorText.replace(/:focus-visible|:focus|:hover|:active/g,p=>'[data-workshop-state~="'+p.slice(1)+'"]')+'{'+rule.style.cssText+'}';
    else if(rule.cssRules){const inner=walk(rule.cssRules);if(inner)css+=rule.cssText.slice(0,rule.cssText.indexOf('{')).trim()+'{'+inner+'}';}
  }return css;}
  for(const sheet of doc.styleSheets)try{output.push(walk(sheet.cssRules));}catch{}
  const style=doc.createElement('style');style.textContent=output.join('\n');doc.head.append(style);
}
export function applySourceAppearance(root,recipe){
  const doc=root.ownerDocument;doc.getElementById('workshop-part-overrides')?.remove();
  // Restore from captured inline styles/text before every update, including undo/reset.
  for(const el of [root,...root.querySelectorAll('*')]){
    if(!el.__workshopOriginal)el.__workshopOriginal={style:el.getAttribute('style'),text:[...el.childNodes].filter(n=>n.nodeType===3).map(n=>[n,n.nodeValue])};
    const saved=el.__workshopOriginal;if(saved.style===null)el.removeAttribute('style');else el.setAttribute('style',saved.style);
    for(const [node,text]of saved.text)node.nodeValue=text;
  }
  const style=doc.createElement('style');style.id='workshop-part-overrides';doc.head.append(style);
  for(const [key,change]of Object.entries(recipe.appearance||{})){
    const el=partElement(root,key);if(!el)continue;
    let declaration=el.style;
    if(key.includes('::')){el.dataset.workshopPart=key.split('::')[0];const index=style.sheet.insertRule('[data-workshop-part="'+key.split('::')[0]+'"]::'+key.split('::')[1]+'{}');declaration=style.sheet.cssRules[index].style;}
    for(const [property,value]of Object.entries(change.style||{}))declaration.setProperty(property,value,'important');
    if(typeof change.text==='string'){
      const nodes=el.__workshopOriginal.text.filter(([,text])=>text.trim());
      if(nodes.length){nodes[0][0].nodeValue=change.text;for(const [node]of nodes.slice(1))node.nodeValue='';}
    }
  }
}
export function renderSourceButton(host,recipe,{onReady,state='original'}={}){
  const frame=document.createElement('iframe');frame.title=recipe.source_button.name+' · Entwurf';
  frame.setAttribute('sandbox','allow-same-origin');frame.setAttribute('scrolling','no');
  frame.style.cssText='border:0;width:1000px;height:600px;position:absolute;left:0;top:0;transform-origin:top left;';
  const stage=document.createElement('div');stage.className='source-button-stage';stage.style.cssText='position:relative;width:100%;overflow:hidden;min-height:90px;';stage.append(frame);host.replaceChildren(stage);
  let root,canvasWidth=520,canvasHeight=180;
  const fit=()=>{const width=host.getBoundingClientRect().width;if(width<=0)return;const scale=Math.min(1,width/canvasWidth);frame.style.transform='scale('+scale+')';stage.style.height=Math.ceil(canvasHeight*scale)+'px';};
  const update=(value=recipe)=>{recipe=value;if(root){applySourceAppearance(root,recipe);const r=root.getBoundingClientRect();canvasWidth=Math.max(520,r.width+90);canvasHeight=Math.max(180,r.height+36);const doc=frame.contentDocument;for(const el of [doc.body,doc.documentElement]){el.style.setProperty('width',canvasWidth+'px','important');el.style.setProperty('height',canvasHeight+'px','important');}doc.getElementById('source-stage').style.width=(canvasWidth-90)+'px';doc.getElementById('source-stage').style.height=(canvasHeight-36)+'px';frame.style.height=Math.max(600,canvasHeight)+'px';frame.style.width=Math.max(1000,canvasWidth)+'px';fit();}};
  const setState=value=>{if(!root)return;root.dataset.workshopState=value==='hover'?'hover':value==='active'?'hover active':value==='focus'?'focus focus-visible':'';if('disabled'in root)root.disabled=value==='disabled'||value==='original'&&root.__sourceDisabled;};
  frame.addEventListener('load',async()=>{
    if(!stage.isConnected)return;
    try{
      const doc=frame.contentDocument;root=doc.querySelector('#source-context button,#source-context a,#source-context input');
      if(!root)throw Error('Die Originalquelle ist nicht mehr verfügbar. Bitte den aktuellen Bibliothekseintrag öffnen.');
      await doc.fonts.ready;settleSourceMotion(doc);root.__sourceDisabled=root.disabled;copyStateRules(doc);update();setState(state);onReady?.({root,frame,parts:sourceParts(root),update,setState});
    }catch(error){stage.replaceChildren(Object.assign(document.createElement('p'),{textContent:error.message}));}
  });
  frame.src='/api/game-buttons/'+encodeURIComponent(recipe.source_button.id)+'/preview';
  const observer=new ResizeObserver(()=>{if(!host.isConnected||!stage.isConnected){observer.disconnect();return;}fit();});observer.observe(host);fit();
  return {element:frame,update,setState};
}
