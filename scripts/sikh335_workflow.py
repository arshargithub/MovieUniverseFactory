"""Authored local335 work records. No provider, embedded script or raw Blender launcher."""
import json
import sys
from pathlib import Path
from movie_factory import production_knowledge as pk

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/sikh335'
TASK = 'sikh335-control-ownership'
SOURCE = '.runtime/art-direction/series01-sikh320/build-10/sequence.blend'


def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2) + '\n')


def bind(path):
    return {'path': path, 'sha256': pk.file_hash(ROOT / path)}


def prepare():
    task = pk.read_json(ROOT, 'results/sikh331/pose-03/task.json')
    paths = ['results/sikh335/REQUEST.md', 'results/sikh335/STRATEGY.md',
        'results/sikh331/PROOF_AUDIT.md', 'results/workflow330/NIHANG_PROSPECTIVE_BRIEF.md',
        'docs/knowledge/NATIVE_WORKFLOW_334.md', 'docs/knowledge/PLANNING_PIPELINE_330.md',
        'docs/knowledge/EXPERT_LENS_PLANNING_328.md', SOURCE]
    task.update(id=TASK, operation='motion',
        entities=['nihang_leader', 'nihang_horse', 'nihang_crowd', 'renderer'],
        query='Nihang whole horse control ownership rearing support rider interfaces same-film clothing crowd attention',
        intent='Inspect real control ownership before representation repair and integrated isolated leader/crowd production.',
        inputs={p: pk.file_hash(ROOT / p) for p in paths},
        execution_authority={'source': paths[0], 'scope': 'Resume334 recommended representation package; read-only rig precursor first.'})
    save('task.json', task)
    packet = pk.task_packet(ROOT, task)
    save('knowledge-packet.json', packet)
    print(json.dumps({'ready': packet['dispatch_ready'], 'blockers': packet['blockers'],
                      'obligations': packet['obligations'], 'impact': packet.get('impact_set')}, indent=2))


