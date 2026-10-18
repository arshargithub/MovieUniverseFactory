"""Decode saved301 latents; repair/export in a fresh process, no new sampling."""
import gc
import importlib.metadata
import json
import os
from pathlib import Path
import sys
import time
from fractions import Fraction

import trellis298_worker as original
from trellis298_worker import BASE, OUT, REV, dump, sha, run, RestrictedImports

BUCKET = 'mf-trellis303-recovery-281482331395'
LATENT_SHA = '1676894daec0ef9006db5ecc6abf2251b4eca41882ed378c6acbc8652aadfbc6'
CONFIG_SHA = '222c359ab1ed9bc6735a640a34f95d47f8681b9bc4aaa101bfb80274676253c6'
FOLDER = OUT / 'head1024'
DECODERS = {'shape_slat_decoder': 'ckpts/shape_dec_next_dc_f16c32_fp16',
            'tex_slat_decoder': 'ckpts/tex_dec_next_dc_f16c32_fp16'}


def restrict():
    names = {d.metadata['Name'].lower().replace('_', '-') for d in importlib.metadata.distributions()}
    if names & {'nvdiffrast', 'nvdiffrec', 'bria-rmbg', 'rembg', 'plyfile'}:
        raise RuntimeError('Prohibited dependency')
    sys.meta_path.insert(0, RestrictedImports())


def memory(stage):
    import torch
    torch.cuda.synchronize()
    free, total = torch.cuda.mem_get_info()
    record = {'stage': stage, 'pid': os.getpid(), 'free_bytes': free, 'total_bytes': total,
              'allocated_bytes': torch.cuda.memory_allocated(), 'reserved_bytes': torch.cuda.memory_reserved(),
              'peak_allocated_bytes': torch.cuda.max_memory_allocated(),
              'peak_reserved_bytes': torch.cuda.max_memory_reserved(), 'monotonic': time.monotonic()}
    dump(OUT / ('memory-' + stage + '.json'), record)
    print('MEMORY', json.dumps(record), flush=True)


def upload(path):
    path = Path(path)
    if path.parent != FOLDER or path.name not in {'raw-shape.safetensors', 'source.safetensors',
            'geometry.json', 'repaired.safetensors', 'remeshed-source.safetensors', 'candidate.glb', 'receipt.json'}:
        raise ValueError('Unreviewed checkpoint path')
    run(['aws', 's3', 'cp', str(path), f's3://{BUCKET}/output/checkpoints/{path.name}',
         '--only-show-errors', '--region', 'us-east-1'])
    dump(OUT / ('upload-' + path.name + '.json'), {'sha256': sha(path), 'bytes': path.stat().st_size,
        'bucket': BUCKET, 'key': 'output/checkpoints/' + path.name, 'public': False})


def save_tensors(name, tensors):
    from safetensors.torch import save_file
    # Plain nonexecutable tensors; clone shared coordinates before serialization.
    path = FOLDER / name
    save_file({k: v.detach().cpu().contiguous().clone() for k, v in tensors.items()}, str(path))
    upload(path)


def validate_metadata(meta):
    if meta['resolution'] != 1024 or meta['seed'] != 298 or meta['core_revision'] != REV:
        raise ValueError('Checkpoint provenance mismatch')
    if meta['latents_sha256'] != LATENT_SHA or meta['pipeline_config_sha256'] != CONFIG_SHA:
        raise ValueError('Checkpoint binding mismatch')
    if meta['denormalized_for_decoder'] is not True or meta['pipeline_type'] != '1024_cascade':
        raise ValueError('Latent semantics mismatch')
    for key in ('shape', 'texture'):
        if meta[key]['shape'] != [1, 32] or meta[key]['scale'] != [[1, 1]] * 3:
            raise ValueError('Unsupported sparse shape/scale')
        if meta[key]['features_dtype'] != 'torch.float32' or meta[key]['coordinates_dtype'] != 'torch.int32':
            raise ValueError('Unsupported sparse dtype')


