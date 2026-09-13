"""Fixed read-only measurements of the hash-bound third gait, never a repair."""
from pathlib import Path
import importlib.util
import math
import bpy

BASE=Path('/Users/adisharma/projects/MovieUniverseFactory/runs/demonstrator-01')

def diagnose(mf,out,job,helper):
    if set(job)!={'mode','output_dir','profile'} or job['mode']!='demo_forefoot_diagnosis' or job['profile']!={}:raise ValueError('Fixed diagnosis required')
    out=Path(out).resolve()
    if BASE.resolve() not in out.parents:raise ValueError('Invalid output')
    spec=importlib.util.spec_from_file_location('forefoot_replay',Path(__file__).with_name('demo_fullpace_replay.py'));replay=importlib.util.module_from_spec(spec);spec.loader.exec_module(replay)
    source_basis={};rows={'source':[],'candidate':[]};geometry={'source':[],'candidate':[]};inventory={};edges=None;triangles=None;selected=None;topology=None
    def observe(kind,frame,horse):
        nonlocal edges,triangles,selected,topology
        names=[p.name for p in horse.pose.bones if p.name.endswith(('.R','.R.001')) and any(x in p.name for x in ('forefoot','forearm','f_toe','f_hoof','upper_arm'))]
        if not inventory:
            for n in names:
                p=horse.pose.bones[n]
                inventory[n]={'rest_length':p.bone.length,'parent':p.parent.name if p.parent else None,'rotation_mode':p.rotation_mode,'constraints':[{'name':c.name,'type':c.type,'subtarget':getattr(c,'subtarget',None),'influence':c.influence,'rest_length':getattr(c,'rest_length',None),'volume':getattr(c,'volume',None)} for c in p.constraints]}
        if kind=='source':source_basis[frame]={n:horse.pose.bones[n].matrix_basis.copy() for n in ('forefoot_ik.R','forefoot_heel_ik.R')}
        bones={n:{'length':(horse.pose.bones[n].tail-horse.pose.bones[n].head).length,'basis_scale':list(horse.pose.bones[n].scale),'pose_scale':list(horse.pose.bones[n].matrix.to_scale()),'head':list(horse.pose.bones[n].head),'tail':list(horse.pose.bones[n].tail)} for n in names}
        rows[kind].append({'frame':frame,'bones':bones})
        obj=bpy.data.objects['horse'];deps=bpy.context.evaluated_depsgraph_get();ev=obj.evaluated_get(deps);mesh=ev.to_mesh(preserve_all_data_layers=True,depsgraph=deps)
        try:
            if selected is None:
                groups={g.index for g in obj.vertex_groups if g.name in ('DEF-forefoot.R','DEF-forefoot.R.001','DEF-f_hoof.R','DEF-forearm.R','DEF-forearm.R.001')}
                selected={v.index for v in mesh.vertices if any(g.group in groups and g.weight>.15 for g in v.groups)}
                edges=[tuple(e.vertices) for e in mesh.edges if all(i in selected for i in e.vertices)]
                mesh.calc_loop_triangles();triangles=[tuple(t.vertices) for t in mesh.loop_triangles if all(i in selected for i in t.vertices)]
                topology=(len(mesh.vertices),len(mesh.edges))
            if topology!=(len(mesh.vertices),len(mesh.edges)):raise ValueError('Evaluated topology changed')
            points={i:mesh.vertices[i].co.copy() for i in selected}
            if not all(math.isfinite(x) for p in points.values() for x in p):raise ValueError('Nonfinite evaluated mesh')
            lengths=[(points[a]-points[b]).length for a,b in edges]
            areas=[(points[b]-points[a]).cross(points[c]-points[a]).length/2 for a,b,c in triangles]
            geometry[kind].append({'frame':frame,'edge_lengths':lengths,'triangle_areas':areas})
            if frame in (0,2.75,3.875,5,7.5):
                mf.write_json(out/f'{kind}-mesh-{frame}.json',{'coordinates':'evaluated object-local','points':{str(i):list(v) for i,v in points.items()},'triangles':triangles})
        finally:ev.to_mesh_clear()
    result=replay.reconstruct(mf,helper,observer=observe)
    # Disposable single-pose interventions, not new keyed gait variants.
    interventions=[]
    for frame in (1.875,3.25,3.875):
        for condition,restore in [('unchanged',()),('source_foot_only',('forefoot_ik.R',)),('source_heel_only',('forefoot_heel_ik.R',)),('source_foot_and_heel',('forefoot_ik.R','forefoot_heel_ik.R')),('reset_unchanged',())]:
            horse=bpy.data.objects['horse.rig'];helper._refresh(bpy.context.scene,mf,frame)
            for n in restore:
                horse.pose.bones[n].matrix_basis=source_basis[frame][n]
                bpy.context.view_layer.update()
            obj=bpy.data.objects['horse'];deps=bpy.context.evaluated_depsgraph_get();ev=obj.evaluated_get(deps);mesh=ev.to_mesh(preserve_all_data_layers=True,depsgraph=deps)
            try:
                points={i:mesh.vertices[i].co.copy() for i in selected}
                lengths=[(points[a]-points[b]).length for a,b in edges]
                areas=[(points[b]-points[a]).cross(points[c]-points[a]).length/2 for a,b,c in triangles]
                metrics={}
                for key,vals in [('edge_lengths',lengths),('triangle_areas',areas)]:
                    ratios=[]
                    for i,v in enumerate(vals):
                        lo=min(r[key][i] for r in geometry['source']);hi=max(r[key][i] for r in geometry['source'])
                        if lo>1e-10:ratios.append(max(v/hi,lo/max(v,1e-12)))
                    metrics[key]={'max_outside_envelope_factor':max(ratios),'outside_by_5percent':sum(x>1.05 for x in ratios)}
                interventions.append({'frame':frame,'condition':condition,'metrics':metrics})
            finally:ev.to_mesh_clear()
    mf.write_json(out/'single-pose-controls.json',{'scope':'Disposable unkeyed source-basis restoration at three fixed frames. Does not generate, qualify or save a new gait. Same-frame source values isolate foot/heel edits; no claim of phase-matched repair.','controls':interventions})
    segment_summary={}
    for n in inventory:
        if not n.startswith('DEF-'):continue
        segment_summary[n]={k:{'min':min(r['bones'][n]['length'] for r in rr),'max':max(r['bones'][n]['length'] for r in rr)} for k,rr in rows.items()}
        segment_summary[n]['rest_length']=inventory[n]['rest_length']
    summaries={}
    for key,items in [('edge_lengths',edges),('triangle_areas',triangles)]:
        worst=[];outside=set()
        for i,ids in enumerate(items):
            lo=min(r[key][i] for r in geometry['source']);hi=max(r[key][i] for r in geometry['source'])
            if lo<1e-10:continue
            for r in geometry['candidate']:
                value=r[key][i];exc=max(value/hi,lo/max(value,1e-12));
                if exc>1.05:outside.add(i)
                worst.append({'frame':r['frame'],'vertices':ids,'source_min':lo,'source_max':hi,'candidate':value,'outside_envelope_factor':exc})
        summaries[key]={'count':len(items),'outside_source_envelope_by_5percent':len(outside),'worst':sorted(worst,key=lambda x:x['outside_envelope_factor'],reverse=True)[:15]}
    mf.write_json(out/'diagnosis.json',{'clean_comparison':result,'segment_ranges':segment_summary,'mesh':summaries,'inventory':inventory,'note':'Source-cycle envelopes are diagnostic context only, not a replacement acceptance gate. Topology and finite coordinates checked at all 81 samples for both states.'})
    mf.write_json(out/'bone-samples.json',rows)
    mf.write_json(out/'mesh-samples.json',geometry)
    return ['diagnosis.json','bone-samples.json','mesh-samples.json']
