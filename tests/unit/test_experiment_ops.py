from copy import deepcopy
from datetime import datetime, timedelta, timezone
import json
import sqlite3
import sys

import pytest

from movie_factory.experiment_ledger import Ledger, effective_events, summarize
from movie_factory.experiment_ops import build_report, demo_events, main
from movie_factory.engineering_usage import import_rollout, reconcile


def at(seconds):
    return (datetime(2026, 1, 1, tzinfo=timezone.utc)+timedelta(seconds=seconds)).isoformat()


def event(kind, t, **fields):
    return {'event_id': f'{kind}-{t}', 'experiment_id': 'X', 'episode_id': 'one',
            'event_type': kind, 'utc': at(t), 'phase': 'implementation', **fields}


def simple():
    return [event('start', 0), event('work_started', 0, activity_id='a', actor='assistant'),
            event('work_ended', 100, activity_id='a'), event('close', 100, disposition='YELLOW')]


def result(events):
    return summarize(events, 'X')['episodes'][0]


def test_acceptance_fixture_waits_and_overlapping_jobs():
    report = build_report(demo_events(), 'SIMULATED-OPS')
    episode = report['episodes'][0]
    assert episode['calendar_elapsed_seconds'] == 120*60
    assert episode['excluded_input_wait_seconds'] == 35*60
    assert episode['net_elapsed_seconds'] == 85*60
    assert episode['native_job_wall_sum_seconds'] == 15*60
    assert episode['native_job_wall_union_seconds'] == 10*60
    assert sum(episode['phase_net_seconds'].values()) == episode['net_elapsed_seconds']
    assert episode['human_review_seconds'] == 120
    assert report['engineering_usage']['status'] == 'UNKNOWN'
    assert report['factory_api']['known_api_cost_usd'] is None
    assert report['consumption_per_outcome']['closed_episodes']['net_seconds'] == 5100
    assert report['consumption_per_outcome']['closed_experiments']['net_seconds'] == 5100


@pytest.mark.parametrize('reason,excluded', [('director_response', 100), ('next_prompt', 100),
    ('user_pause', 100), ('provider_limit', 0), ('machine_failure', 0), ('infrastructure', 0)])
def test_wait_reasons(reason, excluded):
    e = [event('start', 0), event('wait_started', 0, wait_id='w', reason=reason),
         event('wait_ended', 100, wait_id='w'), event('close', 100, disposition='RED')]
    r = result(e)
    assert r['excluded_input_wait_seconds'] == excluded
    assert r['net_elapsed_seconds'] == 100-excluded


def test_background_assistant_work_keeps_question_time_in_net():
    e = simple()
    e[2:2] = [event('wait_started', 10, wait_id='w', reason='director_response'),
              event('wait_ended', 90, wait_id='w')]
    assert result(e)['excluded_input_wait_seconds'] == 0


def test_overlapping_waits_subtracted_once():
    e = [event('start', 0), event('wait_started', 0, wait_id='w1', reason='next_prompt'),
         event('wait_started', 20, wait_id='w2', reason='user_pause'),
         event('wait_ended', 80, wait_id='w1'), event('wait_ended', 100, wait_id='w2'),
         event('close', 100, disposition='GREEN')]
    assert result(e)['excluded_input_wait_seconds'] == 100


def test_unexplained_gap_and_crashed_work_not_inferred_wait():
    e = simple(); e[2]['utc'] = at(50)
    r = result(e)
    assert r['net_elapsed_seconds'] is None
    assert r['unknown_gap_seconds'] == 50
    assert r['coverage_fraction'] == .5
    e = simple(); del e[2]
    assert 'missing_interval_end' in result(e)['uncertainties']
    assert result(e)['net_elapsed_seconds'] is None


def test_open_episode_is_not_closed_or_exact():
    r = result(simple()[:-1])
    assert r['lifecycle'] == 'OPEN'
    assert r['net_elapsed_seconds'] is None


def test_clock_jump_invalidates_exact_time():
    e = [event('start', 0), event('job_started', 0, job_id='j', clock_id='c', monotonic_seconds=1),
         event('job_completed', 100, job_id='j', clock_id='c', monotonic_seconds=51),
         event('close', 100, disposition='RED')]
    r = result(e)
    assert r['native_job_wall_sum_seconds'] == 50
    assert r['net_elapsed_seconds'] is None
    assert 'clock_discontinuity' in r['uncertainties']
    e = simple(); e[2]['utc'] = at(-1)
    assert result(e)['net_elapsed_seconds'] is None


def test_reopened_episode_preserves_closed_outcome_and_overnight_gap():
    first = simple()
    second = [event('reopen', 10000, prior_episode_id='one'),
              event('work_started', 10000, activity_id='b'),
              event('work_ended', 10100, activity_id='b'), event('close', 10100, disposition='GREEN')]
    for e in second:
        e['episode_id'] = 'two'
    r = summarize(first+second, 'X')
    assert r['closed_episode_count'] == 2
    assert r['net_episode_sum_seconds'] == 200
    assert [e['disposition'] for e in r['episodes']] == ['YELLOW', 'GREEN']
    second[0]['prior_episode_id'] = 'missing'
    assert summarize(first+second, 'X')['net_episode_sum_seconds'] is None


