"""Synthetic control tests; none is a visual/production qualification."""
import copy
import json
from pathlib import Path
import pytest
from movie_factory import review_control as rc
from movie_factory import production_knowledge as pk


def put(root, name, value):
    p=root/name; p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(value) if not isinstance(value,str) else value)


def b(root, name):
    return {'path':name,'sha256':pk.file_hash(root/name)}


@pytest.fixture
def fixture(tmp_path,monkeypatch):
    root=tmp_path
    for name in ['candidate.bin','evidence.txt','task.json',
                 'src/movie_factory/review_control.py','src/movie_factory/production_knowledge.py']:
        put(root,name,{} if name.endswith('.json') else 'SYNTHETIC')
    fresh={'dispatch_ready':True,'packet_digest':'knowledge-v1','obligations':[{'id':'quality'}]}
    monkeypatch.setattr(pk,'task_packet',lambda root,task:copy.deepcopy(fresh))
    c={'schema':1,'id':'fixture','intent':'SYNTHETIC ONLY', 'protected':['original'],
       'exclusions':['final release'],'production_approval':False,
       'requirements':[{'id':'shape','criterion':'SYNTHETIC readable form','modes':['image']}],
       'knowledge_mapping':{'quality':{'checks':['shape'],'reason':'explicit fixture mapping'}}}
    s={'schema':1,'contract_id':'fixture','checks':{'shape':'FAIL'},
       'defects':[{'id':'D1','requirement':'shape','status':'OPEN','description':'synthetic failure'}],
       'artifacts':{'candidate':b(root,'candidate.bin')},'bindings':{'source':b(root,'task.json')},
       'knowledge_task':'task.json','knowledge_digest':'knowledge-v1',
       'capabilities':{m:m not in {'direct_audio','direct_motion'} for m in rc.MODES}}
    put(root,'contract.json',c);put(root,'state.json',s)
    put(root,rc.REGISTRY,{'contract':b(root,'contract.json'),'state':b(root,'state.json')})
    review={'fingerprint':rc.load(root)[2],'purpose':'scoped_review','candidate':s['artifacts'],
            'evidence':{'E1':{'binding':b(root,'evidence.txt'),'mode':'image',
                             'observation_scope':'Synthetic fixture region',
                             'candidate_digest':pk.digest(s['artifacts'])}},
            'checks':[{'id':'shape','status':'PASS','observation':'Synthetic fit',
                       'comparison':'Synthetic accepted control','evidence':['E1']}],
            'defect_closures':{'D1':{'test':'Synthetic falsification','observation':'No synthetic defect','evidence':['E1']}},
            'adjacent_review':{'status':'PASS','observation':'Synthetic adjacent check','evidence':['E1']}}
    return root,c,s,review,fresh


def test_complete_synthetic_receipt_never_production(fixture):
    root,_,_,r,_=fixture
    result=rc.deliver(root,r,'out/receipt.json')
    assert result['ready_for_scoped_review'] is True
    assert result['production_approved'] is result['director_approved'] is False
    assert (root/'out/receipt.json').exists()
    with pytest.raises(FileExistsError):rc.deliver(root,r,'out/receipt.json')


@pytest.mark.parametrize('status',['FAIL','NOT_RUN','YELLOW','DEFERRED',None])
def test_bad_status_does_not_deliver(fixture,status):
    root,_,_,r,_=fixture;r['checks'][0]['status']=status
    assert not rc.deliver(root,r,'out/receipt.json')['ready_for_scoped_review']
    assert not (root/'out/receipt.json').exists()


@pytest.mark.parametrize('purpose',['development','diagnostic','production','director_approved',None])
def test_label_cannot_waive(fixture,purpose):
    root,_,_,r,_=fixture;r['purpose']=purpose
    assert 'UNSUPPORTED_HANDOFF_PURPOSE' in rc.assess(root,r)['failures']


@pytest.mark.parametrize('mutation',[
    'stale_review','candidate','missing_check','extra_check','duplicate_check','missing_observation',
    'missing_comparison','missing_evidence','stale_evidence','wrong_candidate_evidence',
    'unavailable_mode','wrong_mode','missing_closure','unknown_closure','missing_closure_test',
    'closure_wrong_evidence','adjacent_fail','adjacent_no_evidence','stale_source','stale_contract',
    'stale_state','stale_candidate','stale_engine','stale_knowledge'])
