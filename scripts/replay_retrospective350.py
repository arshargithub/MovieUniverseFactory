"""Frozen-history policy rehearsal, no native or provider dispatch.

Classifications are human-readable, agent-authored with hindsight. This tests
what the policy does with them, not whether an LLM would discover them.
"""
import argparse
import json
from pathlib import Path
from movie_factory import retrospective as rt, production_knowledge as pk


def replay(root):
    spec=pk.read_json(root,'results/workflow350/replay-cases.json')
    rows=[]
    for case in spec['cases']:
        sources={p:pk.file_hash(root/p) for p in case['sources']}
        observations=[dict(o,observation=case['reason']) for o in case['observations']]
        history=[dict(id='policy',kind='initialize',data=dict(version=rt.VERSION,engine=rt.engine())),
                 dict(id=case['id'],kind='outcome',data=dict(attempt=case['id'],role=case.get('role','production'),
                     origin='frozen_history_classification',observations=observations,evidence=sources))]
        projected=rt.project(history)
        actual=sorted(k for k,g in projected['gates'].items() if g['status']=='OPEN')
        rows.append(dict(id=case['id'],sources=sources,observations=observations,
                         expected=sorted(case['expected_open']),actual=actual,
                         passed=actual==sorted(case['expected_open']),gates=projected['gates']))
    return dict(policy_version=rt.VERSION,engine=rt.engine(),case_spec_sha256=pk.file_hash(root/'results/workflow350/replay-cases.json'),
                scope=spec['status'],no_native_or_provider_calls=True,cases=rows,passed=all(r['passed'] for r in rows),
                semantic_limit='A false PASS without failure flags still evades the trigger. Dedicated regression retains this counterexample. No Director-input savings measured.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    result=replay(root)
    output=(root/args.output).resolve()
    output.relative_to(root/'results/workflow350')
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('x') as stream:json.dump(result,stream,indent=2);stream.write('\n')
    print(json.dumps(dict(passed=result['passed'],cases=len(result['cases']),output=str(output))))
    return 0 if result['passed'] else 2


if __name__=='__main__':raise SystemExit(main())
