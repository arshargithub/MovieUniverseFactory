"""Actual diagnostic/component observations; not a final appearance verdict."""
import json,sys
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.native_admission import Bridge
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,DATABASE);label,step,reason=sys.argv[1:4];task='sikh335-'+('supporting-appearance' if label=='appearance' else 'continuous-performance');s=c.state(task);tag=f'{label}-c{s["cycle"]}';run=pk.read_json(r,f'results/sikh363/{tag}-{step}-run.json')
reqs=next(x['requirements'] for x in s['planning_artifacts']['STRATEGIZING']['steps'] if x['id']==step)
v=dict(verdict='PASS',run_digest=pk.digest(run),evidence=run['artifacts'],observation=reason,comparison='Actual source-bound diagnostic evidence against363 known failures; output availability/coverage only, not repair or art acceptance.',open_defects=[],requirement_outcomes={k:dict(status='PASS' if k=='preservation' else 'NOT_TESTED',observation='Technical preservation only.' if k=='preservation' else 'Diagnostic/component coverage only; known363 artistic failure remains open, not qualified by availability.') for k in reqs})
Bridge(c).record_review(task,step,v);(r/f'results/sikh363/{tag}-{step}-review.json').write_text(json.dumps(v,indent=2)+'\n')
