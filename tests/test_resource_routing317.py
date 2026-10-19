import json
from pathlib import Path
from movie_factory import production_knowledge as pk
from test_production_knowledge import root,task
from test_resource_manifest import case

def test_declared_resource_gate_is_enforced_by_packet(root,case):
    fixture,r,use=case
    (root/'fixture').write_text('synthetic')
    (root/'resource.json').write_text(json.dumps(r));(root/'conditions.json').write_text(json.dumps(use))
    t=task(root,'knowledge',['knowledge']);t['resource_uses']=[{'manifest':'resource.json','conditions':'conditions.json'}]
    assert 'UNBOUND_RESOURCE_USE' in pk.task_packet(root,t)['blockers']
    for p in ('resource.json','conditions.json'):t['inputs'][p]=pk.file_hash(root/p)
    assert pk.task_packet(root,t)['dispatch_ready']
    r['failures']=[{'id':'hoof','status':'open'}];(root/'resource.json').write_text(json.dumps(r));t['inputs']['resource.json']=pk.file_hash(root/'resource.json')
    assert 'RESOURCE:fixture:OPEN_FAILURE:hoof' in pk.task_packet(root,t)['blockers']

def test_changed_artifact_invalidates_otherwise_bound_resource(root,case):
    fixture,r,use=case;(root/'fixture').write_text('changed')
    (root/'resource.json').write_text(json.dumps(r));(root/'conditions.json').write_text(json.dumps(use))
    t=task(root,'knowledge',['knowledge']);t['resource_uses']=[{'manifest':'resource.json','conditions':'conditions.json'}]
    for p in ('resource.json','conditions.json'):t['inputs'][p]=pk.file_hash(root/p)
    assert not pk.task_packet(root,t)['dispatch_ready']
