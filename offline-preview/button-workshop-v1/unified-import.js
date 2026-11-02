// Translate an original into the same four editable parts as every workshop button.
const split=value=>{const list=[];let depth=0,start=0;for(let i=0;i<value.length;i++){if(value[i]==='(')depth++;if(value[i]===')')depth--;if(value[i]===','&&!depth){list.push(value.slice(start,i).trim());start=i+1;}}list.push(value.slice(start).trim());return list.filter(v=>v&&v!=='none');};
const color=value=>{const nums=value?.match(/[\d.]+/g)?.map(Number)||[0,0,0];return {hex:'#'+nums.slice(0,3).map(n=>Math.round(n).toString(16).padStart(2,'0')).join(''),alpha:nums[3]??1};};
const local=value=>value.replace(/https?:\/\/(?:127\.0\.0\.1|localhost):\d+/g,'');
export function captureButton(root){
  const win=root.ownerDocument.defaultView,face=root.querySelector(':scope > .dice-mini')||root,css=win.getComputedStyle(face),rect=root.getBoundingClientRect();
  const width=rect.width||430,height=rect.height||50;
  const leaf=[...root.querySelectorAll('b,strong,span')].find(el=>el.textContent.trim()&&el.getBoundingClientRect().width>0&&el.textContent.trim().length>2);
  const label=leaf||face,labelCss=win.getComputedStyle(label),labelRect=label.getBoundingClientRect();
  const direct=[...root.childNodes].filter(n=>n.nodeType===3&&n.textContent.trim()).map(n=>n.textContent.trim()).join(' ');
  const text=direct||label.textContent.trim()||face.getAttribute('data-value')||root.getAttribute('aria-label')||'Button';
  const images=[...root.querySelectorAll('img')];const image=images.find(el=>el.getBoundingClientRect().width>width*.45);
  const imageUrl=image?local(image.getAttribute('src')||''):'';
  let depth={x:0,y:0,color:'#7863df'},soft=[];
  for(const shadow of split(css.boxShadow)){
    const ink=shadow.match(/rgba?\([^)]*\)/)?.[0]||'rgb(0,0,0)',nums=shadow.replace(ink,'').match(/-?[\d.]+px/g)?.map(parseFloat)||[];
    if(!shadow.includes('inset')&&!nums[2]&&!nums[3]&&(nums[0]||nums[1]))depth={x:nums[0]||0,y:nums[1]||0,color:color(ink).hex};else soft.push(shadow);
  }
  const background=local(css.backgroundImage),colors=background.match(/rgba?\([^)]*\)/g)||[];
  const surface=color(css.backgroundColor),material=image?'plain':background.includes('gradient(')?'gradient':surface.alpha<1?'translucent':'plain';
  const radius=['TopLeft','TopRight','BottomRight','BottomLeft'].map(key=>Math.min(parseFloat(css['border'+key+'Radius'])||0,Math.min(width,height)/2));
  const contour={template:'rectangle',points:[[0,0],[100,0],[100,100],[0,100]].map(([x,y],i)=>({x,y,round:Math.min(50,radius[i]/Math.min(width,height)*100)}))};
  const symbol=[...root.querySelectorAll('span')].find(el=>el!==leaf&&/^[→←▶♠⚄]$/.test(el.textContent.trim()));
  let svg=root.querySelector('svg')?.outerHTML||'';if(svg.length>6000)svg='';
  return {width,height,font_size:parseFloat(labelCss.fontSize)||15,font_family:labelCss.fontFamily,font_weight:labelCss.fontWeight,letter_spacing:labelCss.letterSpacing,line_height:labelCss.lineHeight,text_transform:labelCss.textTransform,text_shadow:labelCss.textShadow,ink:color(labelCss.color).hex,background,background_size:css.backgroundSize,background_position:css.backgroundPosition,surface:surface.hex,opacity:Math.round(surface.alpha*100),accent:colors.length?color(colors[0]).hex:surface.hex,gradient_to:colors.length?color(colors.at(-1)).hex:surface.hex,gradient_angle:parseFloat(background.match(/(-?[\d.]+)deg/)?.[1]||180),material,edge:parseFloat(css.borderTopWidth)||0,border_color:css.borderTopColor,depth,soft_shadow:soft.join(', ')||'none',image:imageUrl,image_fit:image?win.getComputedStyle(image).objectFit:'contain',text:text.slice(0,90),label_visible:svg&&!direct&&!label.textContent.trim()?0:1,contour,symbol:symbol?.textContent.trim()||'',svg:svg?local(svg):'',label_position:image?{x:(labelRect.x-rect.x)/width*100,y:(labelRect.y-rect.y)/height*100,width:labelRect.width/width*100,height:labelRect.height/height*100}:null};
}
export function recipeFromProfile(profile,source,catalog,previous=null){
  const p=structuredClone(profile),settings={...catalog.defaults,style:'minimal',material:p.material,shape:'custom',edge:Math.min(5,Math.round(p.edge)),finish:'matte',wear:0,accent:p.accent,gradient_to:p.gradient_to,opacity:Math.round(p.opacity/5)*5,font:'source',font_link:'manual',lettering:'plain',label:p.text,depth:Math.max(0,Math.min(20,Math.round(p.depth.y))),depth_x:Math.max(-20,Math.min(20,Math.round(p.depth.x))),depth_mode:'manual',depth_color:p.depth.color,ink_mode:'manual',ink_color:p.ink,font_scale:100,shadow:p.soft_shadow==='none'?0:25,sound:'off'};
  p.initial={material:settings.material,accent:settings.accent,gradient_to:settings.gradient_to,opacity:settings.opacity,shadow:settings.shadow};
  return {schema_version:4,kind:'button',name:previous?.name||source.name.slice(0,80),notes:previous?.notes||'Eigener Entwurf aus '+source.name,parent_id:previous?.parent_id||null,settings,contour:p.contour,base:p,source_button:structuredClone(source),review:Object.fromEntries(catalog.review_dimensions.map(([key])=>[key,'open']))};
}
