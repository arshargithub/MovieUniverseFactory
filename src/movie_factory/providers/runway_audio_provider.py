"""Bounded AUDIO-220 developer-API preview. No POST retry or budget escalation.

Reuse only the trusted credential/transport interface, never the video submitter.
The initial $3 ceiling stays enforced; the conditional extra $2 requires a later
evidence-bound implementation/review, not a CLI flag. Unknown charges stay held.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import uuid
from urllib.parse import urlparse
import httpx
from ..budget import BudgetLedger
from ..telemetry import utc_now
from .runway_provider import RunwayProvider, RunwayError, load_runway_key, save_json


def validate_payload(payload):
    """Strict small audio allowlist; estimates reserve whole published units."""
    model = payload.get('model')
    prompt = payload.get('promptText')
    if not isinstance(prompt, str) or not 1 <= len(prompt.encode('utf-16-le'))//2 <= 1000:
        raise RunwayError('Audio prompt must contain 1-1000 UTF-16 units')
    if model == 'eleven_v3':
        allowed = {'model','promptText','voice','languageCode','speed','stability','style','seed'}
        if payload.get('voice') not in [{'type':'runway-preset','presetId':v} for v in ('Tom','Kirk')]:
            raise RunwayError('Only the two scoped voice audition presets are allowed')
        for key, lo, hi in [('speed',.7,1.2),('stability',0,1),('style',0,1)]:
            value = payload.get(key, 1 if key=='speed' else .5)
            if type(value) not in (int,float) or not math.isfinite(value) or not lo<=value<=hi:
                raise RunwayError('Invalid speech setting')
        if payload.get('languageCode','en') != 'en': raise RunwayError('English script only')
        if type(payload.get('seed',303)) is not int or not 0<=payload.get('seed',303)<=4294967295:
            raise RunwayError('Invalid seed')
        credits=max(5,math.ceil((len(prompt.encode('utf-16-le'))//2)/50))
        endpoint='/v1/text_to_speech'
    elif model == 'eleven_text_to_sound_v2':
        allowed={'model','promptText','duration','loop'}
        duration=payload.get('duration')
        if type(duration) not in (int,float) or not math.isfinite(duration) or not .5<=duration<=20:
            raise RunwayError('Explicit 0.5-20 second effect duration required')
        if type(payload.get('loop',False)) is not bool: raise RunwayError('Invalid loop')
        credits=math.ceil(duration); endpoint='/v1/sound_effect'
    elif model == 'seed_audio':
        allowed={'model','promptText','outputFormat','sampleRate'}
        if payload.get('outputFormat')!='wav' or payload.get('sampleRate')!=48000:
            raise RunwayError('SeedAudio proof must be WAV 48kHz')
        # Documented maximum120s *.25 credits/s, not prompt-requested duration.
        credits=30; endpoint='/v1/sound_effect'
    else: raise RunwayError('Unapproved audio model')
    if set(payload)-allowed: raise RunwayError('Unsupported payload fields')
    return endpoint,credits/100


class AudioProvider(RunwayProvider):
    def __init__(self, root, output, *, client=None):
        self.output=Path(output); self.output.mkdir(parents=True,exist_ok=True)
        self.ledger=BudgetLedger(self.output/'budget.jsonl',campaign_limit=5,
            scope_limits={'scored':3,'contingency':2},stage_limits={'audio':(5,30)},
            request_limit=30,request_ceiling_usd=.30,work_item_attempt_limit=3,
            additional_campaign_ceiling_usd=3)
        if client is None:
            key=load_runway_key(root)
            if not key: raise RunwayError('RUNWAY_API_KEY missing')
            client=httpx.Client(base_url='https://api.dev.runwayml.com',headers={
                'Authorization':'Bearer '+key,'X-Runway-Version':'2024-11-06'},
                timeout=60,follow_redirects=False)
        self.client=client

    def submit_audio(self,name,payload,attempt=1):
        endpoint,cost=validate_payload(payload)
        if not re.fullmatch(r'[a-z][a-z0-9-]{0,50}',name) or attempt not in (1,2,3):
            raise RunwayError('Invalid work item')
        path=self.output/f'{name}-{attempt}.json'
        try: fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        except FileExistsError: raise RunwayError('Already claimed; poll/reconcile, never redispatch') from None
        with os.fdopen(fd,'w') as f: f.write('{"status":"CLAIMED"}\n'); f.flush(); os.fsync(f.fileno())
        reservation=self.ledger.reserve(run_id='AUDIO-220',stage='audio',
            scope='scored' if attempt==1 else 'contingency',amount_usd=cost,
            purpose=name,model=payload['model'],prompt_hash=hashlib.sha256(payload['promptText'].encode()).hexdigest())
        record={'name':name,'attempt':attempt,'status':'DISPATCH_UNCERTAIN',
            'reservation_id':reservation,'payload':payload,'reserved_usd':cost,
            'submitted_utc':utc_now(),'actual_cost_usd':None}
        save_json(path,record)
        data=self._request('POST',endpoint,payload)
        try: task_id=str(uuid.UUID(data['id']))
        except (ValueError,KeyError,TypeError): raise RunwayError('Missing task ID; reservation retained') from None
        record.update(task_id=task_id,status='PENDING');save_json(path,record)
        return {'name':name,'task_id':task_id,'status':'PENDING','reserved_usd':cost}

    def fetch_audio(self,name,attempt=1):
        if not re.fullmatch(r'[a-z][a-z0-9-]{0,50}',name) or attempt not in (1,2,3):
            raise RunwayError('Invalid work item')
        path=self.output/f'{name}-{attempt}.json'; record=json.loads(path.read_text())
        if record.get('status')!='SUCCEEDED' or len(record.get('output',[]))!=1:
            raise RunwayError('Expected one successful audio output')
        url=record['output'][0]; parsed=urlparse(url);host=parsed.hostname or ''
        if parsed.scheme!='https' or parsed.username or parsed.password or not any(
            host==d or host.endswith('.'+d) for d in ('runwayml.com','runwayml.cloud','cloudfront.net','runwaycdn.com')):
            raise RunwayError('Output host requires review')
        ext='.wav' if record['payload']['model']=='seed_audio' else '.mp3'
        dest=self.output/f'{name}-{attempt}{ext}';partial=dest.with_suffix(ext+'.partial')
        if dest.exists(): raise RunwayError('Output exists; verify, do not overwrite')
        size=0;digest=hashlib.sha256()
        try:
            with httpx.stream('GET',url,timeout=60,follow_redirects=False) as r:
                r.raise_for_status()
                with partial.open('xb') as f:
                    for chunk in r.iter_bytes():
                        size+=len(chunk)
                        if size>60_000_000: raise RunwayError('Output exceeds60MB')
                        digest.update(chunk);f.write(chunk)
                    f.flush();os.fsync(f.fileno())
            partial.rename(dest)
        except Exception: raise RunwayError('Audio download incomplete; no generation retried') from None
        record.update(local_file=dest.name,output_sha256=digest.hexdigest(),output_bytes=size)
        save_json(path,record)
        return {'name':name,'path':str(dest),'bytes':size,'sha256':digest.hexdigest()}


def main():
    p=argparse.ArgumentParser();p.add_argument('command',choices=['account','submit','poll','download','budget'])
    p.add_argument('--output',type=Path,required=True);p.add_argument('--name');p.add_argument('--payload',type=Path)
    p.add_argument('--attempt',type=int,choices=[1,2],default=1);a=p.parse_args()
    try:
        provider=AudioProvider(Path.cwd(),a.output)
        if a.command=='submit': result=provider.submit_audio(a.name,json.loads(a.payload.read_text()),a.attempt)
        elif a.command=='download': result=provider.fetch_audio(a.name,a.attempt)
        elif a.command=='poll': result=provider.poll(a.name,a.attempt)
        elif a.command=='account': result=provider.account()
        else: result=provider.ledger.summary()
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({'error':str(e) if isinstance(e,RunwayError) else type(e).__name__}));raise SystemExit(1) from None

if __name__=='__main__': main()
