// A changed action at the same screen position needs a fresh, deliberate press.
export function createActionIntentGuard({now=()=>performance.now(),repeatWindow=600}={}){
  let previous=null;
  return function prepare(button,command,available=()=>true){
    const created=now();
    let press=null;
    button.addEventListener('pointerdown',event=>{
      press={enabled:!button.disabled&&available(),time:event.timeStamp,x:event.clientX,y:event.clientY};
    });
    button.addEventListener('pointercancel',()=>{press=null;});
    return event=>{
      const intent=press;press=null;
      if(button.disabled||!available()||event.timeStamp<created)return false;
      // Keyboard and assistive activation have no pointer press.
      if(event.detail===0)return true;
      if(!intent?.enabled||intent.time<created||event.detail>1)return false;
      const near=previous&&Math.hypot(intent.x-previous.x,intent.y-previous.y)<16;
      const repeated=previous&&intent.time>=previous.time&&intent.time-previous.time<repeatWindow;
      if(near&&repeated&&command!==previous.command)return false;
      previous={...intent,command};
      return true;
    };
  };
}
