import importlib.util
from pathlib import Path

spec=importlib.util.spec_from_file_location('audit250',Path(__file__).resolve().parents[2]/'scripts/audit250_metrics.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def test_union_does_not_double_count_background_work():
    assert m.seconds([(0,10),(5,15),(20,25)])==20

def test_director_wait_excluded_but_continuing_job_retained():
    tasks=[(0,10),(30,40)];jobs=[(8,20)]
    assert m.seconds(tasks+jobs)==30
    assert m.seconds(m.subtract(jobs,tasks))==10

def test_clip_open_task_at_cutoff():
    assert m.clip([(0,50)],10,20)==[(10,20)]

def test_subtract_split_and_overlap():
    assert m.subtract([(0,20)],[(2,5),(4,8),(15,30)])==[(0,2),(8,15)]

def test_invalid_or_zero_interval_is_not_effort():
    assert m.seconds([(4,4),(5,2)])==0

def test_superseded_job_end_not_double_counted():
    common={'experiment_id':'e','episode_id':'p','job_id':'j'}
    events=[dict(common,event_id='a',event_type='job_started'),dict(common,event_id='b',event_type='job_completed'),dict(common,event_id='c',event_type='job_completed',supersedes='b')]
    pairs,open_,orphans=m.paired_events(events,'job_started','job_completed','job_id')
    assert len(pairs)==1 and pairs[0][1]['event_id']=='c'
    assert not open_ and not orphans

def test_orphan_is_visible_not_bridged():
    e={'experiment_id':'e','episode_id':'p','job_id':'j','event_id':'z','event_type':'job_completed'}
    pairs,open_,orphans=m.paired_events([e],'job_started','job_completed','job_id')
    assert not pairs and not open_ and orphans==[e]

def test_explicit_case_coverage_and_handoff_dedup():
    import json
    path=Path(__file__).resolve().parents[2]/'docs/knowledge/PASHTUN_PRODUCTION_AUDIT250_CASES.json'
    d=json.loads(path.read_text());r=d['cases']
    assert [x['case'] for x in r]==list(range(1,293))
    assert len({x['message_id'] for x in r})==292
    assert all(x['labels'] and x['reason'] and x['lesson'] for x in r)
    assert sum('system_handoff' in x['labels'] for x in r)==1
    h=[x for x in r if x['avoidable_final_id']]
    assert len(h)==len({x['avoidable_final_id'] for x in h})==44
    assert all(x['fresh_final_since_prior_input'] for x in h)

def test_portable_baseline_reconciles_counts_and_scope():
    import json
    root=Path(__file__).resolve().parents[2]
    d=json.loads((root/'docs/knowledge/PASHTUN_PRODUCTION_AUDIT250_METRICS.json').read_text())
    assert sum(s['human_inputs'] for s in d['stages'])==d['classification']['human_inputs']==291
    p=d['profiles']['shared_visual_development']
    assert p['completed_turns']+p['aborted_turns']+p['open_turns']==266
    assert sum(p['native_outcomes'].values())==p['native_matched_jobs']==1501
    assert p['native_outcomes']['RUNNING_AT_CUTOFF']==1
    assert abs(p['observed_task_active_union_seconds']+p['native_outside_tasks_seconds']-p['task_or_native_union_seconds'])<0.001
    assert p['native_sum_seconds']>=p['native_union_seconds']
    assert d['status']=='HISTORICAL_SNAPSHOT_NOT_SEQUENCE_CLOSURE'

def test_classification_rates_are_not_additive_defect_counts():
    import json
    root=Path(__file__).resolve().parents[2]
    d=json.loads((root/'docs/knowledge/PASHTUN_PRODUCTION_AUDIT250_CASES.json').read_text())
    repeated={r['case'] for r in d['cases'] if 'repeated_correction' in r['labels']}
    defects={r['case'] for r in d['cases'] if 'defect_or_missed_requirement' in r['labels']}
    assert len(repeated)==58 and len(defects)==93 and repeated<=defects
    assert sum(d['counts'].values())>len(d['cases'])
