"""Trusted no-edit native control. Not an animation builder or art evaluator.

Imports bpy only inside the worker. Recipes never contain code, paths, camera
changes or pose edits. A future authoring vocabulary needs separate qualification.
"""
import hashlib
import json
from pathlib import Path

OBJECTS = ('horse.rig', 'HORSE hind support pivot', 'mounted leader',
           '320 articulated upper body mounted leader')
# Exact diagnosed legacy320 defect, permitted ONLY for this unchanged negative
# control. It is not a working-rig certificate or a general invalid-driver waiver.
LEGACY_DRIVER_DEFECT = '054bf94aeb90448916005e7c0e8c5dbe163e7fbbea52cde230adf8c32ee0e21c'


def validate(recipe):
    fields={'operation', 'frame', 'width', 'height', 'samples'}
    if isinstance(recipe,dict) and recipe.get('operation')=='nihang_frames':
        fields.add('frames')
        if 'view' in recipe:fields.add('view')
    if not isinstance(recipe, dict) or set(recipe) != fields:
        raise ValueError('NIHANG_RECIPE_FIELDS')
    if recipe['operation'] not in {'nihang_save', 'nihang_render', 'nihang_rig_inspect','nihang_cast_inspect','nihang_frames'}:
        raise ValueError('NIHANG_OPERATION')
    for key, lo, hi in [('frame', 252, 441), ('width', 64, 1080), ('height', 64, 1920), ('samples', 1, 32)]:
        if type(recipe[key]) is not int or not lo <= recipe[key] <= hi:
            raise ValueError('NIHANG_RECIPE_BOUND:' + key)
    if recipe['operation']=='nihang_frames':
        if not isinstance(recipe.get('view','production'),str) or recipe.get('view','production') not in {'production','leader_front','leader_reverse','crowd_front','neutral_front','neutral_back','neutral_side'}:
            raise ValueError('NIHANG_DIAGNOSTIC_VIEW')
        frames=recipe['frames']
        if (not isinstance(frames,list) or not 1<=len(frames)<=16 or
                any(type(f) is not int or not 252<=f<=441 for f in frames) or
                len(set(frames))!=len(frames) or recipe['frame'] not in frames):
            raise ValueError('NIHANG_FRAME_SET')
    return recipe


def diagnostic_camera(bpy,view):
    """Temporary evidence camera only. No production-camera key edits or save."""
    from mathutils import Vector
    if view.startswith('neutral_'):
        if bpy.context.scene.name!='MF neutral garment studio':raise ValueError('NEUTRAL_VIEW_SCENE')
        target=Vector((0,0,1.19))
        offset=Vector({'neutral_front':(0,-3,.07),'neutral_back':(0,3,.07),'neutral_side':(3,-.15,.07)}[view])
        data=bpy.data.cameras.new('MF diagnostic camera temporary')
        camera=bpy.data.objects.new('MF diagnostic camera temporary',data)
        bpy.context.scene.collection.objects.link(camera)
        camera.location=target+offset
        camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
        data.type='ORTHO';data.ortho_scale=1.22
        return camera
    leader=view.startswith('leader_')
    root=bpy.data.objects['mounted leader' if leader else 'FOOT WARRIOR 0']
    upper=next(o for o in root.children if o.name.startswith('320 articulated upper body'))
    head=next(o for o in upper.children if o.name.startswith('secondary adult head'))
    target=head.matrix_world.translation+Vector((0,0,-.22 if leader else -.35))
    facing=-1 if leader else 1
    if view=='leader_reverse':facing=1
    offset=root.matrix_world.to_quaternion()@Vector((.6,facing*1.9,.12))
    data=bpy.data.cameras.new('MF diagnostic camera temporary')
    camera=bpy.data.objects.new('MF diagnostic camera temporary',data)
    bpy.context.scene.collection.objects.link(camera)
    camera.location=target+offset
    camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
    data.lens=55
    return camera


