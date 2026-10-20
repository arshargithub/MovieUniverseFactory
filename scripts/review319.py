"""Package explicitly scoped manual findings, never synthesize an artistic pass."""
import json
from pathlib import Path
from movie_factory import production_knowledge as pk

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/sikh319'
def bind(p):
    return {'path':str(p.relative_to(ROOT)),'sha256':pk.file_hash(p)}

def main():
    packet=json.loads((OUT/'delivery-19/packet.json').read_text())
    evidence=[bind(OUT/n) for n in (
        'FINAL_OBSERVATIONS.json','DIRECTOR_AV_QUEUE.json','REVIEW_PROGRESS.md')]
    findings={
        'authority':('PASS','Local supporting-cast scope only; no new providers, spend, installations, cloud, uploads or publication. Principal remains proxy.'),
        'strategy':('PASS','Strategy and fresh packet applied; failed whole-form/contact variants retained. Early propagation to all variants violated intended proof order and is explicitly recorded as a lesson, not hidden.'),
        'current_state':('PASS','Accepted Pashtun source/PCM bound exactly; prior AV and strict replay failures retained. Director313 judgment authority preserved.'),
        'sikh_scope':('PASS','Nonrecurring supporting leader/crowd changed; main character, horse/action, geography, timing and selected music protected.'),
        'economics':('PASS','Lifecycle jobs/work recorded with initial capture gap disclosed; usage and attributable cost unknown. No fabricated efficiency percentage.'),
        'versioning':('PASS','Candidate19 native, recipes and delivered media hash-bound; earlier01–06 source snapshot gap retained. No overwrite of accepted masters.'),
        'cache_safety':('PASS','Protected sources and full frame inventory checked; exact Pashtun PCM/source unchanged and no Pashtun native rerender. Reuse beyond this timeline remains unqualified.'),
        'render_profile':('FAIL','Six fresh-open controls: three exceed unchanged1/255 strict threshold. Native opens and full media decode, but renderer qualification is not passed.'),
        'rights':('NOT_RUN','Existing recorded anatomical donor route used; unused conflicting-label beard donor excluded. Final release-wide rights clearance not performed here.'),
        'reuse_envelope':('NOT_RUN','Current sidecar binds source/dependencies/evidence and preserves open failures; general reuse remains blocked.'),
    }
    checks=[]
    for obligation in packet['obligations']:
        ident=obligation['id']
        status,observation=findings.get(ident,(
            'NOT_RUN',
            'Applicable source/strategy and scoped frame evidence reviewed; see named final observations. Complete audiovisual, ensemble and production acceptance remain pending under Director313; no agent listening/playback or inherited PASS.'))
        checks.append({
            'id':ident,'kind':obligation['check_kind'],'status':status,
            'observation':observation,
            'action_taken':'Preserved scoped evidence and unresolved findings; delivered complete manual AV candidate without claiming strict production admission.',
            'evidence':evidence})
    review={
        'packet_digest':packet['packet_digest'],'checks':checks,
        'hypotheses':[
            {'prediction':'Rapid spear plant may expose cuff sampling gaps invisible in sparse poses.',
             'observation':'Candidate15 full timeline found109.5mm separation; candidate19 maximum under0.01mm with contiguous visible cuff.',
             'response':'Dense samples through fastest interval; retained696-frame contact check and chronological images.',
             'result':'resolved'},
            {'prediction':'Donor adaptation and local beard repair may introduce adjacent whole-form regressions.',
             'observation':'Reversed crowd torso and kinked/thin beard alternatives rejected internally; final semantic orientation and coherent locks inspected.',
             'response':'Neutral/reverse-angle and actual-shot controls; preserve working whole forms during local correction.',
             'result':'resolved'}
        ],
        'adjacent_regressions':'All696 frames,26 decoded controls and exact boundary frames479/480 inspected.1476 protected objects and actor roots unchanged. No new observed scoped cast interface blocker; prior AV failures and principal proxy retained.',
        'stopping_reason':'Complete agreed manual Director313 AV candidate delivered, not strict production admission. No new implementation authority assumed for principal source qualification.'
    }
    (OUT/'knowledge-review.json').write_text(json.dumps(review,indent=2)+'\n')

if __name__=='__main__':
    main()
