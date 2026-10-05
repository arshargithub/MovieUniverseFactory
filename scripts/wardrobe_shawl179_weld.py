"""Fixed shared-boundary cloth construction; no runtime source/path payloads."""
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as foundation
INPUT=foundation.BASE/'wardrobe179-initial07/constructed-layout.npz'
INPUT_SHA='e740133b78865b9690f35bec30b353276400fd42636357fbb3a83e078af1d0a2'
COUNT=3256
WELD_INPUT=foundation.BASE/'wardrobe179-weld-initial03/constructed-layout.npz'
WELD_SHA='dae2e300de4d012829c60dbf4d60b043ea904eaf4ce137e8dd92f629e8e99f23'

def regular_curve(points):
    import numpy as np
    length=np.concatenate(([0.],np.cumsum(np.linalg.norm(np.diff(points,axis=0),axis=1))))
    if length[-1]<1e-6:raise ValueError('Collapsed garment guide')
    query=np.linspace(0,length[-1],len(points))
    return np.stack([np.interp(query,length,points[:,k]) for k in range(3)],axis=1)

def weld(record):
    import numpy as np
    p=record['points'].copy();f=record['faces'];s=record['stitches']
    if p.shape!=(3287,3) or f.shape!=(3120,4) or s.shape!=(31,2):
        raise ValueError('Fixed inspected one-course topology required')
    hood=p[:1271].reshape(41,31,3)
    # Equal arc sampling retains the outline while avoiding tiny sliver cells.
    for _ in range(3):
        for row in range(1,40):hood[row]=regular_curve(hood[row])
        for col in range(31):hood[:,col]=regular_curve(hood[:,col])
    keep=np.arange(len(p));keep=keep[(keep<1240)|(keep>=1271)]
    mapping={int(old):new for new,old in enumerate(keep)}
    for h,w in s:mapping[int(h)]=mapping[int(w)]
    faces=np.array([[mapping[int(v)] for v in face] for face in f],dtype=int)
    if any(len(set(face))!=4 for face in faces):raise ValueError('Collapsed welded quad')
    pins={mapping[int(i)]:float(w) for i,w in zip(record['pin_indices'],record['pin_weights'])}
    return p[keep],faces,pins

def validate(job):
    if not isinstance(job,dict) or set(job)!={'operation'} or job['operation'] not in ('initial01','initial02','initial03','solve01','windoff01','solve02','windoff02'):
        raise ValueError('Fixed welded construction operation only')
    if foundation.SOURCE.is_symlink() or foundation.digest(foundation.SOURCE)!=foundation.SOURCE_SHA:
        raise ValueError('Protected foundation mismatch')
    if INPUT.is_symlink() or foundation.digest(INPUT)!=INPUT_SHA:raise ValueError('Inspected cut mismatch')
    if job['operation'].startswith(('solve','windoff')) and (WELD_INPUT.is_symlink() or foundation.digest(WELD_INPUT)!=WELD_SHA):
        raise ValueError('Conditioned shared-boundary cut mismatch')
    out=foundation.BASE/('wardrobe179-weld-'+job['operation'])
    if out.exists() or out.is_symlink():raise ValueError('Never overwrite evidence')
    return out

