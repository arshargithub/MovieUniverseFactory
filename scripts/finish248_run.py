"""Local allowlisted launcher and fresh task binder; never loads credentials."""
import json,os,subprocess,sys,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from finish248_fist import OPS,SOURCES,OUT
from finish248_render import OPS as RENDER_OPS
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def admit_render():
    import numpy as np
    sources={};evidence={};measurements={}
    for name,frames in [('opening08',(305,360,410,450)),('route09',(475,499,523,580,631,676,696))]:
        d=OUT/name;rec=json.loads((d/'result.json').read_text())
        if digest(d/'scene.blend')!=rec['native_sha256'] or digest(d/'contact.npz')!=rec['contact_sha256']:raise ValueError('Changed native/contact')
        z=np.load(d/'contact.npz');err=float(np.max(abs(z['before']-z['after'])))
        if err>2e-5 or rec['camera_max_error']>2e-5 or rec['source_geometry_sha256']!=rec['protected_geometry_sha256']:raise ValueError('Protected motion/geometry')
        if not all(np.isfinite(z[k]).all() for k in ('before','after','reins','thumb_bases','cameras','lenses')):raise ValueError('Invalid pose/contact values')
        sources[name]=rec['native_sha256'];measurements[name]={'nonfinger_world_error':err,'camera_error':rec['camera_max_error'],'frames':len(z['frames'])}
        for f in frames:
            p=d/f'actual-{f}.png';evidence[str(p.relative_to(ROOT))]=digest(p)
    path=OUT/'render-admission.json'
    if path.exists():raise ValueError('Preserve admission')
    path.write_text(json.dumps({'status':'PROCEED_TO_RENDER','sources':sources,'measurements':measurements,'images':evidence,'observation':'All eleven actual-camera controls visually inspected. Closed grasp reads at close opening360 and uphill631/676/696 without the earlier distal straight extension; thumb remains above fingers, cuff and forearm continuous, rein follows grasp. Turn499/523 preserves active posture and grasp.475 preserves checkpoint/escape route,580 establishes checkpoint below,631 checks back,676/696 return attention forward. Accepted identity/wardrobe/terrain/horse framing unchanged in these controls. Scoped six-view bare and four-view contact admission is retained separately.','limits':'Admission to full chronological render only, not final visual acceptance, complete motion review or universal anatomical qualification.'},indent=2)+'\n')
def admit_fit():
    files=[OUT/'fit07'/f'{name}.png' for name in ('actual-360','L-outside','L-palm','R-outside','R-palm')]
    files.extend(OUT/'shape06/continuous12-surface'/f'{side}-{angle}.png' for side in ('L','R') for angle in ('palm','side','knuckles'))
    evidence={str(p.relative_to(ROOT)):digest(p) for p in files}
    target=OUT/'fit07/admission.json'
    if target.exists():raise ValueError('Preserve admission')
    target.write_text(json.dumps({'status':'PROCEED_TO_BUILD','evidence':evidence,'observation':'All eleven named controls visually inspected. Moving the MCP origin toward the palm removes the long false proximal extension. Continuous weights remove the dorsal wedges exposed by03; revised PIP/DIP closure returns fingertips into a compact finger mass. Both finished-surface views show the thumb resting above the index, joined fist silhouette, above-little-finger rein entry and supported exit, with intact sleeve/wrist boundary. Actual360 retains accepted face, clothes and staging. Wrist cutoff in masked bare controls is diagnostic, not production geometry.','limits':'Static scoped admission only. Full motion, reopening and final20-second sequence still required. Not medical hand anatomy or universal rig qualification.'},indent=2)+'\n')
def reconcile():
    from movie_factory.production_knowledge import freeze
    pin=ROOT/'docs/knowledge/pilot/source-pins.json'
    old=json.loads(pin.read_text());new=freeze(ROOT)
    changed=[k for k in old['sources'] if old['sources'][k]!=new['sources'][k]]
    if set(changed) not in ({'unit'},{'workflow','context'},{'index'},{'render'}):raise ValueError(('Unreviewed source changes',changed))
    suffix='' if changed==['unit'] else ('-index' if changed==['index'] else ('-render-audio' if changed==['render'] else '-style'))
    out=ROOT/('.runtime/knowledge-pilot213/reconciliation248'+suffix);out.mkdir(parents=True,exist_ok=False)
    (out/'previous-pins.json').write_bytes(pin.read_bytes())
    (out/'review.json').write_text(json.dumps({'reviewed_diff':'248 additive authority/style/carry-forward reviewed. Render amendment checked against actual245 ten-control strict replay record, preserving historical210 failure.247 final40.18s audio mapping reviewed against its manifest and current unit;248 explicitly preserves the accepted narration/sound in20s cut, bounded exception only. No unrelated historical source change admitted.', 'changed_sources':changed,'new_catalog_sha256':new['catalog_sha256']},indent=2))
    pin.write_text(json.dumps(new,indent=2)+'\n')
