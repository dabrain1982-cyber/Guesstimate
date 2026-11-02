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
  this.classList={add:(...names)=>{this.className=[...new Set([...(this.className||'').split(' ').filter(Boolean),...names])].join(' ');},toggle:()=>{}};
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

// Only pure factory slices execute in the VM. Network, timers and app/DB code
// are unavailable. Event registration is a no-op in the tiny DOM above.
const captures={};
const add=(key,markup,deps)=>captures[key]={markup,evidence:[...new Set(deps)].map(p=>({path:p,sha256:hash(p)}))};
const dice='static/dice-table.js';
const mini=slice(dice,'const makeMiniDie =','const renderZones =');run(mini.code);
for(const zone of ['held','tray'])add('dice-'+zone,run(`makeMiniDie({id:'example',value:4},'${zone}')`).outerHTML,[dice]);
const score=slice(dice,'const renderKniffel =','const maexchenLabel =');
context.kniffelSheet=new Element('div');context.kniffelLights=null;context.kniffelSignature=null;context.memberId=1;
run(score.code);
const keys=['ones','twos','threes','fours','fives','sixes','three_kind','four_kind','full_house','small_straight','large_straight','five_kind','chance'];
context.exampleScore={current_member_id:1,rolls_left:2,categories:keys.map(key=>({key,label:key})),available_scores:{ones:3},scorecards:[1,2].map(id=>({id,name:'Musterplatz '+id,scores:{},totals:{upper:0,bonus:0,upper_total:0,lower:0,total:0}}))};
run('renderKniffel(exampleScore)');add('kniffel',context.kniffelSheet.children.map(c=>c.outerHTML).join(''),[dice]);
const territory='offline-preview/conquest-2-5d-v1/territory-model.js',cards='offline-preview/conquest-2-5d-v1/cards.js',turn='offline-preview/conquest-2-5d-v1/turn-controls.js';
run(read(territory).replaceAll('export ',''));
run(read(cards).replace(/^import .*?;\r?\n/m,'').replaceAll('export ','').replace("new URL('./assets/karte.png', import.meta.url).href", "'/conquest-source/assets/karte.png'"));
context.cardExamples=[{id:'alaska',name:'Alaska',symbol:'infantry',type:'Infanterie'},{id:'ontario',name:'Ontario',symbol:'cavalry',type:'Reiter'},{id:'brasilien',name:'Brasilien',symbol:'artillery',type:'Geschütz'}];
run("function countryCard(card){return createCountryCard(card,{owned:card.id==='alaska',ownerName:'Musterarmee',ownerColor:'#d8ff42'});}");
add('awarded-card',run('countryCard(cardExamples[0])').outerHTML,[territory,cards]);
for(const expanded of [false,true]){
 const mount=new Element('div');mounts.set('#hand-cards',mount);
 for(const id of ['cards-toggle','trade-panel','trade-cards'])mounts.set('#'+id,new Element(id==='trade-panel'?'section':'button'));
 context.cardHand=new Element('section');context.cardsExpanded=expanded;context.selectedCards=new Set(expanded?context.cardExamples.map(c=>c.id):[]);context.trading=false;
 context.turn={hand:()=>context.cardExamples};context.remote={tradeInfo:{can_trade:true,next_value:4}};context.tradeButton=mounts.get('#trade-cards');
 context.anchorCards=()=>{};context.setActionLabel=(button,label)=>{button.textContent=label;};
 const render=slice(turn,'function renderHand(','function showHand(');run(render.code);run('renderHand()');
 add('hand-'+(expanded?'expanded':'collapsed'),mount.children.map(c=>c.outerHTML).join(''),[territory,cards,turn]);
}
const table='static/card-table.js';context.room={dataset:{memberId:1}};
run(slice(table,'const cardElement =','const renderCards =').code);
add('playtable-card',run("cardElement({id:'example',zone:'player:1',rank:'A',symbol:'♠',color:'black',face_up:true,x:45,y:40,z:1,rotation:-4})").outerHTML,[table]);
const output=path.join(root,'offline-preview/game-workshop-v1/generated-windows.json');
fs.writeFileSync(output,JSON.stringify({schema:1,description:'Neutral inert examples captured from the current original DOM factories.',captures},null,2)+'\n');
console.log('Captured '+Object.keys(captures).length+' original window contents.');
