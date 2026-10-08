"""Audit and rebuild latent facial deltas from their retained source controller."""
import json
import numpy as np


def coords(data):
    a=np.empty(len(data)*3,dtype=np.float32);data.foreach_get('co',a);return a.reshape(-1,3)


def independent_shape(basis,delta):
    if basis.shape!=delta.shape or not np.isfinite(delta).all() or np.max(abs(delta))>.5:
        raise ValueError('Invalid independent facial delta')
    return basis+delta


def inspect(scene,out,rest=False):
    import bpy
    from mathutils.kdtree import KDTree
    from wardrobe_motion178_controls import render_geometry_paused
    body=bpy.data.objects['MF_studio_adult_body'];source=bpy.data.objects['MF_continuous_head_neck']
    with render_geometry_paused():
        scene.frame_set(1);bpy.context.view_layer.update()
        transform_record={'basis':np.array(source.matrix_basis).tolist(),
            'parent':source.parent.name if source.parent else None,
            'parent_inverse':np.array(source.matrix_parent_inverse).tolist(),
            'constraints':[{'name':c.name,'type':c.type,'influence':c.influence} for c in source.constraints]}
        if rest:
            if source.parent:raise ValueError('Rest source unexpectedly parented')
            for c in source.constraints:c.mute=True
            bpy.context.view_layer.update()
        # Hidden controllers do not necessarily reevaluate matrix_world when
        # their constraint is muted. The unparented object's authored basis is
        # the recorded neutral transform, independent of the riding pose.
        matrix=np.array(source.matrix_basis if rest else source.matrix_world);p=coords(source.data.shape_keys.key_blocks[0].data)
        world=p@matrix[:3,:3].T+matrix[:3,3]
        basis=coords(body.data.shape_keys.key_blocks[0].data)
        count=int(body.get('accepted_head_vertex_count',0))
        if not 1000<count<=len(basis):raise ValueError('Missing head-domain authority')
        tree=KDTree(len(world))
        for i,v in enumerate(world):tree.insert(v,i)
        tree.balance();mapped=[tree.find(p) for p in basis[:count]]
        ids=np.array([r[1] for r in mapped]);dist=np.array([r[2] for r in mapped])
    source_keys=[];arrays={}
    for k in source.data.shape_keys.key_blocks:
        delta=coords(k.data)-p
        source_keys.append({'name':k.name,'max_delta':float(abs(delta).max()),'value':k.value})
        if k.name=='Basis':continue
        a=np.zeros_like(basis);a[:count]=delta[ids]@matrix[:3,:3].T
        arrays[k.name]=a
    np.savez_compressed(out/'mapped-deltas.npz',**arrays)
    record={'source_keys':source_keys,'head_count':count,'source_vertices':len(p),'transform_record':transform_record,
        'source_matrix':matrix.tolist(),'mapping_distance_quantiles':np.quantile(dist,[0,.5,.9,.99,1]).tolist(),
        'body_basis_bounds':[basis.min(0).tolist(),basis.max(0).tolist()],
        'source_world_bounds':[world.min(0).tolist(),world.max(0).tolist()],
        'visual_gate':'NOT_RUN','scope':'Nearest retained source vertex deltas, same original transfer family; no correction applied'}
    (out/'result.json').write_text(json.dumps(record,indent=2)+'\n')
    return record,arrays


def rebuild(scene,out):
    import bpy
    from wardrobe_motion178_controls import render_geometry_paused
    body=bpy.data.objects['MF_studio_adult_body'];source=bpy.data.objects['MF_continuous_head_neck']
    constraints=[(c,c.mute) for c in source.constraints]
    record,arrays=inspect(scene,out,rest=True)
    for c,mute in constraints:c.mute=mute
    if record['mapping_distance_quantiles'][3]>.08 or record['mapping_distance_quantiles'][4]>.3:
        raise ValueError('Retained head correspondence not established')
    body.data=body.data.copy();keys=body.data.shape_keys
    basis=coords(keys.key_blocks[0].data)
    controller=source.data.shape_keys
    action=controller.animation_data.action;slot=controller.animation_data.action_slot
    controller.animation_data.action=None
    neutral={k.name:(1. if k.name=='MF_ear_definition129' else 0.) for k in list(controller.key_blocks)[1:]}
    # Preserve each source's actual assembly baseline, including the accepted
    # ear offset, by reading its recorded driver expression rather than guessing.
    import ast
    for key in list(keys.key_blocks)[1:]:
        fc=next(f for f in keys.animation_data.drivers if f.data_path==key.path_from_id('value'))
        expr=ast.parse(fc.driver.expression,mode='eval').body
        if not isinstance(expr,ast.BinOp) or not isinstance(expr.op,ast.Sub) or not isinstance(expr.left,ast.Name) or expr.left.id!='source':
            raise ValueError('Unexpected driver baseline')
        offset=ast.literal_eval(expr.right)
        if not isinstance(offset,(float,int)) or not -1<=offset<=1:raise ValueError('Invalid baseline')
        neutral[key.name]=float(offset)
    def set_neutral():
        for name,value in neutral.items():controller.key_blocks[name].value=value
        source.data.update();body.data.update();bpy.context.view_layer.update()
    def evaluated():
        ev=body.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
        result=coords(mesh.vertices);ev.to_mesh_clear();return result
    checks=[]
    with render_geometry_paused():
        body.hide_viewport=False;scene.frame_set(360);set_neutral()
        before=evaluated()
        for name,delta in arrays.items():
            if name not in keys.key_blocks:raise ValueError('Missing target key')
            keys.key_blocks[name].data.foreach_set('co',independent_shape(basis,delta).ravel())
        set_neutral();after=evaluated()
        neutral_error=float(abs(after-before).max())
        if neutral_error>1e-5:raise ValueError('Accepted neutral changed')
        for name in arrays:
            amplitude=-.15 if neutral[name]>.8 else .15
            set_neutral();controller.key_blocks[name].value=neutral[name]+amplitude
            source.data.update();body.data.update();bpy.context.view_layer.update()
            actual=float(keys.key_blocks[name].value)
            q=evaluated();delta=float(abs(q-after).max())
            checks.append({'key':name,'actual_value':actual,'evaluated_delta':delta})
            if abs(actual-amplitude)>1e-5 or not np.isfinite(q).all() or delta>.5:
                raise ValueError('Independent evaluated facial control failed: '+name)
        set_neutral();controller.animation_data.action=action
        if slot:controller.animation_data.action_slot=slot
        from entrance189_performance import facial_values
        for f in (217,265,309,312,337,360):
            scene.frame_set(f);bpy.context.view_layer.update();q=evaluated()
            if not np.isfinite(q).all() or abs(q).max()>30:raise ValueError('Combined bounds failed')
            error=max(abs(keys.key_blocks[n].value-v) for n,v in facial_values(f).items())
            if error>1e-5:raise ValueError('Combined driver values failed')
        if not np.array_equal(coords(keys.key_blocks[0].data),basis):raise ValueError('Base changed')
    record.update({'independent_controls':checks,'neutral_evaluated_max_error':neutral_error,
        'neutral_baselines':neutral,'basis_exact':True,'visual_gate':'NOT_RUN',
        'scope':'Independent retained-source facial deltas; no neutral geometry or accepted identity edit'})
    (out/'face-repair.json').write_text(json.dumps(record,indent=2)+'\n')
    return record
