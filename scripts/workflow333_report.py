"""Evidence report; unsuccessful native qualification must remain explicit."""
import json
from movie_factory import production_knowledge as pk, context_hygiene as ch
from movie_factory.production_workflow import Controller
from movie_factory.task_router import DATABASE
from workflow333 import ROOT, OUT, TASK, save, bind


def main():
    receipt = pk.read_json(ROOT, '.runtime/context-hygiene/runs/workflow333-qualified-tests/receipt.json')
    assert receipt['exit_code'] == 0
    assert pk.file_hash(ROOT / receipt['stdout']) == receipt['stdout_sha256']
    (OUT / 'tests.txt').write_text((ROOT / receipt['stdout']).read_text())
    save('test-receipt.json', receipt)
    previous = pk.read_json(ROOT, 'results/workflow332/protected.json')
    protected = {p: {'expected': v['expected'], 'actual': pk.file_hash(ROOT / p)} for p, v in previous.items()}
    assert all(v['actual'] == v['expected'] for v in protected.values())
    assert pk.read_json(ROOT, 'results/sikh331/STATUS.json')['native_dispatch_closed']
    save('protected.json', protected)
    c = Controller(ROOT, DATABASE); c._fresh(c.state(TASK))
    save('routing-receipt.json', c.routing('workflow333-handler-qualification'))
    events = c.events(TASK)
    save('stage-trace.json', [{k: v for k, v in e.items() if k in {'event_id', 'utc', 'stage', 'kind', 'action'}} for e in events])
    ch.load(ROOT)
    packet = pk.task_packet(ROOT, pk.read_json(ROOT, 'results/workflow333/task.json'))
    assert packet['packet_digest'] == pk.read_json(ROOT, 'results/workflow333/knowledge-packet.json')['packet_digest']
    paths = ['results/workflow333/CLOSEOUT.md', 'results/workflow333/tests.txt',
             'results/workflow333/negative-control.json', 'results/workflow333/protected.json',
             'results/workflow333/save-run.json', 'results/workflow333/native-worker-status.json',
             'results/workflow333/native-stdout.log', 'results/workflow333/stage-trace.json',
             'src/movie_factory/native_admission.py', 'src/movie_factory/adapters/blender/nihang_control.py',
             'tests/test_native_handler333.py', 'tests/test_knowledge317.py', 'tests/test_knowledge319.py']
    evidence = [bind(p) for p in paths]
    uses = {
        'reuse_envelope': 'Existing runner/controller extended; real native positive use remains unqualified.',
        'authority': 'Only source-preserving control attempted. No embedded code enabled, new artist variant, paid call, install or upload.',
        'strategy': 'Frozen four-stage plan preceded worker; first control failed and successor blocked.',
        'visual_gate': 'No render returned; no image or motion PASS supplied. Negative native preflight is not a visual-control success.',
        'anticipation': 'Actual skipped-script warning exposed an overbroad dependency inference; no quiet waiver to continue.',
        'stopping': 'Report unsuccessful qualification with explicit recovery gap, not readiness based on test count.',
        'versioning': 'Parent/reference/accepted hashes rechecked; actual worker error and stage records retained.',
        'economics': 'One local native process; no measured efficiency gain or engineering token claim; capture gap disclosed.',
        'retrieval': 'Fresh twelve-obligation packet plus330/328/331/332 and AU13/16 manual reconciliation; no corpus completeness claim.',
        'current_state': '331/325 not reopened;253 accepted and320 rejected remain unchanged.',
        'au_reuse': 'Local logs/tests retained; no fresh native replay or remote protection claim.',
        'au_review': 'Gate success below qualifies truthful process reporting only; native failure and missing outputs stay explicit.'}
    review = {'packet_digest': packet['packet_digest'], 'scope': 'Process reporting of FAILED native qualification, not media delivery.',
        'checks': [{'id': o['id'], 'status': 'PASS', 'kind': o['check_kind'], 'action_taken': uses[o['id']],
                    'observation': uses[o['id']], 'evidence': evidence} for o in packet['obligations']],
        'hypotheses': [{'prediction': 'A real failed prerequisite might still allow dependent native work.',
            'observation': 'Dependent launch, renamed retry and delivery all blocked after actual worker failure.',
            'response': 'Preserve exact negative receipts; positive reopen remains NOT_RUN.', 'result': 'resolved'},
            {'prediction': 'Skipped embedded code might block the no-edit path.',
             'observation': 'It did. Current guard cannot distinguish skipped UI from evaluation dependency.',
             'response': 'Record native qualification FAIL and future diagnostic/recovery requirement; do not enable scripts.', 'result': 'resolved'}],
        'adjacent_regressions': '408 focused tests pass. Three stale historical source assertions corrected against approved320 amendment, without changing pins or historical task records.',
        'stopping_reason': 'Bounded native control ended unsuccessfully before save; actual failure controls verified. Native implementation remains unqualified; no art/media handoff.'}
    save('knowledge-review.json', review)
    gate = pk.check_review(ROOT, packet, review); save('knowledge-gate.json', gate)
    assert gate['ready_for_review'], gate
    native = pk.read_json(ROOT, 'results/workflow333/native-runner-status.json')
    report = {'scope': 'Native handler qualification333', 'overall': 'NATIVE_QUALIFICATION_FAILED',
        'tests': (OUT / 'tests.txt').read_text().strip().splitlines()[-1], 'knowledge_reporting_gate': gate,
        'native_processes': 1, 'native_elapsed_seconds': native['elapsed'],
        'save': 'NOT_RUN_GUARD_FAILED_BEFORE_SAVE', 'fresh_process_reopen': 'NOT_RUN', 'render': 'NOT_RUN',
        'actual_failed_prerequisite_controls': 'PASS', 'mock_positive_and_bad_output_controls': 'PASS',
        'visual_negative_control': 'NOT_RUN', 'artistic_authoring_qualified': False,
        'production_approved': False, 'provider_calls': 0, 'protected_unchanged': True,
        'controller_state': c.state(TASK)['stage'], 'measured_efficiency_gain': None,
        'engineering_tokens': None, 'remote_protection_performed': False, 'evidence': evidence}
    save('report.json', report)
    print(json.dumps({k: report[k] for k in ['overall', 'tests', 'native_processes', 'native_elapsed_seconds', 'controller_state']}))


if __name__ == '__main__': main()
