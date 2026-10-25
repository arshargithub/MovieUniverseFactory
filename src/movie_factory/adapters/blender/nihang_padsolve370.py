"""Fixed, native, frame-baked exterior contact for the existing saddle cloth.

Actual per-frame fitted seed, anatomical radial rays, editable native shape keys.
No horse/rider authoring, arbitrary recipe code, external cache or cloth-physics claim.
"""
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import numpy as np


def radial(local_point, center_x):
    x = float(local_point[0]) - center_x
    side = max(-1., min(1., x / .12))
    return (side, 0., max(.25, 1. - abs(side)))


def face_contacts(points, triangles, project, rounds=5):
    """Bounded, shared-vertex face contact correction; no physical-sim claim."""
    points = np.asarray(points, dtype=float).copy()
    triangles = np.asarray(triangles, dtype=int)
    for _ in range(rounds):
        delta = np.zeros_like(points); counts = np.zeros(len(points)); corrections = 0
        for ids in triangles:
            center = points[ids].mean(0); target = np.asarray(project(center), dtype=float)
            move = target-center
            if np.linalg.norm(move) > 1e-5:
                delta[ids] += move; counts[ids] += 1; corrections += 1
        if not corrections: break
        active = counts > 0
        points[active] += delta[active]/counts[active,None]
        points = np.array([project(p) for p in points])
    return points


def apply_contact_moves(points, constraints):
    """Share actual final-surface corrections over their source vertices."""
    points = np.asarray(points, dtype=float).copy()
    delta = np.zeros_like(points); counts = np.zeros(len(points))
    for ids, move in constraints:
        ids = sorted(set(ids))
        delta[ids] += np.asarray(move, dtype=float); counts[ids] += 1
    active = counts > 0
    points[active] += delta[active]/counts[active,None]
    return points


def module(name):
    spec = importlib.util.spec_from_file_location('pad370_' + name, Path(__file__).with_name(name + '.py'))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def actions(bpy, ignore=None):
    result = {}
    for action in bpy.data.actions:
        curves = []
        if hasattr(action, 'fcurves'):
            try: curves = list(action.fcurves)
            except RuntimeError: pass
        if not curves:
            for layer in action.layers:
                for strip in layer.strips:
                    for bag in getattr(strip, 'channelbags', []): curves.extend(bag.fcurves)
        curves=[c for c in curves if c.data_path not in (ignore or {}).get(action.name,set())]
        result[action.name] = hashlib.sha256(json.dumps([(c.data_path, c.array_index,
            [(tuple(k.co), k.interpolation) for k in c.keyframe_points]) for c in curves], sort_keys=True).encode()).hexdigest()
    return result


def phase_spec(phase):
    if phase=='preparation':return ('370 contact-solved saddle cloth',[306,300,308,313,314]+[f for f in range(276,315) if f not in (306,300,308,313,314)])
    if phase=='apex':return ('371 apex contact-solved saddle cloth',[323,333,315,319,328]+[f for f in range(315,334) if f not in (323,333,315,319,328)])
    if phase=='landing':return ('373 landing contact-solved saddle cloth',[343,344,346,334,367]+[f for f in range(334,368) if f not in (343,344,346,334,367)])
    raise ValueError('PAD371_UNKNOWN_PHASE')


