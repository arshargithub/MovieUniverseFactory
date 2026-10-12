"""One-request, free-tier-only public-reference pilot. No billing or retry route."""
import json
import os
import re
from pathlib import Path
import httpx
from ..settings import _read_dotenv
from ..telemetry import utc_now
from .runway_provider import save_json

URL = 'https://www.youtube.com/watch?v=O9QgHF1gtC8'
MODEL = 'gemini-3.8-flash'
PROMPT = ('Analyze only the audible music from 01:10 to 01:45 of this video. '
          'Do not use the title, imagery, lyrics, or prior knowledge to infer musical events. '
          'If audio is inaccessible, say AUDIO_UNAVAILABLE and do not guess. '
          'Give a short timestamped account of changes in lead sound, rhythm, texture and energy; '
          'identify the most prominent transition and approximate onset. Distinguish likely '
          'instrument identification from certainty. Describe what is audible, not a transcription '
          'or reproduction of the melody or lyrics. No web search. Maximum 350 words.')

def payload():
    return {'contents':[{'parts':[{'fileData':{'fileUri':URL}}, {'text':PROMPT}]}],
            'generationConfig':{'maxOutputTokens':3000}}

def redact_error(value, key=''):
    """Retain diagnostic explanation, excluding credentials/account identifiers."""
    text = str(value)
    if key:
        text = text.replace(key, '[REDACTED]')
    text = re.sub(r'AIza[\w-]{20,}', '[REDACTED]', text)
    text = re.sub(r'projects/[\w-]+', 'projects/[REDACTED]', text)
    return text[:4000]

def load_key(root):
    p=Path(root)/'.env'; expected=Path.home()/'.config/movie-factory/.env'
    if p.is_symlink() and (p.resolve(strict=True)!=expected or p.lstat().st_uid!=os.getuid()):
        raise ValueError('Unapproved credential link')
    values=_read_dotenv(p.resolve(strict=True))
    key=values.get('GEMINI_API_KEY','')
    if not key: raise ValueError('Gemini credential missing')
    return key

def run(root, output, *, free_tier_confirmed, client=None):
    if free_tier_confirmed is not True: raise ValueError('Free tier confirmation required')
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    claim=out/'request-ledger.json'
    # Fixed single-request campaign. An uncertain or failed request is never retried.
    with os.fdopen(os.open(claim,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w') as f:
        json.dump({'utc':utc_now(),'campaign':'music-reference229-38','request_limit':1,
                   'paid_spend_authorized_usd':0,'tier_basis':'Director reports free tier',
                   'estimated_cost_usd':0,'actual_cost_usd':None,'model':MODEL,
                   'payload':payload(),'state':'CLAIMED_NO_RETRY'},f)
        f.flush();os.fsync(f.fileno())
    owned=client is None
    key=''
    if owned:
        key=load_key(root)
        client=httpx.Client(base_url='https://generativelanguage.googleapis.com',
                            headers={'x-goog-api-key':key},timeout=90,
                            follow_redirects=False)
    try:
        response=client.post(f'/v1beta/models/{MODEL}:generateContent',json=payload())
        result={'utc':utc_now(),'http_status':response.status_code,'model':MODEL,
                'actual_cost_usd':None,'billing':'No invoice check; user-reported free tier',
                'retry':False}
        if response.status_code==200:
            data=response.json()
            result.update(usage=data.get('usageMetadata'),
                          candidates=data.get('candidates',[]),
                          prompt_feedback=data.get('promptFeedback'),
                          provider_model=data.get('modelVersion'))
        else:
            # Keep useful error semantics, never request headers or secret values.
            try:
                error=response.json().get('error',{})
                result.update(error_status=error.get('status'),error_code=error.get('code'))
                result['error_message']=redact_error(error.get('message',''), key)
            except (ValueError,AttributeError): pass
        save_json(out/'result.json',result)
        return result
    except httpx.HTTPError:
        result={'state':'NETWORK_ERROR_OR_UNCERTAIN','retry':False,'actual_cost_usd':None}
        save_json(out/'result.json',result)
        return result
    finally:
        if owned: client.close()
