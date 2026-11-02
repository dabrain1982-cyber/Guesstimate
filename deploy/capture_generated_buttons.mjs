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
for(const key of ['type','title','src','alt','id'])Object.defineProperty(Element.prototype,key,{set(v){this.setAttribute(key,v);},get(){return this.getAttribute(key);}});
for(const key of ['hidden','disabled'])Object.defineProperty(Element.prototype,key,{set(v){if(v)this.setAttribute(key,'');else delete this.attributes[key];},get(){return key in this.attributes;}});
const document={createElement:tag=>new Element(tag),createElementNS:(_,tag)=>new Element(tag)};
const context=vm.createContext({document,URL,console:{log(){}},performAction(){}});
const run=code=>vm.runInContext(code,context,{timeout:1000});
const slice=(file,start,end)=>{const text=read(file),a=text.indexOf(start),b=text.indexOf(end,a+start.length);if(a<0||b<0)throw Error('Capture boundary changed: '+file+' '+start);return {code:text.slice(a,b),line:text.slice(0,a).split('\n').length};};
const buttons=[];
const add=(key,file,line,element,details,deps=[file])=>buttons.push({key,path:file,line,markup:element.outerHTML,evidence:[...new Set(deps)].map(p=>({path:p,sha256:hash(p)})),...details});
const dice='static/dice-table.js',mini=slice(dice,'const makeMiniDie =','const renderZones =');run(mini.code);
for(const zone of ['held','tray'])add('dice-'+zone,dice,mini.line,run(`makeMiniDie({id:'example',value:4},'${zone}')`),{factory_line:mini.line+mini.code.slice(0,mini.code.indexOf('document.createElement("button")')).split('\n').length-1,game:'Würfelspiele',games:['Würfeltisch','Kniffel'],template:'dice_table_game.html',usage:zone==='held'?'Würfel behalten / wieder einsammeln':'Würfelauswahl zurücknehmen',shell:'dice-game-shell',context_token:zone==='held'?'data-dice-held':'data-dice-tray',ancestors:[]});
const score=slice(dice,'const scoreButton = document.createElement("button");','cell.append(scoreButton);');
add('kniffel-score',dice,score.line,run(`(()=>{const kniffel={available_scores:{ones:4}},category={key:'ones',label:'Einser'};${score.code};return scoreButton;})()`),{game:'Kniffel',games:['Kniffel'],template:'dice_table_game.html',usage:'Ergebnis in Kniffelblock eintragen',shell:'dice-game-shell',context_token:'data-kniffel-sheet',ancestors:[['table','',''],['tbody','',''],['tr','',''],['td','is-current','']],cell_width:Number(read('static/dice-table.css').match(/\.kniffel-player-column\s*\{\s*width:\s*(\d+)px/)[1])});
const portrait='static/player-portrait.js';run(read(portrait).replace('export function','function'));
add('conquest-card-badge',portrait,read(portrait).slice(0,read(portrait).indexOf("const badge = make('button'")).split('\n').length,run(`(()=>{const host=document.createElement('div'),view=createPlayerPortrait(host);view.update({name:'Beispielarmee',cardCount:3,onCards(){},color:'#d8ff42'});return host.children[0].children.find(c=>c.className==='player-portrait-badge');})()`),{game:'Conquest',games:['Conquest'],template:'conquest_table.html',usage:'Eigene Karten am Avatar öffnen',ancestors:[['div','player-portrait','']]});
const iconFile='offline-preview/comic-ui-v1/components.js';
const icon=slice(iconFile,'const paths =','export function button(');run(icon.code.replace('export function icon','function icon'));
const icons={dice:run("icon('dice')").outerHTML,evidence:[{path:iconFile,sha256:hash(iconFile)}]};
const output=path.join(root,'offline-preview/game-workshop-v1/generated-buttons.json');
fs.writeFileSync(output,JSON.stringify({schema:1,description:'Inert captures from original DOM factories with neutral examples. Regenerate when evidence changes.',buttons,icons},null,2)+'\n');
console.log('Captured '+buttons.length+' generated button uses and canonical dice icon.');
