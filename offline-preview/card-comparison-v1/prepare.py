"""Prepare licensed comparison assets without changing any game source."""
from pathlib import Path
from zipfile import ZipFile
import hashlib
import json
import math

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DOWNLOADS = ROOT / 'runtime/card-comparison-20261027/downloads'


def write(name, data):
    path = HERE / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data if isinstance(data, bytes) else data.encode('utf-8'))


def prepare():
    checksums = {}
    for name, expected in {
        'kenney_boardgame-pack.zip': '3b6a7dd5af658d1ffa0071429d5dde10ff63121e88bd06d4904e721e60b2c398',
        'poker_pack.zip': '04f1281f413dd8b72ba5fbba2f33cfe683eed7fed6712240776b1a1e54a96bc4',
    }.items():
        actual = hashlib.sha256((DOWNLOADS / name).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f'Unexpected archive: {name}')
        checksums[name] = actual
    with ZipFile(DOWNLOADS / 'kenney_boardgame-pack.zip') as archive:
        for name in archive.namelist():
            # Explicit data-only subset; no scripts, SWFs or executables extracted.
            if name.startswith('PNG/Cards/') and name.endswith('.png'):
                write('assets/kenney/' + Path(name).name, archive.read(name))
        write('assets/kenney/license.txt', archive.read('license.txt'))
    with ZipFile(DOWNLOADS / 'poker_pack.zip') as archive:
        for name in ('card.obj', 'card.mtl'):
            write('assets/mehrasaur/' + name, archive.read('dist/obj_mtl/' + name))
        # Keep the editable original; never execute or open its Blender file.
        write('assets/mehrasaur/card.blend', archive.read('dist/blend/card.blend'))
    obj = (HERE / 'assets/mehrasaur/card.obj').read_text()
    vertices, faces = [], []
    # Source card is rotated about Z. Its long axis is source Z.
    a = math.radians(46.087)
    c, s = math.cos(a), math.sin(a)
    for line in obj.splitlines():
        p = line.split()
        if not p:
            continue
        if p[0] == 'v':
            x, y, z = map(float, p[1:4])
            vertices.append([c*x+s*y, z, s*x-c*y])
        if p[0] == 'f':
            faces.append([int(v.split('/')[0])-1 for v in p[1:]])
    lo = [min(v[i] for v in vertices) for i in range(3)]
    hi = [max(v[i] for v in vertices) for i in range(3)]
    scale = 192 / (hi[1]-lo[1])
    vertices = [[(v[i]-(lo[i]+hi[i])/2)*scale for i in range(3)] for v in vertices]
    width = (hi[0]-lo[0])*scale
    meshes = {name: dict(position=[], uv=[]) for name in ('front', 'back', 'edge')}
    for face in faces:
        va, vb, vc = (vertices[i] for i in face[:3])
        ab = [vb[i]-va[i] for i in range(3)]
        ac = [vc[i]-va[i] for i in range(3)]
        normal = [ab[1]*ac[2]-ab[2]*ac[1], ab[2]*ac[0]-ab[0]*ac[2], ab[0]*ac[1]-ab[1]*ac[0]]
        length = math.sqrt(sum(v*v for v in normal))
        nz = normal[2]/length
        side = ('front' if nz > 0 else 'back') if abs(nz) > .99 else 'edge'
        target = meshes[side]
        for j in range(1, len(face)-1):
            for index in (face[0], face[j], face[j+1]):
                x, y, z = vertices[index]
                target['position'].extend(round(v, 6) for v in (x, y, z))
                target['uv'].extend([round((x/width+.5) if side != 'back' else (.5-x/width), 7), round(y/192+.5, 7)])
    metadata = dict(source='https://opengameart.org/content/poker-pack', author='mehrasaur', license='CC0-1.0',
                    source_vertices=len(vertices), triangles=sum(len(v['position'])//9 for v in meshes.values()),
                    dimensions=[width, 192, (hi[2]-lo[2])*scale],
                    changes='Rigid axis alignment, centering, uniform scale, convex face triangulation and planar face/back UVs; original outline retained.')
    write('assets/mehrasaur/card-mesh.json', json.dumps(dict(metadata=metadata, meshes=meshes), separators=(',', ':')))
    write('assets/import-manifest.json', json.dumps(dict(downloaded='2026-10-27', archives=checksums, model=metadata), indent=2))
    print(json.dumps(metadata, indent=2))


if __name__ == '__main__':
    prepare()
