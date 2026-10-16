"""Analytic bake-to-GLB control; deliberately not the full CUDA exporter."""
import torch
import numpy as np
from .uvraster import rasterize_uv
from .material import finish_glb


def build_fixture(size=64, device='cpu'):
    uvs = torch.tensor([[0.,0.],[1.,0.],[1.,1.],[0.,1.]], device=device)
    vertices = torch.tensor([[0.,0.,.2],[1.,0.,.5],[1.,1.,.6],[0.,1.,.3]], device=device)
    faces = torch.tensor([[0,1,2],[0,2,3]], device=device)
    normal = torch.tensor([-.3,-.1,1.], device=device)
    normals = (normal/normal.norm()).expand(4,-1).clone()
    stats = {}
    mask, ids, bary = rasterize_uv(uvs, faces, size, 4096, stats=stats)
    pos = (vertices[faces[ids[mask]]]*bary[mask].unsqueeze(-1)).sum(1)
    yy,xx = np.mgrid[:size,:size]
    expected = np.stack([(xx+.5)/size,(yy+.5)/size,.2+.3*(xx+.5)/size+.1*(yy+.5)/size],-1)
    np.testing.assert_allclose(pos.cpu().numpy(), expected.reshape(-1,3), atol=2e-6)
    attrs = torch.zeros((size,size,6), device=device)
    # Analytic position-to-material field substitutes only for the learned volume.
    attrs[...,0][mask] = (pos[:,0] > .5).float()
    attrs[...,1][mask] = (pos[:,1] > .5).float()
    attrs[...,2][mask] = .2
    attrs[...,3][mask] = .75*(pos[:,0] > .5).float()
    attrs[...,4][mask] = .2+.6*(pos[:,1] > .5).float()
    attrs[...,5][mask] = 1.
    layout = dict(base_color=slice(0,3),metallic=slice(3,4),roughness=slice(4,5),alpha=slice(5,6))
    inputs = [v.clone() for v in [vertices,faces,uvs,normals]]
    mesh = finish_glb(vertices,faces,uvs,normals,attrs,mask,layout)
    assert all(torch.equal(a,b) for a,b in zip(inputs,[vertices,faces,uvs,normals]))
    return mesh, {'device':device, 'size':size,'coverage':int(mask.sum()),'raster':stats,
                  'position_error_max':float(np.abs(pos.cpu().numpy()-expected.reshape(-1,3)).max()),
                  'scope':'Raster + analytic material field + shared upstream PBR finish. NOT full CuMesh/BVH/FlexGEMM/inference.'}
