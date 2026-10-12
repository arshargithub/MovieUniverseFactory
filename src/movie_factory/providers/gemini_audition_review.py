"""One free-tier review of two explicitly generated original music auditions."""
import base64
import hashlib
import json
import os
from pathlib import Path
import httpx
from .gemini_reference_provider import MODEL, load_key, redact_error
from .runway_provider import save_json
from ..telemetry import utc_now

PROMPT = ('Listen to both18-second original instrumental auditions, labeled A and B. '
          'Describe each independently before comparing. Do not assume the intended instruments: '
          'identify the actual dominant melodic timbre with confidence, bass/drum character, '
          'any voices, and timestamped changes0-4,4-7,7-11,11-18seconds. '
          'Is there an immediate rhythmic hook and a distinct emotional lift around7-8seconds? '
          'Does it sustain forward energy afterward, and does the ending cut off unnaturally? '
          'Are the two actually different in lead hierarchy or merely interchangeable generic backing music? '
          'Listen for clipping, glitches or muddy sound. Then judge potential for an exhilarating, '
          'self-possessed horse-rider entrance with private narration early and a decisive turn at7.25s. '
          'Avoid flattery; identify specific shortcomings and useful traits. Do not claim to evaluate '
          'the video or a voice mix: only these music files are supplied. No lyrics or melody transcription. '
          'If inaccessible state AUDIO_UNAVAILABLE. Return concise structured prose, at most900words.')


SKETCH_PROMPT = (
    'Listen to the supplied original instrumental sketch. First give neutral observations, '
    'without assuming instruments: actual duration, foreground timbre and confidence, '
    'melodic phrases and recurrence, harmonic changes, rhythm, space and dynamic development. '
    'Give timestamps for each distinct section and the strongest emotional or melodic opening. '
    'Does it develop a memorable singing phrase, or sound like generic repetitive backing? '
    'Is its character expressive and expansive, mechanically chugging, frantic, melancholy, '
    'or something else? Are there vocals, clipping, glitches or an unnatural ending? '
    'Be critical and specific. Then suggest ONE contiguous18-second excerpt if suitable, '
    'with exact approximate source start and end; identify where the lift falls within it. '
    'The eventual picture is an assured rider noticing danger then making a decisive turn '
    'at7.25s and continuing uphill. No picture or narration is supplied: do not claim to '
    'evaluate their synchronization or mix. Prefer a musically coherent passage over a forced '
    'cut. If no good excerpt or no meaningful melodic development, say so explicitly. '
    'No melody or lyric transcription. If audio inaccessible say AUDIO_UNAVAILABLE. '
    'Maximum700words; distinguish observation from taste judgment.')


def run(root, *, free_tier_confirmed, attempt=1, campaign='music231'):
    if free_tier_confirmed is not True:raise ValueError('Free-tier confirmation required')
    if campaign not in ('music231','music233'):raise ValueError('Unapproved review campaign')
    root=Path(root);out=root/f'.runtime/art-direction/series01-{campaign}'
    if attempt not in (1,2):raise ValueError('At most one explicit retry')
    if attempt==2:
        prior=json.loads((out/'model-review.json').read_text())
        if prior.get('http_status')!=503:raise ValueError('Retry only for verified temporary503')
    suffix='' if attempt==1 else '-retry'
    files=([out/'audition-harmonica.mp3',out/'audition-synth.mp3'] if campaign=='music231'
           else [out/'sketch.mp3'])
    prompt=PROMPT if campaign=='music231' else SKETCH_PROMPT
    for f in files:
        if f.is_symlink() or not f.is_file() or f.stat().st_size>2_000_000:
            raise ValueError('Expected bounded original audition MP3')
    with os.fdopen(os.open(out/f'review-request{suffix}.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w') as f:
        json.dump({'utc':utc_now(),'request_limit':1,'model':MODEL,'paid_authority_usd':0,
                   'estimated_cost_usd':0,'actual_cost_usd':None,'attempt':attempt,'automatic_retry':False,'prompt':prompt,
                   'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}},f)
        f.flush();os.fsync(f.fileno())
    parts=[]
    for label,p in zip(['A','B'],files):
        parts.extend([{'text':'Audition '+label},{'inlineData':{'mimeType':'audio/mpeg','data':base64.b64encode(p.read_bytes()).decode()}}])
    parts.append({'text':prompt})
    key=load_key(root)
    try:
        with httpx.Client(base_url='https://generativelanguage.googleapis.com',headers={'x-goog-api-key':key},timeout=150,follow_redirects=False) as client:
            r=client.post(f'/v1beta/models/{MODEL}:generateContent',json={'contents':[{'parts':parts}],'generationConfig':{'maxOutputTokens':5000}})
            d=r.json();result={'utc':utc_now(),'http_status':r.status_code,'model':MODEL}
            if r.status_code==200:
                cs=d.get('candidates',[])
                result.update(usage=d.get('usageMetadata'),text='\n'.join(p.get('text','') for c in cs for p in c.get('content',{}).get('parts',[]) if not p.get('thought')),finish=[c.get('finishReason') for c in cs])
            else:result['error']=redact_error(d.get('error',{}).get('message',''),key)
    except (httpx.HTTPError,ValueError):result={'state':'UNCERTAIN_NO_RETRY'}
    save_json(out/f'model-review{suffix}.json',result)
    print(json.dumps(result,indent=2))
    return result
