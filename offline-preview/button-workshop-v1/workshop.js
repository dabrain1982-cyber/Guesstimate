import {renderButton,materialize,registerSourceRenderer} from './media-renderer.js';
import {isSourceRecipe,renderSourceButton} from './source-renderer.js';
import {captureButton,recipeFromProfile} from './unified-import.js';
registerSourceRenderer(renderSourceButton);
import {createSound} from './sound.js';
import {ContourEditor} from './contour-editor.js';
import {makeContour,outlinePath,contourPlane} from './geometry.js';
import {applyMatchingFont} from './font-matching.js';
import {ButtonUsageDialog} from './button-usage.js';

const $=selector=>document.querySelector(selector);
const clone=value=>structuredClone(value);
const embedding=new URLSearchParams(location.search).get('embedded')==='1'&&window.parent!==window;
function notifyWorkshop(type,detail={}){if(embedding)window.parent.postMessage({channel:'stormseed-elements',type,...detail},location.origin);}
if(embedding){document.body.classList.add('embedded');const css=document.createElement('link');css.rel='stylesheet';css.href='embedded.css';document.head.append(css);}
let catalog,current,pinned,saved=[],savedFingerprint='',saving=false,savingShape=false,activeShapeId=null;
const controls=new Map(),reviews=new Map();
const audioPlayers=new Map(),soundChoices=new Map();
const sound=createSound(message=>{$('#sound-state').textContent=current?.settings?.sound?.startsWith('media-')?message.replace('kurzer Buttonausschnitt','vollständige kurze Probe'):message;},()=>{for(const player of audioPlayers.values())player.pause();});
const fingerprint=()=>JSON.stringify({name:current.name,settings:current.settings,contour:current.contour,review:current.review,notes:current.notes,source_button:current.source_button,appearance:current.appearance,base:current.base});
function toolButton(label,action,primary=false){
  const element=document.createElement('button');element.type='button';element.className='workshop-action'+(primary?' primary':'');element.textContent=label;element.addEventListener('click',action);
  return {element,label:text=>{element.textContent=text;}};
}
const ui=(host,label,action,options={})=>{const view=toolButton(label,action,options.primary);$(host).replaceChildren(view.element);return view;};
let saveView,shapeSaveView,contourEditor,usageView,usageDialog;
function initPreviewBackground(){
  const select=$('#preview-background'),color=$('#preview-background-color'),stage=$('.live-plinth');
  const modes=['light','checker','dark','custom'];
  let preference={mode:'light',color:'#e4e6e9'};
  try{
    const stored=JSON.parse(localStorage.getItem('button-preview-background'));
    if(stored&&modes.includes(stored.mode)&&/^#[\da-f]{6}$/i.test(stored.color))preference=stored;
  }catch{}
  const apply=()=>{
    stage.dataset.previewBackground=preference.mode;
    const background=preference.mode==='dark'?'#293c3c':preference.mode==='custom'?preference.color:'#e4e6e9';
    const rgb=background.slice(1).match(/../g).map(value=>parseInt(value,16)/255);
    const light=rgb[0]*.2126+rgb[1]*.7152+rgb[2]*.0722;
    stage.style.setProperty('--preview-background',background);
    stage.style.setProperty('--preview-ink',light>.5?'#35434b':'#fff7e3');
    select.value=preference.mode;color.value=preference.color;color.closest('label').hidden=preference.mode!=='custom';
  };
  const savePreference=()=>{apply();try{localStorage.setItem('button-preview-background',JSON.stringify(preference));}catch{}};
  select.addEventListener('change',()=>{preference.mode=select.value;savePreference();});
  color.addEventListener('input',()=>{preference.color=color.value;savePreference();});
  apply();
}
const steps=['Form','Oberfläche & Farbe','Beschriftung','Bewegung & Ton','Speichern'];
let editorStep=0,previousDraft=null;
function showStep(index){
  editorStep=Math.max(0,Math.min(steps.length-1,index));
  for(const panel of document.querySelectorAll('[data-editor-step]'))panel.hidden=Number(panel.dataset.editorStep)!==editorStep;
  for(const button of document.querySelectorAll('[data-step-button]')){
    const selected=Number(button.dataset.stepButton)===editorStep;
    if(selected)button.setAttribute('aria-current','step');else button.removeAttribute('aria-current');
  }
  $('#settings-title').textContent=(editorStep+1)+' · '+steps[editorStep];
  $('#step-back').disabled=editorStep===0;
  $('#step-next').hidden=editorStep===steps.length-1;
  $('#step-next').textContent='Weiter: '+(steps[editorStep+1]||'Speichern')+' →';
  $('#step-description').textContent=[
    'Beginne mit Umriss, Rundungen und Größe. Tiefe 0 ergibt einen flachen Button.',
    'Wähle Fläche, Farben und Glanz. Die Seitenwand gehört zur Tiefe, der Schlagschatten ist unabhängig davon.',
    'Wähle Text, Schriftart und Schriftfarbe. Fett und Kursiv kannst du einzeln einschalten.',
    'Probiere Druckbewegung und Klang am großen Button aus.',
    'Gib deinem Entwurf einen Namen. Speichern legt einen eigenen Stand in deiner Bibliothek an.'
  ][editorStep];
  if(editorStep!==3){sound.stop();for(const player of audioPlayers.values())player.pause();}
}
function newRecipe(){return builtin({name:'Mein neuer Button',settings:{style:'minimal',material:'plain',shape:'soft',accent:'#47745f',finish:'matte',wear:0,font:'letter-clear',font_link:'manual',lettering:'plain',ink_mode:'manual',ink_color:'#fff5db',depth_mode:'manual',depth_color:'#284438',depth:0,shadow:0,edge:0,label:'Mein Button',sound:'off'}});}
async function startNew(){
  if(current){previousDraft={recipe:clone(current),savedFingerprint,url:location.href};try{sessionStorage.setItem('button-previous-draft',JSON.stringify(previousDraft));}catch{}}
  const url=new URL(location.href);url.searchParams.delete('source_button');url.searchParams.delete('recipe');url.searchParams.set('new','1');history.replaceState(null,'',url);
  sound.stop();await load(newRecipe());showView('editor');showStep(0);
  $('#resume-draft').hidden=!previousDraft;setMessage('Neuer Button begonnen. Dein vorheriger Entwurf lässt sich über „Vorigen Entwurf fortsetzen“ wieder öffnen.');
}
function splitLegacyStyle(){
  const button=$('#hero-button .preview-button'),label=button.querySelector('.comic-button-label');
  const css=getComputedStyle(button),ink=getComputedStyle(label).color;
  const colorToHex=value=>{const rgb=value.match(/\d+/g)?.slice(0,3);return rgb?.length===3?'#'+rgb.map(v=>Number(v).toString(16).padStart(2,'0')).join(''):null;};
  const background=css.getPropertyValue('--matched-background').match(/#[\da-f]{6}(?![\da-f])/gi);
  const s=current.settings;s.accent=background?.at(-1)||s.accent;s.ink_color=colorToHex(ink)||s.ink_color;
  s.font='letter-'+s.font.slice(6);s.font_link='manual';s.ink_mode='manual';s.material='plain';s.style='minimal';
  if(current.base)current.base.surface_mode='custom';
  for(const [key,{input}]of controls)input.value=s[key];render();updateDirty();
  setMessage('Schrift und Fläche getrennt. Die bisherige Grundfarbe ist jetzt eine eigene Farbfläche; ihre Struktur kannst du unter Oberfläche & Farbe wählen.');
}

function showView(view,target=null,focus=true){
  if(embedding&&view==='library'){notifyWorkshop('open-library');return;}
  $('#editor-view').hidden=view!=='editor';$('#library-view').hidden=view!=='library';
  for(const control of document.querySelectorAll('[data-view]'))control.setAttribute('aria-pressed',String(control.dataset.view===view));
  history.replaceState(null,'','#'+(target||(view==='library'?'library':'editor')));
  if(view==='library'){sound.stop();for(const player of audioPlayers.values())player.pause();}
  if(focus){const heading=$(target?'#'+target:view==='library'?'#library-title':'#editor-title');heading.tabIndex=-1;heading.focus({preventScroll:true});if(target)heading.scrollIntoView({block:'start'});else window.scrollTo({top:0});}
}
function showTarget(id){
  if(id==='shape-library'||id==='draft-library'){
    $('#library-search').value='';library();showView('library',id);
  }else if(id==='sound-gallery'){$('#sound-gallery').open=true;showView('editor',id);}
}

async function request(path,options={}) {
  let response,payload;
  try{response=await fetch(path,{cache:'no-store',...options});payload=await response.json();}
  catch{throw new Error('Die lokale Werkstatt ist gerade nicht erreichbar. Deine Eingaben bleiben stehen.');}
  if(!response.ok)throw new Error(payload.error||'Die lokale Werkstatt ist gerade nicht erreichbar. Deine Eingaben bleiben stehen.');
  return payload;
}
const post=(path,data)=>request(path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});
function builtin(row){const settings=applyMatchingFont(catalog,{...catalog.defaults,...row.settings});return {schema_version:2,kind:'button',name:row.name,notes:'',parent_id:null,settings,contour:makeContour(catalog,settings.shape),review:Object.fromEntries(catalog.review_dimensions.map(([key])=>[key,key==='motion'?'like':'open']))};}
function updateDirty(){const dirty=fingerprint()!==savedFingerprint;$('#dirty-state').textContent=dirty?'noch nicht gespeichert':'gespeicherter Stand';$('#dirty-state').classList.toggle('is-saved',!dirty);if(usageView)usageView.element.disabled=dirty||!current.parent_id;notifyWorkshop('button-state',{id:dirty?null:current.parent_id});}
function setMessage(message,error=false){for(const id of ['#save-status','#file-status']){$(id).textContent=message;$(id).classList.toggle('is-error',error);}}

function appendOptions(input,spec){
  const media=catalog.button_media;
  if(!media||!['font','sound'].includes(spec.key)){for(const [value,text]of spec.options)input.append(new Option(text,value));return;}
  const chosen=new Set();
  const group=(name,rows)=>{const block=document.createElement('optgroup');block.label=name;for(const [value,text]of rows){block.append(new Option(text,value));chosen.add(value);}if(block.children.length)input.append(block);};
  if(spec.key==='font'){
    const names={chalk:'Kreideschrift',stone:'Gemeißelte Schrift',iron:'Gestanzte Schrift',stamp:'Stempel & Schreibmaschine',hand:'Handschrift',comic:'Comic',clear:'Klar'};
    group('Schriftarten mit eigenem Charakter',media.fonts.map(row=>['letter-'+row.style,names[row.style]+' · '+row.font]));
    group('Spielschriften',spec.options.filter(([value])=>value==='cinzel').map(([value])=>[value,'Cinzel · Black Jack']));
    group('Frühere gekoppelte Stile',media.fonts.map(row=>[row.value,row.name+' · gekoppelte Fläche']));
  }
  else{input.append(new Option('Ohne Ton','off'));chosen.add('off');for(const name of [...new Set(media.sounds.map(row=>row.group))])group(name,media.sounds.filter(row=>row.group===name).map(row=>[row.id,row.name]));}
  group(spec.key==='font'?'Bisherige Schriften & Original':'Bisherige Klänge',spec.options.filter(([value])=>!chosen.has(value)));
}

function makeControls(){
  const groups=[{id:'form',name:'Umriss & Größe',step:0,keys:['shape','size','height_ratio','edge']},
    {id:'depth',name:'Tiefe & Schatten',step:0,keys:['depth','depth_x','shadow']},
    {id:'material',name:'Fläche & Farben',step:1,keys:['material','accent','gradient_to','opacity','finish','wear','depth_mode','depth_color']},
    {id:'style',name:'Gestaltungsstil',step:1,keys:['style']},
    {id:'lettering',name:'Text & Schrift',step:2,keys:['label','font','font_bold','font_italic','font_scale','ink_mode','ink_color','font_link','lettering']},
    {id:'motion',name:'Druckbewegung',step:3,keys:['duration','feel']},
    {id:'sound',name:'Klang',step:3,keys:['sound','volume']}];
  for(const group of groups){
    const details=document.createElement('details');details.open=true;details.dataset.editorStep=group.step;
    const summary=document.createElement('summary');summary.textContent=group.name;details.append(summary);
    const fields=document.createElement('div');fields.className='control-fields';let formatting;
    for(const key of group.keys){
      const spec=catalog.fields.find(field=>field.key===key);
      const row=document.createElement('div');row.className='control-row';
      const label=document.createElement('label');label.htmlFor='setting-'+spec.key;label.textContent=({font:'Schriftart',ink_mode:'Schriftfarbe bestimmen',ink_color:'Schriftfarbe',depth_mode:'Seitenwandfarbe bestimmen',depth:'Tiefe · 0 = flach'})[spec.key]||spec.label;row.append(label);
      let input;
      if(spec.type==='select'){
        input=document.createElement('select');appendOptions(input,spec);
      }else{
        input=document.createElement('input');input.type=spec.type==='checkbox'?'checkbox':spec.type==='range'?'range':spec.type==='color'?'color':'text';
        if(spec.type==='range'){input.min=spec.min;input.max=spec.max;input.step=spec.step;}
        if(spec.type==='text')input.maxLength=spec.max;
      }
      input.id='setting-'+spec.key;input.name=spec.key;
      let output;
      if(spec.type==='range'){output=document.createElement('output');output.htmlFor=input.id;row.append(output);}
      row.append(input);
      if(spec.type==='checkbox'){
        if(!formatting){formatting=document.createElement('div');formatting.className='font-formatting';fields.append(formatting);}
        row.classList.add('is-toggle');row.classList.add(spec.key);row.prepend(input);formatting.append(row);
      }else fields.append(row);
      controls.set(spec.key,{input,output,spec,row});
      input.addEventListener('input',()=>{
        const nextValue=input.value;
        if(current.settings.font.startsWith('media-')&&(['style','material','accent','gradient_to','opacity','finish','wear','depth_mode','depth_color','ink_mode','ink_color'].includes(spec.key)||(spec.key==='font'&&nextValue.startsWith('letter-'))))splitLegacyStyle();
        input.value=nextValue;
        if(current.base&&['style','material','accent','gradient_to','opacity','finish','wear'].includes(spec.key))current.base.surface_mode='custom';
        if(spec.key==='shape'){
          if(input.value!=='custom')contourEditor.setTemplate(input.value);
          else{contourEditor.shape='custom';current.settings.shape='custom';current.review.shape='open';reviews.get('shape').value='open';render();updateDirty();}
          return;
        }
        current.settings[spec.key]=spec.type==='checkbox'?input.checked:spec.type==='range'?Number(input.value):input.value;
        if(spec.key==='ink_color'){current.settings.ink_mode='manual';controls.get('ink_mode').input.value='manual';}
        if(spec.key==='depth_color'){current.settings.depth_mode='manual';controls.get('depth_mode').input.value='manual';}
        if(spec.key==='font'){current.settings.font_link='manual';current.settings.lettering='plain';controls.get('font_link').input.value='manual';controls.get('lettering').input.value='plain';}
        if(['font_link','lettering'].includes(spec.key)){
          applyMatchingFont(catalog,current.settings);controls.get('font').input.value=current.settings.font;
        }
        const dimension={style:'style',material:'surface',form:'shape',lettering:'lettering',motion:'motion',sound:'sound'}[spec.group];
        current.review[dimension]='open';reviews.get(dimension).value='open';
        if(spec.key==='material'){
          current.review.lettering='open';reviews.get('lettering').value='open';
          if(current.settings.sound==='material'){current.review.sound='open';reviews.get('sound').value='open';}
        }
        updateOutputs();render();updateDirty();
      });
    }
    if(group.id==='style'){const note=document.createElement('p');note.id='style-description';note.className='settings-note';fields.append(note);}
    if(group.id==='material'){const note=document.createElement('p');note.id='material-description';note.className='settings-note';fields.append(note);}
    if(group.id==='material'){
      const original=document.createElement('div');original.id='surface-origin';original.className='settings-note';
      original.append(toolButton('Eigene Oberfläche bearbeiten',()=>{if(current.base)current.base.surface_mode='custom';render();updateDirty();}).element);
      const note=document.createElement('p');note.id='side-color-note';note.className='settings-note';fields.append(original,note);
    }
    if(group.id==='lettering'){const note=document.createElement('p');note.id='font-suggestion';note.className='font-suggestion';fields.append(note);}
    if(group.id==='lettering'){
      const legacy=document.createElement('div');legacy.id='legacy-style';legacy.className='settings-note';legacy.append(toolButton('Schrift und Fläche trennen',splitLegacyStyle).element);fields.append(legacy);
    }
    if(group.id==='depth'){const note=document.createElement('p');note.className='settings-note';note.textContent='Die Seitenwandfarbe findest du im nächsten Schritt bei Oberfläche & Farbe. Der Schlagschatten ist ein eigener Effekt.';fields.append(note);}
    if(group.id==='form'||group.id==='sound'){
      const note=document.createElement('p');note.className='settings-note';const link=document.createElement('a');
      link.href=group.id==='form'?'#shape-library':'#sound-gallery';link.textContent=group.id==='form'?'Gespeicherte Formen öffnen':'Klangbeispiele anhören';note.append(link);fields.append(note);
    }
    details.append(fields);$('#settings-form').append(details);
  }
  for(const [key,name] of catalog.review_dimensions){
    const row=document.createElement('div'),label=document.createElement('label'),select=document.createElement('select');
    label.htmlFor='review-'+key;label.textContent=name;select.id='review-'+key;
    for(const [value,text]of catalog.review_states)select.append(new Option(text,value));
    select.addEventListener('change',()=>{current.review[key]=select.value;updateDirty();});
    row.append(label,select);$('#review-fields').append(row);reviews.set(key,select);
  }
}
function updateOutputs(){for(const {input,output,spec}of controls.values())if(output)output.textContent=input.value+(spec.unit||'');}
async function load(recipe,persisted=false){
  if(isSourceRecipe(recipe)){
    const host=document.createElement('div');host.style.cssText='position:fixed;left:-10000px;top:0;width:620px;visibility:hidden';document.body.append(host);
    try{const context=await new Promise((resolve,reject)=>{const timer=setTimeout(()=>reject(Error('Die Originalquelle konnte nicht geladen werden.')),8000);renderSourceButton(host,recipe,{onReady:value=>{clearTimeout(timer);resolve(value);}});});const converted=recipeFromProfile(captureButton(context.root),recipe.source_button,catalog,recipe);converted.id=recipe.id;return load(converted,persisted);}catch(error){setMessage(error.message,true);}finally{host.remove();}return;
  }
  activeShapeId=null;
  current=clone(recipe);if(!isSourceRecipe(current))current.settings={...catalog.defaults,...current.settings};current.parent_id=persisted?recipe.id:(recipe.parent_id||null);
  if(persisted){const url=new URL(location.href);url.searchParams.delete('source_button');url.searchParams.delete('new');url.searchParams.set('recipe',recipe.id);history.replaceState(null,'',url);}
  $('#recipe-name').value=current.name;$('#recipe-notes').value=current.notes;
  document.body.classList.remove('source-mode');$('#source-original').hidden=!current.source_button;$('#source-original-preview').replaceChildren();$('#source-original').open=false;
  $('.save-hint').textContent=current.source_button?'Speichert deinen eigenen Buttonentwurf. Die eingesetzten Originalbuttons bleiben unverändert.':'Speichert den ganzen Button mit Form, Material, Schrift, Bewegung und Klang. Ältere Stände bleiben erhalten.';
  for(const [key,{input}]of controls)input.value=current.settings[key];
  for(const [key,select]of reviews)select.value=current.review[key];
  contourEditor.setLayout(current.base,current.settings);contourEditor.load(current.contour,current.settings.shape);
  savedFingerprint=persisted?fingerprint():'';
  updateOutputs();render();updateDirty();setMessage(persisted?'Gespeicherten Entwurf geladen. Änderungen erzeugen beim Speichern einen neuen Stand.':'Vorlage geladen. Du kannst sie verändern und als eigenen Entwurf speichern.');
  showStep(0);
}
function render(){
  if(isSourceRecipe(current))return;
  const s=current.settings;
  contourEditor?.setLayout(current.base,s);
  const sourceFont=[...controls.get('font').input.options].find(o=>o.value==='source');sourceFont.hidden=!current.base;sourceFont.disabled=!current.base;
  const material=catalog.fields.find(row=>row.key==='material').options.find(row=>row[0]===s.material)[1];
  const style=catalog.fields.find(row=>row.key==='style').options.find(row=>row[0]===s.style)[1].split(' · ')[0];
  $('#material-caption').textContent=`${material} · ${style}`;
  $('#material-description').textContent=catalog.material_descriptions?.[s.material]||'';
  if(controls.has('gradient_to'))controls.get('gradient_to').row.hidden=s.material!=='gradient';
  if(controls.has('opacity'))controls.get('opacity').row.hidden=s.material!=='translucent';
  controls.get('wear').row.hidden=s.style==='minimal'||['plain','gradient','translucent'].includes(s.material);
  controls.get('finish').row.hidden=s.material==='translucent';
  $('#style-description').textContent=catalog.style_descriptions?.[s.style]||'';
  if(['plain','gradient','translucent'].includes(s.material))$('#style-description').textContent={comic:'Kräftige Kontur und gemalte Beschriftungswirkung auf deiner gewählten Fläche.',natural:'Zurückhaltende Kontur und räumliche Lichtwirkung auf deiner gewählten Fläche.',minimal:'Ruhige Farbflächen und eine reduzierte Kontur, ohne Materialstruktur.'}[s.style];
  $('#font-suggestion').textContent=s.lettering==='plain'?'Schriftart, Fett und Kursiv bestimmen die Beschriftung. Die Schriftfarbe wählst du unabhängig davon.':'Dieser ältere Entwurf enthält noch die Wirkung „'+catalog.fields.find(f=>f.key==='lettering').options.find(([key])=>key===s.lettering)[1]+'“. Eine neue Schriftwahl ersetzt sie.';
  $('#motion-caption').textContent=`${s.depth===0?'ohne Tiefe':s.depth<=4?'dezent':s.depth<=8?'spürbar':'kräftig'} · ${s.duration} ms`;
  const action=()=>{$('#preview-feedback').textContent='Gedrückt und wieder oben. Nur ein Beispiel – keine Spielaktion.';};
  renderButton($('#hero-button'),current,{sound,action});
  // Read the canonical renderer's result; preserve all recipe values and originals.
  const originalSurface=$('#hero-button .preview-button').dataset.originalSurface==='true';
  controls.get('finish').input.disabled=s.material==='translucent';
  controls.get('finish').input.setAttribute('aria-describedby','material-description');
  if(originalSurface)$('#material-description').textContent+=' Noch ist die Originalfläche der Vorlage sichtbar. Sobald du hier eine Farbe, Glanz oder Material wählst, wird deine eigene Oberfläche verwendet.';
  $('#surface-origin').hidden=!originalSurface;
  $('#side-color-note').textContent=s.depth===0?'Der Button ist flach. Die Seitenwandfarbe wird sichtbar, sobald du im Schritt Form eine Tiefe größer als 0 wählst.':'Die Seitenwandfarbe gilt für die sichtbare Tiefe. Eine Farbwahl stellt automatisch auf „Eigene Farbe“ um.';
  controls.get('volume').row.hidden=s.sound==='off';

  const mediaStyle=catalog.button_media?.fonts.find(row=>row.value===s.font),matched=!!mediaStyle;
  const letteringOnly=s.font.startsWith('letter-');
  controls.get('font_link').row.hidden=true;
  controls.get('lettering').row.hidden=true;
  $('#legacy-style').hidden=!matched;
  const hero=$('#hero-button .preview-button'),textStyleAllowed=!hero.querySelector('.button-picture')&&!hero.querySelector('.comic-button-label').hidden;
  const labelStyle=getComputedStyle(hero.querySelector('.comic-button-label'));
  for(const [key,inherited] of [['font_bold',Number(labelStyle.fontWeight)>=600],['font_italic',labelStyle.fontStyle!=='normal']]){
    controls.get(key).input.checked=typeof s[key]==='boolean'?s[key]:inherited;
    controls.get(key).input.disabled=!textStyleAllowed;
  }
  for(const option of controls.get('font').input.options){
    if(option.value.startsWith('media-'))option.hidden=option.value!==s.font;
    if(option.value.startsWith('letter-')||option.value.startsWith('media-'))option.disabled=(!textStyleAllowed||option.value.startsWith('media-'))&&option.value!==s.font;
  }
  for(const group of controls.get('font').input.querySelectorAll('optgroup'))if(group.label==='Frühere gekoppelte Stile')group.hidden=!matched;
  if(matched){
    $('#material-caption').textContent=mediaStyle.name+' · '+mediaStyle.font;
    $('#font-suggestion').textContent='Übernommener älterer Stil: Schrift und Fläche sind noch gekoppelt. „Schrift und Fläche trennen“ übernimmt die Grundfarbe als eigene Farbfläche.';
  }else if(letteringOnly){
    $('#font-suggestion').textContent=s.font==='letter-chalk'?'Cabin Sketch hat einen unregelmäßig gezeichneten Strich. Wähle die Schriftfarbe für deine Kreide selbst.':'Diese Schrift bringt ihren eigenen Charakter mit. Fläche und Schriftfarbe bestimmst du unabhängig davon.';
  }else if(!textStyleAllowed)$('#font-suggestion').textContent='Dieses Original nutzt ein eigenes Bild oder Symbol. Die Schriftwirkungen sind für sichtbar beschriftete Buttons vorgesehen.';
  $('#state-grid').replaceChildren();
  for(const [state,label]of [['normal','normal'],['hover','darüber'],['pressed','gedrückt'],['selected','ausgewählt'],['disabled','gesperrt'],['focus','tastaturfokus']]){
    const tile=document.createElement('article'),caption=document.createElement('span'),host=document.createElement('div');
    caption.textContent=label;tile.append(caption,host);$('#state-grid').append(tile);
    renderButton(host,current,{state,size:14,label:s.label,sound,action});
  }
  renderButton($('#compare-a'),pinned,{size:18,sound,action});
  renderButton($('#compare-b'),current,{size:18,sound,action});
  $('#compare-a-label').textContent=pinned.name;$('#compare-b-label').textContent=current.name;
  materialize($('#context-surface'),current);
  renderButton($('#context-button'),current,{label:'weiter zum spiel',size:17,sound,action});
  const channels=s.accent.slice(1).match(/../g).map(x=>parseInt(x,16)/255);
  const light=channels[0]*.2126+channels[1]*.7152+channels[2]*.0722;
  const low=(['chalk','screen'].includes(s.lettering)&&light>.6)||(['carved','etched'].includes(s.lettering)&&light<.3);
  $('#readability').hidden=!low;$('#readability').textContent=low?'Die Schrift hebt sich wenig ab. Probiere eine andere Grundfarbe oder Schriftwirkung.':'';
  $('#sound-state').textContent=s.sound==='off'?'Ohne Ton':s.volume===0?'Ton gewählt · Lautstärke 0 %':['wood','stone','metal'].includes(s.sound)?'Alter synthetischer Platzhalter gewählt':'Klang gewählt · zum Testen den großen Button drücken';
  for(const [id,choice]of soundChoices)choice.setAttribute('aria-pressed',String(s.sound===id));
  for(const player of audioPlayers.values())player.volume=s.volume/100;
}
function library(){
  const search=$('#library-search').value.trim().toLocaleLowerCase('de-DE'),matches=row=>row.name.toLocaleLowerCase('de-DE').includes(search);
  const allButtons=saved.filter(row=>row.kind!=='shape'),allShapes=saved.filter(row=>row.kind==='shape');
  const buttons=allButtons.filter(matches),shapes=allShapes.filter(matches);
  $('#library-total').textContent=String(saved.length);$('#library-total').title=saved.length+' gespeicherte Entwürfe und Formen';
  $('#recipe-count').textContent=String(allButtons.length);$('#saved-recipes').replaceChildren();
  if(!buttons.length){const p=document.createElement('p');p.className='empty-library';p.textContent=search?'Kein Entwurf mit diesem Namen.':'Hier erscheinen deine gespeicherten Buttonentwürfe. Sie bleiben auch nach dem Schließen erhalten.';$('#saved-recipes').append(p);}
  for(const recipe of buttons)recipeCard($('#saved-recipes'),recipe,true);
  $('#shape-count').textContent=String(allShapes.length);$('#saved-shapes').replaceChildren();
  if(!shapes.length){const p=document.createElement('p');p.className='empty-library';p.textContent=search?'Keine Form mit diesem Namen.':'Hier erscheinen eigene Formvorlagen. Unter der Kontur „Nur die Form als Vorlage speichern“ öffnen.';$('#saved-shapes').append(p);}
  for(const recipe of shapes)shapeCard(recipe);
  $('#builtin-recipes').replaceChildren();for(const row of catalog.presets.filter(matches))recipeCard($('#builtin-recipes'),builtin(row),false,row.description);
  if(!$('#builtin-recipes').children.length){const p=document.createElement('p');p.className='empty-library';p.textContent='Keine Startvorlage mit diesem Namen.';$('#builtin-recipes').append(p);}
}
function shapeCard(recipe){
  const card=document.createElement('article');card.className='shape-card';
  const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');const plane=contourPlane(recipe.base,recipe.settings);svg.setAttribute('viewBox',`0 0 600 ${plane.height+48}`);svg.setAttribute('aria-hidden','true');
  const path=document.createElementNS(svg.namespaceURI,'path');path.setAttribute('d',outlinePath(recipe.contour.points,recipe.base||(recipe.settings.height_ratio??100)!==100?plane:null));path.setAttribute('fill','#cadf9e');path.setAttribute('stroke','#405632');path.setAttribute('stroke-width','5');svg.append(path);
  const title=document.createElement('h3');title.textContent=recipe.name;
  const detail=document.createElement('small');detail.textContent=`${recipe.contour.points.length} Randpunkte · `+new Intl.DateTimeFormat('de-DE',{dateStyle:'short',timeStyle:'short'}).format(new Date(recipe.created_at));
  const use=toolButton('form verwenden',()=>{applyShape(recipe);showView('editor');});use.element.setAttribute('aria-label',recipe.name+' als Form verwenden');
  card.append(svg,title,detail,use.element);$('#saved-shapes').append(card);
}
function applyShape(recipe){if(recipe.base){const ratio=current.base?current.base.height/current.base.width:180/560;current.settings.height_ratio=Math.max(20,Math.min(250,Math.round((recipe.base.height/recipe.base.width)/ratio*(recipe.settings.height_ratio??100))));controls.get('height_ratio').input.value=current.settings.height_ratio;contourEditor.setLayout(current.base,current.settings);}activeShapeId=recipe.id||null;$('#shape-name').value=recipe.name;contourEditor.applySaved(recipe.contour);$('#shape-save-status').textContent='Form übernommen. Du kannst die Übernahme mit Rückgängig zurücknehmen.';$('#preview-feedback').textContent=`Form „${recipe.name}“ übernommen. Material, Schrift und Klang bleiben erhalten.`;}
async function saveShape(){
  if(savingShape)return;const name=$('#shape-name').value.trim();
  const message=$('#shape-save-status');message.classList.remove('is-error');
  if(!name){message.textContent='Bitte gib deiner Form einen Namen.';$('#shape-name').focus();return;}
  savingShape=true;shapeSaveView.element.disabled=true;
  const data={...clone(current),kind:'shape',name,parent_id:activeShapeId};
  try{const {recipe}=await post('/api/recipes',data);saved.unshift(recipe);activeShapeId=recipe.id;library();message.textContent=`„${recipe.name}“ ist unter „Deine Formen“ gespeichert.`;notifyWorkshop('button-saved',{id:recipe.id});}
  catch(error){message.textContent=error.message;message.classList.add('is-error');}
  finally{savingShape=false;shapeSaveView.element.disabled=false;}
}
function soundGallery(){
  const host=$('#sound-gallery-grid');host.replaceChildren();const legacy=$('#legacy-sound-grid');legacy.replaceChildren();
  for(const record of catalog.sounds){
    const card=document.createElement('article');card.className='sound-card';
    const group=document.createElement('span');group.className='sound-group';group.textContent=record.group;
    const name=document.createElement('h3');name.textContent=record.name;
    const description=document.createElement('p');description.textContent=record.description;
    const player=document.createElement('audio');player.controls=true;player.preload='none';player.src='/assets/audio/'+record.file;player.setAttribute('aria-label',record.name+' anhören');player.volume=current.settings.volume/100;
    player.addEventListener('play',()=>{sound.stop();for(const other of audioPlayers.values())if(other!==player)other.pause();$('#sound-state').textContent=record.name+' · ganze Aufnahme';});
    audioPlayers.set(record.id,player);
    const choose=toolButton('am button verwenden',()=>{
      current.settings.sound=record.id;controls.get('sound').input.value=record.id;current.review.sound='open';reviews.get('sound').value='open';render();updateDirty();
    });choose.element.setAttribute('aria-label',record.name+' am Button verwenden');choose.element.setAttribute('aria-pressed','false');soundChoices.set(record.id,choose.element);
    const credit=document.createElement('div');credit.className='sound-credit';
    const source=document.createElement('a');source.href=record.source;source.target='_blank';source.rel='noopener';source.textContent=record.author;
    const license=document.createElement('a');license.href=record.license_url;license.target='_blank';license.rel='noopener';license.textContent=record.license;
    credit.append(source,' · ',license,` · ${record.duration.toLocaleString('de-DE')} s · ${record.media_short?'kurze Werkstattprobe, vollständig am Button':'bisheriger Buttonausschnitt mit Ein-/Ausblendung'}`);
    card.append(group,name,description,player,choose.element,credit);(record.media_short?host:legacy).append(card);
  }
  ui('#sound-stop','alle töne stoppen',()=>{sound.stop();for(const player of audioPlayers.values()){player.pause();player.currentTime=0;}$('#sound-state').textContent='Wiedergabe gestoppt';},{variant:'secondary'});
}
function recipeCard(host,recipe,persisted,description){
  const card=document.createElement('article');card.className='recipe-card';
  const thumbnail=document.createElement('div');thumbnail.className='recipe-thumbnail';
  renderButton(thumbnail,recipe,{label:recipe.settings?.label,size:12});thumbnail.inert=true;thumbnail.setAttribute('aria-hidden','true');
  const title=document.createElement('h3');title.textContent=recipe.name;
  const open=toolButton(persisted?'entwurf öffnen':'vorlage verwenden',()=>{load(recipe,persisted);showView('editor');}).element;open.setAttribute('aria-label',recipe.name+(persisted?' öffnen':' als Startvorlage verwenden'));
  const detail=document.createElement('small');detail.textContent=persisted?new Intl.DateTimeFormat('de-DE',{dateStyle:'short',timeStyle:'short',timeZone:'Europe/Berlin'}).format(new Date(recipe.created_at)):description;
  card.append(thumbnail,title,detail,open);host.append(card);
}
async function save(){
  if(saving)return;
  if(!current.name.trim()){setMessage('Bitte gib deinem Entwurf einen Namen.',true);$('#recipe-name').focus();return;}
  saving=true;saveView.element.disabled=true;saveView.label('wird gespeichert');
  const submitted=clone(current),submittedFingerprint=fingerprint();
  try{
    const {recipe}=await post('/api/recipes',submitted);saved.unshift(recipe);library();
    notifyWorkshop('button-saved',{id:recipe.id});
    if(fingerprint()===submittedFingerprint){
      current.parent_id=recipe.id;current.id=recipe.id;savedFingerprint=fingerprint();updateDirty();
      const url=new URL(location.href);url.searchParams.delete('source_button');url.searchParams.delete('new');url.searchParams.set('recipe',recipe.id);history.replaceState(null,'',url);
    }
    setMessage('Auf diesem PC gespeichert. Der bisherige Stand bleibt erhalten. ');
    const link=document.createElement('a');link.href='#draft-library';link.textContent='Gespeicherte Entwürfe öffnen';$('#save-status').append(link);
  }catch(error){setMessage(error.message,true);}
  finally{saving=false;saveView.element.disabled=false;saveView.label('entwurf speichern');}
}
function exportRecipe(){
  const data=JSON.stringify({...current,renderer_version:catalog.renderer_version},null,2);
  const url=URL.createObjectURL(new Blob([data],{type:'application/json'}));
  const a=document.createElement('a');a.href=url;a.download=(current.name.replace(/[^\p{L}\p{N}-]+/gu,'-').slice(0,70)||'button-entwurf')+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  setMessage('Entwurfsdatei zum Mitnehmen erstellt.');
}
async function importRecipe(event){
  const file=event.target.files[0];event.target.value='';if(!file)return;
  try{
    if(file.size>32768)throw new Error('Die Entwurfsdatei ist zu groß.');
    let payload;try{payload=JSON.parse(await file.text());}catch{throw new Error('Diese Datei enthält keinen gültigen Entwurf.');}
    const {recipe}=await post('/api/validate',payload);if(recipe.kind==='shape')applyShape(recipe);else load(recipe);showView('editor');setMessage('Datei eingelesen. Zum dauerhaften Aufheben bitte speichern.');
  }catch(error){setMessage(error.message,true);}
}
async function init(){
  initPreviewBackground();
  const [definitions,collection]=await Promise.all([request('/api/catalog'),request('/api/recipes')]);
  catalog=definitions;saved=collection.recipes;
  sound.configure(catalog.sounds);
  current=newRecipe();pinned=builtin(catalog.presets[0]);
  makeControls();
  for(const [index,name]of steps.entries()){
    const button=toolButton((index+1)+' · '+name,()=>showStep(index)).element;button.dataset.stepButton=index;$('#editor-steps').append(button);
  }
  $('#step-back').addEventListener('click',()=>showStep(editorStep-1));
  $('#step-next').addEventListener('click',()=>showStep(editorStep+1));
  $('#start-new').addEventListener('click',startNew);
  try{previousDraft=JSON.parse(sessionStorage.getItem('button-previous-draft'));}catch{}
  $('#resume-draft').hidden=!previousDraft;
  $('#resume-draft').addEventListener('click',async()=>{
    if(!previousDraft)return;
    const resume=previousDraft;await load(resume.recipe);savedFingerprint=resume.savedFingerprint;updateDirty();
    history.replaceState(null,'',resume.url);showView('editor');setMessage('Deinen vorherigen Entwurf wieder geöffnet.');
  });
  const original=document.createElement('details');original.id='source-original';original.className='source-original';original.hidden=true;
  const summary=document.createElement('summary');summary.textContent='Unverändertes Original zum Vergleich';const note=document.createElement('p');note.textContent='Dies ist die vorhandene Spielgestaltung. Deine Änderungen wirken ausschließlich auf deinen Entwurf.';const preview=document.createElement('div');preview.id='source-original-preview';original.append(summary,note,preview);$('.live-panel').append(original);
  original.addEventListener('toggle',()=>{if(original.open&&current.source_button)renderSourceButton(preview,{schema_version:3,source_button:current.source_button,appearance:{}});});
  contourEditor=new ContourEditor($('#contour-editor'),catalog,(contour,shape)=>{
    current.contour=contour;current.settings.shape=shape;controls.get('shape').input.value=shape;
    current.review.shape='open';reviews.get('shape').value='open';render();updateDirty();
  });
  ui('#pin-button','aktuellen entwurf festhalten',()=>{pinned=clone(current);render();$('#preview-feedback').textContent='Entwurf zum Vergleich festgehalten. Verändere jetzt deinen aktuellen Button.';},{variant:'secondary'});
  saveView=ui('#save-button','entwurf speichern',save,{primary:true});
  usageView=ui('#usage-button','Verwendungen verwalten',()=>{
    if(embedding){notifyWorkshop('manage-usage',{id:current.parent_id});return;}
    if(!usageDialog)usageDialog=new ButtonUsageDialog();usageDialog.open(current.parent_id,current);
  });
  shapeSaveView=ui('#shape-save-button','form als vorlage speichern',saveShape);
  ui('#export-button','exportieren',exportRecipe,{variant:'secondary'});
  ui('#import-button','datei einlesen',()=>$('#recipe-file').click(),{variant:'secondary'});
  $('#recipe-file').addEventListener('change',importRecipe);
  $('#recipe-name').addEventListener('input',event=>{current.name=event.target.value;$('#compare-b-label').textContent=current.name;updateDirty();});
  $('#recipe-notes').addEventListener('input',event=>{current.notes=event.target.value;updateDirty();});
  for(const control of document.querySelectorAll('[data-view]'))control.addEventListener('click',()=>showView(control.dataset.view));
  $('#library-search').addEventListener('input',library);
  document.addEventListener('click',event=>{const link=event.target.closest('a');if(!link)return;const id=link.getAttribute('href')?.slice(1);if(['shape-library','draft-library','sound-gallery'].includes(id)){event.preventDefault();showTarget(id);}});
  load(current);library();soundGallery();render();
  const openingQuery=new URLSearchParams(location.search),sourceButton=openingQuery.get('source_button');
  if(sourceButton){
    const result=await request('/api/button-usage/'+encodeURIComponent(sourceButton)+'/editor');
    await load(result.recipe,result.persisted===true);
    if(result.persisted)setMessage('Im lokalen Spiel verwendeten Entwurf „'+result.recipe.name+'“ geladen. Änderungen erzeugen beim Speichern einen neuen Stand.');
  }
  {const requested=openingQuery.get('recipe'),record=saved.find(r=>r.id===requested);if(requested&&!record)throw new Error('Der angeforderte gespeicherte Entwurf wurde nicht gefunden.');if(record){if(record.kind==='shape')applyShape(record);else await load(record,true);}}
  const target=location.hash.slice(1);if(['shape-library','draft-library','sound-gallery'].includes(target))showTarget(target);else showView(target==='library'?'library':'editor',null,false);
  if(collection.unreadable)setMessage(`${collection.unreadable} gespeicherte Datei(en) konnten nicht gelesen werden. Die Dateien wurden erhalten.`,true);
  document.body.dataset.ready='true';
  if(embedding){let lastHeight=0;const resize=()=>{const height=Math.ceil(document.body.getBoundingClientRect().height);if(height>0&&height!==lastHeight){lastHeight=height;notifyWorkshop('editor-height',{height});}};new ResizeObserver(resize).observe(document.body);resize();}
  document.dispatchEvent(new Event('button-editor-ready'));
}
init().catch(error=>{$('#startup-error').hidden=false;$('#startup-error').textContent='Die Werkstatt konnte nicht geladen werden. '+error.message;document.dispatchEvent(new CustomEvent('button-editor-startup-error',{detail:error.message}));});
