"""Read actual rider/cache ownership before any new motion integration."""
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base
SOURCE_SHA='7038eaf08e1349478841d02604e2b025d76650c1a5c402d7eb76065ffab62812'

def main():
    import bpy
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
    if job!={'operation':'inspect07'}:raise ValueError('Fixed actor inspection required')
    source=base.BASE/'entrance190-blink03/scene.blend';out=base.BASE/'entrance190-actor-inspect07'
    if out.exists() or source.is_symlink() or base.digest(source)!=SOURCE_SHA:raise ValueError('Changed source or prior output')
    out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
    base.check_protected();scene=bpy.context.scene;scene.frame_set(360);bpy.context.view_layer.update()
    rows=[]
    for o in scene.objects:
        if not o.name.startswith(('MF','AS_world','AS_valley')):continue
        rows.append({'name':o.name,'type':o.type,'render':not o.hide_render,
            'parent':o.parent.name if o.parent else None,'parent_type':o.parent_type,'parent_bone':o.parent_bone,
            'matrix_world':[list(r) for r in o.matrix_world],
            'constraints':[{'name':c.name,'type':c.type,'target':c.target.name if hasattr(c,'target') and c.target else None} for c in o.constraints],
            'modifiers':[{'name':m.name,'type':m.type,'object':m.object.name if hasattr(m,'object') and m.object else None,
                          'cache':bpy.path.abspath(m.filepath) if m.type=='MESH_CACHE' else None} for m in o.modifiers]})
    rig=bpy.data.objects['MF_body156_fit_rig']
    bones={b.name:{'parent':b.parent.name if b.parent else None,'head':list(b.head),'matrix':[list(r) for r in b.matrix],
        'mode':b.rotation_mode,'constraints':[c.type for c in b.constraints]} for b in rig.pose.bones}
    (out/'inspection.json').write_text(json.dumps({'source_sha256':SOURCE_SHA,'objects':rows,'bones':bones},indent=2)+'\n')

if __name__=='__main__':main()
