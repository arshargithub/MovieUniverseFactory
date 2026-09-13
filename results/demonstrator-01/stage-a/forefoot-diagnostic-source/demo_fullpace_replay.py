"""Independent clean-reference audit of the existing third candidate; no new gait."""
from pathlib import Path
import json
import bpy
BASE=Path('/Users/adisharma/projects/MovieUniverseFactory/runs/demonstrator-01')
SCENE_SHA='37594a7ef2d59e5dcc9af42c332f28ab41e86e78f78a60e6bd5ff9e2a7ca961e'
RECORD_SHA='cc43617fb765512a6ee7882246c398d718bd6725f08f1cde23ca5a737f8eac8c'

def reconstruct(mf,helper,observer=None):
    helper._file(BASE/'realism-motion/scene.blend',SCENE_SHA);helper._file(BASE/'fullpace-probe3/authoring.json',RECORD_SHA)
    bpy.ops.wm.open_mainfile(filepath=str(BASE/'realism-motion/scene.blend'),load_ui=False,use_scripts=False)
    scene=bpy.context.scene;horse=bpy.data.objects['horse.rig'];path=bpy.data.objects['horse diagnostic path']
    for tr in horse.animation_data.nla_tracks:
        if tr.name.startswith('HoofContactOverlay'):tr.mute=True
    for pb in horse.pose.bones:
        pb.ik_stretch=0
        for c in pb.constraints:
            if c.type=='IK':c.use_stretch=False
    names=[p.name for p in horse.pose.bones if p.name.startswith(('DEF-thigh','DEF-lower_leg','DEF-hind_foot','DEF-upper_arm','DEF-forearm','DEF-forefoot','DEF-r_hoof','DEF-f_hoof'))]
    clean={}
    for tick in range(81):
        helper._refresh(scene,mf,tick/8);clean[tick]={n:(horse.pose.bones[n].tail-horse.pose.bones[n].head).length for n in names}
        if observer:observer("source",tick/8,horse)
    d=json.loads((BASE/'fullpace-probe3/authoring.json').read_text())
    path.animation_data.action=path.animation_data.action.copy()
    for fc in mf.action_channels(path.animation_data.action):
        if fc.data_path=='location' and fc.array_index==1:
            for k in fc.keyframe_points:k.co.y=-12*k.co.x/24
    helper._refresh(scene,mf,0);adjust=bpy.data.objects.new('fullpace body travel',None);scene.collection.objects.link(adjust);o=bpy.data.objects['realism speed compensation'];world=o.matrix_world.copy();o.parent=adjust;o.matrix_world=world
    for f,z in d['zkeys']:
        path.location.z=z;path.keyframe_insert('location',index=2,frame=f);adjust.location=(0,-(12-6.47)*f/24,z);adjust.keyframe_insert('location',frame=f)
    for o in (path,adjust):
        for fc in mf.action_channels(o.animation_data.action):
            for k in fc.keyframe_points:k.interpolation='LINEAR' if fc.array_index==1 else 'BEZIER';k.handle_left_type=k.handle_right_type='AUTO_CLAMPED'
    action=bpy.data.actions.new('authored fullpace gait');slot=action.slots.new(id_type='OBJECT',name=horse.name);bag=action.layers.new('Authored existing IK').strips.new(type='KEYFRAME').channelbag(slot,ensure=True)
    for name in sorted({r[1] for r in d['records']}):
        pb=horse.pose.bones[name];pb.rotation_mode='QUATERNION';rows=[r for r in d['records'] if r[1]==name];prev=None
        for i,row in enumerate(rows):
            q=row[3]
            if prev and sum(a*b for a,b in zip(prev,q))<0:q=[-x for x in q];rows[i]=row[:3]+[q]
            prev=q
        for prop,count,col in (('location',3,2),('rotation_quaternion',4,3)):
            for axis in range(count):
                fc=bag.fcurves.new(pb.path_from_id(prop),index=axis)
                for row in rows:k=fc.keyframe_points.insert(row[0],row[col][axis]);k.interpolation='BEZIER';k.handle_left_type=k.handle_right_type='AUTO_CLAMPED'
    tr=horse.animation_data.nla_tracks.new();tr.name='authored fullpace';st=tr.strips.new(action.name,0,action);st.action_slot=slot;st.blend_type='REPLACE';st.extrapolation='NOTHING'
    comparisons=[]
    for tick in range(81):
        helper._refresh(scene,mf,tick/8)
        if observer:observer("candidate",tick/8,horse)
        for n,before in clean[tick].items():
            after=(horse.pose.bones[n].tail-horse.pose.bones[n].head).length
            if before>1e-6:comparisons.append({'frame':tick/8,'bone':n,'source_length':before,'candidate_length':after,'ratio':after/before})
    result={'source_scene_sha256':SCENE_SHA,'authoring_sha256':RECORD_SHA,'reference':'Unmodified source rotation modes, clean NLA source; same no-IK-stretch setting as candidate. Reference captured before any candidate pose writes.','min_ratio':min(x['ratio'] for x in comparisons),'max_ratio':max(x['ratio'] for x in comparisons),'worst':sorted(comparisons,key=lambda x:abs(x['ratio']-1),reverse=True)[:12]}
    result['pass']=result['min_ratio']>=.97 and result['max_ratio']<=1.03
    return result

def verify(mf,out,job,helper):
    if set(job)!={'mode','output_dir','profile'} or job['mode']!='demo_fullpace_clean_audit' or job['profile']!={}:raise ValueError('Fixed verification required')
    out=Path(out).resolve()
    if BASE.resolve() not in out.parents:raise ValueError('Invalid output')
    result=reconstruct(mf,helper);mf.write_json(out/'clean-reference.json',result);return ['clean-reference.json']
