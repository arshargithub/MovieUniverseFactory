"""Bounded static garment reconstruction and side/back hair donor adaptation."""
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/'.runtime/art-direction/series01-facebuilder-trial-01'
HEAD=BASE/'bilateral-04/head-bilateral.blend'
HEAD_SHA='c263b6b715548e8fee58661eadd6f26f8b37c81295ae0fcc2c830a3786561322'
HAIR=ROOT/'.runtime/assets/series01-dressing-source/o4saken-long01'
SCARF=ROOT/'.runtime/assets/series01-dressing-source/scarf-original.glb'


def validate(job):
    if not isinstance(job,dict) or set(job)!={'operation','variant'} or job['operation']!='dressing_renewal' or type(job['variant']) is not int or job['variant'] not in (1,2,3):
        raise ValueError('Unsupported structured job')
    for path,digest in [(HEAD,HEAD_SHA),(HAIR/'o4saken_long01.obj','3b58e92dae179dd6d0d9b0be07d5996827d8a8dd4158579d6bcc2e48ebd60c17'),(HAIR/'o4saken_long01.png','436f34ddbd3d27275ecbfb7ea3e3159dc16ff8039313c003fdea30bcbdcefb10')]:
        if path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest()!=digest:raise ValueError('Source changed')
    out=BASE/f'dressing-renew-{job["variant"]:02}'
    if job['variant']==3:
        import struct
        b=SCARF.read_bytes()
        if SCARF.is_symlink() or hashlib.sha256(b).hexdigest()!='b34727d6d989d33cef5fb77c84bb34194bf8045e4d01ac4a4d7c48c93319e7c7':raise ValueError('Scarf changed')
        n=struct.unpack_from('<I',b,12)[0];doc=json.loads(b[20:20+n])
        if any('uri' in x for k in ('buffers','images') for x in doc.get(k,[])):raise ValueError('External URI')
    if out.exists():raise ValueError('No overwrite')
    return out


def hood_point(t,d,variant=1):
    a=abs(t)
    if a<=math.pi/2:
        x=1.20*math.sin(t);z=1.54*math.cos(t)
    else:
        q=(a-math.pi/2)/.9
        x=math.copysign(1.20+(.45 if variant==1 else .16)*q,t);z=-2.05*q
    fold=(.022+.055*d+.03*max(0,a-1))*math.sin(14*t+2*d)*math.sin(math.pi*d)
    front=-.28
    if variant>1:
        front=-.37-.18*max(0,a-1.3)+.06*math.sin(t*8)
        x+=.04*math.sin(t*10)*(1-d)
        z+=.025*math.cos(t*11)*(1-d)
        fold*=2
    return (x*(1-.20*d)+fold, front+1.50*d+.09*math.sin(9*t+d*3)*math.sin(math.pi*d), z-.20*d+.035*math.sin(18*t+d*4)*math.sin(math.pi*d))


def wrap_point(a,v,variant=1):
    rx=(.65+1.43*v) if variant==1 else (.46+1.62*v)
    ry=(.54+.47*v) if variant==1 else (.39+.70*v)
    phase=v*math.pi*6+2.2*math.sin(a)+.30*math.sin(3*a)
    fold=(.035+.065*v)*math.sin(phase)+.014*math.sin(phase*2.4)
    z=-1.30-1.20*v+.30*v*math.sin(a)+.16*abs(math.sin(a))+.035*math.sin(phase+.8)
    if variant>1:
        z=-1.42-1.28*v+.85*v*math.sin(a)**2+.43*v*math.sin(a)-.12*math.cos(a)+.045*math.sin(phase+.8)
    return ((rx+fold)*math.sin(a),-(ry+fold)*math.cos(a),z)


def make_mesh(name,verts,faces,mat,thickness=.015):
    import bpy
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
    obj=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(obj)
    mesh.materials.append(mat)
    for p in mesh.polygons:p.use_smooth=True
    sub=obj.modifiers.new('Smooth continuous cloth','SUBSURF');sub.levels=1
    solid=obj.modifiers.new('Woven cloth thickness','SOLIDIFY');solid.thickness=thickness
    return obj


def cloth_material():
    import bpy
    mat=bpy.data.materials.new('MF_continuous_indigo');mat.use_nodes=True
    n,l=mat.node_tree.nodes,mat.node_tree.links;p=n.get('Principled BSDF')
    p.inputs['Roughness'].default_value=.92
    noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=18;noise.inputs['Detail'].default_value=2
    ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.008,.020,.054,1);ramp.color_ramp.elements[1].color=(.035,.075,.16,1)
    l.new(noise.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs[0],p.inputs['Base Color'])
    grain=n.new('ShaderNodeTexNoise');grain.inputs['Scale'].default_value=175;grain.inputs['Detail'].default_value=2
    bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.13;bump.inputs['Distance'].default_value=.009
    l.new(grain.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs[0],p.inputs['Normal'])
    return mat


