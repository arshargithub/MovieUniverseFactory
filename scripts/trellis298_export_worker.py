"""Fixed export-only reconstruction of already generated source. No inference."""
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
    parent = Path('/opt/pytorch/bin/python')
    vp = BASE / 'venv/bin/python'
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
    assert not names & {'nvdiffrast', 'nvdiffrec', 'bria-rmbg', 'rembg'}
    sys.meta_path.insert(0, RestrictedImports())
    import torch
    import cumesh
    from safetensors.torch import load_file, save_file
    from movie_factory.trellis_adapter.patch import adapted_sources
    assert torch.cuda.get_device_capability() == (8, 9)
    source = BASE / 'input/source.safetensors'
    assert sha(source) == 'bdd085b6b86ad2dd731beda22cb9b1f03fd6b3da961bf6d72a91e792d9a8b6ff'
    patch = BASE / 'patched'
    for name, text in adapted_sources(BASE / 'results/sikh288/upstream').items():
        path = patch / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    package = types.ModuleType('mf_export298')
    package.__path__ = [str(patch / 'o-voxel/o_voxel')]
    sys.modules['mf_export298'] = package
    exporter = importlib.import_module('mf_export298.postprocess')
    # Open sheet is the relevant discriminator; closed cube is insufficient.
    v = torch.tensor([[-.2+.4*x/3,-.2+.4*y/3,0] for y in range(4) for x in range(4)], device='cuda')
    f = torch.tensor([[y*4+x,y*4+x+1,(y+1)*4+x+1] for y in range(3) for x in range(3)] +
                     [[y*4+x,(y+1)*4+x+1,(y+1)*4+x] for y in range(3) for x in range(3)], dtype=torch.int32, device='cuda')
    assert len(f) > 8  # cuBVH constructor requires more than eight triangles.
    sheet = cumesh.remeshing.remesh_narrow_band_dc(v, f, center=torch.zeros(3,device='cuda'),
        scale=35/32, resolution=32, band=1, project_back=0, verbose=True, bvh=cumesh.cuBVH(v,f))
    assert len(sheet[0]) and len(sheet[1]) and torch.isfinite(sheet[0]).all()
    sv, sf = sheet
    assert sf.min() >= 0 and sf.max() < len(sv)
    triangles = sv[sf.long()]
    assert (torch.linalg.vector_norm(torch.cross(triangles[:,1]-triangles[:,0], triangles[:,2]-triangles[:,0], dim=1),dim=1) > 1e-10).all()
    directed = torch.cat((sf[:,[0,1]], sf[:,[1,2]], sf[:,[2,0]]))
    edges = directed.sort(dim=1).values
    _, inverse, counts = torch.unique(edges, dim=0, return_inverse=True, return_counts=True)
    assert (counts == 2).all(), 'Open-sheet reconstruction is not a closed shell'
    signs = torch.where(directed[:,0] < directed[:,1], 1, -1)
    orientation = torch.zeros(len(counts), dtype=signs.dtype, device=signs.device)
    orientation.scatter_add_(0,inverse,signs)
    assert (orientation == 0).all(), 'Shell winding is inconsistent'
    thickness = float(sv[:,2].max()-sv[:,2].min())
    expected_thickness = 2*(35/32)/32
    assert .5*expected_thickness < thickness < 1.5*expected_thickness
    save_file({'vertices':sheet[0].cpu().contiguous(),'faces':sheet[1].cpu().contiguous()}, str(OUT/'open-sheet.safetensors'))
    dump(OUT/'open-sheet.json', {'vertices':len(sheet[0]),'faces':len(sheet[1]),'closed_edge_incidence':True,
        'thickness':thickness,'expected_thickness':expected_thickness,'status':'TECHNICAL_PASS_NOT_VISUAL'})
    del sheet, v, f
    torch.cuda.empty_cache()
    tensors = load_file(str(source), device='cpu')
    geometry = json.loads((BASE/'input/geometry.json').read_text())
    layout = {k:slice(*value) for k,value in geometry['layout'].items()}
    original = cumesh.remeshing.remesh_narrow_band_dc
    def captured(*args, **kwargs):
        result = original(*args, **kwargs)
        save_file({'vertices':result[0].cpu().contiguous(),'faces':result[1].cpu().contiguous()}, str(OUT/'remeshed-source.safetensors'))
        dump(OUT/'remeshed-source.json', {'vertices':len(result[0]), 'faces':len(result[1]),
            'sha256':sha(OUT/'remeshed-source.safetensors')})
        return result
    cumesh.remeshing.remesh_narrow_band_dc = captured
    torch.cuda.reset_peak_memory_stats()
    start = time.monotonic()
    mesh = exporter.to_glb(vertices=tensors['vertices'].cuda(), faces=tensors['faces'].cuda(),
        attr_volume=tensors['attrs'].cuda(), coords=tensors['coords'].cuda(), attr_layout=layout,
        voxel_size=geometry['voxel_size'], aabb=[[-.5]*3,[.5]*3], decimation_target=300000,
        texture_size=2048, remesh=True, remesh_band=1, remesh_project=0, verbose=True)
    mesh.export(OUT/'candidate.glb')
    torch.cuda.synchronize()
    dump(OUT/'receipt.json', {'source_sha256':sha(source),'glb_sha256':sha(OUT/'candidate.glb'),
        'export_seconds':time.monotonic()-start,'remesh':True,'remesh_project':0,'remesh_band':1,
        'pytorch_peak_allocated_bytes':torch.cuda.max_memory_allocated(),'pytorch_peak_reserved_bytes':torch.cuda.max_memory_reserved(),
        'total_gpu_peak_bytes':None,'memory_limit':'CuMesh BVH allocations are outside the PyTorch allocator',
        'new_generation':False,'production_ready':False})
    assert not any(n.split('.')[0] in {'nvdiffrast','nvdiffrec','rembg','plyfile'} for n in sys.modules)
    dump(OUT/'loaded-modules.json', sorted(sys.modules))
    print('EXPORT_ONLY_COMPLETE', flush=True)


if __name__ == '__main__':
    OUT.mkdir(exist_ok=True)
    export() if '--export' in sys.argv else setup()
