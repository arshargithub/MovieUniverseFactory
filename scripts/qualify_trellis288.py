"""Bounded local synthetic qualification. No provider calls or model downloads."""
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'.runtime/trellis288/fixture'
EVIDENCE = ROOT/'results/sikh288'


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate(job):
    if not isinstance(job, dict) or set(job) != {'operation'} or job['operation'] not in {'build', 'inspect', 'reopen', 'package'}:
        raise ValueError('Fixed structured operation required')
    return job['operation']


def packet(job):
    from movie_factory.production_knowledge import task_packet, packet_markdown
    task = json.loads((EVIDENCE/'task.json').read_text())
    task['id'] = 'trellis288-'+validate(job)
    task['phase'] = 'execution'
    task['execution_authority'] = {'source':'results/sikh288/STRATEGY.md',
                                 'scope':'Local synthetic exporter adapter tests; no production generation'}
    task['open_decisions'] = []  # This dispatch is local only, not AWS/inference.
    paths = [Path(__file__), EVIDENCE/'STRATEGY.md', ROOT/'tests/test_trellis288.py']
    paths += list((ROOT/'src/movie_factory/trellis_adapter').glob('*.py'))
    if job['operation'] != 'build': paths += [OUT/'fixture.glb', OUT/'fixture.json']
    if job['operation'] == 'reopen': paths += [OUT/'fixture.blend', OUT/'blender-inspect.json']
    task['inputs'].update({str(p.relative_to(ROOT)):sha(p) for p in paths})
    p = task_packet(ROOT, task)
    (EVIDENCE/(task['id']+'-packet.json')).write_text(json.dumps(p, indent=2))
    (EVIDENCE/(task['id']+'-packet.md')).write_text(packet_markdown(p))
    if not p['dispatch_ready']: raise RuntimeError(p['blockers'])
    return p


def build():
    from movie_factory.trellis_adapter.fixture import build_fixture
    from movie_factory.trellis_adapter.patch import unified_patch
    OUT.mkdir(parents=True,exist_ok=True)
    if (OUT/'fixture.glb').exists(): raise ValueError('Preserve prior fixture')
    mesh, receipt = build_fixture()
    mesh.export(OUT/'fixture.glb')
    receipt['glb_sha256'] = sha(OUT/'fixture.glb')
    (OUT/'fixture.json').write_text(json.dumps(receipt,indent=2))
    (EVIDENCE/'adapter.patch').write_text(unified_patch(EVIDENCE/'upstream'))
    deps = []
    for d in importlib.metadata.distributions(path=[str(ROOT/'.runtime/trellis288-deps')]):
        files = [f for f in (d.files or []) if any(s in str(f).lower() for s in ['license','notice','copying'])]
        deps.append({'name':d.metadata['Name'],'version':d.version,
                     'license_expression':d.metadata.get('License-Expression'),
                     'license_metadata':d.metadata.get('License'),
                     'notices':[{'path':str(f), 'sha256':sha(d.locate_file(f))} for f in files if d.locate_file(f).is_file()]})
    (EVIDENCE/'local-dependencies.json').write_text(json.dumps({'scope':'Mac CPU fixture only, NOT Linux/CUDA/inference SBOM','packages':deps},indent=2))
    print(json.dumps(receipt))


def snapshot():
    import bpy
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    if len(meshes) != 1: raise ValueError('Expected exactly one imported fixture mesh')
    obj=meshes[0]
    coords=sorted([[round(v,6) for v in (obj.matrix_world @ vert.co)] for vert in obj.data.vertices])
    expected=sorted([[0,0,.2],[1,0,.5],[1,1,.6],[0,1,.3]])
    if coords != expected: raise ValueError(('Axis/geometry mismatch',coords))
    bs=next(n for n in obj.active_material.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    if not all(bs.inputs[k].is_linked for k in ['Base Color','Metallic','Roughness']):
        raise ValueError('Missing imported PBR channel connections')
    return {'vertices':coords,'faces':len(obj.data.polygons),'uv_count':len(obj.data.uv_layers.active.data),
            'images':sorted([{'name':i.name,'size':list(i.size),'colorspace':i.colorspace_settings.name} for i in bpy.data.images if i.source=='FILE'],key=lambda x:x['name']),
            'pbr_channels_linked':True}


def blender_run(job):
    import bpy
    op=validate(job)
    receipt=json.loads((OUT/'fixture.json').read_text())
    if sha(OUT/'fixture.glb') != receipt['glb_sha256']: raise ValueError('GLB drift')
    if op=='reopen':
        bpy.ops.wm.open_mainfile(filepath=str(OUT/'fixture.blend'))
        actual=snapshot();expected=json.loads((OUT/'blender-inspect.json').read_text())
        if actual != expected: raise ValueError('Reopen mismatch')
        (OUT/'blender-reopen.json').write_text(json.dumps({'matches':True,'snapshot':actual},indent=2))
        return
    if op!='inspect': raise ValueError('Blender only inspects synthetic GLB')
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.gltf(filepath=str(OUT/'fixture.glb'))
    actual=snapshot()
    (OUT/'blender-inspect.json').write_text(json.dumps(actual,indent=2))
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'fixture.blend'))
    obj=next(o for o in bpy.context.scene.objects if o.type=='MESH')
    # Diagnostic emission render checks texture/UV orientation, NOT PBR lighting.
    material=obj.active_material.copy();obj.active_material=material
    nodes=material.node_tree.nodes;links=material.node_tree.links
    bs=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
    source=bs.inputs['Base Color'].links[0].from_socket
    output=next(n for n in nodes if n.type=='OUTPUT_MATERIAL')
    emission=nodes.new('ShaderNodeEmission');links.new(source,emission.inputs['Color']);links.new(emission.outputs[0],output.inputs['Surface'])
    camdata=bpy.data.cameras.new('UV diagnostic');cam=bpy.data.objects.new('UV diagnostic',camdata);bpy.context.collection.objects.link(cam)
    cam.location=(.5,.5,4);camdata.type='ORTHO';camdata.ortho_scale=1.2
    scene=bpy.context.scene;scene.camera=cam;scene.render.engine='CYCLES'
    scene.cycles.device='CPU';scene.cycles.samples=1
    scene.render.resolution_x=384;scene.render.resolution_y=384;scene.render.resolution_percentage=100
    scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.view_settings.exposure=0;scene.view_settings.gamma=1
    scene.render.image_settings.file_format='PNG';scene.render.filepath=str(OUT/'uv-diagnostic.png')
    bpy.ops.render.render(write_still=True)


