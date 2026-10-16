"""Synthetic adapter checks; no inference, network or cloud spending."""
import ast
from pathlib import Path
import numpy as np
from PIL import Image
import pytest
from movie_factory.trellis_adapter.admission import prepare_rgba
from movie_factory.trellis_adapter.patch import adapted_sources, unified_patch

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('mode,value', [('RGB', 255), ('RGBA', 255), ('RGBA', 0), ('RGBA', 150)])
def test_bad_mask(mode, value):
    with pytest.raises(ValueError):
        prepare_rgba(Image.new(mode, (8, 8), tuple([value]*len(mode))))


def test_alpha_foreground_and_inclusive_bounds():
    arr = np.zeros((8, 8, 4), np.uint8)
    arr[2:6, 1:5] = [230, 120, 12, 255]
    out = prepare_rgba(Image.fromarray(arr))
    assert out.size == (4, 4)
    assert np.all(np.array(out) == [230, 120, 12])
    arr[:] = 0
    arr[3, 3] = [255, 0, 0, 255]
    assert prepare_rgba(Image.fromarray(arr)).size == (1, 1)


def test_pinned_patch_excludes_restricted_paths():
    sources = adapted_sources(ROOT/'results/sikh288/upstream')
    for source in sources.values():
        ast.parse(source)
        assert 'import nvdiffrast' not in source
        assert 'getattr(rembg' not in source
    pipe = sources['trellis2/pipelines/trellis2_image_to_3d.py']
    assert 'pipeline.rembg_model = None' in pipe
    assert 'Prepared-alpha admission cannot be bypassed' in pipe
    assert 'rasterize_uv(out_uvs, out_faces, texture_size)' in sources['o-voxel/o_voxel/postprocess.py']
    assert '+++ b/o-voxel/o_voxel/_mf_uvraster.py' in unified_patch(ROOT/'results/sikh288/upstream')


def test_upstream_drift_blocks(tmp_path):
    for name in ('postprocess.py', 'trellis2_image_to_3d.py'):
        (tmp_path/name).write_bytes((ROOT/'results/sikh288/upstream'/name).read_bytes()+b'\n')
    with pytest.raises(ValueError, match='drift'):
        adapted_sources(tmp_path)


def torch_api():
    torch = pytest.importorskip('torch', reason='Opt-in isolated TRELLIS test dependencies')
    from movie_factory.trellis_adapter.uvraster import rasterize_uv
    torch.set_num_threads(2)
    return torch, rasterize_uv


@pytest.mark.parametrize('budget', [1, 19, 1024])
@pytest.mark.parametrize('reverse', [False, True])
def test_square_shared_edge_barycentric_pairing(budget, reverse):
    torch, raster = torch_api()
    uv = torch.tensor([[0.,0.],[1.,0.],[1.,1.],[0.,1.]])
    faces = torch.tensor([[0,1,2],[0,2,3]])
    if reverse:
        faces = faces.flip(1)
    stats = {}
    mask, tri, bary = raster(uv, faces, 16, budget, stats=stats)
    xy = (uv[faces[tri[mask]]]*bary[mask].unsqueeze(-1)).sum(1).numpy()
    yy, xx = np.mgrid[:16,:16]
    assert mask.all()
    np.testing.assert_allclose(xy, np.stack([xx+.5, yy+.5], -1).reshape(-1,2)/16, atol=2e-6)
    assert stats['peak_candidates'] <= budget
    assert stats['total_candidates'] == 512


def test_mixed_aspect_and_oversize_budget():
    torch, raster = torch_api()
    # Hundred very wide and very tall triangles: shared rectangle exaggerates work.
    uv = torch.tensor([[0.,0.], [1.,0.], [0.,.02], [0.,1.], [.02,0.]])
    faces = torch.tensor([[0,1,2],[0,3,4]]*50)
    stats = {}
    raster(uv, faces, 128, 123, stats=stats)
    assert stats['peak_candidates'] <= 123
    assert stats['total_candidates'] < 128*128*100
    # One triangle larger than the budget must itself be split, not an exception.
    stats = {}
    raster(uv, torch.tensor([[0,1,3]]), 128, 233, stats=stats)
    assert stats['chunks'] > 1 and stats['peak_candidates'] <= 233


def test_empty_degenerate_and_overlap_determinism():
    torch, raster = torch_api()
    uv = torch.tensor([[0.,0.],[1.,0.],[0.,1.]])
    for faces in [torch.empty((0,3),dtype=torch.long), torch.tensor([[0,0,0]])]:
        mask, tri, bary = raster(uv, faces, 8)
        assert not mask.any() and (tri == -1).all() and (bary == 0).all()
    faces = torch.tensor([[0,1,2],[2,1,0]])
    a = raster(uv, faces, 8, 7)
    b = raster(uv, faces, 8, 512)
    for x,y in zip(a,b):
        assert torch.equal(x,y)
    assert (a[1][a[0]] == 1).all()


