"""Local qualification records; no provider or legacy Blender launcher."""
import json
import sys
from pathlib import Path
from movie_factory import production_knowledge as pk

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/workflow334b'


def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2) + '\n')


def bind(path):
    return {'path': path, 'sha256': pk.file_hash(ROOT / path)}


def prepare():
    task = pk.read_json(ROOT, 'results/workflow330/task.json')
    paths = ['results/workflow334b/STRATEGY.md', 'results/workflow332/CLOSEOUT.md',
             'results/sikh331/PROOF_AUDIT.md', 'docs/knowledge/ROUTER_FIRST_332.md',
             'docs/knowledge/PLANNING_PIPELINE_330.md', 'docs/knowledge/EXPERT_LENS_PLANNING_328.md']
    task.update(id='workflow334b-native-handler',
        query='Native handler qualification immutable save fresh reopen source preservation review blocking',
        intent='Qualify native persistence and failed-proof blocking, not new artistic animation',
        inputs={p: pk.file_hash(ROOT / p) for p in paths},
        execution_authority={'source': paths[0], 'scope': 'Director334 local handler integration and unchanged-source control'})
    save('task.json', task)
    packet = pk.task_packet(ROOT, task)
    save('knowledge-packet.json', packet)
    assert packet['dispatch_ready'], packet['blockers']
    print(json.dumps({'ready': packet['dispatch_ready'], 'obligations': packet['obligations'],
                      'impact': packet.get('impact_set')}))


TASK = 'workflow333-native-control'
SOURCE = '.runtime/art-direction/series01-sikh320/build-10/sequence.blend'


