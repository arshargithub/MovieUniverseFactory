"""Fixed independent replay plus evaluated rig-ownership regression evidence."""
import sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'src')]
import bpy
import sikh300_native
from movie_factory.sikh300_motion import validate
def main():
    p=Path(sys.argv[sys.argv.index('--')+1]);job=validate(json.loads(p.read_text()))
    if job!={'operation':'reopen','version':1}:raise ValueError('Only selected replay operation admitted')
    sikh300_native.main()
    rig=bpy.data.objects['horse.rig'];rows=[]
    for side in ('L','R'):
        for name in ('upper_arm','forearm','forefoot','f_toe'):
            pb=rig.pose.bones['ORG-'+name+'.'+side]
            owned=[c for c in pb.constraints if c.type=='COPY_TRANSFORMS']
            assert owned and any('_fk.' in c.subtarget for c in owned), pb.name
            for c in pb.constraints:
                if c.type!='COPY_TRANSFORMS':continue
                desired=1. if '_fk.' in c.subtarget else 0.
                assert abs(c.influence-desired)<1e-7
                if desired:assert not c.mute and c.target==rig and c.subtarget in rig.pose.bones
                rows.append({'bone':pb.name,'target':c.subtarget,'influence':c.influence,'expected':desired})
    modes={name:rig.pose.bones[name].rotation_mode for name in ('hind_foot_ik.L','hind_foot_ik.R')}
    assert set(modes.values())=={'QUATERNION'}
    result={'fore_constraints':rows,'hind_rotation_modes':modes,'checks_passed':True,'scope':'Selected300 explicit local control ownership, not restored generic Rigify drivers','inherited_driver_count':len(rig.animation_data.drivers) if rig.animation_data else 0}
    (p.parent/'rig-ownership.json').write_text(json.dumps(result,indent=2))
    # Independent road-attribution controls. Only transient render state changes;
    # selected native and the six strict replay frames above remain untouched.
    scene=bpy.context.scene;scene.frame_set(360)
    scene.render.resolution_x=360;scene.render.resolution_y=640
    inventory={'road_modifiers':[(m.name,m.type) for m in bpy.data.objects['irregular packed farm track'].modifiers],
               'lights':[{'name':o.name,'type':o.data.type,'location':list(o.matrix_world.translation),'energy':o.data.energy,'shadow':o.data.use_shadow} for o in scene.objects if o.type=='LIGHT'],
               'ground_candidates':[{'name':o.name,'location':list(o.matrix_world.translation),'hide_render':o.hide_render,'materials':[m.name if m else None for m in o.data.materials]} for o in scene.objects if o.type=='MESH' and any(t in o.name.lower() for t in ('road','track','ground','soil','skid','wear','occlusion'))]}
    (p.parent/'ground-inventory.json').write_text(json.dumps(inventory,indent=2))
    def render(name):
        scene.render.filepath=str(p.parent/(name+'.png'));bpy.ops.render.render(write_still=True)
    render('ground-baseline-360')
    lights=[o for o in scene.objects if o.type=='LIGHT'];shadows={o.name:o.data.use_shadow for o in lights}
    for o in lights:o.data.use_shadow=False
    render('ground-no-shadows-360')
    for o in lights:o.data.use_shadow=shadows[o.name]
    lamp=bpy.data.objects['headlamp beam'];old=lamp.hide_render;lamp.hide_render=True
    render('ground-no-headlamp-360');lamp.hide_render=old
    overlays=[o for o in scene.objects if o.type=='MESH' and any(t in o.name.lower() for t in ('skid','wear','occlusion'))];hidden={o.name:o.hide_render for o in overlays}
    for o in overlays:o.hide_render=True
    render('ground-no-overlays-360')
    for o in overlays:o.hide_render=hidden[o.name]
if __name__=='__main__':main()
