"""Offline real-candidate regression and subprocess recovery; no production edits.

Observations below were made manually from existing images. This program does
not perform perception and does not convert these observations into a PASS.
"""
import json
import subprocess
import sys
from pathlib import Path

from movie_factory import production_knowledge as pk
from movie_factory import review_control as rc

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/review307'


def save(name, data):
    (OUT/name).write_text(json.dumps(data, indent=2)+'\n')


def run(*args):
    p = subprocess.run([sys.executable, '-m', 'movie_factory.review_control', *args],
                       cwd=ROOT, capture_output=True, text=True, check=False)
    return p.returncode, json.loads(p.stdout)


def bind(name):
    return {'path': name, 'sha256': pk.file_hash(ROOT/name)}


def main():
    c, s, fingerprint = rc.load(ROOT)
    # Two separate interpreters, no builder transcript or cached Python state.
    code_a, a = run('capsule')
    code_b, b = run('capsule')
    assert code_a == code_b == 0 and a == b
    assert len(a['open_defects']) == 4 and len(a['requirements']) == 13
    assert a['capabilities']['direct_motion'] is False
    assert a['capabilities']['direct_audio'] is False
    save('review-capsule.json', a)
    observations = [
        {'id':'rear', 'mode':'timed_images', 'path':'.runtime/audit306/candidate-rear.jpg',
         'comparison_path':'.runtime/audit306/reference-rear.jpg', 'status':'FAIL',
         'observation':'Candidate torso pitches around a largely fixed hind support with paired foreleg shapes; the reference has distinct preparation, head/neck change, forefoot support, apex and landing articulation.',
         'comparison':'Matched 4 fps image sequences: candidate 11.5-15 s versus reference 15.5-19 s. Rejects pose progression; not real-time cadence or audio acceptance.'},
        {'id':'terrain', 'mode':'image', 'path':'.runtime/art-direction/series01-sikh305/movie-13/frames/frame-0648.png',
         'status':'FAIL', 'observation':'Broad uniform gray road and long smooth, nearly symmetric drainage furrows with repeated tufts still read as constructed surfaces rather than a worked rural track and drainage system.',
         'comparison':'Compare road-to-ditch-to-field continuity against the agreed rural Punjab scene intent; visual judgment, not a quantified realism score.'},
        {'id':'field_boundaries', 'mode':'image', 'path':'.runtime/art-direction/series01-sikh305/movie-13/frames/frame-0080.png',
         'status':'FAIL', 'observation':'Hard straight edges and flat green strips are plainly exposed between plots; the earth bund/vegetation transition is not believable.',
         'comparison':'The Director asks for agricultural plot divisions, not rectangular carpet strips. Known regression, not a novel blind discovery.'},
        {'id':'debris', 'mode':'timed_images', 'path':'.runtime/audit306/brake-aftermath.jpg',
         'status':'FAIL', 'observation':'Brake fragments disappear without a credible persistent settled residue; audit306 separately traces fixed-lifetime hide_render after landing.',
         'comparison':'5-7.5 s at 8 fps image sequence plus source diagnosis in audit306. Solid chips must settle/persist or leave view; dust may dissipate.'},
    ]
    evidence = {}
    for row in observations:
        row['binding'] = bind(row.pop('path'))
        if 'comparison_path' in row:
            row['comparison_binding'] = bind(row.pop('comparison_path'))
        evidence[row['id']] = {'binding':row['binding'], 'mode':row['mode'],
            'observation_scope':row['comparison'], 'candidate_digest':pk.digest(s['artifacts'])}
    checks=[]
    for req in c['requirements']:
        obs=next((o for o in observations if o['id']==req['id']),None)
        checks.append({'id':req['id'], 'status':'FAIL' if obs else 'NOT_RUN',
            'observation':obs['observation'] if obs else 'No new acceptance judgment in this process-calibration pass.',
            'comparison':obs['comparison'] if obs else 'Required criterion retained; no inherited PASS.',
            'evidence':[req['id']] if obs else []})
    review={'fingerprint':fingerprint, 'purpose':'scoped_review', 'candidate':s['artifacts'],
            'evidence':evidence, 'checks':checks, 'defect_closures':{},
            'adjacent_review':{'status':'NOT_RUN','observation':'No full-sequence acceptance in this audit.', 'evidence':[]}}
    save('actual305-review.json',review)
    receipt='results/review307/SHOULD_NOT_EXIST.json'
    assert not (ROOT/receipt).exists()
    check_code,checked=run('check','--review','results/review307/actual305-review.json')
    deliver_code,delivered=run('deliver','--review','results/review307/actual305-review.json','--output',receipt)
    assert check_code==deliver_code==2
    assert not delivered['ready_for_scoped_review'] and 'artifacts' not in delivered
    assert not (ROOT/receipt).exists()
    for defect in s['defects']:
        assert 'OPEN_DEFECT:'+defect['id'] in delivered['failures']
    save('actual305-gate.json',delivered)
    transfer=[
        {'id':'historical175-negative', 'binding':bind('.runtime/art-direction/series01-facebuilder-trial-01/wardrobe175-preview01/upper-rear.png'),
         'status':'FAIL_STATIC_ROUTE', 'observation':'Stiff parallel corrugated rear band, rectangular silhouette and abrupt joins fail a naturally supported cloth route.'},
        {'id':'historical185-limited-positive', 'binding':bind('.runtime/art-direction/series01-facebuilder-trial-01/wardrobe185-redressreview02/rear-217.png'),
         'status':'PASS_VISIBLE_STATIC_REAR_FOLDS_ONLY', 'observation':'Overlapping irregular folds sit outside rear headfall, with nonrectangular edges. Occluded shoulder connections and dynamics are not accepted by this still.'},
        {'id':'accepted253-anchor', 'binding':bind('.runtime/art-direction/series01-finish248/encoded-qc01/controls/clean-14.png'),
         'status':'PASS_STATIC_GEOGRAPHY_READABILITY_ONLY', 'observation':'Checkpoint figures and the rocky detour read as distinct options in a detailed illustrated environment. Existing Director acceptance is preserved; this is not new motion/audio approval.'}
    ]
    save('manual-calibration.json',{'known305_regressions':observations,'transfer_controls':transfer,
        'method':'Same-agent visual inspection. Labels and historical context known. Controls selected after implementation, not blind or statistically independent.',
        'limits':'No measured general visual accuracy, fresh-model review or direct playback/listening qualification. No claim that tests detect fabricated well-formed perceptual PASS declarations.',
        'adjacent_hypothesis':{'id':'H307-crop-root-density','status':'UNCONFIRMED',
            'observation':'Exposed thin repeated crop stalk bases at field edges may remain artificial even after green strips are fixed.',
            'test':'Inspect actual framing and closer ground/crop boundary proof after upstream terrain correction; do not declare a Director-approved defect or start unrelated polish.'}})
    save('integration-results.json',{'real305_check_exit':check_code,'real305_deliver_exit':deliver_code,
        'receipt_emitted':False,'open_defects_preserved':4,'requirements_preserved':13,
        'subprocess_capsules_equal':True,'fresh_processes':2,'capsule_sha256':pk.digest(a),
        'capsule_utf8_bytes':len(json.dumps(a,indent=2).encode()),
        'knowledge_packet_utf8_bytes':(OUT/'knowledge-packet.md').stat().st_size,
        'protected_artifacts_rehashed':True,'production_changes':False,
        'limits':'Process restart proves state reconstruction, not LLM memory retention, independent judgment, or reduced total prompt size.'})
    # Review the software/process package, never the scene, through the existing
    # bridge as well. Each observation is deliberately scoped to this package.
    process_observations = {
        'authority':('Kept production paused and all external actions out of scope.', 'Only local code, tests and records changed; protected candidate and Pashtun bindings still verify.', 'integration-results.json'),
        'strategy':('Implemented the frozen strategy with a supported-path boundary and recovery proof.', 'Real305 rejection, synthetic positive tests and subprocess recovery are demonstrated; perception limitations are not hidden.', 'REVIEW.md'),
        'visual_gate':('Kept scene readiness separate from software admission.', 'Four known visual regressions remain open; timed images were not promoted to direct motion/audio.', 'manual-calibration.json'),
        'anticipation':('Injected stale, missing, relabeled and unsupported evidence cases; inspected transfer controls.', '102 tests pass; adjacent crop-edge hypothesis remains unconfirmed rather than being silently accepted.', 'tests.xml'),
        'stopping':('Completed process package without starting construction or claiming visual readiness.', 'Review route qualification is the named next prerequisite; no incremental scene handed off as complete.', 'REVIEW.md'),
        'versioning':('Bound current contract/state/candidate/engine/knowledge and rehashed at delivery.', 'Both actual delivery and restart tests use current hashes; no receipt is emitted for305.', 'integration-results.json'),
        'economics':('Recorded lifecycle/test jobs locally and used no paid providers or installations.', 'Byte counts are not token counts; capture gap and unknown usage are disclosed.', 'REVIEW.md'),
        'retrieval':('Read fresh knowledge packet and manually reconciled thirteen305 scope requirements.', 'Eleven global/process obligations remain; the knowledge-only task is explicitly not a future domain production packet.', 'review-capsule.json'),
        'current_state':('Preserved exact253 acceptance and current306 rejection over historical optimistic statuses.', 'Fresh processes preserve protected Pashtun and all four open scene defects.', 'integration-results.json'),
        'au_reuse':('Carried reference/quality-floor, provenance and review-escape lessons into admission.', 'Accepted Pashtun anchor is not reopened; negative controls stay negative and tests are not artistic proof.', 'manual-calibration.json'),
        'au_review':('Recorded regression versus transfer controls and perception limits explicitly.', 'Familiar same-agent controls are not reported as independent held-out accuracy.', 'manual-calibration.json'),
    }
    packet=json.loads((OUT/'knowledge-packet.json').read_text())
    assert set(process_observations)=={r['id'] for r in packet['obligations']}
    process_review={'packet_digest':packet['packet_digest'],
        'scope':'Software/process307 only. No motion, audio or scene artistic acceptance.',
        'checks':[{'id':r['id'],'kind':r['check_kind'],'status':'PASS',
            'action_taken':process_observations[r['id']][0],
            'observation':process_observations[r['id']][1],
            'evidence':[bind('results/review307/'+process_observations[r['id']][2])]}
            for r in packet['obligations']],
        'hypotheses':[
            {'prediction':'A development label or stale state could bypass the agreed scoped checks.',
             'observation':'Injected failures and real305 block in the supported command.',
             'response':'Use the fresh delivery receipt; arbitrary chat remains outside enforcement.', 'result':'resolved'},
            {'prediction':'Structured tests could be misreported as artistic qualification.',
             'observation':'Same-agent controls and absent direct motion/audio are insufficient for that claim.',
             'response':'Retain false modality flags and scoped claims; route qualification remains separate.', 'result':'resolved'}],
        'adjacent_regressions':'Existing knowledge and255 tests retained; obsolete assertion corrected with recorded explanation. Protected production hashes unchanged. No visual acceptance inferred.',
        'stopping_reason':'Authorized local control package complete; independent perception and direct motion/audio qualification explicitly remain unproven. Production remains paused.'}
    save('process-review.json',process_review)
    process_gate=pk.check_review(ROOT,packet,process_review)
    save('process-gate.json',process_gate)
    assert process_gate['ready_for_review'], process_gate
    print(json.dumps({'real305_blocked':True,'receipt_emitted':False,'fresh_processes_equal':True,
                      'output':'results/review307/integration-results.json'}))


if __name__ == '__main__':
    main()
