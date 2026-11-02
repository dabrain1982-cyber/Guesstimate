import {button} from '/shared/components.js';
import {cloneContour,makeContour,contourError,outlinePath,contourPlane} from './geometry.js';

const NS='http://www.w3.org/2000/svg';
const copy=value=>structuredClone(value);
export class ContourEditor {
  constructor(host,catalog,onChange){
    this.catalog=catalog;this.onChange=onChange;this.selected=0;this.undo=[];this.redo=[];this.plane=contourPlane();this.physical=false;
    host.innerHTML=`<p class="contour-intro">Ziehe die Randpunkte. Mit Doppelklick auf eine Kante kommt ein Punkt dazu. Pfeiltasten bewegen den ausgewählten Punkt.</p>
      <svg id="contour-canvas" viewBox="0 0 600 228" aria-label="Kontur bearbeiten" role="group">
        <defs><pattern id="contour-grid" width="28" height="18" patternUnits="userSpaceOnUse"><path d="M 28 0 L 0 0 0 18" fill="none" stroke="#aebba633" stroke-width="1"/></pattern></defs>
        <rect width="600" height="228" rx="12" fill="#e9eddf"/><rect x="20" y="24" width="560" height="180" fill="url(#contour-grid)" stroke="#a3b392" stroke-dasharray="3 4"/>
        <path class="contour-shadow" fill="#26352e" transform="translate(0 5)"/>
        <path class="contour-fill" fill="#c9de9e" stroke="#364b37" stroke-width="2"/>
        <g class="contour-handles"></g>
      </svg>
      <div class="point-fields"><div><label for="selected-point">Ausgewählter Punkt</label><select id="selected-point"></select></div><div><label for="point-x">X-Position (%)</label><input id="point-x" type="number" min="0" max="100" step="any"></div><div><label for="point-y">Y-Position (%)</label><input id="point-y" type="number" min="0" max="100" step="any"></div><div class="rounding-field"><label for="point-round">Rundung dieses Punkts <output id="point-round-value"></output></label><input id="point-round" type="range" min="0" max="50" step="1"></div></div>
      <div class="contour-actions"><span id="point-add"></span><span id="point-remove"></span><span id="contour-undo"></span><span id="contour-redo"></span><span id="contour-reset"></span></div>
      <p id="contour-status" class="contour-status" role="status"></p>`;
    this.host=host;this.svg=host.querySelector('svg');this.handles=host.querySelector('.contour-handles');
    this.picker=host.querySelector('#selected-point');
    const tool=(selector,label,action)=>{const item=button({label,small:true,variant:'secondary',action});host.querySelector(selector).append(item.element);return item.element;};
    this.addButton=tool('#point-add','punkt hinzufügen',()=>this.add());
    this.removeButton=tool('#point-remove','punkt entfernen',()=>this.remove());
    this.undoButton=tool('#contour-undo','rückgängig',()=>this.travel(false));
    this.redoButton=tool('#contour-redo','wiederholen',()=>this.travel(true));
    tool('#contour-reset','grundform zurücksetzen',()=>{this.resetBase();this.message('Grundform wiederhergestellt. Rückgängig holt deine Änderung zurück. Es wurde nichts gespeichert.');});
    this.picker.addEventListener('change',()=>{this.selected=Number(this.picker.value);this.draw();});
    for(const key of ['x','y','round']){
      const input=host.querySelector('#point-'+key);
      input.addEventListener('focus',()=>{this.inputBefore=this.snapshot();});
      input.addEventListener('pointerdown',()=>{this.inputBefore=this.snapshot();});
      input.addEventListener('input',()=>{
        if(!Number.isFinite(input.valueAsNumber))return;
        this.inputBefore??=this.snapshot();
        const next=cloneContour(this.contour);next.points[this.selected][key]=input.valueAsNumber;
        if(this.accept(next)){this.shape='custom';this.draw();this.publish();}
        else input.value=this.contour.points[this.selected][key];
      });
      input.addEventListener('change',()=>{if(this.inputBefore)this.remember(this.inputBefore);this.inputBefore=null;input.value=this.contour.points[this.selected][key];this.draw();});
    }
    this.svg.addEventListener('pointerdown',event=>{
      const handle=event.target.closest('[data-point]');if(!handle||event.button!==0)return;
      event.preventDefault();this.selected=Number(handle.dataset.point);handle.focus({preventScroll:true});
      this.drag={before:this.snapshot(),pointer:event.pointerId};this.svg.setPointerCapture(event.pointerId);this.draw();
    });
    this.svg.addEventListener('pointermove',event=>{
      if(!this.drag||event.pointerId!==this.drag.pointer)return;
      const next=cloneContour(this.contour),p=this.position(event);next.points[this.selected]={...next.points[this.selected],...p};
      if(this.accept(next)){this.shape='custom';this.draw();this.publish();}
    });
    const end=event=>{if(!this.drag||event.pointerId!==this.drag.pointer)return;this.remember(this.drag.before);this.drag=null;this.draw();};
    this.svg.addEventListener('pointerup',end);this.svg.addEventListener('pointercancel',end);
    this.svg.addEventListener('focusin',event=>{const handle=event.target.closest('[data-point]');if(handle){this.selected=Number(handle.dataset.point);this.draw();}});
    this.svg.addEventListener('dblclick',event=>{
      if(event.target.closest('[data-point]'))return;
      const p=this.position(event);let closest;
      this.contour.points.forEach((a,i)=>{
        const b=this.contour.points[(i+1)%this.contour.points.length],dx=(b.x-a.x)*this.plane.width/100,dy=(b.y-a.y)*this.plane.height/100;
        const t=Math.max(0,Math.min(1,((p.x-a.x)*this.plane.width/100*dx+(p.y-a.y)*this.plane.height/100*dy)/(dx*dx+dy*dy)));
        const q={x:a.x+(b.x-a.x)*t,y:a.y+(b.y-a.y)*t};const distance=Math.hypot((q.x-p.x)*this.plane.width/100,(q.y-p.y)*this.plane.height/100);
        if(!closest||distance<closest.distance)closest={i,q,distance};
      });
      if(closest.distance>24){this.message('Doppelklicke direkt auf eine Kante.');return;}
      this.add(closest.i,closest.q);
    });
    this.svg.addEventListener('keydown',event=>{
      const handle=event.target.closest('[data-point]');if(!handle)return;
      this.selected=Number(handle.dataset.point);
      if(event.key===' '||event.key==='Enter'){event.preventDefault();this.draw();return;}
      if(event.key==='Delete'||event.key==='Backspace'){event.preventDefault();this.remove();return;}
      const direction={ArrowLeft:['x',-1],ArrowRight:['x',1],ArrowUp:['y',-1],ArrowDown:['y',1]}[event.key];
      if(!direction)return;event.preventDefault();const before=this.snapshot(),next=cloneContour(this.contour),[key,amount]=direction;
      next.points[this.selected][key]=Math.max(0,Math.min(100,next.points[this.selected][key]+amount*(event.shiftKey?5:.5)));
      if(this.accept(next)){this.shape='custom';this.remember(before);this.draw();this.publish();}
    });
  }
  setLayout(base=null,settings={}){this.plane=contourPlane(base,settings);this.origin=base?.contour||null;this.physical=!!base||(settings.height_ratio??100)!==100;const h=this.plane.height+48;this.svg.setAttribute('viewBox',`0 0 600 ${h}`);const rectangles=this.svg.querySelectorAll(':scope > rect');rectangles[0].setAttribute('height',h);rectangles[1].setAttribute('height',this.plane.height);if(this.contour)this.draw();}
  resetBase(){const before=this.snapshot();this.contour=this.origin?.template===this.contour.template?cloneContour(this.origin):makeContour(this.catalog,this.contour.template);this.shape='custom';this.selected=0;this.remember(before);this.draw();this.publish();}
  position(event){const box=this.svg.getBoundingClientRect(),p=this.plane;return {x:Math.round(Math.max(0,Math.min(100,((event.clientX-box.left)/box.width*600-p.x)/p.width*100))*10)/10,y:Math.round(Math.max(0,Math.min(100,((event.clientY-box.top)/box.height*(p.height+48)-p.y)/p.height*100))*10)/10};}
  snapshot(){return {contour:cloneContour(this.contour),shape:this.shape,selected:this.selected};}
  load(contour,shape){this.contour=cloneContour(contour);this.initial=cloneContour(contour);this.shape=shape;this.selected=0;this.undo=[];this.redo=[];this.inputBefore=null;this.draw();}
  applySaved(contour){const before=this.snapshot();this.contour=cloneContour(contour);this.shape='custom';this.selected=0;this.remember(before);this.draw();this.publish();}
  accept(next){const error=contourError(next.points);if(error){this.message(error);return false;}this.contour=next;this.message();return true;}
  remember(before){if(JSON.stringify(before.contour)===JSON.stringify(this.contour)&&before.shape===this.shape)return;this.undo.push(before);if(this.undo.length>80)this.undo.shift();this.redo=[];this.syncButtons();}
  publish(){this.onChange(cloneContour(this.contour),this.shape);}
  setTemplate(template){const before=this.snapshot();this.contour=makeContour(this.catalog,template);this.shape=template;this.selected=0;this.remember(before);this.draw();this.publish();}
  add(index=this.selected,position=null){
    if(this.contour.points.length>=32){this.message('Höchstens 32 Randpunkte sind möglich.');return;}
    const before=this.snapshot(),next=cloneContour(this.contour),a=next.points[index],b=next.points[(index+1)%next.points.length];
    const p=position||{x:(a.x+b.x)/2,y:(a.y+b.y)/2};
    next.points.splice(index+1,0,{x:Math.round(p.x*100)/100,y:Math.round(p.y*100)/100,round:0});
    if(this.accept(next)){this.shape='custom';this.selected=index+1;this.remember(before);this.draw();this.publish();}
  }
  remove(){
    if(this.contour.points.length<=3)return;
    const before=this.snapshot(),next=cloneContour(this.contour);next.points.splice(this.selected,1);
    if(this.accept(next)){this.shape='custom';this.selected=Math.min(this.selected,next.points.length-1);this.remember(before);this.draw();this.publish();}
  }
  travel(forward){const from=forward?this.redo:this.undo,to=forward?this.undo:this.redo;if(!from.length)return;to.push(this.snapshot());const saved=from.pop();Object.assign(this,copy(saved));this.inputBefore=null;this.draw();this.publish();}
  syncButtons(){this.undoButton.disabled=!this.undo.length;this.redoButton.disabled=!this.redo.length;this.addButton.disabled=this.contour.points.length>=32;this.removeButton.disabled=this.contour.points.length<=3;}
  message(text=''){this.host.querySelector('#contour-status').textContent=text||`${this.contour.points.length} Randpunkte · ${this.shape==='custom'?'eigene Kontur':'Vorlage'} · Änderungen erscheinen direkt in allen Vorschauen.`;}
  draw(){
    const points=this.contour.points,path=outlinePath(points,this.physical?this.plane:null);
    this.host.querySelector('.contour-fill').setAttribute('d',path);this.host.querySelector('.contour-shadow').setAttribute('d',path);
    if(this.handles.children.length!==points.length){
      this.handles.replaceChildren();this.picker.replaceChildren();
      points.forEach((p,i)=>{
        const handle=document.createElementNS(NS,'g');handle.dataset.point=i;handle.setAttribute('role','button');handle.setAttribute('tabindex','0');handle.setAttribute('aria-label',`Randpunkt ${i+1}`);
        const hit=document.createElementNS(NS,'circle');hit.setAttribute('r','14');hit.setAttribute('class','point-hit');
        const circle=document.createElementNS(NS,'circle');circle.setAttribute('r','5.5');circle.setAttribute('class','point-dot');
        const text=document.createElementNS(NS,'text');text.textContent=i+1;text.setAttribute('y','-12');text.setAttribute('text-anchor','middle');
        handle.append(hit,circle,text);this.handles.append(handle);this.picker.append(new Option(`Punkt ${i+1}`,i));
      });
    }
    points.forEach((p,i)=>{const handle=this.handles.children[i];handle.setAttribute('transform',`translate(${this.plane.x+p.x*this.plane.width/100} ${this.plane.y+p.y*this.plane.height/100})`);handle.classList.toggle('is-selected',i===this.selected);handle.setAttribute('aria-pressed',String(i===this.selected));});
    this.picker.value=this.selected;
    for(const key of ['x','y','round']){const input=this.host.querySelector('#point-'+key);if(document.activeElement!==input)input.value=points[this.selected][key];}
    this.host.querySelector('#point-round-value').textContent=points[this.selected].round+' %';this.syncButtons();this.message();
  }
}
