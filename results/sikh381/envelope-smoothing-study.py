from pathlib import Path
import numpy as np
from scipy.sparse import coo_matrix,diags
from scipy.sparse.linalg import splu
from movie_factory.horse_envelope381 import support
q=np.load('.runtime/factory-native/sikh376-appearance-c136-repair/horse-cache376.npz');g=np.load('.runtime/factory-native/sikh374-appearance-c124-inspect/horse-form374.npz');raw=np.load('/tmp/envelope381-control2.npz');m=support(q['rest'],g['weights'],g['group_names']);n=len(m);i,j=g['edges'].T;degree=np.bincount(g['edges'].ravel(),minlength=n);A=coo_matrix((np.ones(len(i)*2),(np.r_[i,j],np.r_[j,i])),shape=(n,n)).tocsr();L=diags(degree)-A;ids=np.flatnonzero(m>0);M=L[ids][:,ids];solve=splu((diags(np.ones(len(ids)))+10*M).tocsc()).solve;out={}
for f in [283,333,339,342,346,367]:
 p=q['source'][int((f-276)*2)];d=np.zeros_like(p);d[ids]=solve((raw['posed_'+str(f)]-p)[ids]);out['posed_'+str(f)]=p+d
np.savez_compressed('/tmp/envelope381-smooth.npz',**out)
s=Path('results/sikh381/geometry-study.py').read_text().replace("q=np.load('.runtime/factory-native/sikh380-appearance-c146-repair/chest380.npz')","q=np.load('/tmp/envelope381-smooth.npz')").replace('geometry-study.png','envelope149-smooth.png');Path('/tmp/envelopeplot381c.py').write_text(s)
