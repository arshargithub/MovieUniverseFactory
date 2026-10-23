"""Reviewed numeric authoring vocabulary. Never executes recipe code or paths.

This is a transport, not a choreography algorithm or quality judge. Native
recipes and target names must additionally be admitted in the production plan.
"""
import json
import math
from pathlib import Path


def vector(value, size, bound):
    return (isinstance(value, list) and len(value) == size and
            all(type(x) in (int, float) and math.isfinite(x) and abs(x) <= bound for x in value))


def validate(recipe):
    if not isinstance(recipe, dict) or set(recipe) != {'operation', 'frame', 'width', 'height', 'samples', 'edits'}:
        raise ValueError('PATCH_FIELDS')
    for key, lo, hi in [('frame', 252, 441), ('width', 64, 1080), ('height', 64, 1920), ('samples', 1, 32)]:
        if type(recipe[key]) is not int or not lo <= recipe[key] <= hi:
            raise ValueError('PATCH_BOUND:' + key)
    if recipe['operation'] != 'nihang_patch' or not isinstance(recipe['edits'], list) or not 1 <= len(recipe['edits']) <= 4096:
        raise ValueError('PATCH_OPERATION_OR_COUNT')
    for edit in recipe['edits']:
        if not isinstance(edit, dict): raise ValueError('PATCH_EDIT')
        kind = edit.get('kind')
        name = edit.get('target')
        if not isinstance(name, str) or not name or len(name) > 128 or any(c in name for c in '/\\\n'):
            raise ValueError('PATCH_TARGET')
        if kind == 'repair_bbone_targets':
            if set(edit) != {'kind','target'} or name != 'horse.rig':
                raise ValueError('PATCH_REPAIR_FIELDS')
        elif kind=='neutral_garment_proof':
            if set(edit)!={'kind','target','phase'} or name!='mounted leader' or edit['phase'] not in {'neutral','bend'}:
                raise ValueError('PATCH_NEUTRAL_FIELDS')
        elif kind=='neutral_actor_transfer':
            if set(edit)!={'kind','target','phase'} or name!='mounted leader' or edit['phase'] not in {'leader','near_crowd'}:
                raise ValueError('PATCH_TRANSFER_FIELDS')
        elif kind in {'coherent_actor','coherent_refit','mounted_finish345','mounted_cloth345','mounted_whole347','mounted_anatomy351','mounted_arm352','mounted_cloth352','mounted_cloth352_refine'}:
            if set(edit)!={'kind','target'} or name!='mounted leader':raise ValueError('PATCH_ACTOR_FIELDS')
        elif kind=='supporting_look':
            if set(edit)!={'kind','target'} or name!='mounted leader':raise ValueError('PATCH_LOOK_FIELDS')
        elif kind=='supporting_finish':
            if set(edit)!={'kind','target'} or name!='mounted leader':raise ValueError('PATCH_FINISH_FIELDS')
        elif kind == 'supported_motion':
            import importlib.util
            spec=importlib.util.spec_from_file_location('mf_nihang_motion',Path(__file__).with_name('nihang_motion.py'))
            motion=importlib.util.module_from_spec(spec);spec.loader.exec_module(motion)
            motion.validate(edit)
        elif kind == 'supported_pose':
            if set(edit) != {'kind','target','frame','pitch','hip_back','hip_drop','neck_pitch','poll_pitch'} or name != 'horse.rig':
                raise ValueError('PATCH_SUPPORT_FIELDS')
            if type(edit['frame']) is not int or not 252 <= edit['frame'] <= 441:
                raise ValueError('PATCH_SUPPORT_FRAME')
            for key, lo, hi in [('pitch',-1.1,-.3),('hip_back',-.2,.4),('hip_drop',0,.45),('neck_pitch',-.4,.8),('poll_pitch',0,1.2)]:
                if type(edit[key]) not in (int,float) or not math.isfinite(edit[key]) or not lo<=edit[key]<=hi:
                    raise ValueError('PATCH_SUPPORT_BOUND:'+key)
        elif kind == 'bone_pose':
            if set(edit) != {'kind', 'target', 'bone', 'frame', 'quaternion'} or name != 'horse.rig':
                raise ValueError('PATCH_BONE_FIELDS')
            if not isinstance(edit['bone'], str) or not edit['bone'] or len(edit['bone']) > 128:
                raise ValueError('PATCH_BONE')
            q = edit['quaternion']
            if (type(edit['frame']) is not int or not 252 <= edit['frame'] <= 441 or
                not vector(q, 4, 1) or abs(sum(x*x for x in q) - 1) > 1e-5):
                raise ValueError('PATCH_POSE_BOUND')
        elif kind == 'mesh':
            if set(edit) != {'kind', 'target', 'vertices', 'faces', 'color', 'roughness'} or not name.startswith('MF Nihang '):
                raise ValueError('PATCH_MESH_FIELDS')
            verts, faces = edit['vertices'], edit['faces']
            if not isinstance(verts, list) or not 3 <= len(verts) <= 10000 or not all(vector(v, 3, 1000) for v in verts):
                raise ValueError('PATCH_VERTICES')
            if not isinstance(faces, list) or not 1 <= len(faces) <= 10000:
                raise ValueError('PATCH_FACES')
            if any(not isinstance(f, list) or not 3 <= len(f) <= 4 or len(set(f)) != len(f) or
                   any(type(i) is not int or not 0 <= i < len(verts) for i in f) for f in faces):
                raise ValueError('PATCH_FACE_INDEX')
            if not vector(edit['color'], 4, 1) or min(edit['color']) < 0:
                raise ValueError('PATCH_COLOR')
            if type(edit['roughness']) not in (int, float) or not 0 <= edit['roughness'] <= 1:
                raise ValueError('PATCH_ROUGHNESS')
        else:
            raise ValueError('PATCH_UNKNOWN_KIND')
    return recipe


