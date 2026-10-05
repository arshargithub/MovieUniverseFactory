"""Fixed approved single-drape wardrobe operations; no runtime code payloads.

Agent-authored pre-dressing, seamed hood and one outer course. Native cloth
provides free secondary motion; this is not automatic tying or textile physics
calibration. All visual gates start NOT_RUN. Failed outputs are immutable.
"""
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import wardrobe_motion178 as foundation

BASE = foundation.BASE
OPERATIONS = ('initial01', 'initial02', 'initial03', 'initial04', 'solve01', 'windoff01', 'initial05', 'solve02', 'windoff02')
OPERATIONS += ('initial06','initial07','solve03','windoff03')
CONSTRUCTION_AUDIT = {}
HEAD_ROWS, HEAD_COLS, WRAP_ROWS, WRAP_COLS = 41, 31, 96, 21
HEAD_COUNT = HEAD_ROWS * HEAD_COLS
COUNT = HEAD_COUNT + WRAP_ROWS * WRAP_COLS
INITIAL = BASE/'wardrobe179-initial04/constructed-layout.npz'
INITIAL_SHA = 'e541c75772c9e7ca03aa6d3c6c9f6f794c901e7d50d81ff41b9ccd8607b62bb0'
JOINED_INITIAL = BASE/'wardrobe179-initial05/constructed-layout.npz'
JOINED_SHA = '74acd62caa000ec3d9cc562de5b230d9c76a2cfaaeb9cb23e1e932d9b022ce76'
CONTACT_INITIAL = BASE/'wardrobe179-initial07/constructed-layout.npz'
CONTACT_SHA = 'e740133b78865b9690f35bec30b353276400fd42636357fbb3a83e078af1d0a2'


def validate(job):
    if not isinstance(job, dict) or set(job) != {'operation'} or job['operation'] not in OPERATIONS:
        raise ValueError('Fixed approved shawl operation only')
    if foundation.SOURCE.is_symlink() or foundation.digest(foundation.SOURCE) != foundation.SOURCE_SHA:
        raise ValueError('Protected foundation mismatch')
    if job['operation'] in ('solve01','windoff01') and (INITIAL.is_symlink() or foundation.digest(INITIAL)!=INITIAL_SHA):
        raise ValueError('Inspected fixed construction mismatch')
    if job['operation'] in ('solve02','windoff02') and (JOINED_INITIAL.is_symlink() or foundation.digest(JOINED_INITIAL)!=JOINED_SHA):
        raise ValueError('Joined construction mismatch')
    if job['operation'] in ('solve03','windoff03') and (CONTACT_INITIAL.is_symlink() or foundation.digest(CONTACT_INITIAL)!=CONTACT_SHA):
        raise ValueError('Contact-cleared construction mismatch')
    out = BASE / ('wardrobe179-' + job['operation'])
    if out.exists() or out.is_symlink():
        raise ValueError('Never overwrite evidence')
    return out


def head_point(u, v):
    """Rounded crown and long soft rear fall, no rear band or rim."""
    sections = ((0., -.04, 1.14, 1.31, 1.24),
                (.22, .57, 1.28, 1.35, 1.25),
                (.45, 1.10, .64, 1.32, .94),
                (.65, 1.27, -.72, 1.39, .37),
                (1., 1.32, -1.60, 1.59, .12))
    segment = next((i for i in range(4) if u <= sections[i+1][0]), 3)
    a, b = sections[segment:segment+2]
    t = (u-a[0])/(b[0]-a[0]); t = t*t*(3-2*t)
    y, z, width, drop = [a[k]*(1-t)+b[k]*t for k in range(1, 5)]
    angle = (2*v-1)*1.57
    lateral=max(0.,min(1.,(u-.4)/.25));lateral=lateral*lateral*(3-2*lateral)
    y=y*(1-lateral*math.sin(angle)**2)+.14*lateral*math.sin(angle)**2
    return (width*math.sin(angle), y+.12*math.sin(angle)**2,
            z-drop*(1-math.cos(angle)))


