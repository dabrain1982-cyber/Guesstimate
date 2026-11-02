const cfg=JSON.parse(document.querySelector('#media-config').textContent),settings=cfg.settings,host=document.querySelector('#media-stage'),status=document.querySelector('#media-status');
const node=(tag,text,className)=>{const item=document.createElement(tag);if(text)item.textContent=text;if(className)item.className=className;return item;};
async function init(){
  if(settings.type==='font'){
    const families={chalk:'Media Chalk',stone:'Media Stone',iron:'Media Iron',stamp:'Media Stamp',hand:'Media Hand',comic:'Media Comic',clear:'Media Clear'};
    await document.fonts.load(settings.weight+' 32px "'+families[settings.style]+'"','ÄÖÜ äöü ß');
    if(!document.fonts.check(settings.weight+' 32px "'+families[settings.style]+'"'))throw new Error('Die lokale Schrift fehlt.');
    const sample=node('section',null,'lettering finish-'+settings.style);sample.setAttribute('aria-label',cfg.name);
    sample.append(node('h1','Dein nächster Zug'),node('p','Wer ist als Nächstes dran?'),node('p','ÄÖÜ äöü ß · 0123456789','glyphs'),node('small',settings.font+' · '+settings.finish));host.append(sample);return;
  }
  const card=node('section',null,'sound-card'),wave=node('div',null,'waveform');wave.setAttribute('aria-hidden','true');
  for(const height of settings.waveform){const bar=node('span');bar.style.height=Math.max(4,height*100)+'%';wave.append(bar);}
  const audio=node('audio');audio.id='sound-audio';audio.preload='metadata';audio.src=settings.url;audio.volume=settings.default_volume;
  const text=node('p','Bereit zum Probehören','');text.id='sound-state';const controls=node('div',null,'sound-actions'),play=node('button','▶ Probehören'),stop=node('button','Stopp');play.id='sound-play';stop.id='sound-stop';play.disabled=stop.disabled=!cfg.interactive;
  const volume=node('label','Lautstärke','sound-volume'),slider=node('input');slider.type='range';slider.min=0;slider.max=100;slider.value=Math.round(settings.default_volume*100);slider.disabled=!cfg.interactive;slider.setAttribute('aria-label','Lautstärke der Klangprobe');volume.append(slider);
  const setState=value=>{text.textContent=value;card.dataset.playback=value==='Beispiel beendet'?'ended':value==='Wird abgespielt …'?'playing':'stopped';};
  play.addEventListener('click',async()=>{audio.pause();audio.currentTime=0;try{await audio.play();setState('Wird abgespielt …');}catch(error){setState('Abspielen fehlgeschlagen: '+error.message);}});
  stop.addEventListener('click',()=>{audio.pause();audio.currentTime=0;setState('Gestoppt');});slider.addEventListener('input',()=>{audio.volume=Number(slider.value)/100;});audio.addEventListener('ended',()=>setState('Beispiel beendet'));
  controls.append(play,stop);card.append(node('h1',cfg.name),node('p',settings.usage),wave,node('p',settings.duration.toLocaleString('de-DE',{maximumFractionDigits:2})+' Sekunden · Kenney · CC0'),controls,volume,text,audio);host.append(card);window.addEventListener('pagehide',()=>audio.pause());
  await new Promise((resolve,reject)=>{if(audio.readyState>=1)return resolve();audio.addEventListener('loadedmetadata',resolve,{once:true});audio.addEventListener('error',()=>reject(new Error('Die lokale Klangdatei fehlt.')),{once:true});});
}
init().then(()=>{document.body.dataset.state='ready';status.textContent='';}).catch(error=>{document.body.dataset.state='error';status.textContent='Vorschau konnte nicht geladen werden: '+error.message;});
