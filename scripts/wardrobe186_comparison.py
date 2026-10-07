"""Render the preserved original with the correction's exact review framing."""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import wardrobe186 as correction


def validate(job):
    if job != {'operation': 'matched-original-front'}:
        raise ValueError('Fixed comparison operation required')
    if correction.SOURCE.is_symlink() or correction.base.digest(correction.SOURCE) != correction.SOURCE_SHA:
        raise ValueError('Unbound original')
    out = correction.base.BASE / 'wardrobe186-comparison07'
    if out.exists() or out.is_symlink():
        raise ValueError('Preserve previous evidence')
    return out


def main():
    import bpy
    from mathutils import Vector
    from wardrobe_riding_fit import fit_render
    args = sys.argv[sys.argv.index('--') + 1:]
    if len(args) != 1:
        raise ValueError('One structured job required')
    out = validate(json.loads(Path(args[0]).read_text()))
    out.mkdir()
    (out / 'handler.py').write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(correction.SOURCE), load_ui=False, use_scripts=False)
    scene = bpy.context.scene
    scene.camera.animation_data_clear()
    scene.camera.data.type = 'ORTHO'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 8
    scene.render.use_persistent_data = True
    for ob in scene.objects:
        if ob.name.startswith(('MF185_gait_', 'MF185_rein_', 'MF185_stirrup_')):
            ob.hide_render = True
    scene.frame_set(265)
    bpy.context.view_layer.update()
    rig = bpy.data.objects['MF_body156_fit_rig']
    center = tuple(rig.matrix_world @ rig.pose.bones['MF185_head'].head + Vector((0, 0, -1.4)))
    fit_render(out, 'original-front', 0, center, 8., (640, 640))
    correction.base.check_protected()
    record = {'source_sha256': correction.SOURCE_SHA, 'frame': 265,
              'center': center, 'ortho_scale': 8., 'resolution': [640, 640],
              'paired_with': '../wardrobe186-delivery06/repaired-original-light-front.png',
              'visual_gate': 'NOT_RUN',
              'reason': 'Original185 front used scale9; this rerender matches correction scale8, camera and light recipe without changing the original asset.'}
    (out / 'result.json').write_text(json.dumps(record, indent=2) + '\n')


if __name__ == '__main__':
    main()
