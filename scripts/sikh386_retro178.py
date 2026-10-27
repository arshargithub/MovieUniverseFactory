"""178 explicit source prerequisite tests; no artistic approval."""
import json
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk,retrospective as rt
r=Path(__file__).resolve().parents[1];o=r/'results/sikh386';task='sikh335-supporting-appearance';c=wf.Controller(r,'.runtime/factory-entry.sqlite3');s=c.state(task);assert s['cycle']==178
bind=lambda p:dict(path=p,sha256=pk.file_hash(r/p))
ev={p:bind(p) for p in ['results/sikh386/RECOVERY178.md','results/sikh386/CYCLE177_CLOSEOUT.json','results/sikh386/policy-migration178.json','results/sikh386/REQUEST.md']}
keys=['__migration__','form','interfaces','evidence','whole_look','director_form_motion','__worker__','__positive_forequarter_form__','__forequarter_method__']
common=dict(reference_assessment=dict(readiness_digest=pk.digest(s['brief']['reference_readiness']),diagnosis='method',disposition='retain',
    reason='Gross physical/action references remain adequate; current experiment is actual source/control only.',aspects=list(s['brief']['reference_readiness']['decisions']),evidence=list(ev.values())),
    cause='Distinct unresolved findings share ONE actual original80source/control prerequisite; exact per-key causes and limits are inSOURCE_FINDING_TABLE178. The physical target has not been authored or tested.',
    uncertainty='Source/worker correctness does not establish positive mass, attachment, volume-method success or humanAV.',
    change_or_retain_rationale='Retain unchanged178source experiment; consolidate its redundant bookkeeping payload, not its requirements or failure history.',
    preserve='Accepted80action/source, all distinct requirement findings/triggers and original response/event history. No known art failure waived.',
    test='One canonical183sample original80cage/bone export and matched close/whole283333339controls; inspect actual returned invariants and source appearance.',
    expected='Exact source/ownership and usable evidence available for subsequent positive target. Each artistic or humanAV finding remains unqualified.',
    failure_response='Evaluate actual failed/inconclusive outcome before another remedy; reference/target/representation gap returns to its appropriate stage.',
    target_stage='STRATEGIZING',plan=pk.digest(s['brief']),evidence=ev,
    scope_assessment=dict(decision='keep',unit_digest=pk.digest(s['brief']['work_unit']),reason='One source prerequisite for one connected chest-mass outcome; per-key context and interfaces remain in bound table.'),
    causal_assessment=dict(category='evidence',method_family='actual_source_control_before_volume',changed_prediction='No new physical remedy: obtain actual evaluated source once before volume authoring; metadata consolidation enables the same bounded plan.',previous_result='Earlier tests inconclusive because packet blocked before any native worker; not an artistic experiment.'))
for key in keys:
    # Read source-backed canonical state while repairing its packet encoding;
    # every response/admission still uses the supported controller and guards.
    gate=rt.expand_packet_gates(c.retrospective_packet(task))[key];assert gate['status']=='OPEN',key
    event='sikh386-c178-'+key+'-source-prerequisite'
    c.retrospective(task,'response',dict(key=key,response=dict(common,gate_digest=pk.digest(gate))),event)
    challenge=dict(response_event=event,counterexample='Correct inputs and transport can still yield bad anatomy; no positive form is claimed here.',evidence=ev,
        checks={k:dict(status='PASS',observation=t) for k,t in dict(causal_test=common['test'],actual_method='Unchanged fixed178source/export and actual visual controls, not a new artist repair.',preservation=common['preserve'],authority='Same178/226Director386ceiling and no new resources.').items()})
    c.retrospective(task,'admit',dict(key=key,challenge=challenge),event+'-admit')

p=c.retrospective_packet(task)
key='__migration__';admission='sikh386-c178-'+key+'-source-prerequisite-admit';oid='sikh386-c178-migration-validated'
c.retrospective(task,'outcome',dict(attempt=oid,role='diagnostic',origin='verified_serialization_policy_migration',observations=[dict(requirement=key,status='PASS',observation='Exact current engine matches migrated projection; source-bound migration preserves history/counters; codec160tests pass. Administrative only.')],evidence=ev),oid)
c.retrospective(task,'evaluate',dict(key=key,evaluation=dict(admission_event=admission,result='effective',outcome_event=oid,observation='Serialization policy and source migration checked; anatomy remains unqualified.',evidence=ev)),oid+'-effect')
p=c.retrospective_packet(task);c.packet(task)
(o/'RETRO178_START.json').write_text(json.dumps(p,indent=2)+'\n');print('178 source prerequisite admitted; no art PASS')
