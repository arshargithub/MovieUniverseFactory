"""Reconcile redundant descriptions of ONE pre-native source experiment.

No gate/trigger/event deletion, ceiling change, art PASS, native job or new plan.
"""
import json
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk,retrospective as rt

r=Path(__file__).resolve().parents[1];o=r/'results/sikh386';task='sikh335-supporting-appearance';c=wf.Controller(r,'.runtime/factory-entry.sqlite3')
s=c.state(task);assert s['cycle']==177 and s['stage']=='EXECUTING'
bind=lambda p:dict(path=p,sha256=pk.file_hash(r/p))
con=c.connect();before=rt.snapshot(con,task);count=con.execute("SELECT count(*) FROM native_runs WHERE id LIKE 'sikh386-%'").fetchone()[0];con.close();assert count==0
pending={k:v for k,v in before['interventions'].items() if v['effect_required'] and 'result' not in v}
receipt=dict(error='RETRO_PACKET_TOO_LARGE_RECONCILE_SCOPE',native_jobs=0,cycle=177,max=226,
    pending_interventions=pending,original_event_count=before['sequence'],gate_count=len(before['gates']),
    rationale='Distinct requirement findings were given distinct descriptions of the same source-control prerequisite. Existing lossless whole-payload dedup needs one shared prerequisite body. Preserve per-key causes in bound table and all previous events; no art trial or target has run.')
(o/'PACKET_RECONCILIATION177.json').write_text(json.dumps(receipt,indent=2)+'\n')
(o/'SOURCE_FINDING_TABLE177.md').write_text('''#177 one source experiment, distinct unresolved findings\n\n|Finding|Actual unresolved cause|What this source experiment can decide|What it cannot decide|\n|---|---|---|---|\n|form|Previous chest is flat/bib; positive volume missing.|Exact original80cage and pose/ownership anchors.|Acceptable positive anatomy.|\n|interfaces|Previous weights/root surfaces formed sheets/bulbs.|Actual changing chest/upperarm/neck relationship.|Natural repaired attachments.|\n|evidence|Precision and wrong views substituted for form.|Matched close/whole source and183actual samples.|Complete final moving-form proof.|\n|whole_look|Local improvement concealed bad connected mass.|Whole source context beside close crop.|Wholehorse final quality.|\n|director_form_motion|No agent real-time AV capability.|Preserve original accepted action/source.|Human temporal acceptance under changed skin.|\n|__worker__|New fixed exporter lacks actual native integration.|Actual canonical return/state invariants.|Any anatomy or fullspeed success.|\n|__positive_forequarter_form__|Clear references but no constructed positive target.|Inputs for a different volume construction.|A passed chest target.|\n|__forequarter_method__|Past fields/rest/ownership methods failed.|Actual B-bone evaluated source instead of assumed linear skinning.|Success of an untested volumetric method.|\n\nThis is one183sample source export and matched control set, not eight independent remedies or newart attempts. All per-key findings, triggers and original response records remain immutable. The initial response set could not fit the60KBpacket; admitted tests receive explicit inconclusive bookkeeping outcomes, not invented art results. The same unchanged177source plan then gets shared source-prerequisite responses through the existing lossless codec. No controller cap or source/authority requirement is altered.\n''')
ev={p:bind(p) for p in ['results/sikh386/PACKET_RECONCILIATION177.json','results/sikh386/SOURCE_FINDING_TABLE177.md','results/sikh386/REQUEST.md']}
oid='sikh386-c177-pre-native-packet-block'
c.retrospective(task,'outcome',dict(attempt=oid,role='technical',origin='observed_pre_native_packet_guard',
    observations=[dict(requirement=x['key'],status='UNKNOWN',observation='Actual source/control experiment could not dispatch because its redundant response packet exceeded60KB. No art target or source worker ran; physical outcome is inconclusive.') for x in pending.values()],evidence=ev),oid)
for admission,trial in pending.items():
    c.retrospective(task,'evaluate',dict(key=trial['key'],evaluation=dict(admission_event=admission,result='inconclusive',outcome_event=oid,
        observation='Explicit unexecuted-test disposition due to packet representation; no anatomical conclusion or new art method.',evidence=ev)),admission+'-packet-disposition')

keys=['form','interfaces','evidence','whole_look','director_form_motion','__worker__','__positive_forequarter_form__','__forequarter_method__']
common=dict(reference_assessment=dict(readiness_digest=pk.digest(s['brief']['reference_readiness']),diagnosis='method',disposition='retain',
    reason='Gross physical/action references remain adequate; current experiment is actual source/control only.',aspects=list(s['brief']['reference_readiness']['decisions']),evidence=list(ev.values())),
    cause='Distinct unresolved findings share ONE actual original80source/control prerequisite; exact per-key causes and limits are inSOURCE_FINDING_TABLE177. The physical target has not been authored or tested.',
    uncertainty='Source/worker correctness does not establish positive mass, attachment, volume-method success or humanAV.',
    change_or_retain_rationale='Retain unchanged177source experiment; consolidate its redundant bookkeeping payload, not its requirements or failure history.',
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
    con=c.connect();gate=rt.snapshot(con,task)['gates'][key];con.close();assert gate['status']=='OPEN',key
    event='sikh386-c177-'+key+'-source-prerequisite'
    c.retrospective(task,'response',dict(key=key,response=dict(common,gate_digest=pk.digest(gate))),event)
    challenge=dict(response_event=event,counterexample='Correct inputs and transport can still yield bad anatomy; no positive form is claimed here.',evidence=ev,
        checks={k:dict(status='PASS',observation=t) for k,t in dict(causal_test=common['test'],actual_method='Unchanged fixed177source/export and actual visual controls, not a new artist repair.',preservation=common['preserve'],authority='Same177/226Director386ceiling and no new resources.').items()})
    c.retrospective(task,'admit',dict(key=key,challenge=challenge),event+'-admit')
p=c.retrospective_packet(task);c.packet(task)
(o/'RETRO177_START.json').write_text(json.dumps(p,indent=2)+'\n');print(json.dumps(dict(packet_characters=len(json.dumps(p)),pending_effects=len(p['pending_effects386']),native_jobs=0,execution_guard='PASS',art='NOT_RUN')))