def restore(tensors, meta):
    import torch
    from trellis2.modules.sparse import SparseTensor
    validate_metadata(meta)
    if set(tensors) != {'shape_feats', 'shape_coords', 'texture_feats', 'texture_coords'}:
        raise ValueError('Unexpected tensor keys')
    restored = []
    for label in ('shape', 'texture'):
        f, c = tensors[label + '_feats'], tensors[label + '_coords']
        if f.dtype != torch.float32 or c.dtype != torch.int32 or f.ndim != 2 or c.shape != (f.shape[0], 4) or f.shape[1] != 32:
            raise ValueError('Invalid tensor layout')
        if len(f) == 0 or not torch.isfinite(f).all() or (c < 0).any() or (c[:, 0] != 0).any() or c[:, 1:].max() >= 1024:
            raise ValueError('Invalid tensor values')
        if len(torch.unique(c, dim=0)) != len(c):
            raise ValueError('Duplicate sparse coordinates')
        item = SparseTensor(feats=f.cuda(), coords=c.cuda(), shape=torch.Size(meta[label]['shape']),
                            scale=tuple(Fraction(*x) for x in meta[label]['scale']))
        if list(item.shape) != meta[label]['shape'] or len(item.layout) != 1:
            raise ValueError('Sparse reconstruction mismatch')
        restored.append(item)
    if not torch.equal(restored[0].coords, restored[1].coords):
        raise ValueError('Shape/texture coordinates disagree')
    return restored


def preflight():
    original.preflight()
    import torch
    from trellis2.modules import sparse as sp
    from safetensors.torch import save_file, load_file
    torch.manual_seed(303)
    coords = torch.tensor([[0,x,y,z] for x in range(2) for y in range(2) for z in range(2)], dtype=torch.int32, device='cuda')
    feats = torch.randn(8, 32, device='cuda', dtype=torch.float16)
    source = sp.SparseTensor(feats=feats, coords=coords, shape=torch.Size([1,32]))
    conv = sp.SparseConv3d(32, 32, 3).cuda().half().eval()
    with torch.no_grad():
        first = conv(source)
        cached = conv(source)
        path = OUT / 'sparse-control.safetensors'
        save_file({'feats':feats.cpu(), 'coords':coords.cpu()}, str(path))
        saved = load_file(str(path))
        fresh = sp.SparseTensor(feats=saved['feats'].cuda(), coords=saved['coords'].cuda(), shape=source.shape, scale=source._scale)
        result = conv(fresh)
    assert torch.equal(first.coords, result.coords)
    assert torch.allclose(first.feats, result.feats, atol=1e-6, rtol=1e-6)
    assert torch.allclose(cached.feats, result.feats, atol=1e-6, rtol=1e-6)
    dump(OUT / 'sparse-reconstruction-control.json', {'status':'PASS', 'max_error':float((first.feats-result.feats).abs().max()),
        'limit':'Small serialized sparse-convolution cache reconstruction; not bit-identical replay of unsaved301 decoded geometry'})


def decode():
    restrict()
    import torch
    from safetensors.torch import load_file
    from huggingface_hub import hf_hub_download
    from trellis2 import models
    from trellis2.pipelines import Trellis2ImageTo3DPipeline
    assert torch.cuda.get_device_properties(0).total_memory >= 44 * 1024**3
    latent = BASE / 'checkpoint/latents.safetensors'
    assert sha(latent) == LATENT_SHA
    meta = json.loads((BASE / 'checkpoint/latents.json').read_text())
    validate_metadata(meta)
    manifest = json.loads((BASE / 'checkpoint/weight-manifest.json').read_text())
    local = {}
    weights = BASE / 'weights'; weights.mkdir(exist_ok=True)
    for key, prefix in DECODERS.items():
        for ext in ('.json', '.safetensors'):
            filename = prefix + ext
            path = Path(hf_hub_download('microsoft/TRELLIS.2-4B', filename, revision=REV, token=False))
            assert sha(path) == manifest['files']['microsoft/TRELLIS.2-4B/' + filename]['sha256']
            (weights / (key + ext)).symlink_to(path)
        local[key] = str(weights / key)
    os.environ['HF_HUB_OFFLINE'] = os.environ['TRANSFORMERS_OFFLINE'] = '1'
    pipeline = Trellis2ImageTo3DPipeline(models={k: models.from_pretrained(p) for k,p in local.items()}, low_vram=True)
    pipeline.cuda()
    shape, texture = restore(load_file(str(latent)), meta)
    memory('before-shape')
    with torch.no_grad():
        meshes, subs = pipeline.decode_shape_slat(shape, 1024)
        assert len(meshes) == 1
        mesh = meshes[0]
        memory('after-shape')
        save_tensors('raw-shape.safetensors', {'vertices':mesh.vertices, 'faces':mesh.faces})
        attrs = pipeline.decode_tex_slat(texture, subs)
        memory('after-texture')
        value = attrs[0]
        save_tensors('source.safetensors', {'vertices':mesh.vertices, 'faces':mesh.faces,
                     'attrs':value.feats, 'coords':value.coords[:,1:]})
        dump(FOLDER / 'geometry.json', {'voxel_size':1/1024, 'layout':{k:[v.start,v.stop] for k,v in pipeline.pbr_attr_layout.items()},
            'vertices':len(mesh.vertices), 'faces':len(mesh.faces), 'source_sha256':sha(FOLDER/'source.safetensors'),
            'latents_sha256':LATENT_SHA, 'repair_applied':False, 'decoder_process':os.getpid()})
        upload(FOLDER/'geometry.json')
    dump(OUT/'decode.json', {'status':'PASS', 'pid':os.getpid(), 'loaded_models':list(local),
                           'new_sampling':False, 'image_encoder_loaded':False})


