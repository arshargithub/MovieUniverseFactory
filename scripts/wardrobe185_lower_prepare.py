"""Bounded outer-Python preparation of lower-cloth contact regions.

Uses the repository SciPy environment, never Blender's incompatible Python.
These are conservative contact proxies, not modifications to the visible body.
"""
import hashlib
import json
from pathlib import Path
import numpy as np
from wardrobe185_lower import world_points
from wardrobe185_lower_pattern import lower_region_masks
from wardrobe185_convex import robust_hull,convex_outside

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'.runtime/art-direction/series01-facebuilder-trial-01'
SOURCE_SHA='20b06605833f46561db93ba3c25ef27e934b96abe39854958e8f1b101a284d0e'
CONTACT_SHA='15c434d960df8f9720b81d1d7d044ef0a29bca309631f310c7e1ba996de590c9'


def support_candidates(points):
    """Keep all maxima for the fixed hull directions without a huge matrix."""
    p=np.asarray(points)
    if p.ndim!=2 or p.shape[1]!=3 or not len(p) or not np.isfinite(p).all():raise ValueError('Invalid hull source')
    i=np.arange(96);z=1-2*(i+.5)/len(i);phi=i*np.pi*(3-np.sqrt(5));r=np.sqrt(1-z*z)
    directions=np.concatenate([np.stack([r*np.cos(phi),r*np.sin(phi),z],axis=1),np.eye(3),-np.eye(3)])
    best=np.full(len(directions),-np.inf);indices=np.zeros(len(directions),dtype=int)
    for start in range(0,len(p),4096):
        scores=p[start:start+4096]@directions.T;local=scores.argmax(0);values=scores[local,np.arange(len(directions))]
        replace=values>best;indices[replace]=start+local[replace];best[replace]=values[replace]
    return p[np.unique(indices)]


def build_hull(points):
    q,f=robust_hull(support_candidates(points),margin=.025)
    if convex_outside(points,q.astype(np.float32).astype(float),f).any():raise ValueError('Lower hull misses fitted source')
    return q,f


def main():
    source=BASE/'wardrobe185-lowercapture02/moving-source.npz';contact=BASE/'wardrobe185-horsecache01/contacts.npz'
    digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    if SOURCE_SHA is None or digest(source)!=SOURCE_SHA or digest(contact)!=CONTACT_SHA:raise ValueError('Unbound lower contact inputs')
    out=BASE/'wardrobe185-lowercontact01'
    if out.exists():raise ValueError('Preserve earlier lower contact evidence')
    out.mkdir();(out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    record=json.loads((source.parent/'source.json').read_text());data=np.load(source,allow_pickle=False)
    masks=lower_region_masks(data['pants_1']);arrays={};report={}
    for region,mask in masks.items():
        matrices=data[region+'_matrices'];gather=[]
        for frame in record['sample_frames']:
            gather.append(world_points(data['pants_'+str(frame)][mask],np.linalg.inv(matrices[frame-1])))
        p=np.concatenate(gather);q,f=build_hull(p)
        arrays[region+'_points']=q;arrays[region+'_faces']=f;arrays[region+'_matrices']=matrices
        report[region]={'source_points':len(p),'vertices':len(q),'faces':len(f),'outside_fitted_samples':0}
    with np.load(contact,allow_pickle=False) as horse:mat=horse['saddle_matrices']
    delta=mat@np.linalg.inv(mat[0]);seat_matrices=np.concatenate([np.repeat(np.eye(4)[None,:,:],216,axis=0),delta])
    gather=[]
    for frame in (217,223,326):
        path=BASE/('wardrobe185-lowerinspect01/surfaces-%03d.npz'%frame)
        with np.load(path,allow_pickle=False) as sample:
            for name in ('MF185_gait_horse','MF185_gait_saddle','MF185_gait_saddle.pad'):
                p=world_points(sample[name+'__points'],np.linalg.inv(seat_matrices[frame-1]))
                mask=(abs(p[:,0])<2.6)&(p[:,1]>-2.8)&(p[:,1]<2.4)&(p[:,2]>-9.8)
                gather.append(p[mask])
    p=np.concatenate(gather);q,f=build_hull(p)
    arrays['seat_points']=q;arrays['seat_faces']=f;arrays['seat_matrices']=seat_matrices
    report['seat']={'source_points':len(p),'vertices':len(q),'faces':len(f),'outside_fitted_samples':0,
        'limits':'Conservative local seat envelope fitted at three gait phases; inspect bulk and actual rendered clearance before admission'}
    np.savez_compressed(out/'contact.npz',**arrays)
    (out/'result.json').write_text(json.dumps({'source_sha256':SOURCE_SHA,'horse_contacts_sha256':CONTACT_SHA,
        'contact_sha256':digest(out/'contact.npz'),'regions':report,'visual_gate':'NOT_RUN'},indent=2)+'\n')
    print(json.dumps(report))


if __name__=='__main__':main()
