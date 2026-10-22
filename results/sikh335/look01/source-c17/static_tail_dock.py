"""Reviewed deterministic static tail groom, not a dynamic tail rig."""
import math
import hashlib
import struct


def data_signature(ob):
    """Preserve actual native groom/control data across selected reopen."""
    h=hashlib.sha256()
    h.update(str((ob.data.dimensions,ob.data.bevel_depth,ob.data.bevel_resolution)).encode())
    for row in ob.matrix_world:h.update(struct.pack('<4f',*row))
    for spline in ob.data.splines:
        h.update(str((spline.type,len(spline.points),spline.material_index)).encode())
        for point in spline.points:h.update(struct.pack('<5f',*point.co,point.radius))
    return h.hexdigest()


def soften_dock_surface(bm,matrix,root):
    import bmesh
    local=[v for v in bm.verts if (matrix@v.co-root).length<.50]
    for _ in range(5):
        bmesh.ops.smooth_vert(bm,verts=local,factor=.32,use_axis_x=True,use_axis_y=True,use_axis_z=True)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))


def root_fibers(root):
    import bpy
    from character_assembly import material
    data=bpy.data.curves.new('MF_170_static_tail_fibers','CURVE')
    data.dimensions='3D';data.bevel_depth=.010;data.bevel_resolution=1
    for strand in range(480):
        angle=strand*2.399963229728653
        variation=.5+.5*math.sin(strand*13.7)
        radial=math.sqrt((strand+.5)/480)
        spline=data.splines.new('POLY');spline.points.add(20)
        spline.material_index=strand%4
        for j,p in enumerate(spline.points):
            t=j/20;s=t*(.78+.22*variation)
            spread=radial*(.22+.22*math.sin(math.pi*s))*(1-.65*t**3)
            x=root.x+math.cos(angle+ .18*math.sin(5*s))*spread
            y=root.y-.06+4*s+.14*(1-math.exp(-30*s))+math.sin(angle)*spread*.75
            z=root.z+.14-5.4*s**.8+math.sin(angle)*spread*.45
            p.co=(x,y,z,1);p.radius=(.65+.45*variation)*(1-.90*t)
    ob=bpy.data.objects.new('MF_170_tail_fibers',data)
    bpy.context.scene.collection.objects.link(ob)
    for tone in range(4):
        factor=.82+.12*tone
        mat=material('MF_170_tail_fiber_brown_'+str(tone),tuple(c*factor for c in (.065,.026,.012)))
        shader=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');shader.inputs['Roughness'].default_value=.78
        data.materials.append(mat)
    bpy.data.objects['MF_170_tail_dock'].hide_render=True
    bpy.data.objects['MF_fit_Full Bushy Flowing Horse Tail'].hide_render=True
    return ob.name