@pytest.mark.parametrize('case', ['nan','outside','index','float_faces','budget','size'])
def test_invalid_raster_inputs(case):
    torch, raster = torch_api()
    uv = torch.tensor([[0.,0.],[1.,0.],[0.,1.]])
    faces = torch.tensor([[0,1,2]])
    args = {'size':8, 'candidate_budget':100}
    if case == 'nan': uv[0,0] = float('nan')
    if case == 'outside': uv[0,0] = -1
    if case == 'index': faces[0,0] = 3
    if case == 'float_faces': faces = faces.float()
    if case == 'budget': args['candidate_budget'] = 0
    if case == 'size': args['size'] = 0
    with pytest.raises(ValueError): raster(uv, faces, **args)


def test_independent_scalar_oracle():
    torch, raster = torch_api()
    rng = np.random.default_rng(288)
    uv = rng.uniform(.05,.95,(18,2)).astype(np.float32)
    faces = np.arange(18).reshape(-1,3)
    mask, ids, weights = raster(torch.tensor(uv), torch.tensor(faces), 11, 31, eps=0)
    expected = np.full((11,11), -1)
    for row in range(11):
        for col in range(11):
            point = np.array([(col+.5)/11,(row+.5)/11,1.])
            for f,verts in enumerate(faces):
                matrix = np.vstack([uv[verts].astype(float).T, np.ones(3)])
                bary = np.linalg.solve(matrix, point)
                if np.all(bary >= 0): expected[row,col] = f
    np.testing.assert_array_equal(ids.numpy(), expected)
    assert np.allclose(weights[mask].sum(1), 1)


def test_material_and_glb_roundtrip(tmp_path):
    torch_api()
    pytest.importorskip('trimesh')
    pytest.importorskip('cv2')
    import trimesh
    from movie_factory.trellis_adapter.fixture import build_fixture
    mesh, receipt = build_fixture()
    path = tmp_path/'fixture.glb'
    mesh.export(path)
    scene = trimesh.load(path, force='scene', process=False)
    restored = next(iter(scene.geometry.values()))
    np.testing.assert_allclose(restored.vertices, mesh.vertices, atol=1e-6)
    np.testing.assert_allclose(restored.visual.uv, mesh.visual.uv, atol=1e-6)
    for attr in ['baseColorTexture','metallicRoughnessTexture']:
        np.testing.assert_array_equal(np.asarray(getattr(restored.visual.material,attr)),
                                      np.asarray(getattr(mesh.visual.material,attr)))
    mr = np.asarray(restored.visual.material.metallicRoughnessTexture)
    assert mr[8,8].tolist() == [0,51,0]
    assert mr[48,48].tolist() == [0,204,191]
    assert receipt['coverage'] == 4096


def test_fixed_blender_dispatch():
    import importlib.util
    spec = importlib.util.spec_from_file_location('trellis288_runner', ROOT/'scripts/qualify_trellis288.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.validate({'operation':'inspect'}) == 'inspect'
    for bad in [None, {'operation':'execute'}, {'operation':'inspect','path':'arbitrary.blend'}, {'operation':True}]:
        with pytest.raises(ValueError): module.validate(bad)


def test_patch_applies_to_exact_upstream(tmp_path):
    import subprocess
    from movie_factory.trellis_adapter.patch import TARGETS
    for name,path in TARGETS.items():
        target=tmp_path/path;target.parent.mkdir(parents=True,exist_ok=True)
        data=(ROOT/'results/sikh288/upstream'/name).read_bytes()
        if name=='postprocess.py': data=data.removesuffix(b'\n')
        target.write_bytes(data)
    patch=tmp_path/'adapter.patch'
    patch.write_text(unified_patch(ROOT/'results/sikh288/upstream'))
    subprocess.run(['git','apply','--check',str(patch)],cwd=tmp_path,check=True,capture_output=True)
    subprocess.run(['git','apply',str(patch)],cwd=tmp_path,check=True,capture_output=True)
    for path,source in adapted_sources(ROOT/'results/sikh288/upstream').items():
        assert (tmp_path/path).read_text()==source


def test_cuda_probe_import_guard():
    import importlib.util
    spec=importlib.util.spec_from_file_location('cuda_probe',ROOT/'scripts/trellis288_cuda_probe.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    guard=module.RestrictedImports()
    for name in ['nvdiffrast','nvdiffrast.torch','rembg','trellis2.pipelines.rembg','renderutils']:
        with pytest.raises(ImportError): guard.find_spec(name)
    assert guard.find_spec('numpy') is None
