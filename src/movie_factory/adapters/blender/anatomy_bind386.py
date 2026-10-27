"""Closed neutral-preserving skin-binding correction on the original horse.

Constant rest/skin authoring only; no new bones, pose curves, or pose cache.
Actual finite deformer response is measured, not approximated as rigid LBS.
"""
import json
import numpy as np

def validate(e):
    if set(e)!={'kind','target','strength'} or e['kind'] not in {'mounted_anatomy386_bind_preserve','mounted_anatomy386_bind_core'} or e['target']!='horse':raise ValueError('BIND386_FIELDS')
    if type(e['strength']) not in (int,float) or not np.isfinite(e['strength']) or not 0<=e['strength']<=.7:raise ValueError('BIND386_STRENGTH')
    return e

def solve_step(jacobian,residual):
    J=np.asarray(jacobian);r=np.asarray(residual)
    if J.shape!=(len(r),3,3) or r.shape!=(len(r),3) or not np.isfinite(J).all() or not np.isfinite(r).all():raise ValueError('BIND386_RESPONSE_SHAPE')
    condition=np.linalg.cond(J)
    if not np.isfinite(condition).all() or condition.max()>50:raise ValueError('BIND386_RESPONSE_CONDITION')
    return np.linalg.solve(J,r[...,None])[...,0],float(condition.max())

def probe_tolerance(epsilon):
    """A smaller probe makes the relative requirement stricter, never easier."""
    return min(.00015,.05*float(np.linalg.norm(np.array([.42,-.56,.72])*epsilon)))

def segment_hit(p,d,tri,eps=1e-8):
    a=tri[:,0];e1=tri[:,1]-a;e2=tri[:,2]-a;h=np.cross(d,e2);det=np.einsum('ni,ni->n',e1,h);valid=abs(det)>eps;safe=np.where(valid,det,1);s=p-a;u=np.einsum('ni,ni->n',s,h)/safe;q=np.cross(s,e1);v=np.einsum('ni,ni->n',d,q)/safe;t=np.einsum('ni,ni->n',e2,q)/safe
    return valid&(u>eps)&(v>eps)&(u+v<1-eps)&(t>eps)&(t<1-eps)

def crossing_pairs(points,faces,affected):
    tri=points[faces];lo=tri.min(1);hi=tri.max(1);pairs=[]
    for i in np.flatnonzero(affected):
        ids=np.flatnonzero(np.all(hi>=lo[i]-1e-8,axis=1)&np.all(lo<=hi[i]+1e-8,axis=1));ids=ids[ids!=i]
        if len(ids):
            shared=np.any(faces[ids,:,None]==faces[i][None,None,:],axis=(1,2));pairs.extend((min(i,int(j)),max(i,int(j))) for j in ids[~shared])
    if not pairs:return set()
    pairs=np.unique(np.array(pairs,dtype=int),axis=0);aa=tri[pairs[:,0]];bb=tri[pairs[:,1]];hit=np.zeros(len(pairs),bool)
    for i,j in [(0,1),(1,2),(2,0)]:hit|=segment_hit(aa[:,i],aa[:,j]-aa[:,i],bb)|segment_hit(bb[:,i],bb[:,j]-bb[:,i],aa)
    return {tuple(map(int,x)) for x in pairs[hit]}

def weights(horse):
    names=[g.name for g in horse.vertex_groups];w=np.zeros((len(horse.data.vertices),len(names)),np.float32)
    for v in horse.data.vertices:
        for g in v.groups:w[v.index,g.group]=g.weight
    return names,w

