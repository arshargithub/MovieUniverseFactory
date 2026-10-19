"""Generate an exact-bound manual313 queue; never a production admission."""
import json,sys
from pathlib import Path
from movie_factory import production_knowledge as pk
from movie_factory import review_control as rc
from sikh315_run import ROOT,BASE,sha,source_for

def main():
    v=int(sys.argv[1]);assert 1<=v<=16
    out=ROOT/'results/sikh315';delivery=BASE/f'delivery-{v:02d}'
    verification=json.loads((delivery/'verification.json').read_text())
    replay=json.loads((out/f'reopen-{v}/comparison.json').read_text())
    nativecheck=BASE/f'reopen-{v:02d}/native-checks.json'
    assert nativecheck.exists() and verification['pashtun_pcm_exact']
    def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':sha(p)}
    media={Path(m['path']).stem:bind(ROOT/m['path']) for m in verification['media']}
    evidence={
        'strategy':bind(out/'STRATEGY.md'),
        'observations':bind(out/'REVIEW_PROGRESS.md'),
        'learning':bind(out/'CARRY_FORWARD.md'),
        'native':bind(source_for('movie',v)),
        'native_checks':bind(nativecheck),
        'reopen_comparison':bind(out/f'reopen-{v}/comparison.json'),
        'decoded_media_checks':bind(delivery/'verification.json'),
        'audio':bind(BASE/f'audio-{v:02d}/manifest.json'),
        'render_profile':bind(out/'render-profile.json'),
        'reference':bind(ROOT/'.runtime/art-direction/series01-sikh256/references/reference-b.mov'),
        'protected_pashtun':bind(ROOT/'.runtime/art-direction/series01-finish248/delivery01/pashtun-20s.mp4'),
    }
    for p in sorted((delivery/'encoded-controls').glob('*.png')):evidence['encoded_'+p.stem]=bind(p)
    for p in sorted((delivery/'chronology').glob('*.jpg')):evidence['chronology_'+p.stem]=bind(p)
    assert len([k for k in evidence if k.startswith('encoded_')])==21
    contract,state,digest=rc.load(ROOT)
    observations={
        'policy':'Local reversible correction; no new cloud, paid calls, installations, uploads or principal admission. Manual313 queue only.',
        'references':'Whole reference interval plus side and chronological controls; accepted Pashtun protected. No automatic same-film or motion acceptance.',
        'camera':'Preserved first brake/rest geography; departure tracks beyond crowd before holding recession. All encoded control frames and chronology inspected.',
        'rear':'Head/poll preparation, staggered support, rise, active foreleg changes, descent/contact/recovery inspected as frames. Full-speed naturalness remains pending.',
        'terrain':'Actual crown, ruts, eroded bank and mound plus embedded aggregate; clay/shot controls inspected, support recalculated.',
        'field_boundaries':'Rooted verge/litter and drainage with cultivated parcels; not a geometry-free texture overlay. Director believability judgment remains pending.',
        'debris':'Solid tire debris persists at end; world-space wake has tested unparented births, drift and nonshrinking expansion. Full-speed optical effect pending.',
        'horse_surface':'Restored donor eye/mouth/teeth/hoof regions with exact polygon correspondence; coat pigmentation, groom and supporting cloth variation. Final actor-quality acceptance not claimed.',
        'departure':'Slow-travel wheelspin/side-slip, then recovery/straightening and forward acceleration share one clock; chronological and numeric checks. Dramatic playback judgment pending.',
        'wind':'Existing nonuniform field gusts retained; frame continuity checked. No new direct-motion qualification.',
        'sound':'Existing cleared sources retimed to impacts and launch, peak/decode checks and protected Pashtun PCM. Direct listening NOT_RUN.',
        'technical':'Current fixed-control reopen '+replay['status']+'; source/support/ownership checks separate from historical strict replay failure and artistic acceptance.',
        'protected':'Accepted Pashtun source hash unchanged, no Blender rerender; first20s source PCM exact before lossy delivery encoding. Existing first brake/rest choreography protected.',
    }
    queue={'schema':1,'status':'AWAITING_DIRECTOR_AV','authority':'docs/knowledge/review_control/README.md#current-authority--exchange313',
           'candidate':media,'evidence':evidence,'agent_scope':'Source, image, timed-frame and technical inspection only',
           'direct_motion':False,'direct_audio':False,'production_pass':False,'director_pass':False,
           'requirements':[{'id':r['id'],'agent_observation':observations[r['id']],
                            'human_status':'AWAITING_DIRECTOR_AV' if r['id'] not in ('policy','protected','technical') else 'NOT_AN_ARTISTIC_JUDGMENT'} for r in contract['requirements']],
           'open_defects_preserved':[d['id'] for d in state['defects']]+['D315-01','D315-02','D315-03','D315-04','D315-05'],
           'strict_replay_current_controls':replay['status'],
           'limits':['Historical305 strict replay FAIL is not erased.','Manual queue is not a successful strict deliver receipt.','Principal Sikh remains a labeled proxy.','Supporting cast finish does not admit final character assets.'],
           'next_work_package':{'outcome':'Resolve the Director verdict on this exact integrated scene, then carry accepted supporting action into principal Sikh integration.',
                                'excluded':'No speculative new principal model, paid generation, cloud or Gurkha work.',
                                'exit':'Exact shot-specific Director decisions captured; any rejected known-visible defect corrected before integration; approved Sikh identity and same-film checks retained.'}}
    (out/'DIRECTOR_AV_QUEUE.json').write_text(json.dumps(queue,indent=2))
    packet=json.loads((out/f'movie-{v}/packet.json').read_text())
    process_ids={'authority','strategy','handoff','current_scope','sikh_scope'}
    review={'packet_digest':packet['packet_digest'],'checks':[{'id':r['id'],'kind':r['check_kind'],
              'status':'PASS' if r['id'] in process_ids else 'NOT_RUN',
              'observation':'Applied as recorded in315 strategy, observations and exact manual queue; audiovisual acceptance remains pending.',
              'action_taken':'Preserved scope and references; performed source/frame/technical checks without substituting these for full-speed listening or motion judgment.',
              'evidence':[bind(out/'STRATEGY.md'),bind(out/'DIRECTOR_AV_QUEUE.json')]} for r in packet['obligations']],
              'hypotheses':[{'prediction':'An improved pose can still fail natural motion.','observation':'Continuous timing/listening not directly available to agent.','response':'Explicit313 Director AV queue; do not infer pass.','result':'unresolved'}],
              'adjacent_regressions':'Ground contacts, departure framing, world-space FX, protected Pashtun, first brake/rest and exact candidate checked; human AV pending.',
              'stopping_reason':'Planned integrated Director313 audiovisual review, not production acceptance.'}
    (out/'knowledge-review.json').write_text(json.dumps(review,indent=2))
    checked=pk.check_review(ROOT,packet,review)
    assert not checked['ready_for_review']
    (out/'knowledge-gate.json').write_text(json.dumps(checked,indent=2))
    print(out/'DIRECTOR_AV_QUEUE.json')

if __name__=='__main__':main()
