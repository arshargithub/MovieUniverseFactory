"""Synthetic positive/negative evidence, never production qualification."""
import copy
import pytest
from movie_factory.resource_manifest import validate
from movie_factory.production_knowledge import file_hash

@pytest.fixture
def case(tmp_path):
    p=tmp_path/'fixture';p.write_text('synthetic')
    bind={'path':'fixture','sha256':file_hash(p)}
    r={'schema_version':1,'id':'fixture','state':'qualified','reuse_mode':'exact',
       'source':[bind],'provenance':[bind],'dependencies':[bind],
       'rights':{'status':'verified_for_use','scope':'synthetic','evidence_paths':['fixture']},
       'tested_conditions':{'rig':'r1','runtime':'5.2.1','shot':'test'},'evidence':[bind],
       'failures':[],'effort':{'active_seconds':None,'evidence_path':None}}
    return tmp_path,r,copy.deepcopy(r['tested_conditions'])

def test_exact_scoped_fixture(case):
    root,r,use=case;assert validate(root,r,use)['reuse_admissible']

@pytest.mark.parametrize('field',['source','provenance','dependencies','evidence'])
def test_missing_binding_blocks(case,field):
    root,r,use=case;r[field]=[];assert not validate(root,r,use)['reuse_admissible']

def test_stale_artifact_blocks(case):
    root,r,use=case;(root/'fixture').write_text('changed');assert any(x.startswith('STALE') for x in validate(root,r,use)['blockers'])

def test_changed_rig_and_unspecified_conditions_block(case):
    root,r,use=case;use['rig']='r2';assert 'UNTESTED_CONDITION:rig' in validate(root,r,use)['blockers']
    del use['runtime'];assert 'UNSPECIFIED_CONDITION:runtime' in validate(root,r,use)['blockers']

def test_unresolved_rights_and_known_failure_block(case):
    root,r,use=case;r['rights']['status']='unresolved';r['failures']=[{'id':'bad-hoof','status':'open'}]
    b=validate(root,r,use)['blockers'];assert 'RIGHTS:unresolved' in b and 'OPEN_FAILURE:bad-hoof' in b

def test_unsafe_path_and_candidate_not_promoted(case):
    root,r,use=case;r['source']=[{'path':'../outside','sha256':'0'*64}];r['state']='in_progress'
    b=validate(root,r,use)['blockers'];assert 'NOT_QUALIFIED:in_progress' in b and any(x.startswith('MISSING_OR_UNSAFE') for x in b)

def test_unknown_effort_is_not_zero(case):
    root,r,use=case;assert r['effort']['active_seconds'] is None
    r['effort']['active_seconds']=10;assert 'UNSOURCED_EFFORT' in validate(root,r,use)['blockers']

def test_failure_cannot_be_closed_without_evidence(case):
    root,r,use=case;r['failures']=[{'id':'bad','status':'closed'}]
    assert 'UNSUPPORTED_DISPOSITION:bad' in validate(root,r,use)['blockers']
