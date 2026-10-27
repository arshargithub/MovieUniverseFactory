import hashlib
import numpy as np
import pytest
from movie_factory.adapters.blender import anatomy_rest386 as r,nihang_anatomy386 as a,nihang_patch

def test_bounded_3d_form_is_distinct_from_depth_only_and_cannot_exceed_region(tmp_path):
 p=tmp_path/'.runtime/art-direction/anatomy386-targets/form.npz';p.parent.mkdir(parents=True);rest=np.zeros((22514,3),dtype=np.float32);rest[:,1]=-.8;rest[:,2]=1.3;target=rest.copy();target[0]+=[.02,.1,.03];mask=np.zeros(22514);mask[0]=1
 def save():
  np.savez_compressed(p,rest=rest,target=target,mask=mask);return dict(path=str(p.relative_to(tmp_path)),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
 b=save();e=dict(kind='mounted_anatomy386_form',target='horse',data=b);a.validate(e);nihang_patch.validate(dict(operation='nihang_patch',frame=283,width=640,height=640,samples=8,edits=[e]));assert r.load(tmp_path,b,depth_only=False)['target'].shape==(22514,3)
 with pytest.raises(ValueError,match='DEPTH_SCOPE'):r.load(tmp_path,b)
 target[0,0]=.3
 with pytest.raises(ValueError,match='DISPLACEMENT'):r.load(tmp_path,save(),depth_only=False)
