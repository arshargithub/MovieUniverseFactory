"""Bounded free-tier non-music listening check; no taste scoring or retries."""
import base64,json,os,hashlib,sys
from pathlib import Path
import httpx
from .gemini_reference_provider import load_key,MODEL,redact_error
from ..telemetry import utc_now
ROOT=Path(__file__).resolve().parents[3]
def run(pronunciation_only=False,transport_control=False):
    out=ROOT/'.runtime/art-direction/series01-finish237'
    source=ROOT/'.runtime/art-direction/series01-audio223/provider'
    names=['finish237-voice-1.mp3','finish237-hoof-1.mp3','finish237-wind-1.mp3','turn-1.mp3']
    prompt=('This is technical voice and physical-foley QA, NOT music review. Listen to each labeled file independently. '
        'For the narration transcribe exactly what is spoken with approximate phrase start/end times. '
        'Describe pronunciation of the word after The, using phonetic plain English; desired word is Pathans, roughly puh-TAHNS, aspirated t not English th. '
        'Does the full author name sound intact? Describe unnatural breaks, mispronunciation or glitches, not a creative approval. '
        'For each effect describe what is actually audible, onset/offset of useful transients, any voices/music, clipping or unwanted events. '
        'For the hoof specify whether single/multiple impacts and whether it has low-mid weight or tinny sharpness. '
        'Do not infer sounds from filenames or requested intent. If audio unavailable say AUDIO_UNAVAILABLE. '
        'No music/taste recommendations, no claims about unseen footage. At most700words.')
    suffix=''
    if pronunciation_only:
        prior=json.loads((out/'audio-qc-result.json').read_text())
        if prior!={'state':'UNCERTAIN_NO_RETRY'}:raise ValueError('Diagnostic only after documented timeout')
        names=names[:1];suffix='-pronunciation'
        prompt='Listen to this narration. Transcribe the words exactly and give approximate phrase timestamps. How is the word after The pronounced? Describe its syllables and stress without assuming its spelling. Flag unintelligible words, cut syllables or audio glitches. No music or taste review. If audio inaccessible say AUDIO_UNAVAILABLE. Maximum200words.'
    if transport_control:
        prior=json.loads((out/'audio-qc-result-pronunciation.json').read_text())
        if prior!={'state':'UNCERTAIN_NO_RETRY'}:raise ValueError('Expected preserved failed diagnostic')
        suffix='-transport-control'
    parts=[];hashes={}
    for name in names:
        p=source/name
        if p.is_symlink() or not p.is_file() or p.stat().st_size>2000000:raise ValueError('Bounded media required')
        raw=p.read_bytes();hashes[name]=hashlib.sha256(raw).hexdigest()
        parts.extend([{'text':name},{'inlineData':{'mimeType':'audio/mpeg','data':base64.b64encode(raw).decode()}}])
    parts.append({'text':prompt})
    with (out/('audio-qc-request'+suffix+'.json')).open('x') as f:json.dump(dict(utc=utc_now(),files=hashes,prompt=prompt,model=MODEL,request_limit=1,automatic_retry=False,paid_authority_usd=0,tier='Director-reported free tier; account remaining quota unknown'),f)
    key=load_key(ROOT)
    try:
        with httpx.Client(base_url='https://generativelanguage.googleapis.com',headers={'x-goog-api-key':key},timeout=90,follow_redirects=False) as c:
            r=c.post(f'/v1beta/models/{MODEL}:generateContent',json={'contents':[{'parts':parts}],'generationConfig':{'maxOutputTokens':1200 if pronunciation_only else 4500}})
            d=r.json();result=dict(http_status=r.status_code,utc=utc_now(),usage=d.get('usageMetadata'))
            if r.status_code==200:result['text']='\n'.join(p.get('text','') for c in d.get('candidates',[]) for p in c.get('content',{}).get('parts',[]) if not p.get('thought'))
            else:result['error']=redact_error(d.get('error',{}).get('message',''),key)
    except (httpx.HTTPError,ValueError) as exc:result={'state':'UNCERTAIN_NO_RETRY','error_type':type(exc).__name__}
    (out/('audio-qc-result'+suffix+'.json')).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':
    if sys.argv[1:] not in ([],['pronunciation'],['transport-control']):raise ValueError('Closed request')
    run(sys.argv[1:]==['pronunciation'],sys.argv[1:]==['transport-control'])
