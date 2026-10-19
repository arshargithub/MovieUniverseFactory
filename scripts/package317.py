"""Bind a completed manual313 review package, not a production admission."""
import json,sys
from pathlib import Path
from movie_factory import production_knowledge as pk
from movie_factory.resource_manifest import validate

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/sikh317'
BASE=ROOT/'.runtime/art-direction/series01-sikh317'
VERSION=8
SUFFIX=f'{VERSION:02d}'
ACCEPTED='.runtime/art-direction/series01-finish248/delivery01/pashtun-20s.mp4'
ACCEPTED_SHA='1004ed9f2e06d2eafb008c925eb9d266e8a13b8603086020e28d19e3b606722b'
def read(p):return json.loads(p.read_text())
def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':pk.file_hash(p)}
def prepare():
    task=read(OUT/f'movie-{VERSION}/task.json')
    task.update(id=f'sikh317-integrated-delivery-{VERSION}',operation='audio',
        query='Complete scene, synchronized existing sound, protected music, tested interfaces and scoped reuse')
    task['entities']=sorted(set(task['entities']+['music_reference']))
    assert pk.file_hash(ROOT/ACCEPTED)==ACCEPTED_SHA
    task['preserve_accepted_artifact']=ACCEPTED_SHA
    paths=[ROOT/pk.CATALOG,ROOT/pk.PINS,Path(__file__),OUT/'STRATEGY.md',
        BASE/f'build-{SUFFIX}/sequence.blend',BASE/f'delivery-{SUFFIX}/verification.json',
        BASE/f'audio-{SUFFIX}/manifest.json',OUT/'FINAL_OBSERVATIONS.json',
        OUT/f'reopen-{VERSION}/comparison.json',OUT/f'movie-{VERSION}/receipt.json',
        ROOT/ACCEPTED,ROOT/'docs/knowledge/CURRENT_PRODUCTION_STATE.md']
    task['inputs'].update({str(p.relative_to(ROOT)):pk.file_hash(p) for p in paths})
    packet=pk.task_packet(ROOT,task)
    if not packet['dispatch_ready']:raise ValueError(packet['blockers'])
    dest=OUT/f'delivery-{VERSION}';dest.mkdir(exist_ok=False)
    for name,data in (('task',task),('packet',packet)):(dest/(name+'.json')).write_text(json.dumps(data,indent=2)+'\n')
    (dest/'packet.md').write_text(pk.packet_markdown(packet))
    print(dest/'packet.md')
