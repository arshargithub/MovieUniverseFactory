"""Explicit source/control-only retrospective reasoning for initial386proof.

Only administrative checks close here. Anatomy and human AV remain unqualified.
"""
import json
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk

r=Path(__file__).resolve().parents[1];o=r/'results/sikh386';task='sikh335-supporting-appearance';c=wf.Controller(r,'.runtime/factory-entry.sqlite3')
s=c.state(task);assert s['cycle']==177 and s['max_corrections']==226 and s['stage']=='EXECUTING'
bind=lambda p:dict(path=p,sha256=pk.file_hash(r/p))
evidence={p:bind(p) for p in ['results/sikh386/ADMIN_CONTROLS177.json','results/sikh386/WORKFLOW_QUALIFICATION.md','results/sikh386/REQUEST.md']}
common=dict(reference_assessment=dict(readiness_digest=pk.digest(s['brief']['reference_readiness']),diagnosis='method',disposition='retain',
    reason='Existing real/reference/accepted-action roles are sufficient for source-control diagnosis; actual positive volume remains untested.',
    aspects=list(s['brief']['reference_readiness']['decisions']),evidence=list(evidence.values())),
    preserve='Accepted80source and all historical failures; no art or humanAV PASS from admin/source checks.',
    failure_response='Record failed/inconclusive tested outcome before another remedy, replan affected scope without reset.',
    target_stage='STRATEGIZING',plan=pk.digest(s['brief']),evidence=evidence,
    scope_assessment=dict(decision='keep',unit_digest=pk.digest(s['brief']['work_unit']),reason='UnitA source prerequisite supports a connected chest-mass proof; surrounding roots and neck remain visible.'))

def reply(key,cause,test,expected,category='administrative'):
    gate=c.retrospective_packet(task)['gates'][key]
    response=dict(common,cause=cause,uncertainty='Administrative/source readiness is not correct positive anatomy.',
        change_or_retain_rationale='Current source-first diagnostic and micro-unit contract separate cause/target from transport precision.',
        test=test,expected=expected,gate_digest=pk.digest(gate),
        causal_assessment=dict(category=category,method_family='actual_source_control_before_volume',
          changed_prediction=test,previous_result='Prior findings retained; no successful chest proof.'))
    event='sikh386-c177-'+key+'-response'
    c.retrospective(task,'response',dict(key=key,response=response),event)
    challenge=dict(response_event=event,counterexample='A valid source/counter/schema can coexist with a visibly malformed chest; this diagnostic does not close form.',
        evidence=evidence,checks={k:dict(status='PASS',observation=t) for k,t in dict(
            causal_test=test,actual_method='Actual source export/control only; volumetric target later, not another old smoothing gain.',
            preservation=response['preserve'],authority='Bound386same-task50grant, current177/226, no additional resources.').items()})
    admission=event+'-admit';c.retrospective(task,'admit',dict(key=key,challenge=challenge),admission)
    return admission

administrative={
 '__migration__':('Policy/code changed; reviewed migration must retain original335history/counters and declared capability limits.',
    'Check current retrospective/planning engines, original authority and fresh actual source bindings after migration.',
    'Policy matches, original task/history preserved; capabilities retain no direct motion/audio.'),
 '__allowance__':('176was exhausted; Director386explicitly authorizes one50extension, not new artistic acceptance.',
    'Check177/226, one50history entry and exact bound grant; no replay or child reset.',
    'Only authorized counter change occurred; art/AV remains pending.'),
 '__requirements__':('Current unit returns from donor head/tack to previous-horse chest, requiring explicit criterion/reference reconciliation.',
    'Inspect386intent, required original source roles, reference roles, unitAcriteria and protected accepted80action; validate fresh full brief.',
    'Current scope/inputs are coherently reconciled; no hidden new resource or artistic PASS.')}
