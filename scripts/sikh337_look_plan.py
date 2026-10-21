"""First authorized appearance correction: source-correct, bounded form proof.

Planning only. Native execution and actual image review remain separate.
"""
import copy
import json
from pathlib import Path
from movie_factory import production_workflow as wf, production_knowledge as pk
from movie_factory import planning_pipeline as pp, expert_planning as ep
from movie_factory.task_router import DATABASE

root = Path(__file__).resolve().parents[1]
out = root / 'results/sikh335/look01'
c = wf.Controller(root, DATABASE)
task = 'sikh335-supporting-appearance'

def bind(path):
    return {'path': path, 'sha256': pk.file_hash(root / path)}

def save(name, value):
    path = out / name
    if path.exists():
        raise RuntimeError('Do not overwrite planning history: ' + name)
    path.write_text(json.dumps(value, indent=2) + '\n')

state = c.state(task)
assert state['cycle'] == 1 and state['max_corrections'] == 4
assert state['planning_step'] == 'GROUNDING'
direction = state['direction']
art = {stage: pk.read_json(root, 'results/sikh335/look01/' + stage.lower() + '.json')['artifact']
       for stage in pp.STEPS[:3]}
brief = art['STRATEGIZING']['brief']
brief['references'] = copy.deepcopy(direction['references'])
assert next(r for r in brief['references'] if r['id'] == 'accepted_film')['role'] == 'accepted_quality'
brief['reference_plan'] = {r['id']: {'reference_digest': pk.digest(r),
                                  'application': r['aspects'][0]['instruction']}
                           for r in brief['references']}
parent = pk.read_json(root, 'results/sikh335/motion01/save-run-c5.json')['artifacts']['native']
brief['source_bindings'][parent['path']] = parent
for path in ('results/sikh335/look01/allowance-337.json',
             'results/sikh335/look01/reference-repair-receipt336.json',
             'results/sikh335/look01/REPLAN_DRAFT_336.md',
             'scripts/sikh337_look_plan.py'):
    brief['source_bindings'][path] = bind(path)

applications = copy.deepcopy(art['GROUNDING']['knowledge_uses'])
applications.update({
    'construction_interfaces': 'Use actual50k head,24k shirt and207 garment cache poses. First proof changes crown/clothing/pad, not donor anatomy; inspect sash/cuffs/seat in stance and crest before copies.',
    'look': 'Compare intended-frame cloth volume and material separation with the accepted Pashtun, not equal daylight pixel detail. Pillbox/cone turban, bodysuit shirt or hovering pad fail.',
    'visual_gate': 'Native save/reopen only proves persistence. Inspect all stance/crest/near-crowd renders; face/beard/horse finish and complete performance remain open regardless of this narrow proof.',
    'secondary': 'Current horse/rider motion changes the garment/tack fit. Use candidate5 as parent for appearance-only edits, and reopen contact if primary motion changes again.',
    'current_state': 'Director337 approves four appearance corrections while preserving prior failures. The still-role error is audited and repaired; no model/provider/spend or production acceptance follows.',
    'render_profile': 'Use three intended-camera540x960 images initially, serial after the motion render. No full-scene movie or same-film pass from a tiny crop.',
    'strategy': 'Test actual supported forms on leader and near actor before replication. The candidate construction is a hypothesis; analytic ridges can still fail as cloth.'})
preservation = {'authority', 'versioning', 'economics', 'cache_safety', 'current_state', 'stopping', 'au_reuse'}
form = {'look', 'au_surface', 'strategy', 'sikh_scope'}
evidence = {'visual_gate', 'anticipation', 'render_profile', 'au_performance', 'sikh_motion'}
mapping = {}
for key, reason in applications.items():
    required = ['preservation', 'evidence'] if key in preservation else (
        ['form', 'evidence'] if key in form else ['evidence', 'interfaces'] if key in evidence else ['interfaces', 'evidence'])
    mapping[key] = {'requirements': required, 'reason': reason}
brief['knowledge_mapping'] = mapping
art['DERIVING']['knowledge_mapping'] = mapping
art['GROUNDING']['knowledge_uses'] = applications
art['GROUNDING']['reconciliation'] = (
    'Director337 approved appearance max4 with existing failures retained. Accepted still now has its correct quality role, '
    'without altering the faithful rearing source. Current motion candidate5 replaces original320 as this appearance-only '
    'input; its narrow contact improvements do not qualify the whole performance. The two-actor form proof is an internal '
    'prerequisite, not the integrated exit: face/beard, horse finish, crowd performance and full excerpt remain required.')
art['GROUNDING']['uses']['references']['implication'] = 'Keep the faithful rearing clip for pose/contact interfaces and the accepted Pashtun still for same-film visual quality; no temporal claims about a still.'
art['GROUNDING']['uses']['constraints']['implication'] = 'Historical64 broken BBone target hazard is repaired in candidate5; preserve that repaired state and do not reintroduce old motion or claim general rig qualification.'

