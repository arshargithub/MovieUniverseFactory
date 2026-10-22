"""Pinned GLB scarf diagnostic/adaptation; no embedded scripts or external URIs."""
import hashlib
import math
import json
from pathlib import Path
import struct
import sys

ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/'.runtime/art-direction/series01-facebuilder-trial-01'
SOURCE=ROOT/'.runtime/assets/series01-dressing-source/scarf-original.glb'
SHA='b34727d6d989d33cef5fb77c84bb34194bf8045e4d01ac4a4d7c48c93319e7c7'


def validate(job):
    if not isinstance(job,dict) or set(job)!={'operation','output_name'} or job['operation']!='scarf_fit':raise ValueError('Invalid job')
    if job['output_name'] not in {'scarf-fit-01','scarf-fit-02','scarf-fit-03','scarf-reconstruct-01','scarf-reconstruct-02','scarf-reconstruct-03'}:raise ValueError('Invalid output')
    out=BASE/job['output_name']
    if out.exists():raise ValueError('No overwrite')
    b=SOURCE.read_bytes()
    if SOURCE.is_symlink() or hashlib.sha256(b).hexdigest()!=SHA:raise ValueError('Source changed')
    n,_=struct.unpack_from('<II',b,12); doc=json.loads(b[20:20+n])
    if any('uri' in x for k in ['buffers','images'] for x in doc.get(k,[])):raise ValueError('External URI prohibited')
    if sum(a.get('count',0) for a in doc['accessors'])>2_000_000:raise ValueError('Complexity cap')
    return out,doc['asset']


def cheek_delta(x,y,z):
    """Small local hollow above the jaw; protect central features and upper face."""
    side=max(0.,min(1.,(abs(x)-.25)/.3))
    front=max(0.,min(1.,(.1-y)/.5))
    t=max(0.,min(1.,(z+.8)/1.0))
    height=math.sin(math.pi*t)**4 if -.8<z<.2 else 0.
    weight=side*front*height
    return (-x*.025*weight,.030*weight,0.)


def reconstruct(scarf,mat):
    import bpy
    import bmesh
    bm=bmesh.new();bm.from_mesh(scarf.data)
    # Open the scanned neck bib, retaining side/back hood fold geometry.
    cut=[]
    for v in bm.verts:
        x,y,z=v.co
        width=.84+.08*max(0.,-z)
        if y<.65 and abs(x)<width and -1.8<z<.65:cut.append(v)
    bmesh.ops.delete(bm,geom=cut,context='VERTS')
    boundary=[v for v in bm.verts if any(e.is_boundary for e in v.link_edges)]
    for _ in range(8):
        bmesh.ops.smooth_vert(bm,verts=boundary,factor=.45,use_axis_x=True,use_axis_y=True,use_axis_z=True)
    bm.to_mesh(scarf.data);bm.free()
    # Continuous inner hood lining behind the retained scan closes scan gaps.
    from head_dressing import hood_point
    verts=[hood_point(-2+4*i/80,j/16) for i in range(81) for j in range(17)]
    mesh=bpy.data.meshes.new('MF_hood_lining')
    mesh.from_pydata(verts,[],[(i*17+j,(i+1)*17+j,(i+1)*17+j+1,i*17+j+1) for i in range(80) for j in range(16)])
    mesh.update();obj=bpy.data.objects.new('MF_hood_lining',mesh);bpy.context.scene.collection.objects.link(obj)
    mesh.materials.append(mat)
    for p in mesh.polygons:p.use_smooth=True
    # Three overlapping shaped shoulder folds, not a flat chest panel.
    for layer in range(3):
        verts=[];faces=[]
        for i in range(65):
            x=-1.75+3.5*i/64
            for j in range(9):
                t=j/8
                z=-1.43-.25*layer+.18*x+.15*x*x-.40*t
                y=-.80+.30*x*x-.10*math.sin(t*math.pi)-.025*math.sin(x*8+layer)
                verts.append((x,y,z))
        for i in range(64):
            for j in range(8):faces.append((i*9+j,(i+1)*9+j,(i+1)*9+j+1,i*9+j+1))
        mesh=bpy.data.meshes.new('MF_shawl_fold');mesh.from_pydata(verts,[],faces);mesh.update()
        obj=bpy.data.objects.new('MF_shoulder_fold',mesh);bpy.context.scene.collection.objects.link(obj)
        mesh.materials.append(mat)
        for p in mesh.polygons:p.use_smooth=True
        obj.modifiers.new('Thin cloth','SOLIDIFY').thickness=.012


