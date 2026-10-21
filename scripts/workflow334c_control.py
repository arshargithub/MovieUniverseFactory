"""Trusted task-specific stage/dispatch commands, never a raw Blender launcher."""
import json
import sys
from pathlib import Path
from movie_factory import production_workflow as wf, native_admission as na, production_knowledge as pk
from movie_factory.task_router import DATABASE
from workflow334c import ROOT, OUT, TASK, SOURCE, save, bind


def controller():
    return wf.Controller(ROOT, DATABASE)


def admit():
    c = controller(); packet = c.packet(TASK)
    observations = {
        'grounding': ('Original334 approval and332 next package bind the task;331 rejection/limits remain explicit.', 'No blanket production renewal inferred.'),
        'expert_coverage': ('Production/reuse, framing and visible anatomy apply; no motion/audio construction.', '328 allows justified omitted lenses for static technical controls.'),
        'film_alignment': ('The existing scene is a negative control, not a lowered same-film target.', 'Accepted253 quality remains unchanged.'),
        'preferences': ('Routine methods and failure tests proceed without Director micro-approval.', 'No predictable artistic failure will be offered as ready.'),
        'reference_roles': ('Native320 is bound as negative_control;331 audit supplies rejection reasons.', 'A rejected native cannot become an exact accepted visual target.'),
        'method': ('Fixed no-edit save then separate-process reopen tests a real interface beyond mocks.', 'Not sufficient for arbitrary pose editing; that remains outside this tested envelope.'),
        'interfaces': ('Relative file remapping, selected rig state and actual render bindings are checked.', 'Scoped inventory cannot certify every cache, node path or complete scene preservation.'),
        'efficient_quality': ('Two native jobs and one deliberately blocked successor, no full sequence render.', 'This exposes boundary failure without more costume/pose patching.'),
        'authority': ('Current chat plans; existing local Blender executes fixed handler. No API/spend/upload/install.', '325 remains exhausted and331 corrections stay consumed.')}
    checks = {name: {'status': 'PASS', 'observation': obs, 'comparison': comparison,
                     'source_ids': ['direction', 'constraints', 'learnings']}
              for name, (obs, comparison) in observations.items()}
    response = {'input_digest': packet['planning_input_digest'], 'outcome': 'admit', 'issues': [],
        'checks': checks, 'strongest_counterexample': 'A successful round-trip may reproduce a bad scene perfectly. '
        'Its visual failure must still block production; this test qualifies infrastructure only.'}
    c.submit(TASK, packet['actor'], packet['ticket'], response, 'workflow334c-CHALLENGING')
    save('challenging.json', response)
    print(json.dumps({'stage': c.state(TASK)['stage'], 'native_jobs_before_admission': len(na.Bridge(c).runs(c.state(TASK)))}))


def dispatch(step):
    c = controller(); bridge = na.Bridge(c)
    parent = bind(SOURCE) if step == 'save' else bridge.runs(c.state(TASK))['save']['artifacts']['native']
    recipe_path = 'results/workflow334c/' + ('save-recipe.json' if step == 'save' else 'render-recipe.json')
    run = bridge.dispatch(TASK, step, 'workflow334c-' + step, parent=parent,
                          blender_bin=na.BLENDER_BIN, timeout=600, recipe=bind(recipe_path))
    save(step + '-run.json', run)
    print(json.dumps(run))
    if run['status'] != 'RETURNED': raise SystemExit(2)


def review_save():
    c = controller(); bridge = na.Bridge(c); run = bridge.runs(c.state(TASK))['save']
    # Invoked only after the main agent inspects actual inventory and source hashes.
    verdict = {'verdict': 'PASS', 'run_digest': pk.digest(run), 'open_defects': [], 'evidence': run['artifacts'],
        'observation': 'Source-preserving derivative, required selected horse/leader state and scoped external inventory present; original hash unchanged.',
        'comparison': 'Meets save-stage technical prerequisite only. Fresh-process state and appearance remain unqualified until reopen; no artistic approval.'}
    bridge.record_review(TASK, 'save', verdict); save('save-review.json', verdict)
    print('Save-stage technical review recorded; reopen now eligible.')


