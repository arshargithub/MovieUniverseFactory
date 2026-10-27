"""Lossless context transport, not semantic filtering or a perceptual test."""
import json
from copy import deepcopy
import pytest
from movie_factory import retrospective as rt,production_knowledge as pk,production_workflow as wf


def source():
    triggers=['native-review:sikh-c'+str(i)+'-revealing-frame-failed' for i in range(500)]
    return dict(gates={str(i):dict(status='OPEN',reason='unresolved',triggers=triggers[i:]) for i in range(8)},
        responses={},pending_effects386={},instruction='Original',sequence=500)


def test_every_trigger_and_gate_digest_roundtrips():
    original=source();saved=deepcopy(original);encoded=rt.encode_trigger_dictionary(original)
    assert original==saved
    assert rt.expand_packet_gates(encoded)==original['gates']
    assert len(json.dumps(encoded))<len(json.dumps(original))
    for key in original['gates']:assert rt.gate_digest(encoded,key)==pk.digest(original['gates'][key])
    assert sum(len(g['triggers']) for g in rt.expand_packet_gates(encoded).values())==sum(len(g['triggers']) for g in original['gates'].values())


@pytest.mark.parametrize('mutation',['index','table','digest','missing'])
def test_transport_corruption_cannot_change_a_finding(mutation):
    value=rt.encode_trigger_dictionary(source())
    if mutation=='index':value['gates']['0']['triggers'][0]=999999
    if mutation=='table':value['trigger_events386'][0]='fabricated'
    if mutation=='digest':value['gate_digests386']['0']='0'*64
    if mutation=='missing':del value['gate_digests386']['0']
    with pytest.raises(wf.Blocked):rt.expand_packet_gates(value)


def test_legacy_and_closed_gate_semantics_unchanged():
    p={'gates':{'closed':dict(status='CLOSED',evaluation='actual_effect')}}
    assert rt.expand_packet_gates(p)==p['gates']
    encoded=rt.encode_trigger_dictionary(p)
    assert rt.expand_packet_gates(encoded)==p['gates']
    assert 'triggers' not in encoded['gates']['closed']
