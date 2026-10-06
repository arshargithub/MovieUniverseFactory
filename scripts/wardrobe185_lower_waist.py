"""Select the torso component of a clipped body band; preserve motion exactly."""
import hashlib
import json
from pathlib import Path
import numpy as np


def components(faces,count):
    neighbors=[set() for _ in range(count)]
    for face in faces:
        for a,b in zip(face,np.roll(face,-1)):neighbors[int(a)].add(int(b));neighbors[int(b)].add(int(a))
    labels=np.full(count,-1,dtype=int);groups=[]
    for seed in range(count):
        if labels[seed]>=0:continue
        group=[];stack=[seed];labels[seed]=len(groups)
        while stack:
            i=stack.pop();group.append(i)
            for j in neighbors[i]:
                if labels[j]<0:labels[j]=len(groups);stack.append(j)
        groups.append(np.array(group))
    return groups


def main():
    base=Path(__file__).resolve().parents[1]/'.runtime/art-direction/series01-facebuilder-trial-01'
    source=base/'wardrobe185-lowersurface03/surfaces.npz';sha='165723e28e4025a6658f242e6a5b684742e8b0b72654260464cdfc0475964ac3'
    digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    if digest(source)!=sha:raise ValueError('Unbound waist source')
    out=base/'wardrobe185-waistcontact01'
    if out.exists():raise ValueError('Preserve contact evidence')
    out.mkdir();(out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    with np.load(source,allow_pickle=False) as d:data={k:d[k] for k in d.files}
    p=data['waist_frames'];f=data['waist_faces'];groups=components(f,len(p[0]))
    eligible=[g for g in groups if abs(p[0,g].mean(0)[0])<.25 and np.ptp(p[0,g,0])>2.5]
    if len(eligible)!=1:raise ValueError('Ambiguous torso component')
    keep=np.sort(eligible[0]);lookup=np.full(len(p[0]),-1);lookup[keep]=np.arange(len(keep))
    chosen=np.all(np.isin(f,keep),axis=1);cf=lookup[f[chosen]]
    edges=np.sort(np.concatenate([cf[:,[0,1]],cf[:,[1,2]],cf[:,[2,0]]]),axis=1)
    _,counts=np.unique(edges,axis=0,return_counts=True)
    if not np.all(counts==2):raise ValueError('Selected waist is not closed')
    data['waist_frames']=p[:,keep];data['waist_faces']=cf
    np.savez_compressed(out/'contact.npz',**data)
    (out/'result.json').write_text(json.dumps({'source_sha256':sha,'contact_sha256':digest(out/'contact.npz'),
        'source_components':len(groups),'retained_component':'Central torso; exclude clipped forearm fragments',
        'retained_vertices':len(keep),'retained_faces':len(cf),'source_frames_exact':True,
        'visual_gate':'NOT_RUN'},indent=2)+'\n')


if __name__=='__main__':main()
