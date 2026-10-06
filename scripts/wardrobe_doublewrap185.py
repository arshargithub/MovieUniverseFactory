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
OPERATIONS += ('screen04',)
OPERATIONS += ('cut01',)
OPERATIONS += ('cut02',)
OPERATIONS += ('cut03',)
OPERATIONS += ('restunit01','screen05')
OPERATIONS += ('restunit02',)
OPERATIONS += ('restunit03',)
OPERATIONS += ('cut04',)
OPERATIONS += ('cut05',)
OPERATIONS += ('screen06',)
OPERATIONS += ('intersections01',)
OPERATIONS += ('cut06',)
OPERATIONS += ('cut07',)
OPERATIONS += ('cut08',)
OPERATIONS += ('cut09',)
OPERATIONS += ('screen07',)
OPERATIONS += ('cut10',)
OPERATIONS += ('screen08',)
OPERATIONS += ('screen09',)
OPERATIONS += ('cut11',)
OPERATIONS += ('screen11',)
OPERATIONS += ('cut12',)
OPERATIONS += ('cut13',)
OPERATIONS += ('screen13',)
OPERATIONS += ('headdress01',)
OPERATIONS += ('screen14',)
OPERATIONS += ('headdress02',)
OPERATIONS += ('cut14',)
OPERATIONS += ('screen15',)
OPERATIONS += ('harnesscontact01',)
OPERATIONS += ('proxy03',)
OPERATIONS += ('intersections02',)
OPERATIONS += ('cut15',)
OPERATIONS += ('cut16',)
OPERATIONS += ('cut17',)
OPERATIONS += ('cut18',)
OPERATIONS += ('cut19',)
OPERATIONS += ('screen19',)
OPERATIONS += ('cut20',)
OPERATIONS += ('screen20',)
OPERATIONS += ('headdress03',)
OPERATIONS += ('headdress04',)
OPERATIONS += ('cut21',)
OPERATIONS += ('cut22',)
OPERATIONS += ('screen22',)
OPERATIONS += ('cut23',)
OPERATIONS += ('screen23',)
OPERATIONS += ('intersections03',)
OPERATIONS += ('cut24',)
OPERATIONS += ('screen24',)
OPERATIONS += ('cut25',)
OPERATIONS += ('screen25',)
OPERATIONS += ('motionprep01',)
OPERATIONS += ('motion01','motionoff01')
OPERATIONS += ('motion02',)
OPERATIONS += ('motionreview02',)
OPERATIONS += ('integration01',)
OPERATIONS += ('gaze01',)
OPERATIONS += ('upper01',)
OPERATIONS += ('upper02',)
OPERATIONS += ('upper03',)
OPERATIONS += ('upper04',)
OPERATIONS += ('motionprep02',)
OPERATIONS += ('holdcheck01','motion03','motionoff03')
OPERATIONS += ('horseprobe01',)
OPERATIONS += ('motionreview03',)
OPERATIONS += ('horsecache01',)
OPERATIONS += ('riding01',)
OPERATIONS += ('riding02',)
OPERATIONS += ('riding03',)
OPERATIONS += ('riding04',)
OPERATIONS += ('riding05',)
OPERATIONS += ('gripcheck01',)
OPERATIONS += ('gripcheck02',)
OPERATIONS += ('gripcheck03',)
OPERATIONS += ('riding06',)
OPERATIONS += ('gallopprep01',)
OPERATIONS += ('gallopcloth01','gallopoff01')
OPERATIONS += ('gallopprep02',)
OPERATIONS += ('gallopprep03',)
OPERATIONS += ('gallopscreen01',)
OPERATIONS += ('gallopcloth02',)
OPERATIONS += ('gallopscreen02','gallopscreen03')
OPERATIONS += ('gallopcontact01',)
OPERATIONS += ('gallopcontact02',)
OPERATIONS += ('gallopcontact03',)
OPERATIONS += ('gallopcontact04',)
OPERATIONS += ('gallopcontact05',)
OPERATIONS += ('gallopcontact06',)
OPERATIONS += ('gallopfidelity01',)
OPERATIONS += ('gallopcontact07','gallopfidelity02')
OPERATIONS += ('gallopstructure01',)
OPERATIONS += ('gallopcontact08',)
OPERATIONS += ('gallopstructure02',)
OPERATIONS += ('convexcontact01',)
OPERATIONS += ('convexcontact02',)
OPERATIONS += ('convexcontact03',)
OPERATIONS += ('riding07',)
OPERATIONS += ('convexsource01',)
OPERATIONS += ('convexscreen01',)
OPERATIONS += ('gallopcloth03','gallopoff03')
OPERATIONS += ('headdress05',)
OPERATIONS += ('headscreen05',)
OPERATIONS += ('gallopcloth04','gallopoff04')
OPERATIONS += ('regionalreview04',)
OPERATIONS += ('headdress06',)
OPERATIONS += ('gallopcloth05','gallopoff05')
OPERATIONS += ('beltfit01',)
OPERATIONS += ('regionalreview05',)
OPERATIONS += ('finishreview01',)
OPERATIONS += ('beltinspect01',)
OPERATIONS += ('beltfit02',)
OPERATIONS += ('shotlayout01',)
OPERATIONS += ('shotmotion01',)
OPERATIONS += ('exitaudit01',)
OPERATIONS += ('seal01',)
OPERATIONS += ('verify01',)
HEAD = base.BASE / 'wardrobe180-xpbdhead08/trajectory.npz'
HEAD_SHA = '55ce2f99edfbb45a7cf8a5898be31caa1f20bd7da3bb2ae2be9c43e49d7095e8'


