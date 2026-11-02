
const views=new WeakMap();
export function setActionLabel(element,label){
  const view=views.get(element);
  if(view)view.label(label);else element.textContent=label;
}
export function finishActionPress(element,action){
  const duration=views.get(element)?.duration||0;
  if(duration)setTimeout(action,globalThis.matchMedia?.('(prefers-reduced-motion: reduce)').matches?120:duration);
  else action();
}
export async function mountConquestButtons(){
  const [{renderButton},{createSound}]=await Promise.all([import('./button-renderer.js'),import('./button-sound.js')]);
  const {icon}=await import('./components.js');
  for(const choice of document.querySelectorAll('[data-dice-count]'))choice.replaceChildren(icon('dice'));
  const read=async path=>{const response=await fetch(new URL(path,import.meta.url));if(!response.ok)throw new Error('Der gespeicherte Buttonentwurf konnte nicht geladen werden.');return response.json();};
  const [recipe,catalog]=await Promise.all([read('./button-profile.json'),read('./button-assets/audio/catalog.json')]);
  const sound=createSound(()=>{},()=>{},new URL('./button-assets/audio/',import.meta.url).href);sound.configure(catalog.sounds);
  const textureUrl=new URL('./button-assets/slate-v1.png',import.meta.url).href;
  for(const id of ['next-phase','confirm-deployment','roll-attack','notice-open-cards','trade-cards','play-again','accept-mission']){
    const old=document.getElementById(id),host=document.createElement('div');
    const view=renderButton(host,recipe,{label:old.textContent,size:16,sound,textureUrl,state:old.disabled?'disabled':'normal'});
    if(id==='next-phase'||id==='roll-attack'||id==='confirm-deployment'||id==='trade-cards')view.element.style.fontSize='1em';
    for(const attribute of old.attributes)if(attribute.name!=='class')view.element.setAttribute(attribute.name,attribute.value);
    view.element.dataset.recipe=recipe.source_id;
    old.replaceWith(view.element);views.set(view.element,{...view,duration:recipe.settings.duration});
  }
}
