const cfg=JSON.parse(document.querySelector('#room-config').textContent),settings=cfg.settings,host=document.querySelector('#room-stage'),status=document.querySelector('#room-status'),view=document.querySelector('#room-view');
async function init(){
  if(settings.renderer==='css'){host.innerHTML=settings.markup;host.inert=true;await Promise.all(settings.images.map(async url=>{const image=new Image();image.src=url;await image.decode();}));await document.fonts.ready;return;}
  const T=await import('/vendor/three.module.js'),{mountRoom}=await import('/room-source/conquest.js'),{BOARD_WIDTH,BOARD_DEPTH,BOARD_Y}=await import('/room-source/territory-model.js');
  const {frameCamera,MIN_ANGLE,MAX_ANGLE}=await import('/board-source/camera.js');
  const renderer=new T.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});renderer.setPixelRatio(Math.min(Math.max(devicePixelRatio,1),1.5));renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1.25;
  const scene=new T.Scene();scene.background=new T.Color('#21150e');const camera=new T.PerspectiveCamera(40,1,.15,200);
  renderer.domElement.setAttribute('role','img');renderer.domElement.setAttribute('aria-label','Conquest · ursprüngliche Wand, Möbel und Teppich als gemeinsamer Raum');host.append(renderer.domElement);
  const textures=await Promise.all(settings.layers.map(name=>new T.TextureLoader().loadAsync('/room-source/'+name)));for(const texture of textures){texture.colorSpace=T.SRGBColorSpace;texture.anisotropy=Math.min(16,renderer.capabilities.getMaxAnisotropy());}mountRoom(scene,...textures);
  let angle=MIN_ANGLE;
  function render(){const width=host.clientWidth,height=host.clientHeight;if(!width||!height)return;renderer.setSize(width,height,false);const points=[];for(const x of [-BOARD_WIDTH/2,BOARD_WIDTH/2])for(const z of [-BOARD_DEPTH/2,BOARD_DEPTH/2])points.push(new T.Vector3(x,BOARD_Y,z));frameCamera(camera,{target:new T.Vector3(0,2.85,0),points,angle,width,height,topPixel:4,bottomPixel:height-4,horizontalLimit:.98,verticalAlignment:1});renderer.render(scene,camera);}
  view.hidden=!cfg.interactive;view.addEventListener('click',()=>{angle=angle===MIN_ANGLE?Math.min(MAX_ANGLE,54):MIN_ANGLE;render();});new ResizeObserver(render).observe(host);render();window.addEventListener('pagehide',()=>renderer.dispose());
}
init().then(()=>{document.body.dataset.state='ready';status.textContent='';}).catch(error=>{document.body.dataset.state='error';status.textContent='Raumkulisse konnte nicht geladen werden: '+error.message;});
