"""Purpose-qualified input contracts. Structural admission, not visual truth."""
from . import production_knowledge as pk, review_control as rc
from .production_workflow import require, nonempty, rows

PURPOSES = {'physical_form','motion_mechanics','design','staging','film_style','technical_validation'}
ORIGINS = {'director','image_search','video_search','built_in_image','generated_video','accepted_asset'}
GENERATED = {'built_in_image','generated_video'}
PHYSICAL = {'physical_form','motion_mechanics'}


def scope(value):
    require(isinstance(value,dict) and value.get('version')==1, 'REFERENCE_SCOPE_REQUIRED')
    require(nonempty(value.get('id')) and value.get('kind') in {'micro_motion','micro_appearance','production'}, 'REFERENCE_SCOPE_KIND')
    needs=rows(value.get('needs',[]));require(needs,'REFERENCE_NEEDS_REQUIRED')
    for n in needs.values():
        require(n.get('purpose') in PURPOSES and nonempty(n.get('question')) and type(n.get('critical')) is bool, 'REFERENCE_NEED_PURPOSE')
        require(isinstance(n.get('coverage'),list) and n['coverage'] and len(set(n['coverage']))==len(n['coverage']) and all(nonempty(x) for x in n['coverage']), 'REFERENCE_NEED_COVERAGE')
    return needs


def validate(root, references, value, expected=None, bindings=None):
    require(isinstance(value,dict) and value.get('version')==1,'REFERENCE_READINESS_REQUIRED')
    if expected is not None:require(value.get('scope')==expected,'REFERENCE_SCOPE_CHANGED')
    needs=scope(value.get('scope'));decisions=value.get('decisions',{});refs=rows(references)
    require(set(decisions)==set(needs),'REFERENCE_DECISION_COVERAGE')
    for ident,n in needs.items():
        d=decisions[ident]
        require(d.get('decision') in {'reuse_existing','acquire','none_needed'} and nonempty(d.get('reason')) and nonempty(d.get('reopen_when')), 'REFERENCE_DECISION_REQUIRED')
        selected=d.get('references');require(isinstance(selected,list),'REFERENCE_SELECTION_REQUIRED')
        if d['decision']=='none_needed':
            require(not selected and d.get('status')=='not_needed','REFERENCE_NONE_CONFLICT')
            require(not (n['critical'] and n['purpose'] in PHYSICAL),'REFERENCE_PHYSICAL_NEEDS_EVIDENCE')
            continue
        require(d.get('status')=='sufficient' and selected,'REFERENCE_NOT_SUFFICIENT')
        selections=rows(selected);covered=set()
        for rid,q in selections.items():
            require(rid in refs and q.get('origin') in ORIGINS,'REFERENCE_UNKNOWN_SOURCE')
            for key in ('observation','governs','excluded_authority','provenance','rights_use'):
                require(nonempty(q.get(key)),'REFERENCE_QUALIFICATION_'+key.upper())
            require(q['rights_use'] in {'reference_only','cleared_for_production'},'REFERENCE_RIGHTS_USE')
            coverage=q.get('coverage',{})
            require(isinstance(coverage,dict) and coverage and set(coverage)<=set(n['coverage']) and all(nonempty(x) for x in coverage.values()),'REFERENCE_VIEW_PHASE_COVERAGE')
            covered.update(coverage)
            require(q.get('evidence'),'REFERENCE_QUALIFICATION_EVIDENCE')
            require(refs[rid]['binding'] in q['evidence'],'REFERENCE_SOURCE_MEDIA_REQUIRED')
            for b in q['evidence']:
                rc.binding(root,b)
                if bindings is not None:require(b in bindings,'REFERENCE_EVIDENCE_NOT_BOUND')
            if q['origin']=='generated_video':
                require(q.get('acquisition_receipt'),'REFERENCE_VIDEO_RECEIPT_REQUIRED');rc.binding(root,q['acquisition_receipt'])
                receipt=pk.read_json(root,q['acquisition_receipt']['path'])
                require(receipt.get('kind')=='reference_video_receipt' and receipt.get('reservation_id') and receipt.get('director_approval'),'REFERENCE_VIDEO_RECEIPT_REQUIRED')
                rc.binding(root,receipt['director_approval'])
                if bindings is not None:require(q['acquisition_receipt'] in bindings,'REFERENCE_EVIDENCE_NOT_BOUND')
            if n['purpose'] in PHYSICAL and q['origin'] in GENERATED:
                corroboration=q.get('validated_against',[])
                require(corroboration and set(corroboration)<=set(selections) and all(selections[k]['origin'] not in GENERATED for k in corroboration),'REFERENCE_GENERATED_PHYSICS_UNCORROBORATED')
        require(covered==set(n['coverage']),'REFERENCE_COVERAGE_GAP')
    return pk.digest(value)


