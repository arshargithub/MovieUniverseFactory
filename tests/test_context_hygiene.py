"""Finite routing/output contracts, not an artistic or token-savings benchmark."""
import copy
import json
from pathlib import Path
import shutil
import sys

import pytest
from movie_factory import context_hygiene as ch
from movie_factory import review_control as rc

REPO=Path(__file__).resolve().parents[1]


@pytest.fixture
def workspace(tmp_path):
    for name in ['docs/knowledge/context/rules.json','results/context311/AGENTS.before.md']:
        dst=tmp_path/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(REPO/name,dst)
    shutil.copyfile(REPO/'results/context311/AGENTS.proposed.md',tmp_path/'AGENTS.md')
    return tmp_path


def edit_catalog(root,fn):
    p=root/ch.CATALOG;data=json.loads(p.read_text());fn(data);p.write_text(json.dumps(data))


def test_all_original_paragraphs_preserved_with_core_or_routes(workspace):
    data,records=ch.load(workspace)
    assert len(records)==42
    core=(workspace/'AGENTS.md').read_text().lower().replace(' ','-')
    for r in records.values():
        for section in r['core_sections']:assert section in core
        assert r['topics'] or r['core_sections']


CASES=json.loads((REPO/'results/context311/routing-expectations.json').read_text())['cases']


@pytest.mark.parametrize('case',CASES,ids=lambda c:'+'.join(c['topics']))
def test_frozen_cross_discipline_expectations(workspace,case):
    result=ch.route(workspace,case['topics'])
    ids={r['id'] for r in result['rules']}
    assert set(case['required'])<=ids
    assert not set(case.get('forbidden',[]))&ids
    assert len(ids)==len(result['rules'])


@pytest.mark.parametrize('topics',[[],['everything'],['horse','unmapped'],['']])
def test_unknown_or_missing_topic_blocks(workspace,topics):
    with pytest.raises(rc.Blocked,match='UNKNOWN_TOPIC'):ch.route(workspace,topics)


def test_budget_never_silently_truncates_required_rules(workspace):
    with pytest.raises(rc.Blocked,match='EXCEEDS_BUDGET'):ch.route(workspace,['horse'],100)


@pytest.mark.parametrize('change',['source','core','rule','missing','mapping','invalid_dependency'])
def test_staleness_and_coverage_fail_closed(workspace,change):
    if change=='source':(workspace/'results/context311/AGENTS.before.md').write_text('changed')
    elif change=='core':(workspace/'AGENTS.md').write_text('changed')
    elif change=='rule':edit_catalog(workspace,lambda d:d['rules'][0].update(original_text='weaker'))
    elif change=='missing':edit_catalog(workspace,lambda d:d['rules'].pop())
    elif change=='mapping':edit_catalog(workspace,lambda d:d['topics']['knowledge']['rules'].remove('R01'))
    else:edit_catalog(workspace,lambda d:d['topics']['horse']['requires'].append('missing'))
    with pytest.raises((rc.Blocked,KeyError)):ch.route(workspace,['horse'])


def test_frozen_cases_detect_removed_adjacent_route(workspace):
    edit_catalog(workspace,lambda d:d['topics']['horse'].update(requires=[]))
    ids={r['id'] for r in ch.route(workspace,['horse'])['rules']}
    assert not set(CASES[0]['required'])<=ids


def test_warning_in_omitted_middle_surfaces(workspace):
    text='start\n'+('routine\n'*90)+'WARNING: hidden middle\n'+('routine\n'*90)+'end\n'
    (workspace/'large.log').write_text(text)
    result=ch.excerpt(workspace,'large.log',lines=2)
    assert result['omitted'] and result['signal_count']==1
    assert 'hidden middle' in result['signals'][0]['excerpt']
    assert (workspace/'large.log').read_text()==text
    assert ch.excerpt(workspace,'large.log',start=92,lines=1)['text'].startswith('WARNING')


def test_many_warnings_and_long_line_stay_bounded(workspace):
    (workspace/'large.log').write_text(('ERROR '+'x'*10000+'\n')*100)
    result=ch.excerpt(workspace,'large.log',chars=256)
    assert len(result['text'])==256 and result['omitted']
    assert result['signal_count']==100 and result['signals_omitted']
    assert len(result['signals'])==12
    assert len(json.dumps(result))<5000


