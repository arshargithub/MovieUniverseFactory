import importlib.util
from pathlib import Path
import sys
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from anatomy386_coupled388 import domain
from anatomy386_structural387 import self_test

def test_coupled_metric_zero_rigid():
    c=self_test();assert max(c.values())<1e-9

def test_domain_protects_distal_and_outside():
    r=np.array([[0,-.7,1.3],[.1,-.7,1.3],[0,-.7,.5],[0,0,1.3],[0,-.7,2.1],[0,-.7,1.2]])
    e=np.array([[0,1],[1,2],[2,3],[3,4],[4,5],[5,0]])
    names=['DEF-forefoot.L'];w=np.zeros((6,1));w[5]=1
    d=domain(r,w,names,e);assert not d[2:].any()
