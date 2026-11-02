import test from 'node:test';
import assert from 'node:assert/strict';
import { PerspectiveCamera, Vector3 } from './vendor/three/three.module.js';
import { frameCamera, framingAtAngle, tableViewBounds, MIN_ANGLE, MAX_ANGLE } from './camera.js';

const target = new Vector3(0, 2.85, 0);
const boardWidth = 12;
const boardDepth = 12 * 1225 / 1284;
const corners = [-1, 1].flatMap(x => [-1, 1].map(z => new Vector3(x * boardWidth / 2, 2.928, z * boardDepth / 2)));

for (const [width, height, topInset] of [
  [2133, 950, 0], [1920, 900, 0], [1920, 1080, 0],
  [1366, 768, 0], [1024, 600, 0], [390, 844, 220],
]) {
  test(`The map fills the usable ${width}x${height} view throughout the lean`, () => {
    const camera = new PerspectiveCamera(40, width / height, .15, 200);
    let previousPosition;
    for (let angle = MIN_ANGLE; angle <= MAX_ANGLE; angle += .25) {
      const framing = framingAtAngle(angle, height, topInset);
      const result = frameCamera(camera, { target, points: corners, angle, width, height, ...framing });
      assert.ok(Number.isFinite(result.distance));
      const projected = corners.map(point => point.clone().project(camera));
      for (const point of projected) {
        assert.ok(point.z > -1 && point.z < 1, 'The map must stay in front of the camera.');
        assert.ok(Math.abs(point.x) <= framing.horizontalLimit + 1e-6, `Horizontal edge at ${angle} degrees`);
        assert.ok(point.y <= result.topLimit + 1e-6, `Map exceeds upper usable boundary at ${angle} degrees`);
        assert.ok(point.y >= result.bottomLimit - 1e-6, `Map cut off below viewport at ${angle} degrees`);
      }
      const horizontalUse = Math.max(...projected.map(point => Math.abs(point.x))) / framing.horizontalLimit;
      const verticalUse = (Math.max(...projected.map(point => point.y)) - Math.min(...projected.map(point => point.y))) / (result.topLimit - result.bottomLimit);
      assert.ok(Math.max(horizontalUse, verticalUse) > .998, 'The view must use the available size instead of fitting every pose at one distant radius.');
      assert.equal(camera.fov, 40, 'Leaning must not change the lens.');
      if (previousPosition) assert.ok(camera.position.distanceTo(previousPosition) < result.distance * .012, 'The lean must remain continuous.');
      previousPosition = camera.position.clone();
    }
    assert.deepEqual(target.toArray(), [0, 2.85, 0]);
  });
}

test('The seated view reaches the lower edge and uses nearly the full map width', () => {
  const width = 1920, height = 900;
  const camera = new PerspectiveCamera(40, width / height, .15, 200);
  frameCamera(camera, { target, points: corners, angle: MIN_ANGLE, width, height, ...framingAtAngle(MIN_ANGLE, height, 0) });
  const mapHalfWidth = Math.max(...corners.map(point => Math.abs(point.clone().project(camera).x)));
  assert.ok(mapHalfWidth > .975 && mapHalfWidth <= .98);
  const bottom = Math.min(...corners.map(point => point.clone().project(camera).y));
  assert.ok(Math.abs(bottom - (1 - 2 * .995)) < .001, 'Do not leave a floor gap in front of the table.');
});

test('The overview balances spare space instead of leaving it all below the map',()=>{
  const width=700,height=1000,camera=new PerspectiveCamera(40,width/height,.15,200);
  const framed=frameCamera(camera,{target,points:corners,angle:MAX_ANGLE,width,height,...framingAtAngle(MAX_ANGLE,height,0),bottomPixel:900});
  const ys=corners.map(point=>point.clone().project(camera).y);
  const topGap=framed.topLimit-Math.max(...ys),bottomGap=Math.min(...ys)-framed.bottomLimit;
  assert.ok(Math.abs(topGap-bottomGap)<1e-6);
});

test('The overview can crop the front wooden rim while keeping the entire map visible', () => {
  const width = 1920, height = 900;
  const camera = new PerspectiveCamera(40, width / height, .15, 200);
  frameCamera(camera, { target, points: corners, angle: MAX_ANGLE, width, height, ...framingAtAngle(MAX_ANGLE, height, 0) });
  const frontRim = new Vector3(0, 2.905, (boardDepth + 1.1) / 2).project(camera);
  assert.ok(frontRim.y < -1, 'The front wooden rim should extend below the image.');
  assert.ok(corners.every(point => point.clone().project(camera).y >= -.995));
});


test('The free upper edge and both bottom controls bound the same complete map',()=>{
  for(const [width,height,rosterBottom,actionsTop,controlsTop] of [
    [1670,1244,410,1170,1195],[1280,720,400,645,675],
    [1024,768,430,610,718],[390,844,205,690,798],[320,660,190,430,615],
  ]){
    const bounds=tableViewBounds(width,height,{rosterBottom,actionsTop,controlsTop});
    assert.equal(bounds.topPixel,width>560?4:rosterBottom+8);
    assert.ok(bounds.bottomPixel<=actionsTop-6 && bounds.bottomPixel<=controlsTop-6);
    for(const angle of [MIN_ANGLE,57,MAX_ANGLE]){
      const camera=new PerspectiveCamera(40,width/height,.15,200);
      frameCamera(camera,{target,points:corners,angle,width,height,...framingAtAngle(angle,height),...bounds});
      for(const point of corners.map(point=>point.clone().project(camera))){
        const y=(1-point.y)*height/2;
        assert.ok(y>=bounds.topPixel-1e-5 && y<=bounds.bottomPixel+1e-5);
      }
    }
  }
});
