"""Bind manually reviewed export controls; no automatic artistic admission."""
import json
from pathlib import Path
import numpy as np
from PIL import Image
from movie_factory import production_knowledge as pk
from trellis301_prepare import ROOT, sha, dump
from trellis301_export_inspect import OUT, SOURCE, VARIANTS, VIEWS


def main():
    target=ROOT/'results/trellis301'
    packet=json.loads((OUT/'packet.json').read_text())
    files=[target/'EXPORT_REVIEW.md',ROOT/'scripts/trellis301_export_inspect.py',
           SOURCE/'comparison-receipt.json',target/'cloud-export/teardown-verification.json',
           ROOT/'.runtime/art-direction/series01-sikh257/sikh-uncovered-concept-v03.png',
           ROOT/'.runtime/art-direction/series01-finish248/opening-final/frame-0200.png']
    for variant in VARIANTS:
        for name in ('inspection.json','reopen.json'):
            files.append(OUT/variant/name)
        assert json.loads((OUT/variant/'reopen.json').read_text())['geometry_binding_exact']
    views=[v[0] for v in VIEWS]+['front-clay','left-quarter-clay','right-quarter-clay']
    files += [OUT/f'comparison-{v}.jpg' for v in views]
    metrics=[]
    for view in views:
        a,b=[np.asarray(Image.open(OUT/variant/f'{view}.png').convert('RGB'),dtype=np.int16) for variant in VARIANTS[1:]]
        delta=np.abs(a-b)
        metrics.append({'view':view,'atlas_pair_mean_rgb_delta':float(delta.mean()),
                        'fraction_pixels_gt10':float((delta.max(axis=2)>10).mean())})
    dump(target/'export-metrics.json',{'diagnostic_not_quality_score':True,'atlas_pair':metrics})
    files.append(target/'export-metrics.json')
    evidence=[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in files]
    fail={'visual_gate','representation','anatomy','look','au_surface'}
    unrun={'motion','secondary','au_deformation','au_performance','au_contact','sikh_cloth','sikh_motion'}
    notes={
        'authority':'Director301 controlled comparison and302 exact payload approval; original15USD preserved, no production acceptance.',
        'strategy':'Fixed source/geometry and atlas controls completed before contingent1024; no second reconstruction of saved shell.',
        'anticipation':'Whole face, beard, crown and reverse angles reviewed in textured/clay controls; eyes remain malformed and beard solid.',
        'stopping':'Export-only rescue rejected; continue the authorized contingent1024 test only after its separate cost/payload admission.',
        'versioning':'GLB hashes verified, identical geometryUV for atlas pair, independent Blender reopen bindings exact; originals unchanged.',
        'economics':'Verified temporary teardown and compute upper bound recorded; actual AWS invoice unknown; raw budget holds retained.',
        'rights':'Same admitted runtime/source and export path, no new rights route; private temporary files removed after verified retrieval.',
        'current_state':'Accepted Pashtun253 and Sikhv03 preserved; failed source is not a new actor/design approval.',
        'au_reference':'Root directly inspected approved Sikhv03 and accepted Pashtun frame0200; accepted differences not repaired away.',
        'sikh_scope':'Head-only source comparison, no body/cloth/identity rewrite or new character scope.'}
    checks=[]
    for obligation in packet['obligations']:
        key=obligation['id'];status='FAIL' if key in fail else 'NOT_RUN' if key in unrun else 'PASS'
        checks.append({'id':key,'kind':obligation['check_kind'],'status':status,
            'action_taken':'Manual static source review and separate technical checks.',
            'observation':notes.get(key,'Malformed eye forms, solid coarse facial hair and noisy turban remain below approved reference/co-star floor.' if status=='FAIL' else 'Static export controls do not qualify motion, deformation, contact or one-cloth performance.'),
            'evidence':evidence})
    review={'packet_digest':packet['packet_digest'],'scope':'Completed fixed-source export comparison; principal admission blocked',
        'checks':checks,'hypotheses':[{'prediction':'Final decimation/atlas loss explains unacceptable facial source quality.',
            'observation':'Higher retention adds beard detail but does not fix eye/moustache anatomy;4K has little visible benefit.',
            'response':'Reject export-only rescue and test the separately admitted1024 source next.','result':'resolved'}],
        'adjacent_regressions':'Higher retention makes rough beard crevices more explicit; no accepted source changed. Performance remains NOT_RUN.',
        'stopping_reason':'Diagnostic substage complete, integrated quality investigation continues; not a character handoff.'}
    dump(target/'export-review.json',review)
    gate=pk.check_review(ROOT,packet,review);dump(target/'export-production-gate.json',gate)
    print(json.dumps(gate,indent=2))


if __name__=='__main__':main()
