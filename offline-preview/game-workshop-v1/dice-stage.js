// Local preview adapter. The two actual renderers are read from unchanged game files.
const room=document.body,canvas=document.querySelector('canvas'),flat=document.querySelector('#flat-rolls');
const status=document.querySelector('#status'),button=document.querySelector('#roll'),output=document.querySelector('#values');
const interactive=room.dataset.interactive==='true';
async function init(){
  if(room.dataset.renderer==='display'){
    canvas.hidden=true;
    const {showRolls}=await import('/dice-source/flat.js');showRolls('#flat-rolls',[2,5]);
    status.textContent='Flache Anzeige aus Conquest · Beispielwerte';room.dataset.state='ready';return;
  }
  flat.hidden=true;
  const {tableDice}=await import('/dice-source/physics.js');
  let renderer=null;
  const adapter=tableDice({room,canvas,engineStatus:status,fallback:document.querySelector('#fallback'),
    fitRoom:()=>{if(renderer)renderer.resize(canvas.clientWidth,canvas.clientHeight);},
    showFallback:()=>{room.dataset.state='error';status.textContent='Die vorhandene 3D-Würfeltechnik konnte nicht geladen werden.';}});
  async function roll(initial=false){
    room.dataset.state='rolling';button.disabled=true;
    const values=initial?[2,5]:Array.from({length:2},()=>1+Math.floor(Math.random()*6));
    renderer=await adapter.roll(values.map((value,i)=>({id:'preview-'+i,value})));
    if(room.dataset.state==='error')return;
    if(!renderer)throw Error('3D-Würfeltechnik nicht verfügbar');
    renderer.resize(canvas.clientWidth,canvas.clientHeight);
    output.value=values.join(' · ');status.textContent='Würfeltisch · lokale Physikprobe';room.dataset.state='ready';button.disabled=false;
  }
  button.hidden=!interactive;button.addEventListener('click',()=>roll().catch(failed));
  window.addEventListener('resize',()=>{if(renderer)renderer.resize(canvas.clientWidth,canvas.clientHeight);});
  window.addEventListener('pagehide',()=>renderer?.stop());
  await roll(true);
}
function failed(error){room.dataset.state='error';status.textContent=error.message;button.disabled=true;}
init().catch(failed);
