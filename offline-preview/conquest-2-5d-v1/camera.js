import { MathUtils } from './vendor/three/three.module.js';

export const MIN_ANGLE = 32;
export const MAX_ANGLE = 82;

export function framingAtAngle(angle, height, topInset = 0) {
  const progress = MathUtils.clamp((angle - MIN_ANGLE) / (MAX_ANGLE - MIN_ANGLE), 0, 1);
  const blend = progress * progress * (3 - 2 * progress);
  return {
    topPixel: topInset + 4,
    horizontalLimit: MathUtils.lerp(.98, .995, blend),
    verticalAlignment: MathUtils.lerp(1, .5, blend),
  };
}

export function tableViewBounds(width, height, { rosterBottom = 0, actionsTop = height, controlsTop = height } = {}) {
  return {
    topPixel: width <= 560 ? Math.max(4, rosterBottom + 8) : 4,
    bottomPixel: Math.min(height * .995, actionsTop - 6, controlsTop - 6),
  };
}

export function placeCamera(camera, target, degrees, distance) {
  const radians = MathUtils.degToRad(degrees);
  camera.position.set(target.x, target.y + Math.sin(radians) * distance, target.z + Math.cos(radians) * distance);
  camera.lookAt(target);
  camera.updateMatrixWorld(true);
}

export function frameCamera(camera, { target, points, angle, width, height, topPixel, bottomPixel = height * .995, horizontalLimit = .98, verticalAlignment = .5 }) {
  camera.clearViewOffset();
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
  const topLimit = 1 - 2 * topPixel / height;
  const bottomLimit = 1 - 2 * bottomPixel / height;
  const availableSpan = topLimit - bottomLimit;
  if (availableSpan <= .05) throw new Error('The viewport is too short to show the board.');
  const fits = (distance) => {
    placeCamera(camera, target, angle, distance);
    let minY = Infinity;
    let maxY = -Infinity;
    for (const point of points) {
      const projected = point.clone().project(camera);
      if (Math.abs(projected.x) > horizontalLimit || projected.z <= -1 || projected.z >= 1) return false;
      minY = Math.min(minY, projected.y);
      maxY = Math.max(maxY, projected.y);
    }
    return maxY - minY <= availableSpan;
  };
  let low = 1;
  let high = 120;
  if (!fits(high)) throw new Error('The available viewport is too small to frame the table.');
  for (let i = 0; i < 22; i++) {
    const middle = (low + high) / 2;
    if (fits(middle)) high = middle;
    else low = middle;
  }
  const distance = high * 1.0002;
  placeCamera(camera, target, angle, distance);
  const projected = points.map(point => point.clone().project(camera).y);
  const maxY = Math.max(...projected), minY = Math.min(...projected);
  const spare = availableSpan - (maxY - minY);
  const shift = topLimit - maxY - spare * MathUtils.clamp(verticalAlignment, 0, 1);
  camera.setViewOffset(width, height, 0, shift * height / 2, width, height);
  camera.updateMatrixWorld(true);
  return { distance, topLimit, bottomLimit };
}
