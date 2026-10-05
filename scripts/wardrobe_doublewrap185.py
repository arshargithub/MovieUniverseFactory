"""Fixed, reviewed double-wrap construction and contact controls.

No runtime code, arbitrary paths, provider calls or protected-data writes.
Coarse section authoring is not automatically a qualified garment.
"""
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import wardrobe_motion178 as base

OPERATIONS = ('route01', 'contact01', 'route02', 'contact02', 'contactoff02', 'contact03', 'contactoff03', 'route03')
OPERATIONS += ('contact04', 'contact05', 'contactoff05', 'settle01')
OPERATIONS += ('fitcheck01', 'settle02')
OPERATIONS += ('fitcheck02',)
OPERATIONS += ('volumecheck01',)
OPERATIONS += ('settle03',)
OPERATIONS += ('isolate01',)
OPERATIONS += ('isolate02',)
OPERATIONS += ('isolate03',)
OPERATIONS += ('proxy01',)
OPERATIONS += ('proxy02',)
OPERATIONS += ('isolate04',)
HEAD = base.BASE / 'wardrobe180-xpbdhead08/trajectory.npz'
HEAD_SHA = '55ce2f99edfbb45a7cf8a5898be31caa1f20bd7da3bb2ae2be9c43e49d7095e8'


def validate(job):
    if not isinstance(job, dict) or set(job) != {'operation'} or job['operation'] not in OPERATIONS:
        raise ValueError('Fixed structured operation required')
    for path, sha in ((base.SOURCE, base.SOURCE_SHA), (HEAD, HEAD_SHA)):
        if path.is_symlink() or base.digest(path) != sha:
            raise ValueError('Protected or diagnostic input changed')
    out = base.BASE / ('wardrobe185-' + job['operation'])
    if out.exists() or out.is_symlink():
        raise ValueError('Preserve previous evidence')
    return out


def periodic_section(controls, u):
    """Uniform cubic section interpolation; no nearest-body projection."""
    controls = np.asarray(controls, dtype=float)
    pos = (u % 1) * len(controls)
    i = int(pos); t = pos-i
    a,b,c,d = (controls[k % len(controls)] for k in (i-1,i,i+1,i+2))
    return .5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t)


def course(layer, rows=96, cols=17, revised=False):
    if layer not in (0,1):
        raise ValueError('Two authored courses only')
    top = np.array([(0,1.63,-1.30),(.90,1.43,-1.40),(1.10,.12,-1.62),
                    (1.08,-.85,-1.95),(0,-1.31,-2.60),(-1.10,-.86,-2.27),
                    (-1.17,.12,-1.76),(-.94,1.43,-1.36)])
    bottom = np.array([(0,1.75,-2.18),(1.40,1.56,-2.25),(1.80,.14,-2.20),
                       (1.67,-1.05,-2.85),(0,-1.53,-3.48),(-1.68,-1.08,-3.04),
                       (-1.84,.13,-2.33),(-1.43,1.58,-2.24)])
    if revised:
        # The actual headfall extends past y1.8 at the nape. Explicit rear
        # sections must encompass it; do not shrink arbitrary cloth to skin.
        top[[0,1,7],1]=[1.96,1.72,1.72]
        bottom[[0,1,7],1]=[1.91,1.83,1.83]
        top[[1,7],0]=[1.21,-1.21];bottom[[1,7],0]=[1.54,-1.54]
        top[[2,6],2]+=.58;bottom[[2,6],2]+=.42
        top[[2,6],0]=[1.25,-1.25]
        top[[3,5],2]+=.28;bottom[[3,5],2]+=.13
    if revised==3:
        def point(u,v):
            a=periodic_section(top,u);b=periodic_section(bottom,u)
            return a*(1-v)+b*v
        p=[];f=[]
        for i in range(rows):
            u=i/rows;theta=math.tau*u
            shift=layer*(.48*math.cos(theta)**2+.10*math.sin(theta)*max(0.,-math.cos(theta)))
            for j in range(cols):
                v=j/(cols-1)+shift
                tangent=point(u+.0001,v)-point(u-.0001,v)
                across=point(u,1)-point(u,0)
                normal=np.cross(tangent,across);normal/=np.linalg.norm(normal)
                p.append(point(u,v)+normal*(.08*layer))
        for i in range(rows):
            for j in range(cols-1):f.append((i*cols+j,((i+1)%rows)*cols+j,((i+1)%rows)*cols+j+1,i*cols+j+1))
        return np.asarray(p),np.asarray(f)
    if layer:
        dz = np.array([-.48,-.32,.035,-.52,-.65,-.28,.035,-.30])
        top[:,2] += dz; bottom[:,2] += dz
        for a in (top,bottom):
            a[:,0] *= 1.035
            a[:,1] += np.where(a[:,1]>.4,.13,np.where(a[:,1]<-.4,-.12,0))
    p=[]; f=[]
    for i in range(rows):
        u=i/rows; a=periodic_section(top,u); b=periodic_section(bottom,u)
        for j in range(cols):
            v=j/(cols-1)
            p.append(a*(1-v)+b*v)
    for i in range(rows):
        for j in range(cols-1):
            f.append((i*cols+j,((i+1)%rows)*cols+j,((i+1)%rows)*cols+j+1,i*cols+j+1))
    return np.asarray(p),np.asarray(f)


