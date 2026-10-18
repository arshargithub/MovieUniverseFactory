"""Fixed isolated inference worker: pinned official weights, no credential input."""
import hashlib
import importlib.abc
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys
import time

BASE = Path('/opt/mf-trellis293')
OUT = BASE / 'evidence'
SOURCE = BASE / 'inference'
REV = 'af44b45f2e35a493886929c6d786e563ec68364d'
SS_REV = '25e0d31ffbebe4b5a97464dd851910efc3002d96'


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2))


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def run(command, **kw):
    print('RUN', command, flush=True)
    return subprocess.run(command, check=True, **kw)


def setup():
    from trellis294_runtime import link_parent_packages
    parent = Path('/opt/pytorch/bin/python')
    vp = BASE / 'venv/bin/python'
    run([str(parent), '-m', 'venv', '--system-site-packages', str(BASE / 'venv')])
    dump(OUT / 'runtime-link.json', link_parent_packages(parent, vp, Path('/opt/pytorch'), BASE / 'venv'))
    run([str(vp), '-c', 'import torch; assert torch.cuda.is_available(); print(torch.__version__,torch.cuda.get_device_name())'])
    run([str(vp), '-m', 'pip', 'install', '--only-binary=:all:', '--no-deps', '--report', str(OUT / 'pip-report.json'),
         'numpy==2.2.6', 'trimesh==4.7.4', 'opencv-python-headless==4.12.0.88', 'pillow==11.3.0',
         'tqdm==4.67.1', 'ninja==1.11.1.4', 'transformers==4.56.2', 'huggingface-hub==0.34.4',
         'safetensors==0.6.2', 'tokenizers==0.22.0', 'easydict==1.13', 'zstandard==0.24.0', 'regex==2025.9.18'])
    run([str(vp), '-m', 'pip', 'install', '--no-deps', '--report', str(OUT / 'attention-install.json'),
         'https://download.pytorch.org/whl/cu128/xformers-0.0.30-cp312-cp312-manylinux_2_28_x86_64.whl#sha256=e2602a3f36c1d5c3aec7dc9f79050e3db5c1e94fc11ad929afbdb409c6d611d5'])
    env = dict(os.environ, MAX_JOBS='2', TORCH_CUDA_ARCH_LIST='8.9', BUILD_TARGET='cuda',
               CUDA_HOME='/usr/local/cuda-12.8', ATTN_BACKEND='xformers', SPARSE_ATTN_BACKEND='xformers',
               PYTORCH_CUDA_ALLOC_CONF='expandable_segments:True', HF_HUB_DISABLE_TELEMETRY='1')
    env['PATH'] = str(BASE / 'venv/bin') + ':/usr/local/cuda-12.8/bin:' + env['PATH']
    env['PYTHONPATH'] = str(SOURCE) + ':' + str(BASE / 'src')
    # Prove new inference imports before expensive native compilation.
    run([str(vp), '-c', 'from transformers import DINOv3ViTModel; import regex,einops,easydict,zstandard,cv2,xformers.ops; print("INFERENCE_IMPORT_PREFLIGHT_PASS")'], env=env)
    for directory in (BASE / 'sources/CuMesh', BASE / 'sources/FlexGEMM', SOURCE / 'o-voxel'):
        run([str(vp), '-m', 'pip', 'install', '--no-build-isolation', '--no-deps', str(directory)], env=env)
    run([str(vp), str(BASE / 'scripts/trellis293_worker.py'), '--inventory'], env=env)
    run([str(vp), str(Path(__file__)), '--preflight'], env=env)
    run([str(vp), str(Path(__file__)), '--infer'], env=env)


