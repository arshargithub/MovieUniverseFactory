"""Bind, package and record the manually reviewed costume173 static scope.

Never infer creative acceptance from a native exit, a test or a checksum.
"""
import base64
from datetime import datetime,timezone
import hashlib
from io import BytesIO
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
from PIL import Image,ImageChops
sys.path.insert(0,str(Path(__file__).resolve().parent))
from package_wardrobe_fit_review import check_review

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'.runtime/art-direction/series01-facebuilder-trial-01'
OUT=BASE/'wardrobe173-operating'
GALLERY=Path('/Users/adisharma/.codex/visualizations/2026/09/09/01a0878c-e7a2-75e0-873c-c31d97f879a1/pashtun-studio-wardrobe.html')
CRITERIA={'protected_foundation','soft_supported_scarf','coherent_chest_fall','continuous_loaded_leather','tailored_worn_textiles','closed_footwear_static_fit','neutral_full_partial_interfaces','adjacent_regressions','whole_static_appearance'}
ROWS=[('upper-front','Front close-up'),('upper-left','Left ¾'),('upper-right','Right ¾'),('upper-rear','Rear close-up'),('upper-profile','True profile'),('chest-left','Cloth detail left'),('chest-right','Cloth detail right'),('standing-front','Full front'),('standing-side','Standing side'),('standing-rear','Full back'),('mounted-side','Riding side'),('mounted-opposite-side','Other riding side'),('mounted-upper-left','Riding left ¾'),('mounted-upper-right','Riding right ¾'),('mounted-upper-rear','Riding rear ¾'),('mounted-partial','Partial lean'),('standing-boot','Boot close-up')]
INPUT_PATHS={'%s/wardrobe172-seal01/dressed-fit.blend'%str(BASE.relative_to(ROOT)),'.runtime/assets/series01-dressing-source/scarf-original.glb','.runtime/art-direction/series01-pashtun-baseline-v01/frontal-v02-individualized.png','.runtime/art-direction/series01-pashtun-baseline-v01/portrait-v07-individualized.png'}


def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(8*1024*1024),b''):h.update(block)
    return h.hexdigest()


def write(name,value):
    (OUT/name).write_text(json.dumps(value,indent=2)+'\n')


def bind():
    OUT.mkdir(exist_ok=True)
    path=OUT/'source-binding.json'
    if path.exists() or (BASE/'wardrobe173-seal01').exists():raise ValueError('Binding must precede selected dispatch; never replace it')
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    tree=subprocess.check_output(['git','rev-parse','HEAD^{tree}'],cwd=ROOT,text=True).strip()
    paths=sorted((ROOT/'src/movie_factory/adapters/blender').glob('*.py'))+[Path(__file__).resolve()]
    sources=[]
    for source in paths:
        relative=str(source.relative_to(ROOT))
        blob=subprocess.check_output(['git','show',commit+':'+relative],cwd=ROOT)
        if hashlib.sha256(blob).hexdigest()!=sha(source):raise ValueError('Freeze all selected source before binding: '+relative)
        sources.append({'path':relative,'sha256':sha(source)})
    inputs=[BASE/'wardrobe172-seal01/dressed-fit.blend',ROOT/'.runtime/assets/series01-dressing-source/scarf-original.glb']
    inputs += [ROOT/'.runtime/art-direction/series01-pashtun-baseline-v01'/name for name in ('frontal-v02-individualized.png','portrait-v07-individualized.png')]
    value={'recorded_utc':datetime.now(timezone.utc).isoformat(),'source_commit':commit,'source_git_tree':tree,'source_files':sources,'source_manifest_sha256':hashlib.sha256(json.dumps(sources,sort_keys=True,separators=(',',':')).encode()).hexdigest(),'inputs':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in inputs],'provenance':'Frozen before selected dispatch; earlier iterative previews have no exact committed-source reconstruction claim','scope':'Fixed enum-only native static construction; scripts disabled; no paid calls','scarf_credit':'Balaclava - scarf as a hood - 3D scan by Tijerín Art Studio, https://skfb.ly/oP7Yu, CC BY4.0 https://creativecommons.org/licenses/by/4.0/; bounded fold-relief derivative; upstream body/horse/groom rights remain separate'}
    write('source-binding.json',value);print(json.dumps({'commit':commit,'source_files':len(sources),'tree':tree}))


