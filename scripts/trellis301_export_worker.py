"""Reviewed fixed-source export comparison; no inference/model/credential loading."""
import gc
import importlib
import importlib.metadata
import json
import os
from pathlib import Path
import sys
import time
import types

from trellis298_worker import BASE, OUT, run, dump, sha, RestrictedImports


def setup():
    from trellis294_runtime import link_parent_packages
    parent, vp = Path('/opt/pytorch/bin/python'), BASE / 'venv/bin/python'
    run([str(parent), '-m', 'venv', '--system-site-packages', str(BASE / 'venv')])
    dump(OUT / 'runtime-link.json', link_parent_packages(parent, vp, Path('/opt/pytorch'), BASE / 'venv'))
    run([str(vp), '-m', 'pip', 'install', '--only-binary=:all:', '--no-deps', '--report', str(OUT / 'pip-report.json'),
         'numpy==2.2.6', 'trimesh==4.7.4', 'opencv-python-headless==4.12.0.88', 'pillow==11.3.0',
         'tqdm==4.67.1', 'ninja==1.11.1.4', 'safetensors==0.6.2'])
    env = dict(os.environ, MAX_JOBS='2', TORCH_CUDA_ARCH_LIST='8.9', BUILD_TARGET='cuda',
               CUDA_HOME='/usr/local/cuda-12.8', PYTORCH_CUDA_ALLOC_CONF='expandable_segments:True',
               PYTHONPATH=str(BASE / 'src'), HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1')
    env['PATH'] = str(BASE / 'venv/bin') + ':/usr/local/cuda-12.8/bin:' + env['PATH']
    run([str(vp), '-c', 'import torch,numpy,trimesh,cv2,PIL,safetensors; assert torch.cuda.is_available(); print("EXPORT_IMPORT_PREFLIGHT_PASS")'], env=env)
    for name in ('CuMesh', 'FlexGEMM'):
        run([str(vp), '-m', 'pip', 'install', '--no-build-isolation', '--no-deps', str(BASE / 'sources' / name)], env=env)
    run([str(vp), str(BASE / 'scripts/trellis293_worker.py'), '--inventory'], env=env)
    run([str(vp), str(Path(__file__)), '--export'], env=env)


def export():
    names = {d.metadata['Name'].lower().replace('_', '-') for d in importlib.metadata.distributions()}
    assert not names & {'nvdiffrast', 'nvdiffrec', 'bria-rmbg', 'rembg', 'plyfile'}
    sys.meta_path.insert(0, RestrictedImports())
    import torch
    import cumesh
    from safetensors.torch import load_file, save_file
    from movie_factory.trellis_adapter.patch import adapted_sources
    from movie_factory.trellis301_quality import RAW_SHA, SHELL_SHA, split_exporter, array_digest
    assert torch.cuda.get_device_capability() == (8, 9)
    source, shell_path = BASE / 'input/source.safetensors', BASE / 'input/remeshed-source.safetensors'
    assert sha(source) == RAW_SHA and sha(shell_path) == SHELL_SHA
    patched = BASE / 'patched'
    for name, text in adapted_sources(BASE / 'results/sikh288/upstream').items():
        if name.endswith('/postprocess.py'):
            text = split_exporter(text)
        path = patched / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    package = types.ModuleType('mf_export301')
    package.__path__ = [str(patched / 'o-voxel/o_voxel')]
    sys.modules['mf_export301'] = package
    exporter = importlib.import_module('mf_export301.postprocess')
    tensors = load_file(str(source), device='cpu')
    shell = load_file(str(shell_path), device='cpu')
    geometry = json.loads((BASE / 'input/geometry.json').read_text())
    layout = {key: slice(*value) for key, value in geometry['layout'].items()}
    calls = []

    def preserved_shell(vertices, faces, **kwargs):
        # to_glb's original BVH still targets the original raw source. Only the
        # previously proved UDF reconstruction is reused, never reconstructed twice.
        assert kwargs['resolution'] == 512 and kwargs['band'] == 1 and kwargs['project_back'] == 0
        calls.append({'faces_in': len(faces), 'reused_faces': len(shell['faces']), 'new_remesh': False})
        return shell['vertices'].cuda().clone(), shell['faces'].cuda().clone()

    cumesh.remeshing.remesh_narrow_band_dc = preserved_shell
    variants = []
    for target, atlases in ((300000, (2048,)), (1000000, (2048, 4096))):
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()
        started = time.monotonic()
        surface = exporter.prepare_surface(vertices=tensors['vertices'].cuda(), faces=tensors['faces'].cuda(),
            attr_volume=tensors['attrs'].cuda(), coords=tensors['coords'].cuda(), attr_layout=layout,
            voxel_size=geometry['voxel_size'], aabb=[[-.5] * 3, [.5] * 3], decimation_target=target,
            texture_size=2048, remesh=True, remesh_band=1, remesh_project=0, verbose=True)
        torch.cuda.synchronize()
        preparation_seconds = time.monotonic() - started
        frozen = {k: surface[k].detach().cpu().contiguous() for k in ('out_vertices', 'out_faces', 'out_uvs', 'out_normals')}
        geometry_digest = array_digest({k: v.numpy() for k, v in frozen.items()})
        save_file(frozen, str(OUT / f'surface-{target}.safetensors'))
        del frozen
        for atlas in atlases:
            started = time.monotonic()
            glb = exporter.bake_surface(surface, atlas, verbose=True)
            glb_path = OUT / f'head-{target}-{atlas}.glb'
            glb.export(glb_path)
            torch.cuda.synchronize()
            after = array_digest({k: surface[k].detach().cpu().numpy() for k in ('out_vertices', 'out_faces', 'out_uvs', 'out_normals')})
            assert after == geometry_digest, 'Baking mutated fixed geometry/UVs'
            record = dict(target_faces=target, texture_size=atlas, source_sha256=RAW_SHA, shell_sha256=SHELL_SHA,
                geometry_uv_sha256=geometry_digest, actual_faces=len(glb.faces), actual_vertices=len(glb.vertices),
                glb_sha256=sha(glb_path), prepare_seconds=preparation_seconds, bake_seconds=time.monotonic()-started,
                pytorch_peak_allocated_bytes=torch.cuda.max_memory_allocated(), total_gpu_peak_bytes=None,
                alpha_mode=glb.visual.material.alphaMode, new_generation=False, new_remesh=False, production_ready=False)
            dump(OUT / f'head-{target}-{atlas}.json', record)
            variants.append(record)
            del glb
        del surface
        gc.collect()
        torch.cuda.empty_cache()
    assert len(calls) == 2
    assert variants[1]['geometry_uv_sha256'] == variants[2]['geometry_uv_sha256']
    dump(OUT / 'comparison-receipt.json', {'variants': variants, 'shell_reuse_calls': calls,
        'quality_verdict': 'NOT_RUN', 'actor_verdict': 'NOT_RUN',
        'memory_limit': 'CuMesh/CUDA native allocations are not fully represented by PyTorch peak'})
    assert not any(n.split('.')[0] in {'nvdiffrast', 'nvdiffrec', 'rembg', 'plyfile'} for n in sys.modules)
    dump(OUT / 'loaded-modules.json', sorted(sys.modules))


if __name__ == '__main__':
    OUT.mkdir(exist_ok=True)
    export() if '--export' in sys.argv else setup()
