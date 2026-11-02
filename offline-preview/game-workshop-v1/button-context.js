// Only this inert preview helper runs; game scripts and actions are stripped.
const target=document.querySelector('[data-usage-target]');
if(!target)parent.postMessage({channel:'stormseed-button-context',ready:false},location.origin);
if(target){
  for(const [panelAttribute,tabAttribute] of [['data-shop-panel','data-shop-tab'],['data-profile-panel','data-profile-tab'],['data-leaderboard-panel','data-leaderboard-tab']]){
    const panel=target.closest('['+panelAttribute+']');if(!panel)continue;
    const value=panel.getAttribute(panelAttribute);
    for(const sibling of document.querySelectorAll('['+panelAttribute+']'))sibling.hidden=sibling!==panel;
    for(const tab of document.querySelectorAll('['+tabAttribute+']'))tab.setAttribute('aria-selected',String(tab.getAttribute(tabAttribute)===value));
  }
  for(let parent=target;parent;parent=parent.parentElement){
    parent.hidden=false;
    if(parent.tagName==='DETAILS')parent.open=true;
  }
  const dialog=target.closest('dialog');
  if(dialog&&!dialog.open)dialog.showModal();
  document.body.inert=true;
  if(dialog)dialog.inert=true;
  async function reveal(){
    await document.fonts.ready;
    target.scrollIntoView({block:'center',inline:'center'});
    parent.postMessage({channel:'stormseed-button-context',ready:true},location.origin);
  }
  if(document.readyState==='complete')reveal();else window.addEventListener('load',reveal,{once:true});
}
