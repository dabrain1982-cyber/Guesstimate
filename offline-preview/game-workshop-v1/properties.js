/* Shared read-only material and view reference. */
const node=(tag,cls,text)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=text;return n;};
export class PropertyPanels{
  constructor({getData,preview,buttonPreview,inspect}){Object.assign(this,{getData,preview,buttonPreview,inspect});}
  asset(id){return this.getData().assets.find(a=>a.id===id);}
  sample(material){
    if(material.preview.type==='button'){const host=node('div','property-button-sample');this.buttonPreview(host,material.preview.recipe);host.inert=true;return host;}
    const asset=this.asset(material.preview.id);return this.preview(asset);
  }
  materials(host){
    host.replaceChildren();host.classList.add('property-grid');
    for(const material of this.getData().properties.materials){
      const card=node('article','property-card');card.dataset.material=material.id;host.append(card);card.append(this.sample(material));
      const body=node('div','property-card-body');
      body.append(node('h3','',material.name));
      body.append(node('p','',material.description),node('p','property-usage','Beispiel: '+material.usage),node('p','property-note',material.note));
      if(material.preview.type!=='button'){const open=node('button','','Originalbeispiel ansehen');open.type='button';open.addEventListener('click',()=>this.inspect(this.asset(material.preview.id)));body.append(open);}
      for(const id of material.lettering){const asset=this.asset(id),open=node('button','property-lettering',asset.name+' ansehen');open.type='button';open.addEventListener('click',()=>this.inspect(asset));body.append(open);}
      card.append(body);
    }
  }
  views(host){
    host.replaceChildren();host.classList.add('property-grid');
    for(const view of this.getData().properties.views){const card=node('article','property-card'),asset=this.asset(view.example),body=node('div','property-card-body');host.append(card);card.append(this.preview(asset));body.append(node('h3','',view.name),node('p','',view.description),node('small','property-note',view.note));const open=node('button','','Originalbeispiel ansehen');open.type='button';open.addEventListener('click',()=>this.inspect(asset));body.append(open);card.append(body);}
  }
  guide(host){
    host.replaceChildren();
    const intro=node('div','section-heading'),caption=node('div');caption.append(node('p','eyebrow','Eigenschaften deiner Bausteine'),node('h2','','Material & Ansicht'),node('p','','Finde passende Oberflächen und einen Blick auf dein Spiel. Die Beispiele stammen aus dem vorhandenen Baukasten.'));intro.append(caption);host.append(intro);
    const note=node('p','recommendation','Diese Beispiele dienen als Referenz für spätere Recherchen. Die Originale bleiben erhalten.');host.append(note);
    host.append(node('h3','property-section-title','Materialfamilien'));
    const materials=node('div');host.append(materials);this.materials(materials);host.append(node('h3','property-section-title','Ansicht'));
    const views=node('div');host.append(views);this.views(views);host.append(node('h3','property-section-title','Licht & Bewegung'));
    const motion=node('div','property-motion');motion.append(node('p','','Licht, Schatten und Bewegung gehören zur jeweiligen Darstellung. Hier siehst du Beispiele aus dem vorhandenen Bestand.'));
    for(const row of this.getData().properties.motion){const p=node('p');p.append(node('strong','',row.name+': '),document.createTextNode(row.description));motion.append(p);}host.append(motion);
  }
}
