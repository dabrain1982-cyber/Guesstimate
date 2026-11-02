// Canonical parametric components for this workshop and future game integration.
import * as T from './vendor/three.module.js';

function mesh(geometry, material, x=0, y=0, z=0) {
  const m = new T.Mesh(geometry, material); m.position.set(x,y,z); m.castShadow=true; m.receiveShadow=true; return m;
}
export function material(color, roughness=.6, metalness=0, flat=false) {
  return flat ? new T.MeshBasicMaterial({color}) : new T.MeshStandardMaterial({color, roughness, metalness});
}
function canvasTexture(draw, width=512, height=512) {
  const c=document.createElement('canvas'); c.width=width; c.height=height;
  draw(c.getContext('2d'),width,height);
  const texture=new T.CanvasTexture(c); texture.colorSpace=T.SRGBColorSpace; return texture;
}
export function buildBoard(cfg, flat=false) {
  if(cfg.width!==undefined)return configuredBoard(cfg,flat);
  const group=new T.Group(), s=cfg.square, w=s*cfg.columns, h=s*cfg.rows;
  group.add(mesh(new T.BoxGeometry(w+cfg.border*2,cfg.thickness,h+cfg.border*2),material(cfg.frame,.55,0,flat),0,-cfg.thickness/2,0));
  const light=material(cfg.light,.7,0,flat), dark=material(cfg.dark,.7,0,flat);
  for(let row=0;row<cfg.rows;row++) for(let col=0;col<cfg.columns;col++) {
    const tile=mesh(new T.BoxGeometry(s*.997,.018,s*.997),cfg.pattern==='checker'&&(col+row)%2?dark:light,(col-(cfg.columns-1)/2)*s,.009,(row-(cfg.rows-1)/2)*s);
    tile.userData.cell={row,col}; group.add(tile);
    if(cfg.pattern==='grid') {
      const line=new T.LineSegments(new T.EdgesGeometry(tile.geometry),new T.LineBasicMaterial({color:cfg.dark})); tile.add(line);
    }
  }
  return group;
}

// Optional authoring properties extend this same factory; older recipes retain their geometry.
function configuredBoard(cfg,flat) {
  const group=new T.Group(),w=cfg.width/10,h=cfg.height/10,border=cfg.border/10,depth=cfg.thickness/10;
  const roughness={matte:.95,satin:.45,gloss:.12}[cfg.finish];
  const frameMat=material(cfg.frame,roughness,0,flat);
  if(cfg.shape==='round') {
    const base=mesh(new T.CylinderGeometry((w+2*border)/2,(w+2*border)/2,depth,96),frameMat,0,-depth/2,0);
    group.add(base);
  } else group.add(mesh(new T.BoxGeometry(w+2*border,depth,h+2*border),frameMat,0,-depth/2,0));
  const texture=canvasTexture((ctx,tw,th)=>{
    ctx.fillStyle=cfg.surface;ctx.fillRect(0,0,tw,th);
    if(cfg.boardImage) {
      const image=cfg.boardImage,scale=(cfg.image_fit==='cover'?Math.max:Math.min)(tw/image.width,th/image.height);
      const iw=image.width*scale,ih=image.height*scale;ctx.drawImage(image,(tw-iw)/2,(th-ih)/2,iw,ih);
    }
    if(cfg.pattern!=='none') {
      ctx.globalAlpha=cfg.pattern_opacity/100;
      if(cfg.pattern==='checker')for(let row=0;row<cfg.rows;row++)for(let col=0;col<cfg.columns;col++) {
        ctx.fillStyle=(row+col)%2?cfg.secondary:cfg.surface;
        ctx.fillRect(col*tw/cfg.columns,row*th/cfg.rows,Math.ceil(tw/cfg.columns),Math.ceil(th/cfg.rows));
      }
      else {
        ctx.strokeStyle=cfg.secondary;ctx.lineWidth=3;ctx.beginPath();
        for(let col=0;col<=cfg.columns;col++){const x=col*tw/cfg.columns;ctx.moveTo(x,0);ctx.lineTo(x,th);}
        for(let row=0;row<=cfg.rows;row++){const y=row*th/cfg.rows;ctx.moveTo(0,y);ctx.lineTo(tw,y);}ctx.stroke();
      }
      ctx.globalAlpha=1;
    }
  },Math.max(256,Math.round(2048*Math.min(1,w/h))),Math.max(256,Math.round(2048*Math.min(1,h/w))));
  texture.anisotropy=8;
  const topMat=flat?new T.MeshBasicMaterial({map:texture,side:T.DoubleSide}):new T.MeshStandardMaterial({map:texture,roughness,side:T.DoubleSide});
  const top=mesh(cfg.shape==='round'?new T.CircleGeometry(w/2,96):new T.PlaneGeometry(w,h),topMat,0,.012,0);
  top.rotation.x=-Math.PI/2;group.add(top);
  group.userData.boardDesign={width:cfg.width,height:cfg.height,shape:cfg.shape,pattern:cfg.pattern,columns:cfg.columns,rows:cfg.rows};
  return group;
}

