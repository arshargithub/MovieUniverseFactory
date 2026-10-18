"""Contingent301 capacity test; preparation only until separately admitted by root.

Same298 input, seed, default samplers, pinned runtime/model and unsigned exporter.
No512 warm-up. Save and privately upload sampled latents before any1024 decode.
"""
import gc
import importlib.metadata
import json
import os
from pathlib import Path
import sys
import time

import trellis298_worker as original
from trellis298_worker import BASE, OUT, REV, SS_REV, dump, sha, run, RestrictedImports

INPUT_SHA = '7f74def2304b885d029c8cf427f027e88f6b2ca0fbc5c5067a8674ebb7e99008'
CONFIG_SHA = '222c359ab1ed9bc6735a640a34f95d47f8681b9bc4aaa101bfb80274676253c6'
BUCKET = 'mf-trellis301-1024-281482331395'


def install_decode_checkpoint(pipeline, save_tensors, upload):
    """Instance-local wrapper; arguments passed unchanged to official decode.

    Saving plain CPU tensors avoids pickle; cloning separates shared coordinate
    storage. Metadata preserves constructor shape/scale. Sparse caches are not
    serialized; decode-rescue equivalence must be tested before claiming rescue.
    """
    decode = pipeline.decode_latent
    calls = []

    def checkpointed(shape_slat, tex_slat, resolution):
        if calls or resolution != 1024:
            raise RuntimeError('Unexpected decode count/resolution')
        calls.append(resolution)
        target = OUT / 'predecode'
        target.mkdir(parents=True, exist_ok=True)
        tensors, metadata = {}, {}
        for label, latent in (('shape', shape_slat), ('texture', tex_slat)):
            for attr in ('feats', 'coords'):
                tensors[f'{label}_{attr}'] = getattr(latent, attr).detach().cpu().contiguous().clone()
            metadata[label] = {'shape': list(latent.shape),
                'scale': [[v.numerator, v.denominator] for v in latent._scale],
                'features_dtype': str(latent.feats.dtype), 'coordinates_dtype': str(latent.coords.dtype)}
        tensor_path = target / 'latents.safetensors'
        save_tensors(tensors, str(tensor_path))
        del tensors
        metadata.update(resolution=resolution, seed=298, pipeline_type='1024_cascade',
            denormalized_for_decoder=True, input_sha256=INPUT_SHA, core_revision=REV,
            pipeline_config_sha256=CONFIG_SHA, latents_sha256=sha(tensor_path),
            sparse_caches_saved=False, decode_rescue_validation='NOT_RUN')
        dump(target / 'latents.json', metadata)
        # Fail before the expensive decode if durable checkpoint delivery fails.
        upload(tensor_path, 'output/predecode/latents.safetensors')
        upload(target / 'latents.json', 'output/predecode/latents.json')
        dump(target / 'upload.json', {'uploaded': True, 'sha256': metadata['latents_sha256'],
            'destination': BUCKET, 'public': False})
        gc.collect()
        return decode(shape_slat, tex_slat, resolution)

    pipeline.decode_latent = checkpointed
    return calls


def private_upload(path, key):
    if not key.startswith('output/predecode/'):
        raise ValueError('Unreviewed checkpoint destination')
    run(['aws', 's3', 'cp', str(path), f's3://{BUCKET}/{key}', '--only-show-errors', '--region', 'us-east-1'])


