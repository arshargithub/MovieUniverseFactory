"""Read-only verification of one hash-bound realism candidate."""
from pathlib import Path
import bpy,math,json
from mathutils import Vector

def verify(mf,out,job,helper):
    if set(job)!={'mode','output_dir','profile'} or job['mode']!='demo_realism_reopen' or job['profile']!={}:raise ValueError('Fixed verification required')
    base=Path('/Users/adisharma/projects/MovieUniverseFactory/runs/demonstrator-01');out=Path(out).resolve()
    if base.resolve() not in out.parents:raise ValueError('Output outside diagnostic runs')
    digest='37594a7ef2d59e5dcc9af42c332f28ab41e86e78f78a60e6bd5ff9e2a7ca961e';scene_file=helper._file(base/'realism-motion/scene.blend',digest)
    bpy.ops.wm.open_mainfile(filepath=str(scene_file),use_scripts=False,load_ui=False)
    scene=bpy.context.scene;rider=bpy.data.objects['rig'];spans={};maxslip=0;penetration=0;reingap=0
    for tick in range(1181):
        f=tick/20;helper._refresh(scene,mf,f);deps=bpy.context.evaluated_depsgraph_get()
        hooves=helper.hoof_surfaces(deps)
        for name,h in hooves.items():
            penetration=max(penetration,-h['min_z'])
            if h['min_z']<=.04:
                spans.setdefault(name,h['center']);p=spans[name];maxslip=max(maxslip,math.hypot(h['center'][0]-p[0],h['center'][1]-p[1]))
            else:spans.pop(name,None)
        for side in ('L','R'):
            hand=rider.pose.bones['hand_fk.'+side];grip=rider.matrix_world@hand.matrix@Vector((0,hand.length*.55,0));obj=bpy.data.objects['repaired rein '+side];point=obj.matrix_world@Vector(obj.data.splines[0].points[-1].co[:3]);reingap=max(reingap,(point-grip).length)
        if tick%20==0:
            for name in ('Man','Helmet','horse','saddle'):helper._bbox(bpy.data.objects[name],deps)
    helper._refresh(scene,mf,0)
    result={'scene_sha256':digest,'frames':[0,59],'step':.05,'max_stance_excursion_m':maxslip,'max_hoof_penetration_m':penetration,'max_rein_endpoint_error_m':reingap,'head_scale':list(rider.pose.bones['head'].scale),'tail_render_children':next(ps.settings.rendered_child_count for ps in bpy.data.objects['horse'].particle_systems if ps.name=='horse.tail'),'all_integer_actor_bounds_finite':True,'screens_pass':maxslip<=.05 and penetration<=.02 and reingap<=.01,'limitations':['Same sole estimator; not independent collision proof.','Surface grasp, skin quality, physical hair and full-pace gallop are not qualified.']}
    lo,hi=helper._bbox(bpy.data.objects['Helmet'],bpy.context.evaluated_depsgraph_get())
    prior=json.loads((base/'free-motion-v2-retry/metrics.json').read_text())['per_frame'][0]['finite_mesh_bounds']['Helmet']
    result['helmet_dimension_ratios_to_previous']=[(hi[i]-lo[i])/(prior[1][i]-prior[0][i]) for i in range(3)]
    mf.write_json(out/'reopen.json',result);return ['reopen.json']