def wrap_description(u, v):
    if not 0 <= u <= 1 or not 0 <= v <= 1:
        raise ValueError('Bounded cloth coordinates required')
    angle = 2*math.pi*u
    front = max(0., -math.cos(angle))
    top = -1.38-.75*front-.22*max(0.,math.cos(angle))+.48*math.sin(angle)*front
    width = 1.10+.33*front
    return angle, top-width*v, front


def pattern():
    import bpy
    import numpy as np
    from mathutils import Vector
    from wardrobe_refinement import tree_for
    hood, hood_faces = foundation.sheet_grid(HEAD_ROWS, HEAD_COLS, head_point)
    # Author neutral contact before physics; never project a solved pose.
    names = ('MF_studio_adult_body', 'MF_fit_tunic_173_visible',
             'MF_171_fitted_sleeve_L_173_visible', 'MF_171_fitted_sleeve_R_173_visible',
             'MF_173_tension_harness_-1', 'MF_173_tension_harness_1',
             'MF_173_static_groom_clearance')
    trees = [tree_for(bpy.data.objects[n]) for n in names]
    ribbon = []
    for row in range(WRAP_ROWS):
        for col in range(WRAP_COLS):
            angle, z, front = wrap_description(row/WRAP_ROWS, (WRAP_COLS-1-col)/(WRAP_COLS-1))
            direction = Vector((math.sin(angle), math.cos(angle), 0))
            origin = Vector((0, .14, z)); extent = 0.
            limit = 2.7 if abs(direction.x) > .75 else 3.2
            for tree in trees:
                start = origin.copy(); travel = 0.
                for _ in range(10):
                    hit, _, _, distance = tree.ray_cast(start, direction, limit-travel)
                    if hit is None: break
                    travel += distance; extent = max(extent, travel)
                    start = hit+direction*1e-5; travel += 1e-5
                    if travel >= limit: break
            if extent <= 0: raise ValueError('Missing outer garment contact')
            # One exterior course with no overlapping terminal layer stack.
            radius = extent+.18+.055*front*math.sin(math.pi*col/(WRAP_COLS-1))
            ribbon.append(tuple(origin+direction*radius))
    # The long headfall is the exterior rear layer. Register its neutral
    # rear corridor to actual groom AND under-wrap, not a guessed ellipse.
    from mathutils.bvhtree import BVHTree
    ribbon_faces=[(i*WRAP_COLS+j,i*WRAP_COLS+j+1,((i+1)%WRAP_ROWS)*WRAP_COLS+j+1,
                   ((i+1)%WRAP_ROWS)*WRAP_COLS+j) for i in range(WRAP_ROWS) for j in range(WRAP_COLS-1)]
    wrap_tree=BVHTree.FromPolygons([Vector(p) for p in ribbon],ribbon_faces)
    for row in range(18,HEAD_ROWS):
        for col in range(HEAD_COLS):
            index=row*HEAD_COLS+col;x,y,z=hood[index]
            outer=y
            rear_trees=[trees[-1]]+([wrap_tree] if abs(x)<1.1 else [])
            for tree in rear_trees:
                start=Vector((x,-.3,z));travel=0.
                for _ in range(12):
                    hit,_,_,distance=tree.ray_cast(start,Vector((0,1,0)),4.-travel)
                    if hit is None:break
                    outer=max(outer,hit.y+.09);travel+=distance+1e-5
                    start=hit+Vector((0,1e-5,0))
                    if travel>=4.:break
            hood[index]=(x,outer,z)
    # Meet the rear superior course along the complete lower hood border.
    # The prior long overlapping hood, joined only at its two ends, formed a
    # closed pocket. No rear clearance plateau or long doubled cape remains.
    join=[]
    for col in range(HEAD_COLS):
        theta=-math.pi/2+math.pi*col/(HEAD_COLS-1)
        wr=int(round((theta%(2*math.pi))/(2*math.pi)*WRAP_ROWS))%WRAP_ROWS
        w=HEAD_COUNT+wr*WRAP_COLS+20
        join.append(w)
        target=Vector(ribbon[w-HEAD_COUNT])
        for row in range(28,HEAD_ROWS):
            k=row*HEAD_COLS+col
            t=(row-28)/(HEAD_ROWS-1-28);t=t*t*(3-2*t)
            hood[k]=tuple(Vector(hood[k]).lerp(target,t))
    # Neutral construction contact must also clear the CROWN, not just rear
    # hair. A pin fixed inside a collision surface cannot be repaired by
    # changing pin stiffness. Never project already simulated frames.
    clearance_trees=(trees[-1],tree_for(bpy.data.objects['MF_continuous_head_neck']))
    def signed_distances(point):
        result=[]
        for tree in clearance_trees:
            hit,normal,_,distance=tree.find_nearest(Vector(point))
            if hit is not None:result.append(float((Vector(point)-hit).dot(normal)))
        return result
    before=[min(signed_distances(p)) for p in hood]
    for index,p in enumerate(hood):
        p=Vector(p)
        # Ray exits from a point within the head avoid oscillating nearest
        # projections between intersecting head and hair exclusion surfaces.
        origin=Vector((0,.25,0));direction=(p-origin).normalized()
        extent=(p-origin).length
        for tree in clearance_trees:
            start=origin.copy();travel=0.
            for _ in range(16):
                hit,normal,_,distance=tree.ray_cast(start,direction,6.-travel)
                if hit is None:break
                travel+=distance;extent=max(extent,travel+.08)
                travel+=1e-5;start=hit+direction*1e-5
                if travel>=6.:break
        p=origin+direction*extent
        for _ in range(20):
            for tree in clearance_trees:
                hit,normal,_,distance=tree.find_nearest(p)
                if hit is not None and (p-hit).dot(normal)<.060:
                    p=hit+normal*.062
        hood[index]=tuple(p)
    after=[min(signed_distances(p)) for p in hood]
    CONSTRUCTION_AUDIT.update({'head_min_signed_before_native':min(before),
        'head_min_signed_after_native':min(after),'head_points_below_060_before':sum(d<.060 for d in before),
        'head_points_below_059_after':sum(d<.059 for d in after),
        'scope':'Nearest outward contact against protected head and actual local groom proxy; neutral pre-dress only'})
    print('179 head construction contact audit',json.dumps(CONSTRUCTION_AUDIT),flush=True)
    if min(after)<.059:raise ValueError('Initial head cloth still intersects contact margin')
    # Carry the outermost sewn border into the course instead of forcing it
    # back inside the clearance surface. Other course vertices remain free.
    for col,w in enumerate(join):
        x,y,z=hood[(HEAD_ROWS-1)*HEAD_COLS+col]
        ribbon[w-HEAD_COUNT]=(x,y,z)
    faces = hood_faces + [tuple(HEAD_COUNT+i for i in f) for f in ribbon_faces]
    points = hood+ribbon
    pins = {}
    # Small stable crown field, not a fully held opening or broad rigid hood.
    for row in (5,8):
        for col in (13,17):
            pins[row*HEAD_COLS+col] = 1.
    for row in range(WRAP_ROWS):
        theta=2*math.pi*row/WRAP_ROWS
        if math.cos(theta)<-.15 or abs(math.sin(theta))>.97:
            pins[HEAD_COUNT+row*WRAP_COLS+20] = 1.
            pins[HEAD_COUNT+row*WRAP_COLS+19] = .7
            pins[HEAD_COUNT+row*WRAP_COLS+18] = .25
    # Sewing edges are local, slightly separated to avoid exact coincidence.
    stitches=[]
    for col,w in enumerate(join):
        h=(HEAD_ROWS-1)*HEAD_COLS+col
        x,y,z=points[h];points[h]=(x,y,z+.012)
        if math.dist(points[h],points[w])>.02:raise ValueError('Nonlocal rear seam')
        stitches.append((h,w))
    p = np.array(points)
    if p.shape != (COUNT,3) or not np.isfinite(p).all(): raise ValueError('Invalid fixed pattern')
    edges = {tuple(sorted((a,b))) for face in faces for a,b in zip(face, face[1:]+face[:1])}
    lengths = np.array([np.linalg.norm(p[a]-p[b]) for a,b in edges])
    if lengths.min() < 1e-5: raise ValueError('Collapsed initial cloth edge')
    return points, faces, pins, stitches


