"""Fresh-open tests for the fixed174 selection; no creative acceptance."""
import json


def verify(out, base, source, source_sha, binding):
    import bpy
    import numpy as np
    import wardrobe_studio as studio
    from wardrobe_riding_fit import digest, accepted_signature, evaluated_surfaces, fit_render
    from body_studio_fit import coordinates_digest
    from static_tail_dock import data_signature
    selected = base/'wardrobe174-seal01'
    result = json.loads((selected/'result.json').read_text())
    bpy.ops.wm.open_mainfile(filepath=str(selected/'dressed-fit.blend'),load_ui=False,use_scripts=False)
    assert digest(base/'wardrobe174-operating/source-binding.json')==result['source_binding_sha256']
    assert bpy.context.scene['MF_174_source_commit']==binding['source_commit']==result['source_commit']
    assert bpy.context.scene['MF_174_source_binding_sha256']==result['source_binding_sha256']
    body = bpy.data.objects['MF_studio_adult_body']; rig = bpy.data.objects['MF_body156_fit_rig']
    with np.load(selected/'evaluated-surfaces.npz',allow_pickle=False) as reference:
        actual = evaluated_surfaces(reference.files)
        errors = {name:float(np.max(np.abs(actual[name]-reference[name])))
                  if actual[name].shape==reference[name].shape else None for name in reference.files}
    protected = accepted_signature(result['protected_signatures'])==result['protected_signatures']
    basis = coordinates_digest(tuple(v.co for v in body.data.vertices))==result['body_basis_digest']
    tail = data_signature(bpy.data.objects['MF_170_tail_fibers'])==result['static_tail_curve_digest']
    assert protected and basis and tail
    assert all(v is not None and np.isfinite(v) and v<2e-5 for v in errors.values())
    belt = bpy.data.objects['MF_173_waist_belt']; assert not belt.hide_render
    thickness = next(m for m in belt.modifiers if m.type=='SOLIDIFY'); prior = thickness.thickness
    before = evaluated_surfaces([belt.name])[belt.name]
    try:
        thickness.thickness = prior+.020; bpy.context.view_layer.update()
        delta = float(np.max(np.abs(evaluated_surfaces([belt.name])[belt.name]-before)))
    finally:
        thickness.thickness = prior; bpy.context.view_layer.update()
    rollback = float(np.max(np.abs(evaluated_surfaces([belt.name])[belt.name]-before)))
    assert delta>1e-5 and rollback<2e-5
    fit_render(out,'reopened-mounted-side',90,(0,-1,-10),29.,(1000,700))
    studio.neutral(rig)
    mats = {name:bpy.data.materials['MF_173_'+name] for name in
            ('cloth','scarf','panel','pants','leather','boot','seam','thread','metal','sole')}
    studio.pose_wardrobe(mats)
    for ob in bpy.context.scene.objects:
        if ob.name.startswith(('MF_fit_horse','MF_fit_saddle','MF_fit_bridle','MF_fit_bit','MF_fit_Torus',
                               'MF_fit_Full','MF_fit_rein_','MF_fit_stirrup_leather_','MF_170_tail_')):
            ob.hide_render = True
    fit_render(out,'reopened-upper-front',0,(0,.15,-1.7),7.,(800,850))
    assert accepted_signature(result['protected_signatures'])==result['protected_signatures']
    assert coordinates_digest(tuple(v.co for v in body.data.vertices))==result['body_basis_digest']
    assert data_signature(bpy.data.objects['MF_170_tail_fibers'])==result['static_tail_curve_digest']
    external = [im.name for im in bpy.data.images if im.source=='FILE' and not im.packed_file and not im.packed_files]
    assert not external
    source_unchanged = digest(source)==source_sha; assert source_unchanged
    (out/'result.json').write_text(json.dumps({'reopened':True,'protected_signatures_exact':protected,
        'body_basis_exact':basis,'static_tail_curve_data_exact':tail,'surface_errors':errors,
        'surface_tolerance':2e-5,'visible_garment_revision_max_delta':delta,
        'revision_rollback_max_delta':rollback,'neutral_static_pattern_regenerated':True,
        'unpacked_external_images':external,'source_unchanged':source_unchanged,
        'appearance_acceptance':'PENDING','motion_and_rights':'NOT_QUALIFIED'},indent=2)+'\n')
