"""Static finite-strain tissue proof with continuous source-surface attachments.

No Blender calls. Required positivity and actual native review remain independent.
Unlike186's hard group cuts, every cut target is tracked by a continuous local
source map, and tissue energy contains an explicit orientation barrier.
"""
from pathlib import Path
import json
import numpy as np
from scipy.spatial import cKDTree
from scipy.optimize import minimize
import anatomy386_volume185 as base


def energy(x,rest,tets,S,pins,goal,weight):
    F=base.gradients(x.reshape(-1,3),tets,S['grad']);J=np.linalg.det(F)
    if J.min()<=.015:return 1e30,np.zeros(x.size)
    invT=np.transpose(np.linalg.inv(F),(0,2,1));log=np.log(J);mu=1.;lam=5.
    # Stable compressible neo-Hookean bulk plus a barrier atJ=.015.
    barrier=.005;gap=J-.015
    W=.5*mu*(np.sum(F*F,axis=(1,2))-3)-mu*log+.5*lam*log*log-barrier*np.log(gap/(1-.015))
    P=mu*F+(-mu+lam*log-barrier*J/gap)[:,None,None]*invT
    g=np.zeros_like(rest);np.add.at(g,tets.ravel(),(S['vol'][:,None,None]*np.einsum('tij,taj->tai',P,S['grad'])).reshape(-1,3))
    d=x.reshape(-1,3)[pins]-goal;g[pins]+=weight*d
    return float(S['vol']@W+.5*weight*np.sum(d*d)),g.ravel()


def attachment(rest,source0,posed,ids):
    # Same continuous local affine map at every cut, no incompatible region labels.
    dist,ix=cKDTree(source0[ids]).query(rest,k=24);ix=ids[ix];out=[]
    for p,a,b,d in zip(rest,source0[ix],posed[ix],dist):
        w=1/np.maximum(d,.025)**2;w/=w.sum();ca=w@a;cb=w@b
        A=(a-ca)*np.sqrt(w[:,None]);B=(b-cb)*np.sqrt(w[:,None]);G=np.linalg.solve(A.T@A+1e-6*np.eye(3),A.T@B)
        out.append((p-ca)@G+cb)
    return np.array(out)


def run(root):
    src=root/'.runtime/factory-native/sikh386-appearance-c186-source/anatomy386-source.npz';q=np.load(src,allow_pickle=False);tri=np.load(root/'.runtime/factory-native/sikh374-appearance-c124-inspect/horse-form374.npz',allow_pickle=False)['triangles']
    C=base.cage(q,tri);S=base.system(C['rest'],C['tets'],C['fixed']);x=C['rest'].copy();hist=[];report=root/'results/sikh386/volume187-numeric.json'
    # Original184 raw skin is the neutral goal. Continuous cut targets preserve
    # their observed bending rather than assigning all neck nodes a head transform.
    source0=q['source'][14].astype(float);ids=C['skinids'];pins=C['fixed'];weight=11.
    for frame in list(range(283,340,2)):
        posed=q['source'][int((frame-276)*2)];goal=attachment(C['rest'][pins],source0,posed,ids)
        result=minimize(energy,x.ravel(),args=(C['rest'],C['tets'],S,pins,goal,weight),jac=True,method='L-BFGS-B',options=dict(maxiter=1500,ftol=1e-10,gtol=1e-5,maxls=50,maxcor=20))
        x=result.x.reshape(-1,3);J=np.linalg.det(base.gradients(x,C['tets'],S['grad']));err=np.linalg.norm(x[pins]-goal,axis=1)
        hist.append(dict(frame=frame,success=bool(result.success),message=str(result.message),iterations=int(result.nit),min_jacobian=float(J.min()),max_jacobian=float(J.max()),volume_ratio=float(S['vol']@J/S['vol'].sum()),pin_max=float(err.max()),pin_rms=float(np.sqrt(np.mean(err**2)))))
        report.write_text(json.dumps(dict(phase='solving',cage=C['stats'],history=hist),indent=2)+'\n')
        if J.min()<=.015:raise ValueError('VOLUME187_INVERSION')
    d=hist[-1]
    if not d['success'] or d['min_jacobian']<=.02 or d['max_jacobian']>5 or d['pin_max']>.06:raise ValueError(('VOLUME187_INVALID',d))
    bound=np.einsum('ni,nij->nj',C['bary'],x[C['tets'][C['cell']]])
    data=q['source'].copy();i=126;delta=(bound-data[i,ids])*C['mask'][:,None]
    if np.linalg.norm(delta,axis=1).max()>.45:raise ValueError('VOLUME187_DELTA')
    data[i,ids]+=delta;mask=np.zeros(len(q['rest']),dtype=np.float32);mask[ids]=C['mask'];dest=root/'.runtime/art-direction/anatomy386-targets';dest.mkdir(parents=True,exist_ok=True)
    np.savez_compressed(dest/'volume187-static339.npz',source=q['source'],target=data,rest=q['rest'],mask=mask,times=q['times'])
    np.savez_compressed(dest/'volume187-cage.npz',rest=C['rest'],posed=x,tets=C['tets'],fixed=pins,skinids=ids,cell=C['cell'],bary=C['bary'])
    final=dict(phase='numeric_prototype_complete',cage=C['stats'],history=hist,max_delta=float(np.linalg.norm(delta,axis=1).max()),corrected_frames=[339],other_samples='Exact uncorrected source placeholders; NOT a motion candidate.',scope='Static339 continuous-interface finite-strain proof only; native front/side/opposite/whole required.')
    report.write_text(json.dumps(final,indent=2)+'\n');print(json.dumps({k:v for k,v in final.items() if k!='history'}))

if __name__=='__main__':run(Path(__file__).resolve().parents[1])
