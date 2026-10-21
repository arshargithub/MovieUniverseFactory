"""Export only completed stage judgments and safe runtime metadata; no inference."""
import json
from pathlib import Path
import sqlite3

from movie_factory import production_knowledge as pk
from movie_factory.production_workflow import Controller, Blocked
from movie_factory.staged_runner import SerialRunner

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/workflow324/live325-report'


def main():
    if OUT.exists(): raise ValueError('Preserve existing report')
    OUT.mkdir()
    c = Controller(ROOT, 'results/workflow324/live-controller.sqlite3')
    r = SerialRunner(c, 'results/workflow324/live-runner.sqlite3')
    stages = []
    with sqlite3.connect(r.database) as con:
        for actor, request, response in con.execute("SELECT actor,request,response FROM calls WHERE status='SUBMITTED' ORDER BY rowid"):
            request, response = json.loads(request), json.loads(response)
            stages.append({'actor': actor, 'runtime': response['runtime'],
                'context_bytes': len(json.dumps(request).encode()),
                'knowledge_digest': request['knowledge_context']['packet_digest'],
                'reference_ids': [x['id'] for x in request['direction']['references']],
                'reference_roles': {x['id']: x['role'] for x in request['direction']['references']},
                'builder_advocacy_present': 'builder_record' in request,
                'result': response['raw_result']})
    assert [s['actor'] for s in stages] == ['planner', 'builder', 'reviewer']
    assert len({s['runtime']['thread_id'] for s in stages}) == 3
    assert len({s['runtime']['turn_id'] for s in stages}) == 3
    assert len({s['knowledge_digest'] for s in stages}) == 1
    assert all(s['reference_roles'] == stages[0]['reference_roles'] for s in stages)
    assert not stages[-1]['builder_advocacy_present']
    assert len(r.calls()) == 4
    try:
        r.present('frozen-nihang324')
        raise AssertionError('Known rejection must not be presented')
    except Blocked as e: delivery_block = str(e)
    result = {'scope': 'Live serial frozen-evidence control path only',
              'call_reservations': r.calls(), 'completed_stages': stages,
              'events': c.events('frozen-nihang324'),
              'final_stage': c.state('frozen-nihang324')['stage'],
              'final_cycle': c.state('frozen-nihang324')['cycle'],
              'findings': c.state('frozen-nihang324')['findings'],
              'delivery_block': delivery_block, 'production_approved': False,
              'usage_complete': False, 'usage_gap': 'Aborted first attempt usage unavailable',
              'observed_completed_tokens': sum(s['runtime']['usage']['total']['totalTokens'] for s in stages),
              'code_bindings': {p: pk.file_hash(ROOT / p) for p in [
                  'src/movie_factory/staged_runner.py', 'src/movie_factory/production_workflow.py',
                  'scripts/workflow324_qualify.py']}}
    (OUT / 'trace.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ['scope','final_stage','final_cycle','delivery_block',
                                           'observed_completed_tokens','usage_complete']}))


if __name__ == '__main__': main()
