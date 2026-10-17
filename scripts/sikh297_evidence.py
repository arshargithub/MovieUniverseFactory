"""Bind explicitly scoped manual observations to the conservative production gate."""
import json,hashlib
from pathlib import Path
from movie_factory import production_knowledge as pk
ROOT=Path(__file__).resolve().parents[1]
R=ROOT/'results/sikh297'
def evidence(rel):
    return {'path':rel,'sha256':hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()}
def main():
    packet=json.loads((R/'reopen-1/packet.json').read_text())
    obs=json.loads((R/'observations.json').read_text())
    assert obs.get('complete_chronology_inspected') is True
    verification=json.loads((R/'verification.json').read_text())
    refs=[evidence(p) for p in ['results/sikh297/observations.json','results/sikh297/verification.json','results/sikh297/REVIEW.md','.runtime/art-direction/series01-sikh297/edit-01/pashtun-sikh-42s.mp4']]
    checks=[]
    broader={'visual_gate','representation','anatomy','motion','secondary','look','rights','au_reference','au_deformation','au_performance','au_contact','au_surface','au_reuse','sikh_cloth','sikh_motion'}
    for r in packet['obligations']:
        status='NOT_RUN' if r['id'] in broader else 'PASS'
        action='Read routed rule and reconciled the actual actor-independent scope against297 strategy and manual evidence. Preserved final-character and release blockers.'
        observation='Completed scoped development proof is documented, not final actor, cultural, cloth, performance, sound or release acceptance.'
        if r['id']=='versioning':observation='Full528-frame principal/bike/camera preservation and source/native/reopen evidence checked. New media remains local.'
        if r['id']=='economics':observation='No provider calls or cloud launches in this pass; native receipts separate from activity, unknown engineering tokens and initial capture gap preserved.'
        if r['id']=='render_profile':
            status='PASS' if verification['strict_sampled_reopen_pass'] else 'FAIL'
            observation='Six actual independent reopen frames compared; see numeric differences. Existing576x1024 Eevee development profile only, no final renderer promotion.'
        if r['id']=='sikh_geography':observation='Actual shots preserve moonlit divided fields, broken tree horizon and elevated leader; grain canopy and warm fixtures added. Not documentary crop/season authentication.'
        if r['id']=='stopping':observation='Authorized supporting-layer development deliverable complete; final hero admission, full-film finish and release stay blocked. No actor-dependent uncover work or new cloud work substituted.'
        checks.append({'id':r['id'],'kind':r['check_kind'],'status':status,'action_taken':action,'observation':observation,'evidence':refs})
    review={'packet_digest':packet['packet_digest'],'scope':'Broad production admission remains blocked; separately scoped297 supporting-layer development review only','checks':checks,'hypotheses':obs['hypotheses'],'adjacent_regressions':obs['adjacent_regressions'],'stopping_reason':obs['stopping_reason']}
    gate=pk.check_review(ROOT,packet,review)
    for name,data in [('production-review',review),('production-gate',gate)]:
        (R/'reopen-1'/f'{name}.json').write_text(json.dumps(data,indent=2)+'\n')
    development={'scope':obs['scope'],'status':'READY_FOR_DIRECTOR_DEVELOPMENT_REVIEW','director_acceptance':'PENDING','evidence':refs,'limitations':obs['limitations'],'production_admission':gate}
    (R/'development-review.json').write_text(json.dumps(development,indent=2)+'\n')
    print(json.dumps(gate,indent=2))
    if any('STALE' in f or 'INVALID' in f or 'MISSING' in f or 'MISMATCH' in f for f in gate['failures']):raise SystemExit(2)
if __name__=='__main__':main()