def infer():
    names = {d.metadata['Name'].lower().replace('_', '-') for d in importlib.metadata.distributions()}
    assert not names & {'nvdiffrast', 'nvdiffrec', 'bria-rmbg', 'rembg', 'plyfile'}
    sys.meta_path.insert(0, RestrictedImports())
    from huggingface_hub import hf_hub_download
    from PIL import Image
    import torch
    from safetensors.torch import save_file
    assert torch.cuda.get_device_capability() == (8, 9)
    device = torch.cuda.get_device_properties(0)
    assert device.total_memory >= 44 * 1024**3, '48GB class test requires >=44GiB exposed memory'
    assert sha(BASE / 'input/head.png') == INPUT_SHA
    weights = BASE / 'weights'
    weights.mkdir(exist_ok=True)
    config_path = Path(hf_hub_download('microsoft/TRELLIS.2-4B', 'pipeline.json', revision=REV, token=False))
    assert sha(config_path) == CONFIG_SHA
    config = json.loads(config_path.read_text())
    manifest = {'core_revision': REV, 'sparse_decoder_revision': SS_REV,
        'files': {'pipeline.json': CONFIG_SHA}, 'sampler_overrides': {}, 'input_sha256': INPUT_SHA}
    for key, value in config['args']['models'].items():
        remote = value.startswith('microsoft/TRELLIS-image-large/')
        repo = 'microsoft/TRELLIS-image-large' if remote else 'microsoft/TRELLIS.2-4B'
        filename = value.removeprefix('microsoft/TRELLIS-image-large/')
        revision = SS_REV if remote else REV
        for ext in ('.json', '.safetensors'):
            path = Path(hf_hub_download(repo, filename + ext, revision=revision, token=False))
            manifest['files'][repo + '/' + filename + ext] = {'sha256': sha(path), 'bytes': path.stat().st_size}
            (weights / (key + ext)).symlink_to(path)
        config['args']['models'][key] = str(weights / key)
    config['args']['image_cond_model']['args']['model_name'] = str(BASE / 'encoder')
    config['args']['low_vram'] = True
    config['args'].pop('rembg_model', None)
    dump(weights / 'pipeline.json', config)
    dump(OUT / 'weight-manifest.json', manifest)
    os.environ['HF_HUB_OFFLINE'] = os.environ['TRANSFORMERS_OFFLINE'] = '1'
    from trellis2.pipelines import Trellis2ImageTo3DPipeline
    import o_voxel
    import cumesh
    start = time.monotonic()
    pipeline = Trellis2ImageTo3DPipeline.from_pretrained(str(weights))
    pipeline.cuda()
    dump(OUT / 'load.json', {'seconds': time.monotonic()-start, 'device': device.name,
        'device_total_bytes': device.total_memory, 'adequacy': 'UNPROVEN until decode completes'})
    calls = install_decode_checkpoint(pipeline, save_file, private_upload)
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    folder = OUT / 'head1024'
    folder.mkdir()
    start = time.monotonic()
    try:
        outputs = pipeline.run(Image.open(BASE / 'input/head.png'), seed=298,
            pipeline_type='1024_cascade', return_latent=False)
    except Exception as exc:
        dump(OUT / 'generation-failure.json', {'type': type(exc).__name__, 'message': str(exc),
            'seconds': time.monotonic()-start, 'predecode_checkpoint_count': len(calls),
            'pytorch_peak_allocated_bytes': torch.cuda.max_memory_allocated(),
            'quality_verdict': 'NOT_RUN', 'actor_verdict': 'NOT_RUN'})
        raise
    assert calls == [1024]
    mesh = outputs[0]
    torch.cuda.synchronize()
    generated = time.monotonic()
    save_file({'vertices': mesh.vertices.contiguous().cpu(), 'faces': mesh.faces.contiguous().cpu(),
        'attrs': mesh.attrs.contiguous().cpu(), 'coords': mesh.coords.contiguous().cpu()}, str(folder / 'source.safetensors'))
    dump(folder / 'geometry.json', {'voxel_size': mesh.voxel_size,
        'layout': {k: [v.start, v.stop] for k, v in mesh.layout.items()},
        'vertices': len(mesh.vertices), 'faces': len(mesh.faces)})
    # Free all inference models before the independent conversion stage.
    del outputs, pipeline
    gc.collect()
    torch.cuda.empty_cache()
    original_remesh = cumesh.remeshing.remesh_narrow_band_dc

    def save_remesh(*args, **kwargs):
        vertices, faces = original_remesh(*args, **kwargs)
        save_file({'vertices': vertices.detach().contiguous().cpu(), 'faces': faces.detach().contiguous().cpu()},
            str(folder / 'remeshed-source.safetensors'))
        return vertices, faces

    cumesh.remeshing.remesh_narrow_band_dc = save_remesh
    glb = o_voxel.postprocess.to_glb(vertices=mesh.vertices, faces=mesh.faces,
        attr_volume=mesh.attrs, coords=mesh.coords, attr_layout=mesh.layout, voxel_size=mesh.voxel_size,
        aabb=[[-.5]*3, [.5]*3], decimation_target=1000000, texture_size=4096,
        remesh=True, remesh_band=1, remesh_project=0, verbose=True)
    glb.export(folder / 'candidate.glb')
    dump(folder / 'receipt.json', {'seed': 298, 'pipeline_type': '1024_cascade',
        'sampler_overrides': {}, 'generation_seconds': generated-start,
        'export_seconds': time.monotonic()-generated, 'pytorch_peak_allocated_bytes': torch.cuda.max_memory_allocated(),
        'total_gpu_peak_bytes': None, 'glb_sha256': sha(folder / 'candidate.glb'),
        'input_sha256': INPUT_SHA, 'production_ready': False, 'actor_verdict': 'NOT_RUN'})
    dump(OUT / 'loaded-modules.json', sorted(sys.modules))


if __name__ == '__main__':
    OUT.mkdir(exist_ok=True)
    if '--preflight' in sys.argv:
        original.preflight()
    elif '--infer' in sys.argv:
        infer()
    else:
        # Reuse the exact admitted installer; only its subprocess entrypoint changes.
        original.__file__ = str(Path(__file__).resolve())
        original.setup()
