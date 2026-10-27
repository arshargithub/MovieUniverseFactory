"""Record explicitly supplied technical outcome; no native/art verdict invented."""
import json,sys
from pathlib import Path
from movie_factory import production_workflow as w,production_knowledge as p
r=Path(__file__).resolve().parents[1];c=w.Controller(r,'.runtime/factory-entry.sqlite3');t='sikh335-supporting-appearance';s=c.state(t);f=sys.argv[1];x=p.read_json(r,f);assert x['cycle']==s['cycle']
bind=lambda q:dict(path=q,sha256=p.file_hash(r/q));ev={q:bind(q) for q in [f]+x['evidence']};pending=c.retrospective_packet(t)['pending_effects386'];keys={v['key'] for v in pending.values()};assert keys<=x['statuses'].keys();oid=f'sikh386-c{s["cycle"]}-diagnostic-outcome'
c.retrospective(t,'outcome',dict(attempt=oid,role='diagnostic',origin='actual_technical_or_numeric_control',observations=[dict(requirement=k,status=x['statuses'][k],observation=x['observation']) for k in keys],evidence=ev),oid)
for aid,v in pending.items():
 status=x['statuses'][v['key']];result={'FAIL':'ineffective','UNKNOWN':'inconclusive','PASS':'effective'}[status]
 c.retrospective(t,'evaluate',dict(key=v['key'],evaluation=dict(admission_event=aid,result=result,outcome_event=oid,observation=x['observation'],evidence=ev)),aid+'-diagnostic-effect')
(r/f'results/sikh386/CYCLE{s["cycle"]}_CLOSEOUT.json').write_text(json.dumps(dict(x,max=s['max_corrections']),indent=2)+'\n');print('Closed',s['cycle'],'remaining',s['max_corrections']-s['cycle'])