def test_transaction_idempotency_correction_and_recovery(tmp_path):
    p = tmp_path/'ledger.sqlite3'
    ledger = Ledger(p)
    first = event('start', 0)
    assert ledger.append(first)
    assert not ledger.append(first)
    with pytest.raises(ValueError):
        ledger.append({**first, 'reason': 'different'})
    correction = {**first, 'event_id': 'corrected', 'supersedes': first['event_id'], 'reason': 'corrected'}
    ledger.append(correction)
    assert len(ledger.events()) == 2
    assert effective_events(ledger.events())[0]['reason'] == 'corrected'
    db = sqlite3.connect(p)
    db.execute('BEGIN IMMEDIATE')
    db.execute("INSERT INTO events(id,payload) VALUES ('interrupted','{}')")
    db.close()  # Simulates an uncommitted interrupted transaction.
    assert len(Ledger(p).events()) == 2
    with pytest.raises(ValueError):
        ledger.append({**correction, 'event_id': 'bad-branch'})


def usage(t, total, *, mode='incremental', **extra):
    return {'record_id': f'u-{t}', 'task_id': 't1', 'source': 'fixture-v1', 'utc': at(t),
            'mode': mode, 'stream_id': 't1', 'tokens': {'input_tokens': total-10,
            'output_tokens': 10, 'total_tokens': total, 'cached_input_tokens': 5,
            'reasoning_output_tokens': 5}, **extra}


def reconcile_fixture(records, **kwargs):
    return reconcile(records, task_ids=['t1'], start=at(0), end=at(100), **kwargs)


def test_incremental_duplicates_and_subsets_not_added():
    a = usage(1, 100)
    r = reconcile_fixture([a, a, usage(2, 200)], complete_capture=True)
    assert r['status'] == 'OBSERVED_SCOPE'
    assert r['observed_tokens']['total_tokens'] == 300
    assert r['observed_tokens']['cache_write_input_tokens'] is None
    assert r['actual_engineering_charge_usd'] is None


def test_conflicting_duplicate_cannot_claim_exact_usage():
    a = usage(1, 100); b = usage(1, 200)
    r = reconcile_fixture([a, b], complete_capture=True)
    assert r['exact_attributable_tokens'] is None
    assert 'conflicting_duplicate_usage' in r['uncertainties']


def test_cumulative_model_change_reset_and_missing_boundary():
    a, b = usage(0, 1000, mode='cumulative'), usage(20, 1500, mode='cumulative', model='other')
    assert reconcile_fixture([a, b], complete_capture=True)['observed_tokens']['total_tokens'] == 500
    r = reconcile_fixture([a, b, usage(40, 100, mode='cumulative'), usage(60, 150, mode='cumulative')])
    assert r['observed_tokens']['total_tokens'] == 550
    assert 'counter_reset_gap' in r['uncertainties']
    r = reconcile_fixture([usage(10, 5000, mode='cumulative'), usage(20, 5500, mode='cumulative')])
    assert r['observed_tokens']['total_tokens'] == 500
    assert 'missing_boundary_baseline' in r['uncertainties']


def test_shared_task_scope_inherited_history_and_missing_linked_task():
    records = [usage(-10, 9000), usage(0, 9000), usage(10, 100, response_id='inherited'), usage(20, 50), usage(101, 5000)]
    r = reconcile_fixture(records, inherited_response_ids=['inherited'])
    assert r['observed_tokens']['total_tokens'] == 50
    r = reconcile(records, task_ids=['t1', 't2'], start=at(0), end=at(100), complete_capture=True)
    assert r['status'] == 'PARTIAL'
    assert r['missing_tasks'] == ['t2']


def test_missing_fields_and_unsupported_source_unknown(tmp_path):
    a = usage(1, 100); a['tokens'] = {'output_tokens': 10}
    r = reconcile_fixture([a], complete_capture=True)
    assert r['observed_tokens']['input_tokens'] is None
    assert r['status'] == 'PARTIAL'
    assert reconcile_fixture([usage(1, 100, mode='unsupported')])['status'] == 'UNKNOWN'
    assert import_rollout(tmp_path/'absent', task_id='t1', start=at(0), end=at(100), installed_version='future')['status'] == 'UNKNOWN'
    assert import_rollout(tmp_path/'absent', task_id='t1', start=at(0), end=at(100), installed_version='0.153.4')['status'] == 'UNKNOWN'


