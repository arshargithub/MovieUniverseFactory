"""Rig-local regional contacts for lower cloth; outer Python preprocessing.

Keep the actual horse/tack. Fit small anatomical regions instead of one
all-pose seat hull or a remeshed skin that bridges separating joints.
No visible actor mesh is edited. Dressing/coverage/visual admission is separate.
"""
import hashlib
import json
from pathlib import Path
import numpy as np
from wardrobe185_lower_prepare import build_hull

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'.runtime/art-direction/series01-facebuilder-trial-01'


def rigid_fit(rest,posed):
    a=rest.mean(0);b=posed.mean(0)
    u,_,vt=np.linalg.svd((rest-a).T@(posed-b))
    r=vt.T@u.T
    if np.linalg.det(r)<0:vt[-1]*=-1;r=vt.T@u.T
    m=np.eye(4);m[:3,:3]=r;m[:3,3]=b-r@a
    return m


def masks(rest):
    x,y,z=np.asarray(rest).T
    return {'pelvis':(z>-6.45)&(z<-5.0)&(abs(x)<1.9),
        'abdomen':(z>-5.65)&(z<-3.65)&(abs(x)<1.5),
        'thighL':(x>0)&(z<-6.15)&(z>-9.25),
        'thighR':(x<0)&(z<-6.15)&(z>-9.25)}


def main():
    digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    contact=BASE/'wardrobe185-lowersurface06/surfaces.npz'
    motion=BASE/'wardrobe185-lowercapture02/moving-source.npz'
    if digest(contact)!='3bf762fe9244188ef563a8ce1f235fb83c07614e7f538c8bc6209ff076e0499e':raise ValueError('Contact source changed')
    if digest(motion)!='20b06605833f46561db93ba3c25ef27e934b96abe39854958e8f1b101a284d0e':raise ValueError('Rig source changed')
    out=BASE/'wardrobe185-lowerregions01'
    if out.exists():raise ValueError('Preserve previous contact evidence')
    out.mkdir();(out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    with np.load(contact,allow_pickle=False) as d:data={k:d[k] for k in d.files}
    with np.load(motion,allow_pickle=False) as d:rig={k:d[k] for k in ('pelvis_matrices','thighL_matrices','thighR_matrices')}
    ids=data['frame_ids'];points=np.concatenate([data[n+'_frames'] for n in ('body','upper','pants')],axis=1)
    body=data['body_frames'];selection=masks(body[0])['abdomen']
    abdomen=np.array([rigid_fit(body[0,selection],q[selection]) for q in body])
    transforms={k:rig[k+'_matrices'][ids-1] for k in ('pelvis','thighL','thighR')};transforms['abdomen']=abdomen
    payload={k:v for k,v in data.items() if k.split('_')[0] not in ('body','upper','pants')};report={}
    for name,selected in masks(points[0]).items():
        mats=transforms[name];inv=np.linalg.inv(mats);source=points[:,selected]
        local=np.einsum('fij,fnj->fni',inv[:,:3,:3],source)+inv[:,None,:3,3]
        # Mounted-only envelope. Standing uses its already admitted separate
        # solve, so do not inflate the riding proxy to an unrelated leg pose.
        q,f=build_hull(local[1:].reshape(-1,3))
        frames=np.einsum('fij,nj->fni',mats[:,:3,:3],q)+mats[:,None,:3,3]
        payload[name+'_frames']=frames.astype(np.float32);payload[name+'_faces']=f
        report[name]={'vertices':len(q),'triangles':len(f),'selected_source_points_per_pose':int(selected.sum()),
            'fit_source_frames':len(ids)-1,'source_containment':'PASS by convex half spaces',
            'local_bounds': [q.min(0).tolist(),q.max(0).tolist()]}
    np.savez_compressed(out/'surfaces.npz',**payload)
    (out/'result.json').write_text(json.dumps({'source_sha256':digest(contact),'rig_sha256':digest(motion),
        'surfaces_sha256':digest(out/'surfaces.npz'),'regions':report,'rendered_actor_unchanged':True,
        'admission':'NOT_RUN','visual_gate':'NOT_RUN','scope':'Mounted regional proxy candidate; actual horse/tack retained; independent standing solve'},indent=2)+'\n')


if __name__=='__main__':main()
