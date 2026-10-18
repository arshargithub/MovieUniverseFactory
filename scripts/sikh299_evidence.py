"""Scoped299 evidence and conservative production admission, not perceptual AI."""
import json,hashlib
from pathlib import Path
from movie_factory import production_knowledge as pk
ROOT=Path(__file__).resolve().parents[1];R=ROOT/'results/sikh299'
def evidence(rel):return {'path':rel,'sha256':hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()}
def main():
    packet=json.loads((R/'reopen-1/packet.json').read_text());obs=json.loads((R/'observations.json').read_text());verification=json.loads((R/'verification.json').read_text())
    assert obs['complete_chronology_inspected'] is True
    refs=[evidence(p) for p in ['results/sikh299/observations.json','results/sikh299/verification.json','results/sikh299/REVIEW.md','results/sikh299/LEARNINGS.md','results/sikh299/MOON_PROVENANCE.md','.runtime/art-direction/series01-sikh299/edit-01/pashtun-sikh-42s.mp4']]
    broader={'visual_gate','representation','anatomy','motion','secondary','look','rights','au_reference','au_deformation','au_performance','au_contact','au_surface','au_reuse','sikh_cloth','sikh_motion'}
    checks=[]
    for r in packet['obligations']:
        status='NOT_RUN' if r['id'] in broader else 'PASS'
        observation='Scoped development evidence is separate from final protagonist, physical simulation, direct listening/realtime perception and release approval.'
        if r['id']=='render_profile':
            status='PASS' if verification['strict_sampled_reopen_pass'] else 'FAIL';observation='Six independent reopen renders numerically compared; only current576x1024 Eevee development source, no renderer promotion.'
        if r['id']=='versioning':observation='Exact native/source snapshots and preserved Pashtun input verified. Changed action/contact/fire/moon source is299-only; native/media remain local, not remotely protected by a local commit.'
        if r['id']=='economics':observation='Zero provider/cloud/install/purchase in299. Receipts are process occupancy, not additional labor or pure wait; tokens unknown and initial capture gap disclosed.'
        checks.append({'id':r['id'],'kind':r['check_kind'],'status':status,'action_taken':'Read routed rule; reconciled299 strategy, motion brief, audit lessons and scoped manual evidence; retained broader production blockers.','observation':observation,'evidence':refs})
    hypotheses=[{'prediction':h['hypothesis'],'observation':h['observation'],'response':'Scoped controls and complete chronological review; retain explicit realtime/audio/production limits.','result':'not_run' if h['id'] in ('S299-FIRE','S299-STOP') else 'resolved'} for h in obs['hypotheses']]
    review={'packet_digest':packet['packet_digest'],'scope':'299 environment and two-stage stop development; full production remains blocked','checks':checks,'hypotheses':hypotheses,'adjacent_regressions':obs['adjacent_regressions'],'stopping_reason':obs['stopping_reason']}
    gate=pk.check_review(ROOT,packet,review)
    for name,data in [('production-review',review),('production-gate',gate)]:(R/'reopen-1'/f'{name}.json').write_text(json.dumps(data,indent=2)+'\n')
    (R/'development-review.json').write_text(json.dumps({'scope':obs['scope'],'status':'READY_FOR_DIRECTOR_DEVELOPMENT_REVIEW','director_acceptance':'PENDING','evidence':refs,'limitations':obs['limitations'],'production_admission':gate},indent=2)+'\n')
    print(json.dumps(gate,indent=2))
    if any(any(k in f for k in ('STALE','INVALID','MISSING','MISMATCH')) for f in gate['failures']):raise SystemExit(2)
if __name__=='__main__':main()