def test_counter_epoch_resumed_stream_and_overlapping_source_are_partial():
    records = [usage(0, 100, mode='cumulative', counter_epoch='one'),
               usage(10, 200, mode='cumulative', counter_epoch='one'),
               usage(20, 300, mode='cumulative', counter_epoch='two'),
               usage(30, 400, mode='cumulative', counter_epoch='two')]
    r = reconcile_fixture(records, complete_capture=True)
    assert r['observed_tokens']['total_tokens'] == 200
    assert r['exact_attributable_tokens'] is None
    r = reconcile_fixture([usage(1, 100), usage(2, 900, source='second-copy')])
    assert r['observed_tokens']['total_tokens'] == 100
    assert 'overlapping_usage_sources_require_reconciliation' in r['uncertainties']


def test_partially_missing_subset_is_not_an_exact_category_total():
    a, b = usage(1, 100), usage(2, 100)
    b['tokens']['cached_input_tokens'] = None
    r = reconcile_fixture([a, b], complete_capture=True)
    assert r['observed_tokens']['cached_input_tokens'] == 5
    assert r['exact_attributable_tokens']['cached_input_tokens'] is None
    assert r['exact_attributable_tokens']['total_tokens'] == 200
    assert r['category_coverage']['cached_input_tokens'] == {'observed_blocks': 1, 'total_blocks': 2}


def test_pending_job_does_not_allow_human_wait_exclusion():
    e = [event('start', 0), event('wait_started', 0, wait_id='w', reason='director_response'),
         event('job_started', 0, job_id='j'), event('wait_ended', 100, wait_id='w'),
         event('close', 100, disposition='YELLOW')]
    r = result(e)
    assert r['observed_excluded_input_wait_seconds'] == 0
    assert r['excluded_input_wait_seconds'] is None


def test_emit_retries_are_idempotent_and_different_fields_fail(tmp_path):
    command = ['--ledger', str(tmp_path/'events.sqlite3'), 'emit', '--experiment', 'X',
               '--episode', 'one', '--type', 'start', '--id', 'start', '--phase', 'design']
    assert main(command) == 0
    assert main(command) == 0
    assert len(Ledger(tmp_path/'events.sqlite3').events()) == 1
    with pytest.raises(ValueError):
        main(command+['--fields', '{"reason":"changed"}'])


def test_usage_excludes_work_between_reopened_episodes():
    records = [usage(10, 100), usage(50, 9000), usage(80, 200)]
    r = reconcile_fixture(records, windows=[(at(0), at(20)), (at(70), at(100))])
    assert r['observed_tokens']['total_tokens'] == 300
    records = [usage(0, 1000, mode='cumulative'), usage(20, 1100, mode='cumulative'),
               usage(70, 9000, mode='cumulative'), usage(80, 9200, mode='cumulative')]
    r = reconcile_fixture(records, windows=[(at(0), at(20)), (at(70), at(100))])
    assert r['observed_tokens']['total_tokens'] == 300


def test_versioned_import_keeps_only_scoped_metadata(tmp_path):
    path = tmp_path/'rollout.jsonl'
    def raw(t, task, response):
        return {'timestamp': at(t), 'type': 'token_usage_record', 'payload': {
            'thread_id': task, 'turn_id': 'turn', 'response_id': response, 'usage': usage(t, 100)['tokens']}}
    rows = [{'timestamp': at(0), 'type': 'turn_context', 'payload': {'turn_id': 'turn', 'model': 'observed', 'effort': 'medium'}},
            {'timestamp': at(1), 'type': 'response_item', 'payload': {'text': 'PRIVATE-CONTENT'}},
            raw(-1, 't1', 'earlier'), raw(2, 'parent-task', 'inherited'), raw(3, 't1', 'new'), raw(3, 't1', 'new')]
    path.write_text('\n'.join(json.dumps(row) for row in rows)+'\n')
    imported = import_rollout(path, task_id='t1', start=at(0), end=at(100), installed_version='0.153.4')
    assert len(imported['records']) == 1
    assert imported['records'][0]['model'] == 'observed'
    assert imported['records'][0]['effort'] == 'medium'
    assert 'PRIVATE-CONTENT' not in json.dumps(imported)


def test_cli_demo_reports_and_monotonic_job_wrapper(tmp_path):
    assert main(['demo', '--output', str(tmp_path/'demo')]) == 0
    data = json.loads((tmp_path/'demo/summary.json').read_text())
    assert data['episodes'][0]['net_elapsed_seconds'] == 5100
    assert 'UNKNOWN' in (tmp_path/'demo/REPORT.md').read_text()
    ledger = tmp_path/'job.sqlite3'
    cmd = ['--ledger', str(ledger), 'job', '--experiment', 'X', '--episode', 'one',
           '--phase', 'test', '--id', 'one-job', '--', sys.executable, '-c', 'raise SystemExit(3)']
    assert main(cmd) == 3
    events = Ledger(ledger).events()
    assert events[-1]['outcome'] == 'FAILED'
    assert events[-1]['monotonic_seconds'] >= events[0]['monotonic_seconds']
    with pytest.raises(SystemExit):
        main(cmd)
