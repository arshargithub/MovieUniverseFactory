"""Finite-strain derivatives and tracked cuts; no anatomy acceptance."""
import sys
from pathlib import Path
import numpy as np
from scipy.optimize._numdiff import approx_derivative
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import anatomy386_volume187 as m

def sample():
 p=np.array([[0.,0,0],[1,0,0],[0,1,0],[0,0,1],[.25,.25,.25]]);t=np.array([[0,1,2,4],[0,1,4,3],[0,4,2,3],[4,1,2,3]])
 return p,t,m.base.system(p,t,np.arange(4))

def test_neo_hookean_analytic_derivative():
 p,t,S=sample();x=p.copy();x[4]+=[.03,-.02,.04];args=(p,t,S,np.arange(4),p[:4],11.)
 _,g=m.energy(x.ravel(),*args);numeric=approx_derivative(lambda a:m.energy(a,*args)[0],x.ravel()).ravel()
 assert np.max(abs(g-numeric))<1e-6

def test_continuous_source_attachment_preserves_rigid_transform():
 rng=np.random.default_rng(42);p=rng.normal(size=(40,3));R=np.array([[0.,-1,0],[1,0,0],[0,0,1]]);b=p@R.T+[2,3,4];q=rng.normal(size=(12,3))
 assert np.allclose(m.attachment(q,p,b,np.arange(len(p))),q@R.T+[2,3,4],atol=1e-5)

def test_orientation_barrier_rejects_inversion():
 p,t,S=sample();x=p.copy();x[:,0]*=-1
 assert m.energy(x.ravel(),p,t,S,np.arange(4),p[:4],11.)[0]==1e30
