import json,copy
import pytest
from movie_factory import retrospective as rt,production_knowledge as pk


def test_shared_response_packet_is_lossless_and_preserves_all_findings(monkeypatch):
    body=dict(cause='same cause '*900,test='same test '*400,evidence={'source':dict(path='source',sha256='a'*64)})
    responses={str(i):dict(body,event='response'+str(i),key=str(i),gate_digest=str(i)) for i in range(10)}
    state=dict(version=rt.VERSION,sequence=99,gates={str(i):dict(status='OPEN',reason='same unresolved issue') for i in range(10)},warnings={},responses=responses,proofs={})
    monkeypatch.setattr(rt,'fresh',lambda con,s:copy.deepcopy(state))
    p=rt.packet(None,{'brief':{}})
    assert p['response_encoding']=='shared_payloads_v1'
    assert len(json.dumps(p))<60000
    assert p['gates']==state['gates'] and rt.expand_packet_responses(p)==responses
    p['response_payloads'][next(iter(p['response_payloads']))]['cause']='tampered'
    with pytest.raises(Exception,match='PAYLOAD_CHANGED'):rt.expand_packet_responses(p)


def test_small_packet_remains_compatible(monkeypatch):
    value=dict(version=rt.VERSION,sequence=1,gates={},warnings={},responses={},proofs={})
    monkeypatch.setattr(rt,'fresh',lambda con,s:value)
    p=rt.packet(None,{'brief':{}})
    assert 'response_encoding' not in p and rt.expand_packet_responses(p)=={}
