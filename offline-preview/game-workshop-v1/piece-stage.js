// Local, neutral equipment preview; original factories provide every visible piece.
const cfg=JSON.parse(document.querySelector('#piece-config').textContent),host=document.querySelector('#piece-stage'),status=document.querySelector('#piece-status'),turn=document.querySelector('#piece-turn');
async function init(){
  if(cfg.settings.renderer==='design'){
    const {startPieceDesign}=await import('/piece-components/authoring.js');
    await startPieceDesign(cfg,host,status);return;
  }
  const T=await import('/vendor/three.module.js'),scene=new T.Scene();
  const renderer=new T.WebGLRenderer({alpha:true,antialias:true,preserveDrawingBuffer:true});renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.outputColorSpace=T.SRGBColorSpace;
  renderer.domElement.setAttribute('role','img');renderer.domElement.setAttribute('aria-label',cfg.model==='conquest'?'Conquest-Sockel mit originaler Zahlenfläche':cfg.representation.toUpperCase()+' · '+(cfg.model==='chess'?'Sechs Schachrollen, beide Farben':'Damesteine, beide Farben'));
  const group=new T.Group();scene.add(group,new T.HemisphereLight('#fff4dd','#314438',2.1));const light=new T.DirectionalLight('#fff2dc',3);light.position.set(-7,18,10);scene.add(light);
  const camera=cfg.representation==='2d'?new T.OrthographicCamera(-5,5,5,-5,.1,200):new T.PerspectiveCamera(33,1,.1,200);
  const {frameCamera}=await import('/board-source/camera.js');let frame,marker,projectCounters;
  if(cfg.model==='conquest'){
    frame=document.createElement('div');frame.className='piece-source-frame';frame.append(renderer.domElement);host.append(frame);
    const layer=document.createElement('div');layer.className='piece-marker-layer';frame.append(layer);
    const original=await import('/piece-source/conquest.js');projectCounters=original.projectCounters;
    marker=original.makeCounter({owner:original.PREVIEW_ARMIES[0],armies:cfg.settings.count,name:'Beispielmarke',layer});group.add(marker.group);marker.button.inert=true;
  }else{
    host.append(renderer.domElement);const {buildPiece}=await import('/models.js'),pieceCfg=cfg.settings.figure;
    const roles=cfg.model==='chess'?['pawn','rook','knight','bishop','queen','king']:['checker','checker','checker'];
    for(let side=0;side<2;side++)roles.forEach((role,i)=>{const piece=buildPiece(role,pieceCfg,side,1,cfg.representation==='2d');piece.position.set((i-(roles.length-1)/2)*1.02,0,(side-.5)*1.3);group.add(piece);});
  }
  function render(){
    const width=frame?160:host.clientWidth,height=frame?120:host.clientHeight;renderer.setSize(width,height,false);
    if(frame){const scale=Math.min((host.clientWidth-24)/width,(host.clientHeight-(cfg.interactive?56:24))/height);frame.style.transform='scale('+scale+')';frame.style.left=(host.clientWidth-width*scale)/2+'px';frame.style.top=(host.clientHeight-height*scale)/2+'px';}
    const box=marker?new T.Box3(new T.Vector3(-.9,0,-.65),new T.Vector3(.9,.08,.65)):new T.Box3().setFromObject(group),target=box.getCenter(new T.Vector3());
    if(cfg.representation==='2d'){
      const size=box.getSize(new T.Vector3()),half=Math.max(size.z/2,size.x/(2*width/height))*1.12;
      camera.left=-half*width/height;camera.right=half*width/height;camera.top=half;camera.bottom=-half;camera.position.set(target.x,target.y+30,target.z);camera.up.set(0,0,-1);camera.lookAt(target);camera.updateProjectionMatrix();
    }else{
      const points=[];for(const x of [box.min.x,box.max.x])for(const y of [box.min.y,box.max.y])for(const z of [box.min.z,box.max.z])points.push(new T.Vector3(x,y,z));
      frameCamera(camera,{target,points,angle:54,width,height,topPixel:frame?0:16,bottomPixel:height-(frame?0:cfg.interactive?42:16),horizontalLimit:.95,verticalAlignment:.5});
    }
    if(marker)projectCounters(marker.entries,camera,width,height);renderer.render(scene,camera);
  }
  turn.hidden=!cfg.interactive||cfg.representation!=='3d'||!!marker;
  turn.addEventListener('click',()=>{group.rotation.y+=Math.PI/4;render();});new ResizeObserver(render).observe(host);render();
  window.addEventListener('pagehide',()=>renderer.dispose());
}
init().then(()=>{document.body.dataset.state='ready';status.textContent='';}).catch(error=>{document.body.dataset.state='error';status.textContent='Spielsteine konnten nicht geladen werden: '+error.message;});
