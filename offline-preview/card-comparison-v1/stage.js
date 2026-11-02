import {originalCard} from '/original/card.js';
import * as T from '/vendor/three.module.js';
import {cardGeometries,cardBody,cardMaterials} from './body.js';

const config=document.body.dataset;
const mode=config.cardMode||new URLSearchParams(location.search).get('mode')||'original';
const interaction=config.cardInteraction||'move';
const backArtwork=config.cardBack||'cardBack_blue2.png';
const contentNode=document.querySelector('#card-content');
const cardContent=contentNode?JSON.parse(contentNode.textContent):null;
document.body.dataset.mode=mode;
document.body.dataset.interaction=interaction;
const stage=document.querySelector('#stage'),table=document.querySelector('#table'),layer=document.querySelector('#cards');
const status=document.querySelector('#stage-status'),keyboard=document.querySelector('#keyboard-cards');
document.querySelector('#mode-label').textContent={original:'Original · flach',graphic:'Neue Grafik · flach',model:'Importierter 3D-Körper'}[mode];
const suits={Hearts:{symbol:'♥',color:'red',name:'Herz'},Spades:{symbol:'♠',color:'black',name:'Pik'},Clubs:{symbol:'♣',color:'black',name:'Kreuz'},Diamonds:{symbol:'♦',color:'red',name:'Karo'}};
let state={card:config.cardKey||'Hearts7',layout:config.cardLayout||'hand',angle:Number(config.cardAngle||0),zoom:Number(config.cardZoom||100),back:config.cardFaceDown==='true'},items=[],fit=1,held=null;
let modelData,renderer,scene,camera,world,shadowPlane,raycaster,dragPlane,needsRender=true;
const textures=new Map(),geometry=new Map(),materialCache=new Map();
const cardInfo=key=>{if(key==='Joker')return {symbol:'★',color:'red',name:'Joker',rank:'★',key,joker:true};const match=key.match(/^(Hearts|Spades|Clubs|Diamonds)(A|K|Q|J|10|[2-9])$/);return {...suits[match[1]],suit:match[1],rank:match[2],key};};
const cardName=item=>cardContent?cardContent.title+(cardContent.kind==='country'?' · '+cardContent.prompt:''):`${cardInfo(item.key).name} ${cardInfo(item.key).rank}`;
function arrange(){
  const common={x:260,y:220,rotation:0,scale:1,back:state.back};
  if(state.layout==='single')return [{...common,key:state.card}];
  if(state.layout==='stack')return Array.from({length:12},(_,i)=>({...common,key:state.card,x:248+i*2,y:228-i*1.6,back:i<11?true:state.back}));
  if(state.layout==='deck')return Object.keys(suits).flatMap((suit,row)=>['A','2','3','4','5','6','7','8','9','10','J','Q','K'].map((rank,col)=>({...common,key:suit+rank,x:32+col*38,y:90+row*84,scale:.255})));
  const keys=['SpadesA','ClubsK','Hearts7','Diamonds10','HeartsQ'].filter(key=>key!==state.card).slice(0,4);
  keys.splice(2,0,state.card);
  return keys.map((key,i)=>({...common,key,x:260+(i-2)*43,y:220+Math.abs(i-2)*13,rotation:(i-2)*11}));
}
function announce(text){status.textContent=text;}
function flip(item){item.back=!item.back;applyPosition(item);announce(`${cardInfo(item.key).name} ${cardInfo(item.key).rank} · ${item.back?'Rückseite':'Vorderseite'}`);}
function applyPosition(item){
  if(item.element){
    item.element.classList.toggle('face-up',!item.back);
    item.element.style.left=`${item.x/520*100}%`;item.element.style.top=`${item.y/440*100}%`;
    item.element.style.transform=`translate(-50%,-50%) rotate(${item.rotation}deg) scale(${item.scale})`;
    item.element.setAttribute('aria-label',`${cardName(item)}, ${item.back?'Rückseite':'Vorderseite'}`);
  }
  if(item.object){
    item.object.position.set(item.x-260,220-item.y,item.index*1.3+(held?.item===item?25:0));
    item.object.rotation.set(0,item.back?Math.PI:0,-item.rotation*Math.PI/180);
    item.object.scale.setScalar(item.scale);
    needsRender=true;
  }
  if(item.button)item.button.setAttribute('aria-label',`${cardInfo(item.key).name} ${cardInfo(item.key).rank}, ${item.back?'Rückseite':'Vorderseite'}`);
  stage.dataset.lastAction=JSON.stringify({index:item.index,x:Math.round(item.x),y:Math.round(item.y),back:item.back});
}
function handleKeys(event,item){
  if(interaction!=='move'){if(interaction==='select'&&[' ','Enter'].includes(event.key)){event.preventDefault();selectCard(item);}return;}
  if(event.key===' '||event.key==='Enter'){event.preventDefault();flip(item);return;}
  const direction={ArrowLeft:[-8,0],ArrowRight:[8,0],ArrowUp:[0,-8],ArrowDown:[0,8]}[event.key];
  if(direction){event.preventDefault();item.x=T.MathUtils.clamp(item.x+direction[0],25,495);item.y=T.MathUtils.clamp(item.y+direction[1],40,400);applyPosition(item);announce('Karte verschoben');}
}
function selectCard(item){
  item.selected=!item.selected;item.element?.classList.toggle('is-selected',item.selected);
  item.element?.setAttribute('aria-pressed',String(item.selected));stage.dataset.selected=String(item.selected);
  announce(item.selected?'Karte ausgewählt':'Auswahl aufgehoben');
}
async function drawFlat(){
  layer.replaceChildren();
  for(const item of items){
    const info=cardInfo(item.key);
    const el=originalCard({...info,id:`sample-${item.index}`,face_up:!item.back,zone:'table',x:item.x/520*100,y:item.y/440*100,z:item.index+1},()=>{if(interaction==='move')flip(item);});
    // Only local input handling differs; DOM/CSS of the original factory is retained.
    el.draggable=false;el.tabIndex=['none','read'].includes(interaction)?-1:0;el.setAttribute('role',interaction==='none'?'img':interaction==='read'?'article':'button');el.title=interaction==='move'?'Ziehen: verschieben · Doppelklick: wenden':interaction==='select'?'Klicken: auswählen':'';
    if(interaction==='select'){el.setAttribute('aria-pressed','false');el.addEventListener('click',()=>selectCard(item));}
    if(mode==='graphic'){
      el.classList.add('graphic');
      el.querySelector('.playing-card-back').style.backgroundImage=`url('/assets/kenney/${backArtwork}')`;
      if(cardContent){const {renderContentCard}=await import('/card-components/content-card.js');await renderContentCard(el,cardContent,interaction!=='none');}
      else{const front=el.querySelector('.playing-card-front');front.replaceChildren();const image=new Image();image.className='face-art';image.alt='';image.src=`/assets/kenney/card${item.key}.png`;front.append(image);}
    }
    item.element=el;applyPosition(item);
    el.addEventListener('dblclick',()=>{if(interaction==='move')flip(item);});
    el.addEventListener('keydown',event=>handleKeys(event,item));
    el.addEventListener('pointerdown',event=>{
      if(event.button!==0||interaction!=='move')return;
      el.focus({preventScroll:true});el.setPointerCapture(event.pointerId);el.classList.add('is-held');
      held={item,start:[event.clientX,event.clientY],position:[item.x,item.y]};
    });
    el.addEventListener('pointermove',event=>{
      if(held?.item!==item)return;
      item.x=T.MathUtils.clamp(held.position[0]+(event.clientX-held.start[0])/(fit*state.zoom/100),25,495);
      const angleScale=Math.max(.3,Math.cos(state.angle*Math.PI/180));
      item.y=T.MathUtils.clamp(held.position[1]+(event.clientY-held.start[1])/(fit*state.zoom/100*angleScale),40,400);
      applyPosition(item);announce('Karte wird bewegt');
    });
    const release=()=>{if(held?.item===item){held=null;el.classList.remove('is-held');announce('Karte abgelegt');}};
    el.addEventListener('pointerup',release);el.addEventListener('pointercancel',release);
    layer.append(el);
  }
  await Promise.all([...layer.querySelectorAll('img')].map(img=>img.decode()));
}
async function loadTexture(path){
  if(!textures.has(path))textures.set(path,new T.TextureLoader().loadAsync(path).then(texture=>{texture.colorSpace=T.SRGBColorSpace;texture.anisotropy=Math.min(8,renderer.capabilities.getMaxAnisotropy());return texture;}));
  return textures.get(path);
}
async function materialsFor(key){
  if(!materialCache.has(key))materialCache.set(key,(async()=>{
    const [front,back]=await Promise.all([loadTexture(`/assets/kenney/card${key}.png`),loadTexture(`/assets/kenney/${backArtwork}`)]);
    return cardMaterials(front,back);
  })());
  return materialCache.get(key);
}
async function initModel(){
  modelData=await fetch('/assets/mehrasaur/card-mesh.json').then(r=>{if(!r.ok)throw new Error('Modelldatei fehlt');return r.json();});
  renderer=new T.WebGLRenderer({canvas:document.querySelector('#scene'),alpha:true,antialias:true});
  renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.shadowMap.enabled=true;renderer.shadowMap.type=T.PCFSoftShadowMap;
  renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.NeutralToneMapping;renderer.toneMappingExposure=1;
  scene=new T.Scene();camera=new T.OrthographicCamera(-260,260,220,-220,1,2400);camera.position.set(0,0,1000);
  world=new T.Group();scene.add(world);
  scene.add(new T.HemisphereLight('#fff6df','#5b796d',1.2));
  const keyLight=new T.DirectionalLight('#fff4db',2);keyLight.position.set(-220,360,600);keyLight.castShadow=true;
  keyLight.shadow.mapSize.set(2048,2048);keyLight.shadow.camera.left=-500;keyLight.shadow.camera.right=500;keyLight.shadow.camera.top=500;keyLight.shadow.camera.bottom=-500;keyLight.shadow.camera.near=1;keyLight.shadow.camera.far=1800;keyLight.shadow.bias=-.00015;keyLight.shadow.normalBias=.3;scene.add(keyLight);
  const fill=new T.DirectionalLight('#d3e9fa',.4);fill.position.set(250,-100,300);scene.add(fill);
  shadowPlane=new T.Mesh(new T.PlaneGeometry(1400,1400),new T.ShadowMaterial({opacity:.27}));shadowPlane.position.z=-4;shadowPlane.receiveShadow=true;world.add(shadowPlane);
  for(const [name,g] of cardGeometries(modelData))geometry.set(name,g);
  raycaster=new T.Raycaster();dragPlane=new T.Plane(new T.Vector3(0,0,1),0);
  const canvas=renderer.domElement;
  const pointer=event=>{const box=canvas.getBoundingClientRect();raycaster.setFromCamera(new T.Vector2((event.clientX-box.left)/box.width*2-1,-(event.clientY-box.top)/box.height*2+1),camera);};
  const pick=event=>{pointer(event);return raycaster.intersectObjects(items.flatMap(i=>i.object?.children||[]))[0]?.object.parent.userData.item;};
  const pointOnTable=event=>{pointer(event);world.updateMatrixWorld(true);const plane=dragPlane.clone().applyMatrix4(world.matrixWorld),hit=new T.Vector3();return raycaster.ray.intersectPlane(plane,hit)?world.worldToLocal(hit):null;};
  canvas.addEventListener('pointerdown',event=>{
    if(event.button!==0||interaction!=='move')return;const item=pick(event);if(!item)return;
    const point=pointOnTable(event);if(!point)return;
    canvas.setPointerCapture(event.pointerId);held={item,point,position:[item.x,item.y]};applyPosition(item);canvas.style.cursor='grabbing';
  });
  canvas.addEventListener('pointermove',event=>{
    if(!held)return;const point=pointOnTable(event);if(!point)return;
    const item=held.item;item.x=T.MathUtils.clamp(held.position[0]+point.x-held.point.x,25,495);item.y=T.MathUtils.clamp(held.position[1]-point.y+held.point.y,40,400);applyPosition(item);announce('Karte wird bewegt');
  });
  const release=()=>{if(held){const item=held.item;held=null;applyPosition(item);canvas.style.cursor='grab';announce('Karte abgelegt');}};
  canvas.addEventListener('pointerup',release);canvas.addEventListener('pointercancel',release);
  canvas.addEventListener('dblclick',event=>{if(interaction!=='move')return;const item=pick(event);if(item)flip(item);});
  canvas.addEventListener('contextmenu',event=>{event.preventDefault();if(interaction!=='move')return;const item=pick(event);if(item)flip(item);});
  renderer.setAnimationLoop(()=>{if(!document.hidden&&needsRender){renderer.render(scene,camera);needsRender=false;}});
  stage.dataset.modelTriangles=String(modelData.metadata.triangles);
  stage.dataset.modelSource=modelData.metadata.source;
}
let revision=0;
async function drawModel(version){
  for(const item of items){
    const materials=await materialsFor(item.key);if(version!==revision)return;
    const group=cardBody(geometry,materials);group.userData.item=item;
    item.object=group;world.add(group);applyPosition(item);
    if(interaction==='move'){const button=document.createElement('button');button.type='button';button.textContent=`${cardInfo(item.key).name} ${cardInfo(item.key).rank}`;button.addEventListener('click',()=>flip(item));button.addEventListener('keydown',event=>handleKeys(event,item));item.button=button;applyPosition(item);keyboard.append(button);}
  }
}
function size(){
  const {width,height}=stage.getBoundingClientRect();fit=Math.min(width/520,height/440);
  table.style.setProperty('--fit',fit*state.zoom/100);layer.style.setProperty('--angle',`${state.angle}deg`);
  if(renderer){renderer.setSize(width,height,false);camera.left=-width/(2*fit);camera.right=width/(2*fit);camera.top=height/(2*fit);camera.bottom=-height/(2*fit);camera.updateProjectionMatrix();world.scale.setScalar(state.zoom/100);world.rotation.x=-state.angle*Math.PI/180;needsRender=true;}
}
async function update(next){
  const rebuild=!items.length||stage.dataset.ready!=='true'||next.layout!==state.layout||next.card!==state.card||next.reset!==state.reset;
  const globalBack=next.back!==state.back;
  state=next;held=null;revision++;const version=revision;
  stage.dataset.layout=state.layout;stage.dataset.angle=String(state.angle);stage.dataset.zoom=String(state.zoom);stage.dataset.back=String(state.back);
  size();
  if(!rebuild){
    for(const item of items){if(globalBack)item.back=state.layout==='stack'&&item.index<11?true:state.back;item.element?.classList.remove('is-held');applyPosition(item);}
    return;
  }
  stage.dataset.ready='false';
  if(world){for(const item of items)if(item.object)world.remove(item.object);}
  keyboard.replaceChildren();items=arrange().map((item,index)=>({...item,index}));
  if(mode==='model')await drawModel(version);else await drawFlat();
  if(version!==revision)return;
  stage.dataset.ready='true';stage.dataset.cardCount=String(items.length);announce(`${items.length} ${items.length===1?'Karte':'Karten'}${interaction==='move'?' · frei bewegen':interaction==='select'?' · auswählen':''}`);
}
try{
  if(mode==='model')await initModel();
  await update(state);
  new ResizeObserver(size).observe(stage);
  window.addEventListener('message',event=>{if(event.origin===location.origin&&event.source===parent&&event.data?.type==='card-settings')update(event.data.state).catch(reportError);});
  parent.postMessage({type:'card-ready',mode},location.origin);
}catch(error){reportError(error);}
function reportError(error){announce(`Vorschau nicht verfügbar: ${error.message}`);stage.dataset.ready='error';parent.postMessage({type:'card-error',message:error.message},location.origin);}
