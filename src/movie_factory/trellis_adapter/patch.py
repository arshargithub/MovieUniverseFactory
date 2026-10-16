"""Build a reviewable patch for exact upstream files; never execute upstream setup."""
import ast
import difflib
import hashlib
from pathlib import Path

PINS = {
    'postprocess.py': 'ef51a1ba0f2748ffb4c265b47d382cee956f23c6a52d0f3587e6d8beccb7e54a',
    'trellis2_image_to_3d.py': 'e2addfca672354284b23d1541a8f49228d5a727d49220fcb8512cca2cdd38ce9',
}
TARGETS = {'postprocess.py': 'o-voxel/o_voxel/postprocess.py',
           'trellis2_image_to_3d.py': 'trellis2/pipelines/trellis2_image_to_3d.py'}


def once(source, old, new):
    if source.count(old) != 1:
        raise ValueError('Upstream anchor not unique')
    return source.replace(old, new, 1)


def adapted_sources(upstream):
    sources = {}
    for name, digest in PINS.items():
        data = (Path(upstream)/name).read_bytes()
        # apply_patch stores a final newline; upstream postprocess has none.
        # Accept only that exact transport normalization, not arbitrary drift.
        if name == 'postprocess.py' and data.endswith(b'\n'):
            data = data[:-1]
        if hashlib.sha256(data).hexdigest() != digest:
            raise ValueError('Upstream drift: '+name)
        sources[name] = data.decode()
    export = once(sources['postprocess.py'], 'import nvdiffrast.torch as dr', 'from ._mf_uvraster import rasterize_uv')
    start = export.index('    # Setup differentiable rasterizer context')
    end = export.index('    # Map these positions back', start)
    export = export[:start] + '''    # No auto-selection or fallback to restricted rasterization.
    mask, triangle_ids, weights = rasterize_uv(out_uvs, out_faces, texture_size)
    if not bool(mask.any()):
        raise ValueError("UV unwrap produced no covered texels")
    valid_pos = (out_vertices[out_faces[triangle_ids[mask]].long()] * weights[mask].unsqueeze(-1)).sum(1)

''' + export[end:]
    export = once(export, 'from ._mf_uvraster import rasterize_uv',
                  'from ._mf_uvraster import rasterize_uv\nfrom ._mf_material import finish_glb')
    start = export.index('    mask = mask.cpu().numpy()')
    export = export[:start] + '''    result = finish_glb(out_vertices, out_faces, out_uvs, out_normals,
                        attrs, mask, attr_layout, remesh)
    if use_tqdm:
        pbar.update(1)
        pbar.close()
    return result
'''
    pipe = once(sources['trellis2_image_to_3d.py'], 'from . import samplers, rembg',
                'from . import samplers\nfrom ._mf_alpha import prepare_rgba')
    pipe = once(pipe, "        pipeline.rembg_model = getattr(rembg, args['rembg_model']['name'])(**args['rembg_model']['args'])", '        pipeline.rembg_model = None  # prepared alpha only; never load BRIA')
    pipe = once(pipe, '        self.rembg_model = rembg_model',
                '        if rembg_model is not None:\n            raise ValueError("Background model prohibited in this adapter")\n        self.rembg_model = None')
    start = pipe.index('    def preprocess_image(')
    end = pipe.index('    def get_cond(', start)
    pipe = pipe[:start] + '''    def preprocess_image(self, input: Image.Image) -> Image.Image:
        return prepare_rgba(input)

''' + pipe[end:]
    pipe = once(pipe, '        if preprocess_image:\n            image = self.preprocess_image(image)',
                '        if not preprocess_image:\n            raise ValueError("Prepared-alpha admission cannot be bypassed")\n        image = self.preprocess_image(image)')
    result = {TARGETS['postprocess.py']: export, TARGETS['trellis2_image_to_3d.py']: pipe,
              'o-voxel/o_voxel/_mf_uvraster.py': Path(__file__).with_name('uvraster.py').read_text(),
              'trellis2/pipelines/_mf_alpha.py': Path(__file__).with_name('admission.py').read_text(),
              'o-voxel/o_voxel/_mf_material.py': Path(__file__).with_name('material.py').read_text()}
    for path, source in result.items():
        ast.parse(source, filename=path)
        if 'import nvdiffrast' in source or 'getattr(rembg' in source or 'import samplers, rembg' in source:
            raise ValueError('Prohibited path survived adapter')
    return result


def unified_patch(upstream):
    result = adapted_sources(upstream)
    originals = {TARGETS[n]: (Path(upstream)/n).read_text() for n in PINS}
    originals[TARGETS['postprocess.py']] = originals[TARGETS['postprocess.py']].removesuffix('\n')
    lines = []
    for path, source in result.items():
        diff = difflib.unified_diff(originals.get(path, '').splitlines(True), source.splitlines(True),
                                  fromfile='a/'+path if path in originals else '/dev/null', tofile='b/'+path)
        for line in diff:
            lines.append(line if line.endswith('\n') else line+'\n\\ No newline at end of file\n')
    return ''.join(lines)
