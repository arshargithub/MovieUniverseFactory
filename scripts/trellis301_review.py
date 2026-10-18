"""Record already-performed manual opacity review; metrics are not visual judgment."""
import json
from pathlib import Path

import numpy as np
from PIL import Image
from movie_factory import production_knowledge as pk

from trellis301_prepare import ROOT, OUT, sha, dump


def main():
    images = ROOT / '.runtime/trellis301/opacity'
    packet = json.loads((images / 'packet.json').read_text())
    metrics = []
    for angle in ('front', 'left-quarter', 'right-quarter', 'back'):
        paths = [images / f'{variant}-{angle}.png' for variant in ('opaque', 'alpha')]
        arrays = [np.asarray(Image.open(path).convert('RGB'), dtype=np.int16) for path in paths]
        delta = np.abs(arrays[0] - arrays[1])
        metrics.append({'angle': angle, 'mean_absolute_rgb_difference_0_255': float(delta.mean()),
            'whole_frame_fraction_any_channel_difference_gt10': float((delta.max(axis=2) > 10).mean()),
            'images': [{'path': str(p.relative_to(ROOT)), 'sha256': sha(p)} for p in paths]})
    dump(OUT / 'opacity-metrics.json', {'metrics': metrics,
        'interpretation': 'Reproducibility diagnostics only; not quality scores or evidence of improved hair'})
    paths = [OUT / 'OPACITY_REVIEW.md', OUT / 'opacity-metrics.json', images / 'opaque.json', images / 'alpha.json',
        images / 'render.log', ROOT / 'scripts/trellis301_inspect.py',
        ROOT / '.runtime/art-direction/series01-sikh257/sikh-uncovered-concept-v03.png',
        ROOT / '.runtime/art-direction/series01-finish248/opening-final/frame-0200.png',
        ROOT / '.runtime/art-direction/series01-finish248/delivery01/manifest.json']
    paths += [images / f'comparison-{angle}.jpg' for angle in ('front', 'left-quarter', 'right-quarter', 'back')]
    evidence = [{'path': str(p.relative_to(ROOT)), 'sha256': sha(p)} for p in paths]
    failed = {'visual_gate', 'representation', 'anatomy', 'look', 'au_surface', 'sikh_scope'}
    unrun = {'motion', 'secondary', 'au_deformation', 'au_performance', 'au_contact', 'sikh_cloth', 'sikh_motion'}
    observations = {
        'authority': 'Authorized local diagnostic only. Exact sensitive-payload cloud approval is pending; no indirect retry.',
        'strategy': 'Opacity was isolated before fixed-source retention and contingent resolution controls.',
        'anticipation': 'Actual beard, moustache, brow and crown surfaces were inspected in all four angles; alpha does not resolve the predicted visual failures.',
        'stopping': 'Diagnostic complete, character not ready. Export is blocked on exact-payload approval; shared Blender slot released.',
        'versioning': 'Source was reopened independently for each variant and never saved; original geometry/material bindings were checked.',
        'economics': 'Fresh read-only price and residual-resource inventory are recorded; prospective14USD admission is not an invoice or a paid dispatch.',
        'rights': 'No new model/dependency or output-rights path introduced by local opacity control; prior admitted sources retained.',
        'current_state': 'Accepted Pashtun253 and Sikh illustratedv03 preserved; failed298 actor admission remains failed.',
        'au_reference': 'Directly inspected approved Sikhv03 and accepted Pashtun close-shot frame0200; rejected candidates are not quality targets.',
    }
    checks = []
    for obligation in packet['obligations']:
        key = obligation['id']
        status = 'FAIL' if key in failed else 'NOT_RUN' if key in unrun else 'PASS'
        observation = observations.get(key, 'Unresolved eye anatomy, chunky beard and crown cavities fail the existing quality floor.' if status == 'FAIL'
            else 'Static material-only control does not test actor motion, deformation, contact or cloth performance.')
        checks.append({'id': key, 'kind': obligation['check_kind'], 'status': status,
            'action_taken': 'Reviewed only the local static opacity diagnostic and preserved separate production obligations.',
            'observation': observation, 'evidence': evidence})
    review = {'packet_digest': packet['packet_digest'], 'scope': 'Completed opacity diagnostic; production admission blocked',
        'checks': checks, 'hypotheses': [{'prediction': 'Enabling generated alpha may recover convincing facial-hair detail.',
            'observation': 'Moustache/brows become patchy and translucent while coarse beard and crown defects remain.',
            'response': 'Reject opacity-only rescue; preserve original control and await admitted fixed-source export comparison.', 'result': 'resolved'}],
        'adjacent_regressions': 'Alpha degrades moustache/brow/nape solidity; no source asset was changed. Motion and actor interfaces remain NOT_RUN.',
        'stopping_reason': 'Local diagnostic complete; exact sensitive-payload upload approval pending. No character or full-comparison completion claimed.'}
    dump(OUT / 'opacity-review.json', review)
    gate = pk.check_review(ROOT, packet, review)
    dump(OUT / 'opacity-production-gate.json', gate)
    print(json.dumps(gate, indent=2))


if __name__ == '__main__':
    main()
