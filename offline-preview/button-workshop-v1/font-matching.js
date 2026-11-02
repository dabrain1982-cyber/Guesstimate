export function matchingFont(catalog,settings){
  const value=catalog.font_recommendations[settings.lettering];
  return typeof value==='string'?value:value?.[settings.material]||'inter';
}
export function applyMatchingFont(catalog,settings){if(settings.font_link==='auto')settings.font=matchingFont(catalog,settings);return settings;}
