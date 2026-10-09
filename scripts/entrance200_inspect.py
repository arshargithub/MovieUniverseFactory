"""Read-only fixed198 inspection for the authorized integrated rider correction."""
import json, sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base
SOURCE=base.BASE/'entrance198-build02/scene.blend'
SOURCE_SHA='e7738a23b9eb2324ff41ef15bc5208c5c1a124434cd79f0137e038002dbb5e85'

def validate(job):
    if job!={'operation':'inspect01'}:raise ValueError('Fixed inspection only')
    out=base.BASE/'entrance200-inspect01'
    if out.exists() or base.digest(SOURCE)!=SOURCE_SHA:raise ValueError('Source/output mismatch')
    r=json.loads((SOURCE.parent/'result.json').read_text())
    for row in r['caches']:
        p=(SOURCE.parent/row['path']).resolve()
        if not p.is_relative_to(base.BASE.resolve()) or base.digest(p)!=row['sha256']:raise ValueError('Cache mismatch')
    return out

def main():
    import bpy
    from wardrobe_motion178_controls import render_geometry_paused
    out=validate(json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text()));out.mkdir()
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
    base.check_protected();scene=bpy.context.scene;rig=bpy.data.objects['MF_body156_fit_rig']
    names=[b.name for b in rig.pose.bones];matrices=[];bases=[];eulers=[]
    with render_geometry_paused():
        for f in range(217,361):
            scene.frame_set(f);bpy.context.view_layer.update()
            matrices.append([np.array(rig.matrix_world@b.matrix) for b in rig.pose.bones])
            bases.append([np.array(b.matrix_basis) for b in rig.pose.bones])
            eulers.append([list((rig.matrix_world@b.matrix).to_euler('XYZ')) for b in rig.pose.bones])
    np.savez_compressed(out/'rig.npz',names=names,matrices=matrices,bases=bases,eulers=eulers)
    body=bpy.data.objects['MF_studio_adult_body'];points=np.array([v.co[:] for v in body.data.vertices]);groups={g.index:g.name for g in body.vertex_groups}
    np.savez_compressed(out/'body.npz',points=points)
    selected=[n for n in names if any(s in n.lower() for s in ('thumb','finger','neck','head','hand','chest'))]
    bones={n:{'parent':rig.data.bones[n].parent.name if rig.data.bones[n].parent else None,'head':list(rig.data.bones[n].head_local),'tail':list(rig.data.bones[n].tail_local),'matrix':[list(x) for x in rig.data.bones[n].matrix_local]} for n in selected}
    (out/'bones.json').write_text(json.dumps(bones,indent=2)+'\n')
    (out/'weights.json').write_text(json.dumps({str(v.index):{groups[g.group]:g.weight for g in v.groups} for v in body.data.vertices if any(('thumb' in groups[g.group].lower() or 'finger' in groups[g.group].lower()) and g.weight>.01 for g in v.groups)},indent=2)+'\n')
    objects={};mats={}
    for o in scene.objects:
        if o.hide_render or not hasattr(o.data,'materials'):continue
        if not (o.name.startswith('MF_') and not o.name.startswith(('MF196','MF188','MF189','MF185_gait'))):continue
        objects[o.name]={'materials':[m.name if m else None for m in o.data.materials],'modifiers':[(m.name,m.type) for m in o.modifiers]}
        for m in o.data.materials:
            if not m or not m.use_nodes:continue
            mats[m.name]=[{'name':n.name,'label':n.label,'type':n.type,'image':getattr(getattr(n,'image',None),'name',None),'inputs':{s.name:{'value':list(s.default_value) if hasattr(s.default_value,'__len__') else s.default_value,'links':[l.from_node.name+'.'+l.from_socket.name for l in s.links]} for s in n.inputs if hasattr(s,'default_value')}} for n in m.node_tree.nodes]
    (out/'objects.json').write_text(json.dumps(objects,indent=2)+'\n');(out/'materials.json').write_text(json.dumps(mats,indent=2)+'\n')
    (out/'result.json').write_text(json.dumps({'source_sha256':SOURCE_SHA,'native_modified':False,'bones':len(names)},indent=2)+'\n');base.check_protected()

if __name__=='__main__':main()
