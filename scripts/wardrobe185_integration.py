"""Fixed character integration diagnostics; accepted masters remain untouched."""
import json
from pathlib import Path


def head_weights(z):
    from wardrobe_motion178_controls import smooth
    neck=smooth((z+1.72)/.34)
    head=smooth((z+1.38)/.38)
    return {'chest':1-neck,'MF185_neck':neck*(1-head),'MF185_head':neck*head}


def head_control(rig):
    """Two-joint derivative, neutral parity, rigid face with a lower-neck blend."""
    import bpy
    from mathutils import Vector
    from wardrobe_motion178_controls import render_geometry_paused
    from wardrobe_refinement import neutral
    neutral(rig)
    roots=[bpy.data.objects[n] for n in ('MF_aimable_eye_Left','MF_aimable_eye_Right',
        'MF_natural147_hair_temples','MF_natural147_hair_retarget')]
    original={ob.name:ob.matrix_world.copy() for ob in roots}
    with render_geometry_paused():
        rig.data=rig.data.copy()
        bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
        bpy.ops.object.mode_set(mode='EDIT')
        for name,z0,z1,parent in (('MF185_neck',-1.55,-.75,'chest'),('MF185_head',-.75,.45,'MF185_neck')):
            bone=rig.data.edit_bones.new(name);bone.head=(0,.22,z0);bone.tail=(0,.22,z1)
            bone.parent=rig.data.edit_bones[parent];bone.use_connect=False
        bpy.ops.object.mode_set(mode='OBJECT');bpy.context.view_layer.update()
        body=bpy.data.objects['MF_studio_adult_body'];body.data=body.data.copy()
        groups={n:body.vertex_groups.get(n) or body.vertex_groups.new(name=n) for n in ('MF185_neck','MF185_head')}
        bone_groups={g.index:g for g in body.vertex_groups if g.name in rig.data.bones}
        changed=0
        for v in body.data.vertices:
            z=(body.matrix_world@v.co).z
            if z<=-1.72:continue
            weights=head_weights(z)
            # This sector is the central neck, not shoulders/upper arms.
            for index in [old.group for old in v.groups]:
                if index in bone_groups:bone_groups[index].remove([v.index])
            for name,w in weights.items():
                if w:body.vertex_groups[name].add([v.index],w,'REPLACE')
            changed+=1
        for ob in roots:
            matches=[c for c in ob.constraints if c.type=='CHILD_OF' and c.target==rig and c.subtarget=='chest']
            if len(matches)!=1:raise ValueError('Expected one chest attachment: '+ob.name)
            c=matches[0];c.subtarget='MF185_head'
            c.inverse_matrix=(rig.matrix_world@rig.pose.bones[c.subtarget].matrix).inverted()
        bpy.context.view_layer.update()
        parity=max(abs(ob.matrix_world[i][j]-original[ob.name][i][j]) for ob in roots for i in range(4) for j in range(4))
        if parity>1e-5:raise ValueError('Neutral eye/groom attachment drift')
    return {'weights_changed':changed,'neutral_root_matrix_error':parity,
        'scope':'Reversible derivative weights/rig; accepted coordinates, textures and expression keys unchanged'}


def boots(rig,mats):
    """Reconstruct at rest, then deform once with shin/foot rather than double pose.

    The source footwear contains baked pose coordinates. A later CHILD_OF is
    therefore not a neutral binding. Regenerate the existing authored last;
    keep the rigid footbed and blend only the ankle/shaft transition.
    """
    import bpy
    from wardrobe_finish import finishing
    from wardrobe_studio import smoothstep
    from wardrobe_motion178_controls import bind
    from wardrobe_refinement import neutral
    neutral(rig)
    names=('MF_173_work_boot_','MF_173_boot_')
    for ob in list(bpy.context.scene.objects):
        if ob.name.startswith(names):bpy.data.objects.remove(ob,do_unlink=True)
    finishing(mats,boots_only=True)
    attached=[]
    for ob in list(bpy.context.scene.objects):
        if not ob.name.startswith(names):continue
        side='L' if '_L' in ob.name else 'R' if '_R' in ob.name else None
        if side is None:raise ValueError('Unknown boot side')
        if ob.type=='CURVE':
            bpy.ops.object.select_all(action='DESELECT');ob.select_set(True)
            bpy.context.view_layer.objects.active=ob;bpy.ops.object.convert(target='MESH')
            ob=bpy.context.view_layer.objects.active
        def weights(point):
            w=smoothstep((-12.05-point.z)/.65)
            return {'shin.'+side:1-w,'foot.'+side:w}
        bind(ob,rig,weights);attached.append(ob.name)
    return attached