def grounding(root,direction,data,required=False):
    expected=direction.get('reference_scope')
    if expected is None and not required and 'reference_readiness' not in data:return
    require(expected is not None,'REFERENCE_SCOPE_REQUIRED')
    validate(root,direction['references'],data.get('reference_readiness'),expected)


def derivation(ground,data):
    ready=ground.get('reference_readiness')
    if ready is None:return
    require(data.get('reference_readiness')==ready,'REFERENCE_GROUNDING_LOST')
    mapping=data.get('reference_mapping',{});reqs=rows(data['requirements']);needs=scope(ready['scope'])
    require(set(mapping)==set(reqs),'REFERENCE_REQUIREMENT_COVERAGE');used=set()
    for rid,ids in mapping.items():
        require(isinstance(ids,list) and ids and set(ids)<=set(needs),'REFERENCE_REQUIREMENT_ASPECT')
        used.update(ids)
        sources={q['id'] for n in ids for q in ready['decisions'][n]['references']}
        require(sources<=set(data['derivations'][rid]['reference_ids']),'REFERENCE_DERIVATION_SOURCE_LOST')
    require({k for k,n in needs.items() if n['critical']}<=used,'REFERENCE_CRITICAL_NEED_LOST')


def brief(root,b,required=False):
    value=b.get('reference_readiness')
    if value is None and not required:return
    validate(root,b['references'],value,bindings=list(b['source_bindings'].values()))
    derivation({'reference_readiness':value},dict(reference_readiness=value,reference_mapping=b.get('reference_mapping'),requirements=b['requirements'],derivations=b['expert_plan']['realizations']))


def strategy(derived,data):
    if 'reference_readiness' not in derived:return
    b=data['brief'];require(b.get('reference_readiness')==derived['reference_readiness'] and b.get('reference_mapping')==derived['reference_mapping'],'REFERENCE_STRATEGY_CHANGED')


def challenge(root,ready,result):
    if ready is None:return
    c=result.get('reference_challenge',{});require(c.get('readiness_digest')==pk.digest(ready),'REFERENCE_CHALLENGE_STALE')
    need_ids=set(scope(ready['scope']));checks=c.get('checks',{});require(set(checks)==need_ids,'REFERENCE_CHALLENGE_COVERAGE')
    for ident,v in checks.items():
        require(v.get('status') in {'PASS','FAIL','NOT_RUN'} and nonempty(v.get('observation')) and nonempty(v.get('counterexample')),'REFERENCE_CHALLENGE_OBSERVATION')
        if result['outcome']=='admit':require(v['status']=='PASS','REFERENCE_CHALLENGE_FAILED')
        require(isinstance(v.get('evidence'),list),'REFERENCE_CHALLENGE_EVIDENCE')
        if ready['decisions'][ident]['decision']!='none_needed':require(v['evidence'],'REFERENCE_CHALLENGE_EVIDENCE')
        for b in v['evidence']:rc.binding(root,b)


def execution(b,result):
    ready=b.get('reference_readiness')
    if ready is None:return
    a=result.get('reference_application',{});require(a.get('readiness_digest')==pk.digest(ready),'REFERENCE_EXECUTION_STALE')
    require(set(a.get('aspects',{}))==set(ready['decisions']) and all(nonempty(x) for x in a['aspects'].values()),'REFERENCE_EXECUTION_COVERAGE')