def test_injected_failures(fixture,mutation):
    root,c,s,r,fresh=fixture
    if mutation=='stale_review':r['fingerprint']='old'
    elif mutation=='candidate':r['candidate']={}
    elif mutation=='missing_check':r['checks']=[]
    elif mutation=='extra_check':r['checks'].append(dict(r['checks'][0],id='unknown'))
    elif mutation=='duplicate_check':r['checks']*=2
    elif mutation=='missing_observation':r['checks'][0]['observation']=''
    elif mutation=='missing_comparison':r['checks'][0]['comparison']=''
    elif mutation=='missing_evidence':r['checks'][0]['evidence']=[]
    elif mutation=='stale_evidence':put(root,'evidence.txt','changed')
    elif mutation=='wrong_candidate_evidence':r['evidence']['E1']['candidate_digest']='old'
    elif mutation=='unavailable_mode':r['evidence']['E1']['mode']='direct_audio'
    elif mutation=='wrong_mode':r['evidence']['E1']['mode']='technical'
    elif mutation=='missing_closure':r['defect_closures']={}
    elif mutation=='unknown_closure':r['defect_closures']['new']=r['defect_closures']['D1']
    elif mutation=='missing_closure_test':r['defect_closures']['D1']['test']=''
    elif mutation=='closure_wrong_evidence':r['defect_closures']['D1']['evidence']=['unknown']
    elif mutation=='adjacent_fail':r['adjacent_review']['status']='FAIL'
    elif mutation=='adjacent_no_evidence':r['adjacent_review']['evidence']=[]
    elif mutation=='stale_source':put(root,'task.json',{'changed':True})
    elif mutation=='stale_contract':put(root,'contract.json',dict(c,requirements=[]))
    elif mutation=='stale_state':put(root,'state.json',dict(s,defects=[]))
    elif mutation=='stale_candidate':put(root,'candidate.bin','different')
    elif mutation=='stale_engine':put(root,'src/movie_factory/review_control.py','different')
    elif mutation=='stale_knowledge':fresh['packet_digest']='changed'
    try:result=rc.deliver(root,r,'out/receipt.json')
    except (rc.Blocked,pk.KnowledgeError):result={'ready_for_scoped_review':False}
    assert result['ready_for_scoped_review'] is False
    assert not (root/'out/receipt.json').exists()


@pytest.mark.parametrize('bad',['../outside','/tmp/out','.env','.git/config','.aws/credentials'])
def test_path_boundaries(fixture,bad):
    with pytest.raises(rc.Blocked):rc.path(fixture[0],bad)


def test_symlink_escape(fixture,tmp_path_factory):
    root,*_=fixture;outside=tmp_path_factory.mktemp('outside')/'file';outside.write_text('x')
    (root/'alias').symlink_to(outside)
    with pytest.raises(rc.Blocked):rc.path(root,'alias')


def test_repeat_state_has_no_builder_verdict(fixture):
    root,_,s,_,_=fixture
    first=rc.capsule(root);second=rc.capsule(root)
    assert first==second
    assert first['open_defects']==s['defects']
    assert 'builder' not in first


def test_changed_scope_cannot_keep_review(fixture):
    root,c,_,r,_=fixture
    c['requirements'][0]['criterion']='Different acceptance'
    put(root,'contract.json',c)
    registry=rc.read(root,rc.REGISTRY);registry['contract']=b(root,'contract.json')
    put(root,rc.REGISTRY,registry)
    assert 'STALE_REVIEW' in rc.assess(root,r)['failures']


def test_cli_malformed_input_fails_closed(fixture,capsys):
    root,*_=fixture;put(root,'bad.json',{'checks':'bad'})
    assert rc.main(['--root',str(root),'deliver','--review','bad.json','--output','receipt.json'])==2
    assert not (root/'receipt.json').exists()


@pytest.mark.parametrize('field,value', [('adjacent_review', None), ('evidence', {'E1': None}),
                                        ('defect_closures', None)])
def test_malformed_nested_input_fails_closed(fixture,field,value,capsys):
    root,_,_,review,_=fixture
    review[field]=value;put(root,'bad.json',review)
    assert rc.main(['--root',str(root),'deliver','--review','bad.json','--output','receipt.json'])==2
    assert not (root/'receipt.json').exists()
