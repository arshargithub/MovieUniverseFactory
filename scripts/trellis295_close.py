"""Bind measured synthetic success separately from blocked actor admission."""
import json
from pathlib import Path
import trellis295_cloud as m
from movie_factory import production_knowledge as pk

def main():
    m.configure('a');c=m.c;root=c.ROOT;out=root/'results/trellis295'
    teardown=json.loads((c.OUT/'teardown-verification.json').read_text())
    assert not any(teardown['remaining'].values())
    receipt=json.loads((c.OUT/'gpu-receipt.json').read_text())
    assert receipt['device']=='NVIDIA L4' and set(receipt['outputs'])=={'cube.glb','uv-control.glb'}
    assert (c.OUT/'exit-code.txt').read_text().strip()=='0'
    verification=json.loads((c.OUT/'blender-verification.json').read_text())
    assert len(verification['jobs'])==4 and all(x['returncode']==0 for x in verification['jobs'])
    packet=m.packet()
    paths=[out/'STRATEGY.md',out/'README.md',out/'INPUT_PREPARATION.md',out/'tests.xml',
        c.OUT/'gpu-receipt.json',c.OUT/'blender-verification.json',c.OUT/'teardown-verification.json',
        c.OUT/'runtime-link.json',c.OUT/'worker-log.txt',c.OUT/'payload-manifest.json']
    evidence=[{'path':str(p.relative_to(root)),'sha256':c.sha(p)} for p in paths]
    processes={'authority','strategy','stopping','versioning','economics','current_state','sikh_scope'}
    checks=[]
    for rule in packet['obligations']:
        passed=rule['id'] in processes
        checks.append({'id':rule['id'],'kind':rule['check_kind'],'status':'PASS' if passed else 'NOT_RUN',
            'action_taken':'Bound Director295 authority, conservative aggregate admission, exact payload, GPU and independent Blender evidence; preserved protected assets and kept actor scope blocked at official access prerequisite.',
            'observation':('Scoped process completed with explicit limits; synthetic technical success is recorded separately from outstanding actor.' if passed else 'Requested character design, same-film appearance, anatomy, cloth, performance and full-inference rights are NOT_RUN. Synthetic controls cannot stand in for those obligations.'),
            'evidence':evidence})
    review={'packet_digest':packet['packet_digest'],'checks':checks,'hypotheses':[
        {'prediction':'Explicit parent-package linkage should fix the child runtime failure.','observation':'Live child imports Torch and queries L4 before installation; both extensions compile and probe exits0.','response':'Retain reproduction test and runtime receipt; distinguish from inference.','result':'resolved'},
        {'prediction':'UV axes or material packing may fail across export and Blender.','observation':'Two GLBs pass bounds/material checks; four independent Blender jobs pass and sampled quadrant colours match exactly; visual quadrant check agrees.','response':'Retain hash-bound scoped proof, no claim about high-resolution character seams.','result':'resolved'},
        {'prediction':'Official model access may block the requested candidate even after export succeeds.','observation':'Gated DINOv3 access/terms not confirmed; no inference or protagonist upload.','response':'Keep candidate BLOCKED, request Director account action, tear down rather than idle.','result':'unresolved'}],
        'adjacent_regressions':'Original Sikh260 portrait, rejected native history, accepted292 staging and Pashtun masters are unchanged. No public upload or extra10USD activation. Raw prior ledgers retained; no fabricated bill.',
        'stopping_reason':'Synthetic GPU/integration test complete and temporary resources independently absent. Candidate scope is not complete: official encoder account access requires Director action. Return a blocker outcome, not a ready-for-review actor.'}
    c.dump(out/'review.json',review);c.dump(out/'gate.json',pk.check_review(root,packet,review))
    c.dump(out/'outcome.json',{'synthetic_gpu_export':'PASS','independent_blender':'PASS',
        'candidate_generation':'NOT_RUN','production_candidate':'BLOCKED_OFFICIAL_DINOV3_ACCESS',
        'actual_billed_usd':None,'extra_contingency_activated_usd':0,'aggregate':m.aggregate(),
        'scope':'No inference, weights, actor quality or performance qualification','evidence':evidence})
    print(json.dumps(json.loads((out/'gate.json').read_text()),indent=2))
if __name__=='__main__':main()