def add_hair(variant=1):
    import bpy
    import bmesh
    from mathutils import Vector
    prior=set(bpy.context.scene.objects)
    bpy.ops.wm.obj_import(filepath=str(HAIR/'o4saken_long01.obj'),forward_axis='NEGATIVE_Z',up_axis='Y')
    meshes=[o for o in bpy.context.scene.objects if o not in prior and o.type=='MESH']
    if len(meshes)!=1:raise ValueError('Expected one donor mesh')
    obj=meshes[0];obj.name='MF_side_back_hair_04saken'
    for v in obj.data.vertices:
        p=obj.matrix_world@v.co
        v.co=(p.x*.67,p.y*.67,p.z*.67+1.40-8.3173*.67)
    obj.matrix_world.identity()
    bm=bmesh.new();bm.from_mesh(obj.data)
    # Remove entire connected frontal cards, avoiding cut fringe tips over the face.
    unseen=set(bm.verts);removed=[]
    while unseen:
        root=unseen.pop();group={root};stack=[root]
        while stack:
            for edge in stack.pop().link_edges:
                for v in edge.verts:
                    if v in unseen:unseen.remove(v);group.add(v);stack.append(v)
        centre=sum((v.co for v in group),Vector())/len(group)
        if abs(centre.x)<.58 and centre.y<-.10:removed.extend(group)
    bmesh.ops.delete(bm,geom=removed,context='VERTS')
    for v in bm.verts:
        x,y,z=v.co
        if abs(x)>.35:
            x*=1.19
            x+=math.copysign(.07*math.sin((z+1)*3)**2,x)
        if variant>1 and z<.6:
            t=max(0.,min(1.,(.6-z)/2))
            x+=math.copysign(.09*math.sin(t*8)+.10*t,x)
            y+=.08*math.sin(t*7)
            z=.6+(z-.6)*1.35
        v.co=(x,y+.12,z)
    bm.to_mesh(obj.data);bm.free()
    mat=bpy.data.materials.new('MF_chestnut_donor');mat.use_nodes=True
    n,l=mat.node_tree.nodes,mat.node_tree.links;p=n.get('Principled BSDF');p.inputs['Roughness'].default_value=.65
    tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(HAIR/'o4saken_long01.png'));tex.image.pack()
    tint=n.new('ShaderNodeMixRGB');tint.blend_type='MULTIPLY';tint.inputs[0].default_value=.65;tint.inputs[2].default_value=(.40,.23,.13,1)
    l.new(tex.outputs['Color'],tint.inputs[1]);l.new(tint.outputs[0],p.inputs['Base Color']);l.new(tex.outputs['Alpha'],p.inputs['Alpha'])
    if variant>1:
        ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.006,.0025,.0012,1);ramp.color_ramp.elements[1].color=(.24,.11,.047,1)
        l.new(tex.outputs['Color'],ramp.inputs[0]);l.new(ramp.outputs[0],p.inputs['Base Color'])
    obj.data.materials.clear();obj.data.materials.append(mat)
    for p in obj.data.polygons:p.use_smooth=True
    return {'vertices':len(obj.data.vertices),'removed_vertices':len(removed),'credit':'o4saken_long01 by 04saken, CC BY 4.0; selected cards removed, fit/deformation/material by MovieUniverseFactory; embedded license overrides catalog CC0 claim.'}