def reject_and_probe():
    c = controller(); bridge = na.Bridge(c); state = c.state(TASK)
    run = bridge.runs(state)['reopen']
    visual = pk.read_json(ROOT, 'results/workflow334c/visual-review.json')
    verdict = {'verdict': 'FAIL', 'run_digest': pk.digest(run), 'open_defects': visual['open_defects'],
        'evidence': run['artifacts'] | {'review': bind('results/workflow334c/visual-review.json')},
        'observation': visual['observation'], 'comparison': visual['comparison']}
    bridge.record_review(TASK, 'reopen', verdict); save('reopen-review.json', verdict)
    try:
        dispatch('dependent')
    except wf.Blocked as exc:
        assert str(exc) == 'DEPENDENCY_REVIEW_FAILED', str(exc)
        assert not (ROOT / '.runtime/factory-native/workflow334c-dependent').exists()
        assert 'dependent' not in bridge.runs(c.state(TASK))
        save('negative-control.json', {'expected': 'DEPENDENCY_REVIEW_FAILED', 'actual': str(exc),
            'worker_launched': False, 'output_created': False, 'source_failure': pk.digest(verdict)})
    else:
        raise AssertionError('FAILED PROOF DID NOT BLOCK')
    # No hidden retry. The deliberate negative control exhausts its zero-repair
    # task; this is not artistic acceptance or a reset of331.
    c.replan(TASK, 'STRATEGIZING', 'Negative-control closure: rejected source blocks production; no artistic correction authority in334.',
             'workflow334c-close-negative')
    save('controller-state.json', {k:v for k,v in c.state(TASK).items() if k != 'ticket'})
    print(json.dumps({'negative_control': 'PASS', 'stage': c.state(TASK)['stage']}))


def failed_preflight():
    c = controller(); bridge = na.Bridge(c); run = bridge.runs(c.state(TASK))['save']
    assert run['status'] == 'FAILED'
    findings = {}
    for name, action, expected in [
        ('dependent', lambda: bridge.dispatch(TASK, 'reopen', 'workflow334c-reopen', parent=bind(SOURCE),
             blender_bin=na.BLENDER_BIN, recipe=bind('results/workflow334c/render-recipe.json')), 'NATIVE_JOB_NOT_SUCCESSFUL'),
        ('rename_retry', lambda: bridge.dispatch(TASK, 'save', 'workflow334c-renamed', parent=bind(SOURCE),
             blender_bin=na.BLENDER_BIN, recipe=bind('results/workflow334c/save-recipe.json')), 'NATIVE_STEP_ALREADY_ATTEMPTED_REPLAN_REQUIRED'),
        ('delivery', lambda: c.deliver(TASK, 'workflow334c-forbidden-delivery'), 'NOT_READY')]:
        try: action()
        except wf.Blocked as exc:
            assert str(exc) == expected, str(exc)
            findings[name] = {'expected': expected, 'actual': str(exc), 'blocked': True}
        else: raise AssertionError(name + ' was not blocked')
    assert len(bridge.runs(c.state(TASK))) == 1
    assert not (ROOT / '.runtime/factory-native/workflow334c-reopen').exists()
    save('negative-control.json', {'controls': findings, 'native_runs': 1, 'followup_workers_launched': 0})
    c.replan(TASK, 'STRATEGIZING', 'Native control failed before save: skipped embedded script flagged. '
        'No evidence to qualify persistence; retain zero artistic corrections and failed attempt.', 'workflow334c-failed-control-close')
    save('controller-state.json', {k:v for k,v in c.state(TASK).items() if k != 'ticket'})
    for name in ['stdout.log', 'stderr.log', 'worker-status.json', 'runner-status.json']:
        path = ROOT / '.runtime/factory-native/workflow334c-save' / name
        (OUT / ('native-' + name)).write_bytes(path.read_bytes())
    print(json.dumps({'negative_controls': 'PASS', 'native_qualification': 'FAIL', 'stage': c.state(TASK)['stage']}))


if __name__ == '__main__':
    command = sys.argv[1]
    if command in {'save', 'reopen', 'dependent'}: dispatch(command)
    else: {'admit': admit, 'review-save': review_save, 'reject-and-probe': reject_and_probe,
           'failed-preflight': failed_preflight}[command]()
