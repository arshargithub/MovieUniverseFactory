"""Input boundary tests, not visual or deformation qualification."""
import copy
from pathlib import Path
import pytest
from movie_factory.adapters.blender import warhorse383 as w,nihang_patch as p,nihang_control as c

def test_closed_import():
    e=dict(kind='warhorse_import383',target='warhorse383');w.validate(e)
    for extra in ['path','code','url','download']:
        with pytest.raises(ValueError):w.validate({**e,extra:'untrusted'})
    with pytest.raises(ValueError):w.validate({**e,'target':'horse'})
    p.validate(dict(operation='nihang_patch',frame=283,width=640,height=640,samples=8,edits=[e]))

@pytest.mark.parametrize('view', sorted(w.VIEWS))
def test_views(view):
    c.validate(dict(operation='nihang_frames',frame=283,frames=[283,315,339],view=view,width=640,height=640,samples=8))

def test_actual_pinned_asset():
    v=w.validate_glb(Path(w.SOURCE))
    assert len(v['skins'][0]['joints'])==39
    assert len(v['meshes'][0]['primitives'])==1
    assert all('uri'not in x for x in v['images'])

def test_wrong_bytes(tmp_path):
    path=tmp_path/'bad.glb';path.write_bytes(b'bad')
    with pytest.raises(ValueError,match='HASH'):w.validate_glb(path)

@pytest.mark.parametrize('kind,method',[('warhorse_retarget383','retarget'),('warhorse_ground383','ground')])
def test_closed_dispatch_without_blender(kind,method,monkeypatch,tmp_path):
    sentinel=object()
    monkeypatch.setattr(w,method,lambda bpy,out,edit:sentinel)
    assert w.run(None,tmp_path,dict(kind=kind,target='warhorse383')) is sentinel
