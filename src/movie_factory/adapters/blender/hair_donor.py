"""Pinned, data-only first fit of the acquired hair donor. No external scripts."""
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[4]
ASSET=ROOT/'.runtime/assets/series01-dressing-source/o4saken-long01'
BASE=ROOT/'.runtime/art-direction/series01-facebuilder-trial-01'


def validate(job):
    if job!={'operation':'hair_fit','output_name':'hair-donor-01'}: raise ValueError('Unsupported job')
    out=BASE/'hair-donor-01'
    if out.exists():raise ValueError('No overwrite')
    for path,digest in [(ASSET/'o4saken_long01.obj','3b58e92dae179dd6d0d9b0be07d5996827d8a8dd4158579d6bcc2e48ebd60c17'),
                        (BASE/'cleanup-portable-01/head-baked.blend','51e2a3d4c9df966e44f6a217d3535115bf19eef8e7ef9561cf6da75dc0ebd9b4')]:
        if path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest()!=digest:raise ValueError('Changed input')
    records=json.loads((ASSET/'acquisition.json').read_text())['files']
    for name in ['o4saken_long01.png','o4saken_long01_nrm.png']:
        record=next(r for r in records if r['local']==name)
        if hashlib.sha256((ASSET/name).read_bytes()).hexdigest()!=record['sha256']:raise ValueError('Changed texture')
    return out


def run(job):
    out=validate(job)
    import bpy
    sys.path.insert(0,str(Path(__file__).resolve().parent))
    from likeness_cleanup import geometry_digest,render_views
    out.mkdir()
    bpy.ops.wm.open_mainfile(filepath=str(BASE/'cleanup-portable-01/head-baked.blend'),load_ui=False,use_scripts=False)
    head=bpy.data.objects['FBHead']; before=geometry_digest(head)
    bpy.ops.wm.obj_import(filepath=str(ASSET/'o4saken_long01.obj'),forward_axis='NEGATIVE_Z',up_axis='Y')
    hair=[o for o in bpy.context.selected_objects if o.type=='MESH']
    if len(hair)!=1:raise ValueError('Expected one hair mesh')
    hair=hair[0]; hair.name='MF_hair_donor_04saken'
    # Importer maps source Y-up into Blender Z-up. Uniform first-fit only.
    hair.scale=(.67,.67,.67); hair.location=(0,0,1.40-8.3173*.67)
    mat=bpy.data.materials.new('MF_donor_hair');mat.use_nodes=True
    nodes,links=mat.node_tree.nodes,mat.node_tree.links
    bsdf=nodes.get('Principled BSDF');bsdf.inputs['Roughness'].default_value=.8
    tex=nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(ASSET/'o4saken_long01.png'));tex.image.pack()
    links.new(tex.outputs['Color'],bsdf.inputs['Base Color']);links.new(tex.outputs['Alpha'],bsdf.inputs['Alpha'])
    hair.data.materials.clear();hair.data.materials.append(mat)
    for p in hair.data.polygons:p.use_smooth=True
    scene=bpy.context.scene;scene.camera.data.ortho_scale=4
    render_views(scene,scene.camera,out,'hair-fit')
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'head-hair-fit.blend'))
    assert geometry_digest(head)==before
    (out/'result.json').write_text(json.dumps({'head_preserved':True,'hair_vertices':len(hair.data.vertices),
        'hair_faces':len(hair.data.polygons),'license':'Embedded CC BY 4.0, author 04saken; catalog CC0 discrepancy retained',
        'scope':'Uniform first fit, not final hairstyle or rig'},indent=2))


if __name__=='__main__':
    args=sys.argv[sys.argv.index('--')+1:]
    if len(args)!=1:raise ValueError('One JSON job required')
    run(json.loads(Path(args[0]).read_text()))
