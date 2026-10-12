import json
import httpx
import pytest
from movie_factory.providers.gemini_music_batch import run, payload, TRACKS, continue_after_503, complete_remaining


def test_budget_pacing_and_no_retry(tmp_path):
    now = [100.0]
    starts = []
    def handler(req):
        starts.append(now[0])
        return httpx.Response(200, json={'usageMetadata': {'promptTokenCount': 20000}, 'candidates': [{'finishReason': 'STOP', 'content': {'parts': [{'text': 'Timestamped observations'}, {'thoughtSignature': 'omit'}]}}]})
    with httpx.Client(transport=httpx.MockTransport(handler), base_url='https://example.test') as client:
        result = run(tmp_path, tmp_path/'out', free_tier_confirmed=True, client=client,
                     clock=lambda: now[0], sleep=lambda n: now.__setitem__(0, now[0]+n))
        assert len(result) == 5 and starts == [100,125,150,175,200]
        assert all(x['complete_response'] for x in result)
        with pytest.raises(FileExistsError):
            run(tmp_path, tmp_path/'out', free_tier_confirmed=True, client=client)
    assert 'thoughtSignature' not in (tmp_path/'out'/'summary.json').read_text()


def test_stop_quota_and_require_confirmation(tmp_path):
    with pytest.raises(ValueError):
        run(tmp_path, tmp_path/'out', free_tier_confirmed=False)
    calls=[]
    def handler(req):
        calls.append(req)
        return httpx.Response(429, headers={'retry-after': '60'}, json={'error': {'message': 'quota projects/secret'}})
    with httpx.Client(transport=httpx.MockTransport(handler), base_url='https://example.test') as c:
        r=run(tmp_path,tmp_path/'out',free_tier_confirmed=True,client=c)
    assert len(calls)==1 and r[0]['retry_after']=='60'
    assert 'projects/secret' not in json.dumps(r)


def test_focus_and_no_leading_instrument():
    for t in TRACKS:
        p=payload(t)
        assert t[3] in p['contents'][0]['parts'][0]['fileData']['fileUri']
        assert t[4] in p['contents'][0]['parts'][1]['text']
        assert 'harmonica' not in json.dumps(p).lower()


def test_bounded_explicit_503_recovery(tmp_path):
    n=[0]
    def handler(req):
        n[0]+=1
        if n[0]==2:
            return httpx.Response(503,json={'error':{'message':'temporary high demand'}})
        return httpx.Response(200,json={'candidates':[{'finishReason':'STOP','content':{'parts':[{'text':'observed'}]}}]})
    with httpx.Client(transport=httpx.MockTransport(handler),base_url='https://example.test') as c:
        run(tmp_path,tmp_path/'out',free_tier_confirmed=True,client=c,sleep=lambda n: None)
        r=continue_after_503(tmp_path,tmp_path/'out',free_tier_confirmed=True,client=c,sleep=lambda n: None)
        assert n[0]==6 and [v['track_id'] for v in r]==['cosmic','rise','dawn','calls']
        with pytest.raises(FileExistsError):
            continue_after_503(tmp_path,tmp_path/'out',free_tier_confirmed=True,client=c)


def test_final_combined_sixth_request(tmp_path):
    n=[0]
    def handler(req):
        n[0]+=1
        if n[0] in (2,5):
            return httpx.Response(503,json={'error':{'message':'high demand'}})
        return httpx.Response(200,json={'candidates':[{'finishReason':'STOP','content':{'parts':[{'text':'A and B observations'}]}}]})
    with httpx.Client(transport=httpx.MockTransport(handler),base_url='https://example.test') as c:
        run(tmp_path,tmp_path/'out',free_tier_confirmed=True,client=c,sleep=lambda n:None)
        continue_after_503(tmp_path,tmp_path/'out',free_tier_confirmed=True,client=c,sleep=lambda n:None)
        complete_remaining(tmp_path,tmp_path/'out',free_tier_confirmed=True,client=c)
        assert n[0]==6
        with pytest.raises(FileExistsError):
            complete_remaining(tmp_path,tmp_path/'out',free_tier_confirmed=True,client=c)
    p=json.loads((tmp_path/'out'/'final'/'remaining'/'request-ledger.json').read_text())['payload']
    assert sum('fileData' in x for x in p['contents'][0]['parts'])==2