def run(bpy, out, phase='preparation'):
    from mathutils import Vector, Matrix
    from mathutils.bvhtree import BVHTree
    prep = module('nihang_prep367'); support = module('nihang_support')
    scene = support.select_production_scene(bpy)
    pad = bpy.data.objects['fitted saddle blanket292']; horse = bpy.data.objects['horse']
    frame_owner = bpy.data.objects['horse.rig']
    name,frames=phase_spec(phase)
    if phase=='apex' and (not scene.get('apex371') or bpy.data.objects.get('370 contact-solved saddle cloth') is None):raise ValueError('PAD371_APEX_SOURCE')
    if phase=='landing' and not scene.get('landing373'):raise ValueError('PAD373_LANDING_SOURCE')
    if bpy.data.objects.get(name) is not None: raise ValueError('PAD370_ALREADY_SOLVED')
    # Use the actual evaluated fit at every frame; no deform-binding seed.
    # Original pad and all original actions stay untouched.
    wrap = next(m for m in pad.modifiers if m.type == 'SHRINKWRAP')
    sub = next(m for m in pad.modifiers if m.type == 'SUBSURF')
    solid = next(m for m in pad.modifiers if m.type == 'SOLIDIFY')
    if wrap.target != horse: raise ValueError('PAD370_HORSE_OWNER')
    ignore={}
    if phase in ('apex','landing') and pad.animation_data and pad.animation_data.action:ignore[pad.animation_data.action.name]={'hide_render'}
    entry_frame=scene.frame_current
    accepted_visibility={}
    if phase in ('apex','landing'):
        for f in range(276,334 if phase=='landing' else 315):
            scene.frame_set(f);bpy.context.view_layer.update();accepted_visibility[f]=bool(pad.hide_render)
    original = prep.frozen(bpy); original_actions = actions(bpy,ignore)
    saved = (wrap.show_viewport, wrap.show_render, solid.show_viewport, solid.show_render,
             sub.levels, sub.render_levels, entry_frame)
    horse_levels = [(m, m.levels) for m in horse.modifiers if m.type == 'SUBSURF']
    for m, old in horse_levels: m.levels = m.render_levels
    # Sample the ACTUAL fitted reference, not the unfitted base cage.
    wrap.show_viewport = wrap.show_render = True
    solid.show_viewport = solid.show_render = False
    sub.levels = sub.render_levels = 2
    rows = []; solved = None
    try:
        scene.frame_set(283); bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get(); pe = pad.evaluated_get(dg)
        data = bpy.data.meshes.new_from_object(pe, preserve_all_data_layers=True, depsgraph=dg)
        solved = bpy.data.objects.new(name, data); scene.collection.objects.link(solved)
        solved.matrix_world = Matrix.Identity(4)
        if [m.name for m in data.materials] != [m.name for m in pad.data.materials]:
            raise ValueError('PAD370_MATERIAL_IDENTITY')
        # Ray directions are stable cross-body directions, never a fresh nearest
        # choice between two sides of a folded thigh. Near the back centre they
        # point upward; at either flank they point outward with a small up component.
        # Anatomical axes belong to the established rig frame. The imported
        # mesh object's transform is not an anatomical coordinate system.
        inv = frame_owner.matrix_world.inverted()
        hv0 = [inv @ (pe.matrix_world @ v.co) for v in data.vertices]
        center_x = (min(p.x for p in hv0) + max(p.x for p in hv0)) * .5
        data.calc_loop_triangles(); triangles = [tuple(t.vertices) for t in data.loop_triangles]
        basis = solved.shape_key_add(name='Basis')
        for f in frames:
            scene.frame_set(f); bpy.context.view_layer.update(); dg = bpy.context.evaluated_depsgraph_get()
            he = horse.evaluated_get(dg); pe = pad.evaluated_get(dg)
            hm = he.to_mesh(); pm = pe.to_mesh()
            try:
                if len(pm.vertices) != len(data.vertices): raise ValueError('PAD370_SEED_TOPOLOGY_DRIFT')
                tree = BVHTree.FromPolygons([he.matrix_world @ v.co for v in hm.vertices],
                                           [tuple(p.vertices) for p in hm.polygons])
                rotation = frame_owner.matrix_world.to_quaternion()
                clear_overhangs = 0; normal_rays = 0
                inv_frame = frame_owner.matrix_world.inverted()
                def project_contact(position):
                    nonlocal clear_overhangs, normal_rays
                    seed = Vector(position); q, n, face_id, nearest_distance = tree.find_nearest(seed)
                    if q is None: raise ValueError('PAD370_CONTACT_SURFACE_MISSING')
                    # Minimum intervention: keep every already-clear fitted
                    # point, rather than dragging an edge onto a remote hit.
                    if (seed-q).dot(n) >= .007:
                        clear_overhangs += 1; return tuple(seed)
                    direction = rotation @ Vector(radial(inv_frame @ seed, center_x)).normalized()
                    hit, normal, face, distance = tree.ray_cast(seed + direction * .8, -direction, 1.6)
                    if hit is None or (hit-seed).length > .15:
                        hit, normal, face, distance = tree.ray_cast(seed+n*.8, -n, 1.6)
                        if hit is not None: direction = n; normal_rays += 1
                        if hit is None:
                            (out/'padsolve370-failure.json').write_text(json.dumps(dict(
                                frame=f, seed=list(seed), direction=list(direction),
                                nearest=None if q is None else list(q), nearest_distance=nearest_distance,
                                signed_seed_gap=None if q is None else float((seed-q).dot(n)),
                                rig_matrix=[list(v) for v in frame_owner.matrix_world],
                                mesh_matrix=[list(v) for v in horse.matrix_world]), indent=2)+'\n')
                            raise ValueError(f'PAD370_NO_EXTERIOR_HIT:{f}')
                    # Physical stand-off from the outermost hit, retaining both
                    # outward travel and normal clearance at grazing contact.
                    point = hit + direction * .006 + normal * .010
                    if (point-seed).length > .25:
                        (out/'padsolve370-failure.json').write_text(json.dumps(dict(
                            frame=f, seed=list(seed), point=list(point), nearest=list(q),
                            signed_seed_gap=float((seed-q).dot(n)), displacement=(point-seed).length),indent=2)+'\n')
                        raise ValueError(f'PAD370_CONTACT_JUMP:{f}')
                    return tuple(point)
                seeds = np.array([tuple(pe.matrix_world @ v.co) for v in pm.vertices])
                points = np.array([project_contact(p) for p in seeds])
                points = face_contacts(points, triangles, project_contact)
                spans = np.linalg.norm(points-seeds, axis=1)
                if max(spans) > .25:
                    index = int(np.argmax(spans))
                    (out/'padsolve370-failure.json').write_text(json.dumps(dict(frame=f, index=index, seed=seeds[index].tolist(), result=points[index].tolist(), displacement=float(spans[index])),indent=2)+'\n')
                    raise ValueError(f'PAD370_TOTAL_CONTACT_JUMP:{f}')
                co = np.asarray(points, dtype=np.float32).ravel()
                if f == frames[0]:
                    data.vertices.foreach_set('co', co); basis.data.foreach_set('co', co)
                key = solved.shape_key_add(name=f'contact_{f}')
                key.data.foreach_set('co', co)
                for t, value in ((f-1, 0.), (f, 1.), (f+1, 0.)):
                    key.value = value; key.keyframe_insert('value', frame=t)
                # Actual final surface includes wool thickness and face interiors.
                if f == frames[0]:
                    m = solved.modifiers.new('370 retained wool thickness', 'SOLIDIFY')
                    m.thickness = solid.thickness; m.offset = solid.offset
                first_contact = None
                for contact_round in range(13):
                    co = np.asarray(points, dtype=np.float32).ravel()
                    key.data.foreach_set('co', co); data.update()
                    scene.frame_set(f); bpy.context.view_layer.update()
                    se = solved.evaluated_get(bpy.context.evaluated_depsgraph_get()); sm = se.to_mesh()
                    try:
                        count = len(points)
                        if len(sm.vertices) != count*2: raise ValueError('PAD370_THICKNESS_TOPOLOGY')
                        sv = [se.matrix_world @ v.co for v in sm.vertices]; sm.calc_loop_triangles()
                        ids = [(i%count,) for i in range(len(sv))] + [tuple(i%count for i in tri.vertices) for tri in sm.loop_triangles]
                        probes = sv + [sum((sv[i] for i in tri.vertices), sv[0]*0)/3 for tri in sm.loop_triangles]
                        gaps = []; constraints = []; worst = []
                        for index, point in enumerate(probes):
                            q, normal, face, distance = tree.find_nearest(point)
                            if q is None: raise ValueError('PAD370_MISSING_CONTACT_SAMPLE')
                            gap = float((point-q).dot(normal)); gaps.append(gap)
                            if gap < .002:
                                target = Vector(project_contact(point))
                                constraints.append((ids[index], tuple(target-point)))
                                worst.append(dict(kind='vertex' if index<len(sv) else 'triangle_centroid',
                                                  index=index if index<len(sv) else index-len(sv),
                                                  point=list(point), nearest=list(q), signed_gap=gap))
                        if first_contact is None:
                            first_contact = dict(min_gap=min(gaps), below_minus_1mm=sum(g<-.001 for g in gaps),
                                                 worst=sorted(worst,key=lambda row:row['signed_gap'])[:8])
                        if min(gaps) >= .002:
                            spans = np.linalg.norm(points-seeds,axis=1)
                            rows.append(dict(frame=f, samples=len(gaps), min_gap=min(gaps),
                                             below_minus_1mm=sum(g < -.001 for g in gaps),
                                             max_seed_displacement=float(max(spans)),
                                             clear_overhangs=clear_overhangs, normal_rays=normal_rays,
                                             final_surface_rounds=contact_round, before_final_contact=first_contact,
                                             positions_sha256=hashlib.sha256(co.tobytes()).hexdigest()))
                            (out/'padsolve370-progress.json').write_text(json.dumps(rows,indent=2)+'\n')
                            print(f'Pad contact frame{f}: min_gap={min(gaps):.6f}; final_rounds={contact_round}',flush=True)
                            break
                        if contact_round == 12:
                            (out/'padsolve370-failure.json').write_text(json.dumps(dict(frame=f, min_gap=min(gaps),
                                before=first_contact, worst=sorted(worst,key=lambda row:row['signed_gap'])[:8]),indent=2)+'\n')
                            raise ValueError(f'PAD370_FINAL_CONTACT_UNRESOLVED:{f}')
                        points = apply_contact_moves(points,constraints)
                        if max(np.linalg.norm(points-seeds,axis=1))>.25:
                            raise ValueError(f'PAD370_FINAL_CONTACT_JUMP:{f}')
                    finally: se.to_mesh_clear()
            finally: he.to_mesh_clear(); pe.to_mesh_clear()
        # Only the new native cache action may be added. Original actions and all
        # original mesh/shape data must remain byte-identical.
        motion = module('nihang_motion')
        for fc in motion.curves(solved.data.shape_keys):
            for k in fc.keyframe_points: k.interpolation = 'LINEAR'
        if phase=='landing':
            visibility=module('nihang_landing373').visibility_keys(accepted_visibility,{334:True,367:True,368:True})
            for ob,values in [(pad,visibility),(solved,[(333,True),(334,False),(367,False),(368,True)])]:
                for f,value in values:ob.hide_render=value;ob.keyframe_insert('hide_render',frame=f)
                for fc in motion.curves(ob):
                    if fc.data_path=='hide_render':
                        for key in fc.keyframe_points:key.interpolation='CONSTANT'
        if phase=='apex':
            for ob,values in [(pad,module('nihang_apex371').visibility_keys(accepted_visibility,{315:True,333:True,334:True})),
                              (solved,[(314,True),(315,False),(333,False),(334,True)])]:
                for f,value in values:ob.hide_render=value;ob.keyframe_insert('hide_render',frame=f)
                for fc in motion.curves(ob):
                    if fc.data_path=='hide_render':
                        for key in fc.keyframe_points:key.interpolation='CONSTANT'
        if phase in ('apex','landing'):
            for f,expected in accepted_visibility.items():
                scene.frame_set(f);bpy.context.view_layer.update()
                if bool(pad.hide_render)!=expected:raise ValueError('PAD371_ACCEPTED_VISIBILITY_CHANGED')
        after_actions = actions(bpy,ignore)
        if any(after_actions.get(n) != h for n, h in original_actions.items()):
            raise ValueError('PAD370_ORIGINAL_ACTION_CHANGED')
        added = set(after_actions)-set(original_actions)
        expected_actions={solved.data.shape_keys.animation_data.action.name}
        if phase in ('apex','landing'):expected_actions.add(solved.animation_data.action.name)
        if added != expected_actions: raise ValueError('PAD370_CACHE_ACTION_SCOPE')
        after = prep.frozen(bpy)
        if any(after.get(n) != h for n, h in original.items()) or set(after)-set(original) != {name}:
            raise ValueError('PAD370_ORIGINAL_GEOMETRY_CHANGED')
        pad.hide_render = True
        solved['contact_source'] = 'fitted saddle blanket292 evaluated each frame; frozen53 motion; no Surface Deform seed'
        solved['contact_interval'] = [min(frames),max(frames)]
        report = dict(rows=sorted(rows,key=lambda row:row['frame']), vertices=len(data.vertices), original_geometry_unchanged=True,
                      original_actions_unchanged=not bool(ignore), original_motion_actions_unchanged=True, added_cache_actions=sorted(added),
                      original_hidden_only=True, phase=phase, interval=[min(frames),max(frames)], visibility_only_action_exclusions=sorted(ignore), material_names=[m.name for m in data.materials],
                      source_uv_layers=[u.name for u in pad.data.uv_layers],
                      result_uv_layers=[u.name for u in data.uv_layers],
                      scope='Native linear shape-key contact cache for declared integer interval only; no horse/rider changes, cloth/wind simulation or unseen-motion qualification. Full rendered review/subframe limits separate.')
        (out/'padsolve370.json').write_text(json.dumps(report, indent=2)+'\n')
        return dict(report='padsolve370.json', frames=len(rows), original_geometry_unchanged=True,
                    original_actions_unchanged=not bool(ignore), original_motion_actions_unchanged=True, new_native_contact_cache=name)
    finally:
        wrap.show_viewport, wrap.show_render, solid.show_viewport, solid.show_render, sub.levels, sub.render_levels, frame = saved
        for m, old in horse_levels: m.levels = old
        scene.frame_set(frame); bpy.context.view_layer.update()
