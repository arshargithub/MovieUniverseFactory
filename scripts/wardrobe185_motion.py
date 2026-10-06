"""Fixed coordinated wardrobe diagnostic; not certified trailer gallop.

Build a small rig/contact library so native cloth need not evaluate the full
protected groom and character during every solver substep.
"""
import json
from pathlib import Path
import numpy as np

SCALE=.12292759120464325
PROXY_SHA='566257ec73b43170c6ad5414b8936ef537b7373b2d57de967286f13e3f091029'


def schedule(frame):
    from wardrobe_motion178_controls import phase,smooth
    p=phase(frame-72,neutral_entry=True)
    p['legs']=smooth((frame-97)/48)
    return p


def animate(rig):
    import bpy
    from mathutils import Matrix,Quaternion,Vector
    from wardrobe_riding_fit import riding_pose
    from wardrobe_refinement import neutral
    from wardrobe_motion178_controls import render_geometry_paused
    with render_geometry_paused():
        rig.animation_data_clear();riding_pose(rig,1.)
        goals={b.name:b.matrix_basis.decompose() for b in rig.pose.bones}
        neutral(rig);identity=Quaternion((1,0,0,0))
        for frame in list(range(1,361,4))+[360]:
            bpy.context.scene.frame_set(frame);p=schedule(frame)
            for bone in rig.pose.bones:
                t=p['legs'] if bone.name.startswith(('thigh.','shin.','foot.','toe.')) else p['lean']
                loc,rot,scale=goals[bone.name]
                bone.rotation_mode='QUATERNION';bone.location=loc*t
                bone.rotation_quaternion=identity.slerp(rot,t)
                if bone.name in ('MF185_neck','MF185_head'):
                    import math
                    angle=-18 if bone.name=='MF185_neck' else -12
                    bone.rotation_quaternion=Quaternion((1,0,0),math.radians(angle)*p['lean'])
                bone.scale=Vector((1,1,1)).lerp(scale,t)
                if bone.name=='pelvis':bone.location.z+=p['bob']
                if bone.name=='chest':bone.rotation_quaternion=Quaternion((0,0,1),p['chest_yaw'])@bone.rotation_quaternion
                for prop in ('location','rotation_quaternion','scale'):bone.keyframe_insert(data_path=prop,frame=frame)
        bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
        for bone in rig.pose.bones:
            if max(abs(bone.matrix_basis[i][j]-Matrix.Identity(4)[i][j]) for i in range(4) for j in range(4))>1e-5:
                raise ValueError('Motion does not start at admitted rest')


def prep(out):
    import bpy
    from mathutils import Matrix
    import wardrobe_motion178 as base
    import wardrobe_motion178_controls as controls
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    path=base.BASE/'wardrobe185-proxy03/proxy.npz'
    if base.digest(path)!=PROXY_SHA:raise ValueError('Contact changed')
    with np.load(path,allow_pickle=False) as d:p=d['points'];f=d['faces']
    bpy.ops.wm.open_mainfile(filepath=str(base.SOURCE),load_ui=False,use_scripts=False)
    base.check_protected();rig,_,_=base.clean_foundation()
    gaze=out.name.endswith('motionprep02')
    if gaze:
        from wardrobe185_integration import head_control
        head_control(rig)
    sample=controls.body_weight_sampler()
    animate(rig)
    canonical=controls.canonical_rig(rig,SCALE)
    mesh=bpy.data.meshes.new('185 motion contact');mesh.from_pydata((p*SCALE).tolist(),[],f.tolist());mesh.update()
    contact=bpy.data.objects.new('MF178_support_185_contact',mesh);bpy.context.scene.collection.objects.link(contact)
    def weights(point):
        if gaze:
            from wardrobe_motion178_controls import smooth
            values=sample(point)
            if point.z>-1.:return {'MF185_head':1.}
            hair=smooth((point.z+2.3)/.4)*smooth((point.y-.65)/.25)*smooth((1.6-abs(point.x))/.25)
            values={name:w*(1-hair) for name,w in values.items()}
            values['MF185_head']=values.get('MF185_head',0)+hair
            return values
        if point.z>-.8 or (point.z>-2.3 and point.y>.8 and abs(point.x)<1.6):return {'chest':1.}
        return sample(point)
    controls.bind(contact,canonical,weights,scale=SCALE)
    audit={};samples=[]
    with controls.render_geometry_paused():
        for frame in (1,169,193,217,289,360):
            bpy.context.scene.frame_set(frame);bpy.context.view_layer.update()
            ev=contact.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh()
            q=np.array([v.co[:] for v in m.vertices])/SCALE;ev.to_mesh_clear()
            if q.shape!=p.shape or not np.isfinite(q).all():raise ValueError('Invalid posed contact')
            if frame==1 and np.max(abs(q-p))>1e-5:raise ValueError('Initial collider differs from admitted geometry')
            expected=Matrix.Scale(SCALE,4)@rig.matrix_world@rig.pose.bones['chest'].matrix
            actual=canonical.matrix_world@canonical.pose.bones['chest'].matrix
            error=max(abs(expected[i][j]-actual[i][j]) for i in range(4) for j in range(4))
            if error>1e-5:raise ValueError('Canonical rig motion mismatch')
            audit[frame]={'canonical_chest_error':error,'max_contact_displacement_m':float(np.linalg.norm(q-p,axis=1).max()*SCALE)}
            samples.append(q)
        bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
        bpy.data.libraries.write(str(out/'motion-rig.blend'),{canonical,contact},fake_user=True,compress=True)
    base.check_protected()
    np.savez_compressed(out/'contact-poses.npz',frames=np.array(samples),frame_ids=[1,169,193,217,289,360],faces=f)
    (out/'result.json').write_text(json.dumps({'protected_local_data_exact':True,'audit':audit,'visual_gate':'NOT_RUN','actual_gallop':'NOT_RUN','head_attention_derivative':gaze,'scope':'Coordinated diagnostic rig/contact library; no cloth solve or acceptance','native_sha256':base.digest(out/'motion-rig.blend')},indent=2)+'\n')


