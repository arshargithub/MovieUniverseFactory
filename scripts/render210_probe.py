"""Read-only scene probes for authorized local render investigation210.

Closed operations, pinned sources, isolated output directories, no saved scene or
preferences, and no runtime-generated code inputs. Run with embedded scripts off.
"""
import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / '.runtime/art-direction/series01-facebuilder-trial-01'
OUT = ROOT / '.runtime/art-direction/series01-render210'
SOURCES = {
    'opening': ('entrance209-opening03', '0c29e23175dacccdbcbd84e50b94ad279f2b87c0f152bee4d85516148502d204'),
    'route': ('entrance209-route04', '411c1b9916dc4ccd508becb7e95622ea0e42d3367200f359279dec9c29d4deee'),
}
OPS = {
    'inspect': ('opening', 'CPU', None, ()),
    'cpu_open': ('opening', 'CPU', None, (217, 300, 343, 349, 360, 217)),
    'metal_open': ('opening', 'GPU', 'ON', (217, 300, 343, 349, 360, 217)),
    'metaloff_open': ('opening', 'GPU', 'OFF', (217, 300, 343, 349, 360, 217)),
    'cpu_route': ('route', 'CPU', None, (427, 520, 620)),
    'metal_route': ('route', 'GPU', 'ON', (427, 520, 620)),
    'metaloff_route': ('route', 'GPU', 'OFF', (427, 520, 620)),
    'cpu_delivery': ('opening', 'CPU', None, (217, 360)),
    'metal_delivery': ('opening', 'GPU', 'ON', (217, 360)),
    'metal_motion': ('opening', 'GPU', 'ON', tuple(range(343, 355))),
}

def validate(job):
    if not isinstance(job, dict) or set(job) != {'operation'} or not isinstance(job['operation'], str) or job['operation'] not in OPS:
        raise ValueError('Only fixed render210 operations are admitted')
    return OPS[job['operation']]

def digest(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def main():
    import bpy
    args = sys.argv[sys.argv.index('--') + 1:]
    if len(args) != 1:
        raise ValueError('One structured job path required')
    job = json.loads(Path(args[0]).read_text())
    source_kind, device, metalrt, frames = validate(job)
    folder, expected = SOURCES[source_kind]
    source = BASE / folder / 'scene.blend'
    record = json.loads((source.parent / 'result.json').read_text())
    if source.is_symlink() or digest(source) != expected:
        raise ValueError('Pinned native source changed')
    for row in record['caches']:
        p = (source.parent / row['path']).resolve()
        if not p.is_relative_to(BASE.resolve()) or digest(p) != row['sha256']:
            raise ValueError('Pinned cache changed')
    out = OUT / job['operation']
    if out.exists():
        raise ValueError('Preserve prior diagnostic evidence')
    out.mkdir(parents=True)
    (out / 'handler.py').write_bytes(Path(__file__).read_bytes())
    start = time.perf_counter()
    bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False, use_scripts=False)
    load_seconds = time.perf_counter() - start
    scene = bpy.context.scene
    pref = bpy.context.preferences.addons['cycles'].preferences
    devices = pref.get_devices_for_type('METAL')
    settings = {n: getattr(scene.cycles, n) for n in (
        'samples', 'use_adaptive_sampling', 'adaptive_threshold', 'adaptive_min_samples',
        'use_denoising', 'denoiser', 'denoising_prefilter', 'max_bounces',
        'diffuse_bounces', 'glossy_bounces', 'transmission_bounces', 'volume_bounces',
        'volume_step_rate', 'volume_max_steps') if hasattr(scene.cycles, n)}
    props = {}
    for prop in pref.bl_rna.properties:
        if 'metal' in prop.identifier or 'denois' in prop.identifier:
            props[prop.identifier] = {'value': str(getattr(pref, prop.identifier)),
                                      'enum': [x.identifier for x in prop.enum_items] if prop.type == 'ENUM' else []}
    info = {'operation': job['operation'], 'source_sha256': expected,
            'blender_version': bpy.app.version_string, 'load_seconds': load_seconds,
            'devices': [{'name': d.name, 'type': d.type} for d in devices],
            'available_preferences': props, 'source_cycles': settings,
            'source_persistent_data': scene.render.use_persistent_data,
            'source_motion_blur': scene.render.use_motion_blur,
            'source_compositor': scene.use_nodes,
            'objects': len(scene.objects), 'meshes': len(bpy.data.meshes),
            'mesh_vertices': sum(len(m.vertices) for m in bpy.data.meshes),
            'frames': [], 'saved_scene_or_preferences': False, 'visual_gate': 'NOT_RUN'}
    (out / 'inspection.json').write_text(json.dumps(info, indent=2) + '\n')
    if frames:
        if device == 'GPU':
            pref.compute_device_type = 'METAL'
            if not any(d.type == 'METAL' for d in devices):
                raise ValueError('No Metal device; no silent CPU fallback')
            for d in devices:
                d.use = d.type == 'METAL'
            if not hasattr(pref, 'metalrt'):
                raise ValueError('Requested MetalRT control unavailable')
            pref.metalrt = metalrt
        for ob in scene.objects:
            for m in ob.modifiers:
                if m.type in ('SMOOTH', 'CORRECTIVE_SMOOTH', 'SUBSURF'):
                    m.show_viewport = False
        scene.render.engine = 'CYCLES'
        scene.cycles.device = device
        scene.cycles.samples = 8
        scene.render.use_persistent_data = False
        resolution = (1080, 1920) if job['operation'].endswith('_delivery') else (432, 768)
        scene.render.resolution_x, scene.render.resolution_y = resolution
        scene.render.resolution_percentage = 100
        info['profile'] = {'device': device, 'metalrt': metalrt, 'persistent_data': False,
                           'samples': 8, 'resolution': list(resolution), 'threads': scene.render.threads,
                           'cycles_device_selection': [{'name': d.name, 'type': d.type, 'use': d.use} for d in devices]}
        for i, f in enumerate(frames):
            t = time.perf_counter()
            scene.frame_set(f)
            bpy.context.view_layer.update()
            prepared = time.perf_counter()
            p = out / f'{i:02d}-{f}.png'
            scene.render.filepath = str(p)
            if bpy.ops.render.render(write_still=True) != {'FINISHED'}:
                raise ValueError('Render failed')
            row = {'frame': f, 'image': p.name, 'evaluation_seconds': prepared-t,
                   'render_seconds': time.perf_counter()-prepared, 'sha256': digest(p)}
            info['frames'].append(row)
            (out / 'progress.json').write_text(json.dumps(info, indent=2) + '\n')
            print('RENDER210', job['operation'], row, flush=True)
    if digest(source) != expected:
        raise ValueError('Protected native changed')
    info['status'] = 'DIAGNOSTIC_COMPLETE_NOT_VISUALLY_QUALIFIED'
    (out / 'result.json').write_text(json.dumps(info, indent=2) + '\n')

if __name__ == '__main__':
    main()
