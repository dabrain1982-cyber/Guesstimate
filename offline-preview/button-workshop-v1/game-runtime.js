import {renderButton} from './media-renderer.js';
import {createSound} from './sound.js';

// Keep native actions, form fields, listeners and changing game labels on the
// original element. The visible proxy uses the very same workshop component.
const mounted=new Map(),sound=createSound(()=>{});
let current={bindings:{},recipes:{}},signature='',queued=false,styles;
function loadStyles(){
  if(styles)return styles;
  const names=['../shared/comic-button.css','materials.css','fonts.css','matched-media.css','game-runtime.css'];
  styles=Promise.all(names.map(name=>new Promise((resolve,reject)=>{
    const link=document.createElement('link');link.rel='stylesheet';link.href=new URL(name,import.meta.url);
    link.onload=resolve;link.onerror=()=>reject(Error('Buttonstil konnte nicht geladen werden.'));document.head.append(link);
  })));
  return styles;
}
function labelOf(element){
  const copy=element.cloneNode(true);
  for(const child of copy.querySelectorAll('[aria-hidden="true"],[hidden],svg,img,.comic-icon'))child.remove();
  return copy.textContent.replace(/\s+/g,' ').trim()||element.getAttribute('aria-label')||'Aktion';
}
function restore(original,record){
  original.classList.remove('workshop-button-original');record.host.remove();mounted.delete(original);
}
function synchronize(original,record){
  const label=labelOf(original);
  if(label!==record.label){record.view.label(label);record.label=label;}
  const element=record.view.element;
  element.disabled=!!original.disabled||original.getAttribute('aria-disabled')==='true';
  element.hidden=original.hidden;
  const selected=original.getAttribute('aria-pressed')??original.getAttribute('aria-selected');
  if(selected!==null)element.setAttribute('aria-pressed',selected);else element.removeAttribute('aria-pressed');
  if(original.title)element.title=original.title;else element.removeAttribute('title');
  if(original.getAttribute('aria-label'))element.setAttribute('aria-label',original.getAttribute('aria-label'));
}
function scan(){
  queued=false;
  for(const [original,record]of mounted){
    const identifier=current.bindings[original.dataset.workshopModel];
    if(!original.isConnected||identifier!==record.id)restore(original,record);
  }
  for(const original of document.querySelectorAll('[data-workshop-model]')){
    const id=current.bindings[original.dataset.workshopModel],recipe=current.recipes[id];
    if(!recipe)continue;
    if(mounted.has(original)){synchronize(original,mounted.get(original));continue;}
    const width=original.getBoundingClientRect().width;if(!width)continue;
    const label=labelOf(original),design=structuredClone(recipe);design.settings.label=label;
    const host=document.createElement('span');host.className='workshop-bound-host';host.style.width=width+'px';
    original.before(host);
    try{
      const view=renderButton(host,design,{label,size:23*width/(design.base?.width||276),sound,
        action:event=>{
          event.preventDefault();event.stopPropagation();original.click();
        }});
      const record={host,view,id,label};mounted.set(original,record);
      original.classList.add('workshop-button-original');synchronize(original,record);
      view.element.dataset.workshopRecipe=id;
    }catch(error){host.remove();console.error('Buttonmodell konnte nicht eingesetzt werden.',error);}
  }
}
function schedule(){if(!queued){queued=true;requestAnimationFrame(scan);}}
new MutationObserver(changes=>{
  if(changes.some(change=>!change.target.closest?.('.workshop-bound-host')))schedule();
}).observe(document.body,{subtree:true,childList:true,attributes:true,attributeFilter:['class','hidden','disabled','aria-disabled','aria-pressed','aria-selected','style','title']});
async function refresh(){
  try{
    const response=await fetch(new URL('../_local/button-models',import.meta.url),{cache:'no-store'});
    if(!response.ok)return;
    const data=await response.json(),next=JSON.stringify(data);
    if(next===signature)return;
    if(Object.keys(data.bindings).length)await loadStyles();
    current=data;sound.configure(data.sounds||[]);signature=next;schedule();
  }catch(error){console.warn('Die lokale Buttonzuordnung ist gerade nicht erreichbar.',error);}
}
refresh();setInterval(refresh,2000);
