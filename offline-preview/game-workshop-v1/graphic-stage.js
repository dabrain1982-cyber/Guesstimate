// The source owns each image, symbol and flyer interior. This adapter only fits whole previews.
const cfg=JSON.parse(document.querySelector('#graphic-config').textContent),host=document.querySelector('#graphic-stage'),status=document.querySelector('#graphic-status');
async function init(){
  if(cfg.renderer==='image'){
    const image=new Image();image.className='graphic-image';image.alt='Unverändertes Originalmotiv';image.src=cfg.url;await image.decode();host.append(image);return;
  }
  let content,width,height;
  if(cfg.renderer==='markup'){
    content=document.createElement('div');content.className='graphic-source-frame';content.innerHTML=cfg.markup;content.inert=true;width=cfg.width;height=cfg.height;
  }else{
    content=document.createElement('div');content.className='graphic-symbols'+(cfg.members.length===1?' single':'');
    let factory,stats;
    if(cfg.factory==='comic')factory=(await import('/graphic-source/comic.js')).icon;
    if(cfg.factory==='equipment')factory=(await import('/graphic-source/equipment.js')).symbolImage;
    if(cfg.factory==='stats'){
      const source=document.createElement('div');(await import('/graphic-source/player-portrait.js')).createPlayerPortrait(source);stats=[...source.querySelectorAll('.player-portrait-stat-icon')];
    }
    for(const member of cfg.members){
      const figure=document.createElement('figure');figure.className='graphic-symbol';const face=document.createElement('div');face.className='graphic-symbol-face';
      if(cfg.factory==='markup')face.innerHTML=member.markup;
      else if(stats)face.append(stats[member.id==='troops'?0:1]);else face.append(factory(member.id));
      const caption=document.createElement('figcaption');caption.className='graphic-symbol-label';caption.textContent=member.name;figure.append(face,caption);content.append(figure);
    }
    width=cfg.members.length===1?212:544;height=cfg.members.length===1?128:Math.ceil(cfg.members.length/5)*112+32;
  }
  content.style.width=width+'px';content.style.height=height+'px';content.style.boxSizing='border-box';host.append(content);
  const fit=()=>{const scale=Math.min((host.clientWidth-28)/width,(host.clientHeight-28)/height);content.style.transform='scale('+scale+')';content.style.left=(host.clientWidth-width*scale)/2+'px';content.style.top=(host.clientHeight-height*scale)/2+'px';};
  new ResizeObserver(fit).observe(host);fit();
  await Promise.all([...content.querySelectorAll('img')].map(image=>image.decode()));
  await document.fonts.ready;
}
init().then(()=>{document.body.dataset.state='ready';status.textContent='';}).catch(error=>{document.body.dataset.state='error';status.textContent='Bildbaustein konnte nicht geladen werden: '+error.message;});
