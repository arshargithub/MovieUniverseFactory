"""Repair an inherited derivation omission without rebuilding good geometry."""
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,DATABASE);task='sikh335-supporting-appearance';s=c.state(task)
assert s['cycle']==99 and s['stage']=='EXECUTING'
path='results/sikh362/STATIC_REVIEW99.md'
c.retrospective(task,'outcome',dict(attempt='362-scope-completeness',role='diagnostic',origin='original-intent-completeness-review',observations=[dict(requirement='__planning__',status='FAIL',observation='Inherited67 derivation still describes only garment/interface proof and leaves head/beard/horse surface open, although current scope and actual99 evidence cover the integrated leader/horse. Add an explicit whole-look requirement before final controller review; preserve actual good native/media rather than rebuild.',foundation=False)],evidence={'actual_static_scope':dict(path=path,sha256=pk.file_hash(r/path))}),'sikh362-whole-look-planning-gap')
s=c.replan(task,'DERIVING','Retain grounded authority and actual99 derivative/controls; explicitly derive whole head/beard/horse surface and same-film requirement for the current integrated goal. Crowd stays deferred, full-speed AV remains Director313. Qualification repair only; no new identity/style or geometry.','sikh362-scope-derivation-repair')
assert s['cycle']==100 and s['max_corrections']==107
print(s['cycle'],s['planning_step'])
