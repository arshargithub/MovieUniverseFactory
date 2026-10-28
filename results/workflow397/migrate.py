"""Reviewed397 idle-boundary administrative migration; no production dispatch."""
import json,sqlite3
from pathlib import Path
from movie_factory import production_workflow as wf,production_governance as g,production_knowledge as pk,context_hygiene as ch
root=Path.cwd();c=wf.Controller(root,'.runtime/factory-entry.sqlite3')
def bind(path):return dict(path=path,sha256=pk.file_hash(root/path))
a=bind('results/workflow397/REQUEST.md');before=json.loads((root/'results/workflow397/PRE_MIGRATION_STATE.json').read_text())
with c.connect() as con:
 assert not con.execute('SELECT 1 FROM heavy_job').fetchone()
 native_before=con.execute('SELECT count(*) FROM native_runs').fetchone()[0]
for task,old in before.items():
 st=c.state(task);assert pk.digest(st)==pk.digest(old),(task,'STATE_CHANGED_BEFORE_MIGRATION')
# Zero prospective authority: total film investment envelope is not invented.
for ident,kind,parent,purpose in [
 ('release01','release',None,'Trailer and episodes1and2; global envelope remains unresolved'),
 ('trailer01','milestone','release01','Trailer completion, distinct from consumed effort'),
 ('nihang-form','capability','trailer01','Continuous credible horse form under accepted rear'),
 ('inherited-anatomy-crafting','family','nihang-form','Original inherited-horse anatomy crafting'),
 ('nihang-motion','capability','trailer01','Reference-grounded rearing performance'),
 ('accepted-motion-preservation','family','nihang-motion','Preserve accepted micro-motion66/75/80')]:
 c.governance('sikh335-supporting-appearance','node',dict(id=ident,kind=kind,parent=parent,limit=0,purpose=purpose,authority=a),'397-node-'+ident)
for task,node,features,ages in [
 ('sikh335-supporting-appearance','inherited-anatomy-crafting',['continuous-forequarter-form'],{'continuous-forequarter-form':50}),
 ('sikh335-continuous-performance','accepted-motion-preservation',['rearing-performance'],{'rearing-performance':0})]:
 st=c.state(task)
 record=dict(task=task,state_digest=pk.digest(st),authority=a,baseline_slots=st['cycle'],original_limit=st['max_corrections'],
   features=features,historical_age=ages,history_evidence={'audit':bind('results/sikh391/AUDIT.md'),'state':bind('results/workflow397/PRE_MIGRATION_STATE.json')},
   unknowns=['Not a whole-project cycle census. Accepted micro-motion evidence does not prove integrated anatomy or Director AV.'],
   profile=g.DEFAULTS,node=node,remaining_allocation=0)
 c.governance(task,'migrate',record,'397-migrate-'+task)
 c.migrate_retrospective(task,a,dict(state_digest=pk.digest(c.state(task)),coverage=['Full original events preserved; cached/full replay matched on5127appearance and2309motion events.','Original counters, maxima, failed findings and accepted native masters preserved.'],unknowns=['No continuous anatomy pass. Historical whole-project net effort incomplete. New planning/native engine admission not automatically refreshed.'],evidence={'calibration':bind('results/workflow397/HISTORICAL_CALIBRATION.json'),'audit':bind('results/sikh391/AUDIT.md')}),'397-retro-'+task)
c.governance('sikh335-supporting-appearance','retire',dict(node='inherited-anatomy-crafting',reason='At least50historical cycles with zero positive chest image proof; practical no-progress stop, retain evidence and alternate-method decision.',authority=a),'397-retire-inherited')
protected=json.loads((root/'results/sikh391/PROTECTED_MASTERS_VERIFY.json').read_text())
for k,v in protected.items():assert pk.file_hash(root/v['path'])==v['expected'],k
out={'tasks':{},'protected':{k:bind(v['path']) for k,v in protected.items()},'no_new_native_jobs':True}
for task,old in before.items():
 now=c.state(task)
 for field in ['cycle','max_corrections','stage','fingerprint']:assert now[field]==old[field],(task,field)
 assert c.governance_status(task)==c.governance_status(task,full=True)
 out['tasks'][task]=dict(before={k:old[k] for k in ['cycle','max_corrections','stage','fingerprint']},after={k:now[k] for k in ['cycle','max_corrections','stage','fingerprint']},governance=c.governance_status(task))
with c.connect() as con:
 assert con.execute('SELECT count(*) FROM native_runs').fetchone()[0]==native_before
 assert not con.execute('SELECT 1 FROM heavy_job').fetchone()
out['native_runs']=native_before
(root/'results/workflow397/MIGRATION_VERIFICATION.json').write_text(json.dumps(out,indent=2)+'\n')
adoption=dict(schema=1,database='.runtime/factory-entry.sqlite3',tasks=list(before),sources={'authority':a,'workflow':bind('docs/knowledge/GOVERNANCE_WORKFLOW_397.md')},protected=out['protected'])
(root/'docs/knowledge/context/current397.json').write_text(json.dumps(adoption,indent=2)+'\n')
actual=ch.current(root);assert actual['governance']['sikh335-supporting-appearance']['decision']=='STOP_AND_REALLOCATE'
(root/'results/workflow397/CURRENT_CAPSULE.json').write_text(json.dumps(actual,indent=2)+'\n')
print(json.dumps({t:v['governance']['decision'] for t,v in out['tasks'].items()}))
