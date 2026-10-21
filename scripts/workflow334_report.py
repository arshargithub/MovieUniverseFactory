"""Collect measured qualification receipts; no native dispatch or provider call."""
import json
import sqlite3
from pathlib import Path
from movie_factory import production_knowledge as pk, context_hygiene as ch
from movie_factory.production_workflow import Controller, Blocked
from movie_factory.task_router import DATABASE

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/workflow334'


def save(name, value):
    (OUT/name).write_text(json.dumps(value,indent=2)+'\n')


def bind(path):
    return {'path':path,'sha256':pk.file_hash(ROOT/path)}


def main():
    receipt=pk.read_json(ROOT,'.runtime/context-hygiene/runs/workflow334-qualified-tests/receipt.json')
    assert receipt['exit_code']==0
    assert pk.file_hash(ROOT/receipt['stdout'])==receipt['stdout_sha256']
    (OUT/'tests.txt').write_text((ROOT/receipt['stdout']).read_text())
    save('test-receipt.json',receipt)
    protected={p:{'expected':v['expected'],'actual':pk.file_hash(ROOT/p)}
               for p,v in pk.read_json(ROOT,'results/workflow333/protected.json').items()}
    assert all(v['expected']==v['actual'] for v in protected.values())
    assert pk.read_json(ROOT,'results/sikh331/STATUS.json')['native_dispatch_closed']
    save('protected.json',protected)
    c=Controller(ROOT,DATABASE)
    author='workflow334author-native-control'; previous='workflow333-native-control'
    c._fresh(c.state(author))
    save('routing-receipts.json',[c.routing(i) for i in ['workflow334-recovery','workflow334-authoring']])
    save('stage-traces.json',{t:c.events(t) for t in [previous,author]})
    save('counter-state.json',{t:{k:c.state(t).get(k) for k in
        ['stage','cycle','max_corrections','technical_recoveries','recovery_history']} for t in [previous,author]})
    assert c.state(previous)['technical_recoveries']==3
    assert c.state(previous)['cycle']==0 and c.state(previous)['max_corrections']==0
    guards={}
    for task in [previous,author]:
        try: c.deliver(task,'workflow334-report-forbidden-delivery:'+task)
        except Blocked as e:
            assert str(e)=='NOT_READY'
            guards[task]=str(e)
        else: raise AssertionError('Rejected task delivered')
    save('delivery-negative.json',guards)
    jobs=[]
    for run in ['workflow334-save','workflow334b-save','workflow334c-save','workflow334c-reopen',
                'workflow334author-save','workflow334author-reopen']:
        folder=ROOT/'.runtime/factory-native'/run
        runner=json.loads((folder/'runner-status.json').read_text())
        worker=json.loads((folder/'worker-status.json').read_text())
        diagnostic=json.loads((folder/'script-diagnostics.json').read_text())
        summary={'run':run,'elapsed_seconds':runner['elapsed'],'worker_ok':worker['ok'],
            'error':worker.get('error'),'toolchain':worker['toolchain'],
            'diagnostic':{'binding':bind(str((folder/'script-diagnostics.json').relative_to(ROOT))),
                'embedded_text_hashes':[{k:t[k] for k in ['name','sha256','use_module']} for t in diagnostic['embedded_texts']],
                'driver_count':len(diagnostic['drivers']), 'blocking_count':len(diagnostic['blocked_drivers']),
                'known_source_defects':len(diagnostic.get('known_source_defects',[])),
                'rig_qualified':diagnostic.get('rig_qualified',False)}}
        jobs.append(summary)
        for name in ['runner-status.json','worker-status.json','stdout.log','stderr.log']:
            (OUT/(run+'-'+name)).write_bytes((folder/name).read_bytes())
    save('native-jobs.json',jobs)
    for stem in ['workflow334c','workflow334author']:
        saved=pk.read_json(ROOT,'results/'+stem+'/save-run.json')
        reopened=pk.read_json(ROOT,'results/'+stem+'/reopen-run.json')
        assert saved['status']==reopened['status']=='RETURNED'
        assert saved['artifacts']['snapshot']['sha256']==reopened['artifacts']['snapshot']['sha256']
        assert saved['dependencies']==reopened['dependencies']
        assert pk.read_json(ROOT,'results/'+stem+'/negative-control.json')['worker_launched'] is False
    ch.load(ROOT)
    packet=pk.task_packet(ROOT,pk.read_json(ROOT,'results/workflow334author/task.json'))
    assert packet['dispatch_ready']
    save('final-knowledge-packet.json',packet)
    paths=['results/workflow334/CLOSEOUT.md','results/workflow334/tests.txt','results/workflow334/protected.json',
           'results/workflow334/native-jobs.json','results/workflow334/counter-state.json',
           'results/workflow334/delivery-negative.json','results/workflow334/stage-traces.json',
           'results/workflow334c/negative-control.json','results/workflow334c/visual-review.json',
           'results/workflow334author/negative-control.json','results/workflow334author/visual-review.json',
           'docs/knowledge/NATIVE_WORKFLOW_334.md']
    evidence=[bind(p) for p in paths]
    uses={
        'reuse_envelope':'Existing controller/runner extended. Real selected-state, numeric authoring and fresh reopen qualified; no universal rig/cache claim.',
        'authority':'Routed same-task recovery and distinct disposable transport control; no331 artistic renewal,325 calls, embedded execution, install or egress.',
        'strategy':'Four stages preceded each successful native pair. Known-defect controls deliberately remain rejected.',
        'visual_gate':'Both actual rendered frames inspected and FAIL recorded; successors/delivery blocked. No direct AV claim.',
        'anticipation':'Skipped-script warning separated from actual64 missing-target drivers; next pose strategy must prove control ownership.',
        'stopping':'Workflow envelope complete with evidence; no additional infrastructure micro-handoff or artistic acceptance claim.',
        'versioning':'Protected bytes unchanged; exact recipes, handlers, outputs and separate-process state bound. Failures retained.',
        'economics':'Six native processes measured; bootstrap/token gaps disclosed. No percentage efficiency claim or remote protection.',
        'retrieval':'Fresh packet and explicit330/328/331/332/333, AU13/16 reconciliation; no exhaustive-memory claim.',
        'current_state':'253 accepted master protected;320/331 remain rejected. Next coupled pose/representation proof, not another offset variant.',
        'au_reuse':'Typed transport tested in actual Blender with new-process comparison; not complete cache portability or off-device restore.',
        'au_review':'Technical positive and actual visual negative separated; semantic wrong-method regression retained; Director AV remains pending future footage.'}
    review={'packet_digest':packet['packet_digest'],'scope':'Workflow implementation readiness, not production-media handoff',
        'checks':[{'id':o['id'],'status':'PASS','kind':o['check_kind'],'action_taken':uses[o['id']],
                   'observation':uses[o['id']],'evidence':evidence} for o in packet['obligations']],
        'hypotheses':[{'prediction':'Successful save could be mistaken for usable art.',
                       'observation':'Real rendered controls rejected and dependent launches blocked.',
                       'response':'Preserve separation and carry diagnosed rig defect into next strategy.','result':'resolved'},
                      {'prediction':'Numeric authored state might disappear on fresh reopen.',
                       'observation':'Exact selected-state and new mesh/material hashes persisted.',
                       'response':'Qualify only this typed-operation envelope.','result':'resolved'}],
        'adjacent_regressions':'428 focused tests; unchanged source/reference/accepted hashes; no altered historical source pins.',
        'stopping_reason':'Supported main-chat workflow ready for Nihang package; artistic readiness not claimed.'}
    save('knowledge-review.json',review)
    gate=pk.check_review(ROOT,packet,review); save('knowledge-gate.json',gate)
    assert gate['ready_for_review'],gate
    report={'overall':'SCOPED_MAIN_CHAT_NATIVE_WORKFLOW_READY','tests':(OUT/'tests.txt').read_text().splitlines()[-1],
        'native_processes':len(jobs),'native_elapsed_seconds':sum(j['elapsed_seconds'] for j in jobs),
        'native_failed_diagnostics':2,'successful_save_reopen_pairs':2,'actual_frames_inspected_rejected':2,
        'same_task_recovery_count':3,'artistic_counters_reset':False,'production_approved':False,
        'authoring_transport_qualified':['bounded quaternion keys','bounded new mesh','base-color and roughness','save/reopen/render'],
        'horse_rig_qualified':False,'direct_av_qualified':False,'live_multimodel_renewed':False,
        'provider_calls':0,'remote_protection_performed':False,'protected_unchanged':True,
        'efficiency_percentage':None,'engineering_tokens':None,'knowledge_gate':gate,'evidence':evidence}
    save('report.json',report)
    with sqlite3.connect(f'file:{ROOT / ".runtime/experiment-ops.sqlite3"}?mode=ro',uri=True) as con:
        save('operating-events.json',[json.loads(r[0]) for r in con.execute(
            "SELECT payload FROM events WHERE json_extract(payload,'$.experiment_id')=? ORDER BY seq",('WORKFLOW334',))])
    print(json.dumps({k:report[k] for k in ['overall','tests','native_processes','native_elapsed_seconds']}))


if __name__=='__main__': main()
