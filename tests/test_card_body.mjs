import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
const root=new URL('../',import.meta.url);
const three=new URL('offline-preview/conquest-2-5d-v1/vendor/three/three.module.js',root);
const source=await readFile(new URL('offline-preview/card-comparison-v1/body.js',root),'utf8');
const body=await import('data:text/javascript;base64,'+Buffer.from(source.replace("'/vendor/three.module.js'",JSON.stringify(three.href))).toString('base64'));
const model=JSON.parse(await readFile(new URL('offline-preview/card-comparison-v1/assets/mehrasaur/card-mesh.json',root),'utf8'));
const geometries=body.cardGeometries(model);
let triangles=0;
for(const [name,data] of Object.entries(model.meshes)){
  const geometry=geometries.get(name);triangles+=geometry.attributes.position.count/3;
  assert.deepEqual(Array.from(geometry.attributes.position.array),Array.from(new Float32Array(data.position)));
  assert.deepEqual(Array.from(geometry.attributes.uv.array),Array.from(new Float32Array(data.uv)));
}
assert.equal(triangles,44);
const T=await import(three.href),front=new T.Texture(),back=new T.Texture();
const materials=body.cardMaterials(front,back,'#123456'),card=body.cardBody(geometries,materials);
assert.equal(card.children.length,3);
assert.equal(card.children[0].material.map,front);assert.equal(card.children[1].material.map,back);
assert.equal(card.children[2].material.color.getHexString(),'123456');
const bounds=new T.Box3().setFromObject(card).getSize(new T.Vector3());
for(const [actual,expected] of [[bounds.x,model.metadata.dimensions[0]],[bounds.y,model.metadata.dimensions[1]],[bounds.z,model.metadata.dimensions[2]]])assert.ok(Math.abs(actual-expected)<1e-4);
console.log('Shared card body: original vertices, UVs, 44 triangles and material sides preserved.');
