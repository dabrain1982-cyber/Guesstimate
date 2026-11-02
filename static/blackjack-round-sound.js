import {clips} from './blackjack-round-clips.js';
export function createRoundSound(root){
  const localClips={
    'card-deal':{url:new URL('./audio/blackjack/card-deal-slide.ogg',import.meta.url)},
    'chips-place':{url:new URL('./audio/blackjack/chips-place.ogg',import.meta.url)},
    'chips-payout':{url:new URL('./audio/blackjack/chips-payout.ogg',import.meta.url)},
  };
  let context,mix,enabled=true,armed=false;const buffers=new Map(),sources=new Set();
  root.addEventListener('pointerdown',()=>{armed=true;},{once:true});
  root.addEventListener('keydown',()=>{armed=true;},{once:true});
  return {setEnabled(value){enabled=value;if(!enabled)for(const source of sources){try{source.stop();}catch{}}},
    async play(id){
      if(!armed||!enabled||!(clips[id]||localClips[id]))return;
      try{
        const Constructor=window.AudioContext||window.webkitAudioContext;
        if(!Constructor)return;
        context||=new Constructor();await context.resume();if(context.state!=='running')return;
        if(!mix){mix=context.createDynamicsCompressor();mix.threshold.value=-18;mix.knee.value=6;mix.ratio.value=4;mix.attack.value=.003;mix.release.value=.12;mix.connect(context.destination);}
        const clip=clips[id]||localClips[id];
        if(!buffers.has(id))buffers.set(id,(async()=>{
          const data=clip.url?await (await fetch(clip.url)).arrayBuffer():Uint8Array.from(atob(clip.data),c=>c.charCodeAt(0)).buffer;
          const buffer=await context.decodeAudioData(data);
          if(clip.url){
            let squared=0,peak=0,count=0;
            for(let channel=0;channel<buffer.numberOfChannels;channel++)for(const value of buffer.getChannelData(channel)){squared+=value*value;peak=Math.max(peak,Math.abs(value));count++;}
            clip.gain=Math.min(.1/Math.max(.0001,Math.sqrt(squared/count)),.7/Math.max(.0001,peak));
          }
          return buffer;
        })());
        const buffer=await buffers.get(id);if(!enabled)return;
        const now=context.currentTime,duration=buffer.duration,source=context.createBufferSource(),gain=context.createGain(),peak=.4*.65*clip.gain;
        gain.gain.setValueAtTime(0,now);gain.gain.linearRampToValueAtTime(peak,now+.006);gain.gain.setValueAtTime(peak,now+Math.max(.007,duration-.025));gain.gain.linearRampToValueAtTime(0,now+duration);gain.connect(mix);source.buffer=buffer;source.connect(gain);source.start(now,0,duration);sources.add(source);source.onended=()=>{sources.delete(source);gain.disconnect();};
        root.dataset.lastSound=id;root.dataset.soundMix='balanced-v1';
      }catch{root.dataset.soundState='error';}
    }};
}