def contact(points,pins):
    import bpy
    import numpy as np
    from mathutils import Vector
    from wardrobe_refinement import tree_for
    # The covered scalp/nape lies within the closed local groom envelope.
    # Open bust normals are not a valid global inside classifier and snapping
    # to their nearest vertices destroyed cell spacing in initial02.
    trees=[tree_for(bpy.data.objects['MF_173_static_groom_clearance'])]
    def margin(p):
        return min((Vector(p)-h).dot(n) for tree in trees for h,n,_,d in [tree.find_nearest(Vector(p))] if h is not None)
    before=[margin(p) for p in points[:1240]]
    for index in range(1240):
        p=Vector(points[index])
        for _ in range(20):
            for tree in trees:
                h,n,_,d=tree.find_nearest(p)
                if h is not None and (p-h).dot(n)<.062:
                    # Preserve the point's tangential location at edge/vertex
                    # contacts rather than collapse several cells onto one.
                    p+=n*(.064-(p-h).dot(n))
        points[index]=p
    # Kinematic support only where the crown is actually close to hair.
    crown=[]
    for row in range(3,20):
        for col in range(8,23):
            i=row*31+col;h,n,_,d=trees[0].find_nearest(Vector(points[i]))
            if h is not None and d<.12 and n.z>.20:pins[i]=1.;crown.append(i)
    after=[margin(p) for p in points[:1240]]
    distances=[min(tree.find_nearest(Vector(p))[3] for tree in trees) for p in points[:1240]]
    audit={'nearest_head_groom_signed_min_before_native':min(before),
            'nearest_head_groom_signed_min_after_native':min(after),
            'unsigned_nearest_clearance_min_native':min(distances),
            'signed_diagnostic_not_closed_surface_inside_classifier':True,
            'crown_contact_pin_count':len(crown),'post_solve_projection':False,
            'method':'Shared rear boundary, arc-resampled rest geometry, actual-contact supported crown/free edges'}
    print('179 welded contact audit',json.dumps(audit),flush=True)
    if min(distances)<.059:raise ValueError('Welded unsigned contact clearance fails')
    return audit

def main():
    import bpy
    import numpy as np
    import wardrobe_studio as studio
    from wardrobe_shawl179 import screens
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text());out=validate(job);out.mkdir()
    for name in ('wardrobe_shawl179_weld.py','wardrobe_shawl179_motion.py','wardrobe_shawl179_collision.py',
                 'wardrobe_underarm179_repair.py','wardrobe_motion178_proof.py','wardrobe_motion178_controls.py',
                 'wardrobe_motion178.py','wardrobe_shawl179.py'):
        (out/name).write_bytes((ROOT/'scripts'/name).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(foundation.SOURCE),load_ui=False,use_scripts=False)
    foundation.check_protected();rig,mats,_=foundation.clean_foundation()
    if job['operation'].startswith(('solve','windoff')):
        with np.load(WELD_INPUT,allow_pickle=False) as record:
            points=record['points'].tolist();faces=record['faces'].tolist()
            pins={int(i):float(w) for i,w in zip(record['pin_indices'],record['pin_weights'])}
        if len(points)!=COUNT or len(faces)!=3120:raise ValueError('Fixed welded topology mismatch')
        from wardrobe_shawl179_motion import simulate
        result=simulate(out,rig,mats,None,points,faces,pins,[],
                        wind_off=job['operation'].startswith('windoff'),integrated=True)
        foundation.check_protected()
        (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
        return
    with np.load(INPUT,allow_pickle=False) as record:points,faces,pins=weld(record)
    audit=contact(points,pins)
    edges=np.linalg.norm(points[faces]-points[np.roll(faces,1,axis=1)],axis=2)
    audit['edge_native_quantiles']=np.quantile(edges,[0,.01,.5,.99,1]).tolist()
    audit['face_edge_aspect_quantiles']=np.quantile(edges.max(1)/edges.min(1),[.5,.99,1]).tolist()
    (out/'contact-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    if (edges.max(1)/edges.min(1)).max()>20:raise ValueError('Conditioned cloth cell-spacing guard fails')
    np.savez_compressed(out/'constructed-layout.npz',points=points,faces=faces,
        pin_indices=np.array(sorted(pins)),pin_weights=np.array([pins[i] for i in sorted(pins)]),
        stitches=np.empty((0,2),dtype=int))
    studio.panel('MF179_continuous_shawl',points.tolist(),faces.tolist(),mats['scarf'],.014,1)
    screens(out)
    foundation.check_protected()
    (out/'result.json').write_text(json.dumps({'protected_exact':True,'visual_gate':'NOT_RUN',
        'physics_not_run':True,'vertices':COUNT,'contact_audit':audit,
        'handler_sha256':foundation.digest(Path(__file__))},indent=2)+'\n')

if __name__=='__main__':main()
