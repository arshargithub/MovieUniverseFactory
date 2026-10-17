"""Evidence-backed development review; keep broader production blockers visible."""
import hashlib,json
from pathlib import Path
from movie_factory import production_knowledge as pk
ROOT=Path(__file__).resolve().parents[1]
RESULT=ROOT/'results/sikh292'
BASE=ROOT/'.runtime/art-direction/series01-sikh292'
def ev(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def main():
    manual=json.loads((RESULT/'observations.json').read_text())
    verified=json.loads((RESULT/'verification.json').read_text())
    if any(r['status']!='PASS' for r in manual['requested_scope_checks']):raise ValueError('Requested development scope has unresolved checks')
    evidence=[ev(RESULT/n) for n in ('observations.json','verification.json','REVIEW.md')]
    evidence+=[ev(BASE/'edit-01/pashtun-sikh-42s.mp4')]
    scoped={'scope':'Director292 substantial development fidelity and joined music preview; not actor admission or final production',
        'status':'READY_FOR_DIRECTOR_DEVELOPMENT_REVIEW','director_acceptance':'PENDING','evidence':evidence,
        'checks':manual['requested_scope_checks'],'limitations':manual['limitations']}
    (RESULT/'development-review.json').write_text(json.dumps(scoped,indent=2)+'\n')
    process={'authority','strategy','versioning','economics','cache_safety','current_state','au_reference','sikh_scope','anticipation','au_staging'}
    for part in ('reopen-1','audio'):
        packet=json.loads((RESULT/part/'packet.json').read_text())
        checks=[{'id':o['id'],'kind':o['check_kind'],'status':'PASS' if o['id'] in process else 'NOT_RUN',
            'action_taken':'Applied292 scoped strategy, preserved accepted20s unit, inspected requested development changes, and retained unqualified production domains.',
            'observation':'Source/authority/beat review and bounded scope recorded; not artistic acceptance.' if o['id'] in process else 'Broader final character, cloth, full-look, temporal naturalness, direct listening or release qualification is not claimed by this development preview.',
            'evidence':evidence} for o in packet['obligations']]
        review={'packet_digest':packet['packet_digest'],'checks':checks,'scope':'Broader production admission, not requested or claimed',
            'hypotheses':manual['hypotheses'],'adjacent_regressions':manual['adjacent_regressions'],
            'stopping_reason':'Complete Director-authorized development preview; protected final actor/cloth/rights/listening gates remain separate and blocked, not waived.'}
        (RESULT/part/'production-review.json').write_text(json.dumps(review,indent=2)+'\n')
        gate=pk.check_review(ROOT,packet,review)
        (RESULT/part/'production-gate.json').write_text(json.dumps(gate,indent=2)+'\n')
        print(part,json.dumps(gate))
    # Explicitly retain the blocked broader gate, rather than converting it
    # into production approval because the scoped preview has been delivered.
    return 2
if __name__=='__main__':raise SystemExit(main())
