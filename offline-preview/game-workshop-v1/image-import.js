// Import and selection for finished artwork. The stored picture is used unchanged.
export class ImageImport {
  constructor(host,{getData,onChange,onImported}) {
    this.getData=getData;this.onChange=onChange;this.onImported=onImported;this.selected=new Map();
    host.innerHTML='<div class="image-import-bar"><input id="art-file" type="file" accept="image/png,image/jpeg,image/webp" hidden><button id="art-import" class="primary" type="button">Bild vom PC hinzufügen</button><label>Aus der Bibliothek auswählen<select id="art-source"><option value="">Bild auswählen …</option></select></label><small>PNG, JPEG oder WebP · bis 20 MB</small></div><p id="art-status" class="image-status" role="status">Fertige Bilder hinzufügen, ansehen und deinen Projekten zuordnen.</p><div id="art-empty" class="image-empty"><span aria-hidden="true">▧</span><h3>Deine Bilder für dieses Element</h3><p>Verwende ein fertiges Bild von deinem PC oder ein Motiv aus der Bibliothek. Die Bilddatei wird unverändert aufbewahrt.</p></div><figure id="art-preview" class="art-preview" hidden><img id="art-picture" alt=""><figcaption id="art-caption"></figcaption></figure>';
    this.$=id=>host.querySelector('#'+id);
    this.$('art-import').addEventListener('click',()=>this.$('art-file').click());
    this.$('art-file').addEventListener('change',event=>{const file=event.target.files[0];event.target.value='';if(file)this.importFile(file);});
    this.$('art-source').addEventListener('change',()=>{this.selected.set(this.kind,this.$('art-source').value);this.show();});
  }
  setKind(kind){this.kind=kind;this.setData();this.show();}
  setData(){const assets=this.getData().assets.filter(a=>a.kind===this.kind&&a.image),select=this.$('art-source');
    select.replaceChildren(new Option('Bild auswählen …',''),...assets.map(a=>new Option(a.name,a.id)));
    select.value=this.selected.get(this.kind)||'';
  }
  show(){const id=this.$('art-source').value,asset=this.getData().assets.find(a=>a.kind===this.kind&&a.id===id);
    this.$('art-preview').hidden=!asset;this.$('art-empty').hidden=!!asset;
    if(asset){this.$('art-picture').src=asset.image;this.$('art-picture').alt=asset.name;this.$('art-caption').textContent=asset.name+(asset.width?' · '+asset.width+' × '+asset.height+' px':'');}
    this.onChange(this.kind,asset?.id||null);
    this.status(asset?'Dieses Bild ist in der Bibliothek vorhanden und kann einem Projekt zugeordnet werden.':'Füge ein fertiges Bild hinzu oder wähle ein Motiv aus deiner Bibliothek.');
  }
  status(text,error=false){this.$('art-status').textContent=text;this.$('art-status').classList.toggle('error',error);}
  async importFile(file){if(this.importing)return;
    if(file.size>20*1024*1024){this.status('Bitte ein Bild mit höchstens 20 MB wählen.',true);return;}
    const category=this.kind,controller=new AbortController(),timer=setTimeout(()=>controller.abort(),20000);
    this.importing=true;this.$('art-import').disabled=true;this.status('Bild wird unverändert auf deinem PC gespeichert …');
    try{const response=await fetch('/api/images/import',{method:'POST',signal:controller.signal,headers:{'Content-Type':file.type||'application/octet-stream','X-Filename':encodeURIComponent(file.name),'X-Image-Kind':category},body:file});
      const result=await response.json();if(!response.ok)throw Error(result.error||'Das Bild konnte nicht hinzugefügt werden.');
      this.selected.set(category,result.asset.id);await this.onImported(result.asset);this.setData();this.show();
    }catch(error){this.status(error.name==='AbortError'?'Das Hinzufügen dauert zu lange. Prüfe die Bibliothek, bevor du es erneut versuchst.':error.message,true);}
    finally{clearTimeout(timer);this.importing=false;this.$('art-import').disabled=false;}
  }
}
