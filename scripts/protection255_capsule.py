"""Bind the accepted unit to known editable inputs and cached native dependencies."""
import json
from pathlib import Path
from movie_factory.production_knowledge import file_hash

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/backup/protect255'
UNIT=ROOT/'.runtime/art-direction/series01-finish248'

def main():
    files={};bindings=[]
    def add(p,expected=None):
        p=p.resolve()
        if not p.is_relative_to(ROOT):raise ValueError('Dependency outside project')
        rel=p.relative_to(ROOT).as_posix();sha=file_hash(p)
        if expected and sha!=expected:raise ValueError('Changed dependency: '+rel)
        files[rel]={'path':rel,'sha256':sha,'bytes':p.stat().st_size}
        return rel
    for name in ('opening08','route09'):
        folder=UNIT/name;record=json.loads((folder/'result.json').read_text())
        add(folder/'scene.blend',record['native_sha256']);add(folder/'result.json')
        add(folder/'contact.npz',record['contact_sha256'])
        for c in record['caches']:
            rel=add(folder/c['path'],c['sha256'])
            bindings.append({'native':name,'object':c['object'],'relative_path':c['path'],'project_path':rel,'sha256':c['sha256']})
    for d in ('audio02','delivery01'):
        for p in (UNIT/d).iterdir():
            if p.is_file():add(p)
    for p in ('scripts/finish248_fist.py','scripts/finish248_render.py','scripts/finish248_run.py',
              'scripts/finish248_delivery.py','docs/knowledge/CURRENT_PRODUCTION_STATE.md',
              'docs/planning/SERIES_01_FINISH245_246_REVIEW.md',
              'docs/planning/SERIES_01_PASHTUN_FINISHED_UNIT_PLAN.md',
              'docs/planning/SERIES_01_PASHTUN_NARRATIVE_AUDIO_PROPOSAL.md',
              'docs/planning/SERIES_01_PASHTUN_BASELINE_V01.md'):
        add(ROOT/p)
    report={'kind':'accepted-unit-recovery-capsule','acceptance':'Director253 provisional only; full trailer release approval separate',
       'clean_sha256':'1004ed9f2e06d2eafb008c925eb9d266e8a13b8603086020e28d19e3b606722b',
       'files':sorted(files.values(),key=lambda x:x['path']),'native_cache_bindings':bindings,
       'editable_source_scope':'Known final native/cache inputs, clean/captioned deliveries, captions, audio join/review mix and current handlers. Full snapshot retains earlier music stems/recipe dependencies.',
       'rights':'Existing provenance in bound source documents; final release clearance remains OPEN, not independently completed by this recovery task.',
       'reuse_envelope':'Exact accepted sequence may be reused. New camera/action/character requires affected tests; native static appearance approval does not certify arbitrary performance. Strict pixel replay FAIL retained.',
       'restoration_status':'NOT_RUN_REMOTE; local hash validation only. Blender dependency inspection required in isolated restored root.',
       'count':len(files),'bytes':sum(x['bytes'] for x in files.values())}
    (OUT/'accepted-capsule.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'files':len(files),'cache_bindings':len(bindings),'bytes':report['bytes']}))

if __name__=='__main__':main()
