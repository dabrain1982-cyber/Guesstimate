const __bjGeometry=(()=>{

// Normalized contours: x/y in percent, rounding as a share of adjacent edges.
const cloneContour=value=>structuredClone(value);
const makeContour=(catalog,template)=>({template,points:catalog.contours[template].map(([x,y,round])=>({x,y,round}))});
// The editable drawing plane is also the physical button's face plane.
const CONTOUR_PLANE=Object.freeze({width:560,height:180,x:20,y:24});
const CONTOUR_ASPECT=CONTOUR_PLANE.width/CONTOUR_PLANE.height;
const BUTTON_WIDTH_UNITS=12;
function contourPlane(base=null,settings={}){return {...CONTOUR_PLANE,height:base?560*base.height/base.width*(settings.height_ratio??100)/100:180*(settings.height_ratio??100)/100};}
function buttonMetrics(width,settings,base=null){
  const unit=width/BUTTON_WIDTH_UNITS;
  const scale=base?width/base.width:1;
  return {fontSize:base?base.font_size*scale:unit,height:(base?base.height*scale:width/CONTOUR_ASPECT)*(settings.height_ratio??100)/100,depth:base?settings.depth*scale:unit*settings.depth/16,
    rim:base?settings.edge*scale:unit*settings.edge/20*(settings.style==='comic'?1:settings.style==='natural'?.65:.4)};
}
const cross=(a,b,c)=>(b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x);
function onSegment(a,b,p){return Math.abs(cross(a,b,p))<1e-7&&p.x>=Math.min(a.x,b.x)-1e-7&&p.x<=Math.max(a.x,b.x)+1e-7&&p.y>=Math.min(a.y,b.y)-1e-7&&p.y<=Math.max(a.y,b.y)+1e-7;}
function intersects(a,b,c,d){const x=cross(a,b,c),y=cross(a,b,d),u=cross(c,d,a),v=cross(c,d,b);return (x*y<0&&u*v<0)||onSegment(a,b,c)||onSegment(a,b,d)||onSegment(c,d,a)||onSegment(c,d,b);}
function contourError(points){
  if(!Array.isArray(points)||points.length<3||points.length>32)return 'Eine Kontur braucht 3 bis 32 Randpunkte.';
  if(points.some(p=>!p||!['x','y','round'].every(k=>typeof p[k]==='number'&&Number.isFinite(p[k]))||p.x<0||p.x>100||p.y<0||p.y>100||p.round<0||p.round>50))return 'Die Punkte müssen innerhalb der Fläche bleiben.';
  let area=0;
  for(let i=0;i<points.length;i++){
    const a=points[i],b=points[(i+1)%points.length];area+=a.x*b.y-b.x*a.y;
    if(Math.hypot(a.x-b.x,a.y-b.y)<.5)return 'Zwei Punkte liegen zu dicht beieinander.';
    for(let j=i+1;j<points.length;j++){
      if(j===i+1||(i===0&&j===points.length-1))continue;
      if(intersects(a,b,points[j],points[(j+1)%points.length]))return 'Die Kontur darf sich nicht selbst kreuzen.';
    }
  }
  return Math.abs(area)<20?'Die Kontur braucht eine größere Fläche.':'';
}
function roundedPoints(points,plane=null){
  if(plane){
    const physical=points.map(p=>({...p,x:p.x*plane.width/100,y:p.y*plane.height/100})),result=[];
    physical.forEach((p,i)=>{if(!p.round){result.push(p);return;}const a=physical[(i+physical.length-1)%physical.length],b=physical[(i+1)%physical.length];const la=Math.hypot(a.x-p.x,a.y-p.y),lb=Math.hypot(b.x-p.x,b.y-p.y),u={x:(a.x-p.x)/la,y:(a.y-p.y)/la},v={x:(b.x-p.x)/lb,y:(b.y-p.y)/lb},angle=Math.acos(Math.max(-1,Math.min(1,u.x*v.x+u.y*v.y))),d=Math.min(la,lb)*p.round/100;
      if(angle<.01||Math.PI-angle<.01){result.push(p);return;}const r=d*Math.tan(angle/2),length=Math.hypot(u.x+v.x,u.y+v.y),distance=r/Math.sin(angle/2),center={x:p.x+(u.x+v.x)/length*distance,y:p.y+(u.y+v.y)/length*distance},start=Math.atan2(p.y+u.y*d-center.y,p.x+u.x*d-center.x),end=Math.atan2(p.y+v.y*d-center.y,p.x+v.x*d-center.x);let delta=end-start;while(delta>Math.PI)delta-=2*Math.PI;while(delta< -Math.PI)delta+=2*Math.PI;
      for(let step=0;step<=12;step++){const t=start+delta*step/12;result.push({x:center.x+r*Math.cos(t),y:center.y+r*Math.sin(t)});}
    });return result.map(p=>({x:p.x/plane.width*100,y:p.y/plane.height*100}));
  }
  const result=[];
  points.forEach((p,i)=>{
    if(!p.round){result.push({x:p.x,y:p.y});return;}
    const a=points[(i+points.length-1)%points.length],b=points[(i+1)%points.length];
    const la=Math.hypot(a.x-p.x,a.y-p.y),lb=Math.hypot(b.x-p.x,b.y-p.y),r=Math.min(la,lb)*p.round/100;
    const start={x:p.x+(a.x-p.x)*r/la,y:p.y+(a.y-p.y)*r/la},end={x:p.x+(b.x-p.x)*r/lb,y:p.y+(b.y-p.y)*r/lb};
    for(let step=0;step<=8;step++){const t=step/8,u=1-t;result.push({x:u*u*start.x+2*u*t*p.x+t*t*end.x,y:u*u*start.y+2*u*t*p.y+t*t*end.y});}
  });return result;
}
function toPolygon(points,plane=null){return `polygon(${roundedPoints(points,plane).map(p=>`${p.x.toFixed(3)}% ${p.y.toFixed(3)}%`).join(',')})`;}
function outlinePath(points,plane=null){const dimensions=plane||CONTOUR_PLANE;return roundedPoints(points,plane).map((p,i)=>`${i?'L':'M'} ${dimensions.x+p.x*dimensions.width/100} ${dimensions.y+p.y*dimensions.height/100}`).join(' ')+' Z';}

return {cloneContour,makeContour,CONTOUR_PLANE,CONTOUR_ASPECT,BUTTON_WIDTH_UNITS,contourPlane,buttonMetrics,contourError,roundedPoints,toPolygon,outlinePath};
})();
const __bjComponents=(()=>{

// A single preview button composition, used at every size and in every demo.
const paths = {
  arrow: '<path d="m5 12 13 0m-5-5 5 5-5 5"/>',
  cards: '<path d="M7 4h12v16H7z"/><path d="m5 6-3 1 3 14 3-1M11 8h4m-4 4h4m-4 4h2"/>',
  flag: '<path d="M5 21V3m0 1c5-4 8 4 14 0v10c-6 4-9-4-14 0"/>',
  army: '<path d="m7 8 1-5 4 2 4-2 1 5-2 3v4l3 4H6l3-4v-4zM7 8h10M9 12h6M5 21h14"/>',
  plus: '<path d="M12 4v16M4 12h16"/>',
  sword: '<path d="m4 3 7 2 10 15-3 2L8 9zM9 15l8-5M7 17l3 4M5 20l4-3"/>',
  shield: '<path d="M12 2 3 6v7c1 5 5 8 9 10 4-2 8-5 9-10V6zM7 12l4 4 6-8"/>',
  reset: '<path d="M5 6a8 8 0 1 1-1 11M5 2v6h6"/>',
  play: '<path d="m8 4 12 8-12 8z"/>',
  pause: '<path d="M7 4v16M17 4v16"/>',
  bolt: '<path d="m14 2-10 12h7l-1 9L21 9h-8z"/>',
  keyboard: '<rect x="2" y="5" width="20" height="14" rx="3"/><path d="M6 9h1m4 0h1m4 0h1M6 12h1m4 0h1m4 0h1M7 16h10"/>',
  hand: '<path d="M7 12V5a2 2 0 0 1 4 0v5-6a2 2 0 0 1 4 0v6-3a2 2 0 0 1 4 0v7c0 6-3 8-7 8-3 0-5-2-6-4l-3-4a2 2 0 0 1 3-2l2 2"/>',
  check: '<path d="m4 12 5 5L20 5"/>',
  dice: '<rect x="3" y="3" width="18" height="18" rx="4"/><path d="M8 8h.01M16 8h.01M12 12h.01M8 16h.01M16 16h.01"/>',
};

function icon(name) {
  const holder = document.createElement('span');
  holder.className = 'comic-icon';
  holder.setAttribute('aria-hidden', 'true');
  holder.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round">${paths[name] || paths.arrow}</svg>`;
  return holder;
}

function button({label, variant='primary', symbol, small=false, action, disabled=false, ariaLabel, motion}) {
  const element = document.createElement('button');
  element.type = 'button';
  element.className = `comic-button tone-${variant}${small ? ' size-small' : ''}`;
  element.disabled = disabled;
  if (ariaLabel) element.setAttribute('aria-label', ariaLabel);
  const face = document.createElement('span');
  face.className = 'comic-button-face';
  if (symbol) face.append(icon(symbol));
  const text = document.createElement('span');
  text.className = 'comic-button-label';
  text.textContent = label;
  face.append(text);
  element.append(face);
  let tapAnimation;
  element.addEventListener('click', event => {
    if (element.disabled) return;
    // A quick click can end before :active has visibly travelled. Complete a
    // short down-and-up stroke for actions; selection/toggle buttons stay sunk.
    if (!element.hasAttribute('aria-pressed') && element.getAttribute('role') !== 'tab') {
      const start = getComputedStyle(face).transform;
      const resting = element.matches(':hover') ? 'translateY(-1px)' : 'translateY(0)';
      const pressed = 'translateY(calc(var(--button-depth) - .08em))';
      const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
      const feeling = motion?.() || {};
      tapAnimation?.cancel();
      tapAnimation = face.animate(reduced ? [
        { transform: pressed }, { transform: pressed, offset: .75 }, { transform: resting },
      ] : [
        { transform: start }, { transform: pressed, offset: .28 },
        { transform: pressed, offset: .53 }, { transform: resting },
      ], { duration: reduced ? 120 : (feeling.duration || 300), easing: reduced ? 'steps(1, end)' : (feeling.easing || 'ease-out') });
    }
    action?.(event);
  });
  return { element, label(value) { text.textContent = value; } };
}

function die(value) {
  const element = document.createElement('div');
  element.className = 'comic-die';
  element.setAttribute('aria-hidden', 'true');
  const positions = {1:[5],2:[1,9],3:[1,5,9],4:[1,3,7,9],5:[1,3,5,7,9],6:[1,3,4,6,7,9]}[value];
  for(let index=1;index<=9;index++) {
    const pip = document.createElement('i');
    if (positions.includes(index)) pip.className='is-dot';
    element.append(pip);
  }
  return element;
}

return {icon,button,die};
})();
const __bjRenderer=(()=>{
const {button}=__bjComponents; const {toPolygon,outlinePath,contourPlane,CONTOUR_PLANE,CONTOUR_ASPECT,buttonMetrics,BUTTON_WIDTH_UNITS}=__bjGeometry;

let sourceRenderer=null;
// Workshop-only adapter: existing game consumers keep the same dependencies and behavior.
function registerSourceRenderer(render){sourceRenderer=render;}

const styledDocuments=new WeakSet();
function componentOptions(doc){if(styledDocuments.has(doc))return;styledDocuments.add(doc);const style=doc.createElement('style');style.textContent=`
.preview-button[data-depth-color="manual"]::before{background:var(--own-depth);box-shadow:none;transform:translateX(var(--depth-x,0px))}
.preview-button[data-basis]::before{transform:translateX(var(--depth-x,0px));box-shadow:none}
.preview-button[data-original-surface="true"] .comic-button-face{background:var(--profile-border,transparent)}
.preview-button[data-original-surface="true"] .comic-button-face::before{box-shadow:none;background-position:var(--profile-position,center);background-size:var(--profile-size,cover)}
.preview-button[data-original-surface="true"] .comic-button-face::after{display:none}
.preview-button[data-lettering="plain"] .comic-button-label{font-weight:var(--plain-weight,700);text-shadow:var(--plain-shadow,none);letter-spacing:var(--plain-spacing,normal);text-transform:var(--plain-case,none)}
.preview-button[data-ink-color="manual"] .comic-button-label{color:var(--own-ink);-webkit-text-fill-color:currentColor}
.preview-button .button-picture{position:absolute;inset:0;width:100%;height:100%;object-fit:contain;pointer-events:none}
`;doc.head.append(style);}
const fonts = {fredoka:'var(--font-display)',inter:'var(--font-ui)',mono:'"Courier New", monospace',cinzel:'"Workshop Cinzel", serif',rocksalt:'"Workshop Rock Salt", cursive',kalam:'"Workshop Kalam", cursive',sharetechmono:'"Workshop Share Tech Mono", monospace'};
const feelings = {direct:'ease-out',soft:'cubic-bezier(.25,.1,.25,1)',spring:'cubic-bezier(.2,.8,.35,1.3)'};
const sizing=new WeakMap();
const observedButtons=new Set();
function fitLabel(element){
  const record=sizing.get(element);if(!record||!element.isConnected||!element.getBoundingClientRect().width)return;
  const label=element.querySelector('.comic-button-label'),face=element.querySelector('.comic-button-face');
  const maximum=buttonMetrics(record.width,record.settings,record.base).fontSize*(record.settings.font_scale??100)/100,available=face.getBoundingClientRect().height*(record.base?.9:.72);
  label.style.fontSize=maximum+'px';
  for(let size=maximum;size>maximum*.4&&label.scrollHeight>available;){size*=.94;label.style.fontSize=size+'px';}
}
function fitButton(element,width){
  const record=sizing.get(element);if(!record||width<=0||Math.abs(width-record.width)<.01)return;
  record.width=width;const dimensions=buttonMetrics(width,record.settings,record.base);
  element.style.setProperty('--button-face-font',`${dimensions.fontSize}px`);
  element.style.setProperty('--button-depth',`${dimensions.depth}px`);
  element.style.setProperty('--material-rim',`${dimensions.rim}px`);
  element.style.setProperty('--depth-x',`${(record.settings.depth_x||0)*(record.base?width/record.base.width:width/276)}px`);
  element.style.setProperty('--cast-shadow-y',`${dimensions.fontSize*.2}px`);
  element.style.setProperty('--cast-shadow-blur',`${dimensions.fontSize*.28}px`);
  fitLabel(element);
}
const buttonObserver=typeof ResizeObserver==='function'?new ResizeObserver(entries=>{
  for(const entry of entries){if(!entry.target.isConnected){buttonObserver.unobserve(entry.target);observedButtons.delete(entry.target);continue;}fitButton(entry.target,entry.contentRect.width);}
}):null;

function materialize(element, recipe, {tintStrength=null,textureUrl=null}={}) {
  const s = recipe.settings;
  element.style.removeProperty('--material-image');delete element.dataset.originalSurface;
  if(recipe.base||s.depth_mode==='manual'||s.ink_mode==='manual'||s.lettering==='plain')componentOptions(element.ownerDocument);
  if(recipe.base)element.dataset.basis='true';else delete element.dataset.basis;
  element.dataset.depthColor=s.depth_mode||'auto';element.dataset.inkColor=s.ink_mode||'auto';
  element.style.setProperty('--own-depth',s.depth_color||'#7863df');element.style.setProperty('--own-ink',s.ink_color||'#071124');
  element.dataset.material=s.material;
  element.dataset.finish=s.finish;
  element.dataset.lettering=s.lettering;
  element.dataset.style=s.style;
  if(textureUrl)element.style.setProperty('--texture',`url("${textureUrl}")`);
  element.style.setProperty('--face',s.accent);
  element.style.setProperty('--gradient-end',s.gradient_to||'#d9bc7e');
  element.style.setProperty('--surface-opacity',(s.opacity??30)+'%');
  element.style.setProperty('--cast-shadow-alpha',String((s.shadow??25)/100));
  if(s.material==='translucent'){
    const plane=CONTOUR_PLANE,svg=`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${plane.width} ${plane.height}"><path transform="translate(${-plane.x} ${-plane.y})" d="${outlinePath(recipe.contour.points)}" fill="none" stroke="#202630" stroke-width="${s.edge*2}" stroke-linejoin="round"/></svg>`;
    element.style.setProperty('--surface-outline',`url("data:image/svg+xml,${encodeURIComponent(svg)}")`);
  }
  element.style.setProperty('--face-light',`color-mix(in srgb, ${s.accent}, white 25%)`);
  element.style.setProperty('--face-shade',`color-mix(in srgb, ${s.accent}, black 35%)`);
  const plane=contourPlane(recipe.base,s);
  element.style.setProperty('--button-shape',toPolygon(recipe.contour.points,recipe.base||(s.height_ratio??100)!==100?plane:null));
  element.style.setProperty('--contour-aspect',String(plane.width/plane.height));
  element.style.setProperty('--button-width',`${recipe.base?recipe.base.width/23:BUTTON_WIDTH_UNITS}em`);
  element.style.setProperty('--button-depth',`${s.depth/16}em`);
  element.style.setProperty('--material-rim',`${s.edge/20*(s.style==='comic'?1:s.style==='natural'?.65:.4)}em`);
  const tint=s.style==='minimal'?100:s.style==='comic'?88-s.wear*.12:32-s.wear*.4;
  element.style.setProperty('--tint-strength',`${Math.round(tintStrength??tint)}%`);
  element.style.setProperty('--button-font',fonts[s.font]);
  if(recipe.base){const b=recipe.base;
    if(s.font==='source')element.style.setProperty('--button-font',b.font_family);
    const originalSurface=s.style==='minimal'&&['material','accent','gradient_to','opacity'].every(key=>s[key]===b.initial[key]);element.dataset.originalSurface=String(originalSurface);
    element.style.setProperty('--profile-border',b.border_color);element.style.setProperty('--plain-weight',b.font_weight);element.style.setProperty('--plain-case',b.text_transform);element.style.setProperty('--plain-spacing',b.letter_spacing);element.style.setProperty('--plain-shadow',b.text_shadow);
    element.style.setProperty('--profile-size',b.background_size);element.style.setProperty('--profile-position',b.background_position);
    if(originalSurface){const rgb=b.surface.slice(1).match(/../g).map(v=>parseInt(v,16)),fill=`rgba(${rgb.join(',')},${b.opacity/100})`;element.style.setProperty('--material-image',b.background==='none'?`linear-gradient(${fill},${fill})`:b.background);}
    if(s.shadow===b.initial.shadow&&b.soft_shadow!=='none'){
      const layers=b.soft_shadow.split(/,(?![^()]*\))/).filter(v=>!v.includes('inset')).map(v=>{const c=v.match(/rgba?\([^)]*\)/)?.[0],n=v.replace(c||'','').match(/-?[\d.]+px/g)||[];return c&&n.length>=3?`drop-shadow(${n.slice(0,3).join(' ')} ${c})`:'';}).join(' ');element.style.filter=layers||'none';
    }else if(!s.shadow)element.style.filter='none';
  }
  element.style.setProperty('--wear-dark',`rgba(14,20,25,${s.wear/100*.23})`);
  element.style.setProperty('--wear-light',`rgba(255,249,224,${s.wear/100*.24})`);
  const rgb=s.accent.slice(1).match(/../g).map(value=>parseInt(value,16)/255);
  const light=rgb[0]*.2126+rgb[1]*.7152+rgb[2]*.0722;
  element.style.setProperty('--surface-ink',light>.53?'#22242b':'#fff5db');
}

