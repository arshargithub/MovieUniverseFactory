"""Fixed175 source binding and native replay; no paths/code admitted by jobs."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'.runtime/art-direction/series01-facebuilder-trial-01'
OUT=BASE/'wardrobe175-operating'


def sha(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def source_paths():
    return sorted((ROOT/'src/movie_factory/adapters/blender').glob('*.py'))+[
        ROOT/'scripts/wardrobe_construction174.py',ROOT/'scripts/wardrobe_outer175.py',
        Path(__file__).resolve(),ROOT/'tests/unit/test_wardrobe_outer175.py',
        ROOT/'scripts/package_wardrobe_studio.py',ROOT/'scripts/package_wardrobe_fit_review.py',
        ROOT/'scripts/check_outer_shawl_gallery.cjs']


def input_paths():
    return [BASE/'wardrobe174-seal01/dressed-fit.blend',
            BASE/'wardrobe174-seal01/result.json',
            BASE/'wardrobe174-preview09/neutral-before-cleanup.npz',
            ROOT/'.runtime/assets/series01-dressing-source/scarf-original.glb',
            ROOT/'.runtime/art-direction/series01-pashtun-baseline-v01/frontal-v02-individualized.png',
            ROOT/'.runtime/art-direction/series01-pashtun-baseline-v01/portrait-v07-individualized.png']


def write(path,data):path.write_text(json.dumps(data,indent=2)+'\n')


def bind():
    OUT.mkdir(exist_ok=True)
    path=OUT/'source-binding.json'
    if path.exists() or (BASE/'wardrobe175-seal01').exists():raise ValueError('Bind once before dispatch')
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    tree=subprocess.check_output(['git','rev-parse','HEAD^{tree}'],cwd=ROOT,text=True).strip()
    rows=[]
    for p in source_paths():
        rel=str(p.relative_to(ROOT));blob=subprocess.check_output(['git','show',commit+':'+rel],cwd=ROOT)
        if p.is_symlink() or hashlib.sha256(blob).hexdigest()!=sha(p):raise ValueError('Commit source first: '+rel)
        rows.append({'path':rel,'sha256':sha(p)})
    write(path,{'source_commit':commit,'source_git_tree':tree,'source_files':rows,
        'inputs':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in input_paths()],
        'provenance':'Frozen selected transformation; earlier exploratory handler revisions not reconstructed'})


def binding():
    path=OUT/'source-binding.json'
    if path.is_symlink():raise ValueError('Binding symlink')
    value=json.loads(path.read_text())
    for key,paths in (('source_files',source_paths()),('inputs',input_paths())):
        rows=value[key]
        if len(rows)!=len(paths) or {r['path'] for r in rows}!={str(p.relative_to(ROOT)) for p in paths}:
            raise ValueError('Unexpected manifest')
        for row in rows:
            p=ROOT/row['path']
            if p.is_symlink() or sha(p)!=row['sha256']:raise ValueError('Bound file changed')
    return value


def protection():
    import bpy
    from wardrobe_riding_fit import accepted_signature
    from body_studio_fit import coordinates_digest
    from static_tail_dock import data_signature
    reference=json.loads((BASE/'wardrobe174-seal01/result.json').read_text())
    assert accepted_signature(reference['protected_signatures'])==reference['protected_signatures']
    assert coordinates_digest(tuple(v.co for v in bpy.data.objects['MF_studio_adult_body'].data.vertices))==reference['body_basis_digest']
    assert data_signature(bpy.data.objects['MF_170_tail_fibers'])==reference['static_tail_curve_digest']
    return reference


def seal(out):
    import bpy
    import numpy as np
    import wardrobe_studio as studio
    from wardrobe_riding_fit import evaluated_surfaces
    frozen=binding();protection()
    studio.render_set(out,full=True)
    reference=protection()
    names=[o.name for o in bpy.context.scene.objects if not o.hide_render and o.type=='MESH']
    np.savez_compressed(out/'evaluated-surfaces.npz',**evaluated_surfaces(names))
    for text in bpy.data.texts:text.use_module=False
    scene=bpy.context.scene;scene['MF_175_source_commit']=frozen['source_commit']
    scene['MF_175_asset_status']='Static appearance review pending; not motion qualified'
    scene['MF_175_source_binding_sha256']=sha(OUT/'source-binding.json')
    bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'dressed-fit.blend'),compress=True)
    write(out/'result.json',{'native_sha256':sha(out/'dressed-fit.blend'),
        'source_commit':frozen['source_commit'],'source_git_tree':frozen['source_git_tree'],
        'source_binding_sha256':sha(OUT/'source-binding.json'),
        **{k:reference[k] for k in ('protected_signatures','body_basis_digest','static_tail_curve_digest')},
        'visual_gate':'NOT_RUN','Director_acceptance':'PENDING','static_only':True,
        'blender_version':bpy.app.version_string,'blender_build_hash':str(bpy.app.build_hash)})


def verify(out):
    import bpy
    import numpy as np
    import wardrobe_studio as studio
    from wardrobe_riding_fit import evaluated_surfaces,fit_render
    selected=BASE/'wardrobe175-seal01';frozen=binding()
    result=json.loads((selected/'result.json').read_text())
    assert sha(selected/'dressed-fit.blend')==result['native_sha256']
    original_shell=next(m for m in bpy.data.objects['MF_173_waist_belt'].modifiers if m.type=='SOLIDIFY')
    initial_shell=(original_shell.thickness,original_shell.offset)
    bpy.ops.wm.open_mainfile(filepath=str(selected/'dressed-fit.blend'),load_ui=False,use_scripts=False)
    assert bpy.context.scene['MF_175_source_commit']==frozen['source_commit']
    assert bpy.context.scene['MF_175_source_binding_sha256']==sha(OUT/'source-binding.json')==result['source_binding_sha256']
    with np.load(selected/'evaluated-surfaces.npz',allow_pickle=False) as reference:
        actual=evaluated_surfaces(reference.files)
        errors={n:float(np.max(np.abs(actual[n]-reference[n]))) if actual[n].shape==reference[n].shape else None for n in reference.files}
    assert all(e is not None and e<2e-5 for e in errors.values())
    protection()
    belt=bpy.data.objects['MF_173_waist_belt'];shell=next(m for m in belt.modifiers if m.type=='SOLIDIFY')
    before=evaluated_surfaces([belt.name])[belt.name];thickness=shell.thickness
    try:
        shell.thickness=thickness+.020;bpy.context.view_layer.update()
        delta=float(np.max(np.abs(evaluated_surfaces([belt.name])[belt.name]-before)))
    finally:
        shell.thickness=thickness;bpy.context.view_layer.update()
    rollback=float(np.max(np.abs(evaluated_surfaces([belt.name])[belt.name]-before)))
    assert delta>1e-5 and rollback<2e-5
    fit_render(out,'reopened-mounted-side',90,(0,-1,-10),29.,(1000,700))
    studio.neutral(bpy.data.objects['MF_body156_fit_rig']);shell.thickness,shell.offset=initial_shell
    bpy.context.view_layer.update();studio.pose_wardrobe(studio.make_materials())
    for ob in bpy.context.scene.objects:
        if ob.name.startswith(('MF_fit_horse','MF_fit_saddle','MF_fit_bridle','MF_fit_bit','MF_fit_Torus',
                               'MF_fit_Full','MF_fit_rein_','MF_fit_stirrup_leather_','MF_170_tail_')):ob.hide_render=True
    fit_render(out,'reopened-upper-front',0,(0,.15,-1.7),7.,(800,850))
    protection()
    external=[i.name for i in bpy.data.images if i.source=='FILE' and not i.packed_file and not i.packed_files]
    assert not external
    write(out/'result.json',{'surface_errors':errors,'surface_tolerance':2e-5,
        'protected_exact':True,'body_basis_exact':True,'tail_exact':True,
        'edit_delta':delta,'rollback_delta':rollback,'unpacked_external_images':external,
        'source_binding_sha256':sha(OUT/'source-binding.json'),'appearance':'PENDING','motion':'NOT_QUALIFIED'})


GALLERY=Path('/Users/adisharma/.codex/visualizations/2026/09/09/01a0878c-e7a2-75e0-873c-c31d97f879a1/pashtun-outer-shawl.html')


def gallery_frames():
    from package_wardrobe_studio import ROWS
    refs=ROOT/'.runtime/art-direction/series01-pashtun-baseline-v01'
    selected=BASE/'wardrobe175-seal01'
    return [(refs/'frontal-v02-individualized.png','Original front','Approved illustrated front'),
            (refs/'portrait-v07-individualized.png','Original portrait','Approved illustrated portrait')]+[
        (selected/(name+'.png'),short,short+' · outer175 · appearance pending') for name,short in ROWS]


def publish():
    """Package only manually reviewed selected images and valid reopen proof."""
    import base64
    from io import BytesIO
    from PIL import Image,ImageChops
    binding()
    selected=BASE/'wardrobe175-seal01';verified=BASE/'wardrobe175-verify01'
    result=json.loads((selected/'result.json').read_text())
    assert sha(selected/'dressed-fit.blend')==result['native_sha256']
    proof=json.loads((verified/'result.json').read_text())
    assert proof['protected_exact'] and proof['body_basis_exact'] and proof['tail_exact']
    assert all(e is not None and e<2e-5 for e in proof['surface_errors'].values())
    assert proof['edit_delta']>1e-5 and proof['rollback_delta']<2e-5 and not proof['unpacked_external_images']
    review=json.loads((OUT/'visual-review.json').read_text())
    criteria={'reference_layer_order','continuous_shoulders','exterior_rear_courses',
              'tucked_broad_ends','required_pose_arms','protected_foundation','adjacent_regressions'}
    assert set(review['criteria'])==criteria
    assert all(r['status']=='PASS' and r['evidence'] for r in review['criteria'].values())
    assert review['known_blockers']==[] and review['Director_acceptance']=='PENDING'
    reviewed=set(review['reviewed_images']);assert {p.name for p in selected.glob('*.png')}<=reviewed
    assert {p.name for p in verified.glob('*.png')}<=reviewed
    pixels={}
    for a,b in [('upper-front.png','reopened-upper-front.png'),('mounted-side.png','reopened-mounted-side.png')]:
        difference=ImageChops.difference(Image.open(selected/a).convert('RGB'),Image.open(verified/b).convert('RGB'))
        pixels[a]=max(hi for lo,hi in difference.getextrema())
    assert max(pixels.values())<=4
    frames=gallery_frames()
    template=GALLERY.read_text();assert '/* REVIEW_DATA */[]' in template
    for quality in (80,74,68,62):
        rows=[]
        for path,short,label in frames:
            picture=Image.open(path).convert('RGB');picture.thumbnail((850,700))
            stream=BytesIO();picture.save(stream,'JPEG',quality=quality,optimize=True)
            rows.append({'short':short,'label':label,'image':'data:image/jpeg;base64,'+base64.b64encode(stream.getvalue()).decode()})
        content=template.replace('/* REVIEW_DATA */[]',json.dumps(rows))
        if len(content.encode())<970000:break
    assert len(content.encode())<1000000
    GALLERY.write_text(content)
    write(OUT/'pixel-comparison.json',pixels)
    print(json.dumps({'gallery_views':len(rows),'gallery_bytes':len(content.encode()),'pixel_differences':pixels}))


def receipt():
    import sqlite3
    from datetime import datetime
    con=sqlite3.connect(f'file:{ROOT/".runtime/experiment-ops.sqlite3"}?mode=ro',uri=True)
    events=[json.loads(p) for p, in con.execute('SELECT payload FROM events ORDER BY seq') if json.loads(p)['event_id'].startswith('wardrobe175-')]
    con.close()
    starts={e['job_id']:e for e in events if e['event_type']=='job_started'}
    ends={e['job_id']:e for e in events if e['event_type']=='job_completed'}
    assert starts.keys()==ends.keys()
    start=next(e for e in events if e['event_id']=='wardrobe175-work-start')
    end=next(e for e in events if e['event_id']=='wardrobe175-work-end')
    seconds=(datetime.fromisoformat(end['utc'])-datetime.fromisoformat(start['utc'])).total_seconds()
    manifest=[{'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size}
        for folder in ('wardrobe175-seal01','wardrobe175-verify01') for p in sorted((BASE/folder).iterdir()) if p.is_file()]
    retained=sum(p.stat().st_size for folder in BASE.glob('wardrobe175-*') if folder.is_dir() for p in folder.rglob('*') if p.is_file())
    write(OUT/'artifact-manifest.json',manifest);write(OUT/'scope-events.json',events)
    card={'status':'STATIC_APPEARANCE_REVIEW_READY_DIRECTOR_PENDING','captured_utc_activity_seconds':seconds,
        'prior_partial_seconds':67788.491694,'cumulative_partial_seconds':67788.491694+seconds,
        'lifetime_net_seconds':None,'engineering_model':None,'reasoning_effort':None,'engineering_tokens':None,
        'engineering_dollar_cost':None,'paid_provider_calls':0,'asset_purchases':0,
        'all_jobs_reconciled':True,'native_job_count':sum(e['job_kind']=='native' for e in starts.values()),
        'process_failures':sum(e.get('returncode') not in (0,None) for e in ends.values()),
        'retained_bytes_before_receipt':retained,'gallery_bytes':GALLERY.stat().st_size,
        'capture_limits':'Partial cumulative history; current initial context recovery and final receipt/commit overhead excluded',
        'limits':['Static pose-regenerated garments, not motion/cloth physics','Creative acceptance pending',
                  'Not cultural, rights, industry certification or release qualification','Local commits are not off-device backup']}
    write(OUT/'CARD.json',card);print(json.dumps(card))


def failure():
    """Honest failed-method comparison/receipt; never a selected native bundle."""
    import base64
    from datetime import datetime
    from io import BytesIO
    import sqlite3
    from PIL import Image
    OUT.mkdir(exist_ok=True)
    review=json.loads((OUT/'method-disposition.json').read_text())
    assert review['status']=='FAILED_INTERNAL_REVIEW_DIRECTOR_DECISION_REQUIRED'
    assert review['known_blockers'] and review['Director_acceptance']=='NOT_REQUESTED_FOR_FAILED_CANDIDATE'
    assert not (BASE/'wardrobe175-seal01').exists() and not (OUT/'source-binding.json').exists()
    last=BASE/'wardrobe175-preview32'
    result=json.loads((last/'result.json').read_text())
    assert result['protected_exact'] and result['body_basis_exact']
    assert result['handler_sha256']==sha(ROOT/'scripts/wardrobe_outer175.py')
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    source=[]
    for p in source_paths():
        rel=str(p.relative_to(ROOT));blob=subprocess.check_output(['git','show',commit+':'+rel],cwd=ROOT)
        assert hashlib.sha256(blob).hexdigest()==sha(p)
        source.append({'path':rel,'sha256':sha(p)})
    write(OUT/'failed-source-preservation.json',{'commit':commit,'source_files':source,
        'inputs':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in input_paths()],
        'last_handler_matches_committed_bytes':True,
        'provenance':'Post-run preservation of failed32 source, NOT a pre-execution seal or qualified replay'})
    refs=ROOT/'.runtime/art-direction/series01-pashtun-baseline-v01'
    frames=[(refs/'frontal-v02-individualized.png','Original front','Approved illustrated front'),
        (refs/'portrait-v07-individualized.png','Original portrait','Approved illustrated portrait')]
    frames += [(last/(name+'.png'),label,label+' · diagnostic32 · FAILED internal review') for name,label in
        [('upper-front','Front'),('upper-right','Right ¾'),('upper-rear','Back'),
         ('upper-profile','Profile'),('mounted-left','Riding front'),('mounted-rear','Riding rear'),
         ('mounted-profile','Riding profile'),('partial-rear','Partial-lean rear')]]
    assert all(p.name in review['reviewed_images'] for p,_,_ in frames[2:])
    template=GALLERY.read_text();assert '/* REVIEW_DATA */[]' in template
    for quality in (80,74,68,62):
        rows=[]
        for p,label,caption in frames:
            picture=Image.open(p).convert('RGB');picture.thumbnail((850,700))
            stream=BytesIO();picture.save(stream,'JPEG',quality=quality,optimize=True)
            rows.append({'short':label,'label':caption,'image':'data:image/jpeg;base64,'+base64.b64encode(stream.getvalue()).decode()})
        content=template.replace('/* REVIEW_DATA */[]',json.dumps(rows))
        if len(content.encode())<970000:break
    assert len(content.encode())<1000000
    GALLERY.write_text(content)
    con=sqlite3.connect(f'file:{ROOT/".runtime/experiment-ops.sqlite3"}?mode=ro',uri=True)
    events=[json.loads(p) for p, in con.execute('SELECT payload FROM events ORDER BY seq')
            if json.loads(p)['event_id'].startswith('wardrobe175-')]
    con.close()
    starts={e['job_id']:e for e in events if e['event_type']=='job_started'}
    ends={e['job_id']:e for e in events if e['event_type']=='job_completed'}
    assert starts.keys()==ends.keys()
    start=next(e for e in events if e['event_id']=='wardrobe175-work-start')
    end=next(e for e in events if e['event_id']=='wardrobe175-work-end')
    seconds=(datetime.fromisoformat(end['utc'])-datetime.fromisoformat(start['utc'])).total_seconds()
    manifest=[{'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size}
        for folder in BASE.glob('wardrobe175-*') if folder.is_dir() and folder!=OUT
        for p in sorted(folder.rglob('*')) if p.is_file()]
    write(OUT/'diagnostic-manifest.json',manifest);write(OUT/'scope-events.json',events)
    card={'status':review['status'],'known_blockers':review['known_blockers'],
        'captured_utc_activity_seconds':seconds,'prior_partial_seconds':67788.491694,
        'cumulative_partial_seconds':67788.491694+seconds,'lifetime_net_seconds':None,
        'engineering_model':None,'reasoning_effort':None,'engineering_tokens':None,'engineering_dollar_cost':None,
        'paid_provider_calls':0,'asset_purchases':0,'all_jobs_reconciled':True,
        'native_job_count':sum(e['job_kind']=='native' for e in starts.values()),
        'process_failures':sum(e.get('returncode') not in (0,None) for e in ends.values()),
        'retained_diagnostic_bytes':sum(r['bytes'] for r in manifest),'gallery_bytes':len(content.encode()),
        'selected_native_outputs':0,'director_accepted_outputs':0,'creative_qualification':'FAIL',
        'episode_status':'OPEN','remote_push':False,'media_backup':False,
        'capture_limits':'Partial history; initial context recovery and final receipt/commit overhead excluded',
        'recommended_choice':'PROPOSED single broad outside crossover, soft closed rear; not adopted',
        'limits':['Technical preservation is not creative acceptance','No selected sealing or native replay performed',
                  'Not motion/rights/release qualification','Local commits are not off-device backup']}
    write(OUT/'CARD.json',card);print(json.dumps(card))


if __name__=='__main__':
    import sys
    if sys.argv[1:]==['bind']:bind()
    elif sys.argv[1:]==['publish']:publish()
    elif sys.argv[1:]==['receipt']:receipt()
    elif sys.argv[1:]==['failure']:failure()
    else:raise ValueError('Only fixed bind/publish/receipt/failure actions')
