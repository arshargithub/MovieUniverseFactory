"""Source-bound route diagnostics and construction, fixed operation admission."""
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
sys.path.insert(0,str(ROOT/'src/movie_factory/adapters/blender'))
import wardrobe_motion178 as base
from wardrobe_riding_fit import HORSE,HORSE_SHA


def validate(job):
    if job not in ({'operation':'inspect01'}, {'operation':'horse02'}, {'operation':'horse04'}):raise ValueError('Fixed route operation required')
    if HORSE.is_symlink() or base.digest(HORSE)!=HORSE_SHA:raise ValueError('Changed horse source')
    out=base.BASE/('entrance190-route-'+job['operation'])
    if out.exists():raise ValueError('Preserve route evidence')
    return out


def inspect(out):
    import bpy
    from worker import action_channels
    bpy.ops.wm.open_mainfile(filepath=str(HORSE),load_ui=False,use_scripts=False)
    scene=bpy.context.scene;scene.frame_set(0);bpy.context.view_layer.update()
    rows=[]
    for o in scene.objects:
        if o.name in ('horse','horse.rig','horse diagnostic path','saddle','saddle.pad','saddle.stirrup','saddle.stirrup.strap','bridle','bridle.body','bit','Torus.002','Full Bushy Flowing Horse Tail'):
            rows.append({'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,
                'parent_bone':o.parent_bone,'matrix_world':[list(r) for r in o.matrix_world],
                'matrix_basis':[list(r) for r in o.matrix_basis],
                'action':o.animation_data.action.name if o.animation_data and o.animation_data.action else None,
                'nla':[{'name':t.name,'mute':t.mute} for t in o.animation_data.nla_tracks] if o.animation_data else [],
                'constraints':[{'name':c.name,'type':c.type,'target':c.target.name if hasattr(c,'target') and c.target else None} for c in o.constraints],
                'modifiers':[{'name':m.name,'type':m.type} for m in o.modifiers]})
        if o.type in ('MESH','CURVE','CURVES'):o.hide_viewport=True
    rig=bpy.data.objects['horse.rig']
    bones={b.name:{'parent':b.parent.name if b.parent else None,'head':list(b.head),'tail':list(b.tail),
        'mode':b.rotation_mode,'constraints':[{'name':c.name,'type':c.type,'target':c.target.name if hasattr(c,'target') and c.target else None} for c in b.constraints]} for b in rig.pose.bones if b.name.startswith(('forefoot','hind_foot','torso','head','neck','root'))}
    actions=[{'name':a.name,'channels':len(action_channels(a)),'range':list(a.frame_range)} for a in bpy.data.actions if 'horse' in a.name.lower()]
    (out/'inspection.json').write_text(json.dumps({'source_sha256':HORSE_SHA,'objects':rows,'controls':bones,'actions':actions},indent=2)+'\n')
    if base.digest(HORSE)!=HORSE_SHA:raise ValueError('Source changed')


def main():
    args=sys.argv[sys.argv.index('--')+1:]
    if len(args)!=1:raise ValueError('One structured job required')
    job=json.loads(Path(args[0]).read_text());out=validate(job);out.mkdir()
    (out/'handler.py').write_bytes(Path(__file__).read_bytes())
    if job['operation']=='inspect01':inspect(out)
    else:
        import entrance190_horse
        (out/'horse-handler.py').write_bytes(Path(entrance190_horse.__file__).read_bytes())
        entrance190_horse.build(out,corrected=job['operation']=='horse04')


if __name__=='__main__':main()
