"""Actual phase4 review and affected-stage rider/neck repair, same counter."""
import json
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.native_admission import Bridge
from movie_factory.task_router import DATABASE
root=Path(__file__).resolve().parents[1];out=root/'results/sikh335/motion01'
c=wf.Controller(root,DATABASE);task='sikh335-continuous-performance'
run=pk.read_json(root,'results/sikh335/motion01/render-run-c4.json')
v={'verdict':'FAIL','run_digest':pk.digest(run),'evidence':run['artifacts'],
   'observation':'All13 actual images inspected. Preparation301 has a perceptible head dip;349 has no premature landing burst,353/355 show post-contact debris. Crest327/338 still has a long straight-looking neck and rider leans backward as one upper-body block. Crowd357 remains schematic and unqualified.',
   'comparison':'Reference load/lift is clearer but crest rider remains nearer upright in source; root pitch plus negative upper-body pitch compounds backward inclination. Neck control ownership must exclude inherited head translation and report actual chain lengths before any structural-stretch claim.',
   'open_defects':['Rider counterbalance and absorption remain weak','Neck crest silhouette requires ownership and length control','Supporting appearance and crowd performance unqualified','Full-speed AV NOT_RUN']}
Bridge(c).record_review(task,'render',v)
(out/'render-review-c4.json').write_text(json.dumps(v,indent=2)+'\n')
(out/'replan-source-c5.json').write_text(json.dumps(c.state(task)['planning_artifacts'],indent=2)+'\n')
c.replan(task,'DERIVING','Keep fixed hoof support and contactFX. Correct compounded backward rider pitch with load-related counterbalance and post-impact absorption; explicitly resolve neck/head position ownership and measure deformation instead of claiming stretching from silhouette alone.','sikh336-coupled-rider-replan')
print({k:c.state(task)[k] for k in ('stage','planning_step','cycle','max_corrections')})