def audit(out):
    import bpy
    import numpy as np
    from mathutils import Vector
    import wardrobe_motion178 as base
    from wardrobe_motion178_proof import dress_actor
    from wardrobe_underarm179_repair import repair
    from wardrobe185_motion import animate
    from wardrobe_riding_fit import fit_render
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(base.SOURCE),load_ui=False,use_scripts=False)
    base.check_protected();rig,mats,_=base.clean_foundation();dress_actor(rig)
    attached=boots(rig,mats);repair(rig,'repair04')
    names=('MF_continuous_head_neck','MF_aimable_eye_Left','MF_aimable_eye_Right',
           'MF_natural147_hair_temples','MF_natural147_hair_retarget','MF_studio_adult_body')
    inventory={}
    for name in names:
        ob=bpy.data.objects[name]
        bounds=[ob.matrix_world@Vector(p) for p in ob.bound_box]
        inventory[name]={'parent':ob.parent.name if ob.parent else None,
            'matrix_world':[list(r) for r in ob.matrix_world],
            'bounds':[[min(p[k] for p in bounds) for k in range(3)],[max(p[k] for p in bounds) for k in range(3)]],
            'constraints':[{'type':c.type,'target':c.target.name if getattr(c,'target',None) else None,
                            'bone':getattr(c,'subtarget',None)} for c in ob.constraints],
            'modifiers':[(m.name,m.type) for m in ob.modifiers]}
    head=bpy.data.objects[names[0]]
    np.savez_compressed(out/'head-basis.npz',points=np.array([head.matrix_world@v.co for v in head.data.vertices]))
    animate(rig);scene=bpy.context.scene;scene.cycles.samples=8;scene.cycles.device='CPU';scene.render.use_persistent_data=True
    for frame in (1,193,217):
        scene.frame_set(frame);bpy.context.view_layer.update()
        for angle,label in ((0,'front'),(90,'side')):
            fit_render(out,'body-'+label+'-%03d'%frame,angle,(0,.1,-5.2),15.8,(600,900))
    base.check_protected()
    (out/'result.json').write_text(json.dumps({'inventory':inventory,'boots':attached,
        'bones':{b.name:{'head':list(b.head_local),'tail':list(b.tail_local)} for b in rig.data.bones},
        'protected_local_data_exact':True,'visual_gate':'NOT_RUN'},indent=2)+'\n')


def gaze_screen(out):
    import bpy
    import numpy as np
    import wardrobe_motion178 as base
    from wardrobe_motion178_proof import dress_actor
    from wardrobe_underarm179_repair import repair
    from wardrobe185_motion import animate
    from wardrobe_riding_fit import fit_render
    from wardrobe_motion178_controls import render_geometry_paused
    import wardrobe_studio as studio
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(base.SOURCE),load_ui=False,use_scripts=False)
    base.check_protected();rig,mats,_=base.clean_foundation()
    body=bpy.data.objects['MF_studio_adult_body']
    def points():
        bpy.context.view_layer.update();ev=body.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh()
        p=np.array([v.co[:] for v in m.vertices]);ev.to_mesh_clear();return p
    before=points();record=head_control(rig);after=points()
    record['neutral_evaluated_body_error']=float(np.max(abs(after-before)))
    if record['neutral_evaluated_body_error']>2e-5:raise ValueError('Neutral body/head changed')
    dress_actor(rig);repair(rig,'repair04');animate(rig)
    scene=bpy.context.scene;scene.cycles.samples=8;scene.cycles.device='CPU';scene.render.use_persistent_data=True
    for frame in (169,193,217):
        scene.frame_set(frame);bpy.context.view_layer.update()
        center=studio.torso_matrix(-2.7)@__import__('mathutils').Vector((0,.15,-1.1))
        for angle,label in ((0,'front'),(90,'side'),(270,'other'),(180,'rear')):
            fit_render(out,'neck-'+label+'-%03d'%frame,angle,tuple(center),5.8,(600,660))
    base.check_protected();record.update({'protected_local_data_exact':True,'visual_gate':'NOT_RUN','cloth_replay':'NOT_RUN'})
    (out/'result.json').write_text(json.dumps(record,indent=2)+'\n')