lens_plan = {
    'story_performance': (['form'], 'Layered Sikh cloth must read as worn by a person, not a generic cap and painted body. Face/beard remain an explicit subsequent appearance dependency.'),
    'camera_editorial': (['form', 'evidence'], 'Judge actual stance283, crest327 and near-crowd390 at intended framing; daylight close Pashtun is a quality comparator, not a pixel-density match.'),
    'animation_physics': (['interfaces'], 'Clothing must remain supported through the existing pose caches and current crest; static projection at rest cannot prove animated fit.'),
    'anatomy_contact': (['interfaces'], 'Preserve donor anatomy and cuffs; inspect neck/collar, sleeve/chest, sash/shirt, thigh/pad and pad/horse boundaries.'),
    'effects_environment': ([], 'No terrain, light or FX authoring in this form proof; retain the existing shot lighting so new geometry cannot be hidden by a relight.'),
    'sound_music': ([], 'This is an appearance prerequisite with no new timing or audio claim. Existing sound and final integrated AV remain outside this proof.'),
    'production_reuse': (['preservation', 'interfaces', 'evidence'], 'Preserve accepted originals and current motion; qualify leader and one near actor before any crowd propagation.')}
beat = brief['expert_plan']['beats'][0]
beat['lenses'] = {name: {'applies': bool(reqs), 'requirements': reqs, 'why': why}
                  for name, (reqs, why) in lens_plan.items()}
art['DERIVING']['beats'] = brief['expert_plan']['beats']
methods = {
    'preservation': ('Derive from candidate5, preserving original320 and accepted Pashtun. Check exact parent and source hashes plus all cache/key ownership before any image claim.', ['source native → derivative', 'unchanged motion → appearance proof']),
    'form': ('Use the reviewed fixed handler for a tapered continuous cloth winding, garment ease and waist-supported folds, plus body-surface saddle pad. This is a testable form hypothesis, not a claim of authentic cloth simulation.', ['crown → forehead/ear silhouette', 'shirt → belt/sash', 'pad → horse/seat']),
    'interfaces': ('Apply consistent garment changes to every existing cache pose; retain moving parents and refit outside layers. Inspect stance and crest for contact; reject if standing-only saddle projection fails under rise.', ['207 garment keys → sleeves/cuffs', 'moving torso → sash', 'horse pose → pad → rider thigh']),
    'evidence': ('Inspect all three actual images and source records against explicit counterexamples. Reject regular cap/cone ridges, embossed shirt folds or unsupported pad. Do not certify remaining face/beard/horse or full-speed motion.', ['actual framing → visible failure', 'phase proof → later continuous review'])}
for rid, (method, interfaces) in methods.items():
    realization = brief['expert_plan']['realizations'][rid]
    realization.update(lenses=[name for name, (reqs, _) in lens_plan.items() if rid in reqs],
                       method=method, interfaces=interfaces,
                       early_proof='Actual283 stance,327 crest and390 near-crowd frames plus preserved cache/ownership record; no propagation before inspection.',
                       failure_condition='Visible cap/cone rather than cloth, embossed/noisy bodysuit, changed anatomy, cache seam, sash penetration, hovering pad or false whole-package claim.',
                       reopen_when='Any primary motion, garment form, parent/contact owner, camera or material change.')
    art['DERIVING']['derivations'][rid] = {f: realization[f] for f in pp.DERIVATION_FIELDS}
brief['strategy'] = ('Source-correct two-actor form proof on current motion candidate5 using the existing reviewed supporting_look handler. '
    'Preserve all animated ownership; evaluate crown/garment/saddle construction before propagation or surface polish. '
    'This does not complete the face/beard, horse finish, crowd performance or integrated excerpt.')
brief['expert_plan']['challenge'].update(
    cross_discipline_conflicts='Torso ease changes sash contact; pad projection may fail in the crest; a stronger crown silhouette can still be an inauthentic cone. Actual shot images veto technically healthy output.',
    omission_probe='Three images are an early form rejection test, not a whole-character or motion pass. Explicitly retain face/beard, horse finish, moving crowd and continuous evidence as downstream requirements.',
    scope_tradeoff='Only leader and nearest crowd actor are changed initially. A failed form is not propagated. Existing dark-shot lighting is retained rather than hiding defects with relighting.')
brief['expert_plan']['challenge']['plan_digest'] = ep.plan_digest(brief)
art['STRATEGIZING']['method_choice'].update(chosen=brief['strategy'], evidence_status='hypothesis',
    alternatives='Do not add more subdivision/noise to the schematic forms or replicate an unreviewed actor. If continuous winding still looks like a cone, reassess cloth routing rather than adding ridges.',
    discriminating_test='Three actual-framing images expose the silhouette and pose-contact failure modes before propagation; compare against accepted-film integration, not previous rejected art.')
art['STRATEGIZING']['resource_scope'] = 'Appearance correction1/max4; one local source-preserving construction and three diagnostic images, serial after current motion render. No new spend, provider, install, principal changes or final AV claim.'
for stage in pp.STEPS[:3]:
    packet = c.packet(task)
    response = {'input_digest': packet['planning_input_digest'], 'outcome': 'complete', 'artifact': art[stage]}
    c.submit(task, packet['actor'], packet['ticket'], response, 'sikh337-look-c1-' + stage)
    save(stage.lower() + '-c1.json', response)
packet = c.packet(task)
packet.pop('ticket', None)
save('challenge-input-c1.json', packet)
print(json.dumps({k: c.state(task)[k] for k in ('task', 'stage', 'planning_step', 'cycle', 'max_corrections')}))
