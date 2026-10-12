"""Closed read-only inspection of the two bound contact derivatives."""
import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base

def main():
    import bpy
    from worker import action_channels
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
    if job != {'operation':'inspect'}: raise ValueError('Closed inspection')
    out=ROOT/'.runtime/art-direction/series01-finish237/inspection.json'
    if out.exists():raise ValueError('Preserve evidence')
    result={}
    for kind,folder in [('opening','entrance218-opening12'),('route','entrance218-route13')]:
        src=base.BASE/folder/'scene.blend';meta=json.loads((src.parent/'result.json').read_text())
        if base.digest(src)!=meta['native_sha256']:raise ValueError('Changed source')
        bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False,use_scripts=False)
        scene=bpy.context.scene;scene.frame_set(217 if kind=='opening' else 361)
        objects=[]
        for ob in scene.objects:
            caches=[dict(name=m.name,path=bpy.path.abspath(m.filepath),start=m.frame_start,
                time_mode=m.time_mode,play_mode=m.play_mode,eval_frame=m.eval_frame) for m in ob.modifiers if m.type=='MESH_CACHE']
            action=ob.animation_data.action if ob.animation_data else None
            if action or caches or ob.type=='ARMATURE' or 'root' in ob.name.lower():
                objects.append(dict(name=ob.name,parent=ob.parent.name if ob.parent else None,
                    location=list(ob.location),world=list(ob.matrix_world.translation),
                    action=action.name if action else None,channels=[(f.data_path,f.array_index,len(f.keyframe_points)) for f in action_channels(action)] if action else [],caches=caches,
                    constraints=[(c.type,getattr(getattr(c,'target',None),'name',None)) for c in ob.constraints]))
        result[kind]=dict(source=str(src.relative_to(ROOT)),sha=base.digest(src),objects=objects,
            actions=[dict(name=a.name,range=list(a.frame_range),channels=len(list(action_channels(a)))) for a in bpy.data.actions])
    out.parent.mkdir(exist_ok=True,parents=True);out.write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':main()