def color(name, rgb):
    import bpy
    m=bpy.data.materials.new(name);m.diffuse_color=(*rgb,1);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*rgb,1)
    p.inputs['Roughness'].default_value=.8
    return m


def route(out):
    import bpy
    import wardrobe_studio as studio
    from wardrobe_motion178_proof import dress_actor
    from wardrobe_underarm179_repair import repair
    from wardrobe_shawl179 import screens
    bpy.ops.wm.open_mainfile(filepath=str(base.SOURCE),load_ui=False,use_scripts=False)
    base.check_protected()
    rig,mats,_=base.clean_foundation();dress_actor(rig);repair(rig,'repair04')
    with np.load(HEAD,allow_pickle=False) as d:
        hp=d['frames'][-1].copy();hf=d['faces'].copy()
    studio.panel('MF185_headfall',hp.tolist(),hf.tolist(),color('headfall',(.06,.10,.18)),.012,1)
    payload={'head':hp,'head_faces':hf}
    for layer,rgb in enumerate(((.16,.30,.27),(.27,.17,.08))):
        p,f=course(layer,revised=3 if out.name.endswith('03') else out.name.endswith('02'))
        ob=studio.panel('MF185_course_'+str(layer),p.tolist(),f.tolist(),color('course'+str(layer),rgb),.012,1)
        ob['qualification']='Coarse route, static and unqualified'
        payload['course'+str(layer)]=p;payload['faces'+str(layer)]=f
    np.savez_compressed(out/'route.npz',**payload)
    screens(out,(1,))
    base.check_protected()
    (out/'result.json').write_text(json.dumps({'protected_exact':True,'visual_gate':'NOT_RUN',
        'motion_gate':'NOT_RUN','representation':'Coarse section-authored layered courses, no simulation',
        'source_sha256':base.SOURCE_SHA,'head_input_sha256':HEAD_SHA},indent=2)+'\n')


def cloth_settings(ob, area, collection=None):
    mod=ob.modifiers.new('Legacy cloth with self contact','CLOTH')
    s=mod.settings;s.quality=12;s.mass=.24*area/len(ob.data.vertices)
    s.tension_stiffness=30;s.compression_stiffness=30;s.shear_stiffness=15
    s.bending_stiffness=.06;s.tension_damping=8;s.compression_damping=8
    s.shear_damping=8;s.air_damping=2;s.vertex_group_mass='support'
    c=mod.collision_settings;c.use_collision=collection is not None
    if collection is not None:c.collection=collection
    c.use_self_collision=True;c.self_distance_min=.002;c.distance_min=.002
    c.collision_quality=4;c.self_friction=5
    mod.point_cache.frame_start=1;mod.point_cache.frame_end=72
    return mod


