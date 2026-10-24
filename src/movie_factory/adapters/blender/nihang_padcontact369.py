"""Fixed saddle/animated-horse contact inspection and bounded support clearance.

No mesh, material, action or pose authoring. Not a cloth simulation qualification.
"""
import json
import math
from pathlib import Path


def validate(edit):
    base = {'kind', 'target', 'mode'}
    if edit.get('kind') != 'mounted_padcontact369' or edit.get('target') != 'fitted saddle blanket292':
        raise ValueError('PAD369_TARGET')
    mode = edit.get('mode')
    expected = base | ({'offset'} if mode == 'fit' else set())
    if mode not in {'inspect', 'fit', 'bind', 'follow'} or set(edit) != expected:
        raise ValueError('PAD369_FIELDS')
    if mode == 'fit':
        x = edit['offset']
        if type(x) not in (int, float) or not math.isfinite(x) or not .008 <= x <= .035:
            raise ValueError('PAD369_OFFSET')
    return edit


def classify(values):
    if not values or any(not math.isfinite(x) for x in values):
        raise ValueError('PAD369_NO_SAMPLES')
    return dict(samples=len(values), minimum_signed_gap_m=min(values),
                penetrating_samples=sum(x < -.001 for x in values),
                below_2mm_samples=sum(x < .002 for x in values))


def run(bpy, out, edit):
    validate(edit)
    import importlib.util
    from mathutils.bvhtree import BVHTree
    spec = importlib.util.spec_from_file_location('pad369_prep', Path(__file__).with_name('nihang_prep367.py'))
    prep = importlib.util.module_from_spec(spec); spec.loader.exec_module(prep)
    spec = importlib.util.spec_from_file_location('pad369_tack', Path(__file__).with_name('nihang_tack354.py'))
    tack = importlib.util.module_from_spec(spec); spec.loader.exec_module(tack)
    scene = bpy.context.scene
    pad = bpy.data.objects['fitted saddle blanket292']; horse = bpy.data.objects['horse']
    wraps = [m for m in pad.modifiers if m.type == 'SHRINKWRAP' and m.target == horse]
    if len(wraps) != 1:
        raise ValueError('PAD369_SUPPORT_OWNER')
    wrap = wraps[0]
    if wrap.wrap_method != 'NEAREST_SURFACEPOINT' or wrap.wrap_mode != 'OUTSIDE_SURFACE':
        raise ValueError('PAD369_SUPPORT_METHOD')
    saved_frame = scene.frame_current
    geometry = prep.frozen(bpy); actions = tack.action_signature(bpy)
    original_offset = float(wrap.offset)
    def sample():
        rows = []
        for f in (283, 300, 303, 306, 309, 311, 314):
            scene.frame_set(f); bpy.context.view_layer.update()
            dg = bpy.context.evaluated_depsgraph_get()
            he = horse.evaluated_get(dg); pe = pad.evaluated_get(dg)
            hm = he.to_mesh(); pm = pe.to_mesh()
            try:
                hv = [he.matrix_world @ v.co for v in hm.vertices]
                tree = BVHTree.FromPolygons(hv, [tuple(p.vertices) for p in hm.polygons])
                pv = [pe.matrix_world @ v.co for v in pm.vertices]
                pm.calc_loop_triangles()
                # Include triangle interiors: outside vertices alone can hide a
                # coarse cloth face cutting through a curved animal surface.
                probes = pv + [sum((pv[i] for i in tri.vertices), pv[0] * 0) / 3
                               for tri in pm.loop_triangles]
                gaps = []
                for p in probes:
                    q, normal, index, distance = tree.find_nearest(p)
                    if q is None: raise ValueError('PAD369_NO_HORSE_SURFACE')
                    gaps.append(float((p - q).dot(normal)))
                rows.append(dict(frame=f, **classify(gaps)))
            finally:
                he.to_mesh_clear(); pe.to_mesh_clear()
        return rows
    try:
        before = sample()
        if edit['mode'] == 'fit':
            # This attempt only changes the existing contact stand-off; no
            # re-sculpt, material cover-up, weight transfer or timing change.
            wrap.offset = edit['offset']; bpy.context.view_layer.update()
            after = sample()
        elif edit['mode'] == 'bind':
            # Stable material points follow the same animated surface before
            # the existing local contact projection. Do not chase a new nearest
            # body point from the old static cloth coordinates each frame.
            if pad.modifiers.get('369 motion-bound saddle support') is not None:
                raise ValueError('PAD369_ALREADY_BOUND')
            if abs(original_offset - .008) > .00001:
                raise ValueError('PAD369_BIND_BASELINE')
            scene.frame_set(283); bpy.context.view_layer.update()
            deform = pad.modifiers.new('369 motion-bound saddle support', 'SURFACE_DEFORM')
            deform.target = horse
            with bpy.context.temp_override(object=pad, active_object=pad,
                                          selected_objects=[pad], selected_editable_objects=[pad]):
                bpy.ops.object.modifier_move_to_index(modifier=deform.name, index=0)
                bpy.ops.object.surfacedeform_bind(modifier=deform.name)
            if not deform.is_bound:
                raise ValueError('PAD369_BIND_FAILED')
            bpy.context.view_layer.update()
            after = sample()
        elif edit['mode'] == 'follow':
            deform = pad.modifiers.get('369 motion-bound saddle support')
            if deform is None or not deform.is_bound or abs(original_offset - .008) > .00001:
                raise ValueError('PAD369_FOLLOW_BASELINE')
            # Discriminating control after both offset tests failed: retain
            # stable surface attachment, stop reprojecting onto a different
            # nearest body surface during compression. Keep the old modifier
            # intact but disabled for reversible comparison.
            wrap.show_viewport = False; wrap.show_render = False
            bpy.context.view_layer.update()
            after = sample()
        else:
            after = before
        if geometry != prep.frozen(bpy) or actions != tack.action_signature(bpy):
            raise ValueError('PAD369_FROZEN_STATE_DRIFT')
        report = dict(mode=edit['mode'], owner=pad.name, target=horse.name,
                      modifier=wrap.name, original_offset=original_offset,
                      offset=float(wrap.offset), before=before, after=after,
                      geometry_unchanged=True, action_signature=actions,
                      actions_unchanged=True,
                      surface_deform_bound=bool(pad.modifiers.get('369 motion-bound saddle support')
                          and pad.modifiers['369 motion-bound saddle support'].is_bound),
                      modifiers=[dict(name=m.name, type=m.type,
                                      viewport=m.show_viewport, render=m.show_render)
                                 for m in pad.modifiers],
                      scope='Evaluated viewport triangle/vertex samples, not continuous collision proof, render-level equivalence, cloth physics or artistic acceptance. Review actual rendered interface.')
        (out / 'padcontact369.json').write_text(json.dumps(report, indent=2) + '\n')
        return dict(report='padcontact369.json', mode=edit['mode'],
                    geometry_unchanged=True, actions_unchanged=True)
    finally:
        scene.frame_set(saved_frame); bpy.context.view_layer.update()