def scan_drape():
    import bpy
    import bmesh
    from mathutils import Vector
    prior=set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(SCARF),import_pack_images=True)
    objects=[o for o in bpy.context.scene.objects if o not in prior and o.type=='MESH']
    if len(objects)!=1:raise ValueError('One scarf mesh required')
    obj=objects[0];points=[obj.matrix_world@v.co for v in obj.data.vertices]
    low=[min(p[i] for p in points) for i in range(3)];high=[max(p[i] for p in points) for i in range(3)]
    scale=2.5/(high[0]-low[0]);obj.parent=None;obj.matrix_world.identity()
    for vertex,p in zip(obj.data.vertices,points):
        x=(p.x-(low[0]+high[0])/2)*scale
        y=(p.y-(low[1]+high[1])/2)*scale+.25
        z=(p.z-high[2])*scale+1.55
        t=max(0.,min(1.,(.9-z)/1.5));front=max(0.,min(1.,(.65-y)/.8))
        x*=1.20+.12*t
        y+=.38-.25*t*front
        z-=(1.15+.80*front)*t
        vertex.co=Vector((x,y,z))
    bm=bmesh.new();bm.from_mesh(obj.data)
    bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.co.z<-2.75],context='VERTS')
    bm.to_mesh(obj.data);bm.free();obj.name='MF_continuous_scan_drape'
    mat=obj.data.materials[0];p=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    for socket in ('Base Color','Emission Color','Emission Strength'):
        for link in list(p.inputs[socket].links):mat.node_tree.links.remove(link)
    p.inputs['Base Color'].default_value=(.025,.055,.13,1);p.inputs['Emission Color'].default_value=(0,0,0,1);p.inputs['Emission Strength'].default_value=0
    p.inputs['Roughness'].default_value=.87
    assert p.inputs['Normal'].is_linked
    return 'Tijerín Art Studio, Balaclava - scarf as a hood - 3D scan, https://skfb.ly/oP7Yu, CC BY 4.0; refit, lower drape deformation, hem trim and indigo recolor by MovieUniverseFactory. Original normal map retained.'


def run(job):
    out=validate(job)
    import bpy
    sys.path.insert(0,str(Path(__file__).resolve().parent))
    from likeness_cleanup import geometry_digest,render_views
    bpy.ops.wm.open_mainfile(filepath=str(HEAD),load_ui=False,use_scripts=False)
    head=bpy.data.objects['FBHead'];before=geometry_digest(head);material=head.data.materials[0]
    values={k.name:k.value for k in head.data.shape_keys.key_blocks}
    for obj in list(bpy.context.scene.objects):
        if obj.name.startswith(('MF_scarf_Tijerin','MF_hood_lining','MF_shoulder_fold')):bpy.data.objects.remove(obj,do_unlink=True)
    mat=cloth_material()
    nu,nv=100,30
    verts=[hood_point(-2.47+4.94*i/nu,j/nv,job['variant']) for i in range(nu+1) for j in range(nv+1)]
    faces=[(i*(nv+1)+j,(i+1)*(nv+1)+j,(i+1)*(nv+1)+j+1,i*(nv+1)+j+1) for i in range(nu) for j in range(nv)]
    # Close rear with a fan; its perimeter is shared with the hood surface.
    centre=len(verts);verts.append((0,1.26,-.6))
    for i in range(nu):faces.append((i*(nv+1)+nv,(i+1)*(nv+1)+nv,centre))
    make_mesh('MF_continuous_hood',verts,faces,mat)
    na,nr=128,48
    verts=[wrap_point(2*math.pi*i/na,j/nr,job['variant']) for i in range(na) for j in range(nr+1)]
    faces=[(i*(nr+1)+j,((i+1)%na)*(nr+1)+j,((i+1)%na)*(nr+1)+j+1,i*(nr+1)+j+1) for i in range(na) for j in range(nr)]
    make_mesh('MF_continuous_shoulder_wrap',verts,faces,mat)
    hair=add_hair(job['variant'])
    scarf_credit=None
    if job['variant']==3:
        bpy.data.objects.remove(bpy.data.objects['MF_continuous_hood'],do_unlink=True)
        scarf_credit=scan_drape()
    scene=bpy.context.scene;scene.camera.data.ortho_scale=4.9
    if job['variant']==3:scene.cycles.transparent_max_bounces=32
    scene.render.resolution_x,scene.render.resolution_y=640,800;scene.cycles.samples=24
    out.mkdir();render_views(scene,scene.camera,out,'review')
    assert geometry_digest(head)==before and head.data.materials[0]==material
    assert values=={k.name:k.value for k in head.data.shape_keys.key_blocks}
    assert hashlib.sha256(HEAD.read_bytes()).hexdigest()==HEAD_SHA
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'head-dressed.blend'))
    (out/'result.json').write_text(json.dumps({'source_sha256':HEAD_SHA,'face_geometry_digest':before,'face_material_unchanged':True,'shape_values':values,'hair':hair,'scarf_credit':scarf_credit,'scope':'Static garment/hair candidate; no physics, animation or complete 360-degree qualification; painted scalp retained'},indent=2))


if __name__=='__main__':
    args=sys.argv[sys.argv.index('--')+1:]
    if len(args)!=1:raise ValueError('One structured job file')
    run(json.loads(Path(args[0]).read_text()))
