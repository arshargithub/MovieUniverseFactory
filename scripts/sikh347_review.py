"""Record inspected52 controls; technical success is not artistic admission."""
import json
from pathlib import Path
from movie_factory import production_workflow as wf, production_knowledge as pk
from movie_factory.native_admission import Bridge
from movie_factory.task_router import DATABASE

r = Path(__file__).resolve().parents[1]
c = wf.Controller(r, DATABASE)
task = 'sikh335-supporting-appearance'
assert c.state(task)['cycle'] == 52
observations = {
    'leader_front': '283/327/350: continuous beard and sewn closure are readable, but eyes/face remain generic and smooth, crown shell-like, shoulders inflated and coat body-shaped. Mottling does not supply garment construction. Accepted Pashtun actual-450 remains a substantially richer integrated finish.',
    'leader_reverse': '283/327/350: spear-side elbow forms a deep dark pocket and wedge-like sleeve; shoulder remains inflated. Waist and sash remain readable but do not make the whole garment plausible. All three reverse controls veto the front-only improvement.',
    'leader_anatomy': '283/327/350 with clothing hidden: spear-side upper arm/elbow shows a hard wedge and unnatural transition beneath the failing sleeve. Underlying anatomy/pose/weights must be discriminated before further cloth finish. Upper-arm roll is only a source-derived hypothesis, not a verified cause.',
    'leader_contact': '283/327/350: fingers surround the shaft but are smooth, widely separated and simplified; wrist transition remains angular, especially327. An endpoint or reduced wrist-angle metric is not a complete anatomical pass. Shoulder/elbow controls independently fail.',
    'render': '283/327/350 production controls: mounted figure remains a simplified assembly rather than a same-film finished supporting character. Actor, horse and saddle form/material finish remain open. Three stills cannot establish rearing fluidity, timing or sound.',
}
for step, observation in observations.items():
    run = pk.read_json(r, f'results/sikh335/look01/{step}-run-c52.json')
    assert run['status'] == 'RETURNED'
    evidence = dict(run['artifacts'])
    ref = '.runtime/art-direction/series01-finish248/opening08/actual-450.png'
    evidence['accepted_co_star'] = dict(path=ref, sha256=pk.file_hash(r/ref))
    verdict = dict(verdict='FAIL', run_digest=pk.digest(run), evidence=evidence,
        observation=observation,
        comparison='Actual three poses in each view inspected. Accepted co-star is finish control, not identity. No direct real-time AV or all-frame claim.',
        open_defects=['Whole actor same-film finish', 'Bare shoulder/elbow and clothed sleeve deformation', 'Complete contact/anatomy', 'Horse/crowd and isolated passage remain open'])
    Bridge(c).record_review(task, step, verdict)
    p = r/f'results/sikh335/look01/{step}-visual-review-c52.json'
    assert not p.exists()
    p.write_text(json.dumps(verdict, indent=2)+'\n')
print('Five actual-image FAIL reviews recorded; no artistic or AV pass.')
