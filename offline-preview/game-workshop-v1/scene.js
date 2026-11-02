import * as T from './vendor/three.module.js';
import {buildBoard,buildPiece,buildDie,buildCard,material,disposeGroup,ROLES} from './models.js';
import {fallStep,ease} from './motion.js';

export class WorkshopScene {
  constructor(host,onMessage) {
    this.host=host;this.onMessage=onMessage;this.scene=new T.Scene();this.world=new T.Group();this.scene.add(this.world);
    this.renderer=new T.WebGLRenderer({antialias:true,alpha:true,preserveDrawingBuffer:true});this.renderer.setPixelRatio(Math.min(devicePixelRatio,2));
    this.renderer.shadowMap.enabled=true;this.renderer.shadowMap.type=T.PCFSoftShadowMap;
    this.renderer.outputColorSpace=T.SRGBColorSpace;this.renderer.toneMapping=T.ACESFilmicToneMapping;this.renderer.toneMappingExposure=1.1;
    this.renderer.domElement.setAttribute('aria-label','Gemeinsame Gestaltungsvorschau');this.renderer.domElement.setAttribute('role','img');host.append(this.renderer.domElement);
    this.ambient=new T.HemisphereLight(0xffffff,0x535749,1.5);this.key=new T.DirectionalLight(0xffefd6,3);this.key.castShadow=true;this.key.shadow.mapSize.set(2048,2048);
    Object.assign(this.key.shadow.camera,{left:-11,right:11,top:11,bottom:-11,near:1,far:40});this.key.shadow.bias=-.0003;
    this.scene.add(this.ambient,this.key);this.textures={};this.jobs=[];this.dice=[];this.cards=[];this.pieces=[];this.raycaster=new T.Raycaster();
    this.resize=new ResizeObserver(()=>this.resizeView());this.resize.observe(host);
    this.renderer.domElement.addEventListener('click',e=>this.pick(e));
    this.last=performance.now();this.renderer.setAnimationLoop(time=>this.tick(time));
    this.renderer.domElement.addEventListener('webglcontextlost',e=>{e.preventDefault();this.onMessage('Die räumliche Vorschau wurde unterbrochen. Bitte diese Seite neu laden.');});
  }
  texture(path) {
    if(!this.textures[path]){const tex=new T.TextureLoader().load(path,()=>this.render());tex.colorSpace=T.SRGBColorSpace;tex.wrapS=tex.wrapT=T.RepeatWrapping;tex.repeat.set(3,3);tex.userData.shared=true;this.textures[path]=tex;}return this.textures[path];
  }
  update(project, selected, focused=false) {
    this.project=project;this.selectedKind=selected;this.jobs=[];this.selected=null;disposeGroup(this.world);this.dice=[];this.cards=[];this.pieces=[];
    this.isolated=focused&&['pieces','board','dice','cards'].includes(selected);
    const e=project.elements,b=e.board,flat=e.camera.mode==='2d', show=k=>this.isolated?k===selected:project.included[k]||selected===k;
    const w=b.square*b.columns,h=b.square*b.rows;
    const tableMat=material(e.background.tint,.8,0,flat);
    if(e.background.table!=='plain') tableMat.map=this.texture('/assets/'+e.background.table+'.png');
    const table=new T.Mesh(new T.BoxGeometry(w+6,.3,h+5),tableMat);table.position.y=-b.thickness-.18;table.receiveShadow=true;this.world.add(table);
    if(show('board'))this.world.add(buildBoard(b,flat));
    if(show('pieces')) {
      const cfg=e.pieces;
      const add=(role,side,row,col)=>{
        const piece=buildPiece(role,cfg,side,b.square,flat);piece.position.set((col-(b.columns-1)/2)*b.square,show('board')?.025:-b.thickness+.025,(row-(b.rows-1)/2)*b.square);
        piece.userData.piece=true;piece.userData.row=row;piece.userData.col=col;piece.userData.side=side;this.world.add(piece);this.pieces.push(piece);
      };
      if(cfg.arrangement==='samples'||this.isolated) {
        const roles=cfg.set==='chess'?['pawn','rook','knight','bishop','queen','king']:['checker','checker','checker'];
        for(let side=0;side<2;side++) roles.forEach((r,i)=>add(r,side,b.rows/2-1+side*2,(b.columns-roles.length)/2+i));
      }else if(cfg.set==='checkers') {
        for(let side=0;side<2;side++)for(let row=0;row<Math.min(3,Math.floor(b.rows/2)-1);row++)for(let col=0;col<b.columns;col++){
          const actual=side?b.rows-1-row:row;if((actual+col)%2)add('checker',side,actual,col);
        }
      }else {
        for(let side=0;side<2;side++)for(let col=0;col<b.columns;col++) {add(ROLES[col%8],side,side?b.rows-1:0,col);add('pawn',side,side?b.rows-2:1,col);}
      }
    }
    if(show('dice')) for(let i=0;i<e.dice.count;i++) {
      const die=buildDie(e.dice,flat);die.position.set((i-(e.dice.count-1)/2)*(e.dice.size+.25),-b.thickness+e.dice.size/2,this.isolated?0:h/2+1);this.world.add(die);this.dice.push(die);
    }
    if(show('cards')) for(let i=0;i<2;i++) {
      const card=buildCard(e.cards,flat,!!i);card.position.set(this.isolated?(i-.5)*e.cards.size*1.7*e.cards.ratio*1.25:w/2+1.3,-b.thickness+.08,this.isolated?0:(i-.5)*e.cards.size*1.9);this.world.add(card);this.cards.push(card);
    }
    this.ambient.intensity=project.included.room?e.room.ambient:1.5;
    this.key.intensity=project.included.room?e.room.light:3;
    const a=e.room.angle*Math.PI/180;this.key.position.set(Math.sin(a)*9,12,Math.cos(a)*9);
    this.renderer.shadowMap.enabled=!flat&&project.included.room&&e.room.shadows;
    const image={studio:null,room:'/assets/room.png',club:'/shared/stormseeds-perfect-clubroom-table-v2.png',cards:'/shared/card-tables-background-v1.png'}[e.background.image];
    this.host.style.backgroundColor=e.background.color;this.host.style.backgroundImage=image?`url("${image}")`:'none';
    this.fitCamera();this.render();
  }
  fitCamera() {
    if(!this.project)return;
    const cfg={...this.project.elements.camera}, width=this.host.clientWidth||600,height=this.host.clientHeight||500,aspect=width/height;
    if(this.isolated&&this.selectedKind!=='board'){cfg.distance={pieces:9,cards:4,dice:5}[this.selectedKind];cfg.elevation=this.selectedKind==='cards'?75:50;}
    this.viewDistance=cfg.distance;
    if(cfg.mode==='3d')this.camera=new T.PerspectiveCamera(cfg.fov,aspect,.1,100);
    else {const span=cfg.distance*.67;this.camera=new T.OrthographicCamera(-span*aspect/2,span*aspect/2,span/2,-span/2,.1,100);}
    const elevation=(cfg.mode==='2d'?89.99:cfg.elevation)*Math.PI/180,yaw=cfg.rotation*Math.PI/180,distance=cfg.distance;
    const offset=this.cards.length&&!this.isolated?.55:0;
    if(cfg.mode==='2d'){this.camera.up.set(0,0,-1);this.camera.position.set(offset,distance,.15);}
    else this.camera.position.set(offset+Math.sin(yaw)*Math.cos(elevation)*distance,Math.sin(elevation)*distance,Math.cos(yaw)*Math.cos(elevation)*distance);
    this.camera.lookAt(offset,0,.15);this.camera.updateProjectionMatrix();this.resizeView();
  }
  resizeView(){const w=this.host.clientWidth,h=this.host.clientHeight;if(!w||!h)return;this.renderer.setSize(w,h);if(this.camera){if(this.camera.isPerspectiveCamera)this.camera.aspect=w/h;else{const half=this.viewDistance*.67/2;this.camera.left=-half*w/h;this.camera.right=half*w/h;}this.camera.updateProjectionMatrix();this.render();}}
  render(){if(this.camera)this.renderer.render(this.scene,this.camera);}
  tick(time) {
    const dt=Math.min((time-this.last)/1000,.035);this.last=time;
    if(!this.jobs.length)return;
    this.jobs=this.jobs.filter(job=>!job(dt,time));this.render();
  }
  roll() {
    if(!this.dice.length){this.onMessage('Nimm Würfel in die Projektmappe auf oder öffne ihren Editor.');return;}
    const room=this.project.elements.room,b=this.project.elements.board,cfg=this.project.elements.dice,animated=room.dice;
    this.jobs=[];const results=[];
    // Face order in buildDie: +X 1, -X 6, +Y 2, -Y 5, +Z 3, -Z 4.
    const rotations={1:[0,0,Math.PI/2],6:[0,0,-Math.PI/2],2:[0,0,0],5:[Math.PI,0,0],3:[-Math.PI/2,0,0],4:[Math.PI/2,0,0]};
    for(const die of this.dice) {
      const result=1+Math.floor(Math.random()*6);results.push(result);const target=new T.Quaternion().setFromEuler(new T.Euler(...rotations[result]));
      die.userData.result=result;const floor=-b.thickness+cfg.size/2;
      if(!animated){die.position.y=floor;die.quaternion.copy(target);continue;}
      let body={y:2+Math.random(),velocity:2,resting:false},elapsed=0;
      die.position.y=body.y;
      this.jobs.push(dt=>{elapsed+=dt;body=fallStep(body,dt,room.gravity,room.bounce,floor);die.position.y=body.y;
        if(body.resting||elapsed>6){die.position.y=floor;die.quaternion.slerp(target,Math.min(1,dt*14));if(die.quaternion.angleTo(target)<.01){die.quaternion.copy(target);return true;}}
        else {die.rotation.x+=dt*7;die.rotation.z+=dt*5;}return false;
      });
    }
    this.render();this.onMessage('Wurfprobe: '+results.join(' · ')+'. Tischkontakt; keine Kollision zwischen Würfeln.');
  }
  flip() {
    const mode=this.project.elements.room.cards;if(mode==='off'){this.onMessage('Kartenbewegung ist ausgeschaltet.');return;}
    if(!this.cards.length){this.onMessage('Nimm Karten auf oder öffne ihren Editor.');return;}
    for(const card of this.cards) {
      card.userData.back=!card.userData.back;const from=card.rotation.z,to=card.userData.back?Math.PI:0;let elapsed=0;
      if(mode==='snap')card.rotation.z=to;
      else this.jobs.push(dt=>{elapsed+=dt;const t=ease(elapsed/.65);card.rotation.z=from+(to-from)*t;card.position.y=-this.project.elements.board.thickness+.08+Math.sin(t*Math.PI)*1.1;return elapsed>=.65;});
    }this.render();this.onMessage('Karten gewendet.');
  }
  pick(event) {
    const cfg=this.project.elements.room;if(cfg.pieces==='off')return;
    const rect=this.renderer.domElement.getBoundingClientRect();this.raycaster.setFromCamera(new T.Vector2((event.clientX-rect.left)/rect.width*2-1,1-(event.clientY-rect.top)/rect.height*2),this.camera);
    const hit=this.raycaster.intersectObjects(this.world.children,true).find(h=>{let o=h.object;while(o&&o!==this.world){if(o.userData.piece||o.userData.cell)return true;o=o.parent;}return false;});
    if(!hit)return;let object=hit.object;while(!object.userData.piece&&!object.userData.cell)object=object.parent;
    if(object.userData.piece){this.selected=object;this.onMessage('Figur gewählt. Klicke auf ein freies Zielfeld. Die Probe prüft keine Spielregeln.');return;}
    if(!this.selected)return;const cell=object.userData.cell;
    if(this.pieces.some(p=>p!==this.selected&&p.userData.row===cell.row&&p.userData.col===cell.col)){this.onMessage('Dieses Feld ist belegt. Wähle ein freies Feld.');return;}
    const piece=this.selected,from=piece.position.clone(),target=object.position.clone();target.y=.025;piece.userData.row=cell.row;piece.userData.col=cell.col;this.selected=null;
    if(cfg.pieces==='snap')piece.position.copy(target);else {let t=0;this.jobs.push(dt=>{t+=dt/.5;piece.position.lerpVectors(from,target,ease(t));return t>=1;});}
    this.render();this.onMessage('Bewegungsprobe ausgeführt. Aufstellung wird beim nächsten Gestalten zurückgesetzt.');
  }
}