for key,(cause,test,expected) in administrative.items():
    if c.retrospective_packet(task)['gates'].get(key,{}).get('status')=='CLOSED':continue
    admission=reply(key,cause,test,expected)
    controls=pk.read_json(r,'results/sikh386/ADMIN_CONTROLS177.json')
    assert controls['cycle']==177 and controls['max_corrections']==226 and controls['new_grant']==50
    assert controls['planning_engine_matches'] and controls['full_source_freshness_checked']
    oid='sikh386-c177-'+key+'-actual-admin-control'
    c.retrospective(task,'outcome',dict(attempt=oid,role='diagnostic',origin='deterministic_admin_controls',observations=[dict(requirement=key,status='PASS',observation=expected+' Actual controls inADMIN_CONTROLS177; this is solely administrative.')],evidence=evidence),oid)
    c.retrospective(task,'evaluate',dict(key=key,evaluation=dict(admission_event=admission,result='effective',outcome_event=oid,observation='Exact administrative invariant validated; no creative finding resolved.',evidence=evidence)),oid+'-effect')

reasons={
 'form':('Current inherited chest is a known flat/bib failure; positive anatomical target still missing.','Export actual cage/bone ownership and show matched stance/crest/descent before authoring target.','Source establishes construction inputs, not positive form.','positive_target'),
 'interfaces':('Past skin ownership created sheets/bulbs; source inputs must expose the actual limb/neck/chest relationship.','Inspect actual upperarm/neck/breast endpoints and evaluated cage, preserving all action.','Interface hypothesis remains unqualified until a positive target is rendered.','representation'),
 'evidence':('Previous target/cache precision and unrelated views did not prove anatomy.','Three anatomical views plus whole source, exact183source samples and known negative references.','Usable evidence/control coverage only; no full moving-form proof yet.','evidence'),
 'whole_look':('Prior local smoothing looked less bad while whole connected horse remained wrong.','Keep complete source context alongside close chest framing, same horse and film.','Actual wholehorse negative context retained; no wholelook PASS.','judgment'),
 'director_form_motion':('Source/image checks cannot establish full-speed visual flow under modified skin.','Retain accepted original action; leave temporal judgment untested until integratedDclip.','No agent motion/audio capability claim or human acceptance inferred.','evidence'),
 '__worker__':('Previous technical failures and changed trusted handler need actual current integration test.','Run fixed386export through canonical bridge and inspect actual returned data/source invariants.','Software tests are insufficient; actual worker return and unchanged state must follow.','execution'),
 '__positive_forequarter_form__':('379/381references clarify gross form, but earlier target construction remained wrong.','Obtain actual original80source, then create positive volume rather than fit another failed derivative.','Source prerequisite only; supported positive anatomy remains untested.','positive_target'),
 '__forequarter_method__':('Earlier ownership and sculpt families failed; new volume is a hypothesis with actual-source prerequisites.','Export actual evaluated source rather than assume linear skinning or reimport an identical rest donor.','Actual source supports the next discriminating positive-volume test, not a method success.','representation')}
for key,(cause,test,expected,category) in reasons.items():
    gate=c.retrospective_packet(task)['gates'].get(key)
    if not gate:continue
    if gate['status']=='TESTING' and gate['plan']!=pk.digest(s['brief']):
        oid='sikh386-c177-'+key+'-reopen'
        c.retrospective(task,'outcome',dict(attempt=oid,role='diagnostic',origin='explicit386scope_change',observations=[dict(requirement=key,status='UNKNOWN',observation='Old test conditions are historical; current386previous-horse unit requires new source/shape proof. No oldPASS inherited.')],evidence=evidence),oid)
        gate=c.retrospective_packet(task)['gates'][key]
    if gate['status']=='OPEN':reply(key,cause,test,expected,category)
packet=c.retrospective_packet(task);(o/'RETRO177_START.json').write_text(json.dumps(packet,indent=2)+'\n')
print(json.dumps(dict(gates={k:v['status'] for k,v in packet['gates'].items()},packet_characters=len(json.dumps(packet)))))
