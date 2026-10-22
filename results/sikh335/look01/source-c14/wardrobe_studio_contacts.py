"""Fixed static stirrup registration to the new costume173 footbed.

This is authored static contact, not forces, continuous grasp or motion proof.
"""


def fit_contacts(objects,rig,leather):
    import bpy
    from mathutils import Matrix,Vector
    from wardrobe_riding_fit import fit_static_contacts
    fit_static_contacts(objects,rig,leather)
    stirrup=next(ob for ob in objects if ob['source_object']=='saddle.stirrup')
    cache=bpy.data.objects.get('MF_173_static_stirrup_rest')
    if cache is None:
        data=stirrup.data.copy()
        for v in data.vertices:v.co=stirrup.matrix_world@v.co
        cache=bpy.data.objects.new('MF_173_static_stirrup_rest',data);bpy.context.collection.objects.link(cache)
        cache.hide_render=True;cache.hide_set(True)
    rest=[v.co.copy() for v in cache.data.vertices];stirrup.matrix_world=Matrix.Identity(4)
    contacts={}
    for side,sign in (('L',1),('R',-1)):
        boot=bpy.data.objects['MF_173_work_boot_'+side]
        target=Vector(boot['static_footbed_support_world']);normal=Vector(boot['static_footbed_normal_world'])
        target+=normal*.015
        ids=[i for i,p in enumerate(rest) if sign*p.x>0]
        center=Vector(tuple((min(rest[i][k] for i in ids)+max(rest[i][k] for i in ids))/2 for k in range(3)))
        center.z=min(rest[i].z for i in ids)+.10
        delta=rig.matrix_world@rig.pose.bones['foot.'+side].matrix@rig.data.bones['foot.'+side].matrix_local.inverted()@rig.matrix_world.inverted()
        rotation=delta.to_quaternion().to_matrix()
        for i in ids:stirrup.data.vertices[i].co=target+rotation@(rest[i]-center)
        top=Vector((center.x,center.y,max(rest[i].z for i in ids)-.10))
        anchor=target+rotation@(top-center)
        strap=bpy.data.objects['MF_fit_stirrup_leather_'+side]
        strap.data.splines[0].points[-1].co=(*anchor,1.)
        contacts[side]={'footbed_support_world':list(target),'normal_world':list(normal),'stirrup_top_attachment_world':list(anchor),'status':'AUTHORED_STATIC_NOT_DYNAMIC'}
    stirrup.data.update();bpy.context.view_layer.update()
    return contacts