def simulate(out):
    from wardrobe185_cut_solve import run
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    run(out,motion=True)


def support_sampler(contact,scale):
    """Transfer the nearest neutral contact triangle's coherent bone field.

    Only the small supported regions constrain cloth. Crown belongs to head;
    shoulder holds belong to torso; free cloth still uses the cloth solver.
    """
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from mathutils.geometry import barycentric_transform
    contact.data.calc_loop_triangles()
    points=[v.co.copy() for v in contact.data.vertices]
    triangles=[tuple(t.vertices) for t in contact.data.loop_triangles]
    tree=BVHTree.FromPolygons(points,triangles,all_triangles=True)
    names={g.index:g.name for g in contact.vertex_groups}
    weights=[{names[g.group]:g.weight for g in v.groups} for v in contact.data.vertices]
    def sample(point):
        q,_,face,_=tree.find_nearest(Vector(point)*scale)
        ids=triangles[face]
        uvw=barycentric_transform(q,*(points[i] for i in ids),Vector((1,0,0)),Vector((0,1,0)),Vector((0,0,1)))
        result={}
        for i,w in zip(ids,uvw):
            for name,value in weights[i].items():result[name]=result.get(name,0)+max(0,w)*value
        total=sum(result.values())
        if total<=0:raise ValueError('Unsupported garment point')
        return {name:w/total for name,w in result.items() if w>1e-8}
    return sample


def hold_preflight(ob,contact,pins,out,scale):
    """Check actual animated targets before physics; never repair solved frames."""
    import bpy
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from wardrobe_doublewrap185_solve import inside
    from wardrobe185_cut import winding_inside
    scene=bpy.context.scene;records=[];failures=[];point_samples=[]
    for frame in sorted(set([1,72,169,193,217,360]+list(range(169,361,4)))):
        scene.frame_set(frame);bpy.context.view_layer.update()
        components=[]
        for collider in (contact if isinstance(contact,list) else [contact]):
            ev=collider.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();m.calc_loop_triangles()
            p=np.array([v.co[:] for v in m.vertices]);f=np.array([t.vertices[:] for t in m.loop_triangles]);ev.to_mesh_clear()
            components.append((BVHTree.FromPolygons(p.tolist(),f.tolist(),all_triangles=True),p,f))
        ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();q=np.array([v.co[:] for v in m.vertices]);ev.to_mesh_clear()
        signed=[]
        for i,w in pins.items():
            point=Vector(q[i]);distance=min(tree.find_nearest(point)[3] for tree,_,_ in components);within=False
            for tree,p,f in components:
                try:part_inside=inside(tree,point)
                except ValueError:part_inside=winding_inside(q[i],p[f])
                within|=part_inside
            signed.append(-distance if within else distance)
            if within or distance<.0015:failures.append({'frame':frame,'index':i,'weight':w,'signed_m':signed[-1]})
        records.append({'frame':frame,'minimum_signed_m':min(signed),'maximum_gap_m':max(signed)})
        point_samples.append(q[list(pins)]/scale)
    result={'gate':'FAIL' if failures else 'PASS','scope':'Supported targets vs moving contact only; not free cloth or visible assembly qualification','poses':records,'violations':failures}
    (out/'hold-preflight.json').write_text(json.dumps(result,indent=2)+'\n')
    np.savez_compressed(out/'held-poses.npz',points=np.array(point_samples),indices=list(pins),frame_ids=[r['frame'] for r in records])
    scene.frame_set(1);bpy.context.view_layer.update()
    if failures:raise ValueError('Moving held cloth targets violate contact: '+str(len(failures)))


