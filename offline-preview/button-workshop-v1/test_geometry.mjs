import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {contourError,makeContour,roundedPoints,toPolygon,CONTOUR_ASPECT,CONTOUR_PLANE,buttonMetrics,outlinePath,contourPlane} from './geometry.js';
import {matchingFont,applyMatchingFont} from './font-matching.js';
const catalog=JSON.parse(readFileSync(new URL('./catalog.json',import.meta.url)));
for(const name of Object.keys(catalog.contours)){
  const contour=makeContour(catalog,name);assert.equal(contourError(contour.points),'');
  const rounded=roundedPoints(contour.points);assert(rounded.every(p=>Number.isFinite(p.x)&&Number.isFinite(p.y)&&p.x>=0&&p.x<=100&&p.y>=0&&p.y<=100));
  assert(toPolygon(contour.points).startsWith('polygon('));
}
assert.notEqual(toPolygon(makeContour(catalog,'comic').points),toPolygon(makeContour(catalog,'cut').points));
assert.match(contourError([{x:0,y:0,round:0},{x:100,y:100,round:0},{x:0,y:100,round:0},{x:100,y:0,round:0}]),/kreuzen/);
assert.match(contourError([{x:0,y:0,round:0},{x:50,y:0,round:0},{x:100,y:0,round:0}]),/Fläche/);
console.log('Geometry: templates, rounded boundaries, distinct forms, crossing and degenerate contours passed.');
assert.equal(matchingFont(catalog,{material:'stone',lettering:'carved'}),'cinzel');
assert.equal(matchingFont(catalog,{material:'wood',lettering:'etched'}),'rocksalt');
assert.equal(matchingFont(catalog,{material:'metal',lettering:'screen'}),'sharetechmono');
const manual={font_link:'manual',font:'inter',material:'wood',lettering:'etched'};
applyMatchingFont(catalog,manual);assert.equal(manual.font,'inter');
console.log('Fonts: stone carving, wood scratching, screen and preserved manual choice passed.');
// A wide preview used to squash the same rounded contour into a pointed strip.
// Every rendered size must keep the drawing plane's aspect and scale all parts.
assert.equal(CONTOUR_ASPECT,560/180);
for(const style of ['comic','natural','minimal']){
  const settings={...catalog.defaults,style};
  const small=buttonMetrics(144,settings),large=buttonMetrics(288,settings);
  for(const key of ['fontSize','height','depth','rim'])assert(Math.abs(large[key]-small[key]*2)<1e-9,`${style}: ${key} scales proportionally`);
  for(const width of [96,144,276,640])assert(Math.abs(width/buttonMetrics(width,settings).height-CONTOUR_ASPECT)<1e-9);
}
const example=makeContour(catalog,'comic'),rounded=roundedPoints(example.points);
const pathNumbers=outlinePath(example.points).match(/-?\d+(?:\.\d+)?/g).map(Number);
for(let i=0;i<rounded.length;i++){
  assert(Math.abs((pathNumbers[i*2]-CONTOUR_PLANE.x)/CONTOUR_PLANE.width-rounded[i].x/100)<1e-9);
  assert(Math.abs((pathNumbers[i*2+1]-CONTOUR_PLANE.y)/CONTOUR_PLANE.height-rounded[i].y/100)<1e-9);
}
console.log('Proportions: editor plane, rounded outlines and all button parts agree across sizes and styles.');
// Imported flat buttons use the very same points in the editor, face and sidewalls.
const imported={width:430,height:50,font_size:15},flat={...catalog.defaults,depth:5,height_ratio:100};
const plane=contourPlane(imported,flat),rectangle=[{x:0,y:0,round:34},{x:100,y:0,round:34},{x:100,y:100,round:34},{x:0,y:100,round:34}];
assert(Math.abs(plane.width/plane.height-8.6)<1e-9);
const original=buttonMetrics(430,flat,imported),half=buttonMetrics(215,flat,imported);
assert.equal(original.height,50);assert.equal(original.fontSize,15);assert.equal(original.depth,5);
for(const key of ['height','fontSize','depth','rim'])assert(Math.abs(original[key]-half[key]*2)<1e-9);
const curve=roundedPoints(rectangle,plane);
for(const p of curve.slice(0,13)){const x=p.x*430/100,y=p.y*50/100;assert(Math.abs(Math.hypot(x-17,y-17)-17)<1e-7,'physical corner keeps its 17px circular radius');}
const notched=[rectangle[0],{x:50,y:20,round:0},...rectangle.slice(1)];
assert.equal(contourError(notched),'');assert.notEqual(toPolygon(notched,plane),toPolygon(rectangle,plane));
assert(toPolygon(notched,plane).includes('50.000% 20.000%'));
const physicalPath=outlinePath(notched,plane).match(/-?\d+(?:\.\d+)?(?:e[-+]?\d+)?/g).map(Number),physicalPoints=roundedPoints(notched,plane);
physicalPoints.forEach((p,i)=>{assert(Math.abs(physicalPath[i*2]-(plane.x+p.x*plane.width/100))<1e-7);assert(Math.abs(physicalPath[i*2+1]-(plane.y+p.y*plane.height/100))<1e-7);});
console.log('Shared editor: 430x50 original, circular corners, proportional type/depth and editable notch agree.');
