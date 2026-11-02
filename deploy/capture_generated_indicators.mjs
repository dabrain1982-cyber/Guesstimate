// Capture DOM produced by the actual local factories, without a browser, game,
// database, handlers, timers or network. The result is inert source evidence.
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8').replace(/^\uFEFF/,'');
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const escape=s=>String(s).replaceAll('&','&amp;').replaceAll('"','&quot;').replaceAll('<','&lt;').replaceAll('>','&gt;');
class Element{
 constructor(tag){this.tag=tag;this.attributes={};this.children=[];this.content='';this.raw='';const values={};
  this.style=new Proxy({setProperty:(k,v)=>{values[k]=String(v);this.attributes.style=Object.entries(values).map(([a,b])=>a+': '+b+';').join(' ');}}, {set:(t,k,v)=>{t.setProperty(k,v);return true;}});
  this.dataset=new Proxy({}, {set:(t,k,v)=>{this.setAttribute('data-'+String(k).replace(/[A-Z]/g,c=>'-'+c.toLowerCase()),v);return true;}});
  this.classList={add:(...names)=>{this.className=[...new Set([...(this.className||'').split(' ').filter(Boolean),...names])].join(' ');},toggle:(name,enabled)=>{const names=new Set(this.className.split(' ').filter(Boolean));if(enabled)names.add(name);else names.delete(name);this.className=[...names].join(' ');}};
 }
 setAttribute(k,v){this.attributes[k]=String(v);} getAttribute(k){return this.attributes[k]??null;} removeAttribute(k){delete this.attributes[k];}
 addEventListener(){} append(...nodes){for(const node of nodes){node.parent=this;this.children.push(node);}}
 replaceChildren(...nodes){this.children=[];this.content='';this.raw='';this.append(...nodes);}
 set className(v){this.setAttribute('class',v);} get className(){return this.attributes.class||'';}
 set textContent(v){this.content=String(v);this.children=[];this.raw='';} get textContent(){return this.content+this.children.map(c=>c.textContent).join('');}
 set innerHTML(v){this.raw=String(v);this.children=[];this.content='';}
 get outerHTML(){return '<'+this.tag+Object.entries(this.attributes).map(([k,v])=>' '+k+'="'+escape(v)+'"').join('')+'>'+escape(this.content)+this.raw+this.children.map(c=>c.outerHTML).join('')+(['img','input'].includes(this.tag)?'':'</'+this.tag+'>');}
}
for(const key of ['type','title','src','alt','id','colSpan','value'])Object.defineProperty(Element.prototype,key,{set(v){this.setAttribute(key,v);},get(){return this.getAttribute(key);}});
for(const key of ['hidden','disabled'])Object.defineProperty(Element.prototype,key,{set(v){if(v)this.setAttribute(key,'');else delete this.attributes[key];},get(){return key in this.attributes;}});
const mounts=new Map();const document={createElement:tag=>new Element(tag),createElementNS:(_,tag)=>new Element(tag),querySelector:selector=>mounts.get(selector)||null};
const context=vm.createContext({document,URL,console:{log(){}},performAction(){}});
const run=code=>vm.runInContext(code,context,{timeout:1000});
const slice=(file,start,end)=>{const text=read(file),a=text.indexOf(start),b=text.indexOf(end,a+start.length);if(a<0||b<0)throw Error('Capture boundary changed: '+file+' '+start);return {code:text.slice(a,b),line:text.slice(0,a).split('\n').length};};


