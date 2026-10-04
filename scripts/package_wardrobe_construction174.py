"""Scoped174 source binding, reviewed-gallery packaging and partial effort card."""
import base64
from datetime import datetime, timezone
from io import BytesIO
import json
from pathlib import Path
import sqlite3
import subprocess

from PIL import Image, ImageChops
from package_wardrobe_studio import sha, check_review, ROWS

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'.runtime/art-direction/series01-facebuilder-trial-01'
OUT = BASE/'wardrobe174-operating'
GALLERY = Path('/Users/adisharma/.codex/visualizations/2026/09/09/01a0878c-e7a2-75e0-873c-c31d97f879a1/pashtun-continuous-shawl.html')
CRITERIA = {'protected_foundation','rear_coverage_and_tucked_ends','supported_two_pass_cloth',
            'close_upper_tunic_and_sleeves','harness_and_belt_layering',
            'neutral_full_partial_interfaces','adjacent_regressions','whole_static_appearance'}


def source_paths():
    return sorted((ROOT/'src/movie_factory/adapters/blender').glob('*.py'))+[
        ROOT/'scripts/wardrobe_construction174.py', Path(__file__).resolve(),
        ROOT/'scripts/wardrobe_construction174_verify.py',
        ROOT/'scripts/package_wardrobe_studio.py', ROOT/'scripts/package_wardrobe_fit_review.py',
        ROOT/'tests/unit/test_wardrobe_construction174.py',ROOT/'tests/unit/test_wardrobe_construction174_package.py']


def write(name, data):
    OUT.mkdir(exist_ok=True)
    (OUT/name).write_text(json.dumps(data,indent=2)+'\n')


def bind():
    if (OUT/'source-binding.json').exists() or (BASE/'wardrobe174-seal01').exists():
        raise ValueError('Bind once before selected dispatch; preserve prior evidence')
    commit = subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    tree = subprocess.check_output(['git','rev-parse','HEAD^{tree}'],cwd=ROOT,text=True).strip()
    rows = []
    import hashlib
    for path in source_paths():
        relative = str(path.relative_to(ROOT))
        blob = subprocess.check_output(['git','show',commit+':'+relative],cwd=ROOT)
        if path.is_symlink() or hashlib.sha256(blob).hexdigest()!=sha(path):
            raise ValueError('Commit selected source before binding: '+relative)
        rows.append({'path':relative,'sha256':sha(path)})
    refs = ROOT/'.runtime/art-direction/series01-pashtun-baseline-v01'
    inputs = [BASE/'wardrobe173-seal01/dressed-fit.blend',
              ROOT/'.runtime/assets/series01-dressing-source/scarf-original.glb',
              refs/'frontal-v02-individualized.png',refs/'portrait-v07-individualized.png',
              BASE/'wardrobe174-preview09/neutral-before-cleanup.npz']
    write('source-binding.json',{'recorded_utc':datetime.now(timezone.utc).isoformat(),
        'source_commit':commit,'source_git_tree':tree,'source_files':rows,
        'inputs':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in inputs],
        'discovery_input_provenance':'neutral-before-cleanup.npz is retained frozen geometry from an uncommitted iterative preview09 physics discovery. This binding proves its exact bytes and selected static transformation, not the original executed discovery source or general cloth simulation reproducibility.',
        'scope':'Fixed structured174 static wardrobe; scripts disabled; earlier previews not committed-source claims',
        'rights':'CC BY4.0 Tijerín Art Studio scarf relief https://skfb.ly/oP7Yu; inherited body/horse/groom rights unresolved'})
    print(json.dumps({'source_commit':commit,'source_files':len(rows)}))