def plan():
    """Authored qualification plan, not a general-purpose automatic planner."""
    from movie_factory import production_workflow as wf, planning_pipeline as pp, expert_planning as ep
    from movie_factory.task_router import DATABASE
    c = wf.Controller(ROOT, DATABASE)
    knowledge = pk.task_packet(ROOT, pk.read_json(ROOT, 'results/workflow334b/task.json'))
    assert knowledge['dispatch_ready']
    for name, operation in [('save-recipe.json', 'nihang_save'), ('render-recipe.json', 'nihang_render')]:
        save(name, {'operation': operation, 'frame': 327, 'width': 540, 'height': 960, 'samples': 8})
    paths = {'direction': 'results/workflow334b/STRATEGY.md',
             'learnings': 'results/sikh331/PROOF_AUDIT.md',
             'film_language': 'docs/knowledge/CURRENT_PRODUCTION_STATE.md',
             'director_preferences': 'docs/planning/SHOT_BEAT_QUALITY_BRIEF.md',
             'references': 'results/sikh331/PROOF_AUDIT.md',
             'controls': 'results/workflow334b/task.json',
             'constraints': 'docs/knowledge/ROUTER_FIRST_332.md'}
    statements = {
        'direction': 'Qualify safe native persistence and failed-proof blocking, without new artistic correction.',
        'learnings': '331 consumed initial plus two corrections and failed; stage chronology cannot be repaired retrospectively.',
        'film_language': 'Preserve accepted253 film and high quality floor; rejected320 is not an acceptable supporting actor.',
        'director_preferences': 'Do not ask Director to approve algorithms or repeatedly review predictable failures.',
        'references': '331 audit identifies schematic costume and unsupported pose family; use as rejected-control context, not a target.',
        'controls': 'Fresh knowledge obligations accompany source inventory; missing corpus coverage needs manual reconciliation.',
        'constraints': 'Canonical router and controller before native work; no quota renewal, arbitrary code or raw launcher.'}
    sources = [{'id': category, 'category': category, 'binding': bind(path), 'status': 'adopted',
                'required': True, 'statement': statements[category], 'scope': '334 qualification only'}
               for category, path in paths.items()]
    # Keep actual primary excerpts bounded rather than copying all historical policy.
    next(s for s in sources if s['id'] == 'film_language')['lines'] = [1, 27]
    next(s for s in sources if s['id'] == 'director_preferences')['lines'] = [1, 36]
    ids = ['preservation', 'persistence', 'visible_control', 'review_block']
    criteria = [
        'Original320 and accepted Pashtun hashes remain unchanged; no creative operations in recipe.',
        'Fresh-process reopened selected rig/object/camera state and scoped external dependencies match saved source evaluation.',
        'Actual diagnostic PNG decodes at540x960 and exposes the unchanged rejected horse/leader; no artistic pass inferred.',
        'No downstream launch after FAIL/NOT_RUN; actual native outputs, not substituted files, enter immutable review.']
    requirements = [{'id': rid, 'criterion': criterion, 'modes': ['image'] if rid == 'visible_control' else ['technical'],
                     'director_av': False} for rid, criterion in zip(ids, criteria)]
    ref = {'id': 'rejected320', 'role': 'negative_control', 'binding': bind(SOURCE),
           'authority': 'Director320/331 retained rejection;334 only qualifies no-edit handling.',
           'scope': 'Native horse/leader diagnostic frame327, not full-motion review.',
           'fidelity': 'Preserve native scene; do not improve or promote the negative control.',
           'allowed_variation': 'Diagnostic render resolution/samples/CPU engine, no saved creative changes.',
           'not_authority': 'Not an approved costume, pose, animation, portable bundle or universal state oracle.',
           'aspects': [{'id': 'retained_rejection', 'instruction': 'Keep the known bad scene rejected after native success.',
                        'requirements': ids}]}
    source_bindings = {k: bind(v) for k, v in paths.items()}
    source_bindings.update({p: bind(p) for p in [SOURCE, 'results/workflow334b/save-recipe.json',
        'results/workflow334b/render-recipe.json', 'src/movie_factory/adapters/blender/nihang_control.py',
        'src/movie_factory/adapters/blender/worker.py', 'scripts/workflow334b.py']})
    applicable = {'production_reuse': ids, 'camera_editorial': ['visible_control'],
                  'anatomy_contact': ['visible_control']}
    reasons = {
        'production_reuse': 'Must preserve original, bind dependencies, inspect new-process output and block propagation.',
        'camera_editorial': 'Actual source camera at327 must show the actor; a technical render is not a new approved look.',
        'anatomy_contact': 'Inspect schematic rider/horse forms as negative-control defects, not attempt new anatomical repair.',
        'story_performance': 'No changed performance or audience story beat in a no-edit handler control.',
        'animation_physics': 'No motion changed or qualified; selected frame state only, not temporal fluidity.',
        'effects_environment': 'Preserve source effects; do not claim simulation-cache portability from scoped file inventory.',
        'sound_music': 'No audio output or listening claim in a single-frame technical control.'}
    beats = [{'id': 'control', 'audience_read': 'No production-media promise: actual unchanged rejected scene stays rejected.',
              'framing': 'Original source camera at frame327;540x960 diagnostic, not final quality.',
              'lenses': {n: {'applies': n in applicable, 'why': reasons[n],
                             'requirements': applicable.get(n, [])} for n in ep.LENSES}}]
    methods = {
        'preservation': ('Hash parent before/after; fixed no-edit recipe and separate derivative.', 'Any parent change or creative operation.'),
        'persistence': ('Two owned Blender processes; save then reopen; compare selected matrices and external-file bindings.',
                        'Missing dependency, disabled script requirement or selected-state drift.'),
        'visible_control': ('Inspect actual PNG at source framing against retained rejection and shot-tier floor.',
                            'Missing/corrupt/blank image or promotion of schematic costume/horse as production-ready.'),
        'review_block': ('Record immutable FAIL against actual output; attempt dependent step and assert no worker/output.',
                         'Dependent process launches despite failed output review.')}
    realizations = {rid: {'beats': ['control'], 'lenses': [n for n, reqs in applicable.items() if rid in reqs],
        'derivation': criteria[ids.index(rid)], 'method': methods[rid][0],
        'interfaces': ['native source → saved derivative → fresh render → internal review → dependent step'],
        'early_proof': 'Source-preserving save/reopen control before any new character construction.',
        'failure_condition': methods[rid][1], 'reopen_when': 'Handler, source, recipe, dependency or requested use changes.',
        'priority': 'quality_floor', 'origin': 'craft_inference', 'reference_ids': ['rejected320']} for rid in ids}
    learning_application = {
        'reuse_envelope': 'Reuse controller/worker; qualify only no-edit persistence, not arbitrary authoring.',
        'authority': 'No new331 corrections, paid runtime, external calls or image/identity changes.',
        'strategy': 'First test native preservation, then fresh-process output, then failed-proof dependency block.',
        'visual_gate': 'Actual rejected-control PNG remains FAIL despite technical success.',
        'anticipation': 'Anticipate broken relative paths, disabled-driver dependencies and false positive visual promotion.',
        'stopping': 'Complete technical qualification or expose failure; no full sequence rendering of known defects.',
        'versioning': 'Bind original, recipes, handler bytes, outputs and known dependency hashes.',
        'economics': 'One serial native job per planned step; record time, no inferred percentage gain.',
        'retrieval': 'Manual330/328/331/332 reconciliation supplements finite pilot.',
        'current_state': '253 accepted protected;320/331 rejected;325 allowance exhausted.',
        'au_reuse': 'Fresh reopen not whole-project portable or remote backup; retain all failures.',
        'au_review': 'Technical output review and frame-visible rejection distinct from Director AV.'}
    mapping = {k: {'requirements': ids, 'reason': v} for k, v in learning_application.items()}
    intent = 'Qualify native persistence and review admission without new artistic construction.'
    protected = ['Accepted Pashtun253 exact bytes', 'Rejected320 source exact bytes', '331 closed attempts and325 exhausted calls']
    brief = {'schema': 1, 'route': 'production', 'intent': intent,
        'audience_result': 'No premature review: only evidence-backed output can advance; known rejected media stays internal.',
        'strategy': 'Validated fixed handler plus two fresh processes and a failed-review negative control.',
        'early_proof': 'No-edit selected native state and dependency preservation.', 'scope': '334 handler qualification',
        'exclusions': 'New animation/costume/character work, AV approval, cloud, spend and arbitrary scripts.',
        'open_decisions': [], 'offline_only': False, 'protected': protected, 'source_bindings': source_bindings,
        'knowledge_task': 'results/workflow334b/task.json', 'knowledge_digest': knowledge['packet_digest'],
        'knowledge_mapping': mapping, 'requirements': requirements,
        'capabilities': {m: m not in {'direct_audio', 'direct_motion'} for m in wf.rc.MODES},
        'references': [ref], 'reference_plan': {'rejected320': {'reference_digest': pk.digest(ref),
            'application': 'Preserve and render as a negative control, not a look or motion target.'}},
        'expert_plan': {'version': 1, 'beat_intents': {'control': intent}, 'beats': beats, 'realizations': realizations}}
    brief['expert_plan']['challenge'] = {'plan_digest': ep.plan_digest(brief), 'open_issues': [],
        'intent_coverage': {'control': {'reason': 'All four technical/negative-control requirements scoped; no artistic admission.', 'requirements': ids}},
        'cross_discipline_conflicts': 'Diagnostic CPU rendering may differ from source engine; no pixel replay or art success claim.',
        'omission_probe': 'Unpacked textures, disabled drivers, stale recipe and failed-dependency bypass are explicit risks.',
        'scope_tradeoff': 'Single frame only; temporal/portable-scene qualification deliberately excluded, not silently passed.'}
    direction = {'intent': intent, 'deliverable_id': 'workflow334b-native-handler-qualification',
        'references': [ref], 'protected': protected, 'beat_intents': {'control': intent},
        'knowledge_task': brief['knowledge_task'], 'knowledge_digest': brief['knowledge_digest'], 'context_sources': sources}
    old = c.state(TASK)
    for key in ('intent', 'deliverable_id', 'references', 'protected', 'beat_intents'):
        direction[key] = old['direction'][key]
    brief['references'] = direction['references']
    brief['reference_plan']['rejected320']['reference_digest'] = pk.digest(direction['references'][0])
    brief['expert_plan']['challenge']['plan_digest'] = ep.plan_digest(brief)
    c.recover_native_control(TASK, 'workflow334-recovery', direction,
        'Director334 recovery: inspect skipped text as data and simple driver validity; retain disabled execution and prior attempt.',
        'workflow334b-recover')
    context_mapping = {k: {'requirements': ids, 'reason': statements[k]} for k in paths}
    artifacts = {
        'GROUNDING': {'uses': {k: {'disposition': 'apply', 'reason': statements[k], 'implication': statements[k]} for k in paths},
            'knowledge_uses': learning_application, 'reconciliation': '334 strategy reconciles known unindexed330/328/331/332; pilot not universal memory.', 'unresolved': []},
        'DERIVING': {'requirements': requirements, 'beats': beats,
            'derivations': {k: {f: v[f] for f in pp.DERIVATION_FIELDS} for k, v in realizations.items()},
            'context_mapping': context_mapping, 'knowledge_mapping': mapping},
        'STRATEGIZING': {'brief': brief, 'method_choice': {
            'chosen': 'Fixed native no-edit handler, save followed by independently launched reopen/render.',
            'alternatives': 'Reject raw331 launcher and arbitrary scripts: bypass admission or transitive pinning. Mock-only is insufficient.',
            'evidence_status': 'hypothesis', 'discriminating_test': 'Selected state and dependencies survive new process and actual failed proof blocks next step.'},
            'steps': [{'id': 'save', 'depends_on': [], 'requirements': ['preservation', 'persistence'], 'kind': 'proof',
                'acceptance': 'Source unchanged, actual native and inventory returned; no missing dependencies.', 'native_recipe': bind('results/workflow334b/save-recipe.json')},
                {'id': 'reopen', 'depends_on': ['save'], 'requirements': ['persistence', 'visible_control'], 'kind': 'proof',
                 'acceptance': 'Fresh process selected state matches; actual image inspected; art rejection remains.', 'native_recipe': bind('results/workflow334b/render-recipe.json')},
                {'id': 'dependent', 'depends_on': ['reopen'], 'requirements': ['review_block'], 'kind': 'build',
                 'acceptance': 'Negative control: MUST NOT dispatch after failed image proof.', 'native_recipe': bind('results/workflow334b/render-recipe.json')}],
            'resource_scope': 'Local existing Blender only, one worker lease,600s process safety, no correction variants or paid calls.',
            'replan_triggers': 'Native preservation failure stops; deliberate artistic FAIL blocks propagation without reopening331.'}}
    for step in pp.STEPS[:3]:
        packet = c.packet(TASK)
        response = {'input_digest': packet['planning_input_digest'], 'outcome': 'complete', 'artifact': artifacts[step]}
        c.submit(TASK, packet['actor'], packet['ticket'], response, 'workflow334b-' + step)
        save(step.lower() + '.json', response)
    # Persist the fresh challenge input separately. The next invocation submits
    # its authored verdict after the main agent reads it; no automatic self-pass.
    challenge = c.packet(TASK)
    challenge.pop('ticket', None)
    save('challenge-input.json', challenge)
    print(json.dumps({'stage': c.state(TASK)['stage'], 'planning_step': c.state(TASK)['planning_step']}))


if __name__ == '__main__':
    {'prepare': prepare, 'plan': plan}[sys.argv[1] if len(sys.argv) > 1 else 'prepare']()