def review(b,result,evidence):
    ready=b.get('reference_readiness')
    if ready is None:return [],[]
    v=result.get('reference_readiness_review',{});require(v.get('readiness_digest')==pk.digest(ready),'REFERENCE_REVIEW_STALE')
    checks=v.get('aspects',{});require(set(checks)==set(ready['decisions']),'REFERENCE_REVIEW_COVERAGE');fail=[];missing=[]
    for k,q in checks.items():
        require(q.get('status') in {'PASS','FAIL','NOT_RUN'} and nonempty(q.get('observation')) and nonempty(q.get('comparison')),'REFERENCE_REVIEW_OBSERVATION')
        require(isinstance(q.get('evidence'),list) and set(q['evidence'])<=set(evidence),'REFERENCE_REVIEW_EVIDENCE')
        if q['status']!='NOT_RUN':require(q['evidence'],'REFERENCE_REVIEW_EVIDENCE')
        if q['status']=='FAIL':fail.append('reference_readiness:'+k)
        if q['status']=='NOT_RUN':missing.append('reference_readiness:'+k)
    return fail,missing


def assessment(root,ready,data):
    """Explicit retain/change decision; not an automatic request for more images."""
    if ready is None:return
    a=data.get('reference_assessment',{});require(a.get('readiness_digest')==pk.digest(ready),'REFERENCE_RETRO_STALE')
    require(a.get('diagnosis') in {'reference_gap','method','execution','evidence','judgment','no_reference_issue'},'REFERENCE_RETRO_DIAGNOSIS')
    require(a.get('disposition') in {'retain','supplement','replace','no_reference_issue'} and nonempty(a.get('reason')),'REFERENCE_RETRO_DISPOSITION')
    require(isinstance(a.get('aspects'),list) and a['aspects'] and set(a['aspects'])<=set(ready['decisions']),'REFERENCE_RETRO_COVERAGE')
    require(a.get('evidence'),'REFERENCE_RETRO_EVIDENCE')
    for b in a['evidence']:rc.binding(root,b)
    if a['diagnosis']=='reference_gap':
        require(a['disposition'] in {'supplement','replace'} and data.get('target_stage')=='GROUNDING','REFERENCE_GAP_REQUIRES_GROUNDING')


def escalation(root,packet):
    b=packet.get('brief') or packet.get('planning_inputs',{}).get('STRATEGIZING',{}).get('brief',{})
    ready=b.get('reference_readiness') or packet.get('planning_inputs',{}).get('GROUNDING',{}).get('reference_readiness')
    micro=(bool(b.get('work_unit')) or (ready or {}).get('scope',{}).get('kind') in {'micro_motion','micro_appearance'}
           or packet.get('direction',{}).get('reference_scope',{}).get('kind') in {'micro_motion','micro_appearance'})
    if not micro:return
    require(ready is not None,'REFERENCE_ESCALATION_INPUT_UNRESOLVED')
    refs=b.get('references') or packet['direction']['references'];validate(root,refs,ready)
    basis=packet.get('reference_escalation_basis',{})
    require(basis.get('readiness_digest')==pk.digest(ready) and basis.get('hypothesis') in {'execution_gap','unresolved_after_adequate_references'},'REFERENCE_ESCALATION_BASIS')
    require(nonempty(basis.get('reason')) and basis.get('evidence'),'REFERENCE_ESCALATION_EVIDENCE')
    for q in basis['evidence']:rc.binding(root,q)


def contract():
    return dict(version=1,entry='Each new native production plan declares reference_scope and explicit reuse_existing/acquire/none_needed decisions; legacy offline/frozen records are not native authority.',qualification='Purpose, actual coverage observations, governs/excluded authority, provenance/rights-use and bound inspected source media; generated physical claims need non-generated corroboration.',propagation='Grounding.reference_readiness -> Derivation.reference_mapping -> brief -> planning challenge -> actual execution/review; copies/digests do not prove truth.',retro='Every current-protocol retrospective response assesses retain/supplement/replace/no_reference_issue; reference_gap outcome opens an immediate finding; reference gap returns to Grounding.',acquisition='Image search and built-in images agent-owned; paid video requires exact approval and persistent budget guard; raw chat tools remain instruction governed.',limits='Source bindings and declared coverage are structural checks. They cannot establish truthful viewing, physical correctness, artistic sufficiency or director acceptance. Reference readiness review does not replace full-speed motion/audio checks.')