def launch(job):
    op=validate(job);p=packet(job)
    if op=='build': build();return
    if op=='package':
        from movie_factory.trellis_adapter.patch import unified_patch
        from movie_factory.budget import BudgetLedger
        from PIL import Image
        ledger=BudgetLedger(ROOT/'.runtime/trellis288/budget.jsonl',campaign_limit=15,
                            scope_limits={'qualification':15},stage_limits={'gpu_session':(15,1)},
                            request_limit=1,request_ceiling_usd=15)
        (EVIDENCE/'budget-status.json').write_text(json.dumps(ledger.summary(),indent=2))
        patch=EVIDENCE/'adapter.patch';patch.write_text(unified_patch(EVIDENCE/'upstream'))
        im=Image.open(OUT/'uv-diagnostic.png')
        expected={(112,112):(0,255,51),(272,112):(255,255,51),(112,272):(0,0,51),(272,272):(255,0,51)}
        observed={str(pt):im.getpixel(pt)[:3] for pt in expected}
        if any(max(abs(a-b) for a,b in zip(observed[str(pt)],rgb))>1 for pt,rgb in expected.items()):
            raise ValueError('Independent Blender UV/color check failed')
        (EVIDENCE/'visual-check.json').write_text(json.dumps({'scope':'Emission UV orientation only; not material beauty or actor quality',
             'image':str((OUT/'uv-diagnostic.png').relative_to(ROOT)), 'sha256':sha(OUT/'uv-diagnostic.png'),
             'expected':{str(k):v for k,v in expected.items()},'observed':observed,'pass':True},indent=2))
        result=subprocess.run([sys.executable,'-m','pytest','tests/test_trellis288.py','-q','--junitxml='+str(EVIDENCE/'tests.xml')],cwd=ROOT,capture_output=True,text=True)
        (EVIDENCE/'tests.txt').write_text(result.stdout+result.stderr)
        if result.returncode: raise RuntimeError('Qualification tests failed')
        paths=list((ROOT/'src/movie_factory/trellis_adapter').glob('*.py'))+[Path(__file__),ROOT/'scripts/trellis288_cuda_probe.py',ROOT/'tests/test_trellis288.py',patch]
        paths+=list((EVIDENCE/'upstream').glob('*.py'))+list(OUT.glob('*.json'))+list(OUT.glob('*.glb'))+list(OUT.glob('*.png'))+[OUT/'fixture.blend']
        (EVIDENCE/'artifact-manifest.json').write_text(json.dumps({str(f.relative_to(ROOT)):sha(f) for f in paths},indent=2))
        print(result.stdout);return
    log=OUT/(op+'.log')
    if log.exists():
        log=next((OUT/f'{op}-{i:02d}.log' for i in range(2,4) if not (OUT/f'{op}-{i:02d}.log').exists()), None)
        if log is None: raise ValueError('Three dispatches exhausted; reassess')
    env={k:os.environ[k] for k in ('PATH','HOME','TMPDIR','LANG','LC_ALL') if k in os.environ}
    start=time.monotonic()
    with log.open('w') as handle:
        result=subprocess.run(['/Applications/Blender.app/Contents/MacOS/Blender','--background','--offline-mode','--factory-startup','--disable-autoexec','--python-exit-code','7','--python',str(Path(__file__).resolve()),'--',json.dumps(job)],env=env,stdout=handle,stderr=subprocess.STDOUT)
    (EVIDENCE/(log.stem+'-job.json')).write_text(json.dumps({'seconds':time.monotonic()-start,'returncode':result.returncode,'packet_digest':p['packet_digest']},indent=2))
    if result.returncode: raise RuntimeError(str(log))
    print(op+' complete')


if __name__=='__main__':
    if '--' in sys.argv:
        args=sys.argv[sys.argv.index('--')+1:]
        if len(args)!=1: raise ValueError('One structured job required')
        blender_run(json.loads(args[0]))
    else:
        if len(sys.argv)!=2: raise ValueError('build, inspect or reopen')
        launch({'operation':sys.argv[1]})
