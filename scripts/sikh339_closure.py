"""Preserve actual exhausted outcomes; a failing gate is the expected result."""
import json
from pathlib import Path
from movie_factory import production_knowledge as pk,production_workflow as wf
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];out=r/'results/sikh335/look01'
def write(path,data):
    p=r/path
    if p.exists():assert json.loads(p.read_text())==data
    else:p.write_text(json.dumps(data,indent=2)+'\n')
def bind(path):return {'path':path,'sha256':pk.file_hash(r/path)}
c=wf.Controller(r,DATABASE);s=c.state('sikh335-supporting-appearance')
assert s['stage']=='REPLAN_REQUIRED' and s['cycle']==s['max_corrections']==12
runs=[]
for n in range(9,13):
    run=pk.read_json(r,f'results/sikh335/look01/save-run-c{n}.json')
    status=pk.read_json(r,f'.runtime/factory-native/sikh339-look-c{n}-save/runner-status.json')
    assert run['status']=='FAILED' and not status['ok']
    runs.append({'cycle':n,'status':run['status'],'error':status['error'],
                 'process_seconds':status['elapsed'],
                 'receipt':bind(f'results/sikh335/look01/save-run-c{n}.json'),
                 'stderr':bind(f'.runtime/factory-native/sikh339-look-c{n}-save/stderr.log'),
                 'stdout':bind(f'.runtime/factory-native/sikh339-look-c{n}-save/stdout.log')})
exhaustion={k:s[k] for k in ('task','stage','cycle','max_corrections')}
exhaustion.update(artistic_pass=False,new_saved_candidates=0,attempts=runs,
                  native_process_seconds=sum(x['process_seconds'] for x in runs),
                  next_requires='Explicit additional same-task correction authority; no counter reset.',
                  limitation='Displacement guard failure does not establish what the unrendered cloth would look like.')
write('results/sikh335/look01/exhaustion-c12.json',exhaustion)
motion=pk.read_json(r,'results/sikh335/motion01/continuous-evidence-c9.json')
for b in [*motion['frames'].values(),motion['movie']]:assert pk.file_hash(r/b['path'])==b['sha256']
write('results/sikh335/motion01/evidence-verification339.json',{
 'frames_verified':len(motion['frames']),'movie':motion['movie'],
 'newly_inspected_frames':[294,307,350,390],
 'observation':'Actual timed images retain known schematic appearance.216x384 diagnostics cannot qualify surface fidelity or full-speed fluidity.',
 'motion_pass':False,'new_motion_correction':False,'director_av':'NOT_RUN'})
packet=pk.read_json(r,'.runtime/knowledge-pilot213/sikh339-current.json')
evidence=[bind('results/sikh335/look01/exhaustion-c12.json'),bind('results/sikh335/REASSESSMENT_339.md')]
checks=[]
for ob in packet['obligations']:
    status='FAIL' if ob['id'] in ('visual_gate','look','construction_interfaces','au_deformation') else 'NOT_RUN'
    checks.append({'id':ob['id'],'kind':ob['check_kind'],'status':status,
                   'action_taken':'Retained applicable obligation; blocked appearance delivery after failed native construction. No prior PASS is inherited.',
                   'observation':'Four attempts produced no saved candidate. The complete obligation is not qualified by code tests, source inspection or the earlier rejected images.',
                   'evidence':evidence})
review={'packet_digest':packet['packet_digest'],'checks':checks,
 'hypotheses':[{'prediction':'New sewn topology may remain unstable around the bent sleeve.',
                'observation':'Actual C12 solver exceeds displacement guard at raised elbow.',
                'response':'Preserve failure, stop at authorized limit, require discriminating rest/support proof before another construction trial.',
                'result':'unresolved'}],
 'adjacent_regressions':'No new saved native; accepted masters and motion candidate5 preserved. Face, headwear, sash, saddle and crowd appearance remain unqualified.',
 'stopping_reason':'Same appearance task exhausted12/max12. This is an authority blocker, not completion or an artistic review queue.'}
write('results/sikh335/look01/knowledge-review339.json',review)
gate=pk.check_review(r,packet,review)
assert not gate['ready_for_review']
write('results/sikh335/look01/knowledge-gate339.json',gate)
print(json.dumps({'stage':s['stage'],'attempts':len(runs),'new_candidates':0,
                  'process_seconds':exhaustion['native_process_seconds'],'motion_frames_verified':len(motion['frames']),
                  'knowledge_gate':'BLOCKED'}))
