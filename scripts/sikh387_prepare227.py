"""Build fresh grounded structural proof, no native dispatch or inferred verdict."""
import copy,json
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk,expert_planning as ep
r=Path(__file__).resolve().parents[1];o=r/'results/sikh387';c=wf.Controller(r,'.runtime/factory-entry.sqlite3');s=c.state('sikh335-supporting-appearance');assert s['cycle']==227
bind=lambda p:dict(path=p,sha256=pk.file_hash(r/p))
b=pk.read_json(r,'results/sikh386/revised226-brief.json');cfg=pk.read_json(r,'results/sikh386/appearance-c226.json')
for k,v in b['source_bindings'].items():
 if v['path'] in {'docs/knowledge/MICRO_APPEARANCE_WORKFLOW_386.md','scripts/sikh386_bind_source_review.py'}:b['source_bindings'][k]=bind(v['path'])
new=['results/sikh387/REQUEST.md','results/sikh387/APPROVED_ALLOWANCE.json','results/sikh387/STRATEGY.md','scripts/sikh387_prepare227.py','scripts/sikh387_plan.py','scripts/anatomy386_structural387.py','results/sikh386/CONTINUATION226.md']
for p in new:b['source_bindings'][p]=bind(p)
b['knowledge_task']=s['direction']['knowledge_task'];b['knowledge_digest']=s['direction']['knowledge_digest']
for row in s['direction']['context_sources']:b['source_bindings'][row['binding']['path']]=row['binding']
intent='Structural proof of coherent supported original-horse forequarter under approved rear, treating chest, shoulder attachment and local skin articulation together; first posed-strain experiment, no final-motion or coat claim.'
b['intent']=intent
unit=b['work_unit'];unit.update(id='horse-forequarter-structural387',primary_outcome=intent,phase='appearance_structural',cycle_window=[227,251],edit_kinds=['mounted_anatomy386_target','mounted_anatomy386_export'],allowed_domains=['chest_surface','shoulder_skin_mapping','diagnostic_camera','source_export'])
u=unit['scope_decision'];u.update(decision='merge',rationale='Prior50slotrun shows chest mass and shoulder insertion cannot be judged/repaired separately under fixed inherited skin deformation.',independent_judgment='Connected forequarter form can be judged without coat, leader or terrain.',coupled_context='Both shoulders, proximalforelegs, lowerneck, thorax and wholehorse remain visible.',worst_proof='339opposite/side/front before dense cache',integration_proof='Densehalf-frame anatomy plus original performance/contacts and film-material integration after positive static form.',allowance_binding=bind('results/sikh387/APPROVED_ALLOWANCE.json'))
u['considered_outcomes']=[dict(id='structural',disposition='current',criterion='Connected natural forequarter across neutral and raised poses',reason='Chest/roots are necessary coupled form.'),dict(id='finish',disposition='deferred',criterion='Nap/tack and film material',reason='Do not conceal unpassed structure.')]
unit['causal_experiment'].update(unknown='Is differential posed skin strain the main shelf cause?',hypothesis='Preserve neutral surface edge geometry under actual posed boundaries instead of fitting an already distorted source surface.',method_family='posed_surface_local_global_arap',discriminator='Same neutral raw mesh, accepted skeleton/actual exterior and distal surfaces, nonlinear local rigid edge solve; unlike215neutral guide fit, operate on339posed region.',success_prediction='Supported chest/roots without shelf, bulb, web or flattened volume in actual339native views.',failure_prediction='Persistent shelf, collapse or skin membrane rejects the method, even with lower edge strain.',failure_response='Reject actual native proof and reassess geometry/shoulder articulation, not more amplitude sweeps.')
for req in b['requirements']:
 if req['id']=='form':req['criterion']='Supported coherent chest and shoulder/neck/upperforeleg origins in283333339; no shelf, pendant bib, skinweb or collapse. Static numeric targets do not qualify fluidity.'
for m in b['expert_plan']['realizations'].values():m.update(method='Source-bound posed elastic reconstruction of connected forequarter; native worst-view proof before dense solve.',early_proof='Three diagnostic poses only; neutral and rigidtransform controls; native339front/side/opposite veto.',failure_condition='Numeric success cannot pass shape. Any unsupported contour, collapse, changed hoof/action or missing evidence remains internal FAIL.')
b['expert_plan']['beat_intents']['torso']=intent;b['expert_plan']['beats'][0]['audience_read']=intent
b['expert_plan']['challenge']['plan_digest']=ep.plan_digest(b)
(o/'revised227-brief.json').write_text(json.dumps(b,indent=2)+'\n')
cfg.update(brief_path='results/sikh387/revised227-brief.json',method='Posed local-global ARAP structural compatibility experiment; actual original native source and fixed skeletal/boundary positions.',proof='Source ownership and strain audit plus neutral/rigidtransform numerical controls, then three actual posed targets for later native proof. This227numeric prerequisite cannot pass artistic form.',scope=intent,failure='Unstable/nonfinite, protected exterior changes or poor native form reject; no artPASS from strainmetrics.',alternatives='Neutral guideARAP215 and localrigidity/smoothing failed; posed elasticity tests a distinct strain hypothesis. Local articulation/topology reconstruction remains next if falsified.',reconciliation='Director387adds25shared corrections227..251. Previous226artFAILretained; two reviewed closure sources reconciled. Merge chest/shoulder necessary coupling; numeric prerequisite first.',sources=new,evidence_status='hypothesis')
for row in s['direction']['context_sources']:
 old=cfg['context_application'].get(row['id'],dict(disposition='apply',reason=row['statement'],requirements=['form','interfaces','evidence','whole_look']))
 old['implication']='Apply387structural strategy, original reference roles and failure history; no source-preservation or bookkeeping success substitutes for connected native anatomy.';cfg['context_application'][row['id']]=old
inputs=[bind('.runtime/factory-native/sikh386-appearance-c193-source/anatomy386-source.npz')]
cfg['steps']=[dict(id='numeric_volume',kind='proof',depends_on=[],requirements=[q['id'] for q in b['requirements']],acceptance=cfg['proof'],script=bind('scripts/anatomy386_structural387.py'),numeric_inputs=inputs)]
(o/'appearance-c227.json').write_text(json.dumps(cfg,indent=2)+'\n')
wf.validate_brief(r,b,'production',s['mode']);print('227fresh brief validated')
