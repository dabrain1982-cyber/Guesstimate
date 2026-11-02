// Normalized contours: x/y in percent, rounding as a share of adjacent edges.
export const cloneContour=value=>structuredClone(value);
export const makeContour=(catalog,template)=>({template,points:catalog.contours[template].map(([x,y,round])=>({x,y,round}))});
// The editable drawing plane is also the physical button's face plane.
export const CONTOUR_PLANE=Object.freeze({width:560,height:180,x:20,y:24});
export const CONTOUR_ASPECT=CONTOUR_PLANE.width/CONTOUR_PLANE.height;
export const BUTTON_WIDTH_UNITS=12;
export function contourPlane(base=null,settings={}){return {...CONTOUR_PLANE,height:base?560*base.height/base.width*(settings.height_ratio??100)/100:180*(settings.height_ratio??100)/100};}
export function buttonMetrics(width,settings,base=null){
  const unit=width/BUTTON_WIDTH_UNITS;
  const scale=base?width/base.width:1;
  return {fontSize:base?base.font_size*scale:unit,height:(base?base.height*scale:width/CONTOUR_ASPECT)*(settings.height_ratio??100)/100,depth:base?settings.depth*scale:unit*settings.depth/16,
    rim:base?settings.edge*scale:unit*settings.edge/20*(settings.style==='comic'?1:settings.style==='natural'?.65:.4)};
}
const cross=(a,b,c)=>(b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x);
function onSegment(a,b,p){return Math.abs(cross(a,b,p))<1e-7&&p.x>=Math.min(a.x,b.x)-1e-7&&p.x<=Math.max(a.x,b.x)+1e-7&&p.y>=Math.min(a.y,b.y)-1e-7&&p.y<=Math.max(a.y,b.y)+1e-7;}
function intersects(a,b,c,d){const x=cross(a,b,c),y=cross(a,b,d),u=cross(c,d,a),v=cross(c,d,b);return (x*y<0&&u*v<0)||onSegment(a,b,c)||onSegment(a,b,d)||onSegment(c,d,a)||onSegment(c,d,b);}
export function contourError(points){
  if(!Array.isArray(points)||points.length<3||points.length>32)return 'Eine Kontur braucht 3 bis 32 Randpunkte.';
  if(points.some(p=>!p||!['x','y','round'].every(k=>typeof p[k]==='number'&&Number.isFinite(p[k]))||p.x<0||p.x>100||p.y<0||p.y>100||p.round<0||p.round>50))return 'Die Punkte müssen innerhalb der Fläche bleiben.';
  let area=0;
  for(let i=0;i<points.length;i++){
    const a=points[i],b=points[(i+1)%points.length];area+=a.x*b.y-b.x*a.y;
    if(Math.hypot(a.x-b.x,a.y-b.y)<.5)return 'Zwei Punkte liegen zu dicht beieinander.';
    for(let j=i+1;j<points.length;j++){
      if(j===i+1||(i===0&&j===points.length-1))continue;
      if(intersects(a,b,points[j],points[(j+1)%points.length]))return 'Die Kontur darf sich nicht selbst kreuzen.';
    }
  }
  return Math.abs(area)<20?'Die Kontur braucht eine größere Fläche.':'';
}
export function roundedPoints(points,plane=null){
  if(plane){
    const physical=points.map(p=>({...p,x:p.x*plane.width/100,y:p.y*plane.height/100})),result=[];
    physical.forEach((p,i)=>{if(!p.round){result.push(p);return;}const a=physical[(i+physical.length-1)%physical.length],b=physical[(i+1)%physical.length];const la=Math.hypot(a.x-p.x,a.y-p.y),lb=Math.hypot(b.x-p.x,b.y-p.y),u={x:(a.x-p.x)/la,y:(a.y-p.y)/la},v={x:(b.x-p.x)/lb,y:(b.y-p.y)/lb},angle=Math.acos(Math.max(-1,Math.min(1,u.x*v.x+u.y*v.y))),d=Math.min(la,lb)*p.round/100;
      if(angle<.01||Math.PI-angle<.01){result.push(p);return;}const r=d*Math.tan(angle/2),length=Math.hypot(u.x+v.x,u.y+v.y),distance=r/Math.sin(angle/2),center={x:p.x+(u.x+v.x)/length*distance,y:p.y+(u.y+v.y)/length*distance},start=Math.atan2(p.y+u.y*d-center.y,p.x+u.x*d-center.x),end=Math.atan2(p.y+v.y*d-center.y,p.x+v.x*d-center.x);let delta=end-start;while(delta>Math.PI)delta-=2*Math.PI;while(delta< -Math.PI)delta+=2*Math.PI;
      for(let step=0;step<=12;step++){const t=start+delta*step/12;result.push({x:center.x+r*Math.cos(t),y:center.y+r*Math.sin(t)});}
    });return result.map(p=>({x:p.x/plane.width*100,y:p.y/plane.height*100}));
  }
  const result=[];
  points.forEach((p,i)=>{
    if(!p.round){result.push({x:p.x,y:p.y});return;}
    const a=points[(i+points.length-1)%points.length],b=points[(i+1)%points.length];
    const la=Math.hypot(a.x-p.x,a.y-p.y),lb=Math.hypot(b.x-p.x,b.y-p.y),r=Math.min(la,lb)*p.round/100;
    const start={x:p.x+(a.x-p.x)*r/la,y:p.y+(a.y-p.y)*r/la},end={x:p.x+(b.x-p.x)*r/lb,y:p.y+(b.y-p.y)*r/lb};
    for(let step=0;step<=8;step++){const t=step/8,u=1-t;result.push({x:u*u*start.x+2*u*t*p.x+t*t*end.x,y:u*u*start.y+2*u*t*p.y+t*t*end.y});}
  });return result;
}
export function toPolygon(points,plane=null){return `polygon(${roundedPoints(points,plane).map(p=>`${p.x.toFixed(3)}% ${p.y.toFixed(3)}%`).join(',')})`;}
export function outlinePath(points,plane=null){const dimensions=plane||CONTOUR_PLANE;return roundedPoints(points,plane).map((p,i)=>`${i?'L':'M'} ${dimensions.x+p.x*dimensions.width/100} ${dimensions.y+p.y*dimensions.height/100}`).join(' ')+' Z';}
