from copy import deepcopy
import json
from pathlib import Path
import pytest
from movie_factory.adapters.blender import nihang_landing373 as l,nihang_patch

def edit():return json.loads(Path('results/sikh373/anchors76.json').read_text())

def test_typed_landing_rejects_wrong_boundary_and_injection():
 e=edit();l.validate(e)
 nihang_patch.validate(dict(operation='nihang_patch',frame=367,width=432,height=768,samples=8,edits=[e]))
 for key,value in [('left_contact',339),('right_contact',347),('code','run')]:
  bad=deepcopy(e);bad[key]=value
  with pytest.raises(ValueError):l.validate(bad)
 for key,value in [('frame',332),('pitch',-.9),('hip_drop',True)]:
  bad=deepcopy(e);bad['anchors'][0][key]=value
  with pytest.raises(ValueError):l.validate(bad)
 l.validate(dict(kind='mounted_landing373_contact',target='mounted leader'))

def test_arrival_accelerates_until_contact_then_stays_planted():
 start=[0,0,5];previous=[0,0,5.002];end=[.2,.1,3.3]
 poses=[l.hoof_path(start,previous,end,f,343) for f in range(333,347)]
 steps=[poses[i+1][2]-poses[i][2] for i in range(10)]
 assert all(b<a<0 for a,b in zip(steps,steps[1:]))
 assert steps[-1]<-.2
 assert poses[10:]==[end]*4
 assert poses[0]==start
 with pytest.raises(ValueError):l.hoof_path([0,0,3],[0,0,4],[0,0,4],334,343)

def test_accepted_cache_visibility_cannot_drop_history():
 prefix={f:True for f in range(276,334)};prefix[333]=False
 keys=l.visibility_keys(prefix,{334:True,367:True,368:True})
 assert dict(keys)[333] is False and dict(keys)[334] is True
 with pytest.raises(ValueError):l.visibility_keys({276:False},{334:True})
