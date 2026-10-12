"""Bounded diagnostic only; no billing, uploads, automatic retries or production edits."""
import argparse
import json
import os
from pathlib import Path
import re
import time
import httpx
from movie_factory.providers.gemini_reference_provider import load_key, payload, MODEL
from movie_factory.production_knowledge import task_packet
from movie_factory.telemetry import utc_now

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '.runtime/art-direction/series01-music-reference229/diagnosis'
TASK = ROOT / 'docs/knowledge/pilot/tasks/music229-diagnosis.json'

def clean(value, key):
    """Retain useful error semantics without credentials or account identifiers."""
    if isinstance(value, dict):
        return {k: clean(v, key) for k, v in value.items()
                if k.lower() not in {'authorization', 'x-goog-api-key', 'apikey', 'api_key'}}
    if isinstance(value, list):
        return [clean(v, key) for v in value]
    if isinstance(value, str):
        value = value.replace(key, '[REDACTED]') if key else value
        value = re.sub(r'AIza[\w-]{20,}', '[REDACTED]', value)
        value = re.sub(r'projects/[\w-]+', 'projects/[REDACTED]', value)
        return value
    return value

def request_body(case):
    if case == 'original':
        return payload()
    if case == 'text':
        return {'contents': [{'parts': [{'text': 'Reply with OK only.'}]}],
                'generationConfig': {'maxOutputTokens': 32, 'thinkingConfig': {'thinkingBudget': 0}}}
    if case == 'control_video':
        return {'contents': [{'parts': [
            {'fileData': {'fileUri': 'https://www.youtube.com/watch?v=9hE5-98ZeCg'}},
            {'text': 'Describe one audible event in the first ten seconds. If audio is inaccessible say AUDIO_UNAVAILABLE. Do not infer from imagery.'}]}],
            'generationConfig': {'maxOutputTokens': 120, 'thinkingConfig': {'thinkingBudget': 0}}}
    raise ValueError('Unknown diagnostic case')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('case', choices=['original', 'text', 'control_video'])
    args = parser.parse_args()
    packet = task_packet(ROOT, json.loads(TASK.read_text()))
    if not packet['dispatch_ready']:
        raise SystemExit('Knowledge dispatch blocked')
    OUT.mkdir(parents=True, exist_ok=True)
    # One dispatch per defined case; quota/access rejection prevents further calls.
    for prior in OUT.glob('*-result.json'):
        if json.loads(prior.read_text()).get('http_status') in {401, 403, 429}:
            raise SystemExit('Credential/access/quota failure: no further calls')
    body = request_body(args.case)
    claim = {'utc': utc_now(), 'case': args.case, 'model': MODEL, 'payload': body,
             'packet_digest': packet['packet_digest'], 'paid_authority_usd': 0,
             'tier_basis': 'Director reports free tier', 'actual_cost_usd': None,
             'max_cases': 3, 'automatic_retries': 0}
    with (OUT / (args.case + '-claim.json')).open('x') as f:
        json.dump(claim, f, indent=2)
        f.flush(); os.fsync(f.fileno())
    key = load_key(ROOT)
    started = time.monotonic()
    with httpx.Client(base_url='https://generativelanguage.googleapis.com',
                      headers={'x-goog-api-key': key}, timeout=90, follow_redirects=False) as client:
        try:
            response = client.post(f'/v1beta/models/{MODEL}:generateContent', json=body)
            try:
                data = response.json()
            except ValueError:
                data = {'non_json_body': response.text[:4000]}
            result = {'utc': utc_now(), 'http_status': response.status_code,
                      'request_path': response.request.url.path,
                      'body': clean(data, key), 'duration_seconds': time.monotonic() - started}
        except httpx.HTTPError as exc:
            result = {'utc': utc_now(), 'network_error_type': type(exc).__name__,
                      'state': 'UNCERTAIN_NO_RETRY', 'duration_seconds': time.monotonic() - started}
    with (OUT / (args.case + '-result.json')).open('x') as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result))

if __name__ == '__main__':
    main()