def plan():
    from movie_factory import production_workflow as wf, planning_pipeline as pp, expert_planning as ep
    from movie_factory.task_router import DATABASE
    c = wf.Controller(ROOT, DATABASE)
    knowledge = pk.task_packet(ROOT, pk.read_json(ROOT, 'results/sikh335/task.json'))
    assert knowledge['dispatch_ready']
    save('inspect-recipe.json', {'operation': 'nihang_rig_inspect', 'frame': 327,
                                 'width': 64, 'height': 64, 'samples': 1})
    paths = {'direction': 'results/sikh335/STRATEGY.md', 'learnings': 'results/sikh331/PROOF_AUDIT.md',
        'film_language': 'docs/knowledge/CURRENT_PRODUCTION_STATE.md',
        'director_preferences': 'docs/planning/SHOT_BEAT_QUALITY_BRIEF.md',
        'references': 'results/workflow330/NIHANG_PROSPECTIVE_BRIEF.md',
        'controls': 'results/sikh335/task.json', 'constraints': 'docs/knowledge/NATIVE_WORKFLOW_334.md'}
    statements = {
        'direction': 'Resume the integrated isolated production package; this precursor discovers rig ownership before any new pose authoring.',
        'learnings': '331 failed whole-pose support and same-film character fidelity despite incremental offset corrections; those attempts remain closed.',
        'film_language': 'Accepted Pashtun quality stays fixed; a supporting actor cannot be a schematic statue.',
        'director_preferences': 'Predict failure through expert lenses and fix internally; setup and routine algorithms are not handovers.',
        'references': 'Reference14–19s governs faithful action phases; accepted film governs appearance; rejected poses are negative controls.',
        'controls': 'Fresh motion-domain packet and manual AU09–13,16 plus317–334 reconciliation accompany this inspection.',
        'constraints': 'Inspect64 invalid used-armature drivers, removed object drivers and FK bypasses; no blind restoration or defect waiver.'}
    sources = [{'id': k, 'category': k, 'binding': bind(p), 'status': 'adopted', 'required': True,
                'statement': statements[k], 'scope': '335 read-only ownership precursor to integrated production'} for k, p in paths.items()]
    for s in sources:
        if s['id'] == 'film_language': s['lines'] = [1, 27]
        if s['id'] == 'director_preferences': s['lines'] = [1, 36]
    specs = {
        'preservation': ('Source masters remain unchanged; no pose or appearance edits during diagnosis.', 'production_reuse'),
        'ownership': ('Record all horse rest/evaluated joints, constraint targets/influences, driver paths and mesh bindings; distinguish control from deformation.', 'animation_physics'),
        'support': ('Identify the supported hindquarter chain and neck/poll/foreleg ownership needed for coupled gather, lift and landing.', 'anatomy_contact'),
        'no_false_pass': ('A successful inventory is not a healthy rig, faithful rearing, same-film look or Director AV pass.', 'story_performance')}
    ids = list(specs)
    reqs = [{'id': k, 'criterion': v[0], 'modes': ['technical'], 'director_av': False} for k, v in specs.items()]
    ref = {'id': 'reference_rear', 'role': 'faithful_motion',
        'time_range_seconds': [14, 19],
        'binding': bind('.runtime/art-direction/series01-sikh256/references/reference-b.mov'),
        'authority': 'Director requires faithful rearing, not a simplified approximation.',
        'scope': '14–19 seconds; source inventory is preparatory and does not qualify performance.',
        'fidelity': 'Coordinated gather, driving hindquarters, brief crest, accelerating reach/contact and absorption.',
        'allowed_variation': 'Adapt to shot geography and existing horse proportions without robotic phase boundaries.',
        'not_authority': 'Not a new identity, wardrobe license or exemption from same-film quality.',
        'aspects': [{'id': 'whole_pose', 'instruction': 'Discover controls that can reproduce whole-body phases rather than root rotation alone.', 'requirements': ids}]}
    applicable = {lens: [k for k, v in specs.items() if v[1] == lens] for lens in ep.LENSES}
    why = {lens: ('Required to interpret actual rig evidence before selecting a representation.' if applicable[lens]
                 else 'Deferred to integrated335 production; no camera, effects, audio or visual change in this read-only precursor.') for lens in ep.LENSES}
    beats = [{'id': 'ownership', 'audience_read': 'No new audience media yet; eliminate unsupported representation assumptions.',
        'framing': 'Inventory at rejected crest327; evaluated against reference phase comparison, not artistic approval.',
        'lenses': {n: {'applies': bool(applicable[n]), 'why': why[n], 'requirements': applicable[n]} for n in ep.LENSES}}]
    real = {k: {'beats': ['ownership'], 'lenses': [v[1]], 'derivation': v[0],
        'method': 'Read-only typed native inventory; inspect target paths, constraints, deform chain and source/reference evidence.',
        'interfaces': ['controller → trusted worker → horse controls → deform bones → mesh → rider/contact future proof'],
        'early_proof': 'Full ownership report before correction keys or crowd propagation.',
        'failure_condition': 'Incomplete ownership evidence, unbound source, mutation or claiming motion quality from an inventory.',
        'reopen_when': 'Source rig or control ownership changes.', 'priority': 'quality_floor',
        'origin': 'craft_inference', 'reference_ids': ['reference_rear']} for k, v in specs.items()}
    applications = json.loads((OUT / 'learning-application.json').read_text())
    mapping = {k: {'requirements': ids, 'reason': v} for k, v in applications.items()}
    bindings = {k: bind(v) for k, v in paths.items()}
    for p in (SOURCE, 'results/sikh335/inspect-recipe.json', 'scripts/sikh335_workflow.py',
              'src/movie_factory/adapters/blender/nihang_control.py', 'src/movie_factory/adapters/blender/worker.py'):
        bindings[p] = bind(p)
    intent = 'Determine actual horse control and deformation ownership before representation-level correction, without mutating media.'
    protected = ['Accepted Pashtun253', 'Rejected320/331 source and failures', '325 exhausted provider allowance']
    brief = {'schema': 1, 'route': 'production', 'intent': intent,
        'audience_result': 'Next motion method has evidence of coordinated whole-body control instead of guessed offsets.',
        'strategy': 'Read-only ownership inspection before deciding targeted repair or deformation rebuild.',
        'early_proof': 'Driver target paths, constraints and evaluated joints from actual native scene.',
        'scope': '335 internal rig ownership precursor', 'exclusions': 'No media edits, artistic approval, paid call or external action.',
        'open_decisions': [], 'offline_only': False, 'protected': protected, 'source_bindings': bindings,
        'knowledge_task': 'results/sikh335/task.json', 'knowledge_digest': knowledge['packet_digest'],
        'knowledge_mapping': mapping, 'requirements': reqs,
        'capabilities': {m: m not in {'direct_audio', 'direct_motion'} for m in wf.rc.MODES},
        'references': [ref], 'reference_plan': {'reference_rear': {'reference_digest': pk.digest(ref),
            'application': 'Map faithful action phases to available controls; do not infer quality from technical success.'}},
        'expert_plan': {'version': 1, 'beat_intents': {'ownership': intent}, 'beats': beats, 'realizations': real}}
    brief['expert_plan']['challenge'] = {'plan_digest': ep.plan_digest(brief), 'open_issues': [],
        'intent_coverage': {'ownership': {'reason': 'Read-only precursor covers preservation, ownership, support and false-positive prevention.', 'requirements': ids}},
        'cross_discipline_conflicts': 'Rig health is not silhouette, performance or costume quality; all remain unqualified.',
        'omission_probe': 'Null driver targets may be display properties rather than deformation; inspect exact paths before blaming them.',
        'scope_tradeoff': 'No render until a usable representation hypothesis is established; integrated deliverable remains open.'}
    direction = {'intent': intent, 'deliverable_id': TASK, 'references': [ref], 'protected': protected,
        'beat_intents': {'ownership': intent}, 'knowledge_task': brief['knowledge_task'],
        'knowledge_digest': brief['knowledge_digest'], 'context_sources': sources}
    # An invalid enum in the first authored plan was caught before dispatch.
    # Reconcile it visibly under the same authority/task; do not erase history.
    c.revise(TASK, brief, bind('results/sikh335/REQUEST.md'),
        'Correct reference role enum to faithful_motion as already required by the Director; no scope or authority change.',
        'sikh335-reference-enum-repair')
    artifacts = {
        'GROUNDING': {'uses': {k: {'disposition': 'apply', 'reason': v, 'implication': v} for k, v in statements.items()},
            'knowledge_uses': applications, 'reconciliation': 'Finite pilot supplemented with330/328/331/334 and AU review/reuse lessons; historical307 capsule is not repinned.', 'unresolved': []},
        'DERIVING': {'requirements': reqs, 'beats': beats,
            'derivations': {k: {f: v[f] for f in pp.DERIVATION_FIELDS} for k, v in real.items()},
            'context_mapping': {k: {'requirements': ids, 'reason': v} for k, v in statements.items()}, 'knowledge_mapping': mapping},
        'STRATEGIZING': {'brief': brief, 'method_choice': {
            'chosen': 'Fixed read-only control/constraint/driver/deformation inventory on the rejected parent.',
            'alternatives': 'Reject another guessed root-pivot pass; do not restore all drivers or rebuild before knowing ownership.',
            'evidence_status': 'hypothesis', 'discriminating_test': 'Determine whether invalid drivers drive deformation or merely UI, and whether actual pose controls reach deform bones.'},
            'steps': [{'id': 'inspect', 'depends_on': [], 'requirements': ids, 'kind': 'proof',
                'acceptance': 'Complete parseable actual ownership evidence, unchanged parent; artistic status remains rejected.',
                'native_recipe': bind('results/sikh335/inspect-recipe.json')}],
            'resource_scope': 'One local read-only worker,600s safety timeout, no external calls or assets.',
            'replan_triggers': 'Missing ownership evidence or unsafe unknown driver blocks; diagnostic findings determine next representation plan, not a Director algorithm approval.'}}
    for stage in pp.STEPS[:3]:
        p = c.packet(TASK)
        response = {'input_digest': p['planning_input_digest'], 'outcome': 'complete', 'artifact': artifacts[stage]}
        c.submit(TASK, p['actor'], p['ticket'], response, 'sikh335-corrected-' + stage)
        save(stage.lower() + '.json', response)
    p = c.packet(TASK); p.pop('ticket', None); save('challenge-input.json', p)
    print(c.state(TASK)['planning_step'])


if __name__ == '__main__':
    {'prepare': prepare, 'plan': plan}[sys.argv[1]]()
