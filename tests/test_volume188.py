"""Continuation supplies a useful gradient on invalid line-search trials."""
import sys
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
from scipy.optimize._numdiff import approx_derivative
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import anatomy386_volume188 as m

def sample():
 p=np.array([[0.,0,0],[1,0,0],[0,1,0],[0,0,1],[.25,.25,.25]]);t=np.array([[0,1,2,4],[0,1,4,3],[0,4,2,3],[4,1,2,3]])
 return p,t,m.base.system(p,t,np.arange(4))

def test_gradient_valid_and_inverted_trials():
 p,t,S=sample();args=(p,t,S,np.arange(4),p[:4],11.)
 for factor in [1.,.02,-.2]:
  x=p.copy();x[:,0]*=factor;x[4]+=[.01,-.02,.01]
  val,g=m.energy(x.ravel(),*args);num=approx_derivative(lambda a:m.energy(a,*args)[0],x.ravel()).ravel()
  assert np.isfinite(val) and np.allclose(g,num,rtol=2e-5,atol=2e-5)
  if factor<0:assert np.linalg.norm(g)>1

def test_nontrivial_soft_pin_move_does_not_stall_at_rest():
 p,t,S=sample();goal=p[:4].copy();goal[1]+=[.1,.2,.1]
 result=minimize(m.energy,p.ravel(),args=(p,t,S,np.arange(4),goal,11.),jac=True,method='L-BFGS-B',options=dict(maxiter=1500,ftol=1e-12,gtol=1e-7,maxls=50))
 x=result.x.reshape(-1,3);J=np.linalg.det(m.base.gradients(x,t,S['grad']))
 assert result.success and np.linalg.norm(x-p)>.1
 assert np.max(np.linalg.norm(x[:4]-goal,axis=1))<.03 and J.min()>.02
