// A neutral equipment view. All figures and comparison objects use existing factories.
import * as T from '/vendor/three.module.js';
import {buildPiece,buildCard,disposeGroup} from '/models.js';
import {frameCamera} from '/board-source/camera.js';

export async function startPieceDesign(cfg,host,status){
  document.body.classList.add('piece-design-preview');
  const s=cfg.settings.figure,v=cfg.view,flat=s.representation==='2d';
  const scene=new T.Scene(),renderer=new T.WebGLRenderer({alpha:true,antialias:true,preserveDrawingBuffer:true});
  renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.outputColorSpace=T.SRGBColorSpace;
  renderer.domElement.setAttribute('role','img');renderer.domElement.setAttribute('aria-label','Dein Figurensatz'+(v.comparison?' mit sichtbarem Größenvergleich':''));host.append(renderer.domElement);
  scene.add(new T.HemisphereLight('#fff8e8','#3f5048',2));const light=new T.DirectionalLight('#fff2db',2.7);light.position.set(-3,8,5);scene.add(light);
  const equipment=new T.Group(),comparison=new T.Group();scene.add(equipment,comparison);
  const roles=s.set==='checkers'?['checker']:v.role==='all'?['pawn','rook','knight','bishop','queen','king']:[v.role];
  const sides=v.side==='both'?[0,1]:[v.side==='dark'?1:0];
  for(const side of sides)roles.forEach((role,index)=>{
    const piece=buildPiece(role,s,side,1,flat);piece.scale.multiplyScalar(s.size/100);
    if(roles.length>1)piece.position.set((index-(roles.length-1)/2)*1.3,0,(side-.5)*1.3);
    else piece.position.set(sides.length>1?(side-.5)*1.35:0,0,0);
    equipment.add(piece);
  });
  const sizes=document.createElement('p');sizes.className='piece-dimensions';
  const sample=equipment.children[0],sampleSize=new T.Box3().setFromObject(sample).getSize(new T.Vector3());
  const sizeText=flat?'Musterfigur: '+(sampleSize.x*10).toFixed(1).replace('.',',')+' cm breit':'Musterfigur: '+(sampleSize.y*10).toFixed(1).replace('.',',')+' cm hoch';sizes.textContent=sizeText;document.body.append(sizes);
  if(v.comparison){
    const reference=buildPiece('pawn',{light:'#82918a',dark:'#82918a',height:1.8,base:.75,stem:1,head:.8,style:'classic',roughness:.7,metallic:0},0,1,flat);
    const bounds=new T.Box3().setFromObject(reference).getSize(new T.Vector3());reference.scale.multiplyScalar(flat?.3/bounds.x:.4/bounds.y);
    reference.position.set(roles.length>1?4.7:2.05,0,.1);comparison.add(reference);
    const card=buildCard({size:1,ratio:2/3,front:'#fff9e9',back:'#527568',ink:'#334d45',accent:'#b96b47',title:'A',text:'',symbol:'diamond'},true);
    card.scale.setScalar(.9/1.7);
    if(!flat)card.rotation.x=Math.PI/2;
    card.position.set(reference.position.x,flat?.02:.45,flat?-.85:-.45);comparison.add(card);
    const legend=document.createElement('p');legend.className='piece-comparison-caption';legend.textContent=flat?'Grau: Vergleichsmarke 3 cm breit · Karte 6 × 9 cm':'Grau: Vergleichsfigur 4 cm hoch · Karte 6 × 9 cm';document.body.append(legend);
  }
  const cameras={top:new T.OrthographicCamera(-3,3,3,-3,.1,200),angled:new T.PerspectiveCamera(33,1,.1,200)};
  let overhead=flat;
  function render(){
    const width=host.clientWidth,height=host.clientHeight;renderer.setSize(width,height,false);
    const actual=new T.Box3().setFromObject(equipment);if(comparison.children.length)actual.union(new T.Box3().setFromObject(comparison));
    const z=v.scale/100,all=roles.length>1;
    const fixed=all?new T.Box3(new T.Vector3(-5/z,0,-2/z),new T.Vector3(6/z,1.8/z,2/z)):new T.Box3(new T.Vector3(-1.7/z,0,-1.4/z),new T.Vector3(2.8/z,1.5/z,1.1/z));
    const clipped=!v.fit&&(actual.min.x<fixed.min.x||actual.max.x>fixed.max.x||actual.max.y>fixed.max.y||actual.min.z<fixed.min.z||actual.max.z>fixed.max.z);
    sizes.textContent=sizeText+(clipped?' · Bei Bedarf „Alles einpassen“ wählen':'');
    const box=v.fit?actual:fixed,target=box.getCenter(new T.Vector3()),camera=overhead?cameras.top:cameras.angled;
    if(overhead){
      const size=box.getSize(new T.Vector3()),half=Math.max(size.z/2,size.x/(2*width/height))*1.14;
      camera.left=-half*width/height;camera.right=half*width/height;camera.top=half;camera.bottom=-half;camera.position.set(target.x,20,target.z);camera.up.set(0,0,-1);camera.lookAt(target);camera.updateProjectionMatrix();
    }else{
      const points=[];for(const x of [box.min.x,box.max.x])for(const y of [box.min.y,box.max.y])for(const z of [box.min.z,box.max.z])points.push(new T.Vector3(x,y,z));
      frameCamera(camera,{target,points,angle:42,width,height,topPixel:20,bottomPixel:height-(cfg.interactive?68:20),horizontalLimit:.94,verticalAlignment:.5});
    }
    renderer.render(scene,camera);
  }
  const turn=document.querySelector('#piece-turn');turn.hidden=!cfg.interactive||flat;turn.addEventListener('click',()=>{equipment.rotation.y+=Math.PI/4;render();});
  const top=document.querySelector('#piece-top');top.hidden=turn.hidden;top.addEventListener('click',()=>{overhead=!overhead;top.textContent=overhead?'Schräg ansehen':'Von oben ansehen';render();});
  const observer=new ResizeObserver(render);observer.observe(host);render();
  host.dataset.size=String(s.size);host.dataset.role=roles.join(',');host.dataset.comparison=String(v.comparison);host.dataset.fixedScale=String(!v.fit);
  window.addEventListener('pagehide',()=>{observer.disconnect();disposeGroup(equipment);disposeGroup(comparison);renderer.dispose();});
}
