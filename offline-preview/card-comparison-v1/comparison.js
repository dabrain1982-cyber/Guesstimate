const defaults={card:'Hearts7',layout:'hand',angle:0,zoom:100,back:false,reset:0};
let state={...defaults};
const frames=[...document.querySelectorAll('iframe')];
const ready=new Set();
function send(){
  for(const frame of frames)frame.contentWindow.postMessage({type:'card-settings',state},location.origin);
  document.querySelector('#angle-value').value=`${state.angle}°`;
  document.querySelector('#zoom-value').value=`${state.zoom} %`;
  document.querySelector('#flip').textContent=state.back?'Vorderseiten zeigen':'Karten umdrehen';
}
for(const key of ['card','layout','angle','zoom'])document.getElementById(key).addEventListener('input',event=>{state[key]=['angle','zoom'].includes(key)?Number(event.target.value):event.target.value;send();});
document.querySelector('#flip').addEventListener('click',()=>{state.back=!state.back;send();});
document.querySelector('#reset').addEventListener('click',()=>{state={...defaults,reset:state.reset+1};for(const key of ['card','layout','angle','zoom'])document.getElementById(key).value=String(state[key]);send();});
window.addEventListener('message',event=>{
  if(event.origin!==location.origin||!frames.some(f=>f.contentWindow===event.source))return;
  if(event.data?.type==='card-ready'){
    ready.add(event.source);event.source.postMessage({type:'card-settings',state},location.origin);
    document.querySelector('#comparison-status').textContent=ready.size===3?'Alle drei Varianten sind bereit. Änderungen bleiben nur in diesem Vergleich.':`${ready.size} von 3 Varianten bereit …`;
  }
  if(event.data?.type==='card-error')document.querySelector('#comparison-status').textContent=`Eine Vorschau konnte nicht geladen werden: ${event.data.message}`;
});
