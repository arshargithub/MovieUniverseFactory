"""Reviewed, fixed MPFB setup/proof operations; no arbitrary paths or code input."""
import hashlib
import importlib
import json
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / '.runtime/assets/series01-sikh263-donors/mpfb-2.0.18.zip'
ARCHIVE_SHA = 'c075b3e9b94b8e5556a5f03f4653602d02ea306de08126e8f55ed6dee28a2dad'
INSTALLED = Path('/Users/adisharma/Library/Application Support/Blender/5.2/extensions/user_default/mpfb')
MODULE = 'bl_ext.user_default.mpfb'
USER_DATA = ROOT / '.runtime/mpfb-user-data'


def validate(job):
    if (not isinstance(job, dict) or set(job) != {'operation', 'attempt'}
            or job['operation'] not in {'configure', 'prove', 'reopen'}
            or type(job['attempt']) is not int or not 1 <= job['attempt'] <= 10):
        raise ValueError('Only fixed setup operations and attempts1..10 are accepted')
    return ROOT / '.runtime/art-direction/series01-sikh264' / f"proof-{job['attempt']:02d}"


def verify_sources():
    if hashlib.sha256(ARCHIVE.read_bytes()).hexdigest() != ARCHIVE_SHA:
        raise ValueError('Archive digest mismatch')
    with zipfile.ZipFile(ARCHIVE) as package:
        checked = 0
        for item in package.infolist():
            if item.is_dir():
                continue
            rel = Path(item.filename)
            if rel.is_absolute() or '..' in rel.parts or not (INSTALLED / rel).is_relative_to(INSTALLED):
                raise ValueError('Invalid archive member')
            if (INSTALLED / rel).read_bytes() != package.read(item):
                raise ValueError('Installed extension differs: ' + item.filename)
            checked += 1
    manifest = json.loads((ROOT / 'results/sikh263/file-manifest.json').read_text())
    for item in manifest['files']:
        path = (ROOT / item['path']).resolve()
        if not path.is_relative_to(ROOT / '.runtime/assets/series01-sikh263-donors'):
            raise ValueError('Unbounded donor path')
        if hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']:
            raise ValueError('Donor changed: ' + item['path'])
    return checked


def main(job):
    out = validate(job)
    checked = verify_sources()
    import bpy
    import addon_utils
    if bpy.app.online_access:
        raise ValueError('Launch with --offline-mode')
    addon_utils.enable(MODULE, default_set=False)
    mpfb = importlib.import_module(MODULE)
    services = importlib.import_module(MODULE + '.services')
    common = {'blender': bpy.app.version_string, 'mpfb': list(mpfb.VERSION),
              'verified_extension_files': checked, 'archive_sha256': ARCHIVE_SHA,
              'online_access': bpy.app.online_access, 'production_acceptance': False}
    out.mkdir(parents=True, exist_ok=True)
    result_path = out / (job['operation'] + '.json')
    if result_path.exists():
        raise ValueError('Preserve existing evidence; use a new attempt')
    if job['operation'] == 'configure':
        USER_DATA.mkdir(parents=True, exist_ok=True)
        mpfb.set_preference('mpfb_user_data', str(USER_DATA))
        mpfb.set_preference('mh_auto_user_data', False)
        bpy.ops.wm.save_userpref()
        result = {**common, 'user_data': str(USER_DATA), 'preferences_saved': True}
    elif job['operation'] == 'prove':
        if (out / 'male-base.blend').exists():
            raise ValueError('Preserve prior native')
        if services.LocationService.get_user_home() != str(USER_DATA):
            raise ValueError('SSD data preference not active in fresh process')
        for obj in list(bpy.data.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        macro = services.TargetService.get_default_macro_info_dict()
        # Generic tool-proof settings, not an ethnicity or accepted character preset.
        macro.update(gender=1.0, age=0.5, muscle=0.65, weight=0.5, height=0.6)
        body = services.HumanService.create_human(macro_detail_dict=macro)
        body.name = 'MPFB264_Male_Compatibility_Control'

        def coordinates():
            bpy.context.view_layer.update()
            evaluated = body.evaluated_get(bpy.context.evaluated_depsgraph_get())
            mesh = evaluated.to_mesh()
            points = [v.co.copy() for v in mesh.vertices]
            evaluated.to_mesh_clear()
            return points

        props = importlib.import_module(MODULE + '.entities.objectproperties').HumanObjectProperties
        before = coordinates()
        props.set_value('height', 0.7, entity_reference=body)
        services.TargetService.reapply_macro_details(body)
        after = coordinates()
        delta = max((a - b).length for a, b in zip(before, after, strict=True))
        if delta < 0.001:
            raise ValueError('Morph control failed to change geometry')
        props.set_value('height', 0.6, entity_reference=body)
        services.TargetService.reapply_macro_details(body)
        rig = services.HumanService.add_builtin_rig(body, 'default')
        donors = []
        for name in ('rehmanpolanski_beard_viking', 'rehmanpolanski_moustache_viking'):
            path = ROOT / '.runtime/assets/series01-sikh263-donors/bodyparts05/clothes' / name / (name + '.mhclo')
            donor = services.HumanService.add_mhclo_asset(str(path), body, asset_type='Hair', subdiv_levels=0)
            donors.append({'name': donor.name, 'vertices': len(donor.data.vertices),
                           'materials': len(donor.data.materials),
                           'armature_modifiers': sum(m.type == 'ARMATURE' for m in donor.modifiers)})
        bpy.ops.file.pack_all()
        bpy.ops.wm.save_as_mainfile(filepath=str(out / 'male-base.blend'))
        result = {**common, 'macro_settings': macro, 'body_vertices': len(body.data.vertices),
                  'shape_keys': len(body.data.shape_keys.key_blocks), 'morph_max_delta_m': delta,
                  'bones': len(rig.data.bones), 'donors': donors,
                  'user_data': services.LocationService.get_user_home(),
                  'objects': sorted(o.name for o in bpy.data.objects),
                  'native_sha256': hashlib.sha256((out / 'male-base.blend').read_bytes()).hexdigest()}
    else:
        proof = json.loads((out / 'prove.json').read_text())
        path = out / 'male-base.blend'
        if hashlib.sha256(path.read_bytes()).hexdigest() != proof['native_sha256']:
            raise ValueError('Native changed before reopen')
        bpy.ops.wm.open_mainfile(filepath=str(path))
        objects = sorted(o.name for o in bpy.data.objects)
        if objects != proof['objects']:
            raise ValueError('Reopened object inventory differs')
        body = bpy.data.objects['MPFB264_Male_Compatibility_Control']
        if len(body.data.vertices) != proof['body_vertices'] or len(body.data.shape_keys.key_blocks) != proof['shape_keys']:
            raise ValueError('Body or editable morph inventory differs')
        result = {**common, 'object_inventory_matches': True,
                  'body_vertices': len(body.data.vertices), 'shape_keys': len(body.data.shape_keys.key_blocks),
                  'packed_images': sum(bool(i.packed_file) for i in bpy.data.images),
                  'native_sha256': proof['native_sha256']}
    result_path.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    args = sys.argv[sys.argv.index('--') + 1:]
    if len(args) != 1:
        raise ValueError('One structured JSON operation required')
    main(json.loads(args[0]))
