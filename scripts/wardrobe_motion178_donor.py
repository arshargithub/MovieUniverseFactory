"""Fixed adaptation of the existing credited cloth donor; no new assets.

Initial construction screens only. Artist-authored folds are raw material,
not automatic appearance/motion acceptance. No accepted skin/hair edits.
"""
import math


def smooth(v):
    v=max(0.,min(1.,v));return v*v*(3-2*v)


def fit_point(point, contact_fit=False):
    x,y,z=point
    if len(point)!=3 or not all(math.isfinite(v) and abs(v)<10 for v in point):
        raise ValueError('Bounded audited donor coordinates required')
    front=smooth((.4-y)/1.2);lower=smooth((1.4-z)/1.8)
    crown=smooth((z-.8)/1.2)
    px=x*(.98+.13*crown);py=y*.84+.16+.55*crown*front
    pz=z*.85-.70-lower*(1.25*front+1.05*(1-front))
    if contact_fit:
        # Coherent front/back depth fit: the original donor wraps surround a
        # much shallower dummy torso. Do not bury them inside this actor.
        py+=lower*(-1.10*front+.52*(1-front))
        pz-=.23*crown
    # Relocate existing lateral ends as whole coherent regions, not by
    # snapping vertices independently or inventing new shoulder clasps.
    end=smooth((-1.0-z)/1.6)*smooth((abs(x)-.65)/.7)*front
    angle=math.copysign(math.pi*.60*end,x)
    px,py=math.cos(angle)*px-math.sin(angle)*(py-.14),.14+math.sin(angle)*px+math.cos(angle)*(py-.14)
    pz+=1.0*end
    return px,py,pz


def build(recipe,mats,contact_fit=False):
    import bpy,bmesh
    import numpy as np
    from hijab_donor import DONOR,SHA,inspect_glb,connected_groups
    if DONOR.is_symlink() or recipe.digest(DONOR)!=SHA:
        raise ValueError('Pinned existing garment donor changed')
    metadata=inspect_glb(DONOR.read_bytes())
    prior=set(bpy.context.scene.objects)
    # Reproduce the audited arbitrary donor coordinate frame. glTF import
    # converts metres into the active scene's length units; this character
    # scene is1native unit=0.1229m, unlike the original donor audit at1m.
    scale=bpy.context.scene.unit_settings.scale_length
    try:
        bpy.context.scene.unit_settings.scale_length=1.
        bpy.ops.import_scene.gltf(filepath=str(DONOR),import_pack_images=True)
    finally:bpy.context.scene.unit_settings.scale_length=scale
    imported=[ob for ob in bpy.context.scene.objects if ob not in prior and ob.type=='MESH']
    if len(imported)!=1:raise ValueError('Audited single donor mesh required')
    ob=imported[0];world=[ob.matrix_world@v.co for v in ob.data.vertices]
    expected=((-2.1838200092315674,-1.6730645895004272,-3.5770931243896484),
              (2.170639991760254,1.8346062898635864,2.491938352584839))
    measured=tuple(tuple(fn(p[k] for p in world) for k in range(3)) for fn in (min,max))
    if max(abs(measured[r][k]-expected[r][k]) for r in range(2) for k in range(3))>1e-4:
        raise ValueError('Original audited donor coordinate bounds not reproduced')
    ob.parent=None;ob.matrix_world.identity()
    for vertex,p in zip(ob.data.vertices,world):vertex.co=p
    bm=bmesh.new();bm.from_mesh(ob.data)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001)
    groups=connected_groups(bm)
    if [len(g) for g in groups]!=[2481,412]:raise ValueError('Audited donor topology differs')
    bmesh.ops.delete(bm,geom=groups[1],context='VERTS')
    for vertex in bm.verts:vertex.co=fit_point(vertex.co,contact_fit)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bm.to_mesh(ob.data);bm.free()
    ob.name='MF178_existing_donor_shawl';ob.data.materials.clear();ob.data.materials.append(mats['scarf'])
    coords=ob.data.attributes.new('MF_173_material_coords','FLOAT_VECTOR','POINT')
    for vertex,item in zip(ob.data.vertices,coords.data):item.vector=vertex.co
    for face in ob.data.polygons:face.use_smooth=True
    sub=ob.modifiers.new('Preserved authored fold continuity','SUBSURF');sub.levels=1;sub.render_levels=1
    solid=ob.modifiers.new('Thin donor cloth edge','SOLIDIFY');solid.thickness=.012
    return ob,{'donor_sha256':SHA,'credit':metadata['asset']['extras'],
        'scope':'Coherent initial warp of artist-authored folds, not cloth physics or Director acceptance',
        'vertices':len(ob.data.vertices),'faces':len(ob.data.polygons)}