def cast_inventory(bpy):
    """Read-only first supporting actors; inspect real owners before adapting."""
    from mathutils import Vector
    roots=[bpy.data.objects['mounted leader']]
    crowd=sorted([o for o in bpy.data.objects if o.name.startswith('FOOT WARRIOR ')],key=lambda o:o.name)
    if not crowd:raise ValueError('CAST_CROWD_MISSING')
    roots.append(crowd[0]);objects={};materials={}
    for root in roots:
        for obj in [root,*root.children_recursive]:
            row={'type':obj.type,'parent':obj.parent.name if obj.parent else None,'hidden':obj.hide_render,
                 'world':[[float(v) for v in r] for r in obj.matrix_world],
                 'local':[[float(v) for v in r] for r in obj.matrix_local]}
            if obj.type=='MESH':
                row.update(vertices=len(obj.data.vertices),polygons=len(obj.data.polygons),
                           smooth_polygons=sum(p.use_smooth for p in obj.data.polygons),
                           uv_layers=[u.name for u in obj.data.uv_layers],
                           shape_keys=len(obj.data.shape_keys.key_blocks) if obj.data.shape_keys else 0,
                           modifiers=[{'name':m.name,'type':m.type,'render':m.show_render} for m in obj.modifiers])
                points=[Vector(v) for v in obj.bound_box]
                row['local_bounds']={k:[fun(p[i] for p in points) for i in range(3)] for k,fun in [('min',min),('max',max)]}
            if obj.type=='CURVE':row.update(splines=len(obj.data.splines),bevel_depth=obj.data.bevel_depth)
            if obj.data and hasattr(obj.data,'materials'):
                row['materials']=[m.name if m else None for m in obj.data.materials]
                for mat in obj.data.materials:
                    if mat is None or mat.name in materials:continue
                    nodes={}
                    for n in mat.node_tree.nodes if mat.use_nodes else []:
                        inputs={}
                        for socket in n.inputs:
                            if not hasattr(socket,'default_value'):continue
                            value=socket.default_value
                            if isinstance(value,(str,bool,int,float)):inputs[socket.name]={'value':value,'linked':socket.is_linked}
                            elif hasattr(value,'__iter__'):inputs[socket.name]={'value':list(value),'linked':socket.is_linked}
                        nodes[n.name]={'type':n.bl_idname,'inputs':inputs}
                        if hasattr(n,'color_ramp'):nodes[n.name]['ramp']=[{'position':e.position,'color':list(e.color)} for e in n.color_ramp.elements]
                    materials[mat.name]={'nodes':nodes}
            objects[obj.name]=row
    return {'frame':bpy.context.scene.frame_current,'actors':[r.name for r in roots],
            'objects':objects,'materials':materials,'scope':'Actual supporting-actor ownership, topology counts, UVs, cached poses and material parameters; no mutation or appearance pass.'}


def rig_inventory(bpy):
    """Read-only ownership evidence. Never execute asset scripts or repair by inference."""
    rig = bpy.data.objects.get('horse.rig')
    if rig is None or rig.type != 'ARMATURE':
        raise ValueError('NIHANG_HORSE_RIG_MISSING')
    def vector(v): return [float(x) for x in v]
    def matrix(m): return [vector(row) for row in m]
    bones = {}
    for b in rig.pose.bones:
        constraints = []
        for c in b.constraints:
            row = {'name': c.name, 'type': c.type, 'influence': c.influence,
                   'mute': c.mute, 'valid': c.is_valid}
            for key in ('target', 'pole_target'):
                target = getattr(c, key, None)
                row[key] = target.name if target else None
            for key in ('subtarget', 'pole_subtarget', 'chain_count', 'pole_angle',
                        'use_stretch', 'owner_space', 'target_space', 'mix_mode'):
                if hasattr(c, key): row[key] = getattr(c, key)
            constraints.append(row)
        bones[b.name] = {'parent': b.parent.name if b.parent else None,
            'deform': b.bone.use_deform, 'head_rest': vector(b.bone.head_local),
            'tail_rest': vector(b.bone.tail_local), 'rest': matrix(b.bone.matrix_local),
            'head': vector(b.head), 'tail': vector(b.tail), 'matrix': matrix(b.matrix),
            'basis': matrix(b.matrix_basis), 'constraints': constraints,
            'properties': {k: v for k, v in b.items() if isinstance(v, (int, float, str, bool))}}
    drivers = []
    for owner in (rig, rig.data):
        ad = owner.animation_data
        for fc in ad.drivers if ad else []:
            d = fc.driver
            drivers.append({'owner': owner.name, 'owner_type': type(owner).__name__,
                'path': fc.data_path, 'index': fc.array_index, 'type': d.type,
                'valid': d.is_valid, 'expression': d.expression,
                'variables': [{'name': v.name, 'type': v.type,
                    'targets': [{'id': t.id.name if t.id else None, 'id_type': t.id_type,
                                 'data_path': t.data_path, 'bone_target': t.bone_target}
                                for t in v.targets]} for v in d.variables]})
    meshes = []
    for obj in bpy.data.objects:
        if obj.type != 'MESH': continue
        mods = [m for m in obj.modifiers if m.type == 'ARMATURE' and m.object == rig]
        if not mods: continue
        meshes.append({'name': obj.name, 'vertices': len(obj.data.vertices),
            'groups': [g.name for g in obj.vertex_groups],
            'modifiers': [{'name': m.name, 'type': m.type, 'viewport': m.show_viewport,
                           'render': m.show_render} for m in obj.modifiers]})
    return {'rig': rig.name, 'world': matrix(rig.matrix_world), 'bones': bones,
            'drivers': drivers, 'deformed_meshes': meshes,
            'scope': 'Read-only horse controls, rest/evaluated joints, constraint ownership and driver target paths.'}


