"""Mathematical/control tests only, not artistic or native qualification."""
import math
import numpy as np
import pytest
from movie_factory.adapters.blender.nihang_finish362 import crown_point,pigment_range
from movie_factory.adapters.blender.nihang_patch import validate

def test_crown_preserves_fitted_brow_and_monotone_upper_shape():
    for a in np.linspace(-math.pi,math.pi,21):
        p=(.1*math.sin(a),-.025+.1*math.cos(a),.06)
        assert crown_point(p,-.025)==pytest.approx(p)
        z=[crown_point((p[0],p[1],h),-.025)[2] for h in np.linspace(.06,.31,101)]
        assert min(np.diff(z))>0 and max(z)<.241
    assert crown_point((0,-.025,.254),-.025)[2]<.238

def test_fixed_finish_rejects_arbitrary_parameters():
    v=dict(operation='nihang_patch',frame=283,width=640,height=640,samples=8,edits=[dict(kind='mounted_finish362',target='mounted leader')])
    validate(v)
    v['edits'][0]['code']='arbitrary'
    with pytest.raises(ValueError,match='PATCH_ACTOR_FIELDS'):validate(v)

def test_only_exact_old_pigment_range_is_changed():
    class Socket:
        def __init__(self,v):self.default_value=v
    class Node:
        type='MAP_RANGE'
        def __init__(self,a,b):self.inputs={'From Min':Socket(a),'From Max':Socket(b)}
    class Tree:pass
    class Material:pass
    mat=Material();mat.node_tree=Tree();a=Node(.16,.34);b=Node(.1,.9);mat.node_tree.nodes=[a,b]
    assert pigment_range(mat)==1
    assert a.inputs['From Min'].default_value==.295 and a.inputs['From Max'].default_value==.390
    assert b.inputs['From Min'].default_value==.1
    assert pigment_range(mat)==0