function renderButton(host, recipe, {state='normal',label,symbol,action=()=>{},sound=null,size=null,tintStrength=null,textureUrl=null}={}) {
  if(recipe.schema_version===3&&recipe.source_button){if(!sourceRenderer)throw Error('Die Originalbutton-Ansicht ist hier nicht eingerichtet.');return sourceRenderer(host,recipe,{state:state==='normal'?'original':state==='pressed'?'active':state});}
  for(const previous of observedButtons)if(!previous.isConnected){buttonObserver.unobserve(previous);observedButtons.delete(previous);}
  const s=recipe.settings;
  const view=button({label:label||s.label,symbol,disabled:state==='disabled',
    motion:()=>({duration:s.duration,easing:feelings[s.feel]}),action});
  const el=view.element;
  el.classList.add('preview-button');
  el.style.fontSize=`${size||s.size}px`;
  materialize(el,recipe,{tintStrength,textureUrl});
  sizing.set(el,{width:0,base:recipe.base,settings:s});
  if(recipe.base){const b=recipe.base,face=el.querySelector('.comic-button-face'),labelEl=el.querySelector('.comic-button-label');
    if(b.label_visible===0&&s.label===b.text){labelEl.hidden=true;labelEl.style.display='none';el.setAttribute('aria-label',s.label);}
    if(b.image&&s.material===b.initial.material&&s.accent===b.initial.accent){const picture=el.ownerDocument.createElement('img');picture.className='button-picture';picture.alt='';picture.src=b.image;picture.style.objectFit=b.image_fit;face.prepend(picture);if(b.label_position){const p=b.label_position;Object.assign(labelEl.style,{position:'absolute',left:p.x+'%',top:p.y+'%',width:p.width+'%',height:p.height+'%',maxWidth:'none',display:'grid',placeItems:'center'});}}
    if(b.symbol){const span=el.ownerDocument.createElement('span');span.className='comic-icon';span.textContent=b.symbol;span.setAttribute('aria-hidden','true');face.append(span);}
    else if(b.svg){const span=el.ownerDocument.createElement('span');span.className='comic-icon';span.setAttribute('aria-hidden','true');span.innerHTML=b.svg;face.prepend(span);}
  }
  fitButton(el,(size||s.size)*(recipe.base?recipe.base.width/23:BUTTON_WIDTH_UNITS));if(buttonObserver){buttonObserver.observe(el);observedButtons.add(el);}
  const setLabel=view.label;view.label=value=>{setLabel(value);fitLabel(el);};
  if(state==='pressed'||state==='selected')el.setAttribute('aria-pressed','true');
  if(state==='hover')el.dataset.previewState='hover';
  if(state==='focus')el.dataset.showFocus='true';
  if(sound){
    let pointerHeld=false,keyboardHeld=false;
    el.addEventListener('pointerdown',()=>{if(!el.disabled){pointerHeld=true;sound.play(recipe,'down');}});
    el.addEventListener('pointerup',()=>{if(pointerHeld){pointerHeld=false;sound.play(recipe,'up');}});
    el.addEventListener('pointercancel',()=>{pointerHeld=false;});
    el.addEventListener('keydown',event=>{if([' ','Enter'].includes(event.key)&&!event.repeat&&!el.disabled){keyboardHeld=true;sound.play(recipe,'down');}});
    el.addEventListener('keyup',event=>{if([' ','Enter'].includes(event.key)&&keyboardHeld){keyboardHeld=false;sound.play(recipe,'up');}});
  }
  host.replaceChildren(el);
  document.fonts?.ready.then(()=>fitLabel(el));
  return view;
}