def prepare():
    task=json.loads((ROOT/'docs/knowledge/pilot/tasks/rein218.json').read_text())
    task.update(id='rein248-final-fist',intent='Correct Director-reopened distal knuckle bend in final20 second unit; preserve non-finger performance and sound',query='bare fist anatomical MCP pivot palm finger roots weights rein contact final screen believability')
    task['entities']=['hand','rein','shot','renderer']
    files=['scripts/finish248_fist.py','scripts/finish248_render.py','scripts/entrance214_contact.py','scripts/finish248_run.py','docs/knowledge/pilot/rein248-authority.json','docs/planning/SERIES_01_PASHTUN_FINISHED_UNIT_PLAN.md']
    files.append('docs/planning/SHOT_BEAT_QUALITY_BRIEF.md')
    for name in ('opening08','route09'):
        if (OUT/name/'result.json').exists():
            files.extend(str((OUT/name/x).relative_to(ROOT)) for x in ('scene.blend','result.json','contact.npz'))
    trial=ROOT/'.runtime/art-direction/series01-facebuilder-trial-01'
    for name,sha in SOURCES.values():
        folder=trial/name
        if digest(folder/'scene.blend')!=sha:raise ValueError('Source')
        files.extend(str((folder/x).relative_to(ROOT)) for x in ('scene.blend','result.json'))
        rec=json.loads((folder/'result.json').read_text())
        for c in rec['caches']:
            p=(folder/c['path']).resolve()
            if digest(p)!=c['sha256']:raise ValueError('Cache')
            files.append(str(p.relative_to(ROOT)))
    task['inputs']={f:digest(ROOT/f) for f in sorted(set(files))}
    task['execution_authority']={'source':'docs/knowledge/pilot/rein248-authority.json','scope':'Final bare fist/rein repair and20 second delivery explicitly authorized248;219 deferral reopened'}
    task['hypotheses_to_test']=['Distal rest-joint origins or weights create false extended knuckles; further curl alone cannot fix them.','A shifted root may collapse palm or misroute reins; inspect surfaces and actual action.']
    path=ROOT/'docs/knowledge/pilot/tasks/rein248.json';path.write_text(json.dumps(task,indent=2)+'\n')
    subprocess.run([str(ROOT/'.venv/bin/python'),'-m','movie_factory.production_knowledge','packet','--task',str(path.relative_to(ROOT)),'--output','.runtime/knowledge-pilot213/rein248.json'],check=True,cwd=ROOT)
def launch(op):
    if op not in OPS|RENDER_OPS.keys():raise ValueError('Closed operation')
    from movie_factory.production_knowledge import task_packet
    current=task_packet(ROOT,json.loads((ROOT/'docs/knowledge/pilot/tasks/rein248.json').read_text()))
    if not current['dispatch_ready']:raise ValueError(('Knowledge preflight blocked',current['blockers']))
    attempt=1
    while (OUT/f'job-{op}-{attempt:02d}').exists():attempt+=1
    folder=OUT/f'job-{op}-{attempt:02d}';folder.mkdir(parents=True,exist_ok=False)
    job=folder/'job.json';job.write_text(json.dumps({'operation':op}))
    handler=ROOT/'scripts'/('finish248_render.py' if op in RENDER_OPS else 'finish248_fist.py')
    (folder/'handler.py').write_bytes(handler.read_bytes())
    env={k:os.environ[k] for k in ('PATH','HOME','TMPDIR','LANG','LC_ALL') if k in os.environ}
    env['CYCLES_METAL_DISABLE_BINARY_ARCHIVES']='1'
    with (folder/'worker.log').open('w') as log:
        subprocess.run(['/Applications/Blender.app/Contents/MacOS/Blender','--background','--factory-startup','--disable-autoexec','--python-exit-code','7','--python',str(handler),'--',str(job)],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
if __name__=='__main__':
    if sys.argv[1]=='admit-render':admit_render()
    elif sys.argv[1]=='admit-fit':admit_fit()
    elif sys.argv[1]=='reconcile':reconcile()
    elif sys.argv[1]=='prepare':prepare()
    else:launch(sys.argv[1])
