// Earlier synth drafts remain identifiable for reading old recipes.
function createSynthSound(onState) {
  let context,active=[];
  return {
    stop(){for(const node of active){try{node.stop();}catch{}}active=[];},
    async play(recipe, edge='down') {
      const s=recipe.settings;
      if(s.sound==='off'||s.volume===0)return;
      try {
        const Constructor=window.AudioContext||window.webkitAudioContext;
        if(!Constructor)throw new Error('Audio wird in diesem Browser nicht unterstützt.');
        context ||= new Constructor();
        if(context.state!=='running')await context.resume();
        if(context.state!=='running')throw new Error('Der Browser hat den Klang noch nicht freigegeben.');
        const material=s.sound==='material'?s.material:s.sound;
        const now=context.currentTime;
        const gain=context.createGain();
        const peak=s.volume/100*(edge==='down'?.18:.09);
        const duration=material==='metal'?.16:material==='wood'?.075:.045;
        gain.gain.setValueAtTime(.0001,now);
        gain.gain.exponentialRampToValueAtTime(Math.max(.0002,peak),now+.003);
        gain.gain.exponentialRampToValueAtTime(.0001,now+duration);
        gain.connect(context.destination);
        const base={wood:180,stone:730,metal:1050}[material]*(edge==='up'?1.42:1);
        for(const ratio of material==='metal'?[1,1.61]:[1]) {
          const oscillator=context.createOscillator();
          oscillator.type=material==='metal'?'sine':'triangle';
          oscillator.frequency.setValueAtTime(base*ratio,now);
          oscillator.frequency.exponentialRampToValueAtTime(base*ratio*.63,now+duration);
          oscillator.connect(gain);oscillator.start(now);oscillator.stop(now+duration+.01);active.push(oscillator);
        }
        const buffer=context.createBuffer(1,Math.ceil(context.sampleRate*duration),context.sampleRate);
        const samples=buffer.getChannelData(0);
        for(let i=0;i<samples.length;i++)samples[i]=(Math.random()*2-1)*.16;
        const noise=context.createBufferSource();noise.buffer=buffer;
        const filter=context.createBiquadFilter();filter.type='lowpass';filter.frequency.value=material==='wood'?650:material==='stone'?2600:4000;
        noise.connect(filter);filter.connect(gain);noise.start(now);noise.stop(now+duration);active.push(noise);
        onState(`Alter synthetischer Platzhalter · ${material==='wood'?'Holz':material==='stone'?'Stein':'Metall'} · ${s.volume} %`);
      } catch(error) {onState(error.message);}
    },
  };
}

// Local source recordings: one short shot on press; release never doubles it.
export function createSound(onState,onPlay=()=>{},assetBase='/assets/audio/'){
  const records=new Map(),buffers=new Map(),synth=createSynthSound(onState);
  let context,source,sequence=0;
  function stop(){sequence++;try{source?.stop();}catch{}source=null;synth.stop();}
  return {
    configure(rows){for(const row of rows)records.set(row.id,row);},stop,
    async play(recipe,edge='down'){
      const s=recipe.settings;if(s.sound==='off'||s.volume===0)return;
      if(edge!=='up')onPlay();
      const id=s.sound==='material'?{wood:'wood-plank','wood-aged':'wood-plank',stone:'stone-scrape',metal:'robot-step'}[s.material]:s.sound;
      if(s.sound==='material'&&!id){if(edge!=='up')onState('Dieser Fläche ist kein Materialklang zugeordnet. Wähle bei Bedarf einen Klang aus.');return;}
      if(['wood','stone','metal'].includes(id)){stop();return synth.play(recipe,edge);}
      if(edge==='up')return;
      const record=records.get(id);if(!record){onState('Dieser Klang ist nicht verfügbar.');return;}
      stop();const ticket=sequence;
      try{
        const Constructor=window.AudioContext||window.webkitAudioContext;
        if(!Constructor)throw new Error('Audio wird in diesem Browser nicht unterstützt.');
        context ||= new Constructor();await context.resume();
        if(context.state!=='running')throw new Error('Der Browser hat den Klang noch nicht freigegeben.');
        if(!buffers.has(id))buffers.set(id,fetch(assetBase+record.file).then(async response=>{
          if(!response.ok)throw new Error('Die lokale Klangdatei konnte nicht geladen werden.');
          return context.decodeAudioData(await response.arrayBuffer());
        }).catch(error=>{buffers.delete(id);throw error;}));
        const buffer=await buffers.get(id);if(ticket!==sequence)return;
        const offset=Math.min(record.button_offset,Math.max(0,buffer.duration-.02));
        const duration=Math.min(record.button_duration,buffer.duration-offset),now=context.currentTime;
        const gain=context.createGain(),peak=s.volume/100*.65;
        gain.gain.setValueAtTime(0,now);gain.gain.linearRampToValueAtTime(peak,now+.006);
        gain.gain.setValueAtTime(peak,now+Math.max(.007,duration-.025));gain.gain.linearRampToValueAtTime(0,now+duration);
        gain.connect(context.destination);source=context.createBufferSource();source.buffer=buffer;
        source.connect(gain);source.start(now,offset,duration);source.onended=()=>gain.disconnect();
        onState(`${record.name} · kurzer Buttonausschnitt · ${s.volume} %`);
      }catch(error){onState(error.message);}
    },
  };
}