return {registerSourceRenderer,materialize,renderButton};
})();
const __bjMedia=(()=>{
const {renderButton:originalRender,materialize:originalMaterialize,registerSourceRenderer}=__bjRenderer;
// Opt-in editor/library extension. Games retain their unchanged original renderer.


const matchedFont=font=>typeof font==='string'&&font.startsWith('media-')?font.slice(6):null;
function previewRecipe(recipe){
  if(recipe.base?.surface_mode==='custom')recipe={...recipe,base:{...recipe.base,initial:{...recipe.base.initial,accent:'custom'}}};
  if(recipe.settings?.font?.startsWith('letter-'))return {...recipe,settings:{...recipe.settings,font:recipe.base?'source':'inter',lettering:'plain'}};
  if(!matchedFont(recipe.settings?.font))return recipe;
  return {...recipe,settings:{...recipe.settings,font:recipe.base?'source':'inter',lettering:'plain',ink_mode:'auto',depth_mode:'auto'},
    ...(recipe.base?{base:{...recipe.base,soft_shadow:'none'}}:{})};
}
function applyStyle(element,recipe){
  if(recipe.settings?.font?.startsWith('letter-'))element.dataset.letterFont=recipe.settings.font.slice(7);
  else delete element.dataset.letterFont;
  const style=matchedFont(recipe.settings?.font);
  if(style){element.dataset.mediaFont=style;element.dataset.originalSurface='false';element.dataset.inkColor='auto';element.dataset.depthColor='auto';}
  else delete element.dataset.mediaFont;
  const label=element.querySelector('.comic-button-label');
  if(label){
    label.style.fontWeight=typeof recipe.settings?.font_bold==='boolean'?(recipe.settings.font_bold?'700':'400'):'';
    label.style.fontStyle=typeof recipe.settings?.font_italic==='boolean'?(recipe.settings.font_italic?'italic':'normal'):'';
    label.style.fontSynthesis=typeof recipe.settings?.font_bold==='boolean'||typeof recipe.settings?.font_italic==='boolean'?'weight style':'';
  }
}
function materialize(element,recipe,options){originalMaterialize(element,previewRecipe(recipe),options);applyStyle(element,recipe);}
function renderButton(host,recipe,options={}){
  const view=originalRender(host,previewRecipe(recipe),options);
  applyStyle(view.element,recipe);
  const label=view.element.querySelector('.comic-button-label'),doc=view.element.ownerDocument;
  if(label&&doc.fonts){const css=doc.defaultView.getComputedStyle(label),family=css.fontFamily.split(',')[0];
    doc.fonts.load(css.fontStyle+' '+css.fontWeight+' '+css.fontSize+' '+family,label.textContent).then(()=>{if(view.element.isConnected)view.label(options.label||recipe.settings.label);}).catch(()=>{});
  }
  return view;
}

return {matchedFont,materialize,renderButton};
})();
const __bjAudioRecords=[{"id": "media-piece", "name": "Spielstein setzen", "group": "Karten, Würfel & Spielsteine", "description": "Marke oder Chip ablegen", "file": "media-piece.wav", "author": "Kenney", "source": "https://kenney.nl/assets/casino-audio", "license": "CC0-1.0", "license_url": "https://creativecommons.org/publicdomain/zero/1.0/", "duration": 0.1725, "button_offset": 0, "button_duration": 0.1725, "media_short": true, "sha256": "9daa659417fc4edd3c864c170b258d2d3a299cd44cab8937ea796f4025785cd3", "source_id": "media-sound-piece"}];
const __bjAudioAssets={"media-piece.wav": "UklGRpI7AABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YW47AAAAAAAAAAAAAAAAAAAAAAAAAAABAAEAAQABAAEAAgADAAMAAwACAAIAAwADAAMABQAGAAUAAwAEAAUABQAFAAYABQAEAAUABQAEAAQABAADAAMABAAEAAMAAwACAAIABAAEAAUABQADAAEABAADAP//AAAAAAAAAgAEAAIAAgADAAIAAgAEAAIABQAKAAcAAgADAAUABwAHAAUABAAHAAYABgAJAAcAAwAIAAoABQAFAAkACQAEAAQACwANAAUABwAOAAUA/v8GAAwACAAHAAYABAAHAAcAAgAIAAsABQAFAAgABwALABIAEgANAAsADwASAA8ADgASAAsABQANABMADwARAA8ACQANAAwAAQADAAkACAAMAAsAAwAKABUADwALAA0ABAAEAA8ACgD/////AQADAAkACQAHAAQAAAAFABUAEwAKABIAHgAZABMAFAAVABEACgAHAAwAEwASAA0AEQAZABcADwAIAAcAEAAWABAACQAMABIAEwAWABgAEgALAA4AFgAVABUAGgAUAA8AGwAdAA0AEAAhAB8AFAAZACIAHQAWACAAKgAjAB4AIQAcABgAGwAXABcAIAAeABsAJAAiABoAIAAhABcAGgAkACIAGAAPAAwADwAOAAoABQD8//r/BQAJAAMABQAJAAcABwADAPz//P8CAAEA+f/6/wAA/v/8/wEAAAD8/wQABgAAAAAAAAD9/wMAAwD8//7/AgABAP//9P/w//z//////wkABgD7/wYACwD4//L//P/1/+7/9//1/+f/5P/o/+z/9f/7//b/9f/+//v/8P/6/wYAAQD8//3/9v/1//7/+//0//3//f/q/+X/8v/y/+z/8f/8////+f/u/+j/7v/z//P/9f/y/+z/7f/1/wAACQALAAcABwALAA0ACQABAP//BgANAAcA+f/x//X/+P/x//H/+f/0/+///P8BAPn/+f/6/+v/6f/4//n/8P/7/wgABwADAAEABQAUABYABQAAAAUAAAD+/wEA/f/9/wAA+f/4/wQACgAMABAADQAIAAcABgAJAAsA///0//j//f/+//7//P/6//n/+v/1//D//v8LAP7/7//0//X/9f8AAP3/8f/z//T/6//s/+7/6f/p/+n/5P/p//j//P/u/+P/6v/z//T/9f/x//D//P/5/+P/3v/o/+r/7f/3//T/5//c/+D/6v/o/+j/9v/x/+H/4v/h/+L/9//6/+X/5v/y//H/8//2//D/8P/0//b/+//y/+f/7f/v/+b/5//n/+T/6//t/+f/6//q/9v/2P/j/+P/3P/W/9T/3f/n/+D/1//f/+v/6f/n/+z/7f/s/+z/5v/k/+n/4//f/+z/9v/y//L/+v/5/+z/5P/r//T/9v/0/+//7//9/wQAAwAFAAAA8//1//j/8f/z//H/5v/o//D/7P/q/+7/8v/5/+3/2v/n//n/7P/o//j/8f/l/+//9f/s/+v/6//m/+n/7f/k/9z/4f/m/+X/4f/h/+L/3//b/9r/2v/g/+v/5v/b/+P/7P/o/+7/8f/k/+L/6//o/+b/6f/b/9D/3f/x//f/7P/d/9v/4v/o/+v/5P/f/+3/9P/r/+//9//x/+r/7f/z//f/7//l/+3/8f/s//H//f/8//H/6P/u//z/+v/3//j/8f/w//z/+v/t/+//7//p//X/BAD///T//P8AAPL/7//+//v/7v/3/////v8FAAwACwAQAAoAAQAJAAoAAAAHAA0ABAAHABAACQAEAAwAGQAbABAADQAUABAADAAPAAkABAAQABYADgAMABEAFgAVABIAFAAUAA8AEwAYABIACwAGAAMAAwD+//j/9//z//b/AwD//+7/9P////r/8//z//j/+P/x//X/AgAAAP3/AAD6//b/AAAAAPb/8//0//v/BQAHAAYAAwD8//3/AgD+//v/9v/t//r/BgD1/+v/+v/5/+v/8/8AAAEA+//4//z//P/4////BQD2/+v/+/8HAAMAAgAAAPv///8DAAAACAAWABAABgALABAACwADAAEABQAFAP//AAADAPr/+/8HAAgABQACAPr///8KAAEA//8SABMABwAIAAQA9v/0//n/+P/z//X/+v/0//H//v/5/+D/5f/5/+//5f/0//7/+v/3//b/8//w//D/8v/z//P/+P/2//D/9f/7/+3/5//8/wcA9//r//H/9P/3//3/9f/v//f/8//q//D/9P/y//r/+//0//n/9v/o/+P/5//x//f/8P/w//T/5//q////+P/t//n//P/9/wUA9//h/9//3f/c/+v/8v/x/+3/5f/p//X/8//x//j/+f/6//b/6f/q//D/6P/w//r/6v/k//T/7//d/9v/4//r/+z/5P/d/9n/2f/i/+j/6v/v//L/8v/0/+v/5P/y/wAA/v/3//f//f8CAAIA///8//7////6//n/AQAEAAQACAADAP//AQD7//j/BgAJAAIACwAQAAQABAAMAA4ADAAFAPv/9//1//r/BwANAAsABwAFAA0AEgAKAAoADAD/////DgAQAA4AFgAVABAAEgASABIAFQARAA8AEAAJAAwAGgAYABEAGAAZAA0ADgAdAB8AGQAbABcACgALABcAGAARAA4ACAAGABAAGAASAAQA/v/7//3/CQARAAUA/P8AAAUADQARAAgACgARAAcABQARABAADgAZABkAFgAcABcAEQAWABUAEgAXABYADQAPABkAHQATABEAIgApAB4AHwAkACEAJQAlABsAGQAdACAAKAAnABwAJAA1ADcALwAtADEANQA0ADIALgAnACgALgAtAC4ANQA5ADgAKwAbACIAMQAwACoAIAAdAC0ANQAkAB4AJwArACcAHwAbAB8AGwAVABwAGQATAB4AIgAZABsAHgAZAB4AKgAqACYALQA0ACoAHQAnADIALAAsADUALwAoACoAKAArADgAOAAsAC0ANwA8ADoAMAAkACIALQA1ADQALgAlACcANAA1ACYAKgBCAEkAQAA/AEMARABKAE4AQgA4ADsAPwA6ADQAMgA3ADoANAAyADwAQQA3ADUAPAA5ADIAOgA9AC8AJwAqACgAIgAoADAAMAAqACMAIwAqACcAGQAXACIAJgAhAB8AGwAVABQAGQAgACgAKAAbABMAGQAfAB0AFQAHAAUAFgAhABQACwARABEACgAMABAAEAARAA4ABQAHABAACwAHABQAGwAOAAkAEAATABYAIAAeAA0ACgAXABgAEgAXABkACAAEACMAOwAfAPz/AgAcABoACwANABgAGwAWAAgA+/8BABIAFQANAAwACAD9/wAADwAPAP///f8TACsAKwAQAPb/9P8EABAAEQAQABEAEwAUAA0AAgAEABEAEgAIAA4AIQAgAA4ACgAUABkAFwAUABEAGgAoAB8ACQASADEALwALAP//DAANAAoAIAA1ACoAGgAfACcAJAAcAA0ABQAcADcAKAAJAAsAGwAQAAAADgAmACcAHwAhABwAEgAaACEAEwAMABkAGwAUABsAIQAbABUAEQAUABwAHQAaABgAEAAHAAoACwAHAAwAEgASAB0AKgArACgAGwAOAB4AMAAlACIAOAA4ACAAEwAUAB8AKQAgABwALwA2ACkAIwAeABkAIwAuAC4AMgAuACUAMQA0AB4AFwAiACEAIAAkAB8AJgA0ACwAIgAvADcALgAiABEAEwAsADUAKwAqACYAHwApACoAGQAYAB4AGwAhACgAGwAOAA0ADgAXABgACgAUADEAKwASABMAGgAbAB8AHAAZAB0AGAAWACcAJQARABUAHQAWABcAFgAIAAgAFgAdACIAIQAWACEALwAdAA4AGgAbABIAGAAcACEALAAhABEAHAAnACQAJgAdAAgAEQAkABwAEgAYABkAFAASABQAIgAsABcABAASACEAIQAgACAAHQAhACAAEwANABgAHQASAAkAEAAcABsAEwALAAoAEQAZABwAHQAaABYAGAAZABEAEAAYABsAHAAjAB0ADwANAAoABwAUAB0AEwAQAB4AIgAcABkAFgAVABcAEwAQABMADQAEAAsAEQALAAsADwAIAA4AIQAbAAYACwAeACIAHQAZABcAGQAZABcAIAApAB8AEwAUABQAFwAkACUAGgAZABkADwANABEABwAAAAUACAAJABIAEQAEAAEAAQD6//r/AwABAPX/7f/v//f/9v/q/+j/9v/5/+//7v/u/+b/5f/p/+P/4v/u//T/7f/n/+P/3P/W/9X/4P/w//L/6f/r/+7/6f/s//P/6P/a/9//5P/b/9n/4P/k/+3//P/6/+r/6P/2//r/8P/t/+3/5f/e/+T/7P/r/+v/7//s/+v/9v/7/+7/5P/p/+z/6v/t//L/7//u//b//f/5//H/8P/6/wQAAwD6//b/+f/+//3/+P/x//L//f8EAAUACgARAA0AAgD///z/9v/8/wsADQD+//T/+P/7//n/+f/6//z/BAAHAPv/7v/7/wwADQAKAAoAAAD6/wcADQAEAP///f/8/wMAAwD2/+//9/8BAAQA+v/t/+v/6//u//f/9P/w//j/+v/4/wMA/f/i/+P/8v/1/wAACgD+//n/AAD6//n/AAD7//f///8EAAwADwADAAIACwAOABYAHAAQABAAGQAPABEAGwADAPH/BQARABUAKQAkAAcACAAaACAAIQAXAAkAEgAeAB0AHgAeABgAGwAlACIAFwARABUAGgAVAA0ACQAKABAAFwAZABcADwAFAA4AIAAXAAUABgAMABUAJAAfAAkABgATABQACgAFAA4AFgAPAAkADQANAAoADAASABcAEAADAAgAFwAbABcAFAAWAB4AGQAMAA8ADAAIACUANgAgABwAGQADAB4APwAXAAIAJgAbAP7/DAAYABwAIAAMAA0AIAAPAB0ARQAmAB0ARgATAOn/OABDAP7/GgA7ABEACgABAOj/FQAmAAIAMgA8AM//zP8WAAcAIQBaABkA+/8kAND/mP8tAHcADgD3/zgAHgDM/8T/GQBcACgA8P8rAFEA9P+r/+T/MAA3ACUAHgADAPD/EAARANv/9/9KADcAAAAGAPn/5P8DAAIA+/86ADwA5P/h/xAAAAAPADwADQDZ/wIAMQA0ACUA/f/b//X/LwBMABYAxf/u/2IARwDR/+f/ZwCEAEcAQgA0AKP/XP8hAL8ASgDc/9z/kf+V/0EATADc/yYAbwD4/7z/AwAyAG0AmgA9AKP/Zf/L/3oAWQCf/+D/mAA/AN//XABTAL7/+/9QAMz/fv8IAHIABgBk/77/1AAMAXgAOQCk/8j+f/+sAN//Cf9EACQBTADd/0YAPwD6/+z/1f/g/2wAMgEgAbz/yP5///z/iv/t/3gA5v/7/7oAEACD/3MAXgBP/9H/ogAsACAAxACbAPb/yv8+ALIANwCd/8P/Wf8X/6wAEQEv/3z/+ADi/5v/+gAWAKL/MgEvAOD+YQCV/9L9lwB5AjcAu/+uACAAWAA4ANT+HgDnAQMAjP7n//sAMAGGAOb+v/4KAL0A9gAhAIX+8/4CARMCtgG9AIQAwf8a/XL+DAN1AKP9tgTmBNr5dvuWBTcCUvzT/xQBj/+iALH/jP9WAZX/egAoA7z+T/+gBfr9kPhSB3gKIvr2+B0Crf5z/OUCjgRJAhcBQP9S/ZH77/7/BnIF8f7q/239P/7GCVT4D9Uv5GkBQezN4ysIyhIADnAiCxgm45PCJsQw8pBA3Uj1DgIVEDbI/B6xzqwoy6oC20HxPNMUQA4J8ufA+NsIGMIUhgmqJUsnVQK86BPZctHn7vUZLR8bDe4Kkgjt83XvEgOQAib1dAhCJZcfAgV964HgRPGx/jz0nAH/J8olQgLr8WDvPu3/8Uj42ggdIW8YrvmX+osJ2/sY6iz32xLYFnT9A+3U83b3jvvoAQnrwNnh/ToY7AoqGZcp3/0L1E7XUuMMA38ouBeQBCgo7jBV/G3U1Mp50/X8gSEwHjcW4g9B9lno4vPB94P6ABIvIt0UAQFP967vL+rV8a8DEhGFE/QMKASjAfn94e6j59H7phcVHFcECesb7D70weZj5HYE/RnPF9YcPBbz8EPTy9Pe7lEdSjHDFqoJfhntDZvnZNFM0uTr1xUpKtwigRT2+GDavd2b/PUSPRnHFnUM4f2a8iHsROKZ24PyHxteJsEWKg3SAOLoxdoP3EHutRjGOpYxhhN1+pPg3s0z17r31hQzHjkfriAvDefgVMRO0Xb5CCLJMPginw/V+lreos312GH7diY/OaMkeQr2+JndBM0f4TIAxxPaHfQXRwjG/TXvot7v4z37BhGVINsgpg2O+BbrreMb638BhxQJGMANU/+j9inxsOog7RD9NA26E/EStAzzALH0WvDE9okBgwg7CDYCav0M/+T/5fcK8Sn5pAeYCQgBgP6oA9oFowPCAYP/i/uT+O35iwAgCLsJFgSR+0z1K/Xu+SD/OwWJDMQNGwZH/uD7GPu3+d35J/w1ABYFcwamAY37Yvka+lL85ACiBXYHywbRA7L+gvtV/Bn9Xvx9/uQD4AXCAMD61fo6/mr/CAAcApgCJgEwAaYC9wItAcb9Yvsr/aIBhgOoALb8CvzJ/VH/JgKMBuYGIAGb+xj7Gf2X/soAcQR/BW8BQP3N/GP8h/qt+2sAxATNBngFTwB9+6T7+v7dAA0BPAKuAw4Cov76/Ub/I/4k/BP+/wHPAhsCZQNVAxX/lPtL/I7+YAGBBMADjf5w+1T+MgM8A+v9bvuC/28CJgEaAtcDo//c+mn9EgLAAWj/sf97ASgCuwHHALf+EP3H/ocB0ACk/4QCXwT1/8X7Af6JAIT+2v5yBAsGdwDy/Ab/OwDk/qL/VwJoAsD/4f5lAD4ATv6I/pQAUQE+AYcB1gAC/1P+MwCgAk4CUwAcADQA4/51/3kBRABg/iYAYgEo/1r+kADLAVcBNAHjAFz/zf0Y/pIAKwP/AjUAX/7L/hD/Wv8OAl0E3gFY/d/7Tv2T/wQC8QNEBBECb/7j/Pr9f/61/vYAQQNTA6ECXAF9/if8qvzV/vYA3QLVA6AC1v+N/er8y/1G/ygAAQGiAqECHAAI/83/4f5b/qUACwHQ/uT/6ALbARn/Ov+R/7D9tP0oArAFTAPl/sv9EP5l/SL+ggAhAp0CDwFS/YX82QCaA3UB9v/rAOb/lP2S/oIBWQJJAfX/bP+bAMYAdP2h+8f+SQGCAP8A4AKmAucAnv7o+8/7Wf+iAp4DqQOdAln/UPyw/TUBUQAW/bH+/wEZAYUAkwLjAMT8TP2T/yX/MgBOA8kCvP+2/ij+X/3Z/3oD+gIfAGb+Ff3R/fABRgM4/279PwAdAdH/IwFmApv/P/1a/zIBYv9s/vf/LgAMAeQE5QNe/Gj6Mv9q/0X97QAaBFABIv/U/yoAVQE8Ao//t/3D/4r/ofxB/h8CNAF7/9YBDQOSAK7+Iv1Y+0X+4wPbAz4ArP93/8/9i/+sAmkAi/zy/ucDewOo/6/9dPwk/GIApQTzAfD9Hf8hAOT+nACHAVP87vniANgG8wP0/nn96vzp/NT/7gLFApUBCAER/3v8Ffw9/fr+jgE0A/ICQwKjAMH98fye/uj+p/7DAf0ESgKw/ET7Tv0C/0QBSAOxAZ3/igDL/0L8VvyG/94AfwIuBY8Di/47/KL8mP3M/2IBFQBV/z4BdgEW/z3/PQHP/9b9cgDWAlUAQP7+//YAR/+X/mUAFwJFAeD+o/0S/q3+HP8XAB0CGgTrAhT+lvoL/Nz/HwLZAYoA7v+7/5r/8QC7AmABjP36+3z+EwLcAqAABv+E/5P/iP6x/jwADgGTABUA4f8z/wj/RQBCADn+0P53AikDcQBg/6P/V/6H/RP/IQAF/77+aAHuA8kCU//T/EH8jP1oALgCOgIaAJ//mQDH/wP++f6fALz/g/8BAcH/mv3n/7YCfAAx/dP9XABZAdkAjQCEAKn/0f4z/7H/5v+BAP3/R/6P/jsA9f+a/8IBnAJM/y38//xR/4IAOAGqAXIBQwGYAHz+E/0k/qv/JQAGAHD/nf9uASMCAAC5/Vz9V/4sACACsQImAYj+E/2L/bH+QwDGAUgBSAA4AdwAs/39/HL/CQD9/kb/WQDgASUDUQHj/RT9nP1p/fj+5QEUAmkASwA7AL7+iP7p/ywAIgBoAccBDwAc/uH8Df0+/5wBnAJ3AoUAv/0o/fr9ff6mAI8DMQO5AP/+Dv2f+zj9igDWAigDQgHJ/lD+O/8w/xX+vP1z/0sCyAOFAiH/7Pv3+/r+BQHZANAAEgHY/wP+x/2t/ub+EP/mAB4D4QJIAN/9gP3t/hIADwB2AGIB+QBY/+b9aP2f/mgAVQCr/+0AJQK7AH/+I/41/4v/Of9qADcCiQGk/yb/g/5F/Vz+RgGLAn8BUv8n/dz8+f5kARUC+gCC/yb/QADNAd8BxP+S/Qr9jP3e/scAdQEGASgBgQBP/uH98f/KAK7/af+BADsBHwGNADr/5P2M/nUAlgAs/33+PP5I/jQAhwI4AjsAJ/8r/6j/agC3ABUAvv+cAJ8AfP6i/cT/qADj/iH+2/51/xMBGAPXAtQAof4c/TP+BAHRAdsAXgBu/zn+qv5A/1/+WP4LADoBuwFmAkAB8f2V/ID+v/92/9IAFwPiAsMA8v6N/cb8jf2b/38BxAFBAJX+n/7PAPMCwQFK/kr9Qv/UAFABOQHq/4L+qf6F/+7/uv/y/oH+Xv8zAaQCkgFN/ir9dv82AUUBOAHB/yz9U/0HANABMQJ/ASb/EP2P/Wf/cQCdAK8A4QCuAKP/4P62/5MAnv+0/oT/JwBPAJwBqwFm/vT7Nf2g/wAC1gNTAqj+yP1y/8b/rv6S/gUAfgHEAY8B7wCB/un7dPwh/yoBNAIQAscAyP///uH9R/6eAAMC+QAo/6/+6f/IANL/sP70/s//uQBsAZMAi/6p/Tv+Iv/IAKcCQAI1ALP/7f9k/v/8/f2g/5IAMgHsAAkA0f+r/wX/yv4s/wsAMwFDAX8AQgAG/8f8bv2QAM0BpQEdAhgBLf6k/Hz97/4DAPcACwJbAv4AJv/y/RD9tf3SAA8D1AHi/2//9/5N/vL++P8XAIEAhgGCAVEA2v5i/VT9qf/cAeABIAGhANH/0v7p/ZT97P4UATcCewLgAbn/of02/ab9zP79AIACHALRAIf/eP7t/Tf+nP8TAS8B1QD/AEcAw/5o/tP+Iv9dALEB/ACE/0X/NP+a/v3+fwBYAf4AUgC9/zL/C/+c/2wAVAA6/+7+PwAcAVIANP9c/h7+7P+DAoICQgBj/oH9Cf4yAMEBPQHp//n+L/9sAIoALv8H/ywARwC//8z/jf8Y/8j/xgBSACj/Kv8zAN0A6ACgAMP/9/5n/ysAt/+1/p3+jP/kALUBOwEQAD//4f7k/kb/cP+R//UAywIdAiT/bv3m/dH+HQCaAWwBAABX/xX/xf5Q////LAAcARMCFQFM/1T+1P1x/lAA5QDK//b/gAF7Ac3/x/6y/pT+Ef+XAGsBnACp/1P/Cv9h/34AggBa/5b/IwEBASL/b/40/33/mf+eABgBAAAy/5//1f9m/2P/6P9fAN0AQgGiAOP+x/2H/uH/mQALAeUAvP8b/63/nv+z/t/+LwAYAVcBXwHWAFj/qP1N/Zz+OAA1AdcB2wGeAMz+w/3k/dX+XwD0AWECQgGj/2/+6/1y/qn/VQBwANAA9wBFAJX/Wv8B/xD/XADDAbABcwAa/zL+UP5T/xYArwDaAQoCzv90/Vr9iv4pAE8CHQMfAXr+n/1v/s//qABTAND/ZwA6AbsAUP9b/lj+Lv+JAD0BfQCF/7T/XABDAG//iv59/tH/SgE8Af7//P7g/sX/EQFeAVkAT/8N/zn/Xv9Z/6v/CwFqAq4BW//i/bn9Sv4UACsCDAI7AHT/0P+7/zf/8/5L/4QAvAGAARkA2P5q/ib/jgAkAasAYgBdAMv/Kv9J/7z/HgDJAD0BYAC0/v790/5AAEQBRQFeAKz/zf/c/0P/5v51/3wASwFnAc8AKgCj/8P+Sv5C/2oASAAXALwAkgA9/7L+T//L/xAAWgA9ADwAywCtAGX/sP58/2cAbwBHAEkAtv/m/o7/WQGnARgAJ/9l/zP/1f6s/70AoQBbANQAngD+/tr9oP4oAAIBHAGbAJ3/+f5J/+b/MQBdAF4A8v98/1r/YP+i/0cAzgCsAPn/Dv+E/uL+uf8+AIIAyACtAN//tv4Y/s3+WwBLAQgBOQB2/0f/9v+EAPr/N/9O/8j/HgBSAOj///4R/1IA1wDZ/+r+I//n/30AnwD3//H+0/7U/6EAfQD3/57/qv8lAH0AIwCx/8j/7P+k/z7/G/95/1UA8ACsAP//Xf/a/gP//f+gAFgACgAnABYAsv9s/3z/zP8OAAEA3//z/wAA6f8PAHAAcQD0/4v/ef+B/5v/4v/9/9T/FQC3AG8APf/g/sb/jQDKAN4ANQDG/mH+4/92AVwBKwA4/+3+SP8qALgAMwCO/wYAvwAyABH/6P6Q/zIAywAYAVsAAv+D/lD/XADDAKoAfABGAB4AJAD6/27/Mf+l/ywAggDyABIBPgD//m7+0v6e/zcAhACuAI0AAQCF/2D/Nf8u/9v/uwDXAFcA2P9T//L+R/8cAI8AegB+AKAAKwAa/2j+tP6i/8MAvgHFAWkAqf76/a7+6v/MABABwAAPAH//Xv9X/yj/V/8zACABbwHyAOb///7c/j//ov/7/10AxgAgAfQAAgAO/73+5v6X/8kAUAGgAAAA4v9J/5n+K/9eANgA9AAfAYsAdP9G/+L/2v8z/yD/3/+8ACEBqwCd//L+Hf+t/3MAMgHxAMP/Ov+m/7D/Nf9P/wUAsgAjAfAAt/9o/kf+I/8WANQAPwECASoAbv9D/zD/y/7W/gMAXgGcAeYA7v/5/of+Af/H/zMAkwAFAesAQwDN/5b/Jv/l/pb/pQDdAGUAJwAVALr/Y/90/7r/FACPAOMAsgAAABv/hf61/ov/aADlAPoAugBJAN//j/9B/wn/Rv8MAMIA1gBlAMT/M/8K/1H/zv+kAJYBcgEAALL+Q/48/uL+dwC0AawBLAGWAGD/Bf6t/V/+uP+UAdIC/QHW/4P+l/4M/1r/zv+fAIMBswG6AEb/Tf4C/oX+GQDFAesB0AAFAMX/Sv/D/uL+yv/5AHwB1ADJ/zL/9v4W/7j/NQA5AJgAVwFBAUgAif8f/7b+6v4LACwBjwFDAWwAUP97/kr++P5pAJEBdAG2AFAA3P8B/7n+ff9XANcAaAGDAVgA5v6V/vP+Mv/U/w4B2QGaAc4A4f/2/nP+s/6l/+IA0gHOAcIAZ/+G/lT+zf76/2IBCgKWAakAxv/T/hb+VP6c/w4B7gH5ARABiP9t/oD+PP/j/68ArAG6AYEAT//S/or+s/7g/0kB2AGJAacAaP+G/pP+Pv8UAOEAMAHZAIEAaADz/zH/Ef+o/0wA2gARAUMA8v64/sH/oADCAK0AeQAUAOb/2f9x/zL/2v+vALwAdgCDAG0A8P+w/9b/q/9A/6L/0QB8ARsBbADj/3X/Vf+D/7P/DwDEACEBlgDZ/7T/yP+K/1X/k/8vAPEAbwEaAR0AOP/X/ib/LwAwARYBHACN/8X/8/+x/4j/2f9tAOAAywAsAJ3/dv93/6X/NACiAGIA9v/+/xIAvf9+/8n/LwBeAJIAsABSALf/W/84/0L/0v/GAD8B2gAcAHr/F/8//+T/VABUAF4AoADBAHIAp//a/sX+b/9PABwBgwEJAfn/UP9H/yX/4f5n/88A5AG+AagAY/+u/vf+y/9bAHwAeABsAGMAWgDz/xL/mP5+/zYBFQJOAav/bv5G/hb/OAD3ABYB+wDqAH0Agf+t/qz+Xf9jAGcBtAHiALD/PP+C/47/MP8//xoAHwGQAS0BMAAt/7T+5v6F/z4A4gBIAT0BrAC8/7/+W/4c/4oAdwFfAboAJQDL/2//Af/k/oX/xADmAQUC1AAM/+f9JP5s/74AYAFBAbIACABu//H+y/5L/1wAXgGZAe0A5P8V/9D+IP+3/yoAgQD2AEIB3QDW/9n+bf6s/oz/vQBxATcBmwAhAJ7/C//U/in/4f+uADQBIAFMACD/jP7t/pD/8P9DAKYA2ADMAH8AzP/i/nz+Df8zACQBUAG3ANj/Mf/k/v/+hv8lAI4AywDMAGUAw/9F/xv/SP+4/0UA0QARAawAwP/g/nn+sv6a/9EAhgFVAZcAlP+X/lz+EP/6/74AYgFuAbAAvf/x/nX+zv7t/90ALwEuAbwArv/C/qP+4v4r////QQHgAV0BLgDx/k3+oP6K/4EAPAFqAfgAPgB4/7T+YP7o/gYABAFzAUEBewCC//D++f5J/77/bwD/ANkAHABr//7+3v5Q/y0AzAAJARcBqQC8/wj/1/76/pP/hQAlARsBhgCW/8r+uf5U/xAAngDLAGgAxf+L/7H/jv87/3X/TwAnAWkBwwBz/1X+Kf4O/4wAmwFjAVsAqP96/zr/8f4y/+b/eQDXAAkBpACQ/5r+if5C/y4A5wAgAbEA7v9i/zf/Y//q/1kAPQD5//n/8v/C/7n/0f/T//T/RABXAPP/eP9K/3T/5v9nAIkAPQD0/9j/0P/i//L/zP+h/7j///8yAC0AAADX/8D/t//B/9n/DgBpAIQAEgCQ/3X/i/+w/wkAUgAvAAAAMgBdAAkAkf9j/3r/3f92AKYAHACV/67/9//d/6j/2P84AGIAXAAjAJr/Iv9B/8z/LgAjAOf/4f8YADwAGQC9/2n/gv/5/zMA+P+v/7L/5//t/6T/gP/f/2wAqgBlAKT/3/7b/rX/mwC/ACIAef9p/wUAoQBzAJn/D/9l/yAAjQBvAPL/e/90/9b/DADO/5P/zP8+AJsArgAnAEr/Cf+u/28AmgBFAOb/vP+y/7v/3//5//D/8v8fAEgANQD+/9z/3f/v/xQASAB2AJsAhwD5/0r/KP+X/xgAXQBaADMAGgAZABUA7v+Z/2j/vf96ABAB/gBMAJr/aP+D/6j/BgCmAAoB5ABmALb/7P6q/mz/iwATAe4AdgDe/3v/lf/e////LQCRAMQAbADd/47/jv/H/x0ATgBLAD4AJAABAPP/1f+Z/5//DACHAK4AWwDO/4b/mf+3/9j/EQBFAFwAXQBGAA4AuP9h/1j/0f+PAAkB7gBrANz/av87/3v/HQDFAAMBrQAFAH3/X/+o/xkAgQC7AJIAJQD4/wAAu/9m/7L/aADUAMsAdgDf/03/V//9/3gAZwBSAIcAmQA/AL//bf9m/7j/WADjAMQAFQCZ/5//1P8NADgAKwASACwAOADw/5//q//1/xwAGwAaAAEAw/+q/9v/CAD4/9T/5P8ZACcAAADZ/8v/5P84AIoAegAMAJb/ZP+p/0IAnQBYAMP/cv+P//f/cwCkAFEAz/+I/4P/pf/Z/xYAYQCFAEQA0/94/0H/Xf/Y/0YAcgCGAHkAOADm/4X/O/9r/w0AmADQALsANABY/97+Gf9y/6j/KwDGAMAAUwAQALv/LP8V/7b/VQB6AGEALgDQ/4L/jf/B/+H/9v8PACsAKQDP/0n/Hv9v//L/ZwCIADgA0P+a/3j/Yv+F/9//LwBXAFoAGACG/xP/OP+8/ykAZQB4AG8AUgDy/0f/zf4A/8T/hwDmAOIAjADj/z3/Bf8x/4r/BACBAMMAnQAAAEr/GP+J/w4AQgBAADkAIQD7/+H/xv+r/8n/GABMAF4AXwARAIv/cv8EAJYAhQAOAKv/cP9r/8P/QQB3AD0A3v/Q/xUAIQDd/73/0P/w/0YAiQA1ALD/kP+k/7b/AQB2AKUAcwAcALr/Xf9a/9L/aQDSAPAAiQDF/07/W/+O/9//aQDDAIMA6f9v/0L/a//w/40A5wDZAGMAtP9E/0X/cP/F/3EABQHoAEgAwv96/zr/K/+m/2gAzgC9AHcABwB7/yP/Wf8OALAAxQB9ADAA7v/K/9L/1//G/9j/LQCPAKgAbgD9/3f/Qf+z/1gAlACEAHEAPgD5/9b/xf+//wcAmgDiAIQA/P/F/7D/nv/W/ywAMgAcAEUAagA4AOH/s/+w/77/3P///xsATACHAIEAIwC4/5n/2f8fABcA8f8AADUAWQA9ANH/av96//P/bwCTAD4Ax/+c/7v/6/8JAAMACwBpANcAsgD7/2v/df/E//X/GQBCAE4ASABBAAcAlf9X/6P/PAC1ANoAmgAIAJr/ov/M/9P/AQBxALYAgwD2/33/ef/a/z4AbQByAHAAZgA4AOv/mf9m/5j/NADGAOwApAAVALL/wP/c/77/xv8hAIoA0AC+AC4AiP9e/6n/+v8pAFIAbwB+AIgAXwDm/3b/dP/X/2IAuACdAGEARAD//4//Z/+a//H/bgDWAKkADACq/7r/7P8EAAEADABLAIQAZgAYANr/pP+k/w8AgwCaAHoAUAAWAMj/Zf84/7r/qwAmAdAAHwCZ/3T/uf8sAF8ARABKAIQAfQAVAKj/dP+a/xEAegCIAFQAGwANABgA6/+T/5X//P9eAIkAcAAOAK7/mf+l/5f/qP8GAHQAsQCgAB4Acf86/4n/3f8WAFQAbQBPAB4A0f9f/xj/UP/5/5cArgBKAM//bf85/2L/5/9uAK0AkwAjAIv/N/9i/8r/KABrAIEAVwAAAK3/jP+g/8P/AQBrAKYAbQAGAMf/rf+0//P/UACTAJ0AZgDs/33/ff/N/w8ANAA2AAYA0//P/+D/6P/3/xoAUwBwADkA1P+R/4f/uP8tAKEApAA6AM//kP9d/1j/tP8tAGgAcwBfABoAx/+X/5j/2/8+AFgAFQDb/9D/yf/F/+T/FwA0AC4AGwAKAPD/zP++/+P/KQBfAF4ALwD6/83/rv+6/+//FgAkADQALAD5/9H/0v/W/97/DABOAGkASwAVAOH/rf+d/9T/GQArACoAOQAzAAgA1f+q/5z/xf8bAGEAbABQABoAvf9t/4H/1v8hAGcAjQBXAPn/1v/j/+n/8v8GABsAOABiAHMARwAEAOf/8P8RAEsAcQBSABsAEgAdAP//3v8DAFIAcgBcAD8AGQDn/+P/IQBYAGYAdQB1ADkA9v/v/wUAIABWAIsAiABgAEEAMAASAN7/xf/5/08AigCmAI4AIQCZ/2X/pv8bAIEAqgB+AC8AEAAVAAkADwA0ADYAKwBSAGgAMgAHABIAIAAuAEQANQAXAD0AiwCQAEYAAADf//b/UwCjAIEAOAA3AFMASwAsAPz/0f/8/3UAuwCNADIA+P/q//H/AQArAHIAqwCmAGAA7f9//4L/FwC8AOEAjwAxAAsAEgARAPX/5P8TAH4AygClAB8AmP9s/7n/NAB/AJcAoQCWAF4A+v+e/6f/HgCZAMMAlQAuAN3/0v/h/93/5v8wALIACwHaAD4Ar/+E/9L/XQC6AKYAUQAiADMAJwDO/5f/2v9RAK4A0ACDAOv/nf/c/zYASwBBAE4AWABHACgA9f+2/7D/AABbAHkAXwAqAPz/9P8SACsAJAAiAEQAcABtADAA9P/x/yEAXACAAGUAGgD7/x4AOgA0ACkAHAAZADMASQAkAOD/1v8gAG0AdQBAAP7/3v///yoALQAmACkAJgAyAEwAOAAAAPL/IgBWAEwACgDZ/+H/EAA2ACgAAQAaAF8AVgD6/7r/xv/4/zAAXQBcACAA5//l//n/9f/v/wYAPgBvAFUA6f+E/3L/nv/h/xYAJAAqAEoASQD1/5v/kP/M/yoAgQBzAPf/lf+b/9f/GgBLAEUAKQAsACUA5f+p/7H/6v8oAFMAQAD9/93/7//m/9P/8/8TABgAQwBwAFAADADh/8f/3/8lAD0ADQDq/+n/3//V/+7/BQAAABEARgBEAAoA8f/u/9r/5f8jAE4ARQAoABoAEADp/7X/w/8gAHoAkgBwACoA2v+l/7f/AAA5AD0AOQBCAC8A9v/P/+P/DQAhACgALgAnABEA9//f/9P/6f8kAGUAcAAzAOD/uP/K//D/BgAMAAkABAAQACcAFADd/7//y//s/xQAKAAXAPn/5f/s/wkAGAAYACQAHgDh/53/kf++//b/GgAhAP3/s/+M/7H/8f8iAEEAIQDM/6H/xv8IADEAIQDd/6b/sf/g//f/6v/i//b/DwAfAA4Azf+D/3T/q/8CAE0AXgA2APz/uv93/17/kP/0/1QAfgBNAOT/kP92/43/0/8mAEoAOQAWANT/hv96/7P/6/8WAEIAQQAMAOr/6v/V/77/7P8qACEA+v/o/93/7P8JAOP/nf+5/xwARwAjAN3/mP+F/8L/IABLACMA3f/G/+3/EwD2/7f/uf8AADwASwAmAMz/jf+u/+j/9v/7/xkASQBrAFkAEADJ/6n/s//f/xEAKQAzAEcASQAUAND/tP/F/+//IQAvAAkA6f/k/9b/vf/A/9z/AAAsAFAARAAIAMP/lv+o//7/TQBaAD4AGwDq/7j/pP+s/87///8hADIAKQDu/5j/d/+m//b/LQA7AC4ABQDP/7f/v//M//L/NwBiAEUA6/+N/3L/oP/h/xoAQQA9ABwA8/+y/2z/Xf+a//v/PQBBACQAAADW/7b/r/+5/+H/KgBbADkA4v+T/4D/uf8gAGgASwDh/43/hv+r/9v/EAA7AEEAHwDt/8H/sP+7/9n///8NAP7//f8cABoA2/+x/87///8SABoAGgDy/7X/tP/4/yQAHQAaABsA/P/e/+D/7v/+/w8AFAAUABcAAQDN/6f/v//7/yMANQBCADQABQDg/83/xv/U/+3/AAAVACgAGADh/6z/sf/t/xEACQARACgAGADt/9f/2P/l/wUAMgBDAB0A6f/P/8T/yf/v/xwANABBADMAAADZ/93/6P/w//7/+//l/9r/3P/L/7L/uf/q/yUATABBAPr/lv9i/4//+f9CAEMAJgAMAO//0v+5/6f/u/8AAEMAVgAnAMz/gv+D/7//+P8GAPf/6P/g/8//u/+o/6P/xf8BACMACADC/4n/mf/h/xsAIgAMAAYAGwASAMv/hP+C/7z/CAA7ACIA0f+R/43/qf+8/8X/2f/8/x8AKQD3/5v/cf+s/w0ATABQAB8A3f+5/7b/sv+1/97/HQA6ABkA2f+x/7j/2//4//b/1v/F/+n/GQAaAO3/uv+u/+H/GwAcAPj/5P/h/+j/+f/8/+r/6P8AAA0ABAACAP//7f/0/w8AAQDT/8n/7P8YADIAJQABAO3/4//e/+3/AAABAAEABwAAAN//wP/J/+///f/8//z/3P+r/7H/5/8QACEAFwD6/+3/9v/y/+D/4P/w/wEAFgAfAAIA0P+w/63/vf/h/w8AMAArAAYA2//D/8H/1f/z//f/2v/D/83/+P8iAB8A8f/M/8D/xv/l/wwAGQAIAPb/8f/q/9T/y//n/wgAIQAqAAgA1v/N/+L/8f/5//7/AAD+//j/BgAkABsA9v/r//r/BgAAANb/sf/D//H/IABVAGMANQAJAPX/2P+//8v/9P8fAEIAUQA5AAMA4v/m//b/DAAgACAAJgAyAAoAvf+o/+H/MABpAGwAMwDp/8X/3P8PADgATQBPADgAFwD4/9z/4v8XAE8AZQBVACEA8f/5/xQADAAHACYAPQBAAEkAOwAKAO3/9P8CABMAJQAsACYAFAD///r/BgAgAEQATwAtAAsACAARAB0AJQAiAB8AGgAIAPj/+/8QACcAMAAwACcABgDs//7/GgAWAA0AHgA6AEEALwAaABAACwAbAD0APQAZAAcAEQAbABsAGgAtAEcAQQAvACoAHgAbAD4AWAA/ABUAAAAEACAAQwBfAF8AOgAOAPj/9f8BABUAIwA0AEAAKwAQABQAJwA2AEEAQwA8ACwACQDq/+//GABKAGAAUAAuAA0A9f/w//r/AgASADEATQBSADYABQDc/87/3v/9/xYALwBDADkAGAAAAPT/8P8AACQARABMADcAGAD9/9n/w//e/xQAQQBVADcA6/+o/6H/y//6/xcAKgA3ADUAIgADAOD/xf/I/+//KQBSAFYAOQAHANv/xv/H/9//FwBQAFwANQDy/7b/o//E/woASwBZADcADgDt/9X/1f/p/w4ARwBsAFYAIQDx/8f/vP/o/ysAUABPAD8AJQD6/8//xP/a/wAAJwBCADwAGAD4/+j/2f/M/9L/6v8IACAAHQAAANn/vf/J/+7//f/6//7//P/6/wQA/P/W/8X/0v/e/+T/6P/g/8T/q/+6/+P/+v/7//X/2v/B/8T/y//G/8b/xf/C/8z/4f/o/9n/xP+7/7n/vf/S/93/0P/R/+f/5P/Q/8P/uv/D/93/6f/t/+//1/+1/6r/r//E/+f/AgAKAPj/zv+0/7n/xv/T/9z/2P/X/9//2f/U/9v/0v++/8P/1P/U/8v/xP/B/8P/z//g/+T/2v/W/9f/y//A/8H/xP/E/87/2//m/+7/3v+7/7H/yf/Y/9P/1//n/+v/4v/Y/9D/xv/I/93/6v/j/+b/8//n/9H/z//M/8T/0v/t//n/9v/r/9b/wv+9/8T/1P/z/xkAJAAFANn/tv+0/97/BwAHAPL/5P/f/+P/4f/N/8z/7P8UADAAIgDh/5n/gf+g/9//CAAFAPz/8f/U/8j/1v/T/83/4v///xAACQDb/7H/wP/q/wUAGQAhAAUA1v+6/8L/3f/5/wUA/v/z/+7/4P/M/8r/2f/x/wYABgD1/+T/1//V/+r/+//9/wAAAQDx/9b/x//T/+3/AAAOABUA/v/V/8X/y//S/97/9f8MABoAEADr/73/qf+///D/GAAcAPn/0P++/7T/tf/Y/wAAEQATAP3/xf+c/6T/wv/i//7/AADp/9P/z//E/6b/mP+6/+//BQD2/9b/u/+2/8n/5v/v/9j/yf/h//z/8v/K/6z/v//8/xgA+P/J/7z/0P/y/wQA9//U/77/0P/+/xEA9P/Q/9H/7P8CAAMA8P/m//b//P/n/9b/0//b//P/AwD3/+n/7P/z//n/7//X/93/BQASAAAA6//W/9L/8v8MAPv/1//L/+T/BAD//9j/xv/l/w4AFAD5/9n/vf+7/+j/EAAJAPL/7f/7/wUA9P/T/9L/6/8AAA8ACgD0/+j/5P/i/+z/9f/6/xEAFwDz/9P/yv/S//n/HgAVAAAA9v/k/9v/6v/z//n/CgAOAPb/4f/p//n/+v/6//3/7f/b/+r//P/9/wgAEAD6/9n/w/+1/7//5/8MABgABwDu/+P/6//v/+P/1v/f//7/EwAPAP//5P/M/9H/6//5//7/CAAHAPL/4f/Z/9P/2//y////AgAOABQA///Z/8L/y//w/xsAMQAoAAgA4P/B/8T/3//4/w4AKgA1ABwA5/+t/5T/rf/f/w8ALwApAAkA6P+5/5n/tf/y/yIARwBGABUA7//k/9j/1//1/yAARgBOADAAAgDZ/7v/wf/p/w8AJQAqACMAEgDw/8j/wP/f/wgAJgAvACAACAD8/wMADAAJAAoAGQAjAB0A///Z/9n/9f////3/AwABAAAAEQAdAAsA8P/e/+X/AgAeACEAEwAIAAkADAAEAPn/9v8DACIAOAAoAPn/y//F//H/IgAuACYAIQAeABQAAQDn/9H/1f8AAD4AXgBLABYA5P/Z//T/CQAIAAYADgAfAD0ASwAtAPv/4v/r//v/DAArAD0AIwD8//D/+P8DABcAKQAyAC4AGgAFAAIACwAVACIAKwApAB8AEgAKAA4AGAAgAC0APQBBADQAGgD8/+b/6/8GACsARgBGADQAHwAJAPj//P8VADMASwBWAEQAIAAEAPz//v8GABgAKgAxAC0AIwAOAP7/AgATAB0AJAAqACsAJQAWAP//8/8AABsANQA4AB0A+f/n//f/GAAsADEALAAaAA0AEAAJAPX/9f8LAB8AIwAbAAwA/v/1//n/BQAPABsAJgAiABMABQD0/+v//f8WACQAJgAdABIADAAFAP//AgAJAAsAEQAaABoAGQAXAA4AAgAAAAcADwAQAA0ABgD9//v/BwATAA8AAwD8//j//P8DAAYABAAHAA4ADwAJAAEA+//5/wAABwAFAAAAAAACAAQABAD+//T/8f/4/wAABQADAPz/+f/9/////P/7//3/AAAAAAAA/f/8/wAABAAGAAEA+//3//j//f8BAAAA/f/8////AAAAAP7/+//7//3///8AAAAA/v/8//z//f/+////AAAAAAAA//////7///8AAAAAAAAAAAAAAAAAAAAA"};
async function __bjAudioAsset(file){const data=__bjAudioAssets[file];return {ok:typeof data==='string',async arrayBuffer(){return Uint8Array.from(atob(data),c=>c.charCodeAt(0)).buffer;}};}
const __bjSoundEngine=(()=>{

// Earlier synth drafts remain identifiable for reading old recipes.
function createSynthSound(onState) {
  let context,active=[];
  return {
    stop(){for(const node of active){try{node.stop();}catch{}}active=[];},
    async play(recipe, edge='down') {
      const s=recipe.settings;
      if(s.sound==='off'||s.volume===0)return;
      try {
        const Constructor=window.AudioContext||window.webkitAudioContext;
        if(!Constructor)throw new Error('Audio wird in diesem Browser nicht unterstützt.');
        context ||= new Constructor();
        if(context.state!=='running')await context.resume();
        if(context.state!=='running')throw new Error('Der Browser hat den Klang noch nicht freigegeben.');
        const material=s.sound==='material'?s.material:s.sound;
        const now=context.currentTime;
        const gain=context.createGain();
        const peak=s.volume/100*(edge==='down'?.18:.09);
        const duration=material==='metal'?.16:material==='wood'?.075:.045;
        gain.gain.setValueAtTime(.0001,now);
        gain.gain.exponentialRampToValueAtTime(Math.max(.0002,peak),now+.003);
        gain.gain.exponentialRampToValueAtTime(.0001,now+duration);
        gain.connect(context.destination);
        const base={wood:180,stone:730,metal:1050}[material]*(edge==='up'?1.42:1);
        for(const ratio of material==='metal'?[1,1.61]:[1]) {
          const oscillator=context.createOscillator();
          oscillator.type=material==='metal'?'sine':'triangle';
          oscillator.frequency.setValueAtTime(base*ratio,now);
          oscillator.frequency.exponentialRampToValueAtTime(base*ratio*.63,now+duration);
          oscillator.connect(gain);oscillator.start(now);oscillator.stop(now+duration+.01);active.push(oscillator);
        }
        const buffer=context.createBuffer(1,Math.ceil(context.sampleRate*duration),context.sampleRate);
        const samples=buffer.getChannelData(0);
        for(let i=0;i<samples.length;i++)samples[i]=(Math.random()*2-1)*.16;
        const noise=context.createBufferSource();noise.buffer=buffer;
        const filter=context.createBiquadFilter();filter.type='lowpass';filter.frequency.value=material==='wood'?650:material==='stone'?2600:4000;
        noise.connect(filter);filter.connect(gain);noise.start(now);noise.stop(now+duration);active.push(noise);
        onState(`Alter synthetischer Platzhalter · ${material==='wood'?'Holz':material==='stone'?'Stein':'Metall'} · ${s.volume} %`);
      } catch(error) {onState(error.message);}
    },
  };
}

// Local source recordings: one short shot on press; release never doubles it.
function createSound(onState,onPlay=()=>{},assetBase='/assets/audio/'){
  const records=new Map(),buffers=new Map(),synth=createSynthSound(onState);
  let context,source,sequence=0;
  function stop(){sequence++;try{source?.stop();}catch{}source=null;synth.stop();}
  return {
    configure(rows){for(const row of rows)records.set(row.id,row);},stop,
    async play(recipe,edge='down'){
      const s=recipe.settings;if(s.sound==='off'||s.volume===0)return;
      if(edge!=='up')onPlay();
      const id=s.sound==='material'?{wood:'wood-plank','wood-aged':'wood-plank',stone:'stone-scrape',metal:'robot-step'}[s.material]:s.sound;
      if(s.sound==='material'&&!id){if(edge!=='up')onState('Dieser Fläche ist kein Materialklang zugeordnet. Wähle bei Bedarf einen Klang aus.');return;}
      if(['wood','stone','metal'].includes(id)){stop();return synth.play(recipe,edge);}
      if(edge==='up')return;
      const record=records.get(id);if(!record){onState('Dieser Klang ist nicht verfügbar.');return;}
      stop();const ticket=sequence;
      try{
        const Constructor=window.AudioContext||window.webkitAudioContext;
        if(!Constructor)throw new Error('Audio wird in diesem Browser nicht unterstützt.');
        context ||= new Constructor();await context.resume();
        if(context.state!=='running')throw new Error('Der Browser hat den Klang noch nicht freigegeben.');
        if(!buffers.has(id))buffers.set(id,__bjAudioAsset(record.file).then(async response=>{
          if(!response.ok)throw new Error('Die lokale Klangdatei konnte nicht geladen werden.');
          return context.decodeAudioData(await response.arrayBuffer());
        }).catch(error=>{buffers.delete(id);throw error;}));
        const buffer=await buffers.get(id);if(ticket!==sequence)return;
        const offset=Math.min(record.button_offset,Math.max(0,buffer.duration-.02));
        const duration=Math.min(record.button_duration,buffer.duration-offset),now=context.currentTime;
        const gain=context.createGain(),peak=s.volume/100*.65;
        gain.gain.setValueAtTime(0,now);gain.gain.linearRampToValueAtTime(peak,now+.006);
        gain.gain.setValueAtTime(peak,now+Math.max(.007,duration-.025));gain.gain.linearRampToValueAtTime(0,now+duration);
        gain.connect(context.destination);source=context.createBufferSource();source.buffer=buffer;
        source.connect(gain);source.start(now,offset,duration);source.onended=()=>gain.disconnect();
        onState(`${record.name} · kurzer Buttonausschnitt · ${s.volume} %`);
      }catch(error){onState(error.message);}
    },
  };
}

return {createSound};
})();
const __bjPlayers=(()=>{

// One compact player component. Games supply public data, never their own markup.
function createPlayerPortrait(host) {
  const make = (tag, className) => {
    const node = document.createElement(tag);
    node.className = className;
    return node;
  };
  const root = make('div', 'player-portrait');
  const stats = make('div', 'player-portrait-stats');
  stats.hidden = true;
  const statViews = ['troops', 'countries'].map((key, index) => {
    const row = make('span', 'player-portrait-stat');
    const symbol = make('span', 'player-portrait-stat-icon');
    symbol.setAttribute('aria-hidden', 'true');
    symbol.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' + (index === 0
      ? '<circle cx="12" cy="4" r="2"/><path d="m8 9 4-2 4 2m-4-2v8m-4 6 4-6 4 6M8 9l-2 5m10-5 2 5"/>'
      : '<path d="m3 8 6-4 6 3 6-3v15l-6 3-6-3-6 3zm6-4v15m6-12v15"/>') + '</svg>';
    const value = make('strong', 'player-portrait-stat-value');
    row.append(symbol, value); stats.append(row);
    return {key, row, value};
  });
  const frame = make('span', 'player-portrait-frame');
  const image = make('img', 'player-portrait-image');
  const fallback = make('span', 'player-portrait-fallback');
  fallback.setAttribute('aria-hidden', 'true');
  frame.append(image, fallback);
  const copy = make('div', 'player-portrait-copy');
  const status = make('span', 'player-portrait-status');
  const name = make('strong', 'player-portrait-name');
  const metrics = make('span', 'player-portrait-metrics');
  const wallet = make('div', 'player-portrait-wallet');
  const walletValues = ['balance', 'wager', 'gain'].map((key, index) => {
    const item = make('span', 'player-portrait-wallet-item');
    const label = make('small', 'player-portrait-wallet-label');
    label.textContent = ['Bestand', 'Einsatz', 'Gewinn'][index];
    const amount = make('strong', 'player-portrait-wallet-value');
    item.append(label, amount); wallet.append(item);
    return {key, amount, label};
  });
  wallet.hidden = true;
  copy.append(status, name, metrics, wallet);
  const badge = make('button', 'player-portrait-badge');
  badge.type = 'button'; badge.hidden = true;
  let openCards = null;
  badge.addEventListener('click', () => openCards?.());
  root.append(stats, frame, copy, badge);
  host.replaceChildren(root);
  image.addEventListener('error', () => { image.hidden = true; fallback.hidden = false; });
  return {
    get anchor() { return frame; },
    focusCards() { badge.focus(); },
    update(player) {
      name.textContent = player.name;
      name.title = player.name;
      status.textContent = player.status || '';
      status.hidden = !player.status;
      metrics.textContent = player.metrics || '';
      metrics.hidden = !player.metrics;
      metrics.title = player.metricsDescription || '';
      wallet.hidden = !player.wallet;
      root.dataset.wallet = String(Boolean(player.wallet));
      metrics.hidden = Boolean(player.wallet) || !player.metrics;
      if (player.wallet) {
        for (const {key, amount, label} of walletValues) {
          if (key === 'balance') label.textContent = 'Bestand' + (player.wallet.unit ? ' · ' + player.wallet.unit : '');
          const value = player.wallet[key];
          amount.textContent = value == null ? '—' : (key === 'gain' && value > 0 ? '+' : '') + Number(value).toLocaleString('de-DE');
          amount.dataset.sign = key === 'gain' && value != null ? (value > 0 ? 'positive' : value < 0 ? 'negative' : 'neutral') : 'neutral';
        }
      }
      root.dataset.kind = player.kind || 'player';
      root.dataset.layout = player.layout || 'default';
      root.dataset.current = String(Boolean(player.current));
      stats.hidden = !player.stats;
      for (const item of statViews) {
        const value = player.stats?.[item.key] ?? 0;
        const label = item.key === 'troops' ? 'Truppen' : 'Länder';
        item.value.textContent = Number(value).toLocaleString('de-DE');
        item.row.title = value + ' ' + label;
        item.row.setAttribute('aria-label', value + ' ' + label);
      }
      badge.hidden = player.cardCount == null;
      badge.textContent = String(player.cardCount ?? '');
      openCards = player.onCards || null;
      badge.disabled = !openCards;
      badge.title = player.name + ': ' + player.cardCount + (player.cardCount === 1 ? ' Länderkarte' : ' Länderkarten');
      badge.setAttribute('aria-label', badge.title + (openCards ? ' · eigene Karten ansehen' : ''));
      root.style.setProperty('--player-color', player.color || '#d8ff42');
      fallback.textContent = Array.from(player.name || '?')[0];
      const portrait = player.portrait;
      if (portrait?.url) {
        if (image.getAttribute('src') !== portrait.url) {
          image.hidden = false;
          fallback.hidden = true;
          image.src = portrait.url;
        }
        image.alt = `${portrait.alt} von ${player.name}`;
        root.style.setProperty('--portrait-scale', String(portrait.crop?.scale || 1));
        root.style.setProperty('--portrait-top', `${portrait.crop?.top || 0}%`);
      } else {
        image.removeAttribute('src');
        image.hidden = true;
        fallback.hidden = false;
        image.alt = '';
      }
    },
  };
}

return {createPlayerPortrait};
})();
const recipe={"schema_version": 2, "renderer_version": "button-workshop-v7", "contour": {"template": "soft", "points": [{"x": 0, "y": 0, "round": 40}, {"x": 100, "y": 0, "round": 40}, {"x": 100, "y": 100, "round": 40}, {"x": 0, "y": 100, "round": 40}]}, "name": "vorschlag black Jack button – kompakt", "notes": "Kompakte Tischversion: 204 px breit, ca. 71 px hoch; Cinzel 20,4 px. Auch lange Beschriftungen bleiben zweizeilig lesbar. Dunkles gealtertes Nussbaumholz, Druckbewegung und Klang vom bisherigen Vorschlag erhalten.", "settings": {"style": "natural", "material": "wood-aged", "shape": "soft", "edge": 2, "finish": "matte", "wear": 30, "accent": "#23150e", "font": "cinzel", "font_link": "manual", "lettering": "plain", "size": 17, "label": "Neue Runde", "depth": 3, "duration": 180, "feel": "direct", "sound": "media-piece", "volume": 25, "gradient_to": "#b68b4c", "opacity": 100, "font_scale": 120, "shadow": 25, "height_ratio": 104, "ink_mode": "manual", "ink_color": "#d2b779", "depth_mode": "manual", "depth_color": "#160e09", "depth_x": 1, "font_italic": false}, "kind": "button", "review": {"style": "open", "motion": "open", "shape": "open", "surface": "open", "lettering": "open", "sound": "open"}, "parent_id": "656dbd73ec9c45a1b86791b2e3a0fcb0", "id": "17476727364949609038305dee84e91f", "created_at": "2026-10-30T19:20:14.320644+00:00"};
const renderButton=__bjMedia.renderButton, createSound=__bjSoundEngine.createSound, createPlayerPortrait=__bjPlayers.createPlayerPortrait, audioRecords=__bjAudioRecords;
export {recipe,renderButton,createSound,createPlayerPortrait,audioRecords};
