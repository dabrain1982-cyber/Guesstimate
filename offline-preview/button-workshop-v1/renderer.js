import {button} from './components.js';
let sourceRenderer=null;
// Workshop-only adapter: existing game consumers keep the same dependencies and behavior.
export function registerSourceRenderer(render){sourceRenderer=render;}
import {toPolygon,outlinePath,contourPlane,CONTOUR_PLANE,CONTOUR_ASPECT,buttonMetrics,BUTTON_WIDTH_UNITS} from './geometry.js';
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

export function materialize(element, recipe, {tintStrength=null,textureUrl=null}={}) {
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

export function renderButton(host, recipe, {state='normal',label,symbol,action=()=>{},sound=null,size=null,tintStrength=null,textureUrl=null}={}) {
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
