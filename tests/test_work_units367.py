"""Structural scope/reference gates and their explicit semantic blind spot."""
from copy import deepcopy
import pytest
from movie_factory import work_units as u, expert_planning as ep, production_workflow as wf
from test_production_workflow import setup


def contract(b):
    rid=next(x['id'] for x in b['requirements'] if not x['director_av'])
    ref=b['references'][0];ref['role']='faithful_motion';ref['unit_required']=True
    return dict(version=1,id='preparation',primary_outcome='Gather confidently into first lift',phase='preparation',task='t',reference=ref['id'],
        allowed_domains=['horse_pose','rider_contact'],frozen_domains=['horse_mesh','cloth_look'],
        positive_criteria=[dict(id=rid,reference_feature='Coordinated loading',failure='Tentative hoof taps',comparison='Phase-aligned whole horse, revealing side')],
        boundaries=[dict(id='first_lift',state=['pose','velocity','contacts'],consumer='rise')],
        negative_controls=[dict(id='old',binding=next(iter(b['source_bindings'].values())),expected='FAIL',failure='Old weak preparation')],
        calibration={'old':dict(verdict='FAIL',observation='Foot taps lack coordinated load')},
        operations=['nihang_patch','nihang_save','nihang_frames'],edit_kinds=['mounted_prep367'],cycle_window=[0,9])


def prepared(setup):
    b=deepcopy(setup[2]);b['work_unit']=contract(b);b['expert_plan']['challenge']['plan_digest']=ep.plan_digest(b)
    return b


@pytest.mark.parametrize('mutation', ['missing','multi_goal','unbound_control','passing_control','scope_conflict','no_boundary','no_positive','wrong_reference','no_calibration'])
def test_planning_fail_closed(setup,mutation):
    b=prepared(setup);w=b['work_unit']
    if mutation=='missing':del b['work_unit']
    if mutation=='multi_goal':w['primary_outcome']=['motion','sculpt']
    if mutation=='unbound_control':w['negative_controls'][0]['binding']={'path':'missing','sha256':'0'*64}
    if mutation=='passing_control':w['calibration']['old']['verdict']='PASS'
    if mutation=='scope_conflict':w['frozen_domains'].append('horse_pose')
    if mutation=='no_boundary':w['boundaries']=[]
    if mutation=='no_positive':w['positive_criteria']=[]
    if mutation=='wrong_reference':b['references'][0]['role']='directional_design'
    if mutation=='no_calibration':w['calibration']={}
    b['expert_plan']['challenge']['plan_digest']=ep.plan_digest(b)
    with pytest.raises(wf.Blocked):ep.validate(b)


def test_native_edit_window_and_frozen_domain(setup):
    b=prepared(setup);s={'task':'t','cycle':1,'brief':b}
    u.native(s,{'operation':'nihang_patch','edits':[{'kind':'mounted_prep367'}]})
    with pytest.raises(wf.Blocked,match='UNIT_OUTSIDE_EDIT_SCOPE'):
        u.native(s,{'operation':'nihang_patch','edits':[{'kind':'mounted_chest363'}]})
    with pytest.raises(wf.Blocked,match='UNIT_ASSIGNMENT_EXPIRED'):
        u.native({**s,'cycle':10},{'operation':'nihang_save'})


def test_unit_changes_invalidate_plan_digest(setup):
    b=prepared(setup);old=ep.plan_digest(b);b['work_unit']['phase']='crest';assert ep.plan_digest(b)!=old
    with pytest.raises(wf.Blocked,match='STALE_PLANNING_CHALLENGE'):ep.validate(b)


def test_execution_requires_actual_unit_applications(setup):
    b=prepared(setup)
    with pytest.raises(wf.Blocked,match='UNIT_EXECUTION_LOST'):u.execution(b,{})
    rid=b['work_unit']['positive_criteria'][0]['id']
    a={'id':'preparation','criteria':{rid:'Source-bound actual phase evidence'},'changed_domains':['horse_pose'],'boundaries':{'first_lift':'Pose/velocity/contact measured'}}
    u.execution(b,{'unit_application':a})
    a['changed_domains'].append('horse_mesh')
    with pytest.raises(wf.Blocked,match='UNIT_OUTSIDE_DOMAIN'):u.execution(b,{'unit_application':a})


def reviewed(b):
    row={'status':'PASS','observation':'Actual loading poses inspected','comparison':'Compared reference phase','evidence':['frame']}
    rid=b['work_unit']['positive_criteria'][0]['id']
    return {'unit_review':dict(id='preparation',criteria={rid:deepcopy(row)},boundaries={'first_lift':deepcopy(row)},largest_remaining_mismatch={'blocking':False,'observation':'No observed scoped pose mismatch; AV pending','evidence':['frame']},outside_scope_changes=[])}


@pytest.mark.parametrize('mutation',['criterion_fail','missing_evidence','mismatch','scope_change','missing_boundary','lost_unit'])
def test_review_rejects_visible_or_missing_unit(setup,mutation):
    b=prepared(setup);r=reviewed(b);v=r['unit_review'];rid=b['work_unit']['positive_criteria'][0]['id']
    if mutation=='criterion_fail':v['criteria'][rid]['status']='FAIL'
    if mutation=='missing_evidence':v['criteria'][rid]['evidence']=[]
    if mutation=='mismatch':v['largest_remaining_mismatch']['blocking']=True
    if mutation=='scope_change':v['outside_scope_changes']=['Unplanned cloth edit']
    if mutation=='missing_boundary':v['boundaries']={}
    if mutation=='lost_unit':r={}
    try:
        failures,missing=u.review(b,r,{'frame':{}});assert failures or missing
    except wf.Blocked:pass


def test_legacy_validation_unchanged_and_false_assertion_is_still_possible(setup):
    assert u.validate(setup[2]) is None
    b=prepared(setup);ep.validate(b)
    # Deliberate known semantic false negative: correct fields cannot prove
    # that a visual assertion is true. Preserve this limitation in qualification.
    b['strategy']='Keep rejected prep and merely retime airborne action'
    ep.validate(b)
    assert u.review(b,reviewed(b),{'frame':{}})==([],[])
