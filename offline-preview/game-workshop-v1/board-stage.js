// Preview only: original board factories, map and CSS surfaces. No game actions.
const cfg=JSON.parse(document.querySelector('#board-config').textContent),settings=cfg.settings;
const host=document.querySelector('#board-stage'),status=document.querySelector('#board-status'),turn=document.querySelector('#board-turn');
async function init(){
  if(settings.renderer==='design')document.body.classList.add('board-design-preview');
  if(settings.renderer==='image'){
    const img=new Image();img.alt='Conquest · unverändertes Weltbrett';img.src=settings.image.url;await img.decode();host.append(img);return;
  }
  if(settings.renderer==='playtable'||settings.renderer==='dice-table'){
    const frame=document.createElement('div');frame.className='board-source-frame';frame.innerHTML=settings.markup;frame.inert=true;host.append(frame);
    const {width,depth}=settings.size;frame.style.width=width+'px';frame.style.height=depth+'px';
    if(settings.image.crop){const crop=settings.image.crop;frame.firstElementChild.style.left=-crop.x+'px';frame.firstElementChild.style.top=-crop.y+'px';}
    const fit=()=>{const scale=Math.min((host.clientWidth-24)/width,(host.clientHeight-24)/depth);frame.style.transform='scale('+scale+')';frame.style.left=(host.clientWidth-width*scale)/2+'px';frame.style.top=(host.clientHeight-depth*scale)/2+'px';};
    new ResizeObserver(fit).observe(host);fit();return;
  }
  const T=await import('/vendor/three.module.js');
  const scene=new T.Scene(),renderer=new T.WebGLRenderer({alpha:true,antialias:true,preserveDrawingBuffer:true});
  renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.outputColorSpace=T.SRGBColorSpace;renderer.shadowMap.enabled=true;renderer.shadowMap.type=T.PCFSoftShadowMap;
  renderer.domElement.setAttribute('role','img');renderer.domElement.setAttribute('aria-label',cfg.representation==='2d'?'Flaches Feldbrett':'Räumliches Brett');host.append(renderer.domElement);
  let board;
  if(settings.renderer==='conquest'){
    const {makeTable,makeWoodTexture}=await import('/board-source/conquest.js');
    const texture=await new T.TextureLoader().loadAsync(settings.image.url);texture.colorSpace=T.SRGBColorSpace;texture.anisotropy=Math.min(16,renderer.capabilities.getMaxAnisotropy());board=makeTable(texture,makeWoodTexture());
  }else{
    const {buildBoard}=await import('/models.js');
    if(settings.renderer==='design'){
      const design={...settings.design};
      if(settings.image){const img=new Image();img.src=settings.image.url;await img.decode();design.boardImage=img;}
      board=buildBoard(design,cfg.representation==='2d');
      host.dataset.shape=design.shape;host.dataset.pattern=design.pattern;host.dataset.width=design.width;host.dataset.height=design.height;
    }else board=buildBoard(settings.grid,cfg.representation==='2d');
  }
  scene.add(board,new T.HemisphereLight('#fff4dd','#314438',2.1));
  const comparison=new T.Group();
  if(settings.renderer==='design'&&cfg.view?.comparison){
    const {buildCard,buildPiece}=await import('/models.js');
    const card=buildCard({size:1,ratio:2/3,front:'#fff9e9',back:'#527568',ink:'#334d45',accent:'#b96b47',title:'A',text:'',symbol:'diamond'},true);
    card.scale.setScalar(.9/1.7);card.position.set(-.55,.04,0);
    const pawn=buildPiece('pawn',{light:'#eee7da',dark:'#334d45',height:1,base:1,stem:1,head:1,style:'classic',roughness:.6,metallic:0},0,1,false);
    const size=new T.Box3().setFromObject(pawn).getSize(new T.Vector3());pawn.scale.multiplyScalar(.4/size.y);pawn.position.set(.55,0,0);
    comparison.add(card,pawn);scene.add(comparison);
    const caption=document.createElement('p');caption.className='board-comparison-caption';caption.textContent='Vergleich: Karte 6 × 9 cm · Figur 4 cm hoch';document.body.append(caption);
  }
  const light=new T.DirectionalLight('#fff2dc',3);light.position.set(-7,18,10);light.castShadow=true;scene.add(light);
  if(settings.renderer==='design'){light.shadow.mapSize.set(1024,1024);light.shadow.normalBias=.04;light.shadow.bias=-.0001;}
  const cameras={top:new T.OrthographicCamera(-5,5,5,-5,.1,200),angled:new T.PerspectiveCamera(33,1,.1,200)};
  const {frameCamera}=await import('/board-source/camera.js');
  function render(){
    const camera=cfg.representation==='2d'?cameras.top:cameras.angled;
    const width=host.clientWidth,height=host.clientHeight;renderer.setSize(width,height,false);
    const boardBox=new T.Box3().setFromObject(board);comparison.position.z=boardBox.max.z+.8;
    const actualBox=boardBox.clone();if(comparison.children.length)actualBox.union(new T.Box3().setFromObject(comparison));
    const zoom=(cfg.view?.scale||100)/100;
    const box=settings.renderer==='design'&&cfg.view&&!cfg.view.fit?new T.Box3(new T.Vector3(-6/zoom,0,-6/zoom),new T.Vector3(6/zoom,.8,6/zoom)):actualBox;
    const target=box.getCenter(new T.Vector3());
    if(settings.renderer==='design'){
      const clipped=!cfg.view?.fit&&(boardBox.min.x<box.min.x||boardBox.max.x>box.max.x||boardBox.min.z<box.min.z||boardBox.max.z>box.max.z);
      host.dataset.clipped=String(clipped);
      let hint=document.querySelector('.board-size-hint');if(!hint){hint=document.createElement('p');hint.className='board-size-hint';document.body.append(hint);}
      hint.textContent=clipped?'Brett größer als der Ausschnitt · bei Bedarf „Ganzes Brett einpassen“ wählen':'';
    }
    if(cfg.representation==='2d'){
      const size=box.getSize(new T.Vector3()),half=Math.max(size.z/2,size.x/(2*width/height))*1.08;
      camera.left=-half*width/height;camera.right=half*width/height;camera.top=half;camera.bottom=-half;
      camera.position.set(target.x,target.y+30,target.z);camera.up.set(0,0,-1);camera.lookAt(target);camera.updateProjectionMatrix();
    }else{
      const points=[];for(const x of [box.min.x,box.max.x])for(const y of [box.min.y,box.max.y])for(const z of [box.min.z,box.max.z])points.push(new T.Vector3(x,y,z));
      frameCamera(camera,{target,points,angle:54,width,height,topPixel:16,bottomPixel:height-(cfg.interactive?38:16),horizontalLimit:.95,verticalAlignment:.5});
    }
    renderer.render(scene,camera);
  }
  const topView=document.querySelector('#board-top');let overhead=cfg.representation==='2d';
  // The representation stays part of the design; turning or looking from above changes only this view.
  const originalRepresentation=cfg.representation;
  turn.hidden=!cfg.interactive||cfg.representation!=='3d';topView.hidden=turn.hidden;
  turn.addEventListener('click',()=>{board.rotation.y+=Math.PI/4;render();});
  topView.addEventListener('click',()=>{overhead=!overhead;cfg.representation=overhead?'2d':originalRepresentation;topView.textContent=overhead?'Schräg ansehen':'Von oben ansehen';render();});
  new ResizeObserver(render).observe(host);render();window.addEventListener('pagehide',()=>renderer.dispose());
}
init().then(()=>{document.body.dataset.state='ready';status.textContent='';}).catch(error=>{document.body.dataset.state='error';status.textContent='Brett konnte nicht geladen werden: '+error.message;});
