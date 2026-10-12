import json
import uuid
import httpx
import pytest
from movie_factory.providers.runway_audio_provider import AudioProvider,validate_payload
from movie_factory.providers.runway_provider import RunwayError
from movie_factory.budget import BudgetExceeded

def voice():
    return {'model':'eleven_v3','promptText':'We call them martial races.',
            'voice':{'type':'runway-preset','presetId':'Tom'}}

def test_bounds():
    assert validate_payload(voice())[1]==.05
    assert validate_payload({'model':'seed_audio','promptText':'Instrumental','outputFormat':'wav','sampleRate':48000})[1]==.30
    for extra in [{'model':'gen4.5'},{'speed':float('nan')},{'voice':{'type':'reference-audio'}},{'unknown':True}]:
        with pytest.raises(RunwayError): validate_payload({**voice(),**extra})
    with pytest.raises(RunwayError): validate_payload({'model':'eleven_text_to_sound_v2','promptText':'hoof'})

def test_reserve_before_post_and_no_duplicate(tmp_path):
    seen=[]
    def handler(request):
        assert p.ledger.summary()['committed_usd']==.05
        seen.append(request);return httpx.Response(200,json={'id':str(uuid.uuid4())})
    p=AudioProvider(tmp_path,tmp_path/'audio',client=httpx.Client(base_url='https://api.dev.runwayml.com',transport=httpx.MockTransport(handler)))
    p.submit_audio('tom',voice())
    with pytest.raises(RunwayError): p.submit_audio('tom',voice())
    assert len(seen)==1
    assert p.ledger.summary()['reserved_unknown_usd']==.05

def test_error_redacted_and_reservation_retained(tmp_path):
    p=AudioProvider(tmp_path,tmp_path/'audio',client=httpx.Client(base_url='https://api.dev.runwayml.com',transport=httpx.MockTransport(lambda r:httpx.Response(500,text='secret-do-not-print'))))
    with pytest.raises(RunwayError,match='HTTP 500'): p.submit_audio('tom',voice())
    assert p.ledger.summary()['reserved_unknown_usd']==.05
    assert 'secret' not in (tmp_path/'audio/tom-1.json').read_text()

def test_initial_cap_survives_restart(tmp_path):
    p=AudioProvider(tmp_path,tmp_path/'audio',client=object())
    for i in range(10): p.ledger.reserve(run_id='AUDIO-220',stage='audio',scope='scored',purpose=str(i),amount_usd=.3)
    p=AudioProvider(tmp_path,tmp_path/'audio',client=object())
    with pytest.raises(BudgetExceeded): p.ledger.reserve(run_id='AUDIO-220',stage='audio',scope='contingency',purpose='extra',amount_usd=.05)

def test_no_auth_to_arbitrary_download_host(tmp_path):
    p=AudioProvider(tmp_path,tmp_path/'audio',client=object())
    (tmp_path/'audio/tom-1.json').write_text(json.dumps({'status':'SUCCEEDED','output':['https://evil.example/x.mp3']}))
    with pytest.raises(RunwayError,match='host'): p.fetch_audio('tom')