def apply(bpy,out,e,helpers):
    validate(e);horse=bpy.data.objects['horse'];scene=bpy.context.scene;keys=horse.data.shape_keys.key_blocks
    if horse.get('cache376') or horse.get('weights386') or horse.get('bind_preserve386'):raise ValueError('BIND386_SOURCE_STATE')
    if [k.name for k in keys]!=['Basis','corr.neck','corr.chin','corr.neck.2'] or len(horse.data.vertices)!=22514:raise ValueError('BIND386_SOURCE_KEYS')
    if any((m.show_viewport or m.show_render) and m.type not in {'ARMATURE','SUBSURF'} for m in horse.modifiers):raise ValueError('BIND386_UNQUALIFIED_DEFORMER')
    arm=[(m.name,m.show_viewport,m.show_render) for m in horse.modifiers if m.type=='ARMATURE']
    if not arm or not all(a and b for _,a,b in arm):raise ValueError('BIND386_ARMATURE_NOT_LIVE')
    before=np.array([[v.co[:] for v in k.data] for k in keys],np.float32);raw=np.array([v.co[:] for v in horse.data.vertices],np.float32);names,w0=weights(horse);geometry=helpers('nihang_prep367').frozen(bpy);actions=helpers('nihang_padsolve370').actions(bpy)
    pose_before,rig_before=helpers('anatomy_rest386').pose_samples(bpy,horse,helpers);goal=pose_before[0].copy();saved=(scene.frame_current,scene.frame_subframe);levels=[(m,m.show_viewport) for m in horse.modifiers if m.type=='SUBSURF'];errors=[];conditions=[];probe_errors=[];response_trials=[];current=before.copy();last_response={}
    def put(arrays):
        for k,co in zip(keys,arrays):k.data.foreach_set('co',co.ravel())
        horse.data.shape_keys.update_tag();horse.data.update();horse.update_tag(refresh={'DATA'});bpy.context.view_layer.update()
    def cage():return helpers('nihang_pose376').cage(bpy,horse)
    def rig_state():
        rig=bpy.data.objects['horse.rig']
        return np.array([[list(row) for row in horse.matrix_world]]+[[list(row) for row in rig.matrix_world@pb.matrix] for pb in rig.pose.bones])
    if e['strength']:
        weight_kind='mounted_anatomy386_weights_core' if e['kind'].endswith('_core') else 'mounted_anatomy386_weights'
        helpers('anatomy_weights386').apply(bpy,out,dict(kind=weight_kind,target='horse',strength=e['strength']),helpers)
    _,w1=weights(horse);selected=np.any(w1!=w0,axis=1);ids=np.flatnonzero(selected)
    try:
        for m,_ in levels:m.show_viewport=False
        scene.frame_set(283);bpy.context.view_layer.update()
        for iteration in range(8):
            actual=cage();residual=goal-actual;maximum=float(np.linalg.norm(residual,axis=1).max());errors.append(maximum)
            if maximum<=.0001:break
            if not len(ids) or np.linalg.norm(residual[~selected],axis=1).max()>2e-5:raise ValueError('BIND386_OUTSIDE_RESPONSE')
            active=np.flatnonzero(selected&(np.linalg.norm(residual,axis=1)>.0001));reference_rig=rig_state();qualified=False
            # Only vertices needing inversion are perturbed. A locally
            # nonsmooth but already-correct limb vertex must not be modified.
            for eps in [.001,.0005,.00025,.000125]:
                J=np.zeros((len(active),3,3));reset_max=0.;rig_drift=0.
                for axis in range(3):
                    trial=current.copy();trial[:,active,axis]+=eps;put(trial);plus=cage()[active];rig_drift=max(rig_drift,float(abs(rig_state()-reference_rig).max()));put(current);reset_max=max(reset_max,float(np.linalg.norm(cage()-actual,axis=1).max()))
                    trial=current.copy();trial[:,active,axis]-=eps;put(trial);minus=cage()[active];rig_drift=max(rig_drift,float(abs(rig_state()-reference_rig).max()));put(current);reset_max=max(reset_max,float(np.linalg.norm(cage()-actual,axis=1).max()));J[:,:,axis]=(plus-minus)/(2*eps)
                probe=np.tile(np.array([.42,-.56,.72])*eps,(len(active),1));trial=current.copy();trial[:,active,:]+=probe;put(trial);measured=cage()[active]-actual[active];predicted=np.einsum('nij,nj->ni',J,probe);per_vertex=np.linalg.norm(measured-predicted,axis=1);probe_error=float(per_vertex.max());rig_drift=max(rig_drift,float(abs(rig_state()-reference_rig).max()));put(current);reset_max=max(reset_max,float(np.linalg.norm(cage()-actual,axis=1).max()))
                response_trials.append(dict(iteration=iteration,epsilon=eps,active_vertices=len(active),reset_error=reset_max,rig_drift=rig_drift,probe_error=probe_error,tolerance=probe_tolerance(eps)))
                last_response=dict(jacobian=J,active_ids=active,probe_input=probe,probe_measured=measured,probe_predicted=predicted,probe_errors=per_vertex,epsilon=np.array(eps))
                if reset_max>2e-6:raise ValueError('BIND386_RESPONSE_RESET')
                if rig_drift>1e-7:raise ValueError('BIND386_GEOMETRY_RIG_COUPLING')
                if probe_error<=probe_tolerance(eps):qualified=True;probe_errors.append(probe_error);break
            if not qualified:raise ValueError('BIND386_RESPONSE_PROBE')
            update,condition=solve_step(J,residual[active]);conditions.append(condition);scale=min(1.,.095/max(float(np.linalg.norm(update,axis=1).max()),1e-12));update*=scale;accepted=False
            for alpha in [1.,.5,.25,.125]:
                trial=current.copy();trial[:,active,:]+=alpha*update
                try:helpers('anatomy_domain386').preserve_pectoral_interfaces(raw,trial[0],raw,w0,names,max_proximal=.15)
                except ValueError:continue
                if np.linalg.norm(trial[0]-raw,axis=1).max()>.18:continue
                put(trial);error=float(np.linalg.norm(goal-cage(),axis=1).max())
                if error<maximum:current=trial;accepted=True;break
            if not accepted:put(current);raise ValueError('BIND386_NO_BOUNDED_PROGRESS')
        put(current);neutral=cage();neutral_error=float(np.linalg.norm(neutral-goal,axis=1).max())
        if neutral_error>.0001:raise ValueError('BIND386_NEUTRAL_FIT')
    except Exception as exc:
        (out/'anatomy386-bind-failure.json').write_text(json.dumps(dict(error=type(exc).__name__,reason=str(exc),inverse_errors=errors,conditions=conditions,probe_errors=probe_errors,response_trials=response_trials,key_values={k.name:float(k.value) for k in keys},scope='Failed bounded native solve, not an anatomy candidate.'),indent=2)+'\n')
        np.savez_compressed(out/'anatomy386-bind-failed.npz',rest_before=before,rest_last=current,raw=raw,neutral_goal=goal,**last_response)
        raise
    finally:
        for m,v in levels:m.show_viewport=v
        scene.frame_set(saved[0],subframe=saved[1]);bpy.context.view_layer.update()
    after=np.array([[v.co[:] for v in k.data] for k in keys],np.float32);relative_error=float(abs((after-after[0])-(before-before[0])).max());other=helpers('nihang_prep367').frozen(bpy);geometry.pop('horse');other.pop('horse')
    if geometry!=other or actions!=helpers('nihang_padsolve370').actions(bpy) or relative_error>1e-6 or not np.array_equal(raw,np.array([v.co[:] for v in horse.data.vertices],np.float32)):raise ValueError('BIND386_PRESERVATION')
    pose_after,rig_after=helpers('anatomy_rest386').pose_samples(bpy,horse,helpers);preservation=helpers('anatomy_domain386').evaluated_preservation(pose_before,pose_after,~selected,rig_before,rig_after)
    domain=helpers('anatomy_domain386').preserve_pectoral_interfaces(raw,after[0],raw,w0,names,max_proximal=.15)
    changed=np.any(after[0]!=raw,axis=1);p=raw[changed]
    if np.linalg.norm(after[0]-raw,axis=1).max()>.18 or np.any(abs(p[:,0])>.36) or np.any((p[:,1]<-1.2)|(p[:,1]>-.25)|(p[:,2]<.95)|(p[:,2]>1.75)):raise ValueError('BIND386_CUMULATIVE_REGION')
    edges=np.array([ed.vertices[:] for ed in horse.data.edges]);skin=helpers('anatomy_domain386').main_skin(edges,len(raw));horse.data.calc_loop_triangles();faces=np.array([t.vertices[:] for t in horse.data.loop_triangles]);faces=faces[np.all(skin[faces],axis=1)];affected=np.any(selected[faces],axis=1);surface=[]
    if e['strength']:
        for i,frame in enumerate([283,333,339]):
            old=crossing_pairs(pose_before[i],faces,affected);new=crossing_pairs(pose_after[i],faces,affected);surface.append(dict(frame=frame,before_crossings=len(old),after_crossings=len(new),introduced_crossings=len(new-old),introduced_pair_samples=[list(x) for x in sorted(new-old)[:12]]))
    np.savez_compressed(out/'anatomy386-bind-preserve.npz',rest_before=before,rest_after=after,raw=raw,weights_before=w0,weights_after=w1,selected=selected,pose_before=pose_before,pose_after=pose_after,rig_before=rig_before,rig_after=rig_after,neutral_goal=goal,neutral_actual=neutral)
    report=dict(strength=e['strength'],zero_control=not bool(e['strength']),changed_weight_vertices=len(ids),neutral_error=neutral_error,inverse_errors=errors,response_trials=response_trials,condition_max=max(conditions) if conditions else None,independent_probe_error_max=max(probe_errors) if probe_errors else None,relative_corrective_error=relative_error,pose_preservation=preservation,domain_preservation=domain,max_original_rest_delta=float(np.linalg.norm(after[0]-raw,axis=1).max()),geometry_actions_other_objects_preserved=True,original_armature_live=arm,surface_diagnostics=surface,nap_consumer_not_updated=True,scope='Neutral-preserving constant binding candidate/control only; no new bones/actions/cache. Actual anatomy, final high-resolution surface/contact/consumer and fullspeed AV remain separate. Intermediate weights386report predates bind compensation.')
    if e['strength']:horse['bind_preserve386']=True
    (out/'anatomy386-bind-preserve.json').write_text(json.dumps(report,indent=2)+'\n');return report
