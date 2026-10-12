"""Fixed five-public-reference campaign; zero paid authority and no retries."""
import fcntl
import json
import os
import time
from pathlib import Path

import httpx

from .gemini_reference_provider import MODEL, load_key, redact_error
from .runway_provider import save_json
from ..telemetry import utc_now

TRACKS = (
    ('galactic', 'Galactic Jukebox', 'promptgenix', 'eLI7ZDDY1VQ', '02:35 to the end, especially02:46 onward'),
    ('calls', 'Calls That Never Connected', 'Promptgenix', 'MaDGVf9Pz-o', '01:25 to the end, especially01:37 onward'),
    ('cosmic', 'Cosmic Freight Train', 'promptgenix', 'O9QgHF1gtC8', '01:10 to02:05, especially01:22 onward'),
    ('rise', 'Rise of the Machine, Pt. 2', 'LOAD SHIFT242', 'wJoVRX4Jx58', 'the whole track; locate two or three strongest build/release passages'),
    ('dawn', "New Dawn89'", 'LOAD SHIFT242', 'vJ9SEPrJX9A', 'the whole track; locate two or three strongest build/release passages'),
)


def payload(track):
    if track[0] == 'remaining':
        parts = [
            {'text': 'REFERENCE A: analyze this video, particularly01:25 to the end and01:37 onward.'},
            {'fileData': {'fileUri': 'https://www.youtube.com/watch?v=MaDGVf9Pz-o'}},
            {'text': 'REFERENCE B: separately analyze this complete video, identifying two or three strongest builds/releases.'},
            {'fileData': {'fileUri': 'https://www.youtube.com/watch?v=vJ9SEPrJX9A'}},
            {'text': 'For EACH reference separately provide500-650words: audible instrument palette with confidence, groove/momentum, whole-track timestamp map, detailed lead-in/transition/aftermath at the specified passage for A and strongest lifts for B, tension/release mechanism beyond loudness, then potential application to an original20-second fast horse-rider entrance with narration/danger/decisive turn/uphill surge. Use absolute timestamps within each video. Distinguish audible observations from subjective interpretation. Do not infer from titles/imagery/metadata/prior knowledge. If either audio is inaccessible say AUDIO_UNAVAILABLE for that reference; do not guess. No web search or melody/lyric transcription. Do not copy either composition. Be precise about what enters/exits; avoid unsupported exact BPM/key/measurements. End with uncertainties. Keep A and B clearly separated.'}]
        return {'contents': [{'parts': parts}], 'generationConfig': {'maxOutputTokens': 8500}}
    return {'contents': [{'parts': [
        {'fileData': {'fileUri': 'https://www.youtube.com/watch?v=' + track[3]}},
        {'text': (
            'Analyze the audible music of this complete video. Do not infer sounds from title, '
            'imagery, genre metadata or prior knowledge. No web search. If audio is inaccessible '
            'state AUDIO_UNAVAILABLE and do not guess. Focus particularly on ' + track[4] + '. '
            'Use absolute video timestamps. In650-850words provide: '
            '1) Audible palette: lead timbre/articulation/register, bass, drums, supporting layers, '
            'vocals versus instrumental space; identify instruments tentatively where ambiguous. '
            '2) Short whole-track arrangement map, then detailed lead-in, transition and aftermath '
            'at the requested passage(s). Specify what enters/exits or changes rather than generic '
            'adjectives. 3) Groove and sense of momentum, distinguishing measured tempo from an '
            'estimate (omit exact BPM/key if uncertain). 4) How tension/release works: density, '
            'rhythmic continuity, register, dynamics, expressive lead phrasing. Distinguish audible '
            'observations from interpretations of emotional effect. 5) Separately propose which '
            'arrangement principles could serve an original20-second fast horse-rider entrance '
            'with a private spoken narrator, danger recognition, decisive turn and surging uphill '
            'continuation. What would fit, what would not, and how to make a surge without a long '
            'intro? No reproduction/transcription of lyrics or melody. End with specific uncertainty '
            'notes. Avoid asserting instrument identity merely from a familiar genre association.'
        )}]}], 'generationConfig': {'maxOutputTokens': 6000}}


