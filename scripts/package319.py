"""Bind319 evidence to the explicit313 manual AV queue, not production approval."""
import json
import sys
from pathlib import Path
from movie_factory import production_knowledge as pk
from movie_factory.resource_manifest import validate
from sikh319 import ROOT, BASE, source_for

OUT=ROOT/'results/sikh319'
def read(p):return json.loads(p.read_text())
def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':pk.file_hash(p)}

def main():
    v=int(sys.argv[1]);assert 1<=v<=32
    native=source_for('movie',v);media=BASE/f'delivery-{v:02d}'
    notes=read(OUT/'FINAL_OBSERVATIONS.json')
    assert notes['version']==v and notes['native_sha256']==pk.file_hash(native)
    assert not notes['direct_motion'] and not notes['direct_audio']
    assert not notes['known_frame_visible_blockers']
    verification=read(media/'verification.json')
    assert verification['native_sha']==notes['native_sha256']
    assert verification['pashtun_pcm_exact'] and not verification['pashtun_rerendered']
    assert len(verification['frames'])==696
    for f in verification['frames']:
        assert pk.file_hash(BASE/f'movie-{v:02d}/frames'/f['name'])==f['sha256']
    interfaces=BASE/f'verify-{v:02d}/interfaces.json'
    assert read(interfaces)['status']=='PASS'
    resources=OUT/f'resources-{v}';resources.mkdir(exist_ok=False)
    prior=ROOT/'results/sikh318/resources-4/supporting-crowd.json'
    resource=read(prior)
    resource.update(id='supporting-cast319',state='in_progress',reuse_mode='adapt')
    resource['source'].append(bind(source_for('build',v)))
    resource['provenance'] += [bind(prior),bind(OUT/'STRATEGY.md'),bind(OUT/'CARRY_FORWARD.md')]
    resource['dependencies']=[bind(native)]+[bind(ROOT/'scripts'/n) for n in (
        'sikh319_cast.py','sikh319_contacts.py','sikh319_finish.py','sikh319_refine.py','sikh319_native.py')]
    resource['tested_conditions']={
        'runtime':'Blender5.2.1','sequence':f'Sikh319 candidate{v}',
        'scope':'local_internal_review','representation':'shot-bound donor-derived supporting cast'}
    resource['evidence']=[bind(p) for p in (
        OUT/'FINAL_OBSERVATIONS.json',OUT/'REVIEW_PROGRESS.md',interfaces,
        native.parent/'cast.json',native.parent/'finish.json')]
    resource['failures'].append({
        'id':'D319-AV','status':'open',
        'reason':'Full-speed performance and ensemble acceptance await the Director. No general reusable-character qualification.'})
    for name,data in [('supporting-cast.json',resource),('requested-use.json',resource['tested_conditions'])]:
        (resources/name).write_text(json.dumps(data,indent=2)+'\n')
    verdict=validate(ROOT,resource,resource['tested_conditions'])
    assert not verdict['reuse_admissible']
    assert not any(b.startswith(('STALE:','MISSING_OR_UNSAFE:')) for b in verdict['blockers'])
    (resources/'validation.json').write_text(json.dumps(verdict,indent=2)+'\n')
    evidence=[OUT/n for n in ('STRATEGY.md','FINAL_OBSERVATIONS.json','REVIEW_PROGRESS.md','CARRY_FORWARD.md')]
    evidence += [native,interfaces,media/'verification.json',OUT/f'reopen-{v}/comparison.json',
                 OUT/f'render-benchmark-{v}.json',resources/'validation.json']
    evidence += sorted((media/'chronology').glob('*.jpg'))+sorted((media/'encoded-controls').glob('*.png'))
    evidence += [media/'join-exact-0479.png',media/'join-exact-0480.png']
    assert len(list((media/'encoded-controls').glob('*.png')))==26
    candidates={}
    for item in verification['media']:
        p=ROOT/item['path'];assert pk.file_hash(p)==item['sha256']
        candidates[p.stem]=bind(p)
    accepted=ROOT/'.runtime/art-direction/series01-finish248/delivery01/pashtun-20s.mp4'
    assert pk.file_hash(accepted)=='1004ed9f2e06d2eafb008c925eb9d266e8a13b8603086020e28d19e3b606722b'
    queue={
        'status':'AWAITING_DIRECTOR_AV',
        'authority':'docs/knowledge/review_control/README.md#current-authority--exchange313',
        'candidate':candidates,'protected_pashtun':bind(accepted),
        'evidence':[bind(p) for p in evidence],
        'direct_motion':False,'direct_audio':False,'production_pass':False,'director_pass':False,
        'observations':notes['requirements'],'open_defects_preserved':notes['open_defects'],
        'strict_replay':read(OUT/f'reopen-{v}/comparison.json')['status'],
        'resource_checks':[verdict],
        'next_work_package':notes['next_work_package']}
    dest=OUT/'DIRECTOR_AV_QUEUE.json';assert not dest.exists()
    dest.write_text(json.dumps(queue,indent=2)+'\n')
    print(dest)
if __name__=='__main__':main()