export const ROLES=['rook','knight','bishop','queen','king','bishop','knight','rook'];
const GLYPHS={pawn:'♟',rook:'♜',knight:'♞',bishop:'♝',queen:'♛',king:'♚',checker:'●'};
const HEIGHTS={pawn:.65,rook:.82,knight:.9,bishop:1,queen:1.1,king:1.2,checker:.18};
export function buildPiece(role, cfg, side, square, flat=false) {
  const group=new T.Group(), color=side?cfg.dark:cfg.light;
  const mat=material(color,cfg.roughness,cfg.metallic,flat);
  const scale=square*.92, h=HEIGHTS[role]*cfg.height;
  if(flat) {
    const texture=canvasTexture((ctx,w,h)=>{
      ctx.fillStyle=color;ctx.beginPath();ctx.arc(w/2,h/2,w*.43,0,Math.PI*2);ctx.fill();
      ctx.strokeStyle=side?cfg.light:cfg.dark;ctx.lineWidth=14;ctx.stroke();
      ctx.fillStyle=side?cfg.light:cfg.dark;ctx.font='370px serif';ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText(GLYPHS[role],w/2,h*.53);
    });
    const top=mesh(new T.PlaneGeometry(.7*cfg.base,.7*cfg.base),new T.MeshBasicMaterial({map:texture,transparent:true,side:T.DoubleSide}),0,.025,0);
    top.rotation.x=-Math.PI/2;group.add(top);
  } else if(role==='checker') {
    group.add(mesh(new T.CylinderGeometry(.35*cfg.base,.37*cfg.base,h,40),mat,0,h/2,0));
    const ring=mesh(new T.TorusGeometry(.26*cfg.base,.018,8,40),mat,0,h+.01,0);ring.rotation.x=Math.PI/2;group.add(ring);
  } else {
    const stem=cfg.stem, base=cfg.base;
    const profile=[[0,0],[.34*base,0],[.37*base,.04],[.36*base,.1],[.27*base,.15],[.23*stem,.2],[.14*stem,h*.48],[.12*stem,h*.65],[.24*stem,h*.7],[.25*stem,h*.76],[0,h*.76]];
    group.add(mesh(new T.LatheGeometry(profile.map(([r,y])=>new T.Vector2(r,y)),cfg.style==='geometric'?8:40),mat));
    const head=cfg.head, y=h*.82;
    if(role==='pawn') group.add(mesh(new T.SphereGeometry(.19*head,24,16),mat,0,y,0));
    if(role==='rook') {
      group.add(mesh(new T.CylinderGeometry(.28*head,.23*head,.19,24),mat,0,y,0));
      for(let i=0;i<6;i++) {const a=i*Math.PI/3;const block=mesh(new T.BoxGeometry(.13*head,.15,.14*head),mat,Math.cos(a)*.23*head,y+.12,Math.sin(a)*.23*head);block.rotation.y=-a;group.add(block);}
    }
    if(role==='bishop') {
      const tip=mesh(new T.SphereGeometry(.22*head,24,16),mat,0,y+.05,0);tip.scale.set(.8,1.5,.8);group.add(tip);
      group.add(mesh(new T.SphereGeometry(.065*head,16,10),mat,0,y+.38,0));
    }
    if(role==='queen') {
      group.add(mesh(new T.CylinderGeometry(.3*head,.14*head,.22,24),mat,0,y+.03,0));
      for(let i=0;i<7;i++) {const a=i*Math.PI*2/7;group.add(mesh(new T.SphereGeometry(.06*head,12,8),mat,Math.cos(a)*.25*head,y+.19,Math.sin(a)*.25*head));}
      group.add(mesh(new T.SphereGeometry(.09*head,16,10),mat,0,y+.25,0));
    }
    if(role==='king') {
      group.add(mesh(new T.SphereGeometry(.18*head,24,16),mat,0,y,0));
      group.add(mesh(new T.BoxGeometry(.095*head,.36*head,.095*head),mat,0,y+.27,0));
      group.add(mesh(new T.BoxGeometry(.29*head,.09*head,.095*head),mat,0,y+.31,0));
    }
    if(role==='knight') {
      const shape=new T.Shape();shape.moveTo(-.2,0);shape.lineTo(-.18,.32);shape.lineTo(.04,.61);shape.lineTo(.12,.69);shape.lineTo(.14,.52);shape.lineTo(.31,.32);shape.lineTo(.26,.17);shape.lineTo(.08,.22);shape.lineTo(.06,0);shape.closePath();
      const neck=mesh(new T.ExtrudeGeometry(shape,{depth:.2,bevelEnabled:true,bevelSize:.025,bevelThickness:.025,bevelSegments:2,steps:1}),mat,0,h*.54,-.1);neck.scale.setScalar(head);group.add(neck);
      const eye=material(side?cfg.light:cfg.dark);
      group.add(mesh(new T.SphereGeometry(.022,10,8),eye,.14*head,h*.54+.4*head,.12*head));
    }
  }
  group.scale.setScalar(scale);group.userData.role=role;return group;
}