def apply(bpy, recipe,diagnostic_dir=None):
    # Preflight the entire patch before mutation. A mesh operation creates a new
    # named derivative; it cannot overwrite an accepted existing object.
    names = set()
    for edit in recipe['edits']:
        if edit['kind'] in {'neutral_garment_proof','neutral_actor_transfer'}:
            if bpy.data.objects.get('mounted leader') is None:raise ValueError('PATCH_NEUTRAL_OWNER')
        elif edit['kind'] in {'supporting_look','supporting_finish','coherent_actor','coherent_refit','mounted_finish345','mounted_cloth345','mounted_whole347','mounted_anatomy351','mounted_arm352','mounted_cloth352','mounted_cloth352_refine'}:
            if bpy.data.objects.get('mounted leader') is None or bpy.data.objects.get('fitted saddle blanket292') is None:
                raise ValueError('PATCH_LOOK_OBJECTS')
        elif edit['kind'] in {'repair_bbone_targets','supported_pose','supported_motion'}:
            if bpy.data.objects.get('horse.rig') is None or bpy.data.objects.get('HORSE hind support pivot') is None:
                raise ValueError('PATCH_SUPPORT_OBJECTS')
        elif edit['kind'] == 'bone_pose':
            obj = bpy.data.objects.get(edit['target'])
            if obj is None or not obj.pose or edit['bone'] not in obj.pose.bones:
                raise ValueError('PATCH_BONE_MISSING')
        else:
            if edit['target'] in bpy.data.objects or edit['target'] in names:
                raise ValueError('PATCH_EXISTING_MESH')
            names.add(edit['target'])
    support_evidence=[]
    for edit in recipe['edits']:
        if edit['kind'] in {'mounted_cloth352','mounted_cloth352_refine'}:
            import importlib.util
            spec=importlib.util.spec_from_file_location('mf_nihang_cloth352',Path(__file__).with_name('nihang_cloth352.py'))
            cloth=importlib.util.module_from_spec(spec);spec.loader.exec_module(cloth)
            support_evidence.append({'cloth352':(cloth.refine if edit['kind']=='mounted_cloth352_refine' else cloth.run)(bpy,diagnostic_dir)})
        elif edit['kind']=='mounted_arm352':
            import importlib.util
            spec=importlib.util.spec_from_file_location('mf_nihang_arm352',Path(__file__).with_name('nihang_arm352.py'))
            arm=importlib.util.module_from_spec(spec);spec.loader.exec_module(arm)
            support_evidence.append({'arm352':arm.run(bpy,diagnostic_dir)})
        elif edit['kind']=='mounted_anatomy351':
            import importlib.util
            spec=importlib.util.spec_from_file_location('mf_nihang_anatomy351',Path(__file__).with_name('nihang_anatomy351.py'))
            anatomy=importlib.util.module_from_spec(spec);spec.loader.exec_module(anatomy)
            support_evidence.append({'anatomy351':anatomy.run(bpy,diagnostic_dir)})
        elif edit['kind']=='mounted_whole347':
            import importlib.util
            spec=importlib.util.spec_from_file_location('mf_nihang_whole347',Path(__file__).with_name('nihang_whole347.py'))
            whole=importlib.util.module_from_spec(spec);spec.loader.exec_module(whole)
            support_evidence.append({'whole347':whole.run(bpy,diagnostic_dir)})
        elif edit['kind'] in {'mounted_finish345','mounted_cloth345'}:
            import importlib.util
            spec=importlib.util.spec_from_file_location('mf_nihang_finish345',Path(__file__).with_name('nihang_finish345.py'))
            finish=importlib.util.module_from_spec(spec);spec.loader.exec_module(finish)
            support_evidence.append({'finish345':(finish.cloth if edit['kind']=='mounted_cloth345' else finish.run)(bpy,diagnostic_dir)})
        elif edit['kind']=='coherent_refit':
            import importlib.util
            spec=importlib.util.spec_from_file_location('mf_nihang_refit',Path(__file__).with_name('nihang_refit.py'))
            refit=importlib.util.module_from_spec(spec);spec.loader.exec_module(refit)
            support_evidence.append({'refit':refit.run(bpy,diagnostic_dir)})
        elif edit['kind']=='coherent_actor':
            import importlib.util
            spec=importlib.util.spec_from_file_location('mf_nihang_actor',Path(__file__).with_name('nihang_actor.py'))
            actor=importlib.util.module_from_spec(spec);spec.loader.exec_module(actor)
            support_evidence.append({'actor':actor.run(bpy,diagnostic_dir)})
        elif edit['kind']=='neutral_garment_proof':
            import importlib.util
            spec=importlib.util.spec_from_file_location('mf_nihang_neutral',Path(__file__).with_name('nihang_neutral.py'))
            neutral=importlib.util.module_from_spec(spec);spec.loader.exec_module(neutral)
            support_evidence.append({'neutral':neutral.run(bpy,edit['phase'],diagnostic_dir)})
        elif edit['kind']=='neutral_actor_transfer':
            import importlib.util
            spec=importlib.util.spec_from_file_location('mf_nihang_transfer',Path(__file__).with_name('nihang_transfer.py'))
            transfer=importlib.util.module_from_spec(spec);spec.loader.exec_module(transfer)
            support_evidence.append({'transfer':transfer.run(bpy,edit['phase'],diagnostic_dir)})
        elif edit['kind']=='supporting_look':
            import importlib.util
            spec=importlib.util.spec_from_file_location('mf_nihang_look',Path(__file__).with_name('nihang_look.py'))
            look=importlib.util.module_from_spec(spec);spec.loader.exec_module(look)
            support_evidence.append({'look':look.run(bpy,diagnostic_dir)})
        elif edit['kind']=='supporting_finish':
            import importlib.util
            spec=importlib.util.spec_from_file_location('mf_nihang_finish',Path(__file__).with_name('nihang_finish.py'))
            finish=importlib.util.module_from_spec(spec);spec.loader.exec_module(finish)
            support_evidence.append({'finish':finish.run(bpy,diagnostic_dir)})
        elif edit['kind'] in {'repair_bbone_targets','supported_pose','supported_motion'}:
            import importlib.util
            spec=importlib.util.spec_from_file_location('mf_nihang_support',Path(__file__).with_name('nihang_support.py'))
            support=importlib.util.module_from_spec(spec);spec.loader.exec_module(support)
            if edit['kind']=='repair_bbone_targets':
                support_evidence.append({'repaired_targets':support.repair_bbone_targets(bpy)})
            elif edit['kind']=='supported_motion':
                spec=importlib.util.spec_from_file_location('mf_nihang_motion',Path(__file__).with_name('nihang_motion.py'))
                motion=importlib.util.module_from_spec(spec);spec.loader.exec_module(motion)
                support_evidence.append({'motion':motion.run(bpy,edit,support)})
            else:
                support_evidence.append({'frame':edit['frame'],'support':support.apply_pose(bpy,edit)})
        elif edit['kind'] == 'bone_pose':
            bpy.context.scene.frame_set(edit['frame'])
            pb = bpy.data.objects[edit['target']].pose.bones[edit['bone']]
            pb.rotation_mode = 'QUATERNION'
            pb.rotation_quaternion = edit['quaternion']
            pb.keyframe_insert(data_path='rotation_quaternion', frame=edit['frame'])
        else:
            mesh = bpy.data.meshes.new(edit['target'])
            mesh.from_pydata(edit['vertices'], [], edit['faces']); mesh.update()
            obj = bpy.data.objects.new(edit['target'], mesh)
            bpy.context.scene.collection.objects.link(obj)
            mat = bpy.data.materials.new(edit['target'] + ' material'); mat.use_nodes = True
            node = mat.node_tree.nodes.get('Principled BSDF')
            node.inputs['Base Color'].default_value = edit['color']
            node.inputs['Roughness'].default_value = edit['roughness']
            mesh.materials.append(mat)
    bpy.context.scene.frame_set(recipe['frame']); bpy.context.view_layer.update()
    return support_evidence


