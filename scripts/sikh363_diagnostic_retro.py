"""Admit continued independent diagnosis, not production repair or closure."""
import sys
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,DATABASE);task='sikh335-supporting-appearance';s=c.state(task);tag=sys.argv[1]
def bind(p):return dict(path=p,sha256=pk.file_hash(r/p))
ev={p:bind(p) for p in ['results/sikh363/REQUEST.md','results/sikh363/STRATEGY.md','results/sikh363/appearance-c101-chest-review.json']}
for key,g in c.retrospective_packet(task)['gates'].items():
 if g['status']!='OPEN':continue
 response=dict(cause='Actual chest diagnostic confirms the Director-visible bilateral pectoral protrusion; no correction has been attempted. Availability is not art PASS.',uncertainty='Need side and hand crops to distinguish rest geometry from corrective/deformation and diagnose finger pivots.',change_or_retain_rationale='Continue only independent already-planned read-only diagnostics, no artistic successor or whole appearance approval.',preserve='Exact99 source, original scope/history/limits and known363 failures.',test='Complete side chest and both hand images, then replan construction based on actual cause.',expected='Known defects remain failed while method is selected from actual observations.',failure_response='Replan affected source or handler if diagnostic coverage fails; do not hide visible defects or seek routine Director gate.',target_stage='GROUNDING',plan=pk.digest(s['brief']),gate_digest=pk.digest(g),evidence=ev)
 event='sikh363-diagnostic-'+tag+'-'+key;c.retrospective(task,'response',dict(key=key,response=response),event)
 ch=dict(response_event=event,counterexample='A diagnostic PASS or successful image can conceal unchanged failed anatomy; no downstream construction or handoff under this response.',evidence=ev,checks={k:dict(status='PASS',observation=v) for k,v in dict(causal_test=response['test'],actual_method=response['change_or_retain_rationale'],preservation=response['preserve'],authority=f'Original{s["cycle"]}/max{s["max_corrections"]}, only planned diagnosis, no additional authority.').items()})
 c.retrospective(task,'admit',dict(key=key,challenge=ch),event+'-admit')
print('Diagnostic continuation only, artistic failures retained.')