def screen(out):
    import bpy
    from mathutils import Vector
    import wardrobe_motion178 as base
    import wardrobe_motion178_controls as controls
    import wardrobe_studio as studio
    from wardrobe_motion178_proof import dress_actor
    from wardrobe_underarm179_repair import repair
    from wardrobe_shawl180_cache import cache
    from wardrobe_shawl179 import screens
    from wardrobe_riding_fit import fit_render
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    articulated=out.name.endswith('motionreview03')
    source=base.BASE/('wardrobe185-motion03/trajectory.npz' if articulated else 'wardrobe185-motion02/trajectory.npz');proof=source.parent/'motion-proof.npz'
    hashes=('39300aaf7f60b9b3f13f629141ea477b85e8e201f0d800c4e78bc20f834c12d6','952d8191b5406d4663344c7f5c46ba5e5775eb835820ec4b9f74c765aa2166c2') if articulated else ('c600d77d2f07323ae02803117bffe03a2bae0970ca3472518811e59367aaf749','5e57e3f3405e83ee42ec9b268c90ee46a05a5f507617647805b752bc2ce8fe13')
    for path,sha in zip((source,proof),hashes):
        if base.digest(path)!=sha:raise ValueError('Motion screen source changed')
    with np.load(source,allow_pickle=False) as d:p=d['points'];f=d['faces'];frames=d['frames']
    with np.load(proof,allow_pickle=False) as d:matrices=d['chest_matrices']
    if frames.shape!=(360,7205,3) or matrices.shape!=(360,4,4):raise ValueError('Unexpected diagnostic trajectory')
    bpy.ops.wm.open_mainfile(filepath=str(base.SOURCE),load_ui=False,use_scripts=False)
    base.check_protected();rig,mats,_=base.clean_foundation()
    if articulated:
        from wardrobe185_integration import head_control,upper_garment,harness_routes,boots
        head_control(rig)
    dress_actor(rig);repair(rig,'repair04')
    if articulated:
        upper_garment(rig,mats);harness_routes(rig);boots(rig,mats)
    animate(rig)
    ob=studio.panel('MF185_moving_shawl',p.tolist(),f.tolist(),mats['scarf'],.012,1)
    mod=cache(ob,frames,out/'cloth.mdd');bpy.context.view_layer.objects.active=ob
    while list(ob.modifiers).index(mod)>0:bpy.ops.object.modifier_move_up(modifier=mod.name)
    errors={};matrix_error=0.;scene=bpy.context.scene
    states=[(m,m.show_viewport) for m in ob.modifiers if m!=mod]
    for m,_ in states:m.show_viewport=False
    with controls.render_geometry_paused():
        ob.hide_viewport=False
        for frame in range(1,361):
            scene.frame_set(frame);bpy.context.view_layer.update()
            matrix_error=max(matrix_error,float(np.max(abs(np.array(studio.torso_matrix(-2.7))-matrices[frame-1]))))
            if frame in (1,169,193,217,265,360):
                ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh()
                q=np.array([v.co[:] for v in m.vertices]);ev.to_mesh_clear()
                errors[frame]=float(np.max(abs(q-frames[frame-1])))
        scene.frame_set(169);bpy.context.view_layer.update()
        ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh()
        q=np.array([v.co[:] for v in m.vertices]);ev.to_mesh_clear();backward=float(np.max(abs(q-frames[168])))
    for m,state in states:m.show_viewport=state
    record={'cache_errors_native':errors,'backward_seek_error_native':backward,'all_frame_chest_matrix_error':matrix_error}
    (out/'transfer-check.json').write_text(json.dumps(record,indent=2)+'\n')
    if max(errors.values())>2e-6 or backward>2e-6 or matrix_error>1e-5:raise ValueError('Character/cache transfer mismatch')
    if articulated:
        scene.frame_start=169;scene.frame_end=360;scene.frame_set(169)
        bpy.ops.wm.save_as_mainfile(filepath=str(out/'diagnostic.blend'),check_existing=False,compress=True)
    screens(out,(169,193,217,360) if articulated else (169,193,217,265,360))
    for frame in (169,217):
        scene.frame_set(frame);bpy.context.view_layer.update()
        for angle,label in ((0,'front'),(90,'side'),(180,'rear')):
            fit_render(out,'body-'+label+'-%03d'%frame,angle,(0,.1,-5.2),15.8,(600,900))
    base.check_protected()
    (out/'result.json').write_text(json.dumps({'source':str(source),'transfer':record,'protected_local_data_exact':True,'visual_gate':'NOT_RUN','complete_playback':'NOT_RUN','actual_gallop':'NOT_RUN'},indent=2)+'\n')