export function buildDie(cfg, flat=false) {
  const spots={1:[[0,0]],2:[[-1,-1],[1,1]],3:[[-1,-1],[0,0],[1,1]],4:[[-1,-1],[-1,1],[1,-1],[1,1]],5:[[-1,-1],[-1,1],[1,-1],[1,1],[0,0]],6:[[-1,-1],[-1,0],[-1,1],[1,-1],[1,0],[1,1]]};
  const mats=[1,6,2,5,3,4].map(value=>{
    const map=canvasTexture((ctx,w,h)=>{
      ctx.fillStyle=cfg.color;ctx.fillRect(0,0,w,h);ctx.strokeStyle=cfg.pips;ctx.globalAlpha=.24;ctx.lineWidth=10;ctx.strokeRect(9,9,w-18,h-18);ctx.globalAlpha=1;
      ctx.fillStyle=cfg.pips;for(const [x,y] of spots[value]) {ctx.beginPath();ctx.arc(w/2+x*w*.25,h/2+y*h*.25,w*.065,0,Math.PI*2);ctx.fill();}
    },256,256);
    return flat?new T.MeshBasicMaterial({map}):new T.MeshStandardMaterial({map,roughness:cfg.roughness});
  });
  const die=mesh(new T.BoxGeometry(cfg.size,cfg.size,cfg.size),mats);die.userData.die=true;return die;
}

function textLines(ctx,value,width) {
  const lines=[];let line='';
  for(const char of value) {
    if(char==='\n'){lines.push(line.trim());line='';continue;}
    if(ctx.measureText(line+char).width>width){const split=line.lastIndexOf(' ');if(split>0){lines.push(line.slice(0,split));line=line.slice(split+1);}else{lines.push(line);line='';}}
    line+=char;
  }
  lines.push(line.trim());return lines;
}
function fitText(ctx,value,width,x,y,height,maximum,bold=false) {
  let lines=[],size=maximum;
  for(;size>=10;size--){ctx.font=`${bold?'bold ':''}${size}px Georgia`;lines=textLines(ctx,value,width);if(lines.length*size*1.3<=height)break;}
  for(const line of lines){ctx.fillText(line,x,y);y+=size*1.3;}
}
export function cardTexture(cfg, back=false) {
  return canvasTexture((ctx,w,h)=>{
    ctx.fillStyle=back?cfg.back:cfg.front;ctx.fillRect(0,0,w,h);ctx.strokeStyle=(back?cfg.back_accent:cfg.front_accent)||cfg.accent;ctx.lineWidth=8;ctx.strokeRect(22,22,w-44,h-44);ctx.strokeRect(36,36,w-72,h-72);
    if(back) {
      if(cfg.back_pattern==='none')return;
      ctx.globalAlpha=.65;for(let y=70;y<h-60;y+=50)for(let x=65;x<w-45;x+=50){ctx.beginPath();ctx.moveTo(x,y-12);ctx.lineTo(x+12,y);ctx.lineTo(x,y+12);ctx.lineTo(x-12,y);ctx.closePath();ctx.stroke();}
      return;
    }
    ctx.fillStyle=cfg.ink;ctx.textAlign='center';fitText(ctx,cfg.title,w-95,w/2,cfg.adaptive?Math.max(82,h*.16):100,h*.21,34,true);
    ctx.fillStyle=cfg.symbol_color||cfg.accent;ctx.font=(cfg.adaptive?Math.round(h*.137):100)+'px Georgia';const symbol={crown:'♛',diamond:'◆',star:'★',leaf:'❧'}[cfg.symbol];if(symbol)ctx.fillText(symbol,w/2,h*.46);
    ctx.fillStyle=cfg.ink;fitText(ctx,cfg.text,w-100,w/2,h*.61,h*.29,26);
  },512,Math.round(512/cfg.ratio));
}
export function buildCard(cfg, flat=false, back=false) {
  const height=cfg.size*1.7,width=height*cfg.ratio, edge=material(cfg.accent,.7,0,flat);
  const face=map=>flat?new T.MeshBasicMaterial({map}):new T.MeshStandardMaterial({map,roughness:.85});
  const card=mesh(new T.BoxGeometry(width,.025,height),[edge,edge,face(cardTexture(cfg)),face(cardTexture(cfg,true)),edge,edge]);
  card.userData.card=true;card.userData.back=back;card.rotation.z=back?Math.PI:0;return card;
}

export function disposeGroup(group) {
  const geometries=new Set(),materials=new Set(),textures=new Set();
  group.traverse(o=>{if(o.geometry)geometries.add(o.geometry);for(const m of Array.isArray(o.material)?o.material:o.material?[o.material]:[])materials.add(m);});
  for(const m of materials){if(m.map&&!m.map.userData.shared)textures.add(m.map);m.dispose();}
  for(const g of geometries)g.dispose();for(const t of textures)t.dispose();group.clear();
}