def run(root, output, *, free_tier_confirmed, client=None, clock=time.time, sleep=time.sleep):
    if free_tier_confirmed is not True:
        raise ValueError('Free-tier confirmation required')
    out = Path(output)
    out.mkdir(parents=True, exist_ok=True)
    with (out / 'campaign.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return _run(root, out, client, clock, sleep)


def continue_after_503(root, output, *, free_tier_confirmed, client=None, clock=time.time, sleep=time.sleep):
    """One explicit continuation, only for the observed second-track503. Six total claims max."""
    if free_tier_confirmed is not True:
        raise ValueError('Free-tier confirmation required')
    out = Path(output)
    prior = json.loads((out / 'summary.json').read_text())
    if (prior['requests'] != 2 or not prior['tracks'][0].get('complete_response')
            or prior['tracks'][1].get('http_status') != 503):
        raise ValueError('Continuation only for verified second-track503')
    with (out / 'campaign.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        dest = out / 'continuation'
        dest.mkdir(exist_ok=True)
        # Preserve the503; put its sole retry last after three independent tracks.
        return _run(root, dest, client, clock, sleep, tracks=TRACKS[2:] + (TRACKS[1],))


def complete_remaining(root, output, *, free_tier_confirmed, client=None, clock=time.time, sleep=time.sleep):
    """One final combined request, only after the observed five-attempt/three-success path."""
    if free_tier_confirmed is not True:
        raise ValueError('Free-tier confirmation required')
    out = Path(output)
    first = json.loads((out / 'summary.json').read_text())['tracks']
    second = json.loads((out / 'continuation' / 'summary.json').read_text())['tracks']
    if (len(first) != 2 or len(second) != 3
            or first[1].get('http_status') != 503 or second[2].get('http_status') != 503
            or not all(r.get('complete_response') for r in [first[0], *second[:2]])):
        raise ValueError('Final combined request requires exact verified five-attempt state')
    with (out / 'campaign.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        dest = out / 'final'
        dest.mkdir(exist_ok=True)
        return _run(root, dest, client, clock, sleep,
                    tracks=(('remaining', 'Calls That Never Connected + New Dawn89', 'Two verified artists', '', ''),))


def _run(root, out, client, clock, sleep, tracks=TRACKS):
    # Any previous attempt makes this campaign non-retryable, including uncertain dispatch.
    with os.fdopen(os.open(out / 'campaign-ledger.json', os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), 'w') as f:
        json.dump({'started_utc': utc_now(), 'request_limit': len(tracks), 'min_start_interval_seconds': 25,
                   'model': MODEL, 'paid_authority_usd': 0, 'estimated_cost_usd': 0,
                   'actual_cost_usd': None, 'tier_basis': 'Director screenshot free tier',
                   'limits': {'rpm': 5, 'tpm': 250000, 'rpd': 20},
                   'remaining_account_quota': None, 'retry': False}, f)
        f.flush()
        os.fsync(f.fileno())
    key = ''
    owned = client is None
    if owned:
        key = load_key(root)
        client = httpx.Client(base_url='https://generativelanguage.googleapis.com',
                             headers={'x-goog-api-key': key}, timeout=150,
                             follow_redirects=False)
    results = []
    previous = None
    try:
        for track in tracks:
            if previous is not None:
                delay = max(0, 25 - (clock() - previous))
                if delay:
                    sleep(delay)
            previous = clock()
            dest = out / track[0]
            dest.mkdir(exist_ok=True)
            with os.fdopen(os.open(dest / 'request-ledger.json', os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), 'w') as f:
                json.dump({'utc': utc_now(), 'epoch': previous, 'track': track[1],
                           'artist': track[2], 'payload': payload(track), 'state': 'CLAIMED_NO_RETRY'}, f)
                f.flush()
                os.fsync(f.fileno())
            result = {'track_id': track[0], 'title': track[1], 'utc': utc_now(), 'model': MODEL}
            try:
                response = client.post(f'/v1beta/models/{MODEL}:generateContent', json=payload(track))
                result['http_status'] = response.status_code
                data = response.json()
                if response.status_code == 200:
                    candidates = data.get('candidates', [])
                    result.update(usage=data.get('usageMetadata'), provider_model=data.get('modelVersion'),
                                  text='\n'.join(p.get('text', '') for c in candidates for p in c.get('content', {}).get('parts', []) if not p.get('thought')),
                                  finish_reasons=[c.get('finishReason') for c in candidates],
                                  prompt_feedback=data.get('promptFeedback'))
                    result['complete_response'] = bool(result['text']) and result['finish_reasons'] == ['STOP'] and 'AUDIO_UNAVAILABLE' not in result['text']
                else:
                    result.update(error_message=redact_error(data.get('error', {}).get('message', ''), key),
                                  retry_after=response.headers.get('retry-after'))
            except (httpx.HTTPError, ValueError):
                result['state'] = 'NETWORK_OR_RESPONSE_UNCERTAIN_NO_RETRY'
            save_json(dest / 'result.json', result)
            results.append(result)
            print(json.dumps({k: result.get(k) for k in ('track_id', 'http_status', 'complete_response', 'usage', 'state')}), flush=True)
            if result.get('http_status') != 200:
                break
    finally:
        save_json(out / 'summary.json', {'finished_utc': utc_now(), 'requests': len(results),
                  'estimated_cost_usd': 0, 'actual_cost_usd': None,
                  'all_complete': len(results) == len(tracks) and all(r.get('complete_response') for r in results),
                  'tracks': results})
        if owned:
            client.close()
    return results
