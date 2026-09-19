"""Pinned GLB scarf diagnostic/adaptation; no embedded scripts or external URIs."""
import hashlib
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
    if job['output_name'] not in {'scarf-fit-01','scarf-fit-02','scarf-fit-03'}:raise ValueError('Invalid output')
    out=BASE/job['output_name']
    if out.exists():raise ValueError('No overwrite')
    b=SOURCE.read_bytes()
    if SOURCE.is_symlink() or hashlib.sha256(b).hexdigest()!=SHA:raise ValueError('Source changed')
    n,_=struct.unpack_from('<II',b,12); doc=json.loads(b[20:20+n])
    if any('uri' in x for k in ['buffers','images'] for x in doc.get(k,[])):raise ValueError('External URI prohibited')
    if sum(a.get('count',0) for a in doc['accessors'])>2_000_000:raise ValueError('Complexity cap')
    return out,doc['asset']


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
            v.co.z-=(1.35 if job['output_name']=='scarf-fit-03' else .6)*t
            if job['output_name']=='scarf-fit-03':
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
