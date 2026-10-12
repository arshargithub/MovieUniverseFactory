import json
import httpx
import pytest
from movie_factory.providers import gemini_audition_review as m


def test_bounded_generated_audio_review(tmp_path,monkeypatch):
    with pytest.raises(ValueError):m.run(tmp_path,free_tier_confirmed=False)
    out=tmp_path/'.runtime/art-direction/series01-music231';out.mkdir(parents=True)
    for n in ['harmonica','synth']:(out/f'audition-{n}.mp3').write_bytes(b'fake-test-audio')
    calls=[]
    def handler(req):
        calls.append(req)
        return httpx.Response(200,json={'candidates':[{'finishReason':'STOP','content':{'parts':[{'text':'Review'}, {'thoughtSignature':'omit'}]}}],'usageMetadata':{'totalTokenCount':100}})
    original=httpx.Client
    monkeypatch.setattr(m,'load_key',lambda root:'secret-test')
    monkeypatch.setattr(m.httpx,'Client',lambda **kw:original(transport=httpx.MockTransport(handler),**kw))
    r=m.run(tmp_path,free_tier_confirmed=True)
    assert r['text']=='Review\n' and len(calls)==1
    p=json.loads(calls[0].content)
    assert sum('inlineData' in x for x in p['contents'][0]['parts'])==2
    with pytest.raises(FileExistsError):m.run(tmp_path,free_tier_confirmed=True)
    assert 'secret-test' not in (out/'review-request.json').read_text()
    assert 'fake-test-audio' not in (out/'review-request.json').read_text()
    assert 'thoughtSignature' not in (out/'model-review.json').read_text()

def test_single_sketch_and_guarded_retry(tmp_path,monkeypatch):
    out=tmp_path/'.runtime/art-direction/series01-music233';out.mkdir(parents=True)
    (out/'sketch.mp3').write_bytes(b'fake-sketch')
    with pytest.raises(ValueError):m.run(tmp_path,free_tier_confirmed=True,campaign='arbitrary')
    requests=[]
    def handler(req):
        requests.append(json.loads(req.content))
        return httpx.Response(503,json={'error':{'message':'overloaded'}})
    original=httpx.Client
    monkeypatch.setattr(m,'load_key',lambda root:'secret-test')
    monkeypatch.setattr(m.httpx,'Client',lambda **kw:original(transport=httpx.MockTransport(handler),**kw))
    m.run(tmp_path,free_tier_confirmed=True,campaign='music233')
    m.run(tmp_path,free_tier_confirmed=True,campaign='music233',attempt=2)
    assert len(requests)==2
    assert sum('inlineData' in x for x in requests[0]['contents'][0]['parts'])==1
    assert requests[0]['contents'][0]['parts'][-1]['text']==m.SKETCH_PROMPT
    with pytest.raises(FileExistsError):m.run(tmp_path,free_tier_confirmed=True,campaign='music233',attempt=2)
    with pytest.raises(ValueError):m.run(tmp_path,free_tier_confirmed=True,campaign='music233',attempt=3)
