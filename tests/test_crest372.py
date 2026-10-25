from copy import deepcopy
import math
import pytest
from movie_factory.adapters.blender import nihang_crest372 as c,nihang_patch as p

def candidate():
 return dict(kind='mounted_crest372',target='mounted leader',anchors=[dict(frame=f,left_curl=l,right_curl=r,left_toe=t,right_toe=t) for f,l,r,t in [(315,0,0,0),(319,.42,.30,.1),(323,.80,.60,.18),(326,.68,.87,.2),(329,.92,.73,.17),(333,.8,.95,.22)]])

def test_protected_entry_and_phase_bounds():
 c.validate(candidate())
 for field,value in [('frame',314),('left_curl',.1)]:
  bad=deepcopy(candidate());bad['anchors'][0][field]=value
  with pytest.raises(ValueError):c.validate(bad)
 for value in [334,350]:
  bad=deepcopy(candidate());bad['anchors'][-1]['frame']=value
  with pytest.raises(ValueError):c.validate(bad)
 for k,v in [('left_curl',1.5),('right_toe',float('nan')),('left_curl',True)]:
  bad=deepcopy(candidate());bad['anchors'][2][k]=v
  with pytest.raises(ValueError):c.validate(bad)

def test_curve_entry_continuity_and_no_angular_overshoot():
 a=candidate()['anchors'];assert all(c.sample(a,315)[k]==0 for k in c.FIELDS)
 for lo,hi in zip(a,a[1:]):
  for i in range(21):
   row=c.sample(a,lo['frame']+(hi['frame']-lo['frame'])*i/20)
   for k in c.FIELDS:assert min(lo[k],hi[k])-1e-8<=row[k]<=max(lo[k],hi[k])+1e-8
 assert c.sample(a,323)['left_curl']!=c.sample(a,323)['right_curl']
 assert c.sample(a,329)['right_curl']!=c.sample(a,333)['right_curl']

def test_typed_authoring_and_readonly_contact_routes():
 p.validate(dict(operation='nihang_patch',frame=333,width=640,height=640,samples=8,edits=[candidate()]))
 c.validate(dict(kind='mounted_crest372_contact',target='mounted leader'))
 for bad in [dict(kind='mounted_crest372_contact',target='mounted leader',code='execute'),dict(kind='mounted_crest372',target='another',anchors=candidate()['anchors'])]:
  with pytest.raises(ValueError):c.validate(bad)
