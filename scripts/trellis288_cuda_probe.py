"""Synthetic CUDA exporter probe for an isolated, patched TRELLIS checkout.

Run only after budget, isolated runtime inventory and shutdown admission.
No model weights, images, network, provider keys, AWS API or protagonist assets.
The export subpackage deliberately omits unrelated inference/preview imports.
"""
import argparse
import hashlib
import importlib
import importlib.abc
import importlib.metadata
import json
from pathlib import Path
import sys
import time
import types


class RestrictedImports(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if any(x in fullname.lower() for x in ('nvdiffrast','nvdiffrec','renderutils','rembg','bria')):
            raise ImportError('Restricted component blocked: '+fullname)
        return None


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--checkout',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists(): raise ValueError('Use a new evidence directory')
    prohibited={'nvdiffrast','nvdiffrec','bria-rmbg','rembg'}
    names={d.metadata['Name'].lower().replace('_','-') for d in importlib.metadata.distributions()}
    if names & prohibited: raise RuntimeError('Prohibited installed distribution')
    if any(any(x in n for x in prohibited) for n in sys.modules): raise RuntimeError('Prohibited preloaded module')
    sys.meta_path.insert(0,RestrictedImports())
    from movie_factory.trellis_adapter.patch import adapted_sources
    root=Path(__file__).resolve().parents[1]
    expected=adapted_sources(root/'results/sikh288/upstream')
    for name,source in expected.items():
        if (args.checkout/name).read_text()!=source: raise RuntimeError('Adapter drift: '+name)
    # Load the reviewed export package only; never upstream setup/preview/model code.
    package=types.ModuleType('mf_export288')
    package.__path__=[str(args.checkout/'o-voxel/o_voxel')]
    sys.modules['mf_export288']=package
    import torch
    import trimesh
    import numpy as np
    if not torch.cuda.is_available(): raise RuntimeError('CUDA required; no silent CPU fallback')
    exporter=importlib.import_module('mf_export288.postprocess')
    from movie_factory.trellis_adapter.fixture import build_fixture
    args.output.mkdir(parents=True)
    torch.cuda.reset_peak_memory_stats()
    start=time.monotonic()
    # Analytic UV/axis control using same rasterizer and finishing path on GPU.
    mesh, raster_receipt=build_fixture(device='cuda')
    mesh.export(args.output/'uv-control.glb')
    vertices=torch.tensor([[-.25,-.25,-.25],[.25,-.25,-.25],[.25,.25,-.25],[-.25,.25,-.25],
                           [-.25,-.25,.25],[.25,-.25,.25],[.25,.25,.25],[-.25,.25,.25]],device='cuda')
    faces=torch.tensor([[0,2,1],[0,3,2],[4,5,6],[4,6,7],[0,1,5],[0,5,4],
                        [1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7]],dtype=torch.int32,device='cuda')
    coords=torch.cartesian_prod(*[torch.arange(16,device='cuda',dtype=torch.int32)]*3)
    attrs=torch.tensor([.2,.4,.7,.1,.65,1.],device='cuda').repeat(len(coords),1)
    layout=dict(base_color=slice(0,3),metallic=slice(3,4),roughness=slice(4,5),alpha=slice(5,6))
    mesh=exporter.to_glb(vertices,faces,attrs,coords,layout,[[-.5]*3,[.5]*3],grid_size=16,
                         decimation_target=1000,texture_size=128,remesh=False)
    torch.cuda.synchronize()
    mesh.export(args.output/'cube.glb')
    restored=trimesh.load(args.output/'cube.glb',force='scene',process=False)
    obj=next(iter(restored.geometry.values()))
    if not np.isfinite(obj.vertices).all() or len(obj.faces)==0: raise RuntimeError('Invalid exported geometry')
    if not np.allclose(obj.bounds,[[-.25]*3,[.25]*3],atol=.01): raise RuntimeError('Geometry bounds changed')
    colors=np.asarray(obj.visual.material.baseColorTexture)
    mr=np.asarray(obj.visual.material.metallicRoughnessTexture)
    # Constant volume tests bake and gap fill independent of chart packing.
    if np.max(np.abs(colors[...,:3].astype(int)-np.array([51,102,178])))>3: raise RuntimeError('Base color bake failed')
    if np.max(np.abs(mr.astype(int)-np.array([0,165,25])))>3: raise RuntimeError('Material channels failed')
    result={'scope':'CuMesh unwrap/BVH + FlexGEMM analytic sparse volume + patched raster + PBR/GLB. No inference.',
            'seconds':time.monotonic()-start,'device':torch.cuda.get_device_name(),
            'peak_allocated_bytes':torch.cuda.max_memory_allocated(),
            'peak_reserved_bytes':torch.cuda.max_memory_reserved(),
            'torch':torch.__version__,'cuda':torch.version.cuda,'raster_control':raster_receipt,
            'vertices':len(obj.vertices),'faces':len(obj.faces),
            'packages':sorted(names),'outputs':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in args.output.glob('*.glb')}}
    (args.output/'receipt.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))


if __name__=='__main__': main()
