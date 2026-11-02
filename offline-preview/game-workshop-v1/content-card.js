// Structured contents on the same approved flat card face; no game actions.
const element=(tag,cls,text)=>{const el=document.createElement(tag);if(cls)el.className=cls;if(text!==undefined)el.textContent=text;return el;};

export async function renderContentCard(card,content){
  if(!['country','mission'].includes(content.kind))throw new Error('Nur endliche Conquest-Kartensätze gehören in diese Vorschau.');
  card.classList.add('content-card');card.dataset.contentKind=content.kind;
  const face=card.querySelector('.playing-card-front');face.replaceChildren();
  const header=element('div','content-heading'),category=element('span','content-category',content.category),brand=element('span','content-brand',content.game);
  header.append(category,brand);
  const body=element('div','content-body');
  if(content.kind==='country'){
    const {createCountryCard}=await import('/card-content/conquest/cards.js');
    const original=createCountryCard(content.country);
    body.append(element('h2','content-title',content.title),original.querySelector('.country-card-symbol'),
      element('p','content-type',content.prompt),original.querySelector('.country-card-map'),
      element('p','content-note',content.description));
  }else{
    const prompt=element('p','content-prompt',content.prompt);body.append(prompt);
  }
  const footer=element('div','content-footer',content.kind==='mission'?'Auftragsinhalt · keine laufende Partie':'Länderkarte · Inhalt aus Conquest');
  face.append(header,body,footer);
  requestAnimationFrame(()=>fitContent(body));
}

function fitContent(body){
  for(let size=19;size>=11;size--){body.style.setProperty('--content-font',size+'px');if(body.scrollHeight<=body.clientHeight+1)break;}
}
