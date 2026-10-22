"""Data-only import of pinned CC0 MakeHuman core mesh/rig, no addon execution."""
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[4]
DATA=ROOT/'.runtime/assets/series01-body-mpfb'
BASE=ROOT/'.runtime/art-direction/series01-facebuilder-trial-01'
HASHES={'base.obj':'8e761e6624b8f54536409135d1636da63b32486a90d4897f84e121d144f6fb4c',
        'rig.default.json':'8b949de35c2dd70dbb5094e57a8586c3b9a9f650775a293212581a8f67be6797',
        'weights.default.json':'154b866774a8c2b055a8e86419f22a87b76c60440fdcb70bcb78345f00924e89'}


def validate(job):
    if job != {'operation':'inspect_core01'}:raise ValueError('Fixed core inspection only')
    for name,sha in HASHES.items():
        p=DATA/name
        if p.is_symlink() or hashlib.sha256(p.read_bytes()).hexdigest()!=sha:raise ValueError('Source changed')
    out=BASE/'body154-core01'
    if out.exists():raise ValueError('Do not overwrite evidence')
    return out


def parse_obj(text):
    verts=[];faces=[];groups={};group=None
    for line in text.splitlines():
        f=line.split()
        if not f:continue
        if f[0]=='v':
            x,y,z=map(float,f[1:4]);verts.append((x*.1,-z*.1,y*.1))
        elif f[0]=='g':group=f[1];groups.setdefault(group,set())
        elif f[0]=='f':
            ids=[int(s.split('/')[0])-1 for s in f[1:]]
            if group is not None:groups[group].update(ids)
            if group=='body':faces.append(ids)
    if len(verts)!=19158 or not faces:raise ValueError('Unexpected basemesh topology')
    if not all(math.isfinite(x) for p in verts for x in p):raise ValueError('Nonfinite data')
    return verts,faces,groups


def endpoint(spec,verts,groups):
    strategy=spec['strategy']
    if strategy=='CUBE':indices=groups[spec['cube_name']]
    elif strategy=='VERTEX':indices=[spec['vertex_index']]
    elif strategy=='MEAN':indices=spec['vertex_indices']
    else:raise ValueError('Unexpected endpoint strategy')
    return tuple(sum(verts[i][j] for i in indices)/len(indices) for j in range(3))


def main():
    import bpy
    from mathutils import Vector
    out=validate(json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text()));out.mkdir()
    verts,faces,groups=parse_obj((DATA/'base.obj').read_text())
    definitions=json.loads((DATA/'rig.default.json').read_text())
    weights=json.loads((DATA/'weights.default.json').read_text())['weights']
    bpy.ops.wm.read_factory_settings(use_empty=True)
    mesh=bpy.data.meshes.new('MF_mpfb_core_body');mesh.from_pydata(verts,[],faces);mesh.update()
    ob=bpy.data.objects.new(mesh.name,mesh);bpy.context.scene.collection.objects.link(ob)
    arm=bpy.data.armatures.new('MF_mpfb_core_rig');rig=bpy.data.objects.new(arm.name,arm)
    bpy.context.scene.collection.objects.link(rig);bpy.context.view_layer.objects.active=rig;rig.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    for name,spec in definitions.items():
        bone=arm.edit_bones.new(name);bone.head=endpoint(spec['head'],verts,groups);bone.tail=endpoint(spec['tail'],verts,groups);bone.roll=spec['roll']
        if (bone.tail-bone.head).length<1e-5:raise ValueError('Zero length bone '+name)
    for name,spec in definitions.items():
        bone=arm.edit_bones[name]
        if spec['parent']:bone.parent=arm.edit_bones[spec['parent']]
        bone.use_connect=spec['use_connect']
    bpy.ops.object.mode_set(mode='OBJECT')
    for name,pairs in weights.items():
        if name not in arm.bones:continue
        group=ob.vertex_groups.new(name=name)
        for i,w in pairs:group.add([i],w,'REPLACE')
    mod=ob.modifiers.new('Core authored weights','ARMATURE');mod.object=rig;ob.parent=rig
    for p in mesh.polygons:p.use_smooth=True
    used={i for face in faces for i in face}
    unweighted=[i for i in used if sum(g.weight for g in mesh.vertices[i].groups)<.01]
    assert not unweighted
    def evaluated():
        bpy.context.view_layer.update(); ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
        return [tuple(ev.data.vertices[i].co) for i in sorted(used)]
    neutral=evaluated()
    edits={'upperleg01.L':(.60,0,.15),'upperleg01.R':(.60,0,-.15),
           'lowerleg01.L':(-.80,0,0),'lowerleg01.R':(-.80,0,0),
           'spine02':(.15,0,0),'upperarm01.L':(.25,0,0),'upperarm01.R':(.25,0,0)}
    for name,rotation in edits.items():
        bone=rig.pose.bones[name];bone.rotation_mode='XYZ';bone.rotation_euler=rotation
    posed=evaluated();assert all(math.isfinite(x) for p in posed for x in p)
    moved=sum((Vector(b)-Vector(a)).length>1e-5 for a,b in zip(neutral,posed))
    assert moved>500
    for name in edits:rig.pose.bones[name].rotation_euler=(0,0,0)
    returned=evaluated();error=max((Vector(a)-Vector(b)).length for a,b in zip(neutral,returned));assert error<1e-7
    bpy.context.preferences.filepaths.save_version=0
    native=out/'core-body-rig.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native),check_existing=False)
    bpy.ops.wm.open_mainfile(filepath=str(native),load_ui=False,use_scripts=False)
    assert len(bpy.data.objects['MF_mpfb_core_rig'].data.bones)==len(definitions)
    (out/'result.json').write_text(json.dumps({'status':'TECHNICAL_CANDIDATE_NOT_CHARACTER_ACCEPTANCE',
        'source_hashes':HASHES,'vertex_count':len(verts),'body_faces':len(faces),
        'body_vertices':len(used),'bones':len(definitions),'unweighted_body_vertices':len(unweighted),
        'moved_vertices':moved,'neutral_return_max_error':error,'fresh_open':True,
        'native_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),
        'addon_installed':False,'upstream_code_executed':False,
        'limitations':['Not integrated with accepted Pashtun bust','Not a qualified riding pose','Garment weights not yet transferred','No IK helpers or full MPFB addon features']},indent=2)+'\n')


if __name__=='__main__':main()
