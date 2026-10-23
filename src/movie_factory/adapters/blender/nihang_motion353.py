"""Crest-only sagittal foreleg curl; existing final arrival is invariant."""
import json,math,importlib.util
from pathlib import Path

def curl_angle(frame,fold):
    u=max(0.,min(1.,(frame-331)/10));release=1-u*u*(3-2*u)
    return .75*max(0.,min(1.,fold))**1.2*release if frame<341 else 0.

def run(bpy,out):
    from mathutils import Matrix,Quaternion,Vector
    spec=importlib.util.spec_from_file_location('motion353_profile',Path(__file__).with_name('nihang_motion.py'))
    motion=importlib.util.module_from_spec(spec);spec.loader.exec_module(motion)
    rig=bpy.data.objects['horse.rig'];scene=bpy.context.scene
    if rig.get('motion353'):raise ValueError('MOTION353_PARENT')
    path=Path(__file__).resolve().parents[4]/'results/sikh335/motion01/save-c12-recipe.json'
    anchors=json.loads(path.read_text())['edits'][1]['anchors']
    scene.frame_set(283);bpy.context.view_layer.update();axis=(bpy.data.objects['HORSE hind support pivot'].matrix_world.to_quaternion()@Vector((1,0,0))).normalized()
    names=[stem+'.'+side for side in ('L','R') for stem in ('forefoot_fk','f_toe_fk','f_hoof')]
    preserve=['neck','head','hind_foot_fk.L','hind_foot_fk.R','r_toe_fk.L','r_toe_fk.R']
    capture={}
    for f in range(252,442):
        scene.frame_set(f);bpy.context.view_layer.update()
        capture[f]=dict(world=rig.matrix_world.copy(),bones={n:rig.matrix_world@rig.pose.bones[n].matrix for n in names+preserve})
    records=[];maximum_preserved=0.;maximum_arrival=0.
    def difference(a,b):return max(abs(a[i][j]-b[i][j]) for i in range(4) for j in range(4))
    for f,row in capture.items():
        scene.frame_set(f);bpy.context.view_layer.update();angles={}
        for side,delay in (('L',0),('R',1)):
            fold=motion.sample(anchors,max(252,f-delay))['fold'];angle=curl_angle(f,fold);angles[side]=angle
            origin=row['bones']['forefoot_fk.'+side].translation
            delta=Matrix.Translation(origin)@Quaternion(axis,angle).to_matrix().to_4x4()@Matrix.Translation(-origin)
            for stem in ('forefoot_fk','f_toe_fk','f_hoof'):
                name=stem+'.'+side;pb=rig.pose.bones[name];pb.rotation_mode='QUATERNION';pb.matrix=rig.matrix_world.inverted()@delta@row['bones'][name]
                for prop in ('location','rotation_quaternion','scale'):pb.keyframe_insert(prop,frame=f)
                bpy.context.view_layer.update()
        maximum_preserved=max(maximum_preserved,difference(rig.matrix_world,row['world']),*(difference(rig.matrix_world@rig.pose.bones[n].matrix,row['bones'][n]) for n in preserve))
        if f>=341:maximum_arrival=max(maximum_arrival,*(difference(rig.matrix_world@rig.pose.bones[n].matrix,row['bones'][n]) for n in names))
        records.append(dict(frame=f,angles=angles,hooves={side:list(rig.matrix_world@rig.pose.bones['DEF-f_hoof.'+side].head) for side in ('L','R')}))
    if maximum_preserved>1e-4 or maximum_arrival>1e-4:raise ValueError('MOTION353_PRESERVATION')
    for fc in motion.curves(rig):
        if any('"'+n+'"' in fc.data_path for n in names):
            for k in fc.keyframe_points:
                if 252<=k.co.x<=441:k.interpolation='LINEAR'
    rig['motion353']=1;scene.frame_set(327);bpy.context.view_layer.update()
    report=dict(changed=True,source_preserved=True,frames=records,maximum_preserved_error=maximum_preserved,maximum_arrival_error=maximum_arrival,scope='Crest foreleg silhouette only, full reference performance and appearance not approved.')
    (out/'motion353.json').write_text(json.dumps(report,indent=2)+'\n');return report
