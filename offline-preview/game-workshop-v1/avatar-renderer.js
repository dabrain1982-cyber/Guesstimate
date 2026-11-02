import {createPlayerPortrait} from '/shared/player-portrait.js';
const config=JSON.parse(document.getElementById('avatar-config').textContent),stage=document.getElementById('avatar-stage');
const make=(tag,cls,text)=>{const n=document.createElement(tag);n.className=cls;if(text)n.textContent=text;return n;};
const radii={original:'42% 49% 40% 46%',round:'50%',rounded:'20%',square:'0'};
function portrait(host,own,army=false){
  const s=config.settings,view=createPlayerPortrait(host);
  view.update({name:own?'Dein Avatar':'Vergleich',status:army?'Conquest · Beispiel':'Spieleranzeige',color:own?s.background:'#d8ff42',layout:army?'army':'default',
    ...(army?{stats:{troops:8,countries:3},cardCount:2}:{}),
    portrait:own?{url:config.image,alt:'Eigener Bildausschnitt',crop:{scale:1,top:0}}:{url:'/shared/avatars/stage/a02-wasserschwein.webp',alt:'Wasserschwein',crop:config.reference_crop}});
  host.firstElementChild.style.setProperty('--player-portrait-size',(army?14:22)*(own?s.size/100:1)+'px');
  if(own){view.anchor.style.borderRadius=radii[s.shape];view.anchor.style.borderColor=s.frame;view.anchor.style.borderWidth=s.frame_width*.06+'em';}
}
const grid=make('div','avatar-comparison');stage.append(grid);
if(config.interactive){const reference=make('section','avatar-example');reference.append(make('h2','','Fester Größenvergleich'));const host=make('div','avatar-player');reference.append(host);portrait(host,false);grid.append(reference);}
const own=make('section','avatar-example own');own.append(make('h2','','Deine Gestaltung'));const host=make('div','avatar-player');own.append(host);portrait(host,true);grid.append(own);
if(config.interactive){const context=make('section','avatar-context');context.append(make('h2','','So sitzt dein Bild in der Conquest-Anzeige'));const host=make('div','avatar-army');context.append(host);portrait(host,true,true);stage.append(context);}
else stage.classList.add('avatar-single');
document.body.dataset.ready='true';
