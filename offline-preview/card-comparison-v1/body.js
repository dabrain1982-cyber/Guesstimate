// One imported card body for the existing comparison, library and authoring views.
import * as T from '/vendor/three.module.js';
export function cardGeometries(modelData){
  const result=new Map();
  for(const [name,data] of Object.entries(modelData.meshes)){
    const geometry=new T.BufferGeometry();geometry.setAttribute('position',new T.Float32BufferAttribute(data.position,3));geometry.setAttribute('uv',new T.Float32BufferAttribute(data.uv,2));geometry.computeVertexNormals();result.set(name,geometry);
  }
  return result;
}
export function cardBody(geometries,materials){
  const group=new T.Group();
  for(const side of ['front','back','edge']){const mesh=new T.Mesh(geometries.get(side),materials[side]);mesh.castShadow=true;mesh.receiveShadow=false;group.add(mesh);}
  return group;
}
export function cardMaterials(front,back,edgeColor='#eee8d5'){
  return {front:new T.MeshPhysicalMaterial({map:front,roughness:.62,clearcoat:.16,clearcoatRoughness:.55}),
    back:new T.MeshPhysicalMaterial({map:back,roughness:.62,clearcoat:.16,clearcoatRoughness:.55}),
    edge:new T.MeshStandardMaterial({color:edgeColor,roughness:.9})};
}
