"""Evidence binding for the explicit Director313 manual AV queue, never a pass."""
import json,sys
from pathlib import Path
from movie_factory import production_knowledge as pk
from movie_factory.resource_manifest import validate
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results/sikh318';BASE=ROOT/'.runtime/art-direction/series01-sikh318'
def read(p):return json.loads(p.read_text())
def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':pk.file_hash(p)}
def main():
    v=int(sys.argv[1]);assert 1<=v<=4
    native=BASE/f'build-{v:02d}';media=BASE/f'delivery-{v:02d}';audio=BASE/f'audio-{v:02d}'
    notes=read(OUT/'FINAL_OBSERVATIONS.json');assert notes['version']==v
    assert notes['native_sha256']==pk.file_hash(native/'sequence.blend')
    assert not notes['direct_motion'] and not notes['direct_audio']
    assert not notes['known_frame_visible_blockers']
    verified=read(media/'verification.json');assert verified['native_sha']==notes['native_sha256']
    assert verified['pashtun_pcm_exact'] and not verified['pashtun_rerendered']
    assert len(verified['frames'])==696
    for f in verified['frames']:assert pk.file_hash(BASE/f'movie-{v:02d}/frames'/f['name'])==f['sha256']
    resources=OUT/f'resources-{v}';resources.mkdir(exist_ok=False);checks=[]
    for ident,events in [('horse-rear-coat',['whole-horse-motion.json','coat318.json','groom318.json','impact-events.json']),('drainage-detail',['ditch.json']),('motorcycle-response',['suspension.json']),('supporting-crowd',['crowd.json'])]:
        original=ROOT/f'results/sikh317/resources-8/{ident}.json';r=read(original)
        r['provenance'] += [bind(original),bind(OUT/'STRATEGY.md'),bind(OUT/'CARRY_FORWARD.md')]
        r['dependencies']=[bind(native/'sequence.blend'),bind(ROOT/'scripts/sikh318_native.py'),bind(ROOT/'src/movie_factory/sikh318_motion.py')]
        r['tested_conditions']={'runtime':'Blender5.2.1','sequence':f'Sikh318 candidate{v}','scope':'local_internal_review','representation':'inherited317 rig with318 scoped corrections'}
        r['evidence']=[bind(native/e) for e in events]+[bind(OUT/'FINAL_OBSERVATIONS.json'),bind(BASE/f'check-{v:02d}/interfaces.json')]
        r['failures'].append({'id':'D318-pending','status':'open','reason':'Director318 rejects317 rear/coat; new full-speed judgment pending; supporting cast remains unadmitted.'})
        (resources/(ident+'.json')).write_text(json.dumps(r,indent=2)+'\n')
        (resources/(ident+'-use.json')).write_text(json.dumps(r['tested_conditions'],indent=2)+'\n')
        verdict=validate(ROOT,r,r['tested_conditions']);assert not verdict['reuse_admissible']
        assert not any(x.startswith(('STALE:','MISSING_OR_UNSAFE:')) for x in verdict['blockers']);checks.append(verdict)
    (resources/'validation.json').write_text(json.dumps(checks,indent=2)+'\n')
    paths=[OUT/n for n in ('STRATEGY.md','FINAL_OBSERVATIONS.json','REVIEW_PROGRESS.md','CARRY_FORWARD.md','SUPPORTING_CAST_REVIEW.md',f'reopen-{v}/comparison.json')]
    paths += [native/'sequence.blend',media/'verification.json',audio/'manifest.json',BASE/f'check-{v:02d}/interfaces.json']
    paths += sorted((media/'chronology').glob('*.jpg'))+sorted((media/'encoded-controls').glob('*.png'))
    paths += [media/'join-boundary-01.png',media/'join-boundary-02.png']
    assert len(list((media/'encoded-controls').glob('*.png')))==26
    candidates={}
    for entry in verified['media']:
        p=ROOT/entry['path'];assert pk.file_hash(p)==entry['sha256'];candidates[p.stem]=bind(p)
    accepted=ROOT/'.runtime/art-direction/series01-finish248/delivery01/pashtun-20s.mp4'
    assert pk.file_hash(accepted)=='1004ed9f2e06d2eafb008c925eb9d266e8a13b8603086020e28d19e3b606722b'
    queue={'status':'AWAITING_DIRECTOR_AV','authority':'docs/knowledge/review_control/README.md#current-authority--exchange313',
        'candidate':candidates,'evidence':[bind(p) for p in paths],'protected_pashtun':bind(accepted),
        'direct_motion':False,'direct_audio':False,'production_pass':False,'director_pass':False,
        'open_defects_preserved':notes['open_defects'],'resource_checks':checks,'observations':notes['requirements'],
        'strict_replay':read(OUT/f'reopen-{v}/comparison.json')['status'],
        'next_work_package':{'outcome':'Believable leader and crowd in the same film as the accepted Pashtun.',
            'delivery':'Complete supporting-cast-updated Sikh sequence and protected Pashtun join.',
            'included':'One close-shot leader, one near crowd proof, then bounded variants and performance integration.',
            'excluded':'Final Sikh principal, Gurkha, new spend/providers and release admission.',
            'exit':'Matched form/material and motion/interface review; Director AV judgment pending where required.',
            'recommended_next_action':'Review318 whole sequence, then authorize the scoped supporting-cast integration described in SUPPORTING_CAST_REVIEW.md.'}}
    dest=OUT/'DIRECTOR_AV_QUEUE.json';assert not dest.exists();dest.write_text(json.dumps(queue,indent=2)+'\n')
    task=read(OUT/f'movie-{v}/task.json');task.update(id=f'sikh318-delivery-{v}',operation='audio',query='Integrated corrected rear dark horse ditch and supporting cast fidelity review')
    task['entities']=sorted(set(task['entities']+['music_reference']));task['preserve_accepted_artifact']=pk.file_hash(accepted)
    task['inputs'].update({str(p.relative_to(ROOT)):pk.file_hash(p) for p in paths+[accepted,ROOT/'docs/knowledge/CURRENT_PRODUCTION_STATE.md']})
    packet=pk.task_packet(ROOT,task);assert packet['dispatch_ready'],packet['blockers']
    (OUT/'delivery-task.json').write_text(json.dumps(task,indent=2)+'\n');(OUT/'delivery-packet.json').write_text(json.dumps(packet,indent=2)+'\n');(OUT/'delivery-packet.md').write_text(pk.packet_markdown(packet))
    print(dest)
if __name__=='__main__':main()