def package():
    selected=BASE/'wardrobe173-seal01';fresh=BASE/'wardrobe173-verify01'
    review=json.loads((OUT/'visual-review.json').read_text());check_review(review,selected,'wardrobe173-seal01',CRITERIA)
    binding=json.loads((OUT/'source-binding.json').read_text())
    assert len(binding['inputs'])==len(INPUT_PATHS) and {row['path'] for row in binding['inputs']}==INPUT_PATHS
    expected={str(path.relative_to(ROOT)) for path in (ROOT/'src/movie_factory/adapters/blender').glob('*.py')}|{'scripts/package_wardrobe_studio.py'}
    assert len(binding['source_files'])==len(expected) and {row['path'] for row in binding['source_files']}==expected
    assert hashlib.sha256(json.dumps(binding['source_files'],sort_keys=True,separators=(',',':')).encode()).hexdigest()==binding['source_manifest_sha256']
    result=json.loads((selected/'result.json').read_text());verified=json.loads((fresh/'result.json').read_text())
    assert sha(OUT/'source-binding.json')==result['source_binding_sha256']
    for row in binding['source_files']+binding['inputs']:
        if (ROOT/row['path']).is_symlink() or sha(ROOT/row['path'])!=row['sha256']:raise ValueError('Bound source/input changed')
    assert sha(selected/'dressed-fit.blend')==result['native_sha256']
    assert all(verified[k] for k in ('reopened','protected_signatures_exact','body_basis_exact','static_tail_curve_data_exact','neutral_static_pattern_regenerated','source_unchanged'))
    assert not verified['unpacked_external_images']
    assert all(value is not None and value<verified['surface_tolerance'] for value in verified['surface_errors'].values())
    assert verified['visible_garment_revision_max_delta']>1e-5 and verified['revision_rollback_max_delta']<2e-5
    reopened={}
    for path in fresh.glob('reopened-*.png'):
        delta=ImageChops.difference(Image.open(path).convert('RGB'),Image.open(selected/path.name.removeprefix('reopened-')).convert('RGB'))
        maximum=max(v[1] for v in delta.getextrema());assert maximum<=4
        reopened[path.name]=maximum
    assert len(reopened)==2
    # Preview hashes are observations only; actual selected frames need their
    # own manual failure-seeking review even when these happen to match.
    preview={}
    for path in selected.glob('*.png'):
        before=BASE/'wardrobe173-preview49'/path.name
        if before.is_file():
            delta=ImageChops.difference(Image.open(path).convert('RGB'),Image.open(before).convert('RGB'))
            preview[path.name]=max(v[1] for v in delta.getextrema())
    data=[]
    frames=[(selected/(name+'.png'),short,'Static costume173 · '+short+' · Director appearance pending') for name,short in ROWS]
    refs=ROOT/'.runtime/art-direction/series01-pashtun-baseline-v01'
    frames += [(refs/'frontal-v02-individualized.png','Illustrated front','Approved illustrated identity and costume vocabulary; accepted native differences remain protected'),(refs/'portrait-v07-individualized.png','Illustrated portrait','Approved illustrated identity and scarf vocabulary, not literal fold replication')]
    template=GALLERY.read_text();assert '/* REVIEW_DATA */[]' in template
    for quality in (80,74,68,62):
        data=[]
        for path,short,label in frames:
            im=Image.open(path).convert('RGB');im.thumbnail((850,700));stream=BytesIO();im.save(stream,'JPEG',quality=quality,optimize=True)
            data.append({'short':short,'label':label,'image':'data:image/jpeg;base64,'+base64.b64encode(stream.getvalue()).decode()})
        html=template.replace('/* REVIEW_DATA */[]',json.dumps(data))
        if len(html.encode())<970_000:break
    assert len(html.encode())<1_000_000
    GALLERY.write_text(html)
    write('pixel-comparison.json',{'selected_vs_last_preview_max_channels':preview,'fresh_open_max_channel_differences':reopened,'selected_visual_review':'All selected images individually inspected; pixel agreement is not a visual gate'})
    print(json.dumps({'views':len(data),'gallery_bytes':len(html.encode()),'thumbnail_jpeg_quality':quality,'reopened':reopened}))


