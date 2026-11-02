// Opt-in editor/library extension. Games retain their unchanged original renderer.
import {renderButton as originalRender,materialize as originalMaterialize,registerSourceRenderer} from './renderer.js';
export {registerSourceRenderer};
export const matchedFont=font=>typeof font==='string'&&font.startsWith('media-')?font.slice(6):null;
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
export function materialize(element,recipe,options){originalMaterialize(element,previewRecipe(recipe),options);applyStyle(element,recipe);}
export function renderButton(host,recipe,options={}){
  const view=originalRender(host,previewRecipe(recipe),options);
  applyStyle(view.element,recipe);
  const label=view.element.querySelector('.comic-button-label'),doc=view.element.ownerDocument;
  if(label&&doc.fonts){const css=doc.defaultView.getComputedStyle(label),family=css.fontFamily.split(',')[0];
    doc.fonts.load(css.fontStyle+' '+css.fontWeight+' '+css.fontSize+' '+family,label.textContent).then(()=>{if(view.element.isConnected)view.label(options.label||recipe.settings.label);}).catch(()=>{});
  }
  return view;
}
