// Small, bounded tabletop fall probe; not a general rigid-body solver.
export function fallStep(body, dt, gravity, bounce, floor) {
  let velocity=body.velocity-gravity*dt, y=body.y+velocity*dt, resting=false;
  if(y<=floor){y=floor;velocity=-velocity*bounce;if(velocity<.18){velocity=0;resting=true;}}
  return {y,velocity,resting};
}
export function ease(t){t=Math.max(0,Math.min(1,t));return t*t*(3-2*t);}
