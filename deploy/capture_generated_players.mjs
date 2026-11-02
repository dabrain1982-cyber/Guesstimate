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



const {spawnSync}=await import('node:child_process');
const descriptorScript = `import ast,json
from pathlib import Path
from types import SimpleNamespace
catalog={}
for node in ast.parse(Path('app.py').read_text(encoding='utf-8-sig')).body:
    if isinstance(node,ast.Assign):
        for target in node.targets:
            if isinstance(target,ast.Name) and target.id in ('AVATAR_CATALOG','DEFAULT_AVATAR'):
                catalog[target.id]=ast.literal_eval(node.value)
app=SimpleNamespace(extensions={})
scope={'current_app':app,'url_for':lambda endpoint,filename:'/static/'+filename}
module=ast.parse(Path('player_portrait.py').read_text(encoding='utf-8-sig'))
functions=ast.Module(body=[n for n in module.body if isinstance(n,ast.FunctionDef)],type_ignores=[])
exec(compile(functions,'player_portrait.py','exec'),scope)
scope['register_portraits'](app,[catalog['DEFAULT_AVATAR'],*catalog['AVATAR_CATALOG']])
result={k:{'label':v['name'],'portrait':scope['public_portrait'](k)} for k,v in app.extensions['player_portraits'].items()}
result['self']={'label':'Eigener Startavatar','portrait':scope['public_portrait']('a00',is_self=True)}
print(json.dumps(result))`;
const descriptorsRun=spawnSync(process.env.PYTHON||'python',['-X','utf8','-c',descriptorScript],{cwd:root,encoding:'utf8'});
if(descriptorsRun.status!==0)throw Error(descriptorsRun.stderr);
const descriptors=JSON.parse(descriptorsRun.stdout);
const captures={};const portrait='static/player-portrait.js';
run(read(portrait).replace('export function','function'));
function add(key,label,player){
 context.player=player;
 const markup=run(`(()=>{const host=document.createElement('div');const view=createPlayerPortrait(host);view.update(player);return host.children[0];})()`).outerHTML;
 const deps=[portrait,'player_portrait.py','app.py','offline-preview/conquest-2-5d-v1/turn-controls.js'];
 if(player.portrait)deps.push('static/'+player.portrait.url.replace(/^\/static\//,''));
 captures[key]={label,markup,evidence:deps.map(p=>({path:p,sha256:hash(p)}))};
}
const base={name:'Musterperson',status:'',kind:'player',layout:'army',stats:{troops:18,countries:6},cardCount:3,color:'#d8ff42'};
for(const [key,value] of Object.entries(descriptors))add('avatar-'+key,'Avatar · '+value.label,{...base,portrait:value.portrait});
const cases=[
 ['self-active','Eigener Platz · am Zug',{current:true,status:'du · am Zug',portrait:descriptors.self.portrait,onCards:()=>{}}],
 ['other-waiting','Mitspieler · wartet',{portrait:descriptors.a00.portrait}],
 ['test','Testarmee',{kind:'test',name:'Musterarmee',status:'Testarmee',color:'#82c3ff'}],
 ['neutral','Neutrale Armee',{kind:'neutral',name:'Neutral',cardCount:null,color:'#aaaaaa'}],
 ['out','Ausgeschieden',{status:'ausgeschieden',stats:{troops:0,countries:0},cardCount:0,portrait:descriptors.a00.portrait}],
];
for(const [key,label,patch] of cases)add(key,label,{...base,...patch});
add('winner-player','Sieger des Feldzugs',{name:'Musterperson',status:'Sieger des Feldzugs',current:true,portrait:descriptors.a00.portrait});
add('winner-test','Sieger · Testarmee',{name:'Musterarmee',kind:'test',status:'Sieger des Feldzugs',current:true,color:'#82c3ff'});
fs.writeFileSync(path.join(root,'offline-preview/game-workshop-v1/generated-players.json'),JSON.stringify({schema:1,description:'Original createPlayerPortrait and public_portrait; neutral local examples without game actions or DB.',captures},null,2)+'\n');
console.log('Captured '+Object.keys(captures).length+' canonical player examples.');