class RestrictedImports(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if any(s in fullname.lower() for s in ('nvdiffrast', 'nvdiffrec', 'renderutils', 'rembg', 'bria')):
            raise ImportError('Restricted component blocked: ' + fullname)
        return None


def preflight():
    """Exercise the admitted inference import closure before multi-GB downloads."""
    sys.meta_path.insert(0, RestrictedImports())
    import torch
    import o_voxel
    import xformers.ops as xops
    from trellis2.pipelines import Trellis2ImageTo3DPipeline
    from trellis2 import models
    from trellis2.modules.sparse import SparseTensor, SparseConv3d
    from trellis2.modules.image_feature_extractor import DinoV3FeatureExtractor
    # Resolve every lazy model class that the pinned pipeline can instantiate.
    for name in models.__all__:
        getattr(models, name)
    q = torch.randn(1, 8, 2, 32, device='cuda', dtype=torch.float16)
    assert torch.isfinite(xops.memory_efficient_attention(q, q, q)).all()
    sparse = SparseTensor.full([0, 0, 0, 2, 2, 2], (1, 16), 1.,
                               dtype=torch.float16, device='cuda')
    conv = SparseConv3d(16, 16, 3).cuda().half()
    with torch.no_grad():
        result = conv(sparse)
    assert torch.isfinite(result.feats).all()
    assert hasattr(o_voxel.postprocess, 'to_glb')
    assert not any(n.startswith('plyfile') for n in sys.modules)
    torch.cuda.synchronize()
    dump(OUT / 'inference-preflight.json', {'status': 'PASS', 'models': models.__all__,
         'attention': 'xformers', 'convolution': 'flex_gemm', 'modules': sorted(sys.modules),
         'limits': 'Small kernel and complete lazy-class imports; not model inference or visual qualification'})
    print('FULL_INFERENCE_PREFLIGHT_PASS', flush=True)


def infer():
    names = {d.metadata['Name'].lower().replace('_', '-') for d in importlib.metadata.distributions()}
    assert not names & {'nvdiffrast', 'nvdiffrec', 'bria-rmbg', 'rembg'}
    sys.meta_path.insert(0, RestrictedImports())
    from huggingface_hub import hf_hub_download
    from PIL import Image
    import torch
    import numpy as np
    from safetensors.torch import save_file
    assert torch.cuda.get_device_capability() == (8, 9)
    weights = BASE / 'weights'
    weights.mkdir(exist_ok=True)
    config_path = hf_hub_download('microsoft/TRELLIS.2-4B', 'pipeline.json', revision=REV, token=False)
    config = json.loads(Path(config_path).read_text())
    manifest = {'core_revision': REV, 'sparse_decoder_revision': SS_REV, 'files': {}}
    manifest['files']['pipeline.json'] = sha(Path(config_path))
    for key, value in config['args']['models'].items():
        remote = value.startswith('microsoft/TRELLIS-image-large/')
        repo = 'microsoft/TRELLIS-image-large' if remote else 'microsoft/TRELLIS.2-4B'
        filename = value.removeprefix('microsoft/TRELLIS-image-large/')
        revision = SS_REV if remote else REV
        for ext in ('.json', '.safetensors'):
            path = Path(hf_hub_download(repo, filename + ext, revision=revision, token=False))
            manifest['files'][repo + '/' + filename + ext] = {'sha256': sha(path), 'bytes': path.stat().st_size}
            # Local paths ensure no unpinned loader fallback is used.
            destination = weights / (key + ext)
            destination.symlink_to(path)
        config['args']['models'][key] = str(weights / key)
    config['args']['image_cond_model']['args']['model_name'] = str(BASE / 'encoder')
    config['args']['low_vram'] = True
    config['args'].pop('rembg_model', None)
    dump(weights / 'pipeline.json', config)
    dump(OUT / 'weight-manifest.json', manifest)
    # All required models now local; fail closed on unexpected model fetch.
    os.environ['HF_HUB_OFFLINE'] = '1'
    os.environ['TRANSFORMERS_OFFLINE'] = '1'
    from trellis2.pipelines import Trellis2ImageTo3DPipeline
    import o_voxel
    start = time.monotonic()
    pipeline = Trellis2ImageTo3DPipeline.from_pretrained(str(weights))
    pipeline.cuda()
    dump(OUT / 'load.json', {'seconds': time.monotonic() - start, 'device': torch.cuda.get_device_name()})
    image = Image.open(BASE / 'input/head.png')
    for label, kind, texture_size in [('head512', '512', 2048), ('head1024', '1024_cascade', 4096)]:
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()
        start = time.monotonic()
        outputs, latent = pipeline.run(image, seed=298, pipeline_type=kind, return_latent=True)
        mesh = outputs[0]
        torch.cuda.synchronize()
        generated = time.monotonic()
        folder = OUT / label
        folder.mkdir()
        # Generated tensor data only; no pickle or executable checkpoints.
        save_file({'vertices': mesh.vertices.contiguous().cpu(), 'faces': mesh.faces.contiguous().cpu(),
                   'attrs': mesh.attrs.contiguous().cpu(), 'coords': mesh.coords.contiguous().cpu()}, str(folder / 'source.safetensors'))
        dump(folder / 'geometry.json', {'voxel_size': mesh.voxel_size, 'layout': {k: [v.start, v.stop] for k, v in mesh.layout.items()},
                                      'vertices': len(mesh.vertices), 'faces': len(mesh.faces)})
        glb = o_voxel.postprocess.to_glb(vertices=mesh.vertices, faces=mesh.faces, attr_volume=mesh.attrs,
             coords=mesh.coords, attr_layout=mesh.layout, voxel_size=mesh.voxel_size,
             aabb=[[-.5]*3,[.5]*3], decimation_target=300000, texture_size=texture_size,
             remesh=False, verbose=True)
        glb.export(folder / 'candidate.glb')
        dump(folder / 'receipt.json', {'seed': 298, 'pipeline_type': kind, 'generation_seconds': generated-start,
             'export_seconds': time.monotonic()-generated, 'peak_allocated_bytes': torch.cuda.max_memory_allocated(),
             'peak_reserved_bytes': torch.cuda.max_memory_reserved(), 'glb_sha256': sha(folder / 'candidate.glb'),
             'input_sha256': sha(BASE / 'input/head.png'), 'production_ready': False})
        print('CANDIDATE_EXPORTED', label, flush=True)
        del outputs, latent, mesh, glb
    dump(OUT / 'loaded-modules.json', sorted(sys.modules))


if __name__ == '__main__':
    OUT.mkdir(exist_ok=True)
    preflight() if '--preflight' in sys.argv else infer() if '--infer' in sys.argv else setup()