def contact(out):
    """Two overlapping cloth layers, animated held edge, closed moving support.

    One mesh uses self collision between disconnected panels. This control
    only qualifies the tested contact setup, not whole-costume appearance.
    """
    import bpy
    from mathutils import Vector
    bpy.ops.wm.read_factory_settings(use_empty=True)
    p=[];f=[];rows=17;cols=17;count=rows*cols
    for layer in range(2):
        q,g=base.sheet_grid(rows,cols,lambda u,v:(-.22+.44*u,-.25+.5*v,.12+.022*layer))
        offset=len(p);p.extend(q);f.extend(tuple(k+offset for k in face) for face in g)
    mesh=bpy.data.meshes.new('contact');mesh.from_pydata(p,[],f);mesh.update()
    ob=bpy.data.objects.new('contact',mesh);bpy.context.scene.collection.objects.link(ob)
    pin=ob.vertex_groups.new(name='support')
    revised=out.name.endswith(('02','03','04','05'))
    if revised:
        pin.add(list(range(count)),1.,'REPLACE')
    else:
        for layer in range(2):
            for j in range(cols):pin.add([layer*count+j],1.,'REPLACE')
    ob.shape_key_add(name='Basis');key=ob.shape_key_add(name='Held edge travel')
    for v in key.data:v.co.x+=.08
    key.value=0;key.keyframe_insert(data_path='value',frame=1)
    key.value=0;key.keyframe_insert(data_path='value',frame=24)
    key.value=1;key.keyframe_insert(data_path='value',frame=60)
    bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,-.015))
    support=bpy.context.object;support.scale=(1,1,.03)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    support.modifiers.new('Contact','COLLISION');support.collision.thickness_outer=.002
    domain=bpy.data.collections.new('Contacts');bpy.context.scene.collection.children.link(domain);domain.objects.link(support)
    mod=cloth_settings(ob,.44*.5*2,domain)
    if revised:
        mod.settings.bending_stiffness=.005
        mod.collision_settings.use_self_collision='off' not in out.name
    if out.name.endswith(('03','04')):
        mod.settings.air_damping=.003
    if out.name.endswith('04'):
        mod.settings.quality=48
        mod.collision_settings.collision_quality=8
    if out.name.endswith('05'):
        # Computational profile: not calibrated textile density. The legacy
        # self-contact impulse implementation does not mass-weight responses.
        mod.settings.mass=.3
        mod.settings.air_damping=.2
    scene=bpy.context.scene;scene.render.fps=24;scene.gravity=(0,0,-9.81)
    frames=[]
    for frame in range(1,73):
        scene.frame_set(frame);bpy.context.view_layer.update()
        ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh()
        q=np.array([v.co[:] for v in m.vertices]);ev.to_mesh_clear()
        if q.shape!=(2*count,3) or not np.isfinite(q).all():raise ValueError('Invalid cloth trajectory')
        frames.append(q)
        if frame%12==0:print('185 contact',frame,flush=True)
    np.savez_compressed(out/'trajectory.npz',points=np.array(p),faces=np.array(f),frames=np.array(frames))
    # Corresponding points are a screening measure, not exhaustive contact.
    q=frames[-1];delta=q[count:,2]-q[:count,2]
    free=[i*cols+j for i in range(4,rows-2) for j in range(2,cols-2)]
    result={'mass_per_vertex':mod.settings.mass,'self_collision':mod.collision_settings.use_self_collision,'frames':72,
        'layer_vertical_separation_quantiles':np.quantile(delta[free],[0,.1,.5,.9,1]).tolist(),
        'minimum_height':float(q[:,2].min()),'numeric_finite':True,'visual_gate':'NOT_RUN',
        'scope':'Free upper panel falling onto held moving lower panel' if revised else 'Two held overlapping panels; insufficient contact stress test'}
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result),flush=True)


def main():
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
    out=validate(job);out.mkdir()
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    if job['operation'].startswith('route'):route(out)
    elif job['operation'].startswith('contact'):contact(out)
    elif job['operation'] in ('settle01', 'fitcheck01', 'fitcheck02', 'settle02','settle03'):
        from wardrobe_doublewrap185_solve import settle
        settle(out)
    elif job['operation']=='volumecheck01':
        from wardrobe_doublewrap185_solve import volumecheck
        volumecheck(out)
    elif job['operation'] in ('isolate01','isolate02','isolate03','isolate04'):
        from wardrobe185_isolate import run
        run(out)
    elif job['operation'] in ('proxy01','proxy02'):
        from wardrobe185_proxy import run
        run(out)


if __name__=='__main__':main()