const captures={};
const add=(key,markup,deps,values)=>captures[key]={markup,evidence:deps.map(p=>({path:p,sha256:hash(p)})),...(values?{values}:{})};
const dice='static/dice-table.js';
context.history=new Element('div');run(slice(dice,'const renderHistory =','const renderKniffel =').code);
run("renderHistory([{name:'Musterplatz 1',rolls:[{values:[3,4,5]}]},{name:'Musterplatz 2',rolls:[{}]}])");
add('dice-history',context.history.children.map(c=>c.outerHTML).join(''),[dice]);
context.kniffelSheet=new Element('div');context.kniffelSignature=null;context.memberId=1;
run(slice(dice,'const renderKniffel =','const maexchenLabel =').code);
const keys=['ones','twos','threes','fours','fives','sixes','three_kind','four_kind','full_house','small_straight','large_straight','five_kind','chance'];
for(const count of [1,2,3]){
 context.kniffelSignature=null;context.kniffelLights=new Element('div');context.kniffelLights.className='kniffel-roll-lights';context.kniffelLights.append(...[1,2,3].map(()=>new Element('i')));
 context.score={current_member_id:1,rolls_left:count,categories:keys.map(key=>({key,label:key})),available_scores:{twos:4},scorecards:[1,2].map(id=>({id,name:'Musterplatz '+id,scores:{ones:3},totals:{upper:3,bonus:0,upper_total:3,lower:0,total:3}}))};
 run('renderKniffel(score)');add('kniffel-lights-'+count,context.kniffelLights.children.map(c=>c.outerHTML).join(''),[dice]);
}
add('kniffel-table',context.kniffelSheet.children.map(c=>c.outerHTML).join(''),[dice]);
const life=slice(dice,'life.textContent = player.eliminated',';');
for(const [key,lives,swimming,eliminated] of [['three',3,false,false],['two',2,false,false],['swimming',1,true,false],['out',0,false,true]]){
 context.player={lives,swimming,eliminated};
 add('maexchen-life-'+key,run(`(()=>{const life=document.createElement('div');${life.code};return life;})()`).textContent,[dice],{text:run(`(()=>{const life=document.createElement('div');${life.code};return life;})()`).textContent});
}
const portrait='static/player-portrait.js';run(read(portrait).replace('export function','function'));
for(const [key,current,status] of [['active',true,'am Zug'],['waiting',false,''],['out',false,'ausgeschieden']]){
 context.player={name:'Musterarmee',status,current,layout:'army',stats:{troops:key==='out'?0:18,countries:key==='out'?0:6},cardCount:key==='out'?0:3,color:'#d8ff42'};
 const html=run(`(()=>{const host=document.createElement('div');const view=createPlayerPortrait(host);view.update(player);return host.children[0];})()`).outerHTML;
 add('conquest-portrait-'+key,html,[portrait,'offline-preview/conquest-2-5d-v1/turn-controls.js']);
}
const timer='static/timer.js';context.hold=5;context.limit=60;
run(slice(timer,'const factorAt =','const update =').code);
for(const elapsed of [0,60]){
 const factor=run(`factorAt(${elapsed})`);const points=100-Math.round(50*(1-factor));
 add('quiz-time-'+elapsed,'',[timer],{points,percent:points,hue:Math.round(8+factor*66)});
}

context.fallback=new Element('div');run(slice(dice,'const showFallback =','const animateRoll =').code);
for(const values of [[1,2,3,4,5],[4,2]]){context.rolls=values.map(value=>({value}));run('showFallback(rolls)');add('dice-result-'+values.length,context.fallback.children.map(c=>c.outerHTML).join(''),[dice]);}
const attack='offline-preview/conquest-2-5d-v1/attack.js';context.node=selector=>mounts.get(selector);
run(slice(attack,'function showRolls(','function record(').code);
for(const [key,values] of [['attack',[6,3,2]],['defense',[5,4]]]){mounts.set('#example-roll',new Element('div'));context.rolls=values;run("showRolls('#example-roll',rolls)");add('conquest-roll-'+key,mounts.get('#example-roll').children.map(c=>c.outerHTML).join(''),[attack]);}
const output=path.join(root,'offline-preview/game-workshop-v1/generated-indicators.json');
fs.writeFileSync(output,JSON.stringify({schema:1,description:'Neutral frozen examples from canonical DOM factories and timer function; no game handlers, timers or network.',captures},null,2)+'\n');
console.log('Captured '+Object.keys(captures).length+' canonical indicator examples.');