def screens(out, frames=(1,)):
    import bpy
    from mathutils import Vector
    import wardrobe_studio as studio
    from wardrobe_riding_fit import fit_render
    scene = bpy.context.scene
    scene.render.engine='CYCLES'; scene.cycles.device='CPU'; scene.cycles.samples=8
    scene.render.use_persistent_data=True
    for frame in frames:
        scene.frame_set(frame); bpy.context.view_layer.update()
        target = studio.torso_matrix(-2.7) @ Vector((0,.15,-1.7))
        for label,angle in (('front',0),('rear',180),('profile',90),('profile-other',270)):
            fit_render(out,'%s-%03d'%(label,frame),angle,tuple(target),8.,(540,600))


def main():
    import bpy
    import numpy as np
    import wardrobe_studio as studio
    job = json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
    out = validate(job); out.mkdir()
    for name in ('wardrobe_shawl179.py','wardrobe_shawl179_motion.py','wardrobe_motion178.py','wardrobe_motion178_controls.py',
                 'wardrobe_motion178_proof.py','wardrobe_motion178_playback.py'):
        (out/name).write_bytes((ROOT/'scripts'/name).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(foundation.SOURCE),load_ui=False,use_scripts=False)
    foundation.check_protected()
    rig,mats,groom = foundation.clean_foundation()
    if job['operation'].startswith(('solve','windoff')):
        initial=CONTACT_INITIAL if job['operation'].endswith('03') else JOINED_INITIAL if job['operation'].endswith('02') else INITIAL
        with np.load(initial,allow_pickle=False) as record:
            points=record['points'].tolist();faces=[tuple(f) for f in record['faces'].tolist()]
            pins={int(i):float(w) for i,w in zip(record['pin_indices'],record['pin_weights'])}
            stitches=[tuple(e) for e in record['stitches'].tolist()]
        if len(points)!=COUNT or len(faces)!=3120:raise ValueError('Fixed single-course topology mismatch')
    else:points,faces,pins,stitches = pattern()
    np.savez_compressed(out/'constructed-layout.npz',points=np.array(points),faces=np.array(faces),
                        pin_indices=np.array(sorted(pins)),pin_weights=np.array([pins[i] for i in sorted(pins)]),
                        stitches=np.array(stitches))
    if job['operation'].startswith('initial'):
        studio.panel('MF179_continuous_shawl',points,faces,mats['scarf'],.014,1)
        screens(out)
    else:
        from wardrobe_shawl179_motion import simulate
        result=simulate(out,rig,mats,groom,points,faces,pins,stitches,wind_off=job['operation'].startswith('windoff'))
        foundation.check_protected()
        (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
        return
    foundation.check_protected()
    (out/'result.json').write_text(json.dumps({'scope':'Approved single-course initial construction screen only',
        'protected_exact':True,'visual_gate':'NOT_RUN','motion_gate':'NOT_RUN','source_sha256':foundation.SOURCE_SHA,
        'handler_sha256':foundation.digest(Path(__file__)),'logical_garment':'Seamed hood and one continuous outer course',
        'vertices':COUNT,'physics_not_run':True,'construction_contact_audit':CONSTRUCTION_AUDIT},indent=2)+'\n')


if __name__ == '__main__': main()
