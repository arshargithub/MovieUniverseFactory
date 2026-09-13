"""Fixed bounded pose repair; no full gait authoring, provider code or scene saves."""
from pathlib import Path
import importlib.util
import math
import bpy
BASE=Path('/Users/adisharma/projects/MovieUniverseFactory/runs/demonstrator-01')

def run(mf,out,job,helper):
    if set(job)!={'mode','output_dir','profile'} or job['mode']!='demo_forefoot_pose' or job['profile']!={}:raise ValueError('Fixed pose repair required')
    out=Path(out).resolve()
    if BASE.resolve() not in out.parents:raise ValueError('Invalid output')
    spec=importlib.util.spec_from_file_location('pose_replay',Path(__file__).with_name('demo_fullpace_replay.py'));replay=importlib.util.module_from_spec(spec);spec.loader.exec_module(replay)
    source={};basis={};edges=None;triangles=None;selected=None;topology=None;bounds={};source_angles=[];source_lengths=[]
    names=('forefoot_ik.R','forefoot_heel_ik.R')
    pairs=(('DEF-upper_arm.R','DEF-forearm.R'),('DEF-forearm.R','DEF-forefoot.R'))
    def angle(p,q):return math.degrees((p.tail-p.head).angle(q.tail-q.head))
    def measure():
        nonlocal selected,edges,triangles,topology
        horse=bpy.data.objects['horse.rig'];obj=bpy.data.objects['horse'];deps=bpy.context.evaluated_depsgraph_get();ev=obj.evaluated_get(deps);mesh=ev.to_mesh(preserve_all_data_layers=True,depsgraph=deps)
        try:
            if selected is None:
                groups={g.index for g in obj.vertex_groups if g.name in ('DEF-forefoot.R','DEF-forefoot.R.001','DEF-f_hoof.R','DEF-forearm.R','DEF-forearm.R.001')}
                selected={v.index for v in mesh.vertices if any(g.group in groups and g.weight>.15 for g in v.groups)}
                edges=[tuple(e.vertices) for e in mesh.edges if all(i in selected for i in e.vertices)];mesh.calc_loop_triangles();triangles=[tuple(t.vertices) for t in mesh.loop_triangles if all(i in selected for i in t.vertices)];topology=(len(mesh.vertices),len(mesh.edges))
            if topology!=(len(mesh.vertices),len(mesh.edges)):raise ValueError('Topology changed')
            pts={i:mesh.vertices[i].co.copy() for i in selected}
            return {'edges':[(pts[a]-pts[b]).length for a,b in edges],'areas':[(pts[b]-pts[a]).cross(pts[c]-pts[a]).length/2 for a,b,c in triangles],'angles':[angle(horse.pose.bones[a],horse.pose.bones[b]) for a,b in pairs],'lengths':[(p.tail-p.head).length for p in horse.pose.bones if p.name.startswith('DEF-') and p.name.endswith(('.R','.R.001')) and any(x in p.name for x in ('forefoot','forearm','upper_arm','f_hoof'))],'finite':all(math.isfinite(x) for p in pts.values() for x in p)}
        finally:ev.to_mesh_clear()
    def observer(kind,frame,horse):
        if kind=='source':
            basis[frame]={n:horse.pose.bones[n].matrix_basis.copy() for n in names}
            source[frame]=measure()
    replay.reconstruct(mf,helper,observer)
    for k in ('edges','areas','angles','lengths'):
        bounds[k]=[(min(s[k][i] for s in source.values()),max(s[k][i] for s in source.values())) for i in range(len(source[0][k]))]
    def score(m):
        result={'finite':m['finite']}
        for k in ('edges','areas','angles','lengths'):
            bad=[];worst=1.
            for i,(v,(lo,hi)) in enumerate(zip(m[k],bounds[k])):
                if k=='angles':fail=v<lo-5 or v>hi+5
                else:
                    tolerance=.03 if k=='lengths' else .05
                    fail=v<lo/(1+tolerance) or v>hi*(1+tolerance)
                    if lo>1e-10:worst=max(worst,v/hi,lo/max(v,1e-12))
                if fail:bad.append(i)
            result[k]={'failed':len(bad),'worst_envelope_factor':worst,'values':m[k] if k in ('angles','lengths') else None}
        result['pass']=result['finite'] and all(result[k]['failed']==0 for k in ('edges','areas','angles','lengths'))
        return result
    scene=bpy.context.scene;horse=bpy.data.objects['horse.rig'];trials=[];chosen=[]
    # Numerical interpolation search, each sample starts from the immutable candidate.
    for frame in (1.875,3.25,3.875):
        helper._refresh(scene,mf,frame);original={n:horse.pose.bones[n].matrix_basis.copy() for n in names};original_hoof=helper.hoof_surfaces(bpy.context.evaluated_depsgraph_get())['DEF-f_hoof.R']['center'];accepted=None
        conditions=[('translation_only',1),('orientation_only',1)]+[('coordinated',i/20) for i in range(21)]
        for condition,amount in conditions:
            helper._refresh(scene,mf,frame)
            for n in names:
                target=basis[frame][n];a=original[n];blend=a.lerp(target,amount)
                if condition=='translation_only':blend=a.copy();blend.translation=target.translation
                elif condition=='orientation_only':blend=target.copy();blend.translation=a.translation
                horse.pose.bones[n].matrix_basis=blend;bpy.context.view_layer.update()
            measured=measure();s=score(measured);h=helper.hoof_surfaces(bpy.context.evaluated_depsgraph_get())['DEF-f_hoof.R'];r={'frame':frame,'condition':condition,'amount':amount,'screen':s,'hoof':h,'deviation_from_old_swing_m':math.sqrt(sum((x-y)**2 for x,y in zip(h['center'],original_hoof)))};trials.append(r)
            if condition=='coordinated' and s['pass'] and accepted is None:
                accepted={**r,'control_bases':{n:[list(row) for row in horse.pose.bones[n].matrix_basis] for n in names}}
        chosen.append({'frame':frame,'solution':accepted})
    # Reference positives, and unchanged-candidate negative, measured with same path.
    controls={'source_pass':all(score(s)['pass'] for s in source.values()),'candidate':[]}
    for frame in (1.875,3.25,3.875):
        helper._refresh(scene,mf,frame);controls['candidate'].append({'frame':frame,'screen':score(measure())})
    # Actual temporary mesh distortion on a clean source pose, before armature evaluation.
    helper._file(BASE/'realism-motion/scene.blend',replay.SCENE_SHA);bpy.ops.wm.open_mainfile(filepath=str(BASE/'realism-motion/scene.blend'),load_ui=False,use_scripts=False)
    scene=bpy.context.scene;horse=bpy.data.objects['horse.rig']
    for tr in horse.animation_data.nla_tracks:
        if tr.name.startswith('HoofContactOverlay'):tr.mute=True
    for p in horse.pose.bones:
        p.ik_stretch=0
        for c in p.constraints:
            if c.type=='IK':c.use_stretch=False
    helper._refresh(scene,mf,3.25);controls['distortion_positive']=score(measure())
    obj=bpy.data.objects['horse'];obj.data=obj.data.copy();groups={g.index for g in obj.vertex_groups if g.name.startswith('DEF-forefoot.R')};verts=[v for v in obj.data.vertices if any(g.group in groups and g.weight>.5 for g in v.groups)]
    from mathutils import Vector
    center=sum((v.co for v in verts),Vector())/len(verts)
    for v in verts:v.co=center+(v.co-center)*.7
    obj.data.update();bpy.context.view_layer.update();controls['distortion_negative']=score(measure());controls['distorted_vertices']=len(verts)
    result={'scope':'Pose-only development; no full gait or effects','old_candidate_record_sha256':replay.RECORD_SHA,'source_scene_sha256':replay.SCENE_SHA,'chosen':chosen,'controls':controls,'trials':trials,'pass':all(c['solution'] is not None for c in chosen) and controls['source_pass'] and controls['distortion_positive']['pass'] and not controls['distortion_negative']['pass'] and all(not c['screen']['pass'] for c in controls['candidate'])}
    mf.write_json(out/'pose-results.json',result)
    return ['pose-results.json']