def run(job):
    out,meta=validate(job)
    import bpy
    from mathutils import Vector
    sys.path.insert(0,str(Path(__file__).resolve().parent))
    from likeness_cleanup import geometry_digest,render_views
    headpath=BASE/'cleanup-portable-01/head-baked.blend'
    if hashlib.sha256(headpath.read_bytes()).hexdigest()!='51e2a3d4c9df966e44f6a217d3535115bf19eef8e7ef9561cf6da75dc0ebd9b4':raise ValueError('Head changed')
    out.mkdir()
    bpy.ops.wm.open_mainfile(filepath=str(headpath),load_ui=False,use_scripts=False)
    head=bpy.data.objects['FBHead']; before=geometry_digest(head)
    prior=set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(SOURCE),import_pack_images=True)
    meshes=[o for o in bpy.context.scene.objects if o not in prior and o.type=='MESH']
    if len(meshes)!=1:raise ValueError('Expected single scarf mesh')
    scarf=meshes[0]
    points=[scarf.matrix_world@v.co for v in scarf.data.vertices]
    low=[min(p[i] for p in points) for i in range(3)]; high=[max(p[i] for p in points) for i in range(3)]
    scale=2.5/(high[0]-low[0])
    scarf.parent=None;scarf.matrix_world.identity()
    for v,p in zip(scarf.data.vertices,points):
        v.co=Vector(((p.x-(low[0]+high[0])/2)*scale,(p.y-(low[1]+high[1])/2)*scale+.25,(p.z-high[2])*scale+1.55))
    if job['output_name']!='scarf-fit-01':
        for v in scarf.data.vertices:
            t=max(0.,min(1.,(.9-v.co.z)/1.5))
            v.co.x*=1.12
            v.co.y+=.42
            v.co.z-=(1.35 if job['output_name']=='scarf-fit-03' or job['output_name'].startswith('scarf-reconstruct') else .6)*t
            if job['output_name']=='scarf-fit-03' or job['output_name'].startswith('scarf-reconstruct'):
                v.co.x*=1.08
        # Remove dangling tied ends in this derivative, preserving original GLB.
        import bmesh
        bm=bmesh.new();bm.from_mesh(scarf.data)
        bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.co.z < -2.4],context='VERTS')
        bm.to_mesh(scarf.data);bm.free()
    scarf.name='MF_scarf_Tijerin_derivative'
    # Neutral indigo reveals actual folds; retain source plaid only in original GLB.
    mat=bpy.data.materials.new('MF_indigo_scan_cloth');mat.use_nodes=True
    bsdf=mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value=(.025,.055,.13,1)
    bsdf.inputs['Roughness'].default_value=.9
    scarf.data.materials.clear();scarf.data.materials.append(mat)
    scene=bpy.context.scene;scene.camera.data.ortho_scale=4.7
    if job['output_name'].startswith('scarf-reconstruct'):
        reconstruct(scarf,mat)
        render_views(scene,scene.camera,out,'framing-only')
        assert geometry_digest(head)==before
        head.shape_key_add(name='Basis')
        key=head.shape_key_add(name='MF_lower_cheek_definition_candidate')
        distances=[]
        for v,k in zip(head.data.vertices,key.data):
            delta=Vector(cheek_delta(*v.co));k.co=v.co+delta;distances.append(delta.length)
        key.value=1
        render_views(scene,scene.camera,out,'jaw-candidate')
        bpy.ops.wm.save_as_mainfile(filepath=str(out/'head-reconstruction-candidate.blend'))
        (out/'result.json').write_text(json.dumps({'source':meta,'source_sha256':SHA,
            'base_vertices_unchanged':all((v.co-b.co).length<1e-8 for v,b in zip(head.data.vertices,head.data.shape_keys.key_blocks['Basis'].data)),
            'shape_key':key.name,'maximum_displacement':max(distances),'source_head_preserved':hashlib.sha256(headpath.read_bytes()).hexdigest()=='51e2a3d4c9df966e44f6a217d3535115bf19eef8e7ef9561cf6da75dc0ebd9b4',
            'scope':'Open hood/shoulder reconstruction blockout and reversible cheek definition; not approved'},indent=2))
        return
    render_views(scene,scene.camera,out,'scarf-fit')
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'head-scarf-fit.blend'))
    assert geometry_digest(head)==before
    (out/'result.json').write_text(json.dumps({'source':meta,'source_sha256':SHA,'original_bounds':[low,high],
      'uniform_scale':scale,'vertices':len(scarf.data.vertices),'polygons':len(scarf.data.polygons),
      'head_preserved':True,'changes':'Fit and plain indigo; variants 02/03 widen, shift back, lower neck wrap and trim dangling ends; original retained'},indent=2))


if __name__=='__main__':
    args=sys.argv[sys.argv.index('--')+1:]
    if len(args)!=1:raise ValueError('One JSON file')
    run(json.loads(Path(args[0]).read_text()))
