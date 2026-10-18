"""Fail-closed fixed-source controls; no model, cloud or Blender imports."""
import ast
import hashlib
import struct

RAW_SHA = 'bdd085b6b86ad2dd731beda22cb9b1f03fd6b3da961bf6d72a91e792d9a8b6ff'
SHELL_SHA = '95f8e7abf28c883942cface5966c7dadbe44ad9baefce78c9a9d9652927ef208'
GLB_SHA = '9678b00014314123640e9a5437ae81f738e143d30d528a2df1f5f6e8fc11d915'


def split_exporter(adapted):
    """Split the reviewed exporter at its bake boundary, not its geometry route.

    Caller substitutes the hash-bound reconstructed shell for the original
    remesh call, preserving original source BVH/material sampling. A single
    returned surface is baked twice to vary atlas resolution alone.
    """
    anchor = '    # --- Texture Baking (Attribute Sampling) ---'
    if adapted.count(anchor) != 1 or adapted.count('def to_glb(') != 1:
        raise ValueError('Exporter boundary drift')
    prefix, baking = adapted.split(anchor)
    prefix = prefix.replace('def to_glb(', 'def prepare_surface(', 1)
    names = ('out_vertices', 'out_faces', 'out_uvs', 'out_normals', 'vertices', 'faces',
             'bvh', 'attr_volume', 'coords', 'attr_layout', 'grid_size', 'voxel_size', 'aabb', 'remesh')
    prefix += '\n    return {\n' + ''.join(f'        "{n}": {n},\n' for n in names) + '    }\n\n'
    suffix = 'def bake_surface(surface, texture_size, verbose=False):\n'
    suffix += '    use_tqdm = False\n'
    suffix += ''.join(f'    {n} = surface["{n}"]\n' for n in names)
    result = prefix + suffix + baking
    ast.parse(result)
    if 'import nvdiffrast' in result:
        raise ValueError('Restricted exporter survived')
    return result


def glb_opacity_variant(data, mode='BLEND'):
    """Modify only glTF JSON material alphaMode; retain binary payload byte-for-byte."""
    import json
    if mode not in {'OPAQUE', 'BLEND'}:
        raise ValueError('Unreviewed opacity mode')
    magic, version, length = struct.unpack_from('<4sII', data)
    if (magic, version, length) != (b'glTF', 2, len(data)):
        raise ValueError('Invalid GLB header')
    chunks, offset = [], 12
    while offset < len(data):
        size, kind = struct.unpack_from('<I4s', data, offset)
        offset += 8
        payload = data[offset:offset + size]
        if len(payload) != size:
            raise ValueError('Truncated GLB')
        chunks.append((kind, payload))
        offset += size
    if offset != len(data) or not chunks or chunks[0][0] != b'JSON':
        raise ValueError('Invalid GLB chunks')
    document = json.loads(chunks[0][1])
    if not document.get('materials'):
        raise ValueError('No material to compare')
    for material in document['materials']:
        if 'baseColorTexture' not in material.get('pbrMetallicRoughness', {}):
            raise ValueError('Opacity control requires base color texture')
        material['alphaMode'] = mode
    blob = json.dumps(document, separators=(',', ':')).encode()
    blob += b' ' * (-len(blob) % 4)
    chunks[0] = (b'JSON', blob)
    body = b''.join(struct.pack('<I4s', len(payload), kind) + payload for kind, payload in chunks)
    return struct.pack('<4sII', b'glTF', 2, len(body) + 12) + body


def array_digest(arrays):
    """Works on NumPy arrays; include names/shapes/dtypes, not only raw bytes."""
    digest = hashlib.sha256()
    for name, array in sorted(arrays.items()):
        digest.update(str((name, array.shape, str(array.dtype))).encode())
        digest.update(array.tobytes(order='C'))
    return digest.hexdigest()