def export():
    restrict()
    import torch
    from safetensors.torch import load_file
    from trellis2.representations.mesh import Mesh
    import o_voxel
    import cumesh
    info = json.loads((FOLDER/'geometry.json').read_text())
    assert os.getpid() != info['decoder_process']
    assert sha(FOLDER/'source.safetensors') == info['source_sha256']
    source = load_file(str(FOLDER/'source.safetensors'))
    memory('fresh-repair-process')
    mesh = Mesh(source['vertices'].cuda(), source['faces'].cuda())
    mesh.fill_holes(max_hole_perimeter=3e-2)
    memory('after-repair')
    save_tensors('repaired.safetensors', {'vertices':mesh.vertices, 'faces':mesh.faces})
    vertices, faces = mesh.vertices, mesh.faces
    del mesh
    gc.collect(); torch.cuda.empty_cache()
    memory('before-export')
    remesh = cumesh.remeshing.remesh_narrow_band_dc
    def checkpoint_remesh(*args, **kwargs):
        v, f = remesh(*args, **kwargs)
        save_tensors('remeshed-source.safetensors', {'vertices':v, 'faces':f})
        return v, f
    cumesh.remeshing.remesh_narrow_band_dc = checkpoint_remesh
    started = time.monotonic()
    glb = o_voxel.postprocess.to_glb(vertices=vertices, faces=faces,
        attr_volume=source['attrs'].cuda(), coords=source['coords'].cuda(),
        attr_layout={k:slice(*v) for k,v in info['layout'].items()}, voxel_size=1/1024,
        aabb=[[-.5]*3,[.5]*3], decimation_target=1000000, texture_size=4096,
        remesh=True, remesh_band=1, remesh_project=0, verbose=True)
    glb.export(FOLDER/'candidate.glb'); upload(FOLDER/'candidate.glb')
    memory('after-export')
    dump(FOLDER/'receipt.json', {'seed':298, 'pipeline_type':'1024_cascade', 'recovery':True,
        'latents_sha256':LATENT_SHA, 'source_sha256':info['source_sha256'],
        'glb_sha256':sha(FOLDER/'candidate.glb'), 'export_seconds':time.monotonic()-started,
        'decoder_pid':info['decoder_process'], 'exporter_pid':os.getpid(),
        'production_ready':False, 'actor_verdict':'NOT_RUN', 'bit_identical_to_unsaved301':'NOT_RUN'})
    upload(FOLDER/'receipt.json')


def infer():
    for stage in ('decode', 'export'):
        try:
            run([sys.executable, str(Path(__file__).resolve()), '--' + stage])
        except Exception as exc:
            dump(OUT/'recovery-failure.json', {'stage':stage, 'message':str(exc),
                'saved_files':sorted(p.name for p in FOLDER.iterdir()), 'quality_verdict':'NOT_RUN'})
            raise


if __name__ == '__main__':
    OUT.mkdir(exist_ok=True); FOLDER.mkdir(exist_ok=True)
    if '--preflight' in sys.argv: preflight()
    elif '--decode' in sys.argv: decode()
    elif '--export' in sys.argv: export()
    elif '--infer' in sys.argv: infer()
    else:
        original.__file__ = str(Path(__file__).resolve())
        original.setup()
