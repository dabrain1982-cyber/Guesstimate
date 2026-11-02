import * as T from '/vendor/three.module.js';
import {cardTexture,disposeGroup} from '/models.js';
import {originalCard} from '/original/card.js';
import {cardGeometries,cardBody,cardMaterials} from '/card-components/body.js';
const cfg=JSON.parse(document.querySelector('#card-design-config').textContent),s=cfg.settings,v=cfg.view;
const host=document.querySelector('#card-design-stage'),status=document.querySelector('#card-design-status'),caption=document.querySelector('#card-design-caption');
const selected=cfg.members.find(m=>m.id===v.member_id);
const design={...s,...selected,accent:s.front_accent,adaptive:true};
const front=cardTexture(design),back=cardTexture(design,true);
const ownWidth=s.height*s.ratio/10;
const entries=(v.face==='both'?[false,true]:[v.face==='back']).map((back,index,list)=>({back,x:list.length===2?(index?0:-ownWidth-.35):-.35,height:s.height/10,ratio:s.ratio}));
if(v.comparison)entries.push({reference:true,back:false,x:Math.max(1.35,ownWidth/2+.55),height:.9,ratio:2/3});
let renderer,world,observer;
async function init(){
  let redraw;
  if(s.representation==='2d'){
    const layer=document.createElement('div');layer.className='card-design-flat';host.append(layer);
    for(const entry of entries){
      const element=originalCard({id:'example',suit:'hearts',rank:'7',symbol:'♥',color:'red',face_up:!entry.back,zone:'table',x:50,y:50,z:1},()=>{});
      element.inert=true;element.draggable=false;element.tabIndex=-1;element.setAttribute('role','img');element.setAttribute('aria-label',entry.reference?'Vergleichskarte 6 × 9 cm':(entry.back?'Rückseite':'Vorderseite')+' · '+(selected.title||'Deine Karte'));
      for(const [selector,texture] of [['.playing-card-front',front],['.playing-card-back',back]]){
        const face=element.querySelector(selector);face.replaceChildren();const image=new Image();image.className='card-design-art';image.alt='';image.src=entry.reference?'/assets/kenney/cardHearts7.png':texture.image.toDataURL();face.append(image);
      }
      if(entry.reference)element.classList.add('card-design-reference');entry.element=element;layer.append(element);
    }
    await Promise.all([...layer.querySelectorAll('img')].map(image=>image.decode()));
    redraw=(k,cx)=>{for(const e of entries){e.element.style.width=e.height*e.ratio*k+'px';e.element.style.height=e.height*k+'px';e.element.style.left=host.clientWidth/2+(e.x-cx)*k+'px';e.element.style.top=host.clientHeight/2+'px';e.element.style.transform='translate(-50%,-50%)';}};
  }else{
    const response=await fetch('/assets/mehrasaur/card-mesh.json');if(!response.ok)throw Error('Der gemeinsame Kartenkörper fehlt.');const data=await response.json();
    const geometries=cardGeometries(data),bounds=new T.Box3();for(const geometry of geometries.values())bounds.union(new T.Box3().setFromBufferAttribute(geometry.attributes.position));const dims=bounds.getSize(new T.Vector3());
    renderer=new T.WebGLRenderer({alpha:true,antialias:true,preserveDrawingBuffer:true});renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.NeutralToneMapping;
    renderer.domElement.setAttribute('role','img');renderer.domElement.setAttribute('aria-label','Dein Kartensatz · '+(v.face==='both'?'Vorder- und Rückseite':v.face==='back'?'Rückseite':'Vorderseite'));host.append(renderer.domElement);
    const scene=new T.Scene();world=new T.Group();if(v.tilt)world.rotation.set(-.18,.2,0);scene.add(world,new T.HemisphereLight('#fff6df','#5b796d',1.2));const light=new T.DirectionalLight('#fff4db',2);light.position.set(-220,360,600);scene.add(light);
    const materials=cardMaterials(front,back,s.edge);
    let referenceMaterials;
    if(v.comparison){const texture=await new T.TextureLoader().loadAsync('/assets/kenney/cardHearts7.png');texture.colorSpace=T.SRGBColorSpace;referenceMaterials=cardMaterials(texture,texture,'#a2b0a7');}
    for(const e of entries){const object=cardBody(geometries,e.reference?referenceMaterials:materials);object.scale.set(e.height*e.ratio/dims.x,e.height/dims.y,.003/dims.z);object.position.x=e.x;object.rotation.y=e.back?Math.PI:0;world.add(object);}
    const camera=new T.OrthographicCamera(-2,2,1.5,-1.5,.1,100);camera.position.set(.2,0,20);camera.lookAt(.2,0,0);
    redraw=(k,cx)=>{const w=host.clientWidth,h=host.clientHeight;renderer.setSize(w,h,false);camera.left=-w/(2*k)+cx-.2;camera.right=w/(2*k)+cx-.2;camera.top=h/(2*k);camera.bottom=-h/(2*k);camera.updateProjectionMatrix();renderer.render(scene,camera);};
  }
  const render=()=>{
    const width=host.clientWidth,height=host.clientHeight,zoom=v.scale/100;
    const left=Math.min(...entries.map(e=>e.x-e.height*e.ratio/2)),right=Math.max(...entries.map(e=>e.x+e.height*e.ratio/2)),tall=Math.max(...entries.map(e=>e.height));
    const k=v.fit?Math.min((width-60)/(right-left),(height-90)/tall):Math.min(width/3.6,height/2.2)*zoom;
    const cx=v.fit?(left+right)/2:.2;redraw(k,cx);
    status.textContent=(s.height*s.ratio).toFixed(1).replace('.',',')+' × '+String(s.height).replace('.',',')+' cm · '+(selected.title||'Ohne Titel');
    if(!v.fit&&((right-left)*k>width-20||tall*k>height-50))status.textContent+=' · Bei Bedarf „Alles einpassen“ wählen';
  };
  observer=new ResizeObserver(render);observer.observe(host);render();
  caption.textContent=v.comparison?'Vergleichskarte rechts: 6 × 9 cm · gehört nur zur Vorschau':'';
  document.body.dataset.state='ready';host.dataset.member=selected.id;host.dataset.height=String(s.height);host.dataset.comparison=String(v.comparison);
}
init().catch(error=>{document.body.dataset.state='error';status.textContent='Die Karte konnte nicht geladen werden: '+error.message;});
window.addEventListener('pagehide',()=>{observer?.disconnect();if(world)disposeGroup(world);else{front.dispose();back.dispose();}renderer?.dispose();});