def validate(job):
    if not isinstance(job, dict) or set(job) != {'operation'} or job['operation'] not in OPERATIONS:
        raise ValueError('Fixed structured operation required')
    inputs=[(base.SOURCE,base.SOURCE_SHA)]
    # These handlers bind their own integrated source/current caches. Do not
    # retain an obsolete experimental head solve as an accidental dependency
    # of merely viewing, checking or packaging the current character.
    if job['operation'] not in ('shotlayout01','shotmotion01','exitaudit01','seal01','verify01'):
        inputs.append((HEAD,HEAD_SHA))
    for path, sha in inputs:
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


def screen(out):
    import bpy
    import wardrobe_studio as studio
    from wardrobe_motion178_proof import dress_actor
    from wardrobe_underarm179_repair import repair
    from wardrobe_shawl179 import screens
    source=base.BASE/('wardrobe185-cut03/trajectory.npz' if out.name.endswith('screen05') else 'wardrobe185-isolate04/envelope_clear.npz')
    sha='a5eb72e643d31e76197cb6bf92387e3bb0aa3cba3dd112ab74f4169985d27ac6' if out.name.endswith('screen05') else '08d85408c30497043c9d05ab2d8782579219d6317f36b272f0f397dbf113a2c1'
    if out.name.endswith('screen06'):
        source=base.BASE/'wardrobe185-cut05/trajectory.npz';sha='b58d4b35d26c686014565630ed7debdd18a5ed77fb095e6436901cadc405ba3a'
    if out.name.endswith('screen07'):
        source=base.BASE/'wardrobe185-cut09/trajectory.npz';sha='8c49f81757a678d4f0db3dd24ff8c7f1d5268f2c9fc8e88c27f5b0e24b6f7762'
    if out.name.endswith(('screen08','screen09')):
        source=base.BASE/'wardrobe185-cut10/trajectory.npz';sha='50d88a05d9652c7e368c738406553d89d9bafea7d1c9cf22b04f89b7eff95aaf'
    if out.name.endswith('screen11'):
        source=base.BASE/'wardrobe185-cut11/trajectory.npz';sha='65ab929b2b6309f1223446995b2ff6efee290ab7b8e1346eb906a228f5effb80'
    if out.name.endswith('screen13'):
        source=base.BASE/'wardrobe185-cut13/trajectory.npz';sha='44751128314f25fd6b9900efd38e6380d4fbd42955c78fee73dc5f379942a9d9'
    if out.name.endswith('screen14'):
        source=base.BASE/'wardrobe185-headdress01/trajectory.npz';sha='4418bd6dae0b23dc3ddee0f517fada27e504eb60af01d6b9585d33f1487cf613'
    if out.name.endswith('screen15'):
        source=base.BASE/'wardrobe185-cut14/trajectory.npz';sha='082cc13896e7c8991c4443b60a817e6d189de9f477606a2f1525736735a035bb'
    if out.name.endswith('screen19'):
        source=base.BASE/'wardrobe185-cut19/trajectory.npz';sha='a44440025cf5957ee213ca04f02888f6f86fbeb28fa2d07fdb5fccfbb8c7abf4'
    if out.name.endswith('screen20'):
        source=base.BASE/'wardrobe185-cut20/trajectory.npz';sha='eb63b6c9371ae9d7c1ade8020defd15ca4a455bd03c9fd06f49d679891fdc960'
    if out.name.endswith('screen22'):
        source=base.BASE/'wardrobe185-cut22/trajectory.npz';sha='0f5d77429db1399008ddf7ebc7a7d4d0b4e0022fd314a63678313ec9e7cf22cf'
    if out.name.endswith('screen23'):
        source=base.BASE/'wardrobe185-cut23/trajectory.npz';sha='2f5d1c4a9c0a0b2052aed1d9be891e3fd3a0d5d1be2133d2f77640825ce93d66'
    if out.name.endswith('screen24'):
        source=base.BASE/'wardrobe185-cut24/trajectory.npz';sha='16d36ab0cd4617f7c3f2614c7b25539b80b6ea9467516524576fc5c3201b3882'
    if out.name.endswith('screen25'):
        source=base.BASE/'wardrobe185-cut25/trajectory.npz';sha='01b39b795fa57488cef9b0841a03c897446b29f0c63b8261d02e831ce6aaab45'
    if base.digest(source)!=sha:raise ValueError('Screen input changed')
    with np.load(source,allow_pickle=False) as d:points=d['frames'][-1];faces=d['faces'];counts=d['counts'];source_frame=len(d['frames'])
    from mathutils.bvhtree import BVHTree
    trees=[];offset=0
    for count in counts:
        f=faces[(faces[:,0]>=offset)&(faces[:,0]<offset+count)]
        trees.append(BVHTree.FromPolygons(points.tolist(),f.tolist()));offset+=count
    overlaps={str((i,j)):len(trees[i].overlap(trees[j])) for i in range(len(trees)) for j in range(i+1,len(trees))}
    (out/'layer-intersections.json').write_text(json.dumps(overlaps,indent=2)+'\n')
    bpy.ops.wm.open_mainfile(filepath=str(base.SOURCE),load_ui=False,use_scripts=False)
    base.check_protected();rig,mats,_=base.clean_foundation();dress_actor(rig);repair(rig,'repair04')
    offset=0
    for k,(count,rgb) in enumerate(zip(counts,((.06,.10,.18),(.16,.30,.27),(.27,.17,.08)))):
        f=faces[(faces[:,0]>=offset)&(faces[:,0]<offset+count)]-offset
        studio.panel('MF185_screen_'+str(k),points[offset:offset+count].tolist(),f.tolist(),color('screen'+str(k),rgb),.012,1)
        offset+=count
    if out.name.endswith('screen09'):
        for ob in bpy.data.objects:
            if ob.name.startswith('MF185_screen_'):ob.hide_render=True
        proxy=base.BASE/'wardrobe185-proxy02/proxy.npz'
        if base.digest(proxy)!='19cce587247a325e2f0b081f49e14eb0a40bf6c3364896a327af4639a6d4f7eb':raise ValueError('Proxy changed')
        with np.load(proxy,allow_pickle=False) as d:cp=d['points'];cf=d['faces']
        mesh=bpy.data.meshes.new('Diagnostic collision envelope');mesh.from_pydata(cp.tolist(),[],cf.tolist());mesh.update()
        ob=bpy.data.objects.new('MF185_contact_screen',mesh);bpy.context.scene.collection.objects.link(ob)
        ob.data.materials.append(color('Contact envelope',(.30,.23,.18)))
        for poly in ob.data.polygons:poly.use_smooth=True
    screens(out,(1,));base.check_protected()
    if out.name.endswith(('screen23','screen24','screen25')):
        for ob in bpy.data.objects:
            if ob.name.startswith('MF185_screen_'):
                ob.data.materials.clear();ob.data.materials.append(mats['scarf'])
        finished=out/'material-control';finished.mkdir();screens(finished,(1,));base.check_protected()
    if out.name.endswith(('screen24','screen25')):
        evaluated_trees=[]
        for k in range(3):
            ob=bpy.data.objects['MF185_screen_'+str(k)]
            states=[(m,m.show_viewport) for m in ob.modifiers if m.type=='SOLIDIFY']
            for m,_ in states:m.show_viewport=False
            bpy.context.view_layer.update();ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
            mesh.calc_loop_triangles()
            evaluated_trees.append(BVHTree.FromPolygons([list(ob.matrix_world@v.co) for v in mesh.vertices],[list(t.vertices) for t in mesh.loop_triangles],all_triangles=True))
            ev.to_mesh_clear()
            for m,value in states:m.show_viewport=value
        (out/'evaluated-midsurface-intersections.json').write_text(json.dumps({str((i,j)):len(evaluated_trees[i].overlap(evaluated_trees[j])) for i in range(3) for j in range(i+1,3)},indent=2)+'\n')
    if out.name.endswith('screen11'):
        for ob in bpy.data.objects:
            if ob.name.startswith('MF185_screen_'):ob.hide_render=True
        control=out/'uncovered';control.mkdir();screens(control,(1,));base.check_protected()
    (out/'result.json').write_text(json.dumps({'source':str(source),'source_frame':source_frame,'protected_exact':True,'visual_gate':'NOT_RUN'},indent=2)+'\n')


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
    elif job['operation'] in ('proxy01','proxy02','proxy03'):
        from wardrobe185_proxy import run
        run(out)
    elif job['operation'].startswith('screen'):screen(out)
    elif job['operation'].startswith('cut'):
        from wardrobe185_cut_solve import run
        run(out)
    elif job['operation'] in ('restunit01','restunit02','restunit03'):
        from wardrobe185_rest_unit import run
        run(out)
    elif job['operation'].startswith('intersections'):
        from wardrobe185_intersections import run
        run(out)
    elif job['operation']=='headscreen05':
        from wardrobe185_head_dress import screen as head_screen
        head_screen(out)
    elif job['operation'].startswith('headdress'):
        from wardrobe185_head_dress import run
        run(out)
    elif job['operation']=='harnesscontact01':
        from wardrobe185_harness_contact import run
        run(out)
    elif job['operation'] in ('motionprep01','motionprep02'):
        from wardrobe185_motion import prep
        prep(out)
    elif job['operation'] in ('motion01','motion02','motionoff01','holdcheck01','motion03','motionoff03'):
        from wardrobe185_motion import simulate
        simulate(out)
    elif job['operation'] in ('upper01','upper02','upper03','upper04'):
        from wardrobe185_integration import garment_screen
        garment_screen(out)
    elif job['operation']=='gaze01':
        from wardrobe185_integration import gaze_screen
        gaze_screen(out)
    elif job['operation']=='integration01':
        from wardrobe185_integration import audit
        audit(out)
    elif job['operation']=='horseprobe01':
        from wardrobe185_horse import probe
        probe(out)
    elif job['operation']=='horsecache01':
        from wardrobe185_horse import gait_cache
        gait_cache(out)
    elif job['operation'] in ('riding01','riding02','riding03','riding04','riding05','riding06','riding07'):
        from wardrobe185_riding import preview
        preview(out)
    elif job['operation']=='convexscreen01':
        from wardrobe185_convex import screen as convex_screen
        convex_screen(out)
    elif job['operation'] in ('convexcontact01','convexcontact02','convexcontact03','convexsource01'):
        from wardrobe185_convex import capture
        capture(out)
    elif job['operation'] in ('gallopstructure01','gallopstructure02'):
        from wardrobe185_contact import structure
        structure(out)
    elif job['operation'] in ('gallopfidelity01','gallopfidelity02'):
        from wardrobe185_contact import fidelity
        fidelity(out)
    elif job['operation'] in ('gallopcontact02','gallopcontact03','gallopcontact04','gallopcontact05','gallopcontact06','gallopcontact07','gallopcontact08'):
        from wardrobe185_contact import capture
        capture(out)
    elif job['operation']=='gallopcontact01':
        from wardrobe185_gallop import contact_audit
        contact_audit(out)
    elif job['operation']=='shotlayout01':
        from wardrobe185_shot import layout as shot_layout
        shot_layout(out)
    elif job['operation']=='shotmotion01':
        from wardrobe185_shot import motion as shot_motion
        shot_motion(out)
    elif job['operation']=='exitaudit01':
        from wardrobe185_exit_audit import run as exit_audit
        exit_audit(out)
    elif job['operation']=='seal01':
        from wardrobe185_delivery import seal
        seal(out)
    elif job['operation']=='verify01':
        from wardrobe185_delivery import verify
        verify(out)
    elif job['operation']=='beltinspect01':
        from wardrobe185_belt import inspect as belt_inspect
        belt_inspect(out)
    elif job['operation'] in ('beltfit01','beltfit02'):
        from wardrobe185_belt import screen as belt_screen
        belt_screen(out)
    elif job['operation'] in ('gallopscreen02','gallopscreen03'):
        from wardrobe185_gallop import rescreen
        rescreen(out)
    elif job['operation'] in ('gallopscreen01','regionalreview04','regionalreview05','finishreview01'):
        from wardrobe185_gallop import screen as gallop_screen
        gallop_screen(out)
    elif job['operation'] in ('gallopcloth01','gallopoff01','gallopcloth02','gallopcloth03','gallopoff03','gallopcloth04','gallopoff04','gallopcloth05','gallopoff05'):
        from wardrobe185_motion import simulate
        simulate(out)
    elif job['operation'] in ('gallopprep01','gallopprep02','gallopprep03'):
        from wardrobe185_gallop import prep as gallop_prep
        gallop_prep(out)
    elif job['operation'] in ('gripcheck01','gripcheck02','gripcheck03'):
        from wardrobe185_grip import audit
        audit(out)
    elif job['operation'] in ('motionreview02','motionreview03'):
        from wardrobe185_motion import screen as motion_screen
        motion_screen(out)
    else:raise ValueError('Validated operation has no implementation')


if __name__=='__main__':main()
