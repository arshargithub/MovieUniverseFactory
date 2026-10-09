"""Fixed read-only deformation diagnosis across original and candidate."""
import sys,json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from entrance200_inspect import base,SOURCE,SOURCE_SHA

def main():
    import bpy
    if json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())!={'operation':'deformation12'}:raise ValueError('Fixed diagnostic only')
    out=base.BASE/'entrance200-deformation12'
    if out.exists() or base.digest(SOURCE)!=SOURCE_SHA:raise ValueError('Preserve evidence/source')
    out.mkdir();rows={}
    for label,source in [('before',SOURCE),('after',base.BASE/'entrance200-candidate03/scene.blend')]:
        if label=='after' and base.digest(source)!=json.loads((source.parent/'result.json').read_text())['native_sha256']:raise ValueError('Changed candidate')
        bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);scene=bpy.context.scene
        for ob in scene.objects:
            for m in ob.modifiers:
                if m.type in ('SMOOTH','CORRECTIVE_SMOOTH','SUBSURF'):m.show_viewport=False
        scene.frame_set(360);bpy.context.view_layer.update();rig=bpy.data.objects['MF_body156_fit_rig'];body=bpy.data.objects['MF_studio_adult_body']
        ev=body.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();points=np.array([v.co[:] for v in me.vertices]);ev.to_mesh_clear()
        np.savez_compressed(out/(label+'.npz'),points=points)
        rows[label]={'bones':{b.name:{'matrix':[list(x) for x in rig.matrix_world@b.matrix],'basis':[list(x) for x in b.matrix_basis], 'deform':b.bone.use_deform,'constraints':[(c.name,c.type) for c in b.constraints],'mode':b.rotation_mode} for b in rig.pose.bones if '4_' in b.name or 'MF185_' in b.name},
          'modifiers':[{ 'name':m.name,'type':m.type,'object':getattr(getattr(m,'object',None),'name',None),'vertex_group':getattr(m,'vertex_group',None)} for m in body.modifiers],
          'shapes':[(k.name,k.value) for k in body.data.shape_keys.key_blocks] if body.data.shape_keys else []}
    (out/'result.json').write_text(json.dumps(rows,indent=2)+'\n')

if __name__=='__main__':main()