@pytest.mark.parametrize('name',['.env','.env.backup','.aws/credentials','.git/config','../outside','/tmp/out'])
def test_private_and_escaping_paths_block(workspace,name):
    with pytest.raises(rc.Blocked):ch.safe(workspace,name)


def test_symlink_to_private_file_blocks(workspace):
    (workspace/'.env').write_text('DO_NOT_READ')
    (workspace/'alias.log').symlink_to(workspace/'.env')
    with pytest.raises(rc.Blocked):ch.excerpt(workspace,'alias.log')


def test_binary_read_blocks(workspace):
    (workspace/'binary.log').write_bytes(b'a\x00b')
    with pytest.raises(rc.Blocked):ch.excerpt(workspace,'binary.log')


def test_capture_preserves_exit_streams_and_omissions(workspace):
    code,r=ch.run(workspace,'failure',[sys.executable,'-c',
        'import sys; print("line\\n"*1000); print("ERROR test",file=sys.stderr); sys.exit(7)'])
    assert code==r['exit_code']==7 and r['stdout_summary']['omitted']
    assert r['stderr_summary']['signal_count']==1
    assert (workspace/r['stdout']).read_text().count('line')==1000
    assert (workspace/r['stderr']).read_text()=='ERROR test\n'
    with pytest.raises(FileExistsError):ch.run(workspace,'failure',[sys.executable,'-V'])


def test_capture_without_warnings_is_not_quality_pass(workspace):
    code,r=ch.run(workspace,'good',[sys.executable,'-c','print("hello")'])
    assert code==0 and 'ready_for_review' not in r and 'PASS' not in r


def test_cli_propagates_nonzero_exit(workspace,capsys):
    code=ch.main(['--root',str(workspace),'run','--label','cli','--',sys.executable,'-c','raise SystemExit(3)'])
    assert code==3 and json.loads(capsys.readouterr().out)['exit_code']==3


def test_metadata_has_no_log_bodies_and_repeats_not_tokens(workspace):
    (workspace/'x.log').write_text('BODY_NOT_IN_LEDGER')
    result=ch.excerpt(workspace,'x.log')
    for _ in range(2):ch.record(workspace,'read',result,'x.log')
    ledger=(workspace/ch.LOGS/'usage.jsonl').read_text()
    assert 'BODY_NOT_IN_LEDGER' not in ledger
    rows=[json.loads(line) for line in ledger.splitlines()]
    assert all(r['schema']==2 for r in rows)
    assert rows[0]['emitted_utf8_bytes']==len((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode())
    report=ch.usage(workspace)
    assert report['repeated_identical_reads']==1 and report['tokens'] is None and report['compactions'] is None


def test_current_reads_fresh_state_and_preserves_mode_limits(workspace,monkeypatch):
    p=workspace/'docs/planning/RELEASE_01_STATUS.json';p.parent.mkdir(parents=True)
    p.write_text(json.dumps({'outcome':'trailer','substantive_exchange_count':311,'next_checkpoint_exchange':320,'context_cleanup_311':'paused'}))
    state={'open_defects':[{'id':'D1'}],'protected':['accepted'],'fingerprint':'bound','capabilities':{'direct_motion':False}}
    monkeypatch.setattr(rc,'capsule',lambda root:copy.deepcopy(state))
    reg=workspace/rc.REGISTRY;reg.parent.mkdir(parents=True);reg.write_text('{}')
    result=ch.current(workspace)
    assert result['exchange']==311 and result['capabilities']['direct_motion'] is False
    p.write_text(p.read_text().replace('311','312'))
    assert ch.current(workspace)['exchange']==312
    updated=json.loads(p.read_text());updated['current_process']='awaiting media-review authority'
    p.write_text(json.dumps(updated))
    assert ch.current(workspace)['latest_process']=='awaiting media-review authority'
    def stale(root):raise rc.Blocked('STALE_BINDING')
    monkeypatch.setattr(rc,'capsule',stale)
    with pytest.raises(rc.Blocked):ch.current(workspace)
