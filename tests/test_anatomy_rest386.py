import hashlib
import numpy as np
import pytest
from movie_factory.adapters.blender import anatomy_rest386 as r,nihang_anatomy386 as a,nihang_patch

def test_closed_rest_recipe_and_payload_boundaries(tmp_path):
 path=tmp_path/'.runtime/art-direction/anatomy386-targets/a.npz';path.parent.mkdir(parents=True)
 original=np.zeros((22514,3),dtype=np.float32);original[:,1]=-.8;original[:,2]=1.3;target=original.copy();target[0,1]+=.1;mask=np.zeros(22514);mask[0]=1
 def save(**more):
  np.savez_compressed(path,rest=original,target=target,mask=mask,**more);return dict(path=str(path.relative_to(tmp_path)),sha256=hashlib.sha256(path.read_bytes()).hexdigest())
 binding=save();edit=dict(kind='mounted_anatomy386_rest',target='horse',data=binding);a.validate(edit);nihang_patch.validate(dict(operation='nihang_patch',frame=283,width=640,height=640,samples=8,edits=[edit]));assert r.load(tmp_path,binding)['target'].shape==(22514,3)
 with pytest.raises(ValueError,match='KEYS'):r.load(tmp_path,save(code=np.array([1])))
 target[0,0]+=.001
 with pytest.raises(ValueError,match='DEPTH_SCOPE'):r.load(tmp_path,save())
 target[0,0]=0;target[0,1]=-.9
 with pytest.raises(ValueError,match='DEPTH_SCOPE'):r.load(tmp_path,save())
 target[0,1]=-.7;original[0,2]=target[0,2]=2
 with pytest.raises(ValueError,match='REGION'):r.load(tmp_path,save())
