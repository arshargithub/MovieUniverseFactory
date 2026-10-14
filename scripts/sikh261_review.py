"""Record a failed native gate and an entitlement decision, never a visual pass."""
import json
from pathlib import Path
from movie_factory import production_knowledge as pk
from movie_factory.sikh257_contract import ROOT, digest

def main():
    output=ROOT/'results/sikh261'
    output.mkdir(exist_ok=False)
    source=ROOT/'.runtime/knowledge-pilot213/sikh257-hero-06.json'
    task=json.loads(source.read_text())['task']
    task['id']='sikh261-method-decision'
    task['intent']='Failed native control audit and proposed paid FaceBuilder route; not a ready character or authorization to purchase.'
    task['open_decisions']=['Whether to purchase an eligible FaceBuilder license or continue the uncertain no-cost head-fitting route.']
    packet=pk.task_packet(ROOT,task)
    evidence_paths=[
        'docs/planning/SERIES_01_SIKH_EXECUTION_257.md',
        '.runtime/art-direction/series01-sikh257/hero-05/three-quarter.png',
        '.runtime/art-direction/series01-sikh257/sikh-uncovered-concept-v03.png',
        '.runtime/art-direction/series01-sikh257/facebuilder_status-01/license-status.json',
    ]
    evidence=[{'path':p,'sha256':digest(ROOT/p)} for p in evidence_paths]
    passes={
        'authority':'Only source acquisition and read-only entitlement check; subscription remains proposed, not authorized.',
        'strategy':'Reassessed after failed controls; recommend prior demonstrated head-fitting workflow, not more local offsets.',
        'versioning':'Accepted files preserved, new controls in separate folders; earlier cloth cache is not qualified for new face.',
        'sikh_scope':'Sikh only; no Gurkha, music, publication or Pashtun modification.',
        'current_state':'Director260 portrait remains authority; no native approval inferred.',
    }
    failures={'visual_gate','representation','anatomy','look','au_reference','au_surface','stopping'}
    checks=[]
    for r in packet['obligations']:
        status='PASS' if r['id'] in passes else 'FAIL' if r['id'] in failures else 'NOT_RUN'
        checks.append({'id':r['id'],'kind':r['check_kind'],'status':status,
            'action_taken':'Review preserved controls against approved v03 and record scope-specific limitations in execution record.',
            'observation':passes.get(r['id'],
                'Native face is generic and beard visibly artificial; integrated identity/cloth/contact/motion/sequence quality is not established. No scope-wide pass claimed.'),
            'evidence':evidence})
    review={'packet_digest':packet['packet_digest'],'checks':checks,
        'hypotheses':[{'prediction':'Restoring donor sculpt alone would deliver suitable character identity.',
            'observation':'Multires detail restored in04/05, but direct comparison still shows generic face and artificial beard.',
            'response':'Reject native controls; change fitting method. Beard and one-cloth motion remain independent unsolved interfaces.',
            'result':'unresolved'}],
        'adjacent_regressions':'Crown donor improves shape but does not establish continuous material route; no new cloth cache or motion validated.',
        'stopping_reason':'Director-owned spending choice for recommended FaceBuilder route; no deliverable completion or quality waiver.'}
    gate=pk.check_review(ROOT,packet,review)
    assert not gate['ready_for_review']
    for name,value in [('packet',packet),('review',review),('gate',gate)]:
        (output/(name+'.json')).write_text(json.dumps(value,indent=2)+'\n')
    (output/'packet.md').write_text(pk.packet_markdown(packet))
    (output/'license-status.json').write_bytes((ROOT/evidence_paths[-1]).read_bytes())
    print('BLOCK: native deliverable not ready; material subscription decision required for recommended route.')
    return 2

if __name__=='__main__':raise SystemExit(main())