def receipt():
    con=sqlite3.connect(f'file:{ROOT/".runtime/experiment-ops.sqlite3"}?mode=ro',uri=True)
    events=[json.loads(payload) for (payload,) in con.execute('SELECT payload FROM events ORDER BY seq') if json.loads(payload)['event_id'].startswith('wardrobe173-')];con.close()
    starts={e['job_id']:e for e in events if e['event_type']=='job_started'};ends={e['job_id']:e for e in events if e['event_type']=='job_completed'}
    assert starts.keys()==ends.keys()
    start=next(e for e in events if e['event_id']=='wardrobe173-work-start');end=next(e for e in events if e['event_id']=='wardrobe173-work-end')
    seconds=(datetime.fromisoformat(end['utc'])-datetime.fromisoformat(start['utc'])).total_seconds()
    missing=[key for key,s in starts.items() if s.get('monotonic_seconds') is None or ends[key].get('monotonic_seconds') is None or s.get('clock_id')!=ends[key].get('clock_id')]
    retained=sum(p.stat().st_size for folder in BASE.glob('wardrobe173-*') if folder.is_dir() for p in folder.rglob('*') if p.is_file())
    manifest=[]
    for folder in ('wardrobe173-seal01','wardrobe173-verify01'):
        for path in sorted((BASE/folder).iterdir()):
            if path.is_file():manifest.append({'path':str(path.relative_to(ROOT)),'bytes':path.stat().st_size,'sha256':sha(path)})
    card={'scope':'Exchange173 sustained studio-quality static wardrobe appearance refinement','status':'SCOPED_STATIC_APPEARANCE_REVIEW_READY_DIRECTOR_PENDING','captured_utc_activity_seconds':seconds,'capture_limits':'Initial intake before work start and final receipt/design-commit overhead excluded; preview14 interrupted with stop verified but exact end monotonic time unavailable; historical clock/capture gaps remain','jobs_missing_exact_monotonic_duration':missing,'prior_partial_body_wardrobe_seconds':41832.657314,'cumulative_partial_captured_seconds':41832.657314+seconds,'lifetime_net_seconds':None,'engineering_tokens':None,'engineering_dollar_cost':None,'engineering_model':None,'reasoning_effort':None,'paid_provider_calls':0,'asset_purchases':0,'native_job_count':sum(s['job_kind']=='native' for s in starts.values()),'all_jobs_reconciled':True,'retained_directory_bytes_before_receipt':retained,'gallery_bytes':GALLERY.stat().st_size,'technical_selected_outputs':1,'director_accepted_outputs':0,'head_scale_changed':False,'limits':['Static construction settle and prescribed garment regeneration, not cloth/hair dynamics','Appearance review is not industry-wide studio certification, cultural proof, motion or release qualification','Actual riding/continuous contacts/final horse look remain moving-passage dependencies','Body/horse/groom upstream rights unresolved; local commits are not media backup']}
    write('CARD.json',card);write('scope-events.json',events);write('artifact-manifest.json',manifest);print(json.dumps(card))


if __name__=='__main__':
    import sys
    if sys.argv[1:]==['bind']:bind()
    elif sys.argv[1:]==['package']:package()
    elif sys.argv[1:]==['receipt']:receipt()
    else:raise ValueError('Only fixed binding, package or receipt operation')