def digest_file(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def selected_state(bpy, frame):
    scene = bpy.context.scene
    scene.frame_set(frame)
    bpy.context.view_layer.update()
    def matrix(m):
        return [[round(float(v), 6) for v in row] for row in m]
    result = {'frame': frame, 'objects': {}, 'camera': scene.camera.name if scene.camera else None,
              'object_count': len(bpy.data.objects)}
    # In the isolated neutral proof, production objects belong to another scene.
    # A fresh open leaves their unevaluated matrices at identity. Evaluate their
    # owning scene explicitly; never compare cached old matrices with identities.
    if scene.name=='MF neutral garment studio':
        owners=[s for s in bpy.data.scenes if s!=scene and all(n in s.objects for n in OBJECTS)]
        if len(owners)!=1:raise ValueError('NEUTRAL_SOURCE_SCENE_AMBIGUOUS')
        bpy.context.window.scene=owners[0];owners[0].frame_set(frame);bpy.context.view_layer.update()
    for name in OBJECTS:
        obj = bpy.data.objects.get(name)
        if obj is None:
            raise ValueError('NIHANG_REQUIRED_OBJECT_MISSING:' + name)
        result['objects'][name] = {'type': obj.type, 'world': matrix(obj.matrix_world),
            'parent': obj.parent.name if obj.parent else None}
        if obj.pose:
            result['objects'][name]['bones'] = {bone.name: {
                'matrix': matrix(bone.matrix), 'basis': matrix(bone.matrix_basis)}
                for bone in sorted(obj.pose.bones, key=lambda b: b.name)}
    if bpy.context.window.scene!=scene:
        bpy.context.window.scene=scene;scene.frame_set(frame);bpy.context.view_layer.update()
    if not scene.camera:
        raise ValueError('NIHANG_CAMERA_MISSING')
    result['camera_matrix'] = matrix(scene.camera.matrix_world)
    result['camera_lens'] = scene.camera.data.lens
    result['authored_meshes'] = {}
    for obj in bpy.data.objects:
        if obj.type == 'MESH' and (obj.name.startswith('MF Nihang ') or obj.get('mf_supporting_appearance')):
            geometry = {'vertices': [[round(float(x), 6) for x in v.co] for v in obj.data.vertices],
                        'faces': [list(p.vertices) for p in obj.data.polygons]}
            mats = []
            for mat in obj.data.materials:
                node = mat.node_tree.nodes.get('Principled BSDF') if mat and mat.use_nodes else None
                if node:
                    mats.append({'color': list(node.inputs['Base Color'].default_value),
                                 'roughness': node.inputs['Roughness'].default_value})
            result['authored_meshes'][obj.name] = {'geometry_hash': hashlib.sha256(
                json.dumps(geometry, sort_keys=True).encode()).hexdigest(),
                'vertices': len(obj.data.vertices), 'faces': len(obj.data.polygons), 'materials': mats}
    return result


def script_diagnostics(bpy):
    """Inspect untrusted embedded code as DATA; never execute or register it.

    Autoexec warning alone is not a failed dependency. Only Blender's simple
    expression evaluator is admitted; Python namespace drivers stay blocked.
    """
    texts = []
    for item in bpy.data.texts:
        body = item.as_string()
        if len(body.encode()) > 256000:
            raise ValueError('NIHANG_EMBEDDED_TEXT_TOO_LARGE')
        texts.append({'name': item.name, 'use_module': bool(item.use_module),
                      'sha256': hashlib.sha256(body.encode()).hexdigest(), 'body': body})
    drivers = []
    # All animation-capable IDs, including shape keys and material node trees.
    visited = set()
    def inspect(item):
        if item.as_pointer() in visited:
            return
        visited.add(item.as_pointer())
        data = getattr(item, 'animation_data', None)
        for curve in data.drivers if data else []:
            d = curve.driver
            drivers.append({'owner': item.name, 'owner_type': type(item).__name__, 'users': item.users,
                'path': curve.data_path, 'index': curve.array_index,
                'type': d.type, 'expression': d.expression, 'valid': bool(d.is_valid),
                'simple': bool(d.is_simple_expression),
                'targets': [{'name': v.name, 'type': v.type, 'ids': [t.id.name if t.id else None for t in v.targets]}
                            for v in d.variables]})
        tree = getattr(item, 'node_tree', None)
        if tree: inspect(tree)
    for prop in bpy.data.bl_rna.properties:
        if prop.type == 'COLLECTION':
            for item in getattr(bpy.data, prop.identifier):
                if isinstance(item, bpy.types.ID): inspect(item)
    blocked = [d for d in drivers if d['users'] > 0 and
               (not d['valid'] or (d['type'] == 'SCRIPTED' and not d['simple']))]
    legacy = hashlib.sha256(json.dumps(blocked, sort_keys=True).encode()).hexdigest() == LEGACY_DRIVER_DEFECT
    return {'autoexec_warning': bool(bpy.app.autoexec_fail),
            'message': bpy.app.autoexec_fail_message, 'embedded_texts': texts, 'drivers': drivers,
            'blocked_drivers': [] if legacy else blocked,
            'known_source_defects': blocked if legacy else [],
            'rig_qualified': not blocked,
            'orphan_driver_count': sum(d['users'] == 0 for d in drivers)}


def dependency_relevant(collection, item, linked_ids=None):
    """A fully appended, unused library is input provenance, not a live link.

    Blender drops that orphan ID on save/reopen. Keep input provenance in the
    admitted source bindings; retain every actually used/fake-user library here.
    Other dependency collections are unchanged.
    """
    if collection!='libraries':return True
    if linked_ids is not None:
        return any(getattr(block,'library',None)==item for block in linked_ids)
    return item.users!=0 or item.use_fake_user


def dependencies(bpy, root):
    """Scoped external-file inventory; not complete simulation portability."""
    found = {}
    # Appending can leave nonzero weak provenance users on a library ID, even
    # though no data remains externally linked. Inventory actual linked IDs;
    # the admitted donor hash remains immutable input provenance separately.
    all_ids=list(bpy.data.user_map())
    for collection in ('images', 'libraries', 'cache_files', 'movieclips', 'sounds', 'fonts', 'volumes'):
        for item in getattr(bpy.data, collection):
            if not dependency_relevant(collection,item,all_ids):continue
            filename = getattr(item, 'filepath', '')
            if not filename or filename == '<builtin>' or getattr(item, 'packed_file', None):
                continue
            if collection == 'images' and item.source in {'GENERATED', 'VIEWER'}:
                continue
            resolved = Path(bpy.path.abspath(filename, library=getattr(item, 'library', None))).resolve()
            if not resolved.is_relative_to(root):
                raise ValueError('NIHANG_EXTERNAL_DEPENDENCY_OUTSIDE_ROOT:' + item.name)
            if resolved.suffix.lower() not in {'.png', '.jpg', '.jpeg', '.exr', '.hdr', '.tif', '.tiff', '.webp',
                    '.blend', '.abc', '.vdb', '.usd', '.usdc', '.ogg', '.wav', '.mp3', '.mp4', '.mov', '.bphys'}:
                raise ValueError('NIHANG_UNSUPPORTED_DEPENDENCY:' + item.name)
            if not resolved.is_file():
                raise ValueError('NIHANG_MISSING_DEPENDENCY:' + item.name)
            rel = str(resolved.relative_to(root))
            found[rel] = {'path': rel, 'sha256': digest_file(resolved)}
    return {'bindings': found, 'scope': 'Images, libraries, cache_files, clips, sounds, fonts, volumes; '
            'not arbitrary node paths or complete simulation-cache closure'}


def run(out, job):
    import bpy
    recipe = validate(job['recipe'])
    parent = Path(job['parent_native']).resolve(strict=True)
    root = Path(job['repository_root']).resolve(strict=True)
    if parent == (out / 'scene.blend').resolve() or not parent.is_relative_to(root):
        raise ValueError('NIHANG_PARENT_BOUNDARY')
    bpy.ops.wm.open_mainfile(filepath=str(parent), load_ui=False, use_scripts=False)
    state = selected_state(bpy, recipe['frame'])
    diagnostics = script_diagnostics(bpy)
    (out / 'script-diagnostics.json').write_text(json.dumps(diagnostics, indent=2) + '\n')
    if diagnostics['blocked_drivers']:
        raise ValueError('NIHANG_UNSAFE_OR_INVALID_DRIVER')
    deps = dependencies(bpy, root)
    (out / 'snapshot.json').write_text(json.dumps(state, sort_keys=True, indent=2) + '\n')
    (out / 'dependencies.json').write_text(json.dumps(deps, sort_keys=True, indent=2) + '\n')
    artifacts = ['snapshot.json', 'dependencies.json']
    if recipe['operation']=='nihang_cast_inspect':
        (out/'cast.json').write_text(json.dumps(cast_inventory(bpy),indent=2)+'\n')
        artifacts.append('cast.json')
    elif recipe['operation'] == 'nihang_rig_inspect':
        (out / 'rig.json').write_text(json.dumps(rig_inventory(bpy), indent=2) + '\n')
        artifacts.append('rig.json')
    elif recipe['operation'] == 'nihang_save':
        bpy.context.preferences.filepaths.save_version = 0
        # Remap relative external paths so relocation does not change their target.
        bpy.ops.wm.save_as_mainfile(filepath=str(out / 'scene.blend'), check_existing=False,
                                  compress=True, relative_remap=True)
        artifacts.append('scene.blend')
    else:
        scene = bpy.context.scene
        scene.render.engine = 'CYCLES'
        scene.cycles.device = 'CPU'
        scene.cycles.samples = recipe['samples']
        scene.cycles.seed = 333
        # Reuse static render data within this serial chunk. This is not a new
        # render style; repeated327 image controls must still match exactly.
        scene.render.use_persistent_data = True
        scene.render.resolution_x = recipe['width']
        scene.render.resolution_y = recipe['height']
        scene.render.resolution_percentage = 100
        scene.render.image_settings.file_format = 'PNG'
        frames=recipe.get('frames',[recipe['frame']]);manifest=[]
        for frame in frames:
            scene.frame_set(frame);bpy.context.view_layer.update()
            view=recipe.get('view','production');original_camera=scene.camera
            temp=diagnostic_camera(bpy,view) if view!='production' else None
            if temp:scene.camera=temp
            bpy.context.view_layer.update()
            filename='frame.png' if frame==recipe['frame'] else f'frame-{frame:04d}.png'
            scene.render.filepath = str(out / filename)
            camera_matrix=[[float(v) for v in row] for row in scene.camera.matrix_world]
            try:bpy.ops.render.render(write_still=True)
            finally:
                scene.camera=original_camera
                if temp:
                    data=temp.data;bpy.data.objects.remove(temp,do_unlink=True);bpy.data.cameras.remove(data)
            manifest.append({'frame':frame,'file':filename,'sha256':digest_file(out/filename),
                             'view':view,'camera_matrix':camera_matrix})
        if recipe['operation']=='nihang_frames':
            (out/'frames.json').write_text(json.dumps(manifest,indent=2)+'\n')
            artifacts.append('frames.json')
        artifacts.append('frame.png')
    return artifacts