def package():
    selected = BASE/'wardrobe174-seal01'; fresh = BASE/'wardrobe174-verify01'
    review = json.loads((OUT/'visual-review.json').read_text())
    check_review(review,selected,'wardrobe174-seal01',CRITERIA)
    result = json.loads((selected/'result.json').read_text())
    verified = json.loads((fresh/'result.json').read_text())
    binding = json.loads((OUT/'source-binding.json').read_text())
    assert {r['path'] for r in binding['source_files']}=={str(p.relative_to(ROOT)) for p in source_paths()}
    for row in binding['source_files']+binding['inputs']:
        path = ROOT/row['path']; assert not path.is_symlink() and sha(path)==row['sha256']
    assert sha(OUT/'source-binding.json')==result['source_binding_sha256']
    assert sha(selected/'dressed-fit.blend')==result['native_sha256']
    assert all(verified[k] for k in ('reopened','protected_signatures_exact','body_basis_exact',
        'static_tail_curve_data_exact','neutral_static_pattern_regenerated','source_unchanged'))
    assert not verified['unpacked_external_images']
    assert all(v is not None and v<2e-5 for v in verified['surface_errors'].values())
    assert verified['visible_garment_revision_max_delta']>1e-5 and verified['revision_rollback_max_delta']<2e-5
    pixels = {}
    for path in fresh.glob('reopened-*.png'):
        delta = ImageChops.difference(Image.open(path).convert('RGB'),
                Image.open(selected/path.name.removeprefix('reopened-')).convert('RGB'))
        maximum = max(v[1] for v in delta.getextrema()); assert maximum<=4
        pixels[path.name] = maximum
    assert len(pixels)==2
    refs = ROOT/'.runtime/art-direction/series01-pashtun-baseline-v01'
    frames = [(selected/(name+'.png'),short,'Static continuous shawl174 · '+short+' · Director pending') for name,short in ROWS]
    frames += [(refs/'frontal-v02-individualized.png','Illustrated front','Approved art direction; not literal fold geometry'),
               (refs/'portrait-v07-individualized.png','Illustrated portrait','Approved art direction; accepted native identity remains protected')]
    template = GALLERY.read_text(); assert '/* REVIEW_DATA */[]' in template
    for quality in (80,74,68,62):
        rows = []
        for path,short,label in frames:
            im = Image.open(path).convert('RGB'); im.thumbnail((850,700))
            stream = BytesIO(); im.save(stream,'JPEG',quality=quality,optimize=True)
            rows.append({'short':short,'label':label,'image':'data:image/jpeg;base64,'+base64.b64encode(stream.getvalue()).decode()})
        text = template.replace('/* REVIEW_DATA */[]',json.dumps(rows))
        if len(text.encode())<970_000: break
    assert len(text.encode())<1_000_000
    GALLERY.write_text(text)
    write('pixel-comparison.json',{'fresh_open_max_channel_differences':pixels,'visual_gate':'Separate actual-image manual review'})
    print(json.dumps({'views':len(rows),'gallery_bytes':len(text.encode()),'fresh_open_pixels':pixels}))


def receipt():
    con = sqlite3.connect(f'file:{ROOT/".runtime/experiment-ops.sqlite3"}?mode=ro',uri=True)
    events = [json.loads(p) for (p,) in con.execute('SELECT payload FROM events ORDER BY seq')
              if json.loads(p)['event_id'].startswith('wardrobe174-')]
    con.close()
    starts = {e['job_id']:e for e in events if e['event_type']=='job_started'}
    ends = {e['job_id']:e for e in events if e['event_type']=='job_completed'}
    assert starts.keys()==ends.keys()
    start = next(e for e in events if e['event_id']=='wardrobe174-work-start')
    end = next(e for e in events if e['event_id']=='wardrobe174-work-end')
    seconds = (datetime.fromisoformat(end['utc'])-datetime.fromisoformat(start['utc'])).total_seconds()
    manifest = [{'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size}
                for folder in ('wardrobe174-seal01','wardrobe174-verify01')
                for p in sorted((BASE/folder).iterdir()) if p.is_file()]
    retained = sum(p.stat().st_size for folder in BASE.glob('wardrobe174-*') if folder.is_dir()
                   for p in folder.rglob('*') if p.is_file())
    write('artifact-manifest.json',manifest); write('scope-events.json',events)
    card = {'status':'SCOPED_STATIC_APPEARANCE_REVIEW_READY_DIRECTOR_PENDING',
        'captured_utc_activity_seconds':seconds,'prior_partial_body_wardrobe_seconds':58256.701601,
        'cumulative_partial_captured_seconds':58256.701601+seconds,'lifetime_net_seconds':None,
        'capture_limits':'Initial context recovery and final receipt/design-commit overhead excluded; historical gaps remain',
        'engineering_model':None,'reasoning_effort':None,'engineering_tokens':None,'engineering_dollar_cost':None,
        'paid_provider_calls':0,'asset_purchases':0,'all_jobs_reconciled':True,
        'native_job_count':sum(e['job_kind']=='native' for e in starts.values()),
        'failed_job_count':sum(e.get('returncode') not in (0,None) for e in ends.values()),
        'retained_directory_bytes_before_receipt':retained,'gallery_bytes':GALLERY.stat().st_size,
        'technical_selected_outputs':1,'director_accepted_outputs':0,
        'limits':['Frozen neutral construction and prescribed pose transport, not riding cloth dynamics',
                  'Appearance pending; not cultural, upstream rights, industry certification or release qualification',
                  'Local text commits are not off-device media backup']}
    write('CARD.json',card); print(json.dumps(card))


if __name__=='__main__':
    import sys
    actions = {'bind':bind,'package':package,'receipt':receipt}
    if len(sys.argv)!=2 or sys.argv[1] not in actions: raise ValueError('Fixed packaging operation only')
    actions[sys.argv[1]]()