def main():
    # This file is a manually authored, evidence-specific observation record.
    # Merely running this packager cannot populate it or declare a visual pass.
    notes=read(OUT/'FINAL_OBSERVATIONS.json')
    v=notes['version'];assert v==VERSION
    native=BASE/f'build-{SUFFIX}/sequence.blend';delivery=BASE/f'delivery-{SUFFIX}'
    assert notes['native_sha256']==pk.file_hash(native)
    assert notes['known_frame_visible_blockers']==[]
    assert notes['review_modalities']==['source','still_images','timed_frames','numerical']
    assert notes['direct_motion'] is False and notes['direct_audio'] is False
    verification=read(delivery/'verification.json')
    assert verification['native_sha']==pk.file_hash(native)
    assert verification['pashtun_pcm_exact'] and not verification['pashtun_rerendered']
    assert len(verification['frames'])==696
    for f in verification['frames']:
        assert f['sha256']==pk.file_hash(BASE/f'movie-{SUFFIX}/frames'/f['name'])
    replay=read(OUT/f'reopen-{VERSION}/comparison.json')
    assert len(replay['controls'])==16
    evidence={}
    paths=[OUT/p for p in ('STRATEGY.md','FINAL_OBSERVATIONS.json','REVIEW_PROGRESS.md',
        'CARRY_FORWARD.md','knowledge/RECONCILIATION.md',f'reopen-{VERSION}/comparison.json')]
    paths += [native,delivery/'verification.json',BASE/f'check-{SUFFIX}/interfaces.json',
        delivery/'join-boundary-01.png',delivery/'join-boundary-02.png',
        BASE/f'check-{SUFFIX}/native-checks.json',BASE/f'audio-{SUFFIX}/manifest.json',
        BASE/f'build-{SUFFIX}/hoof-ownership.json',BASE/f'build-{SUFFIX}/coat-reuse.json',
        BASE/f'build-{SUFFIX}/crowd-seams.json',BASE/f'build-{SUFFIX}/leader-seams.json']
    for p in paths:evidence[str(p.relative_to(ROOT))]=bind(p)
    for folder,pattern in (('encoded-controls','*.png'),('chronology','*.jpg')):
        for p in sorted((delivery/folder).glob(pattern)):evidence[str(p.relative_to(ROOT))]=bind(p)
    assert len(list((delivery/'encoded-controls').glob('*.png')))==26
    resource_checks=[]
    for p in sorted((OUT/f'resources-{VERSION}').glob('*-use.json')):
        manifest=p.with_name(p.name.replace('-use.json','.json'))
        r=validate(ROOT,read(manifest),read(p));resource_checks.append(r)
        assert not any(x.startswith(('STALE:','MISSING_OR_UNSAFE:')) for x in r['blockers'])
        evidence[str(manifest.relative_to(ROOT))]=bind(manifest)
    assert len(resource_checks)==4
    media={}
    for m in verification['media']:
        p=ROOT/m['path'];assert m['sha256']==pk.file_hash(p);media[p.stem]=bind(p)
    queue={'schema':1,'status':'AWAITING_DIRECTOR_AV',
        'authority':'docs/knowledge/review_control/README.md#current-authority--exchange313',
        'candidate':media,'evidence':evidence,'observations':notes['requirements'],
        'direct_motion':False,'direct_audio':False,'production_pass':False,'director_pass':False,
        'open_defects_preserved':notes['open_defects'],
        'strict_replay_current_controls':replay['status'],'resource_checks':resource_checks,
        'limits':['Principal rider remains a labeled proxy; no final character admission.',
            'Source/frame checks are not full-speed motion or listening judgment.',
            'Historical strict replay failures remain recorded independently.',
            'Local files and commits do not imply remote backup or publication.'],
        'next_work_package':{
            'outcome':'Carry accepted supporting action into final Sikh principal integration.',
            'director_receives':'The complete29s Sikh sequence and49s joined edit for this scoped motion/surface verdict.',
            'included':'D316 motion, coat, ditch and supporting-cast response with exact tested interfaces.',
            'excluded':'New principal generation, Gurkha, providers, cloud spend and release approval.',
            'exit':'Record exact Director AV verdict; correct any rejection before principal integration.',
            'recommended_next_action':'Review this full integrated candidate, then bind its accepted scope as the integration base.'}}
    assert not (OUT/'DIRECTOR_AV_QUEUE.json').exists()
    (OUT/'DIRECTOR_AV_QUEUE.json').write_text(json.dumps(queue,indent=2)+'\n')
    packet=read(OUT/f'delivery-{VERSION}/packet.json')
    process={'authority','strategy','current_state','sikh_scope'}
    review={'packet_digest':packet['packet_digest'],'checks':[{
        'id':r['id'],'kind':r['check_kind'],'status':'PASS' if r['id'] in process else 'NOT_RUN',
        'observation':'Scoped method and evidence recorded; Director motion/listening verdict pending.',
        'action_taken':'Applied source-bound obligations with interface and timed-frame controls; no inferred AV pass.',
        'evidence':[bind(OUT/'STRATEGY.md'),bind(OUT/'DIRECTOR_AV_QUEUE.json')]} for r in packet['obligations']],
        'hypotheses':[{'prediction':'Correct poses and grounded contacts can still look unnatural at speed.',
            'observation':'Agent has no qualified direct motion/audio review route under313.',
            'response':'Queue exact complete sequence for Director AV judgment, not a technical milestone.',
            'result':'unresolved'}],
        'adjacent_regressions':'See exact-bound final observations and all-frame contact checks.',
        'stopping_reason':'Integrated manual313 Director review, not production qualification.'}
    (OUT/'knowledge-review.json').write_text(json.dumps(review,indent=2)+'\n')
    gate=pk.check_review(ROOT,packet,review);assert not gate['ready_for_review']
    (OUT/'knowledge-gate.json').write_text(json.dumps(gate,indent=2)+'\n')
    print(OUT/'DIRECTOR_AV_QUEUE.json')
if __name__=='__main__':
    if sys.argv[1:]==['--prepare']:prepare()
    elif not sys.argv[1:]:main()
    else:raise ValueError('Fixed prepare or package operation only')
