"""Resume original appearance task within Director380's existing allowance."""
import json,copy
from pathlib import Path
from movie_factory import production_workflow as w,production_knowledge as p,expert_planning as ep
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];o=r/'results/sikh380';c=w.Controller(r,DATABASE);task='sikh335-supporting-appearance';s=c.state(task);assert s['cycle']==143 and s['max_corrections']==146
cy=144

def bind(q):return dict(path=q,sha256=p.file_hash(r/q))
def write(n,v):
 q=o/n;t=json.dumps(v,indent=2)+'\n'
 if q.exists():assert q.read_text()==t
 else:q.write_text(t)
 return bind(str(q.relative_to(r)))
b=copy.deepcopy(s['brief']);src=copy.deepcopy(s['direction']['context_sources']);cfg=p.read_json(r,'results/sikh379/appearance-c143.json')
new=['results/sikh380/SWITCH.md','results/sikh380/APPROVAL.json','results/sikh380/STRATEGY.md','results/sikh379/RETROSPECTIVE379.md','results/sikh379/REJECT143.md','src/movie_factory/adapters/blender/nihang_chest380.py','src/movie_factory/adapters/blender/nihang_patch.py','tests/test_chest380.py','scripts/sikh380_plan.py','scripts/sikh380_replan.py']
for q in new:b['source_bindings'][q]=bind(q)
t=p.read_json(r,'results/sikh379/task143.json');t['id']='sikh380-native144';t['inputs'].update({q:p.file_hash(r/q) for q in new});write('task144.json',t);packet=p.task_packet(r,t);assert packet['dispatch_ready'],packet['blockers'];write('packet144.json',packet)
b.update(knowledge_task='results/sikh380/task144.json',knowledge_digest=packet['packet_digest'])
for row in src:
 if row['id']=='controls':row['binding']=bind('results/sikh380/task144.json');row['lines']=[1,11]
 b['source_bindings'][row['id']]=row['binding']
src.append(dict(id='director380',category='constraints',binding=bind('results/sikh380/SWITCH.md'),lines=[3,3],required=True,status='adopted',scope='144..146 chest only, main chat Astra High approved',statement='380 supersedes earlier no-Astra clauses only for exact remaining chest assignment. Same history/cap, no separate runtime calls or new spend.'))
b['source_bindings']['director380']=bind('results/sikh380/SWITCH.md');b['source_bindings']['results/sikh380/task144.json']=bind('results/sikh380/task144.json')
cause='Actual363 code and original375 matrices identify altered rest form plus stationary central pectoral ownership while humerus turns sharply. Earlier375 masked redistribution excluded central island. Test full bilateral pectoral transfer with raw rest restoration using live native B-bone evaluation; no ARAP or new action.'
b['expert_plan']['realizations']['form']['derivation']=cause;b['expert_plan']['challenge']['plan_digest']=ep.plan_digest(b);write('revised144-brief.json',b)
cfg.update(brief_path='results/sikh380/revised144-brief.json',cause=cause,method='380 restore measured historical raw/Basis delta and transfer whole bilateral pectoral influence to proximal humeri, including center; actual live rig, no pose cache or ARAP.',reconciliation='380 approved scoped Astra main-chat reassessment and reported switch supersede historical Sol-only text only within144..146. All earlier authority/history/quality retained. Unknown global307 remainsblocked,313 scoped correction applies.',alternatives='Restoration alone leaves stationary sag in source-matrix control; partial-mask ownership leaves midline island. Full transfer may over-gather and must be rejected if globular or pinched.',sources=list(dict.fromkeys(cfg['sources']+new)),retrospective_evidence=['results/sikh380/SWITCH.md','results/sikh380/APPROVAL.json','results/sikh380/STRATEGY.md','results/sikh379/RETROSPECTIVE379.md','results/sikh379/REFERENCE_QUALIFICATION.md'])
cfg['steps'][0]['recipe']['edits']=[{'kind':'mounted_horse_chest380','target':'horse'}]
write('appearance-c144.json',cfg)
ch=p.read_json(r,'results/sikh379/appearance-c143-challenge.json')
for q in ch['checks'].values():q['source_ids']+=['director380'];q['comparison']='380 scoped authority and fresh source ownership diagnosis against same gross anatomical references and fixed accepted motion.'
ch['checks']['method']['observation']=cause+' Plan is falsifiable; not an anatomical pass.'
ch['checks']['authority']['observation']='Explicit380approval + selectorconfirmation; same task144/max146, main chat only, no provider/new spend.'
ch['checks']['grounding']['observation']='379 references remain adequate for gross form;380 approved exception and actual inherited source diagnosis reconciled.'
ch['checks']['efficient_quality']['observation']='Five front frames first, no full render after a visible failure. Exact same native skeleton, source masters preserved.'
ch['strongest_counterexample']='The sternum should retain body support; full tissue transfer could over-gather into round lumps or collapse the neck-shoulder interface. Actual native front/reverse/side anatomy vetoes numerical ownership. Nap hidden is incomplete.'
write('appearance-c144-challenge.json',ch)
c.revise(task,b,bind('results/sikh380/SWITCH.md'),cause,'sikh380-replan144',grounding=dict(context_sources=src,reason='Reviewed exact380exception and new source/form/ownership method; no automatic repinning.',evidence={q:bind(q) for q in new}))
print('same task cycle',c.state(task)['cycle'])
