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
OPERATIONS = ('initial01', 'solve01', 'windoff01')
HEAD_ROWS, HEAD_COLS, WRAP_ROWS, WRAP_COLS = 41, 31, 97, 21
HEAD_COUNT = HEAD_ROWS * HEAD_COLS
COUNT = HEAD_COUNT + WRAP_ROWS * WRAP_COLS


def validate(job):
    if not isinstance(job, dict) or set(job) != {'operation'} or job['operation'] not in OPERATIONS:
        raise ValueError('Fixed approved shawl operation only')
    if foundation.SOURCE.is_symlink() or foundation.digest(foundation.SOURCE) != foundation.SOURCE_SHA:
        raise ValueError('Protected foundation mismatch')
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
                (1., 1.32, -3.30, 1.59, .12))
    segment = next((i for i in range(4) if u <= sections[i+1][0]), 3)
    a, b = sections[segment:segment+2]
    t = (u-a[0])/(b[0]-a[0]); t = t*t*(3-2*t)
    y, z, width, drop = [a[k]*(1-t)+b[k]*t for k in range(1, 5)]
    angle = (2*v-1)*1.57
    return (width*math.sin(angle), y+.12*math.sin(angle)**2,
            z-drop*(1-math.cos(angle)))


def wrap_description(u, v):
    if not 0 <= u <= 1 or not 0 <= v <= 1:
        raise ValueError('Bounded cloth coordinates required')
    angle = 2*math.pi*u
    front = max(0., -math.cos(angle))
    top = -1.76-.50*front+.28*math.sin(angle)*front
    width = .65+.92*front
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
            angle, z, front = wrap_description(row/(WRAP_ROWS-1), (WRAP_COLS-1-col)/(WRAP_COLS-1))
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
            radius = extent+.055+.055*front*math.sin(math.pi*col/(WRAP_COLS-1))
            ribbon.append(tuple(origin+direction*radius))
    faces = hood_faces + [tuple(HEAD_COUNT+i for i in f) for f in
                         foundation.sheet_grid(WRAP_ROWS, WRAP_COLS, lambda u,v:(u,v,0))[1]]
    points = hood+ribbon
    pins = {}
    # Small stable crown field, not a fully held opening or broad rigid hood.
    for row in range(3, 17):
        for col in range(10, 21):
            pins[row*HEAD_COLS+col] = 1. if 12 <= col <= 18 else .6
    for row in range(WRAP_ROWS):
        pins[HEAD_COUNT+row*WRAP_COLS+20] = 1.
        pins[HEAD_COUNT+row*WRAP_COLS+19] = .7
        pins[HEAD_COUNT+row*WRAP_COLS+18] = .25
    # Two small shoulder seam zones physically join the hood to the course.
    stitches = []
    for head_col, wrap_row in ((0, 72), (30, 24)):
        for offset in (-1,0,1):
            h = 28*HEAD_COLS+head_col
            w = HEAD_COUNT+(wrap_row+offset)*WRAP_COLS+20
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
    for name in ('wardrobe_shawl179.py','wardrobe_motion178.py','wardrobe_motion178_controls.py',
                 'wardrobe_motion178_proof.py','wardrobe_motion178_playback.py'):
        (out/name).write_bytes((ROOT/'scripts'/name).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(foundation.SOURCE),load_ui=False,use_scripts=False)
    foundation.check_protected()
    rig,mats,groom = foundation.clean_foundation()
    points,faces,pins,stitches = pattern()
    np.savez_compressed(out/'constructed-layout.npz',points=np.array(points),faces=np.array(faces),
                        pin_indices=np.array(sorted(pins)),pin_weights=np.array([pins[i] for i in sorted(pins)]),
                        stitches=np.array(stitches))
    if job['operation']=='initial01':
        studio.panel('MF179_continuous_shawl',points,faces,mats['scarf'],.014,1)
        screens(out)
    else:
        raise ValueError('Motion requires inspected hash-bound construction before dispatch')
    foundation.check_protected()
    (out/'result.json').write_text(json.dumps({'scope':'Approved single-course initial construction screen only',
        'protected_exact':True,'visual_gate':'NOT_RUN','motion_gate':'NOT_RUN','source_sha256':foundation.SOURCE_SHA,
        'handler_sha256':foundation.digest(Path(__file__)),'logical_garment':'Seamed hood and one continuous outer course',
        'vertices':COUNT,'physics_not_run':True},indent=2)+'\n')


if __name__ == '__main__': main()
