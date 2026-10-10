import sys
from pathlib import Path
import pytest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from entrance206_inspect import validate,SOURCES

def test_closed_inspection():
 validate({'operation':'inspect01'})
 for job in ({},{'operation':'other'},{'operation':'inspect01','code':'x'}):
  with pytest.raises(ValueError):validate(job)
 assert len(SOURCES)==2 and all(len(v[1])==64 for v in SOURCES.values())

def test_sequence_and_protected_turn():
 from entrance206_performance import expression,escape_weight
 assert escape_weight(339)==0 and escape_weight(360)>.95
 assert escape_weight(391)==0 and escape_weight(648)==0
 assert expression(327)['browInnerUp']>expression(321)['browInnerUp']+.25
 assert expression(344)['browDownLeft']>expression(321)['browDownLeft']+.45
 for f in range(217,649):assert all(0<=v<=1 for v in expression(f).values())

def test_pinned_root_guide_simulation():
 from entrance206_hair import simulate,topology
 rest=np.column_stack((np.zeros(12),np.linspace(-1,-.7,12),np.linspace(16,13.6,12)));offsets=np.array([0,12]);wind=np.tile([0,1,.03],(48,1))
 a,m,state=simulate(rest,offsets,wind,np.zeros((48,3)))
 assert np.isfinite(a).all() and np.array_equal(a[:,0],np.tile(rest[0],(48,1)))
 assert m[:,2].max()==0 and m[:,1].max()<.03 and m[-1,0]>.05
 b,_,_=simulate(rest,offsets,wind,np.zeros((48,3)))
 assert np.array_equal(a,b)
 covered=rest.copy();covered[:,1]=.6
 c,_,_=simulate(covered,offsets,wind,np.zeros((48,3)))
 assert np.allclose(c,np.tile(covered,(48,1,1)),atol=1e-6)

def test_integrated_closed_enum():
 from entrance206_integrated import validate as check
 check({'operation':'opening06'});check({'operation':'route07'})
 for job in ({'operation':'opening06','path':'anything'},{'operation':'eval'},{},None):
  with pytest.raises(ValueError):check(job)

def test_full_review_clock_and_gate_schema():
 from entrance206_review import OPS,validate
 all_frames=sum((OPS[k][1] for k in ('opening10','route11','attention16','hair14')),())
 assert sorted(all_frames)==list(range(217,649))
 assert OPS['opening10'][2] and OPS['route11'][2]
 validate({'operation':'hair14'})
 with pytest.raises(ValueError):validate({'operation':'route11','skip_gate':True})

def test_bank_setback_preserves_traversed_support():
 from entrance206_geography import cutback
 p=np.array([[-5,-18],[-10,-20],[-20,-40],[-40,-18]],float);h=np.array([2.,5.,10.,12.]);d=np.array([1.,5.,5.,5.])
 a=cutback(p,h,d)
 assert a[0]==h[0] and a[1]==0 and np.array_equal(a[2:],h[2:])
