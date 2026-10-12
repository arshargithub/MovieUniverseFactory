import json
import httpx
import pytest
from movie_factory.providers.gemini_reference_provider import run, payload

def test_free_tier_and_no_retry(tmp_path):
    calls=[]
    def handler(req):
        calls.append(req)
        return httpx.Response(429,json={'error':{'status':'RESOURCE_EXHAUSTED','code':429,'message':'private error'}})
    client=httpx.Client(base_url='https://generativelanguage.googleapis.com',transport=httpx.MockTransport(handler))
    with pytest.raises(ValueError):run(tmp_path,tmp_path/'out',free_tier_confirmed=False,client=client)
    result=run(tmp_path,tmp_path/'out',free_tier_confirmed=True,client=client)
    assert result['http_status']==429 and len(calls)==1
    assert 'private error' not in (tmp_path/'out/result.json').read_text()
    with pytest.raises(FileExistsError):run(tmp_path,tmp_path/'out',free_tier_confirmed=True,client=client)
    assert len(calls)==1
    assert json.loads((tmp_path/'out/request-ledger.json').read_text())['paid_spend_authorized_usd']==0

def test_response_and_nonleading_payload(tmp_path):
    client=httpx.Client(base_url='https://generativelanguage.googleapis.com',transport=httpx.MockTransport(
        lambda req:httpx.Response(200,json={'usageMetadata':{'totalTokenCount':20},'candidates':[]})))
    result=run(tmp_path,tmp_path/'out',free_tier_confirmed=True,client=client)
    assert result['usage']['totalTokenCount']==20
    assert 'harmonica' not in json.dumps(payload()).lower()
    assert 'tools' not in payload()