def run(out, job, control):
    import bpy
    recipe = validate(job['recipe'])
    parent = Path(job['parent_native']).resolve(strict=True)
    root = Path(job['repository_root']).resolve(strict=True)
    if not parent.is_relative_to(root) or parent == (out / 'scene.blend').resolve():
        raise ValueError('PATCH_PARENT_BOUNDARY')
    bpy.ops.wm.open_mainfile(filepath=str(parent), load_ui=False, use_scripts=False)
    bpy.context.scene.frame_set(recipe['frame']); bpy.context.view_layer.update()
    diagnostics = control.script_diagnostics(bpy)
    if diagnostics['blocked_drivers']: raise ValueError('PATCH_UNSAFE_DRIVER')
    before = control.selected_state(bpy, recipe['frame'])
    support = apply(bpy, recipe,out)
    after = control.selected_state(bpy, recipe['frame'])
    diagnostics = control.script_diagnostics(bpy)
    if diagnostics['blocked_drivers']: raise ValueError('PATCH_INVALID_AFTER_REPAIR')
    for name, data in [('snapshot.json', after), ('script-diagnostics.json', diagnostics),
                       ('dependencies.json', control.dependencies(bpy, root)),
                       ('patch-evidence.json', {'before': before, 'after': after, 'recipe': recipe, 'support':support})]:
        (out / name).write_text(json.dumps(data, sort_keys=True, indent=2) + '\n')
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(out / 'scene.blend'), check_existing=False,
                              compress=True, relative_remap=True)
    return ['snapshot.json', 'script-diagnostics.json', 'dependencies.json', 'patch-evidence.json', 'scene.blend']
