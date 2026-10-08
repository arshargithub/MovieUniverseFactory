"""Fixed read-only source inspection for the authorized six-second motion proof."""
import json
import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import wardrobe_motion178 as base

SOURCE_SHA = '7038eaf08e1349478841d02604e2b025d76650c1a5c402d7eb76065ffab62812'


def validate(job):
    if job != {'operation': 'inspect01'}:
        raise ValueError('Fixed inspection required')
    source = base.BASE / 'entrance190-blink03/scene.blend'
    out = base.BASE / 'entrance193-inspect01'
    if out.exists() or source.is_symlink() or base.digest(source) != SOURCE_SHA:
        raise ValueError('Source changed or evidence exists')
    return source, out


def main():
    import bpy
    from wardrobe_motion178_controls import render_geometry_paused
    source, out = validate(json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text()))
    out.mkdir(); (out/'handler.py').write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False, use_scripts=False)
    base.check_protected()
    scene = bpy.context.scene; rig = bpy.data.objects['MF_body156_fit_rig']
    objects = []
    for ob in scene.objects:
        if ob.hide_render: continue
        row = {'name':ob.name, 'type':ob.type, 'parent':ob.parent.name if ob.parent else None,
               'world':np.array(ob.matrix_world).tolist(), 'modifiers':[],
               'materials':[s.material.name if s.material else None for s in ob.material_slots]}
        for m in ob.modifiers:
            r = {'name':m.name,'type':m.type,'viewport':m.show_viewport,'render':m.show_render}
            if m.type == 'MESH_CACHE':
                p = Path(bpy.path.abspath(m.filepath)).resolve()
                if not p.is_relative_to(base.BASE.resolve()): raise ValueError('Cache outside source tree')
                r.update(path=str(p), sha256=base.digest(p), start=m.frame_start)
            for prop in ('target','object'):
                v = getattr(m,prop,None)
                if v is not None: r[prop] = v.name
            row['modifiers'].append(r)
        objects.append(row)
    names = [b.name for b in rig.pose.bones]; matrices=[]; bases=[]; heads=[]; tails=[]
    with render_geometry_paused():
        for f in range(217,361):
            scene.frame_set(f); bpy.context.view_layer.update()
            matrices.append([np.array(rig.matrix_world@b.matrix) for b in rig.pose.bones])
            bases.append([np.array(b.matrix_basis) for b in rig.pose.bones])
            heads.append([rig.matrix_world@b.head for b in rig.pose.bones])
            tails.append([rig.matrix_world@b.tail for b in rig.pose.bones])
    np.savez_compressed(out/'rig.npz', names=names, matrices=matrices, bases=bases, heads=heads, tails=tails,
                        rig_world=np.array(rig.matrix_world))
    mats=[]
    for m in bpy.data.materials:
        if m.users and m.use_nodes:
            mats.append({'name':m.name,'nodes':[{'name':n.name,'type':n.type} for n in m.node_tree.nodes],
                         'links':[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links]})
    (out/'result.json').write_text(json.dumps({'source_sha256':SOURCE_SHA,'objects':objects,'materials':mats,
        'camera':scene.camera.name,'bones':names,'visual_gate':'NOT_RUN'},indent=2)+'\n')
    base.check_protected()


if __name__ == '__main__': main()
